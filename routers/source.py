from fastapi import APIRouter
from crud import crud_source
from schemas import source_schema
from models.source_model import Source
from database import async_session
from typing import List, Optional


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
            return await sourcecrud.create_source(new_source)



@router.get("/get_source")
async def getAllSource():
    async with async_session() as session:
        async with session.begin():
            sourcecrud = crud_source.SourceCrud(session)
            sources =  await sourcecrud.get_all_source()
            return sources




@router.get("/get_source_by_name/{source_name}")
async def getSource(source_name: str):
    async with async_session() as session:
        async with session.begin():
            sourcecrud = crud_source.SourceCrud(session)
            return await sourcecrud.get_source_by_name(source_name)


@router.put('/update_source/{source_id}', status_code = 200)
async def update_author(source_id: int, author_name: Optional[str] = None, author_img: Optional[str] = None,
                        name: Optional[str]= None, 
                        image: Optional[str]= None,
                        content_selector: Optional[str]= None,
                        image_selector: Optional[str]= None,
                        author_selector: Optional[str]= None,
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
                                    image,
                                    content_selector,
                                    image_selector,
                                    author_selector,
                                    label_selector,
                                    disable,
                                    analytics_id,
                                    debug,
                                    debug_link)

