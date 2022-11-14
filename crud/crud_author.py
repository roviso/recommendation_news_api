from typing import List, Optional
from sqlalchemy.orm import Session,with_polymorphic, selectinload
from sqlalchemy import update
from sqlalchemy.future import select
# from schemas import article_schema
from models.author_model import Author
from models import article_model
from crud import crud_follow

class AuthorCrud():
    def __init__(self, db_session: Session):
        self.db_session = db_session
        # self.followcrud = crud_follow.Follow(db_session)

    async def create_author(self, author: Author):
        self.db_session.add(author)
        await self.db_session.flush()

    async def get_author(self,author_id: str) -> Author:
        query = select(Author).where(Author.id == author_id)
        results = await self.db_session.execute(query)
        result = results.scalars().one()
        return result

    async def get_author_by_id(self,author_id: str) -> Author:
        query = select(Author).where(Author.id == author_id)
        results = await self.db_session.execute(query)
        result = results.fetchone()
        return result

    async def get_author_profile(self,author_id: str) -> Author:
        query = select(Author).where(Author.id == author_id).options(selectinload(Author.articles))
        results = await self.db_session.execute(query)
        author_profile =  results.scalars().all()[0]

        followcrud = crud_follow.Follow(self.db_session)


        follower_count = await followcrud.get_author_followers(author_id)
        following_count = await followcrud.get_author_followings(author_id)
        total_articles = author_profile.articles
        total_likes = sum(articles.__dict__['likes'] for articles in total_articles)
        total_views = sum(articles.__dict__['views'] for articles in total_articles)

            
        setattr(author_profile,'followers',int(len(follower_count)))
        setattr(author_profile,'following',int(len(following_count)))
        setattr(author_profile,'total_articles',len(total_articles))
        setattr(author_profile,'total_likes',total_likes)
        setattr(author_profile,'total_views',total_views)

        return author_profile



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
        result = results.first()
        return result

    async def get_all_author(self) -> List[Author]:
        query = select(Author).order_by(Author.id)
        results = await self.db_session.execute(query)
        return results.scalars().all()
        # return self.db_session.query(article_model.Article).filter(article_model.Article.url == article_url).first()


    async def get_author_articles(self, author_id: str) ->List[article_model.Article]:
        query = select(article_model.Article).filter(article_model.Article.author_id == author_id)
        results = await self.db_session.execute(query)
        result = results.scalars().all()
        return result


    async def get_top_authors(self) -> List[Author]:
        all_authors = await self.get_all_author()
        all_author_profiles = [await self.get_author_profile(author.id) for author in all_authors]
        # top_author_profiles = sorted(all_author_profiles, key=lambda x: (x['followers'],x['total_articles'],x['total_likes'],x['total_views']))
        top_author_profiles = sorted(all_author_profiles, key=lambda x: (-x.total_views, -x.total_likes, -x.followers))
        return top_author_profiles


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


