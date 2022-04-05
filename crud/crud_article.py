from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import update
from sqlalchemy.future import select
# from schemas import article_schema
from models.article_model import Article


class ArticleCrud():
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create_article(self, article: Article):
        self.db_session.add(article)
        await self.db_session.flush()


    async def get_article(self,article_url: str) -> Article:
        query = select(Article).where(Article.url == article_url)
        results = await self.db_session.execute(query)
        (result,) = results.one()
        return result

    async def get_all_article(self) -> List[Article]:
        query = select(Article).order_by(Article.id)
        results = await self.db_session.execute(query)
        return results.scalars().all()
        # return self.db_session.query(article_model.Article).filter(article_model.Article.url == article_url).first()

    async def update_article(self, article_id: str, url: Optional[str], head_image: Optional[str], heading: Optional[str],
        date: Optional[str], content: Optional[str], additional_img: Optional[str],
        source: Optional[str], author_id: Optional[str]
        ):
        q = update(Article).where(Article.id == article_id)
        if url:
            q = q.values(url=url)
        if head_image:
            q = q.values(head_image=head_image)
        if heading:
            q = q.values(heading=heading)
        if date:
            q = q.values(date=date)
        if content:
            q = q.values(content=content)
        if additional_img:
            q = q.values(additional_img=additional_img)
        if source:
            q = q.values(source=source)
        if author_id:
            q = q.values(author_id=author_id)
        q.execution_options(synchronize_session="fetch")
        await  self.db_session.execute(q)



# def get_article(db: Session, article_url: str):
#     # if username in db:
#     #     user_dict = db[username]
#     #     return user_schema.UserInDB(**user_dict)
#     return db.query(article_model.Article).filter(article_model.Article.url == article_url).first()


# def create_article(db: Session, article: article_model.Article):
#     db.add(article)
#     db.commit()
#     db.refresh(article)
#     print('Created new User: ',article)
#     return article
