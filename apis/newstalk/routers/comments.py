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
from models import user_model
from apis.newstalk.routers.user import get_current_user

router = APIRouter(
    prefix = "/comments",
    tags=['comments']
)



@router.post('/', status_code = status.HTTP_201_CREATED)
async def comment_article(article_commented_data: comments_schema.CreateCommentsRequest, async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    article_commented = comments_schema.CreateComments(user_id =current_user.id ,
    article_id = article_commented_data.article_id,
    date_of_comment = article_commented_data.date_of_comment,
    comment = article_commented_data.comment
    )
    async with async_session as session:
        async with session.begin():
            comments = Comments(session)
            return await comments.create_comment(article_commented)

@router.get('/get_comments')
async def get_comment_by_id(comment_id: str, async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    async with async_session as session:
        async with session.begin():
            comments = Comments(session)
            return await comments.get_comment_by_id(comment_id)

@router.post('/like_comment', status_code = status.HTTP_201_CREATED)
async def like_article_comment(comment_id: str, async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    comment_like = comments_schema.LikeComments(user_id = current_user.id,
    comment_id = comment_id)
    # comment_like.comment.id = comment_id
    # # return comment_like
    async with async_session as session:
        async with session.begin():
            comments = Comments(session)
            return await comments.like_comment(comment_like)

@router.get('/liked_or_not')
async def get_comment_liked(comment_id: str,async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    user_id = current_user.id
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
async def get_article_comments(article_id: str,current_user: user_model.User = Depends(get_current_user)):
    res = []
    async with async_session() as session:
        async with session.begin():
            comments = Comments(session)
            all_comments = await comments.get_comments_by_article(article_id)
            return all_comments

    
