from fastapi import APIRouter, Depends
from crud.crud_author import AuthorCrud
from crud.crud_source import SourceCrud
from models.author_model import Author
from schemas import author_schema,article_schema
from typing import List, Optional
import secrets
from database import async_session
from fastapi_pagination import paginate,LimitOffsetPage
from apis.newstalk.routers.user import get_current_user
from models import user_model

router = APIRouter(
    prefix = "/author",
    tags=['author']
)

@router.get('/get_all_author', status_code = 200)
async def get_all_author(current_user: user_model.User = Depends(get_current_user)) -> List[Author]:
    async with async_session() as session:
        async with session.begin():
            authorcrud = AuthorCrud(session)
            return await authorcrud.get_all_author()


@router.get('/search_author', status_code = 200)
async def search_author(author_name: str, current_user: user_model.User = Depends(get_current_user)) -> Author:
    async with async_session() as session:
        async with session.begin():
            authorcrud = AuthorCrud(session)
            author = await authorcrud.get_author_by_name(author_name)
            if author:
                (author,)= author
            return author

@router.get("/get_author_articles/{author_id}", status_code = 200, response_model=LimitOffsetPage[article_schema.GetAllArticle])
async def get_label_articles(author_id: str, current_user: user_model.User = Depends(get_current_user)):
    async with async_session() as session:
        async with session.begin():
            authorcrud = AuthorCrud(session)
            articles =  await authorcrud.get_author_articles(author_id)
            return paginate(articles)
            