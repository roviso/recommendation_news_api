from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import update
from sqlalchemy.future import select
# from schemas import article_schema
from models.user_model import User,RegisteredUser


class UserCrud():
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create_user(self, user: User):
        self.db_session.add(user)
        await self.db_session.flush()
        return user

    async def register_user(self, registered: RegisteredUser):
        self.db_session.add(registered)
        await self.db_session.flush()


    async def get_user(self,user_id: str) -> User:
        query = select(User).where(User.id == user_id)
        results = await self.db_session.execute(query)
        (result,) = results.one()
        return result

    async def get_all_user(self) -> List[User]:
        query = select(User).order_by(User.id)
        results = await self.db_session.execute(query)
        return results.scalars().all()
        # return self.db_session.query(article_model.Article).filter(article_model.Article.url == article_url).first()


    async def update_user(self, user_id: str, username: Optional[str], password: Optional[str], first_name: Optional[str],last_name: Optional[str], email: Optional[str] ):
        q = update(RegisteredUser).where(RegisteredUser.id == user_id)
        if username:
            q = q.values(username=username)
        if password:
            q = q.values(password=password)
        if first_name:
            q = q.values(first_name=first_name)
        if last_name:
            q = q.values(last_name=last_name)
        if email:
            q = q.values(email=email)
        q.execution_options(synchronize_session="fetch")
        await  self.db_session.execute(q)
