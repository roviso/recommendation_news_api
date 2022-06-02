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
            return await follow.get_followings(user_id)
