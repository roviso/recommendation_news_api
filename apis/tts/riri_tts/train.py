import os
import time
import torch
import argparse
from tqdm import tqdm
import numpy as np
from inference import infer
from utils.util import mode
from hparams import hparams as hps
from utils.logger import Tacotron2Logger
from utils.dataset import ljdataset, ljcollate, NepaliDataset
from model.model import Tacotron2, Tacotron2Loss
from torch.utils.data import DistributedSampler, DataLoader
np.random.seed(hps.seed)
torch.manual_seed(hps.seed)
torch.cuda.manual_seed(hps.seed)


def prepare_dataloaders(fdir, n_gpu):
    trainset = ljdataset(fdir)
    # trainset = NepaliDataset(fdir)
    collate_fn = ljcollate(hps.n_frames_per_step)
    # sampler = DistributedSampler(trainset) if n_gpu > 1 else None
    train_loader = DataLoader(trainset, num_workers = hps.n_workers, shuffle = n_gpu == 1,
                              batch_size = hps.batch_size, pin_memory = hps.pin_mem,
                              drop_last = True, collate_fn = collate_fn)
                            #   , sampler = sampler)
    return train_loader


def load_checkpoint(ckpt_pth, model, optimizer, device, n_gpu):
    ckpt_dict = torch.load(ckpt_pth, map_location = device)
    (model.module if n_gpu > 1 else model).load_state_dict(ckpt_dict['model'])
    optimizer.load_state_dict(ckpt_dict['optimizer'])
    iteration = ckpt_dict['iteration']
    return model, optimizer, iteration


def save_checkpoint(model, optimizer, iteration, ckpt_pth, n_gpu):
    print(f"saving model checkpoint at {ckpt_pth}")
    torch.save({'model': (model.module if n_gpu > 1 else model).state_dict(),
                'optimizer': optimizer.state_dict(),
                'iteration': iteration}, ckpt_pth)
    # torch.save(model.state_dict(), ckpt_pth)

