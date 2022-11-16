from fastapi import APIRouter, Depends
from crud import crud_source
from schemas import source_schema, article_schema, author_schema
from models.source_model import Source
from database import async_session
from typing import List, Optional
from fastapi_pagination import paginate,LimitOffsetPage
from models import user_model
from apis.newstalk.routers.user import get_current_user

router = APIRouter(
    prefix = "/source",
    tags=['source']
)

@router.get("/get_all_source")
async def getAllSource(current_user: user_model.User = Depends(get_current_user)):
    async with async_session() as session:
        async with session.begin():
            sourcecrud = crud_source.SourceCrud(session)
            sources =  await sourcecrud.get_all_source()
            return sources


@router.get("/get_source_by_id/{source_id}")
async def getSourceById(source_id: int,current_user: user_model.User = Depends(get_current_user)):
    async with async_session() as session:
        async with session.begin():
            sourcecrud = crud_source.SourceCrud(session)
            return await sourcecrud.get_source_by_id(source_id)


@router.get("/get_source_authors/{source_id}", status_code = 200, response_model=LimitOffsetPage[author_schema.GetAllAuthors])
async def get_source_authors(source_id: int,current_user: user_model.User = Depends(get_current_user)):
    async with async_session() as session:
        async with session.begin():
            sourcecrud = crud_source.SourceCrud(session)
            authors = await sourcecrud.get_source_authors(source_id)
            return paginate(authors)


@router.get("/get_source_articles/{source_id}", status_code = 200, response_model=LimitOffsetPage[article_schema.GetAllArticle])
async def get_source_authors(source_id: int,current_user: user_model.User = Depends(get_current_user)):
    async with async_session() as session:
        async with session.begin():
            sourcecrud = crud_source.SourceCrud(session)
            articles = await sourcecrud.get_source_articles(source_id)
            return paginate(articles)

