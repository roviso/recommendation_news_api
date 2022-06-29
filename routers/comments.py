from fastapi import APIRouter,status,Depends
from models import comments_model
from schemas import comments_schema
from typing import List, Optional
import secrets
from database import async_session
from sqlalchemy.orm import Session
import database
from crud.crud_comments import Comments
from crud.crud_replies import Replies


router = APIRouter(
    prefix = "/comments",
    tags=['comments']
)



@router.post('/', status_code = status.HTTP_201_CREATED)
async def comment_article(article_commented: comments_schema.CreateComments, async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            comments = Comments(session)
            return await comments.create_comment(article_commented)

@router.get('/get_comments')
async def get_comment_by_id(comment_id: str, async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            comments = Comments(session)
            return await comments.get_comment_by_id(comment_id)

@router.post('/like_comment', status_code = status.HTTP_201_CREATED)
async def comment_article(comment_like: comments_schema.LikeComments, async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            comments = Comments(session)
            return await comments.like_comment(comment_like)

@router.get('/liked_or_not')
async def get_comment_by_id(comment_id: str, user_id: str ,async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            comments = Comments(session)
            liked = await comments.check_comment_likes(user_id, comment_id)
            if not liked:
                liked = False
            else:
                liked = True

            total_likes = await comments.get_comment_likes(comment_id)
            return {
                "liked": liked, 
                "total_likes": len(total_likes)
            }


@router.get('/get_article_comments', response_model=List[comments_schema.GetComments])
async def get_article_comments(article_id: str):
    res = []
    async with async_session() as session:
        async with session.begin():
            comments = Comments(session)
            # replies = Replies(session)
            all_comments = await comments.get_comments_by_article(article_id)

            # for comment in all_comments:
            #     response_dict = {}
            #     user_dict = {}
            #     user = await comments.userdb.get_user(comment.user_id)
            #     user = user._mapping.User
            #     user_dict['user_id'] = user.id
            #     user_dict['username'] = user.username
                
            #     response_dict['commented_by'] = user_dict
            #     # response_dict['id'] = comment.id
            #     # response_dict['date_of_comment'] = comment.date_of_comment
            #     response_dict['comments'] = comment
            #     # response_dict['likes'] = comment.likes
            #     response_dict['replies'] = await replies.get_replies_by_comment(comment.id)

            #     res.append(response_dict)

    return all_comments

    
