from fastapi import APIRouter,status,Depends
from crud.crud_views import Views
from models.article_model import Article
from schemas import user_schema, views_schema
from typing import List, Optional
import secrets
from database import async_session
from sqlalchemy.orm import Session
import database

router = APIRouter(
    prefix = "/views",
    tags=['views']
)

@router.post('/', status_code = status.HTTP_201_CREATED)
async def view_article(article_viewed: views_schema.CreateUserArticleViews, async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            views = Views(session)
            return await views.view_article(article_viewed)


@router.post('/get_views_by_user', status_code = status.HTTP_201_CREATED)
async def get_views_by_user(user_id: str, article_id:str, async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            views = Views(session)
            return await views.check_viewed_articles(user_id=user_id, article_id=article_id)


@router.post('/get_all_views_by_user', status_code = status.HTTP_201_CREATED)
async def get_all_views_by_user(user_id: str, async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            views = Views(session)
            return await views.get_all_viewed_articles(user_id=user_id)
            # viewed_articles =  [await views.articledb.get_article_by_id(article.article_id) for article in await views.get_all_viewed_articles(user_id=user_id)]

            

    # print(dir(viewed_articles[0].viewed_article),8888888888888888888888888888888888)1

    
