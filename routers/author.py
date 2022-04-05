from fastapi import APIRouter
from crud.crud_author import AuthorCrud
from models.author_model import Author
from schemas import author_schema
from typing import List, Optional
import secrets
from database import async_session

router = APIRouter(
    prefix = "/author",
    tags=['author']
)



@router.post('/create_author', status_code = 200)
async def create_author(article: author_schema.Author):
    author_id = secrets.token_urlsafe(32)
    new_article = Author(id = author_id,**article.dict())
    async with async_session() as session:
        async with session.begin():
            authorcrud = AuthorCrud(session)
            return await authorcrud.create_author(new_article)


@router.put('/update_author/{author_id}', status_code = 200)
async def update_author(author_id: str, author_name: Optional[str] = None, author_img: Optional[str] = None):
    async with async_session() as session:
        async with session.begin():
            authorcrud = AuthorCrud(session)
            return await authorcrud.update_author(author_id, author_name, author_img)



@router.get('/get_all_author', status_code = 200)
async def get_all_author() -> List[Author]:
    async with async_session() as session:
        async with session.begin():
            authorcrud = AuthorCrud(session)
            return await authorcrud.get_all_author()


@router.get('/search_author', status_code = 200)
async def search_author(author_name: str) -> Author:
    async with async_session() as session:
        async with session.begin():
            authorcrud = AuthorCrud(session)
            return await authorcrud.get_author_by_name(author_name)
