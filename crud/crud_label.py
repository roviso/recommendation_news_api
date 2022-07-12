from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.future import select
# from schemas import article_schema
from models.label_model import Label
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


    async def get_label_by_name(self, label_name) ->Label:
        query = select(Label).where(Label.label_name == label_name)
        results = await self.db_session.execute(query)
        result = results.first()
        return result
