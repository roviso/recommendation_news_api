from typing import List, Optional

from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, update, delete
from sqlalchemy.future import select

from crud import crud_article, crud_author, crud_user,crud_source

from models.article_model import Article
from models  import author_model,article_model,user_model, source_model
from config import timeconfig
from timefhuman import timefhuman


class SearchCrud():
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.articledb = crud_article.ArticleCrud(db_session)
        self.authordb = crud_author.AuthorCrud(db_session)
        self.userdb = crud_user.UserCrud(db_session)
        self.sourcedb = crud_source.SourceCrud(db_session)


    async def search_string(self, search_str: str):
        articles = await self.search_article(search_str)
        author = await self.search_author(search_str)
        users = await self.search_user(search_str)
        sources = await self.search_source(search_str)
        # results = articles.union(users).union(sources).union(author)
        return articles,author,users,sources


    async def search_article(self, search_str: str):
        query = select(article_model.Article).filter(article_model.Article.heading.ilike(f'%{search_str}%'))
        results = await self.db_session.execute(query)
        result = results.scalars().all()
        return result

    async def search_user(self, search_str: str):
        query = select(user_model.User).filter(user_model.User.username.ilike(f'%{search_str}%'))
        results = await self.db_session.execute(query)
        result = results.scalars().all()
        return result

    async def search_source(self, search_str: str):
        query = select(source_model.Source).filter(source_model.Source.name.ilike(f'%{search_str}%'))
        results = await self.db_session.execute(query)
        result = results.scalars().all()
        return result

    async def search_author(self, search_str: str):
        query = select(author_model.Author).filter(author_model.Author.author_name.ilike(f'%{search_str}%'))
        results = await self.db_session.execute(query)
        result = results.scalars().all()
        return result