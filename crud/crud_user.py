from re import L
from typing import List, Optional
from sqlalchemy.orm import Session,with_polymorphic,selectinload,joinedload,subqueryload
from sqlalchemy import update
from sqlalchemy.future import select
# from schemas import article_schema
from models.user_model import User,RegisteredUser, UserArticleBookmarks
from models import article_model, user_model, comments_model


class UserCrud():
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create_user(self, user: User):
        self.db_session.add(user)
        await self.db_session.flush()


    async def register_user(self, user_id: str, username: Optional[str], password: Optional[str], first_name: Optional[str],last_name: Optional[str], email: Optional[str] ):
        l = update(User).where(User.id == user_id)
        l = l.values(registered = True)
        l.execution_options(synchronize_session="fetch")
        await self.db_session.execute(l)

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
        await self.db_session.execute(q)


    async def get_user(self,user_id: str) -> User:
        query = select(User).where(User.id == user_id)
        results = await self.db_session.execute(query)
        # result = results.fetchone()
        # return result
        result = results.scalars().one()
        return result

    async def get_user_by_email(self,email: str) -> RegisteredUser:
        # print(f"email give is : {email}, 555555555555555555555555555555555555555555555555555")
        # query = select(RegisteredUser).where(RegisteredUser.email == email)

        # results = await self.db_session.execute(query)
        # print(f"results is {results ,results.scalars().all() }, 666666666666666666666666666666666666666666")
        query = select(RegisteredUser).filter(RegisteredUser.email.ilike(email))
        results = await self.db_session.execute(query)
        (result,) = results.one()

        return result

    async def get_user_profile(self,user_id: str) -> User:
        entity = with_polymorphic(User, RegisteredUser)
        query = select(entity).where(entity.id == user_id)
        # .options(selectinload(entity.user_followings))
        # print(query,111111111111111111111111111111111)
        results = await self.db_session.execute(query)
        # print(results)
        # (result,) = results.one()
        result = results.scalars().one()
        return result

    async def check_user_exists(self,device_id: str,device_name:str) -> User:
        query = select(User).where(User.device_id == device_id,User.device_name == device_name)
        results = await self.db_session.execute(query)
        result = results.fetchone()
        return result

    async def get_registered_user(self,user_id: str) -> RegisteredUser:
        entity = with_polymorphic(User, RegisteredUser)
        query = select(entity).where(entity.id == user_id)
        # print(query,111111111111111111111111111111111)
        results = await self.db_session.execute(query)
        (result,) = results.one()
        return result


    async def search_user_by_name(self,user_name: str) -> List[User]:
        # query = select(User).where(User.username == user_name)
        entity = with_polymorphic(User, RegisteredUser)
        query = select(entity).filter(entity.username.like(f'{user_name}%'))
        # query = select(User).filter(User.username.like(f'{user_name}%'))
        results = await self.db_session.execute(query)
        return results.scalars().all()

    async def get_all_user(self) -> List[User]:
        query = select(User).order_by(User.id)
        results = await self.db_session.execute(query)
        return results.scalars().all()
        # return self.db_session.query(article_model.Article).filter(article_model.Article.url == article_url).first()

    
    async def get_all_registered_user(self) -> List[RegisteredUser]:
        query = select(RegisteredUser).order_by(RegisteredUser.id)
        results = await self.db_session.execute(query)
        return results.scalars().all()


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


    async def upload_profile_Image(self, user_id: str, profile_Image: str):
        q = update(RegisteredUser).where(RegisteredUser.id == user_id).values(profile_Image=profile_Image)
        q.execution_options(synchronize_session="fetch")
        await  self.db_session.execute(q)


    async def get_liked_articles_by_user(self, user_id: str) -> article_model.Article:
        query = select(article_model.Article).join(
            user_model.UserArticleLikes
        ).filter(user_model.UserArticleLikes.user_id == user_id).order_by(article_model.Article.date.desc()).limit(10)
        results = await self.db_session.execute(query)
        result = results.scalars().all()
        return result

    
    async def get_viewed_articles_by_user(self, user_id: str) -> article_model.Article:
        query = select(article_model.Article).join(
            user_model.UserArticleViewed
        ).filter(user_model.UserArticleViewed.user_id == user_id).order_by(user_model.UserArticleViewed.end_time.desc()).limit(30)
        results = await self.db_session.execute(query)
        result = results.scalars().all()
        return result


    async def get_bookmarked_articles_by_user(self, user_id: str) -> article_model.Article:
        query = select(article_model.Article).join(
            user_model.UserArticleBookmarks
        ).filter(user_model.UserArticleBookmarks.user_id == user_id).order_by(article_model.Article.date.desc()).limit(10)
        results = await self.db_session.execute(query)
        result = results.scalars().all()
        return result


    async def get_commented_articles_by_user(self, user_id: str) -> article_model.Article:
        query = select(article_model.Article).join(
            comments_model.Comments
        ).filter(comments_model.Comments.user_id == user_id).order_by(article_model.Article.date.desc()).limit(10)
        results = await self.db_session.execute(query)
        result = results.scalars().all()
        return result


    
    
