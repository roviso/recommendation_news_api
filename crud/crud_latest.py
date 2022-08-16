from typing import List, Optional
from sqlalchemy.orm import Session,joinedload,contains_eager
from sqlalchemy import update
from sqlalchemy.future import select
# from schemas import article_schema
from models.article_model import Article, LatestArticle,AricleKeywords
from crud.crud_article import ArticleCrud
from sqlalchemy import desc

class LatestCrud(ArticleCrud):
    def __init__(self, db_session: Session):
        super().__init__(db_session)
        self.db_session = db_session

    async def create_latest_article(self, latest_article: LatestArticle):
        self.db_session.add(latest_article)
        await self.db_session.flush()

    async def get_article(self,article_id: str) -> LatestArticle:
        query = select(LatestArticle).join(LatestArticle.keywords).join(AricleKeywords.keyword).options(
            contains_eager(LatestArticle.keywords).
            contains_eager(AricleKeywords.keyword)
        ).where(LatestArticle.id == article_id)
        results = await self.db_session.execute(query)
        # result = results.scalars().one()
        # return result
        result = results.fetchone()
        return result

    async def get_article_by_id(self,article_id: str) -> LatestArticle:
        query = select(LatestArticle).where(LatestArticle.id == article_id)
        results = await self.db_session.execute(query)
        result = results.scalars().one()
        return result


    async def get_all_latest_article(self) -> List[LatestArticle]:
        query = select(LatestArticle).order_by(LatestArticle.date.desc())
        results = await self.db_session.execute(query)
        return results.scalars().all()

    async def get_latest_articles(self) ->  List[LatestArticle]:
        query = select(LatestArticle).order_by(LatestArticle.date.desc())
        # .join(LatestArticle.keywords).order_by(LatestArticle.date.desc())
        # .offset(offset).limit(limit)
        results = await self.db_session.execute(query)
        return results.scalars().all()



    async def get_trending_article(self) -> List[LatestArticle]:
        query = select(LatestArticle).join(LatestArticle.keywords).order_by(desc(LatestArticle.likes),desc(LatestArticle.shares)).limit(50)
        results = await self.db_session.execute(query)
        return results.scalars().all()

        

