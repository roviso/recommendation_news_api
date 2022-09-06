from fastapi import APIRouter,status,Depends
from crud.crud_follow import Follow
from models.article_model import Article
from schemas import follow_schema
from typing import List, Optional
import secrets
from database import async_session
from sqlalchemy.orm import Session
import database
from fastapi_pagination import paginate, LimitOffsetPage

router = APIRouter(
    prefix = "/follow",
    tags=['follow']
)


@router.post('/followuser', status_code = status.HTTP_201_CREATED)
async def follow_user(follower_following: follow_schema.FollowUser, async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            follow = Follow(session)
            return await follow.follow_user(follower_following)


@router.post('/isfollowinguser', status_code = status.HTTP_201_CREATED)
async def isfollowinguser(follower_following: follow_schema.FollowUser, async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            follow = Follow(session)
            isfollowing = await follow.check_user_following(follower_following)
            return {'followstatus': True if isfollowing else False}


@router.post('/unfollowuser')
async def unfollow_user(follower_following: follow_schema.FollowUser, async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            follow = Follow(session)
            return await follow.unfollow_user(follower_following)


@router.post('/followauthor', status_code = status.HTTP_201_CREATED)
async def follow_author(follower_following: follow_schema.FollowAuthor, async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            follow = Follow(session)
            return await follow.follow_author(follower_following)


@router.post('/isfollowingauthor', status_code = status.HTTP_201_CREATED)
async def isfollowingauthor(follower_following: follow_schema.FollowAuthor, async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            follow = Follow(session)
            isfollowing = await follow.check_author_following(follower_following)
            return {'followstatus': True if isfollowing else False}

@router.post('/unfollowauthor', status_code = status.HTTP_201_CREATED)
async def unfollow_author(follower_following: follow_schema.FollowAuthor, async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            follow = Follow(session)
            return await follow.unfollow_author(follower_following)


@router.post('/followsource', status_code = status.HTTP_201_CREATED)
async def follow_source(follower_following: follow_schema.FollowSource, async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            follow = Follow(session)
            return await follow.follow_source(follower_following)


@router.post('/isfollowingsource', status_code = status.HTTP_201_CREATED)
async def isfollowingsource(follower_following: follow_schema.FollowSource, async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            follow = Follow(session)
            isfollowing = await follow.check_source_following(follower_following)
            return {'followstatus': True if isfollowing else False}


@router.post('/unfollowsource', status_code = status.HTTP_201_CREATED)
async def unfollow_source(follower_following: follow_schema.FollowSource, async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            follow = Follow(session)
            return await follow.unfollow_source(follower_following)



@router.get("/get_user_followings" , response_model = LimitOffsetPage[follow_schema.UserResponse])
async def get_user_followings(user_id: str, async_session: Session = Depends(database.get_session)):
    # return UserCrud.get_user(user_id=current_user.id)\
    async with async_session as session:
        async with session.begin():
            follow = Follow(session)
            followings =  await follow.get_followings(user_id)

            # followings_counts = len(followings)

            # followings_list = []
            # for following in followings:
            #     followings_list.append(following)
            # print(followings)
            return paginate(followings)
            # return {"count": followings_counts ,
            #         "followings": followings_list}

@router.get("/get_followings_counts")
async def get_user_followings_count(user_id: str, async_session: Session = Depends(database.get_session)):
    # return UserCrud.get_user(user_id=current_user.id)\
    async with async_session as session:
        async with session.begin():
            follow = Follow(session)
            followings_count =  await follow.get_following_count(user_id)
            return {"count": followings_count}


@router.get("/get_author_followings", response_model = LimitOffsetPage[follow_schema.AuthorResponse])
async def get_author_followings(user_id: str, async_session: Session = Depends(database.get_session)):
    # return UserCrud.get_user(user_id=current_user.id)\
    async with async_session as session:
        async with session.begin():
            follow = Follow(session)
            followings =  await follow.get_author_followings(user_id)
            return paginate(followings)

            # author_followings_counts = len(followings)

            # author_followings_list = []
            # for following in followings:
            #     author_followings_list.append(following)

            # return {"count": author_followings_counts ,
            #         "followings": author_followings_list}



@router.get("/get_source_followings", response_model = LimitOffsetPage[follow_schema.SourceResponse] )
async def get_source_followings(user_id: str, async_session: Session = Depends(database.get_session)):
    # return UserCrud.get_user(user_id=current_user.id)\
    async with async_session as session:
        async with session.begin():
            follow = Follow(session)
            followings =  await follow.get_source_followings(user_id)
            return paginate(followings)

            # source_followings_counts = len(followings)

            # source_followings_list = []
            # for following in followings:
            #     source_followings_list.append(following)

            # return {"count": source_followings_counts ,
            #         "followings": source_followings_list}





@router.get("/get_user_followers", response_model = LimitOffsetPage[follow_schema.UserResponse])
async def get_user_followers(user_id: str, async_session: Session = Depends(database.get_session)):
    # return UserCrud.get_user(user_id=current_user.id)\
    async with async_session as session:
        async with session.begin():
            follow = Follow(session)

            followers =  await follow.get_followers(user_id)
            return paginate(followers)
            # follower_counts = len(followers)

            # follower_list = []
            # for follower in followers:
            #     follower_list.append(follower)
            # print(followers,follower_counts)
            # return {"count": follower_counts ,
            #         "followers": follower_list}


@router.get("/get_followers_counts")
async def get_user_followers_count(user_id: str, async_session: Session = Depends(database.get_session)):
    # return UserCrud.get_user(user_id=current_user.id)\
    async with async_session as session:
        async with session.begin():
            follow = Follow(session)
            followings_count =  await follow.get_followers_count(user_id)
            return {"count": followings_count}


@router.get("/get_author_followers", response_model = LimitOffsetPage[follow_schema.UserResponse])
async def get_author_followers(author_id: str, async_session: Session = Depends(database.get_session)):
    # return UserCrud.get_user(user_id=current_user.id)\
    async with async_session as session:
        async with session.begin():
            follow = Follow(session)

            followers =  await follow.get_author_followers(author_id)
    return paginate(followers)
            # follower_counts = len(followers)

            # user_follower_list = []
            # for follower in followers:
            #     user_follower_list.append(follower)
            # print(followers,follower_counts)
            # return {"count": follower_counts ,
            #         "followers": user_follower_list}



@router.get("/get_source_followers", response_model = LimitOffsetPage[follow_schema.UserResponse])
async def get_source_followers(source_id: int, async_session: Session = Depends(database.get_session)):
    # return UserCrud.get_user(user_id=current_user.id)\
    async with async_session as session:
        async with session.begin():
            follow = Follow(session)

            followers =  await follow.get_source_followers(source_id)
            return paginate(followers)
            # follower_counts = len(followers)

            # user_follower_list = []
            # for follower in followers:
            #     user_follower_list.append(follower)
            # print(followers,follower_counts)
            # return {"count": follower_counts ,
            #         "followers": user_follower_list}
