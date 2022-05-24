
from fastapi import APIRouter,Depends
from typing import Optional, List
from models import user_model
from routers import user
from preprocessor import preprocessor
import torch
import torch.nn as nn
from fastapi import BackgroundTasks
from fastapi import Depends
import torch
import torch.nn as nn
from typing import  Optional
from functools import reduce 
from repository.ncf_recommender.loader import load_pkl, load_checkpoint
from repository.ncf_recommender.model import NMF
from repository.ncf_recommender.preprocessor import preprocessor
from repository.ncf_recommender import utils
from helper import url_generator
import random
from randomdict import RandomDict
from models import user_model
from newscacher import newscache, urlcache,usercache
from collections import OrderedDict
from crud.crud_views import Views
from crud.crud_likes import Likes
from database import async_session
# user_model.Base.metadata.create_all(bind=engine)
# author_model.Base.metadata.create_all(bind=engine)

from config import pathconfig


router = APIRouter(
    prefix = "/recommendation",
    tags=['recommendation']
)


print('-------importing modules done-----------------')
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
device = torch.device("cpu")
print("Using: ",device)

load_model = True
save_model = False
load_pkl_flag = True
# data_path = '../repository/data/train.csv'
keyword_len = 20



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



dropout = 0.01
learning_rate = 0.001
print("finish loading Data...)")
if pathconfig.PRE_PKL_PATH.is_file():
    print("... Model found... Initailizing Model ...")
    model_name = pathconfig.MODEL_PATH
else:
    print("No Model Found... SORRY:(")
    model_name = None

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


async def get_all_viewed_articles(user_id):
    async with async_session() as session:
        async with session.begin():
            views = Views(session)
            viewed_articles =  [await views.articledb.get_article_by_id(article.article_id) for article in await views.get_all_viewed_articles(user_id=user_id)]
    
    viewed_urls = [article.id for article in viewed_articles]
    return  viewed_urls

async def get_all_liked_articles(user_id):
    async with async_session() as session:
        async with session.begin():
            likes = Likes(session)
            liked_articles =  [await likes.articledb.get_article_by_id(article.article_id) for article in await likes.get_all_liked_articles(user_id=user_id)]
    
    liked_urls = [article.id for article in liked_articles]
    return  liked_urls


async def url_remover(user_id: str,all_url_list: List[str],url_to_ignore: List[str] = None):
    viewed_articles = await get_all_viewed_articles(user_id)
    # viewed_article_list = [x.viewed_article.url for x in viewed_articles]

    liked_articles = await get_all_liked_articles(user_id)
    # liked_article_list = [x.liked_article.url for x in liked_articles]

    ignore_article_list = viewed_articles + liked_articles + url_to_ignore
    url_list = list(reduce(lambda x,y : filter(lambda z: z!=y,x) ,ignore_article_list,all_url_list))
    
    return url_list


async def get_url_list(user,user_id: str, site: Optional[str] = None, time: Optional[str] =  None):
    url_len = await urlcache.get_len(user_id)
    print(f"url_len : {url_len},")
    # Views()
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
        url_list = await url_remover(user_id,all_url_list = all_url_list,url_to_ignore = prev_visited_url)


        await urlcache.add_to_cache(user_id,url_list)
    else:
        print("ITEM ALREADY IN CACHE")
        url_list = await urlcache.read_from_cache(user_id)
        viewed_articles = await get_all_viewed_articles(user_id)
        
        # for article in viewed_articles:
        #     article_to_remove.append(urlchace.add_to_cache(user_id,i,{k: str(v) for k,v in news.items()}))
        await urlcache.clear_cache_from_list(user_id,viewed_articles)
        url_list = await urlcache.read_from_cache(user_id)

    return url_list


async def cache_news(user_id: str,top_100_recommendation):
    await newscache.cache_news(user_id,top_100_recommendation)

async def get_top_100_recommendation(user_id: str,site: str, time: str):
    if user_id in pre.index_user_mapping.values():
        user = user_id
    else:
        r = RandomDict(pre.index_user_mapping)
        user = r.random_value()

    url_list = await get_url_list(user,user_id, site, time)

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


