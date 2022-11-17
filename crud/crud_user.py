from re import L
from typing import List, Optional
from sqlalchemy.orm import Session,with_polymorphic,selectinload,joinedload,subqueryload
from sqlalchemy import update
from sqlalchemy.future import select
# from schemas import article_schema
from models.user_model import User,RegisteredUser, UserArticleBookmarks,NonRegisteredUser
from models import article_model, user_model, comments_model
from crud import crud_follow

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

    
    async def update_profile_pic(self, user_id: str, profile_Image_path: str):
        q = update(RegisteredUser).where(RegisteredUser.id == user_id)
        q = q.values(profile_Image=profile_Image_path)
        q.execution_options(synchronize_session="fetch")
        await self.db_session.execute(q)



    async def get_user(self,user_id: str) -> User:
        query = select(User).where(User.id == user_id)
        results = await self.db_session.execute(query)
        result = results.scalars().one()
        # (result,) = results.one()
        return result

    
    async def get_registerd_user(self,user_id: str) -> RegisteredUser:
        query = select(RegisteredUser).where(RegisteredUser.id == user_id)
        results = await self.db_session.execute(query)
        result = results.scalars().one()
        return result


    async def check_user_exists_by_email(self,email: str)-> RegisteredUser:
        query = select(RegisteredUser).where(RegisteredUser.email == email)
        results = await self.db_session.execute(query)
        result = results.fetchone()
        return result

    async def get_user_by_email(self,email: str) -> RegisteredUser:
        query = select(RegisteredUser).where(RegisteredUser.email == email)
        results = await self.db_session.execute(query)
        result = results.scalars().one()
        return result

    async def get_user_profile(self,user_id: str) -> User:
        entity = with_polymorphic(User, RegisteredUser)
        query = select(entity).where(entity.id == user_id)
        results = await self.db_session.execute(query)
        user_profile = results.scalars().one()

        followcrud = crud_follow.Follow(self.db_session)

        follower_count = await followcrud.get_followers_count(user_id)
        following_count = await followcrud.get_following_count(user_id)

        setattr(user_profile,'followers',int(follower_count))
        setattr(user_profile,'following',int(following_count))
        return user_profile


    async def get_top_users(self,) -> List[RegisteredUser]:
        all_users = await self.get_all_registered_user()
        all_user_profiles = [await self.get_user_profile(user.id) for user in all_users]
        top_user_profiles = sorted(all_user_profiles, key=lambda x: (-x.followers))
        return top_user_profiles



    async def check_user_exists(self,device_id: str,device_name:str) -> User:
        query = select(User).where(User.device_id == device_id,User.device_name == device_name)
        results = await self.db_session.execute(query)
        result = results.fetchone()
        return result

    async def get_existing_user(self,device_id: str,device_name:str) -> User:
        query = select(User).where(User.device_id == device_id,User.device_name == device_name)
        results = await self.db_session.execute(query)
        result = results.scalars().one()
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

    

    
    async def get_all_registered_user(self) -> List[RegisteredUser]:
        query = select(RegisteredUser).order_by(RegisteredUser.id)
        results = await self.db_session.execute(query)
        return results.scalars().all()

    async def get_all_nonregistered_user(self) -> List[NonRegisteredUser]:
        query = select(NonRegisteredUser).order_by(NonRegisteredUser.id)
        results = await self.db_session.execute(query)
        return results.scalars().all()

    async def get_all_user(self) -> List[User]:
        # query = select(User).order_by(User.id)
        # results = await self.db_session.execute(query)
        # return results.scalars().all()
        registereduser = await self.get_all_registered_user()
        nonregistereduser = await self.get_all_nonregistered_user()
        registereduser.extend(nonregistereduser)
        # print(f"all users arerere: {registereduser}, *********************************")
        return registereduser
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
        return 