from typing import List, Optional

from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import update, delete
from sqlalchemy.future import select
from schemas import follow_schema
from crud import crud_article, crud_author, crud_user
import secrets
from models  import author_model,article_model,user_model
from database import async_session


class Follow():
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.articledb = crud_article.ArticleCrud(db_session)
        self.authordb = crud_author.AuthorCrud(db_session)
        self.userdb = crud_user.UserCrud(db_session)

    async def follow_user(self, follower_following: follow_schema.FollowUser):
        follower = await self.userdb.get_user(follower_following.follower_id)
        temp_follower = user_model.User()
        temp_follower = follower
        following = await self.userdb.get_user(follower_following.following_id)
        temp_following = user_model.User()
        temp_following = following
        if not follower:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such User Found")
        if not following:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such User Found")

        user_following = user_model.UserFollowing(
            follower_id = follower_following.follower_id,
            following_id = follower_following.following_id
        )

        self.db_session.add(user_following)
        await self.db_session.flush()

    async def get_followings(self,user_id):
        query = select(user_model.UserFollowing).where(user_model.UserFollowing.follower_id == user_id)
        results = await self.db_session.execute(query)
        return results.scalars().all()


    # async def follow_user(self, follower_following: follow_schema.FollowUser):
    #     self.db_session.(user_following.insert(), user_id = follower_following.user_id, following_id = follower_following.following_id )
    #     add(user)
    #     await self.db_session.flush()

