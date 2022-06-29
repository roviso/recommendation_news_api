from fastapi import APIRouter
from crud import crud_source
from schemas import source_schema
from models.source_model import Source
from database import async_session



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
            print("_________getting source___________")
            sourcecrud = crud_source.SourceCrud(session)
            sources =  await sourcecrud.get_all_source()
            print(f"_________got sources : {sources}___________")
            return sources




@router.get("/get_source_by_name/{source_name}")
async def getSource(source_name: str):
    async with async_session() as session:
        async with session.begin():
            sourcecrud = crud_source.SourceCrud(session)
            return await sourcecrud.get_source_by_name(source_name)
