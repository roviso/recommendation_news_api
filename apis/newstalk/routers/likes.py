from fastapi import APIRouter,status,Depends
from crud.crud_likes import Likes
from models.article_model import Article
from schemas import user_schema, likes_schema, article_schema

from typing import List, Optional
import secrets
from database import async_session
from sqlalchemy.orm import Session
import database
from fastapi_pagination import paginate,LimitOffsetPage
from models import user_model
from apis.newstalk.routers.user import get_current_user


router = APIRouter(
    prefix = "/like",
    tags=['like']
)


@router.post('/', status_code = status.HTTP_201_CREATED)
async def like_article(article_id:str, async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    article_liked = likes_schema.CreateUserArticleLikes(
        user_id = current_user.id, 
        article_id = article_id 
    )
    async with async_session as session:
        async with session.begin():
            likes = Likes(session)
            return await likes.like_article(article_liked)


@router.post('/get_likes_by_article',status_code = 200)
async def get_likes_by_article(article_id:str, async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    async with async_session as session:
        async with session.begin():
            likes = Likes(session)
            all_liked_user =  await likes.get_articles_like(article_id=article_id)
            return {
                'total_likes': len(all_liked_user),
                'liked_user': all_liked_user
            }


@router.post('/get_likes_by_user', response_model= likes_schema.GetUserArticleLikesResponse)
async def get_likes_by_user(article_id: str, async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    article_liked = likes_schema.GetUserArticleLikes(
        user_id = current_user.id, 
        article_id= article_id
    )
    async with async_session as session:
        async with session.begin():
            likes = Likes(session)
            liked = await likes.check_liked_articles(article_liked)
            if not liked:
                liked = False
            else:
                liked = True
            all_liked_user =  await likes.get_articles_like(article_id=article_liked.article_id)

            liked_users = [likes_schema.LikedUser(
                id = liked_user.id,
                username = liked_user.username
            ) for liked_user in all_liked_user]

            response = likes_schema.GetUserArticleLikesResponse(
                liked = liked,
                total_likes = len(all_liked_user),
                liked_users = liked_users
            )
            return response
            


@router.get('/get_all_likes_by_user', status_code = 200, response_model=LimitOffsetPage[article_schema.GetAllArticle])
async def get_all_likes_by_user(async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    user_id = current_user.id
    async with async_session as session:
        async with session.begin():
            likes = Likes(session)
            all_liked_articles = await likes.get_all_liked_articles(user_id=user_id)
            return paginate(all_liked_articles)