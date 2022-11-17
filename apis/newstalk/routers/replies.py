from fastapi import APIRouter,status,Depends
from models import comments_model
from schemas import replies_schema
from typing import List, Optional
import secrets
from database import async_session
from sqlalchemy.orm import Session
import database
from crud.crud_replies import Replies
from models import user_model
from apis.newstalk.routers.user import get_current_user

router = APIRouter(
    prefix = "/replies",
    tags=['replies']
)



@router.post('/', status_code = status.HTTP_201_CREATED)
async def comment_replies(replies_comment:replies_schema.CreateRepliesRequest, async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    replies_comment = replies_schema.CreateReplies(
        user_id= current_user.id,
        comment_id= replies_comment.comment_id,
    date_of_replies= replies_comment.date_of_replies,
    replies= replies_comment.replies
    )
    async with async_session as session:
        async with session.begin():
            replies = Replies(session)
            return await replies.create_replies(replies_comment)


@router.post('/like_replies', status_code = status.HTTP_201_CREATED)
async def like_replies(replies_id: str, async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    replies_like = replies_schema.LikeReplies(
        user_id= current_user.id,
        replies_id= replies_id
    )
    async with async_session as session:
        async with session.begin():
            replies = Replies(session)
            return await replies.like_replies(replies_like)


    
