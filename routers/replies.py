from fastapi import APIRouter,status,Depends
from models import comments_model
from schemas import replies_schema
from typing import List, Optional
import secrets
from database import async_session
from sqlalchemy.orm import Session
import database
from crud.crud_replies import Replies


router = APIRouter(
    prefix = "/replies",
    tags=['replies']
)



@router.post('/', status_code = status.HTTP_201_CREATED)
async def comment_replies(replies_comment:replies_schema.CreateReplies, async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            replies = Replies(session)
            return await replies.create_replies(replies_comment)


@router.post('/like_replies', status_code = status.HTTP_201_CREATED)
async def like_replies(replies_like: replies_schema.LikeReplies, async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            replies = Replies(session)
            return await replies.like_replies(replies_like)


    