@router.get('/{user_id}', status_code = 200)
async def get_recommendation_cache(background_tasks: BackgroundTasks,user_id: str, site: Optional[str] = None, time: Optional[str] =  None,):
    cached_users = await usercache.get_users()
    if user_id not in cached_users:
        print('---------------------------No-user Found--------------------------')

        top_100_recommendation = await get_top_100_recommendation(user_id,site,time)
        background_tasks.add_task(cache_news,user_id,top_100_recommendation)
        top_20_recommendation = top_100_recommendation[:20]

    else:
        print('------------------------USER FOUND-----------------------------------')
        top_100_recommendation_ordered = await newscache.read_cached_news(user_id)
        # top_100_recommendation = list(filter(None, [dict(recommended_news) for recommended_news in top_100_recommendation_ordered.values()]))
        print(f"len of all is :::::::: {len(top_100_recommendation_ordered)}")
        if len(top_100_recommendation_ordered) > 20:
            top_20_recommendation_ordered = OrderedDict(random.choices(list(top_100_recommendation_ordered.items()), k = 20))
            print(f"len of recommended url is :::::::: {len(top_20_recommendation_ordered)}")
            recommended_news_index = top_20_recommendation_ordered.keys()
            top_20_recommendation = [dict(recommended_news) for recommended_news in top_20_recommendation_ordered.values()]
            await newscache.clear_cache_news(user_id, recommended_news_index)
            top_20_recommendation = list(filter(None, top_20_recommendation))
        else:
            top_100_recommendation = await get_top_100_recommendation(user_id,site,time)
            background_tasks.add_task(cache_news,user_id,top_100_recommendation)
            top_20_recommendation = top_100_recommendation[:20]
        
    return top_20_recommendation


@router.get('/random_user/')
def get_random_user():
    r = RandomDict(pre.index_user_mapping)
    user = r.random_value()

    user_url_df = pre.df.groupby(['user'])
    prev_visited_url = user_url_df.get_group(user).url.to_list()
    prev_visited_articles =  utils.context_giver(prev_visited_url,pre)


    return {"user": user,
            "prev_visited_articles": prev_visited_articles}


@router.get('/get_previously_visited_urls/{user_id}')
def get_previously_visited_urls(user_id: str):
    user_url_df = pre.df.groupby(['user'])
    prev_visited_url = user_url_df.get_group(user_id).url.to_list()
    return utils.context_giver(prev_visited_url,pre)


@router.get('/with_token/', status_code = 200)
async def get_recommendation_cache(background_tasks: BackgroundTasks,current_user: user_model.User = Depends(user.get_current_user), site: Optional[str] = None, time: Optional[str] =  None,):
    user_id = current_user.User.id
    print(f"user_id is :{user_id}")
    cached_users = await usercache.get_users()
    if user_id not in cached_users:
        print('---------------------------No-user Found--------------------------')
        top_100_recommendation = await get_top_100_recommendation(user_id,site,time)
        background_tasks.add_task(cache_news,user_id,top_100_recommendation)
        top_20_recommendation = top_100_recommendation[:20]
    else:
        print('------------------------USER FOUND-----------------------------------')
        top_100_recommendation_ordered = await newscache.read_cached_news(user_id)
        # top_100_recommendation = list(filter(None, [dict(recommended_news) for recommended_news in top_100_recommendation_ordered.values()]))
        print(f"len of all is :::::::: {len(top_100_recommendation_ordered)}")
        if len(top_100_recommendation_ordered) > 20:
            top_20_recommendation_ordered = OrderedDict(random.choices(list(top_100_recommendation_ordered.items()), k = 20))
            print(f"len of recommended url is :::::::: {len(top_20_recommendation_ordered)}")
            recommended_news_index = top_20_recommendation_ordered.keys()
            top_20_recommendation = [dict(recommended_news) for recommended_news in top_20_recommendation_ordered.values()]
            await newscache.clear_cache_news(user_id, recommended_news_index)
            top_20_recommendation = list(filter(None, top_20_recommendation))
        else:
            top_100_recommendation = await get_top_100_recommendation(user_id,site,time)
            background_tasks.add_task(cache_news,user_id,top_100_recommendation)
            top_20_recommendation = top_100_recommendation[:20]
        
    return top_20_recommendation

