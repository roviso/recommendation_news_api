from typing import List, Optional
from sqlalchemy.orm import Session,with_polymorphic, selectinload
from sqlalchemy import update
from sqlalchemy.future import select
# from schemas import article_schema
from models.author_model import Author


class AuthorCrud():
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create_author(self, author: Author):
        self.db_session.add(author)
        await self.db_session.flush()

    async def get_author_by_id(self,author_id: str) -> Author:
        query = select(Author).where(Author.id == author_id)
        results = await self.db_session.execute(query)
        result = results.fetchone()
        return result

    async def get_author_profile(self,author_id: str) -> Author:

        query = select(Author).where(Author.id == author_id).options(selectinload(Author.articles))
        results = await self.db_session.execute(query)
        return results.scalars().all()[0]
        # results = await self.db_session.execute(query)
        # (result,) = results.one()
        # return result

    async def search_author_by_name(self,author_name: str) -> List[Author]:
        query = select(Author).filter(Author.author_name.like(f'{author_name}%'))
        results = await self.db_session.execute(query)
        return results.scalars().all()



    async def get_author_by_name(self,author_name: str) -> Author:
        query = select(Author).where(Author.author_name == author_name)
        results = await self.db_session.execute(query)
        result = results.fetchone()
        return result

    async def get_all_author(self) -> List[Author]:
        query = select(Author).order_by(Author.id)
        results = await self.db_session.execute(query)
        return results.scalars().all()
        # return self.db_session.query(article_model.Article).filter(article_model.Article.url == article_url).first()

    async def update_author(self, author_id: str, author_name: Optional[str], author_img: Optional[str]):
        q = update(Author).where(Author.id == author_id)
        if author_name:
            q = q.values(author_name=author_name)
        if author_img:
            q = q.values(author_img=author_img)
        q.execution_options(synchronize_session="fetch")
        await  self.db_session.execute(q)


# def get_author_by_id(db: Session, author_id: str):
#     # if username in db:
#     #     user_dict = db[username]
#     #     return user_schema.UserInDB(**user_dict)
#     return db.query(author_model.Author).filter(author_model.Author.id == author_id).first()

# def get_author_by_name(db: Session, author_name: str):
#     # if username in db:
#     #     user_dict = db[username]
#     #     return user_schema.UserInDB(**user_dict)
#     return db.query(author_model.Author).filter(author_model.Author.author_name == author_name).first()


# def create_author(db: Session, author: author_model.Author):
#     db.add(author)
#     db.commit()
#     db.refresh(author)
#     print('Created new Author: ',author)
#     return author


