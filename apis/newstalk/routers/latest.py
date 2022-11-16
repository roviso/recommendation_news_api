from numpy import int16
import pandas as pd
from fastapi import APIRouter, status, HTTPException,Depends,Query
from crud.crud_latest import LatestCrud
from crud.crud_author import AuthorCrud
from models.article_model import Article,LatestArticle, RecommendedArticle
from models import author_model
from schemas import article_schema
from typing import List, Optional
import secrets
from database import async_session
from cacher.latest_cache import latestcache
from cacher.tfidf_cache import tfidfcache
from fastapi import BackgroundTasks
from crud.crud_article import ArticleCrud
from helper import tfidf_generator
from operator import add
from functools import reduce
from routers.keywords import add_article_keywords
from fastapi_pagination import paginate,LimitOffsetPage
from models import user_model
from apis.newstalk.routers.user import get_current_user

router = APIRouter(
    prefix = "/latest",
    tags=['latest']
)



async def cache_latest_news(latest_news):
    await latestcache.cache_news(latest_news)


async def get_trending_news():
    async with async_session() as session:
        async with session.begin():
            latestcrud = LatestCrud(session)
            trending_articles = await latestcrud.n_days_news()

    return trending_articles




@router.get('/get_latest_articles', status_code = 200, response_model=LimitOffsetPage[article_schema.GetAllArticle])
async def get_latest_articles(current_user: user_model.User = Depends(get_current_user)) -> List[LatestArticle]:
    async with async_session() as session:
        async with session.begin():
            latestcrud = LatestCrud(session)
            latest_articles = await latestcrud.get_latest_articles()

            return  paginate(latest_articles)




@router.get('/get_latest_article/article_id', status_code = 200)
async def get_latest_articles_by_id(article_id: str) -> List[LatestArticle]:
    async with async_session() as session:
        async with session.begin():
            latestcrud = LatestCrud(session)
            return await latestcrud.get_article_by_id(article_id)

