from fastapi import FastAPI,WebSocket,Cookie,Query,Depends,status
from typing import Optional, List
from fastapi.responses import HTMLResponse
from models import user_model, author_model
from database import engine
from routers import user, token, latest_recommender
from preprocessor import preprocessor
import aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import torch
import torch.nn as nn
from fastapi import BackgroundTasks
import aioredis

from fastapi import status,Depends, Response
from sqlalchemy.orm import Session
from crud import crud_user
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
from newscacher import newscache, urlcache,usercache
from collections import OrderedDict


user_model.Base.metadata.create_all(bind=engine)
author_model.Base.metadata.create_all(bind=engine)


app = FastAPI(title='News Recommendation')

# @app.on_event("startup")
# async def startup():
#     await database.connect()


app.include_router(latest_recommender.router)

# app.include_router(recommendation_ncf.router)



app.include_router(token.router)

app.include_router(user.router)


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
if os.path.isfile('/home/prixa-ml/Desktop/projects/recommendation_news_api/repository/data-processing/processed_data/train_data/pre.pkl'):
    
    pre = load_pkl('/home/prixa-ml/Desktop/projects/recommendation_news_api/repository/data-processing/processed_data/train_data/pre.pkl')
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


url_generated = url_generator.url_generator(pre.df)
url_list =  url_generated.get_url_by_time_only('3_months')
url_list = url_list['url'].unique()


# recommended_user_article = dict()

# async def store_viewed_already(user_id: str, url_list: list):
#     recommended_user_article[user_id] = url_list
#     return recommended_user_article



# @app.get('/get_already_recommended/', status_code = 200)
# async def get_already_recommended():
#     return recommended_user_article

def url_remover(db,user_id: str,all_url_list: List[str],url_to_ignore: List[str] = None):
    viewed_articles = crud_user.get_all_viewed_articles(db,user_id)
    viewed_article_list = [x.viewed_article.url for x in viewed_articles]

    liked_articles = crud_user.get_all_liked_articles(db,user_id)
    liked_article_list = [x.liked_article.url for x in liked_articles]

    ignore_article_list = viewed_article_list + liked_article_list + url_to_ignore
    url_list = list(reduce(lambda x,y : filter(lambda z: z!=y,x) ,ignore_article_list,all_url_list))
    
    return url_list


async def get_url_list(db,user,user_id: str, site: Optional[str] = None, time: Optional[str] =  None):
    url_len = await urlcache.get_len(user_id)
    print(f"url_len : {url_len},")
    if url_len == 0:
        print("NO ITEM FOUND IN CACHE")
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
        url_list = url_remover(db,user_id,all_url_list = all_url_list,url_to_ignore = prev_visited_url)


        await urlcache.add_to_cache(user_id,url_list)
    else:
        print("ITEM ALREADY IN CACHE")
        url_list = await urlcache.read_from_cache(user_id)
        viewed_articles = crud_user.get_all_viewed_articles(db,user_id)
        
        # for article in viewed_articles:
        #     article_to_remove.append(urlchace.add_to_cache(user_id,i,{k: str(v) for k,v in news.items()}))
        await urlcache.clear_cache_from_list(user_id,viewed_articles)
        url_list = await urlcache.read_from_cache(user_id)

    return url_list


async def cache_news(user_id: str,top_100_recommendation):
    await newscache.cache_news(user_id,top_100_recommendation)

async def get_top_100_recommendation(db, user_id: str,site: str, time: str):
    r = RandomDict(pre.index_user_mapping)
    user = r.random_value()

    url_list = await get_url_list(db,user,user_id, site, time)

    print(f"taking url list: {len(url_list)}")

    top_100_recommended_urls =  utils.get_top_100(user,url_list,pre,model)
    top_100_dictionary = dict.fromkeys(top_100_recommended_urls, "recommended")

    top_100_recommended_urls = list(top_100_dictionary.keys())
    top_100_urls = top_100_recommended_urls
    top_100_recommendation = utils.context_giver(top_100_urls,pre)

    return top_100_recommendation

    

def get_random_news(news_list: List[dict], number_to_select: int) -> List[dict]:
    index_list = []
    selected_news = []
    for _ in range(number_to_select):
        i = random.choice(range(len(news_list)))
        index_list.append(i)
        selected_news.append(news_list[i])


@app.get('/{user_id}', status_code = 200)
async def get_recommendation_cache(background_tasks: BackgroundTasks,user_id: str, site: Optional[str] = None, time: Optional[str] =  None,db: Session = Depends(database.get_db)):
    cached_users = await usercache.get_users()
    if user_id not in cached_users:
        print('---------------------------No-user Found--------------------------')

        top_100_recommendation = await get_top_100_recommendation(db,user_id,site,time)
        background_tasks.add_task(cache_news,user_id,top_100_recommendation)
        top_20_recommendation = top_100_recommendation[:20]

    else:
        print('------------------------USER FOUND-----------------------------------')
        top_100_recommendation_ordered = await newscache.read_cached_news(user_id)
        top_100_recommendation = list(filter(None, [dict(recommended_news) for recommended_news in top_100_recommendation_ordered.values()]))
        print(f"len of all is :::::::: {len(top_100_recommendation)}")
        if len(top_100_recommendation) > 20:
            top_20_recommendation_ordered = OrderedDict(random.choices(list(top_100_recommendation_ordered.items()), k = 20))
            recommended_news_index = top_20_recommendation_ordered.keys()
            top_20_recommendation = [dict(recommended_news) for recommended_news in top_20_recommendation_ordered.values()]
            await newscache.clear_cache_news(user_id, recommended_news_index)
            top_20_recommendation = list(filter(None, top_20_recommendation))
        else:
            top_100_recommendation = await get_top_100_recommendation(db,user_id,site,time)
            background_tasks.add_task(cache_news,user_id,top_100_recommendation)
            top_20_recommendation = top_100_recommendation[:20]
        
    return top_20_recommendation




# @app.get('/remove_cached_user/{user_id}', status_code = 200)
# async def get_cached_user(user_id: str):
#     # return await get_recommendation_cache_func(db, user_id,site,time)
#     return await newscache.remove_cached_user(user_id)


# @app.get('/cached_user/', status_code = 200)
# async def get_cached_user():
#     # return await get_recommendation_cache_func(db, user_id,site,time)
#     return await newscache.get_users()


@app.get('/cached_news/{user_id}', status_code = 200)
async def get_recommendation_cache(user_id: str):
    # return await get_recommendation_cache_func(db, user_id,site,time)
    return await newscache.read_cached_news(user_id)
    

@app.post('/remove_cached_news/{user_id}', status_code = 200)
async def remove_cached_news(user_id: str, url_indices : List[int]):
    # return await get_recommendation_cache_func(db, user_id,site,time)
    return await newscache.clear_cache_news(user_id, url_indices)

@app.get('/clear_user_cache/', status_code = 200)
async def clear_user_cache():
    # return await get_recommendation_cache_func(db, user_id,site,time)
    return await usercache.clear_user_cache()


# @app.get('/cached_url/{user_id}', status_code = 200)
# async def get_url_cache(user_id: str):
#     # return await get_recommendation_cache_func(db, user_id,site,time)
#     return await urlcache.read_from_cache(user_id)

# @app.post('/remove_cached_urls/{user_id}', status_code = 200)
# async def remove_cached_urls(user_id: str, urls_to_remove: List[str]):
#     # return await get_recommendation_cache_func(db, user_id,site,time)
#     return await urlcache.clear_cache_from_list(user_id,urls_to_remove)



if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn
    

    uvicorn.run(app, host="0.0.0.0", port=8848, log_level="debug")