import torch
import torch.nn as nn
import numpy as np

from utils import configer
from torch.utils.data import DataLoader
from dataset_loader import Rating_dataSet
from model import NMF
from loader import load_checkpoint,save_checkpoint

from tqdm import tqdm

class trainer():
    def __init__(self,hyperparameters,pre):
        self.config = configer(hyperparameters)
        
        train_dataset = Rating_dataSet(pre.user_df, pre.url_and_label_df, pre.user_flds, pre.url_flds, pre.y)
        self.train_dataLoader = DataLoader(train_dataset, batch_size=self.config.batch_size, shuffle=True,drop_last =True)
        
        
        self.model = NMF(user_emb_sizes = pre.user_emb_sizes, url_emb_sizes = pre.url_emb_sizes,url_to_keyword_dict=pre.url_to_keyword_dict , nlayer = self.config.nlayer, dropout = self.config.dropout, device = self.config.device).to(self.config.device)
        

        self.criterion = nn.MSELoss()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr= self.config.learning_rate)
        self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(self.optimizer, factor = 0.01, patience=5, verbose=True)


        if self.config.load_model:
            load_checkpoint(torch.load(self.config.save_model_name), self.model, self.optimizer)
            self.model.train()


    def train_batch(self, user,url, label,Dominant_Topic,rating):

        user,url, label,Dominant_Topic,rating = user.to(self.config.device),url.to(self.config.device),label.to(self.config.device),Dominant_Topic.to(self.config.device),rating.to(self.config.device)
        
        
        # Forward pass ➡
        prediction, user_embed_MLP, article_embed_MLP = self.model( user, url,label,Dominant_Topic)

        # print('predict_scores.shape :', predict_scores.shape)
        loss = self.criterion(prediction, rating)
        
        # Backward pass ⬅
        self.optimizer.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(self.model.parameters(), self.config.clip)

        # Step with optimizer
        self.optimizer.step()

        return rating,prediction,loss,user_embed_MLP,article_embed_MLP

    def train(self):
        train_losses = []
        counter = 0

        total_batches = len(self.train_dataLoader ) * self.config.epochs
        batches_per_epoch = len(self.train_dataLoader )/self.config.batch_size
        print('total_batches is:',total_batches)
        print('batches_per_epoch is:', batches_per_epoch)
        example_ct = 0  # number of examples seen
        batches_trained = 0
        user_embedding = {}
        item_embedding = {}
    
        print('-----------training started-------------------')
        for epoch in tqdm(range(self.config.epochs)):
            batch_ct = 0
            print(f'Starting new epoch: {epoch} ')
            print(f'Using the leraning rate:{self.optimizer.param_groups[0].get("lr")}')
            for _, (user,url,label,Dominant_Topic,rating) in tqdm(enumerate(self.train_dataLoader)):

                actual_rating,prediction_rating,loss,user_embed_MLP,article_embed_MLP = self.train_batch(user,url,label,Dominant_Topic,rating)
                batch_ct += 1
                train_losses.append(loss.item())

                batches_trained += 1
            if (batches_trained % 500) == 0:
                diff = actual_rating - prediction_rating
                self.train_log(loss, batches_trained, epoch,actual_rating,prediction_rating)
                print('prediction is:', prediction_rating.squeeze())
                print('target rating is:', actual_rating.squeeze())
                print('diff is:', diff.squeeze())
                print('loss is:', loss.item())

            mean_loss = sum(train_losses)/len(train_losses)
            self.scheduler.step(mean_loss)
            
            print("Epoch: {}/{}...".format(epoch+1, self.config.epochs),
                "batch trained: {}/{}...".format(batches_trained,total_batches),
                "Mean Train Loss: {:.6f}...".format(np.mean(train_losses)))
            
            if (self.config.save_model):
                checkpoint = {"state_dict": self.model.state_dict(), "optimizer": self.optimizer.state_dict(),}
                save_checkpoint(checkpoint, filename= self.config.save_model_name)


    def train_log(self, loss, batch_ct, epoch,actual_rating,prediction_rating):
        loss = float(loss)

        # where the magic happens
        # wandb.log({"epoch": epoch, "loss": loss}, step=batch_ct)
        print(f"EPOCH: {epoch}")
        print(f"Loss after " + str(batch_ct).zfill(5) + f" examples: {loss:.3f}")
        print('Prediction is : ', prediction_rating.squeeze())
        print(" Target is : "+ str(actual_rating.squeeze()))


