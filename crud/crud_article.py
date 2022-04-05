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
        q = await self.db_session.execute(select(Article).order_by(Article.id))
        # return self.db_session.query(article_model.Article).filter(article_model.Article.url == article_url).first()



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
