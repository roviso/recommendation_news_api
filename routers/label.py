from fastapi import APIRouter
from crud import crud_label
from schemas import label_schema, article_schema
from models.label_model import Label
from database import async_session
from typing import List, Optional
from fastapi_pagination import paginate,LimitOffsetPage

router = APIRouter(
    prefix = "/label",
    tags=['label']
)

@router.post("/add_label")
async def addlabel(label_name: str,):
    async with async_session() as session:
        async with session.begin():
            labelcrud = crud_label.LabelCrud(session)
            new_label = Label(label_name = label_name)
            await labelcrud.create_label(new_label)
            return new_label



@router.get("/get_label")
async def getAlllabel():
    async with async_session() as session:
        async with session.begin():
            labelcrud = crud_label.LabelCrud(session)
            labels =  await labelcrud.get_all_label()
            return labels




@router.get("/get_label_by_name/{label_name}")
async def get_label_by_name(label_name: str):
    async with async_session() as session:
        async with session.begin():
            labelcrud = crud_label.LabelCrud(session)
            label =  await labelcrud.get_label_by_name(label_name)
            if label:
                (label,)= label
            return label


@router.get("/get_label_by_id/{label_id}")
async def get_label_by_name(label_id: int):
    async with async_session() as session:
        async with session.begin():
            labelcrud = crud_label.LabelCrud(session)
            label =  await labelcrud.get_label_by_id(label_id)
            if label:
                (label,)= label
            return label



@router.get("/get_label_articles/{label_id}", status_code = 200, response_model=LimitOffsetPage[article_schema.GetAllArticle])
async def get_label_articles(label_id: int):
    async with async_session() as session:
        async with session.begin():
            labelcrud = crud_label.LabelCrud(session)
            articles =  await labelcrud.get_label_articles(label_id)
            return paginate(articles)
            


