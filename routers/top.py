from fastapi import APIRouter
from crud.crud_author import AuthorCrud
from crud.crud_source import SourceCrud
from crud.crud_latest import LatestCrud
from crud.crud_user import UserCrud
from models.author_model import Author
from models.user_model import RegisteredUser
from schemas import author_schema,article_schema,profile_schema
from typing import List, Optional
import secrets
from database import async_session
from fastapi_pagination import paginate,LimitOffsetPage

router = APIRouter(
    prefix = "/top",
    tags=['top']
)


@router.get('/top_articles', status_code = 200 , response_model= LimitOffsetPage[article_schema.GetAllArticle])
async def get_top_source(n_days: int) -> List[Author]:
    async with async_session() as session:
        async with session.begin():
            latestcrud = LatestCrud(session)
            top_sources = await latestcrud.get_top_article(n_days)
            

    return paginate(top_sources)



@router.get('/top_source', status_code = 200 , response_model= LimitOffsetPage[profile_schema.SourceProfile])
async def get_top_source() -> List[Author]:
    async with async_session() as session:
        async with session.begin():
            sourcecrud = SourceCrud(session)
            top_sources = await sourcecrud.get_top_sources()
            

    return paginate(top_sources)



@router.get('/top_author', status_code = 200 , response_model= LimitOffsetPage[profile_schema.AuthorProfile])
async def get_top_author() -> List[Author]:
    async with async_session() as session:
        async with session.begin():
            authorcrud = AuthorCrud(session)
            top_authors = await authorcrud.get_top_authors()
            

    return paginate(top_authors)



@router.get('/top_users', status_code = 200 , response_model= LimitOffsetPage[profile_schema.UserProfile])
async def get_top_users() -> List[RegisteredUser]:
    async with async_session() as session:
        async with session.begin():
            usercrud = UserCrud(session)
            top_users = await usercrud.get_top_users()
            

    return paginate(top_users)