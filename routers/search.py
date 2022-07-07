from fastapi import APIRouter,Depends
from crud.crud_user import UserCrud
from crud.crud_author import AuthorCrud
from crud.crud_keywords import KeywordsCrud

from schemas import user_schema, author_schema, article_schema

from repository.ncf_recommender.loader import load_pkl
from typing import List, Optional, Any
import secrets
from database import async_session
from sqlalchemy.orm import Session
import database


from fastapi_pagination import paginate,LimitOffsetPage



router = APIRouter(
    prefix = "/search",
    tags=['search']
)


@router.get('/{tags}', response_model=LimitOffsetPage[article_schema.GetAllArticle])
async def search_articles(tag: str, async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            keywordcrud = KeywordsCrud(session)
            # print(f"searching the tag: {tag}")
            tagged_articles = await keywordcrud.search_articles_by_keywords(tag)
            # print(f"Searched Articles with tag: {tag} are : {tagged_articles}")
    # print(tagged_articles[0].__dict__)
    return paginate(tagged_articles)

@router.get('/author/{author_name}' , response_model = LimitOffsetPage[author_schema.GetAllAuthors])
async def search_author(author_name: str, async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            authorcrud = AuthorCrud(session)
            authors = await authorcrud.search_author_by_name(author_name)
    # print(authors,authors[0].__dict__)
    return paginate(authors)
    # return authors



@router.get('/user/{user_name}', response_model = LimitOffsetPage[user_schema.SearchUsers])
async def search_users(user_name: str, async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            usercrud = UserCrud(session)
            users = await usercrud.search_user_by_name(user_name)
    return paginate(users)
    # print(users)
    # return(users)


