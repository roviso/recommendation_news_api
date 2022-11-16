from fastapi import APIRouter,status,Depends
from crud.crud_bookmarks import Bookmarks
from models.article_model import Article
from schemas import bookmarks_schema, article_schema
from typing import List, Optional
import secrets
from database import async_session
from sqlalchemy.orm import Session
import database
from fastapi_pagination import paginate,LimitOffsetPage
from models import user_model
from apis.newstalk.routers.user import get_current_user


router = APIRouter(
    prefix = "/bookmark",
    tags=['bokmark']
)


@router.post('/', status_code = status.HTTP_201_CREATED)
async def bookmark_article(article_id: str, async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    article_bookmarked = bookmarks_schema.CreateUserArticleBookmarks(
        user_id =current_user.id,
        article_id = article_id
    )

    async with async_session as session:
        async with session.begin():
            bookmarks = Bookmarks(session)
            return await bookmarks.bookmark_article(article_bookmarked)



@router.post('/get_all_bookmarks_by_user', status_code = 200, response_model=LimitOffsetPage[article_schema.GetAllArticle])
async def get_all_likes_by_user(current_user: user_model.User = Depends(get_current_user), async_session: Session = Depends(database.get_session)):
    user_id = current_user.id
    async with async_session as session:
        async with session.begin():
            bookmarks = Bookmarks(session)
            all_bookmarked_articles =  await bookmarks.get_all_bookmarked_articles(user_id=user_id)
            return paginate(all_bookmarked_articles)