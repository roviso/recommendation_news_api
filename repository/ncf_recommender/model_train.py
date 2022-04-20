print('----------importing modules--------------------')
import torch
import argparse
from preprocessor import preprocessor
import os
from loader import load_pkl
from model_trainer import trainer
from config import pathconfig


# Creating the parser
parser = argparse.ArgumentParser()
parser.add_argument('--device', type=str, help='cpu or cuda: if not specified, uses cuda if available')
parser.add_argument('--load_model', dest='load_model', action='store_true', help='if True: loads pre-trained model, Default: True')
parser.add_argument('--no-load_model', dest='load_model', action='store_false')
parser.add_argument('--save_model', dest='save_model', action='store_true', help='if False: saves model, Default: True')
parser.add_argument('--no-save_model', dest='save_model', action='store_false')

parser.add_argument('--epochs', type=int, required=True, help='epoch to train the model')
parser.add_argument('--bs', type=int, required=True, help='Batch Size: Defines the batch size to train the model')
parser.add_argument('--lr', type=float, required=True, help='Learning Rate: Defines the learning rate to train the model')
parser.add_argument('--keyword_len', type=int, help='Keywords to consider during training, DEFAULT: 20')
args = parser.parse_args()

if args.device:
    device = torch.device(args.device)
else:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model_name = f"NCF_checkpoint_{device}.pth.tar"

load_model = args.load_model

save_model = args.save_model

if args.keyword_len:
    keyword_len = args.keyword_len
else:
    keyword_len = 20



print("-----------Using Arguments--------------------")
print(f"Using device: {device}, Load Model: {load_model}, Save Model: {save_model}, Model Name: {model_name}")
print(f"Using epochs: {args.epochs}, Batch Size: {args.bs}, Learning Rate: {args.lr}, Keyword Len: {keyword_len}")


print('----------Preprocessing(loading data)--------------------')
if pathconfig.PRE_PKL_PATH.is_file():
    pre = load_pkl(pathconfig.PRE_PKL_PATH)
    print('Successfully Loaded Pickle file')

elif pathconfig.TRAIN_CSV_PATH.is_file():
    print('No Pickle file found.')
    print('Using CSV file, train.csv.')
    pre = preprocessor(pathconfig.TRAIN_CSV_PATH,keywords_limit = keyword_len)
    if pre:
        print('Successfully Loaded CSV file to train')
print('----------Preprocessing Completed--------------------')




# if os.path.isfile('../data/pre.pkl'):
#     pre = load_pkl('../data/pre.pkl')
#     print('Successfully Loaded Pickle file')
# elif os.path.isfile('../data/train.csv'):
#     print('No Pickle file found.')
#     print('Using CSV file, train.csv.')
#     data_path = '../data/train.csv'
#     print('Starting Pre-processing...')
#     pre = preprocessor(data_path,keywords_limit = keyword_len)
#     if pre:
#         print('Successfully Loaded CSV file to train')
# print('----------Preprocessing Completed--------------------')



hyperparameters = dict(
    epochs = args.epochs,
    nlayer = 3,
    batch_size = args.bs,
    learning_rate = args.lr,
    # architecture = 'NCF_simple',
    dropout = 0.01,
    # save_model_name = ['all_employee_till_april_model.0.pth.tar','all_employee_till_april_model.1.pth.tar','all_employee_till_april_model.2.pth.tar','all_employee_till_april_model.3.pth.tar','all_employee_till_april_model.4.pth.tar',],
    save_model_name = model_name,    
    clip = 5,
    # user_emb_sizes = pre.user_emb_sizes,
    # url_emb_sizes = pre.url_emb_sizes,
    # url_to_keyword = pre.url_to_keyword_dict,
    # keyword_to_url = pre.keyword_to_url_dict,
    device = device,
    load_model = load_model,
    save_model = save_model
)

print(f"hyperparameters: {hyperparameters}")

model_trainer = trainer(hyperparameters,pre)


# print('----------Running TRAINER--------------------')
model_trainer.train()



