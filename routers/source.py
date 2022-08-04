from fastapi import APIRouter
from crud import crud_source
from schemas import source_schema, article_schema, author_schema
from models.source_model import Source
from database import async_session
from typing import List, Optional
from fastapi_pagination import paginate,LimitOffsetPage


router = APIRouter(
    prefix = "/source",
    tags=['source']
)

@router.post("/add_source")
async def addSource(source: source_schema.Source,):
    async with async_session() as session:
        async with session.begin():
            sourcecrud = crud_source.SourceCrud(session)
            new_source = Source(**source.dict())
            await sourcecrud.create_source(new_source)

            sourceInDb = await sourcecrud.get_source_by_name(new_source.name)
            return sourceInDb


@router.get("/get_source")
async def getAllSource():
    async with async_session() as session:
        async with session.begin():
            sourcecrud = crud_source.SourceCrud(session)
            sources =  await sourcecrud.get_all_source()
            return sources


@router.get("/get_source_by_id/{source_id}")
async def getSourceById(source_id: int):
    async with async_session() as session:
        async with session.begin():
            sourcecrud = crud_source.SourceCrud(session)
            return await sourcecrud.get_source_by_id(source_id)


@router.get("/get_source_authors/{source_id}", status_code = 200, response_model=LimitOffsetPage[author_schema.GetAllAuthors])
async def get_source_authors(source_id: int):
    async with async_session() as session:
        async with session.begin():
            sourcecrud = crud_source.SourceCrud(session)
            authors = await sourcecrud.get_source_authors(source_id)
            return paginate(authors)


@router.get("/get_source_articles/{source_id}", status_code = 200, response_model=LimitOffsetPage[article_schema.GetAllArticle])
async def get_source_authors(source_id: int):
    async with async_session() as session:
        async with session.begin():
            sourcecrud = crud_source.SourceCrud(session)
            articles = await sourcecrud.get_source_articles(source_id)
            return paginate(articles)


@router.put('/update_source/{source_id}', status_code = 200)
async def update_author(source_id: int,
                        name: Optional[str]= None, 
                        link: Optional[str]= None, 
                        image: Optional[str]= None,
                        content_selector: Optional[str]= None,
                        image_selector: Optional[str]= None,
                        author_img_selector: Optional[str]= None,
                        author_name_selector: Optional[str]= None,
                        label_selector: Optional[str]= None,
                        disable: Optional[str]= None,
                        analytics_id: Optional[str]= None,
                        debug: Optional[str]= None,
                        debug_link: Optional[str]= None):
    async with async_session() as session:
        async with session.begin():
            sourcecrud = crud_source.SourceCrud(session)
            return await sourcecrud.update_source(source_id,
                                    name,
                                    link,
                                    image,
                                    content_selector,
                                    image_selector,
                                    author_img_selector,
                                    author_name_selector,
                                    label_selector,
                                    disable,
                                    analytics_id,
                                    debug,
                                    debug_link)


@router.get("/remove_source/{source_id}")
async def getSource(source_id: int):
    async with async_session() as session:
        async with session.begin():
            sourcecrud = crud_source.SourceCrud(session)
            return await sourcecrud.remove_source(source_id)

