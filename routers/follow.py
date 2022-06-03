from fastapi import APIRouter,status,Depends
from crud.crud_follow import Follow
from models.article_model import Article
from schemas import follow_schema
from typing import List, Optional
import secrets
from database import async_session
from sqlalchemy.orm import Session
import database

router = APIRouter(
    prefix = "/follow",
    tags=['follow']
)


@router.post('/', status_code = status.HTTP_201_CREATED)
async def follow_user(follower_following: follow_schema.FollowUser, async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            follow = Follow(session)
            return await follow.follow_user(follower_following)


@router.get("/get_all_followings")
async def read_all_user(user_id: str, async_session: Session = Depends(database.get_session)):
    # return UserCrud.get_user(user_id=current_user.id)\
    async with async_session as session:
        async with session.begin():
            follow = Follow(session)
            followings =  await follow.get_followings(user_id)

            followings_counts = len(followings)

            followings_list = []
            for following in followings:
                followings_list.append(following.following_id)

            return {"count": followings_counts ,
                    "followings": followings_list}

@router.get("/get_all_followers")
async def read_all_user(user_id: str, async_session: Session = Depends(database.get_session)):
    # return UserCrud.get_user(user_id=current_user.id)\
    async with async_session as session:
        async with session.begin():
            follow = Follow(session)

            followers =  await follow.get_followers(user_id)
            follower_counts = len(followers)

            follower_list = []
            for follower in followers:
                follower_list.append(follower.follower_id)
            print(followers,follower_counts)
            return {"count": follower_counts ,
                    "followers": follower_list}
