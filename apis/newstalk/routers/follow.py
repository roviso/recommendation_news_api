from fastapi import APIRouter,status,Depends
from crud.crud_follow import Follow
from schemas import follow_schema
from typing import List, Optional
import secrets
from database import async_session
from sqlalchemy.orm import Session
import database
from fastapi_pagination import paginate, LimitOffsetPage
from models import user_model
from apis.newstalk.routers.user import get_current_user

router = APIRouter(
    prefix = "/follow",
    tags=['follow']
)


@router.post('/followuser', status_code = status.HTTP_201_CREATED)
async def follow_user(user_id: str, async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    follower_following = follow_schema.FollowUser(
        follower_id= current_user.id,
        following_id = user_id
    )
    async with async_session as session:
        async with session.begin():
            follow = Follow(session)
            return await follow.follow_user(follower_following)


@router.post('/isfollowinguser', status_code = status.HTTP_201_CREATED)
async def isfollowinguser(user_id: str, async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    follower_following=  follow_schema.FollowUser(
        follower_id= current_user.id,
        following_id = user_id
    )
    async with async_session as session:
        async with session.begin():
            follow = Follow(session)
            isfollowing = await follow.check_user_following(follower_following)
            return {'followstatus': True if isfollowing else False}


@router.post('/unfollowuser')
async def unfollow_user(user_id: str, async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    follower_following=  follow_schema.FollowUser(
        follower_id= current_user.id,
        following_id = user_id
    )
    async with async_session as session:
        async with session.begin():
            follow = Follow(session)
            return await follow.unfollow_user(follower_following)


@router.post('/followauthor', status_code = status.HTTP_201_CREATED)
async def follow_author(author_id: str, async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    follower_following=  follow_schema.FollowAuthor(
        user_id = current_user.id,
        author_id =  author_id
    )
    async with async_session as session:
        async with session.begin():
            follow = Follow(session)
            return await follow.follow_author(follower_following)


@router.post('/isfollowingauthor', status_code = status.HTTP_201_CREATED)
async def isfollowingauthor(author_id: str, async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    follower_following=  follow_schema.FollowAuthor(
        user_id = current_user.id,
        author_id =  author_id
    )
    async with async_session as session:
        async with session.begin():
            follow = Follow(session)
            isfollowing = await follow.check_author_following(follower_following)
            return {'followstatus': True if isfollowing else False}

@router.post('/unfollowauthor', status_code = status.HTTP_201_CREATED)
async def unfollow_author(author_id: str, async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    follower_following=  follow_schema.FollowAuthor(
        user_id = current_user.id,
        author_id =  author_id
    )
    async with async_session as session:
        async with session.begin():
            follow = Follow(session)
            return await follow.unfollow_author(follower_following)


@router.post('/followsource', status_code = status.HTTP_201_CREATED)
async def follow_source(source_id: str, async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    follower_following = follow_schema.FollowSource(
        user_id = current_user.id, 
        source_id = source_id
    )
    async with async_session as session:
        async with session.begin():
            follow = Follow(session)
            return await follow.follow_source(follower_following)


@router.post('/isfollowingsource', status_code = status.HTTP_201_CREATED)
async def isfollowingsource(source_id: str, async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    follower_following = follow_schema.FollowSource(
        user_id = current_user.id, 
        source_id = source_id
    )
    async with async_session as session:
        async with session.begin():
            follow = Follow(session)
            isfollowing = await follow.check_source_following(follower_following)
            return {'followstatus': True if isfollowing else False}


@router.post('/unfollowsource', status_code = status.HTTP_201_CREATED)
async def unfollow_source(source_id: str,  async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    follower_following = follow_schema.FollowSource(
        user_id = current_user.id, 
        source_id = source_id
    )
    async with async_session as session:
        async with session.begin():
            follow = Follow(session)
            return await follow.unfollow_source(follower_following)



@router.get("/get_user_followings" , response_model = LimitOffsetPage[follow_schema.UserResponse])
async def get_user_followings(async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    user_id = current_user.id
    async with async_session as session:
        async with session.begin():
            follow = Follow(session)
            followings =  await follow.get_followings(user_id)
            return paginate(followings)


@router.get("/get_followings_counts")
async def get_user_followings_count(async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    user_id = current_user.id
    async with async_session as session:
        async with session.begin():
            follow = Follow(session)
            followings_count =  await follow.get_following_count(user_id)
            return {"count": followings_count}


@router.get("/get_author_followings", response_model = LimitOffsetPage[follow_schema.AuthorResponse])
async def get_author_followings(async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    user_id = current_user.id
    async with async_session as session:
        async with session.begin():
            follow = Follow(session)
            followings =  await follow.get_author_followings(user_id)
            return paginate(followings)



@router.get("/get_source_followings", response_model = LimitOffsetPage[follow_schema.SourceResponse] )
async def get_source_followings(async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    user_id = current_user.id
    async with async_session as session:
        async with session.begin():
            follow = Follow(session)
            followings =  await follow.get_source_followings(user_id)
            return paginate(followings)



@router.get("/get_user_followers", response_model = LimitOffsetPage[follow_schema.UserResponse])
async def get_user_followers(async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    user_id = current_user.id
    async with async_session as session:
        async with session.begin():
            follow = Follow(session)

            followers =  await follow.get_followers(user_id)
            return paginate(followers)


@router.get("/get_followers_counts")
async def get_user_followers_count(async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    user_id = current_user.id
    async with async_session as session:
        async with session.begin():
            follow = Follow(session)
            followings_count =  await follow.get_followers_count(user_id)
            return {"count": followings_count}


@router.get("/get_author_followers", response_model = LimitOffsetPage[follow_schema.UserResponse])
async def get_author_followers(author_id: str, async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    async with async_session as session:
        async with session.begin():
            follow = Follow(session)
            followers =  await follow.get_author_followers(author_id)
            return paginate(followers)




@router.get("/get_source_followers", response_model = LimitOffsetPage[follow_schema.UserResponse])
async def get_source_followers(source_id: int, async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    async with async_session as session:
        async with session.begin():
            follow = Follow(session)
            followers =  await follow.get_source_followers(source_id)
            return paginate(followers)
