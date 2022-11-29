
from typing import List, Optional
from sqlalchemy.orm import Session,with_polymorphic,selectinload,joinedload,subqueryload
from sqlalchemy import update
from sqlalchemy.future import select
from models import tasks_model

class TasksCrud():
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create_tasks(self, tasks: tasks_model.Tasks):
        self.db_session.add(tasks)
        await self.db_session.flush()


    async def check_tasks(self, task_id: str):
        query = select(tasks_model.Tasks).where(tasks_model.Tasks.id == task_id)
        results = await self.db_session.execute(query)
        result = results.fetchone()
        return result

    async def get_tasks(self, task_id: str) -> tasks_model.Tasks:
        query = select(tasks_model.Tasks).where(tasks_model.Tasks.id == task_id)
        results = await self.db_session.execute(query)
        result = results.scalars().one()
        return result

    
