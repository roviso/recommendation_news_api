from fastapi import APIRouter,status,Depends
from crud.crud_views import Views
from models.article_model import Article
from schemas import user_schema, views_schema
from typing import List, Optional
import secrets
from database import async_session
from sqlalchemy.orm import Session
import database
from models import user_model
from apis.newstalk.routers.user import get_current_user


router = APIRouter(
    prefix = "/views",
    tags=['views']
)

@router.post('/', status_code = status.HTTP_201_CREATED)
async def view_article(article_view: views_schema.CreateUserArticleViewsRequest, async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    article_viewed= views_schema.CreateUserArticleViews(
        user_id = current_user.id ,
        article_id= article_view.article_id,
        start_time= article_view.start_time,
        end_time= article_view.end_time ,
        total_time_spend= article_view.total_time_spend
    )
    async with async_session as session:
        async with session.begin():
            views = Views(session)
            return await views.view_article(article_viewed)


# @router.post('/get_views_by_user', status_code = status.HTTP_201_CREATED)
# async def get_views_by_user(article_id:str, async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
#     user_id = current_user.id
#     async with async_session as session:
#         async with session.begin():
#             views = Views(session)
#             return await views.check_viewed_articles(user_id=user_id, article_id=article_id)


# @router.post('/get_all_views_by_user', status_code = status.HTTP_201_CREATED)
# async def get_all_views_by_user(async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
#     user_id = current_user.id
#     async with async_session as session:
#         async with session.begin():
#             views = Views(session)
#             return await views.get_all_viewed_articles(user_id=user_id)
