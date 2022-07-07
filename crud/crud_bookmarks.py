from typing import List, Optional

from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import update, delete
from sqlalchemy.future import select
from schemas import bookmarks_schema
from crud import crud_article, crud_author, crud_user
import secrets
from models  import author_model,article_model,user_model



class Bookmarks():
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.articledb = crud_article.ArticleCrud(db_session)
        self.authordb = crud_author.AuthorCrud(db_session)
        self.userdb = crud_user.UserCrud(db_session)

    async def check_bookmarked_articles(self, user_id: str, article_id:str):
        query = select(user_model.UserArticleBookmarks).where(user_model.UserArticleBookmarks.article_id == article_id,user_model.UserArticleBookmarks.user_id == user_id)
        results = await self.db_session.execute(query)
        return results.fetchone()


    async def get_all_bookmarked_articles(self, user_id: str):
        query = select(article_model.Article).where(user_model.User.id == user_id).filter(
            user_model.UserArticleBookmarks.article_id == article_model.Article.id, 
            user_model.UserArticleBookmarks.user_id == user_model.User.id
        )
        results = await self.db_session.execute(query)
        result = results.scalars().all()
        return result

        # query = select(user_model.UserArticleBookmarks).where(user_model.UserArticleBookmarks.user_id == user_id)
        # results = await self.db_session.execute(query)
        # return results.scalars().all()

    async def remove_bookmarked_articles(self, user_id: str, article_id:str):
        query = delete(user_model.UserArticleBookmarks).where(user_model.UserArticleBookmarks.article_id == article_id,user_model.UserArticleBookmarks.user_id == user_id)
        await self.db_session.execute(query)

    async def bookmark_article(self, article_bookmarked:bookmarks_schema.CreateUserArticleBookmarks,):
        user = await self.userdb.get_user(article_bookmarked.user_id)
        article = await self.articledb.get_article_by_id(article_bookmarked.article_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such User Found")
        # else:
        #     user = user._mapping.User

        if not article:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such article Found")
        # else:
        #     article = article._mapping.Article

        already_bookmarked = await self.check_bookmarked_articles(user.id,article.id)
        if already_bookmarked:
            await self.remove_bookmarked_articles(user_id = user.id,article_id = article.id)
            await self.articledb.update_bookmarks(article_id = article.id, increase_bookmark= None, decrease_bookmark = 1)
            return JSONResponse(status_code=status.HTTP_201_CREATED, content="article Bookmark Removed")

        else:
            bookmark_article = user_model.UserArticleBookmarks(user_id = user.id,article_id = article.id)
            self.db_session.add(bookmark_article)
            await self.db_session.flush()
            await self.articledb.update_bookmarks(article_id = article.id, increase_bookmark = 1, decrease_bookmark=None)
            return JSONResponse(status_code=status.HTTP_201_CREATED, content="article Successfully Bookmarked")