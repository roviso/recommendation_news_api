from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import update, delete
from sqlalchemy.future import select
# from schemas import article_schema
from models import comments_model
from crud import  crud_user, crud_comments
from schemas import user_schema, comments_schema, replies_schema
from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
import secrets
from timefhuman import timefhuman

class Replies():
    def __init__(self, db_session: Session):
        self.db_session = db_session
        
        self.userdb = crud_user.UserCrud(db_session)
        self.commentsdb = crud_comments.Comments(db_session)

    
    async def get_replies_by_id(self, replies_id: str) -> comments_model.Replies:
        query = select(comments_model.Replies).where(comments_model.Replies.id == replies_id)
        results = await self.db_session.execute(query)
        # return results.fetchone()
        result = results.scalars().one()
        return result


    async def get_replies_by_comment(self, comment_id: str):
        query = select(comments_model.Replies).where(comments_model.Replies.comment_id == comment_id)
        results = await self.db_session.execute(query)
        return results.scalars().all()



    async def check_replies_likes(self, user_id: str, replies_id:str):
        query = select(comments_model.UserRepliesLikes).where(comments_model.UserRepliesLikes.replies_id == replies_id,comments_model.UserRepliesLikes.user_id == user_id)
        results = await self.db_session.execute(query)
        return results.fetchone()

    
    async def remove_replies_likes(self, user_id: str, replies_id:str):
        query = delete(comments_model.UserRepliesLikes).where(comments_model.UserRepliesLikes.replies_id == replies_id,comments_model.UserRepliesLikes.user_id == user_id)
        await self.db_session.execute(query)

    async def get_replies_likes(self, replies_id: str):
        query = select(comments_model.UserRepliesLikes).where(comments_model.UserRepliesLikes.replies_id == replies_id)
        results = await self.db_session.execute(query)
        return results.scalars().all()

    async def update_replies_like(self,  replies_id: str,):
        total_likes = len(await self.get_replies_likes(replies_id))
        q = update(comments_model.Replies).where(comments_model.Replies.id == replies_id)
        q = q.values(likes=total_likes)
        q.execution_options(synchronize_session="fetch")
        await  self.db_session.execute(q)



    
    async def create_replies(self, replies_comment:replies_schema.CreateReplies,):
        user = await self.userdb.get_user(replies_comment.user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such User Found")
            
        comment = await self.commentsdb.get_comment_by_id(replies_comment.comment_id,replies_comment.user_id)

        if not comment:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such Comment Found")


        replies_id = secrets.token_urlsafe(32)

        date_of_replies = timefhuman(replies_comment.date_of_replies)
        likes  = 0 

        new_replies = comments_model.Replies(id = replies_id, comment_id = comment.id, user_id= user.id,date_of_replies = date_of_replies, reply = replies_comment.replies, likes = likes)
        self.db_session.add(new_replies)
        await self.db_session.flush()

        totalreplies = len(await self.get_replies_by_comment(comment.id))
        await self.commentsdb.update_replies(comment.id, totalreplies)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content="replies Successful")


    async def like_replies(self, replies_like: replies_schema.LikeReplies,):
        user = await self.userdb.get_user(replies_like.user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such User Found")

        
        replies = await self.get_replies_by_id(replies_like.replies_id)
        if not replies:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reply not Found")


        already_liked = await self.check_replies_likes(user.id,replies.id)
        if already_liked:
            await self.remove_replies_likes(user_id = user.id,replies_id = replies.id)
            await self.update_replies_like(replies_id = replies.id)
            return JSONResponse(status_code=status.HTTP_201_CREATED, content="Reply Successfully Unliked")
        else:
            new_replies_like = comments_model.UserRepliesLikes(user_id = user.id, replies_id = replies.id)
            self.db_session.add(new_replies_like)
            await self.db_session.flush()
            await self.update_replies_like(replies_id = replies.id)
            return JSONResponse(status_code=status.HTTP_201_CREATED, content="Reply Successfully liked")