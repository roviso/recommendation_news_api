from typing import List, Optional

from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import update, delete
from sqlalchemy.future import select
from schemas import bookmarks_schema
from crud import crud_article,crud_keywords ,crud_author, crud_user
import secrets
from models  import author_model,article_model,user_model
from sqlalchemy import desc


class KeywordsCrud():
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.articledb = crud_article.ArticleCrud(db_session)

        # self.userdb = crud_user.UserCrud(db_session)

    async def create_keywords(self, keyword: article_model.Keywords):
        self.db_session.add(keyword)
        await self.db_session.flush()

    async def delete_keyword(self, keyword_id: int):
        query = delete(article_model.AricleKeywords).where(article_model.AricleKeywords.keywords_id == keyword_id)
        query = delete(article_model.Keywords).where(article_model.Keywords.id == keyword_id)
        await self.db_session.execute(query)

    async def get_keyword(self,keyword_id: int) -> article_model.Keywords:
        query = select(article_model.Keywords).where(article_model.Keywords.id == keyword_id)
        results = await self.db_session.execute(query)
        # result = results.fetchone()
        # return result
        result = results.scalars().one()
        return result

    async def get_keyword_by_tag(self,tag: str) -> article_model.Keywords:
        query = select(article_model.Keywords).where(article_model.Keywords.tag == tag)
        results = await self.db_session.execute(query)
        result = results.fetchone()
        return result


    async def check_article_keyword(self, tag_id:int, article_id: str) -> article_model.AricleKeywords :
        query = select(article_model.AricleKeywords).filter((article_model.AricleKeywords.article_id == article_id) & (article_model.AricleKeywords.keywords_id == tag_id))
        # .where(article_model.AricleKeywords.keywords_id == tag_id and article_model.AricleKeywords.article_id == article_id)
        results = await self.db_session.execute(query)
        result = results.fetchone()
        return result

    async def search_articles_by_keywords(self, tag: str) -> article_model.Article:
        query = select(article_model.Article).join(
            article_model.AricleKeywords
        ).join(
            article_model.Keywords
        ).filter(article_model.Keywords.tag == tag).order_by(article_model.Article.date.desc())
        results = await self.db_session.execute(query)
        result = results.scalars().all()
        return result
    

    async def link_article_keyword(self, article_keyword: article_model.AricleKeywords):
        article = await self.articledb.search_article(article_keyword.article_id)         
        if not article:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such Article Found")

        keyword = await self.get_keyword(article_keyword.keywords_id)
        if not keyword:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Keyword not found")
        
        aleady_exists = await self.check_article_keyword(keyword.id, article.id)

        if not aleady_exists:
            print(f"Adding keywords to article: {article.id}")
            self.db_session.add(article_keyword)
            await self.db_session.flush()
        
        else:
            print(f"keyword: {article_keyword.keywords_id} already exists in the article: {article_keyword.article_id}")


    async def get_article_no_keyword(self):
        query = select(article_model.Article).filter(~article_model.Article.keywords.any())
        results = await self.db_session.execute(query)
        result = results.scalars().all()
        return result