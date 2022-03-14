print('-------importing modules-----------------')
from urllib import response
from fastapi import APIRouter, status,Depends, Response
from sqlalchemy.orm import Session
from crud import crud_user
import pandas as pd
import torch
import torch.nn as nn
from typing import  Optional
import database
from tqdm import tqdm
import os
from functools import reduce 
from repository.ncf_recommender.loader import load_pkl, load_checkpoint
from repository.ncf_recommender.model import NMF
from repository.ncf_recommender.preprocessor import preprocessor
from repository.ncf_recommender import utils
from helper import url_generator
import random
from randomdict import RandomDict
from models import user_model
from schemas import user_schema





router = APIRouter(
    prefix = "/recommendation",
     tags=['Recommendation']
)

# print('-------importing modules done-----------------')
# # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# device = torch.device("cuda")
# print("Using: ",device)

# load_model = True
# save_model = False
# load_pkl_flag = True
# data_path = '../repository/data/train.csv'
# keyword_len = 20



# print('----------Preprocessing(loading data)--------------------')
# if os.path.isfile('/home/prixa-ml/Desktop/projects/recommendation_news_api/repository/data-processing/processed_data/train_data/pre.pkl'):
    
#     pre = load_pkl('/home/prixa-ml/Desktop/projects/recommendation_news_api/repository/data-processing/processed_data/train_data/pre.pkl')
#     print('Successfully Loaded Pickle file')
# elif os.path.isfile('repository/data/train.csv'):
#     print('No Pickle file found.')
#     print('Using CSV file, train.csv.')
#     data_path = 'repository/data/train.csv'
#     print('Starting Pre-processing...')
#     pre = preprocessor(data_path,keywords_limit = keyword_len)
#     if pre:
#         print('Successfully Loaded CSV file to train')
# print('----------Preprocessing Completed--------------------')



# dropout = 0.01
# learning_rate = 0.001
# print("finish loading Data...)")

# print("Initailizing Model...")
# model_name = 'repository/trained_models/NCF_checkpoint_cuda.pth.tar'
# nlayer = 3
# dropout = 0.001
# model = NMF(user_emb_sizes = pre.user_emb_sizes, url_emb_sizes = pre.url_emb_sizes,url_to_keyword_dict= pre.url_to_keyword_dict ,  nlayer = nlayer, dropout = dropout, device = device).to(device)
# criterion = nn.MSELoss()
# optimizer = torch.optim.Adam(model.parameters(), lr= learning_rate)

# if load_model:
#     print("loading Model.....")
#     load_checkpoint(torch.load(model_name), model, optimizer)
#     model.train() 
#     print("Finish Loading Model")


# url_generated = url_generator.url_generator(pre.df)
# url_list =  url_generated.get_url_by_time_only('3_months')
# url_list = url_list['url'].unique()


recommended_user_article = dict()

async def store_viewed_already(user_id: str, url_list: list):
    recommended_user_article[user_id] = url_list
    return recommended_user_article



@router.get('/get_already_recommended/', status_code = 200)
async def get_already_recommended():
    return recommended_user_article


@router.get('/{user_id}', status_code = 200)
async def get_recommendation(user_id: str, site: Optional[str] = None, time: Optional[str] =  None,db: Session = Depends(database.get_db)):
    # user = pre.index_user_mapping[int(user_id)]
    # user = random.choice(list(d.values()))
    global recommended_user_article
    r = RandomDict(pre.index_user_mapping)
    user = r.random_value()

    if site and time :
        url_df = url_generated.get_url_by_time_and_site(site,time)
    elif site:        
        url_df =  url_generated.get_df_by_site(site)
    elif time:        
        url_df =  url_generated.get_url_by_time_only(time)
    else:
        url_df =  url_generated.get_url_by_time_only('4_months')

    all_url_list = url_df['url'].unique()
    user_url_df = pre.df.groupby(['user'])
    prev_visited_url = user_url_df.get_group(user).url.to_list()
    # liked_articles = crud_user.get_all_liked_articles(db,user_id)


    viewed_articles = crud_user.get_all_viewed_articles(db,user_id)
    liked_article_list = [x.liked_article.url for x in viewed_articles]
    prev_visited_url.extend(liked_article_list)

    if user_id in recommended_user_article:
        already_recommended_articles = recommended_user_article[user_id]
        prev_visited_url.extend(already_recommended_articles)
        # print(f"{user_id} already viewed {prev_visited_url}")

    url_list = list(reduce(lambda x,y : filter(lambda z: z!=y,x) ,prev_visited_url,all_url_list))

    top_20_urls =  utils.get_top_20(user,url_list,pre,model)
    if user_id in recommended_user_article:
        recommended_urls = recommended_user_article[user_id]
        recommended_urls.extend(top_20_urls)
    else:
        recommended_urls = top_20_urls
        recommended_user_article.update(await store_viewed_already(user_id,recommended_urls))

    return utils.context_giver(top_20_urls,pre)


@router.post('/likes/',status_code = status.HTTP_201_CREATED)
async def article_liked(article_liked: user_schema.CreateUserArticleLikes,response: Response,db: Session = Depends(database.get_db)):
    return crud_user.create_likes(db, article_liked)
        # return JSONResponse(status_code=status.HTTP_201_CREATED, content=item)




@router.post('/views/',status_code = status.HTTP_201_CREATED)
async def article_viewed(article_viewed: user_schema.CreateUserArticleViewed,db: Session = Depends(database.get_db)):
    
    return crud_user.create_views(db, article_viewed)



@router.post('/comments/',status_code = status.HTTP_201_CREATED)
async def article_commented(article_comment: user_schema.CreateUserArticleComments,db: Session = Depends(database.get_db)):
    
    return crud_user.create_comments(db, article_comment)




# url_list =  [pre.index_url_mapping[i] for i in range(255,500)]
# url_list = random.sample(pre.index_url_mapping.values(), 555)
# url_list =  

# user_name = '02d8b818b3ece264239f15ad4fe54608'
# top_20 = utils.get_top_20(user_name,url_list,pre ,model)

# print(utils.context_giver(top_20,pre) )


# @router.get('/{id}', status_code = 200)
# def get_user(id):
#     print(id,int(id),type(id))
#     return {"user: " : pre.index_user_mapping[int(id)]}


# @router.get('/get_urls/{id}', status_code = 200)
# async def get_recommendation(id):
#     user = pre.index_user_mapping[int(id)]
#     top_20_urls = utils.get_top_20(user,url_list,pre ,model)
#     return utils.context_giver(top_20_urls,pre)



# @router.get('/get_urls_of/{user_id}', status_code = 200)
# async def get_recommendation(user_id: int, site: Optional[str] = None, time: Optional[str] =  None):
#     user = pre.index_user_mapping[int(user_id)]
    
#     if site and time :
#         url_df = url_generated.get_url_by_time_and_site(site,time)
#     elif site:        
#         url_df =  url_generated.get_df_by_site(site)
#     elif time:        
#         url_df =  url_generated.get_url_by_time_only(time)
#     else:
#         url_df =  url_generated.get_url_by_time_only('1_weeks')

#     all_url_list = url_df['url'].unique()
#     user_url_df = pre.df.groupby(['user'])
#     prev_visited_url = user_url_df.get_group(user).url.to_list()
#     url_list = list(reduce(lambda x,y : filter(lambda z: z!=y,x) ,prev_visited_url,all_url_list))

#     top_20_urls =  utils.get_top_20(user,url_list,pre,model)
#     return utils.context_giver(top_20_urls,pre)


