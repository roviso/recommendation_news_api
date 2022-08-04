from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.future import select
# from schemas import article_schema
from models.label_model import Label
from models import article_model
from datetime import datetime
from typing import List, Optional
from sqlalchemy import update


class LabelCrud():
    def __init__(self, db_session: Session):
        self.db_session = db_session
        

    async def create_label(self, label: str):
        self.db_session.add(label)
        await self.db_session.flush()



    async def get_all_label(self) -> List[Label]:
        query = select(Label)
        results = await self.db_session.execute(query)
        return results.scalars().all()


    async def get_label_by_name(self, label_name: str) ->Label:
        query = select(Label).where(Label.label_name == label_name)
        results = await self.db_session.execute(query)
        result = results.first()
        return result

    async def get_label_by_id(self, label_id: int) ->Label:
        query = select(Label).where(Label.id == label_id)
        results = await self.db_session.execute(query)
        result = results.first()
        return result

    async def get_label_articles(self, label_id: int) ->List[article_model.Article]:
        query = select(article_model.Article).filter(article_model.Article.label_id == label_id)
        results = await self.db_session.execute(query)
        result = results.scalars().all()
        return result
