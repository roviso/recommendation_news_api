from typing import Union
from crud.crud_user import UserCrud
from crud.crud_likes import Likes
from fastapi import APIRouter, status, HTTPException,Depends,Query

from config import pathconfig
from schemas import article_schema
from database import async_session
from models import user_model
from crud.crud_article import ArticleCrud
from crud.crud_latest import LatestCrud
from crud.crud_recommendation import RecommendationCrud
from repository.ncf_recommender.loader import load_pkl
from config import pathconfig
from repository.ncf_recommender import utils
import random
import database
from database import async_session
from sqlalchemy.orm import Session
import numpy as np
import pandas as pd
from fastapi_pagination import paginate,LimitOffsetPage
import scipy.sparse as sparse
from routers import utils
from collections import Counter
import operator
from routers.user import get_user_keywords
from routers.keywords import update_articles_keywords
from newscacher import keywordcache, newscache, latestnewscache
import time
from apis.newstalk.routers.user import get_current_user
from routers.recommend import *

router = APIRouter(
    prefix = "/recommend",
    tags=['recommend']
)




## Router => RETURNS articles based on tags(back relationship method)
@router.get('/tags')
async def recommend_by_tags(tags: str, async_session: Session = Depends(database.get_session), current_user: user_model.User = Depends(get_current_user)):
    article_list =  get_similar_articles(tags)
    async with async_session as session:
        async with session.begin():
            articlecrud = ArticleCrud(session)
            articles = [await articlecrud.search_article(article_id) for article_id in article_list]
            # for article_id in article_list:
            # return await articlecrud.get_article_by_id(article_liked)

    return articles



@router.get('/similar/{article_id}', response_model=LimitOffsetPage[article_schema.GetAllArticle])
async def recommend_similar_articles(article_id: str, user_id: str, async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    async with async_session as session:
        async with session.begin():
            articlecrud = ArticleCrud(session)
            article = await articlecrud.search_article(article_id)
            keywords = ' '.join([str(keyword.keyword.tag) for keyword in article.keywords])

            tfidf_similar_article_list =  get_similar_articles(keywords)

            cf_similar_article_list = get_similar_cf_articles(tfidf_similar_article_list)


            all_article_list = list(set([article.id] +tfidf_similar_article_list + cf_similar_article_list))

            similar_articles = await articlecrud.get_all_articles_by_id(all_article_list)

    for article in similar_articles:
        article.url =  f"http://newstalk.prixa.net/redirect/{article.id}?user_id={user_id}&referrer=from_web"

    return  paginate(similar_articles)
    # return {"item": articles,
    #         "total": len(articles),
    #         "limit": limit,
    #         "offset": offset}


@router.get('/user', response_model=LimitOffsetPage[article_schema.GetAllArticle])
async def recommend_user_articles(current_user: user_model.User = Depends(get_current_user),async_session: Session = Depends(database.get_session)):
    user_id = current_user.id
    async with async_session as session:
        async with session.begin():
            articlecrud = ArticleCrud(session)
            likes = Likes(session)
            ### ____________-- Getting user keyword from model dataframe -- ____________________
            # user = pre.user_df.query(f'user == "{user_id}"')
            # keyword_list = [str(keyword) for keyword in user['user_keywords']]

            ### ___________ -- GETTING USER KEYWORD FROM HISTORY -- __________________
            keywords_len = await keywordcache.get_len(user_id)
            if keywords_len == 0:
                print("USER NOT IN CACHE")
                keyword_list = await get_user_keywords(user_id)
                print("keyword_list is ::: ", keyword_list)
                if not keyword_list:
                    keyword_list = await keywordcache.read_from_cache("trending")
                    if not keyword_list:
                        recent_articles = await articlecrud.get_all_article(0, 100)
                        keyword_list = get_trending_keywords(recent_articles)
                await keywordcache.add_to_cache(user_id,keyword_list)
            else:
                print("USER ALREADY CACHED")
                keyword_list = await keywordcache.read_from_cache(user_id)
                
            keywords = ' '.join([str(keyword) for keyword in keyword_list]) 
            tfidf_similar_article_list =  get_similar_articles(keywords)



            cf_similar_article_list = get_similar_cf_articles(tfidf_similar_article_list)

            if user_id not in user_id_dict:
                user_id = random.choice(list(user_id_dict))

            cf_recommended_article_list = get_recommended_cf_articles(user_id)

            all_recommended_article_list = list(set(cf_recommended_article_list + cf_similar_article_list + tfidf_similar_article_list))
            # + cf_similar_article_list))
            all_liked_articles = await likes.get_all_liked_articles(user_id=user_id)

            liked_ids = [liked_articles.id for liked_articles in all_liked_articles]
            recommended_article_list = [id for id in all_recommended_article_list if id not in liked_ids]

            recommended_articles = await articlecrud.get_all_articles_by_id(recommended_article_list)

        ## Replacing with redirect url
        for article in recommended_articles:
            article.url =  f"http://newstalk.prixa.net/redirect/{article.id}?user_id={user_id}&referrer=from_web"

        return  paginate(recommended_articles)



def update_dictionary(old_dict, new_dict):
    for key in old_dict:
        if key in new_dict:
            new_dict[key] = new_dict[key] + old_dict[key]
        else:
            new_dict.update({key: old_dict[key]})
    
    return new_dict



@router.get('/latest_news', response_model=LimitOffsetPage[article_schema.GetAllArticle])
async def latest_news(offset: int = 0, limit: int = Query(default=500), async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    first_exists = await latestnewscache.check_news_exists(offset)
    last_exists = await latestnewscache.check_news_exists(limit)
    if not first_exists and not last_exists:
        print("CACHING LATEST ARTICLE")
        async with async_session as session:
            async with session.begin():
                articlecrud = ArticleCrud(session)
                all_latest_articles = await articlecrud.get_all_recommended_article(offset = 0 , limit = 500)
                await latestnewscache.cache_news(all_latest_articles)
        
    latest_articles = await latestnewscache.read_all_news_from_cache(offset, limit)
    
    # for article in latest_articles:
    #     article.url =  f"http://localhost:8000/redirect/{article.id}?user_id={user_id}&referrer=from_web"

    
    return paginate(latest_articles)


