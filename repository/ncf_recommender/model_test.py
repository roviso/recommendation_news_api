print('-------importing modules-----------------')
import pandas as pd
import torch
import torch.nn as nn
from tqdm import tqdm
import os
from loader import load_pkl, load_checkpoint
from model import NMF
from preprocessor import preprocessor
from dataset_loader import Test_Rating_dataSet
from itertools import islice
import operator
import ast


def str_to_list(list_string):
  return ast.literal_eval(list_string)


print('-------importing modules done-----------------')
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
device = torch.device("cuda")
print("Using: ",device)

load_model = True
save_model = False
load_pkl_flag = True
data_path = 'train.csv'
keyword_len = 20

print('----------Preprocessing(loading data)--------------------')
if os.path.isfile('../data/pre.pkl'):
    print('loding pikle...1111111111111111111111111111111')
    pre = load_pkl('../data/pre.pkl')
    print('Successfully Loaded Pickle file')
elif os.path.isfile('../data/train.csv'):
    print('No Pickle file found.')
    print('Using CSV file, train.csv.')
    data_path = '../data/train.csv'
    print('Starting Pre-processing...')
    pre = preprocessor(data_path,keywords_limit = keyword_len)
    if pre:
        print('Successfully Loaded CSV file to train')
print('----------Preprocessing Completed--------------------')


dropout = 0.01
learning_rate = 0.001
print("finish loading Data...)")

print("Initailizing Model...")
model_name = '../trained_models/NCF_checkpoint_cuda.pth.tar'
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


# user_list = [le_user_mapping[55]]
# url_list =  [pre.index_url_mapping[i] for i in range(len(pre.index_url_mapping))]
url_list =  [pre.index_url_mapping[i] for i in range(255)]

def eval_sample_list(user_list,url_list):
  user_df = pd.DataFrame({'user': user_list})
  article_df = pd.DataFrame({'article':url_list})
  test_ds = Test_Rating_dataSet(user_df,article_df, pre.user_index_mapping, pre.url_to_index_and_labels_dict)
  test_dl = torch.utils.data.DataLoader(test_ds, batch_size=1, shuffle=False,)
  url_to_rating = {}
  device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
  
  for _, (user_name,user,article_url,url_index,labels,Dominant_Topic) in tqdm(enumerate(test_dl)):
      user = user[0].unsqueeze(1)
      user,url_index, label,Dominant_Topic = user.to(device),url_index.to(device),labels.to(device),Dominant_Topic.to(device)
      prediction, user_embed_MLP, article_embed_MLP = model( user, url_index,label,Dominant_Topic)
      
      for i,(url) in enumerate(article_url[0]):
          url_r= {url : float(prediction[i])}
          url_to_rating.update(url_r)

  return url_to_rating

def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))

    
def get_top_20(user_name,url_list, model):
  user_list = [user_name,]
  url_to_rating = eval_sample_list(user_list,url_list)
  sorted_top_url = dict( sorted(url_to_rating.items(), key=operator.itemgetter(1),reverse=True))
  top_20 = take(20, sorted_top_url.items())
  return top_20


def get_recommendation(top_20):
    recommended_list = []
    for recommended_url in top_20:
        pre_df = pre.df[pre.df.url == recommended_url[0]].iloc[0]
        item_val = {
            "url": pre_df.url,
            "head_image": pre.df.head_image,
            "heading": pre.df.heading,
            "date": pre_df.date.split()[0],
            "label": pre_df.label,
            "content": pre.df.content,
            "source": pre.df.source,
            "author": pre.df.author,
            "author_img": pre.df.author_img,
        }
        recommended_list.append(item_val)
    return recommended_list

# get_url_df = pd.read_csv(data_path,index_col=False)
# url_list = get_url_df[['url']].values.tolist()

user_name = '02d8b818b3ece264239f15ad4fe54608'
top_20 = get_top_20(user_name,url_list, model)
print(top_20)
print(get_recommendation(top_20))