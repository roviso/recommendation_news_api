from fastapi import APIRouter, Depends
from crud import crud_label
from schemas import label_schema, article_schema
from models.label_model import Label
from database import async_session
from typing import List, Optional
from fastapi_pagination import paginate,LimitOffsetPage
from models import user_model
from apis.newstalk.routers.user import get_current_user

router = APIRouter(
    prefix = "/label",
    tags=['label']
)


@router.get("/get_label_articles/{label_id}", status_code = 200, response_model=LimitOffsetPage[article_schema.GetAllArticle])
async def get_label_articles(label_id: int,current_user: user_model.User = Depends(get_current_user)):
    async with async_session() as session:
        async with session.begin():
            labelcrud = crud_label.LabelCrud(session)
            articles =  await labelcrud.get_label_articles(label_id)
            return paginate(articles)
            


