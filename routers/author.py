from fastapi import APIRouter
from crud.crud_author import AuthorCrud
from crud.crud_source import SourceCrud
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
async def create_author(author: author_schema.Author):
    async with async_session() as session:
        async with session.begin():
            authorcrud = AuthorCrud(session)
            authordb = await authorcrud.get_author_by_name(author.author_name)
            # print(author,author.__dict__)
            if authordb:
                (author,) = authordb
                # raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Author aleady exists")
                return author
            else:
                sourcecrud = SourceCrud(session)
                author_id = secrets.token_urlsafe(32)
                # (source,) = await sourcecrud.get_source_by_name(author.source)
                # print(source,'found')
                # new_author = Author(id = author_id,source_id= source.id,**author.dict())

                new_author = Author(id = author_id,**author.dict())
                await authorcrud.create_author(new_author)
                return new_author


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