def train(args):
    # setup env
    print("Starting the Model Prepation")
    rank = local_rank = 0
    n_gpu = 1
    if 'WORLD_SIZE' in os.environ:
        os.environ['OMP_NUM_THREADS'] = str(hps.n_workers)
        rank = int(os.environ['RANK'])
        local_rank = int(os.environ['LOCAL_RANK'])
        n_gpu = int(os.environ['WORLD_SIZE'])
        torch.distributed.init_process_group(
            backend = 'nccl', rank = local_rank, world_size = n_gpu)
    torch.cuda.set_device(local_rank)
    device = torch.device('cuda:{:d}'.format(local_rank))
    # device = torch.device('cuda')
    print(f"using device : {device}")

    # build model
    print("building model...")
    model = Tacotron2()
    mode(model, True)
    print('model device:',next(model.parameters()).device)
    print(F"Successfully build model: {model}")
    if n_gpu > 1:
        model = torch.nn.parallel.DistributedDataParallel(
            model, device_ids = [local_rank])
    optimizer = torch.optim.Adam(model.parameters(), lr = hps.lr,
                                betas = hps.betas, eps = hps.eps,
                                weight_decay = hps.weight_decay)
    criterion = Tacotron2Loss()
    
    # load checkpoint
    iteration = 1
    print(f"Training iteration = {iteration}")
    if args.ckpt_pth != '':
        print(f"loading checkpoint: {args.ckpt_pth}")
        model, optimizer, iteration = load_checkpoint(args.ckpt_pth, model, optimizer, device, n_gpu)
        optimizer.param_groups[0]['capturable'] = True
        iteration += 1
    
    # get scheduler
    if hps.sch:
        lr_lambda = lambda step: hps.sch_step**0.5*min((step+1)*hps.sch_step**-1.5, (step+1)**-0.5)
        if args.ckpt_pth != '':
            scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda, last_epoch = iteration)
        else:
            scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)
    
    # make dataset
    print(f"Preparing dataset from {args.data_dir}")
    train_loader = prepare_dataloaders(args.data_dir, n_gpu)
    
    if rank == 0:
        # get logger ready
        if args.log_dir != '':
            if not os.path.isdir(args.log_dir):
                os.makedirs(args.log_dir)
                os.chmod(args.log_dir, 0o775)
            logger = Tacotron2Logger(args.log_dir)

        # get ckpt_dir ready
        if args.ckpt_dir != '' and not os.path.isdir(args.ckpt_dir):
            os.makedirs(args.ckpt_dir)
            os.chmod(args.ckpt_dir, 0o775)

    print("Starting model Training")
    model.train()
    # ================ MAIN TRAINNIG LOOP! ===================
    epoch = 0
    # iteration = 1
    while iteration <= hps.max_iter:
    # for i in tqdm(range(500)):
        print(f"__________________EPOCH: {epoch}_______________________________________")
        
        # print(next(model.parameters()).is_cuda,222222222222222222222)
        if n_gpu > 1:
            train_loader.sampler.set_epoch(epoch)
        for batch in tqdm(train_loader):
            if iteration > hps.max_iter:
                break
            start = time.perf_counter()
            x, y = (model.module if n_gpu > 1 else model).parse_batch(batch)
            # print(f"Input data are : x={x}, y-{y}")
            y_pred = model(x)
            # print(y_pred)
            # loss
            loss, items = criterion(y_pred, y)

            # zero grad
            model.zero_grad()

            # backward, grad_norm, and update
            loss.backward()
            grad_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), hps.grad_clip_thresh)
            optimizer.step()
            if hps.sch:
                scheduler.step()

            dur = time.perf_counter()-start
            # if rank == 0:
                # info
            

            # log
            if args.log_dir != '' and (iteration % hps.iters_per_log == 0):
                learning_rate = optimizer.param_groups[0]['lr']
                logger.log_training(items, grad_norm, learning_rate, iteration)

            # sample
            if args.log_dir != '' and (iteration % hps.iters_per_sample == 0):
                model.eval()
                output = infer(hps.eg_text, model.module if n_gpu > 1 else model)
                model.train()
                logger.sample_train(y_pred, iteration)
                logger.sample_infer(output, iteration)

            

            iteration += 1

        # save ckpt
        if args.ckpt_dir != '' and (epoch % hps.iters_per_ckpt == 0):
            print('Iter: {} Mel Loss: {:.2e} Gate Loss: {:.2e} Grad Norm: {:.2e} {:.1f}s/it'.format(
            iteration, items[0], items[1], grad_norm, dur))
            ckpt_pth = os.path.join(args.ckpt_dir, 'ckpt_riri_{}'.format(iteration))
            # ckpt_pth = os.path.join(args.ckpt_dir, 'ckpt_nepali_riri_fine_trained')
            save_checkpoint(model, optimizer, iteration, ckpt_pth, n_gpu)
            
        print('Iter: {} Mel Loss: {:.2e} Gate Loss: {:.2e} Grad Norm: {:.2e} {:.1f}s/it'.format(
        iteration, items[0], items[1], grad_norm, dur))
        ckpt_pth = os.path.join(args.ckpt_dir, 'ckpt_riri_final')
        # ckpt_pth = os.path.join(args.ckpt_dir, 'ckpt_nepali_riri_fine_trained')
        save_checkpoint(model, optimizer, iteration, ckpt_pth, n_gpu)
            
        epoch += 1

    if rank == 0 and args.log_dir != '':
        logger.close()


if __name__ == '__main__':
    print("Entering Training the model")
    parser = argparse.ArgumentParser()
    # path
    parser.add_argument('-d', '--data_dir', type = str, default = 'data',
                        help = 'directory to load data')
    parser.add_argument('-l', '--log_dir', type = str, default = 'log',
                        help = 'directory to save tensorboard logs')
    parser.add_argument('-cd', '--ckpt_dir', type = str, default = 'ckpt',
                        help = 'directory to save checkpoints')
    parser.add_argument('-cp', '--ckpt_pth', type = str, default = '',
                        help = 'path to load checkpoints')

    args = parser.parse_args()
    
    torch.backends.cudnn.enabled = True
    torch.backends.cudnn.benchmark = False
    train(args)
