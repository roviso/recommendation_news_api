from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import update, delete
from sqlalchemy.future import select
# from schemas import article_schema
from models import user_model, author_model, article_model, comments_model
from crud import crud_article, crud_author, crud_user
from schemas import user_schema, comments_schema
from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
import secrets
from timefhuman import timefhuman

class Comments():
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.articledb = crud_article.ArticleCrud(db_session)
        self.authordb = crud_author.AuthorCrud(db_session)
        self.userdb = crud_user.UserCrud(db_session)

    
    async def get_comment_by_id(self, comment_id: str):
        query = select(comments_model.Comments).where(comments_model.Comments.id == comment_id)
        results = await self.db_session.execute(query)
        return results.fetchone()

    async def get_comments_by_article(self, article_id: str):
        query = select(comments_model.Comments).where(comments_model.Comments.article_id == article_id)
        results = await self.db_session.execute(query)
        return results.scalars().all()


    async def check_comment_likes(self, user_id: str, comment_id:str):
        query = select(comments_model.UserCommentLikes).where(comments_model.UserCommentLikes.comments_id == comment_id,comments_model.UserCommentLikes.user_id == user_id)
        results = await self.db_session.execute(query)
        return results.fetchone()

    
    async def remove_comment_likes(self, user_id: str, comment_id:str):
        query = delete(comments_model.UserCommentLikes).where(comments_model.UserCommentLikes.comments_id == comment_id,comments_model.UserCommentLikes.user_id == user_id)
        await self.db_session.execute(query)

    
    async def get_comment_likes(self, comment_id: str):
        query = select(comments_model.UserCommentLikes).where(comments_model.UserCommentLikes.comments_id == comment_id)
        results = await self.db_session.execute(query)
        return results.scalars().all()


    async def update_comment_likes(self, comment_id: str):
        total_likes = len(await self.get_comment_likes(comment_id))
        q = update(comments_model.Comments).where(comments_model.Comments.id == comment_id)
        q = q.values(likes=total_likes)
        q.execution_options(synchronize_session="fetch")
        await  self.db_session.execute(q)


    
    async def create_comment(self, article_commented:comments_schema.CreateComments,):
        user = await self.userdb.get_user(article_commented.id)
        article = await self.articledb.get_article(article_commented.article.url)
        author = await self.authordb.get_author_by_name(article_commented.article.author.author_name)

        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such User Found")
        else:
            user = user._mapping.User

        if not author:
            author_id = secrets.token_urlsafe(32)
            new_author = author_model.Author(id = author_id,**article_commented.article.author.dict())
            print('no author found in db... Adding the author in db.')
            try:
                await self.authordb.create_author(new_author)

                author = new_author
                print("Successfully added Author in db")
            except:
                print("Unable to add author in db")
                # return JSONResponse(status_code=status.HTTP_201_CREATED, content=item)
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Author not added in database")
        else:
            
            author = author._mapping.Author
            # print(f"Author already present: {author}")

        
        if not article:
            article_id = secrets.token_urlsafe(32)
            article_dict = article_commented.article.dict()
            article_dict['likes'] += 0 ##Increasing like count
            article_dict['views'] = 1 ##Increasing views count
            del article_dict['author'] 
            new_article = article_model.RecommendedArticle(id = article_id,**article_dict,author_id=author.id )
            print('no article found in db... Adding the article in db.')
            try:
                await self.articledb.create_article(new_article)
    
                article = new_article
                print("Successfully added article in db")

            except Exception as e:
                print("Unable to add article in db")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unable to add Article in database, {e}")
        else:
            article = article._mapping.Article

        comment_id = secrets.token_urlsafe(32)

        date_of_comment = timefhuman(article_commented.date_of_comment)
        likes  = 0 

        new_comment = comments_model.Comments(id = comment_id, user_id = user.id, article_id= article.id,date_of_comment =date_of_comment , comments = article_commented.comment, likes = likes)
        self.db_session.add(new_comment)
        await self.db_session.flush()
        await self.articledb.update_comments(article.id)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content="Comment Successfull")


    async def like_comment(self, comment_like: comments_schema.LikeComments,):
        user = await self.userdb.get_user(comment_like.id)
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such User Found")
        else:
            user = user._mapping.User
        
        comment = await self.get_comment_by_id(comment_like.comment.id)
        if not comment:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Comment not Found")
        else:
            comment = comment._mapping.Comments

        already_liked = await self.check_comment_likes(user.id,comment.id)
        if already_liked:
            await self.remove_comment_likes(user_id = user.id,comment_id = comment.id)
            await self.update_comment_likes(comment_id = comment.id)
            return JSONResponse(status_code=status.HTTP_201_CREATED, content="Comment Successfully Unliked")
        else:
            new_comment_like = comments_model.UserCommentLikes(user_id = user.id, comments_id = comment.id)
            self.db_session.add(new_comment_like)
            await self.db_session.flush()
            await self.update_comment_likes(comment_id = comment.id)
            return JSONResponse(status_code=status.HTTP_201_CREATED, content="Comment Successfully liked")


    
    async def update_replies(self, comment_id: str, total_replies : int):
        comment = await self.get_comment_by_id(comment_id)
        comment = comment._mapping.Comments

        q = update(comments_model.Comments).where(comments_model.Comments.id == comment.id)
        q = q.values(totalreplies=total_replies)
        q.execution_options(synchronize_session="fetch")
        await  self.db_session.execute(q)
