print('-------importing modules-----------------')
from fastapi import APIRouter
import pandas as pd
import torch
import torch.nn as nn
from tqdm import tqdm
import os
from repository.ncf_recommender.loader import load_pkl, load_checkpoint
from repository.ncf_recommender.model import NMF
from repository.ncf_recommender.preprocessor import preprocessor
from repository.ncf_recommender import utils

router = APIRouter(
    prefix = "/recommendation",
     tags=['Recommendation']
)

print('-------importing modules done-----------------')
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
device = torch.device("cuda")
print("Using: ",device)

load_model = True
save_model = False
load_pkl_flag = True
data_path = '../repository/data/train.csv'
keyword_len = 20

print('----------Preprocessing(loading data)--------------------')
if os.path.isfile('repository/data/pre.pkl'):
    pre = load_pkl('repository/data/pre.pkl')
    print('Successfully Loaded Pickle file')
elif os.path.isfile('repository/data/train.csv'):
    print('No Pickle file found.')
    print('Using CSV file, train.csv.')
    data_path = 'repository/data/train.csv'
    print('Starting Pre-processing...')
    pre = preprocessor(data_path,keywords_limit = keyword_len)
    if pre:
        print('Successfully Loaded CSV file to train')
print('----------Preprocessing Completed--------------------')



dropout = 0.01
learning_rate = 0.001
print("finish loading Data...)")

print("Initailizing Model...")
model_name = 'repository/trained_models/NCF_checkpoint_cuda.pth.tar'
nlayer = 3
dropout = 0.001
model = NMF(user_emb_sizes = pre.user_emb_sizes, url_emb_sizes = pre.url_emb_sizes,url_to_keyword_dict= pre.url_to_keyword_dict ,  nlayer = nlayer, dropout = dropout, device = device).to(device)
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr= learning_rate)

if load_model:
    print("loading Model.....")
    load_checkpoint(torch.load(model_name), model, optimizer)
    model.train() 
    print("Finish Loading Model")

# url_list =  [pre.index_url_mapping[i] for i in range(255)]
url_list =  pre.index_url_mapping.values()

user_name = '02d8b818b3ece264239f15ad4fe54608'
top_20 = utils.get_top_20(user_name,url_list,pre ,model)

print(utils.context_giver(top_20,pre) )


@router.get('/{id}', status_code = 200)
def get_user(id):
    print(id,int(id),type(id))
    return {"user: " : pre.index_user_mapping[int(id)]}


@router.get('/get_urls/{id}', status_code = 200)
async def get_recommendation(id):
    user = pre.index_user_mapping[int(id)]
    utils.get_top_20(user,url_list,pre ,model)
    return utils.context_giver(top_20,pre)