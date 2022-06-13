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
from sqlalchemy import desc


class KeywordsCrud():
    def __init__(self, db_session: Session):
        self.db_session = db_session
        # self.articledb = crud_article.ArticleCrud(db_session)
        # self.authordb = crud_author.AuthorCrud(db_session)
        # self.userdb = crud_user.UserCrud(db_session)


    async def search_articles_by_keywords(self, tag: str) -> article_model.Article:
        query = select(article_model.Article).join(
            article_model.AricleKeywords
        ).join(
            article_model.Keywords
        ).filter(article_model.Keywords.tag == tag).order_by(article_model.Article.date.desc())
        results = await self.db_session.execute(query)
        result = results.scalars().all()
        return result