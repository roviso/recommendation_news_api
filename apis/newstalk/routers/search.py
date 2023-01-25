from fastapi import APIRouter,Depends
from crud.crud_user import UserCrud
from crud.crud_author import AuthorCrud
from crud.crud_keywords import KeywordsCrud
from schemas import user_schema, author_schema, article_schema
from typing import List, Optional, Any
from database import async_session
from sqlalchemy.orm import Session
import database
from fastapi_pagination import paginate,LimitOffsetPage
from models import user_model
from apis.newstalk.routers.user import get_current_user
from crud import crud_label, crud_search


router = APIRouter(
    prefix = "/search",
    tags=['search']
)


@router.get('/', status_code = 200,)
#  response_model=LimitOffsetPage[article_schema.GetAllArticle])
async def search_articles(search_str: str, async_session: Session = Depends(database.get_session)):
# ,current_user: user_model.User = Depends(get_current_user)):
    async with async_session as session:
        async with session.begin():
            searchcrud = crud_search.SearchCrud(session)
            searched_items = await searchcrud.search_string(search_str)
            return searched_items



@router.get('/hashtag', status_code = 200, response_model=LimitOffsetPage[article_schema.GetAllArticle])
async def search_articles(hashtag: str, async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    async with async_session as session:
        async with session.begin():
            keywordcrud = KeywordsCrud(session)
            tagged_articles = await keywordcrud.search_articles_by_keywords(hashtag)
            return paginate(tagged_articles)



@router.get("/label", status_code = 200, response_model=LimitOffsetPage[article_schema.GetAllArticle])
async def get_label_articles(label_id: int,current_user: user_model.User = Depends(get_current_user)):
    async with async_session() as session:
        async with session.begin():
            labelcrud = crud_label.LabelCrud(session)
            articles =  await labelcrud.get_label_articles(label_id)
            return paginate(articles)
            


@router.get('/author', status_code = 200 , response_model = LimitOffsetPage[author_schema.GetAllAuthors])
async def search_author(author_name: str, async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    async with async_session as session:
        async with session.begin():
            authorcrud = AuthorCrud(session)
            authors = await authorcrud.search_author_by_name(author_name)
            return paginate(authors)




@router.get('/user', status_code = 200, response_model = LimitOffsetPage[user_schema.SearchUsers])
async def search_users(user_name: str, async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    async with async_session as session:
        async with session.begin():
            usercrud = UserCrud(session)
            users = await usercrud.search_user_by_name(user_name)
            return paginate(users)


