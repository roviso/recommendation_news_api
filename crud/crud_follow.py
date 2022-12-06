from typing import List, Optional

from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import update, delete, func
from sqlalchemy.future import select
from schemas import follow_schema
from crud import crud_article, crud_author, crud_user, crud_source
import secrets
from models  import author_model,article_model,user_model, source_model
from database import async_session



class Follow():
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.articledb = crud_article.ArticleCrud(db_session)
        self.sourcedb = crud_source.SourceCrud(db_session)
        self.authordb = crud_author.AuthorCrud(db_session)
        self.userdb = crud_user.UserCrud(db_session)

    async def follow_user(self, follower_following: follow_schema.FollowUser):
        follower = await self.userdb.get_registerd_user(follower_following.follower_id)
        following = await self.userdb.get_registerd_user(follower_following.following_id)


        if not follower:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such Registered User Found")
        if not following:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such Registered User Found")

        user_following = user_model.UserFollowing(
            follower_id = follower_following.follower_id,
            following_id = follower_following.following_id
        )

        self.db_session.add(user_following)
        await self.db_session.flush()


    async def check_user_following(self, follower_following: follow_schema.FollowUser):
        query = select(user_model.UserFollowing).where(user_model.UserFollowing.follower_id == follower_following.follower_id,user_model.UserFollowing.following_id == follower_following.following_id)
        results = await self.db_session.execute(query)
        return results.fetchone()



    async def unfollow_user(self, follower_following: follow_schema.FollowUser):
        follower = await self.userdb.get_registerd_user(follower_following.follower_id)
        following = await self.userdb.get_registerd_user(follower_following.following_id)


        if not follower:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such Registered User Found")
        if not following:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such Registered User Found")

        # user_following = user_model.UserFollowing(
        #     follower_id = follower_following.follower_id,
        #     following_id = follower_following.following_id
        # )
        query = delete(user_model.UserFollowing).where(user_model.UserFollowing.follower_id == follower_following.follower_id,follower_following.following_id == follower_following.following_id )
        await self.db_session.execute(query)



    
    async def follow_author(self, follower_following: follow_schema.FollowAuthor):
        user = await self.userdb.get_registerd_user(follower_following.user_id)
        author = await self.authordb.get_author(follower_following.author_id)


        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such User Found")
        if not author:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such Author Found")

        user_following = user_model.AuthorFollowing(
            follower_id = follower_following.user_id,
            following_id = follower_following.author_id
        )

        self.db_session.add(user_following)
        await self.db_session.flush()

    
    async def check_author_following(self, follower_following: follow_schema.FollowAuthor):
        query = select(user_model.AuthorFollowing).where(user_model.AuthorFollowing.follower_id == follower_following.user_id,user_model.AuthorFollowing.following_id == follower_following.author_id)
        results = await self.db_session.execute(query)
        return results.fetchone()

    
    async def unfollow_author(self, follower_following: follow_schema.FollowAuthor):
        user = await self.userdb.get_registerd_user(follower_following.user_id)
        author = await self.authordb.get_author(follower_following.author_id)


        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such User Found")
        if not author:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such Author Found")

        query = delete(user_model.AuthorFollowing).where(user_model.AuthorFollowing.follower_id == follower_following.user_id,user_model.AuthorFollowing.following_id == follower_following.author_id )
        await self.db_session.execute(query)


    

    async def follow_source(self, follower_following: follow_schema.FollowSource):
        user = await self.userdb.get_registerd_user(follower_following.user_id)
        source = await self.sourcedb.get_source(follower_following.source_id)


        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such User Found")
        if not source:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such Source Found")

        user_following = user_model.SourceFollowing(
            follower_id = follower_following.user_id,
            following_id = follower_following.source_id
        )

        self.db_session.add(user_following)
        await self.db_session.flush()


    async def check_source_following(self, follower_following: follow_schema.FollowSource):
        query = select(user_model.SourceFollowing).where(user_model.SourceFollowing.follower_id == follower_following.user_id,user_model.SourceFollowing.following_id == follower_following.source_id)
        results = await self.db_session.execute(query)
        return results.fetchone()


    async def unfollow_source(self, follower_following: follow_schema.FollowSource):
        user = await self.userdb.get_registerd_user(follower_following.user_id)
        source = await self.sourcedb.get_source(follower_following.source_id)


        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such User Found")
        if not source:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such Source Found")

        # user_following = user_model.SourceFollowing(
        #     follower_id = follower_following.user_id,
        #     following_id = follower_following.source_id
        # )

        query = delete(user_model.SourceFollowing).where(user_model.SourceFollowing.follower_id == follower_following.user_id,user_model.SourceFollowing.following_id == follower_following.source_id )
        await self.db_session.execute(query)


    async def get_followings(self,user_id) -> List[user_model.RegisteredUser]:
        query = select(user_model.RegisteredUser).join(
            user_model.UserFollowing.followings).filter(user_model.UserFollowing.follower_id == user_id)

        # query = select(user_model.UserFollowing).where(user_model.UserFollowing.follower_id == user_id)
        results = await self.db_session.execute(query)
        return results.scalars().all()

    async def get_author_followings(self,user_id):
        query = select(author_model.Author).join(
            user_model.AuthorFollowing).filter(user_model.AuthorFollowing.follower_id == user_id)

        # query = select(user_model.AuthorFollowing).where(user_model.AuthorFollowing.follower_id == user_id)
        results = await self.db_session.execute(query)
        return results.scalars().all()

    async def get_source_followings(self,user_id):
        query = select(source_model.Source).join(
            user_model.SourceFollowing).filter(user_model.SourceFollowing.follower_id == user_id)
        # query = select(user_model.SourceFollowing).where(user_model.SourceFollowing.follower_id == user_id)
        results = await self.db_session.execute(query)
        return results.scalars().all()



    async def get_following_count(self, user_id):
        query = select(func.count()).select_from(select(user_model.UserFollowing).where(user_model.UserFollowing.follower_id == user_id))
        count = await self.db_session.execute(query)
        return count.scalar_one()

    async def get_followers(self,user_id):
        # user = await self.userdb.get_user(user_id)
        query = select(user_model.RegisteredUser).join(
            user_model.UserFollowing.followers).filter(user_model.UserFollowing.following_id == user_id)

        # query = select(user_model.UserFollowing).where(user_model.UserFollowing.following_id == user_id)
        results = await self.db_session.execute(query)
        return results.scalars().all()


    async def get_author_followers(self,author_id):
        query = select(user_model.RegisteredUser).join(
            user_model.AuthorFollowing).filter(user_model.AuthorFollowing.following_id == author_id)

        # query = select(user_model.AuthorFollowing).where(user_model.AuthorFollowing.following_id == author_id)
        results = await self.db_session.execute(query)
        return results.scalars().all()
        

    async def get_source_followers(self,source_id: int):
        query = select(user_model.RegisteredUser).join(
            user_model.SourceFollowing).filter(user_model.SourceFollowing.following_id == source_id)

        # query = select(user_model.SourceFollowing).where(user_model.SourceFollowing.following_id == source_id)
        results = await self.db_session.execute(query)
        return results.scalars().all()


    async def get_followers_count(self, user_id):
        query = select(func.count()).select_from(select(user_model.UserFollowing).where(user_model.UserFollowing.following_id == user_id))
        count = await self.db_session.execute(query)
        return count.scalar_one()
