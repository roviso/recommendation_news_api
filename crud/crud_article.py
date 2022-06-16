from typing import List, Optional
from sqlalchemy.orm import Session,joinedload,contains_eager
from sqlalchemy import update
from sqlalchemy.future import select
# from schemas import article_schema
from models.article_model import Article,RecommendedArticle, LatestArticle,AricleKeywords
from crud.crud_comments import Comments


class ArticleCrud():
    def __init__(self, db_session: Session):
        self.db_session = db_session
        


    async def create_article(self, article: Article):
        self.db_session.add(article)
        await self.db_session.flush()


    async def get_article(self,article_url: str) -> Article:
        query = select(Article).where(Article.url == article_url)
        results = await self.db_session.execute(query)
        result = results.fetchone()
        return result

    async def get_article_by_id(self,article_id: str) -> Article:
        query = select(Article).where(Article.id == article_id)
        results = await self.db_session.execute(query)
        result = results.fetchone()
        return result

    async def get_all_articles_by_id(self, article_ids: list, offset , limit) -> List[Article]:
        query = select(Article).filter(Article.id.in_(article_ids)).order_by(Article.date.desc()).offset(offset).limit(limit)
        results = await self.db_session.execute(query)
        
        return results.scalars().all()


    async def search_article(self,article_id: str) -> Article:
        # query = select(Article).where(Article.id==article_id).order_by(Article.date.desc())
        # results = await self.db_session.execute(query)
        # result = results.scalars().one()
        # return result
        return await self.db_session.get(Article, article_id, populate_existing=True)
        

    async def get_all_article(self, offset , limit) -> List[Article]:
        query = select(Article).order_by(Article.date.desc()).offset(offset).limit(limit)
        results = await self.db_session.execute(query)
        return results.scalars().all()
        # return self.db_session.query(article_model.Article).filter(article_model.Article.url == article_url).first()

    async def get_all_recommended_article(self):
        query = select(Article).order_by(Article.date)
        results = await self.db_session.execute(query)
        return results.scalars().all()


    async def update_article(self, article_id: str, url: Optional[str], head_image: Optional[str], heading: Optional[str],
        date: Optional[str], content: Optional[str], additional_img: Optional[str],
        source: Optional[str], author_id: Optional[str], label: Optional[str]
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
        if label:
            q = q.values(label= label)
        q.execution_options(synchronize_session="fetch")
        await  self.db_session.execute(q)

    async def update_like(self, article_id: str, increase_like: Optional[int]= None, decrease_like: Optional[int]= None,):
        article = await self.get_article_by_id(article_id)
        article = article._mapping.Article
        q = update(Article).where(Article.id == article_id)
        if increase_like:
            print(f"Increasing the likes")
            new_like = (article.likes or 0) + increase_like
            q = q.values(likes=new_like)
        if decrease_like:
            print(f"Decreasing the likes")
            new_like = (article.likes or 0) - decrease_like
            q = q.values(likes=new_like)
        q.execution_options(synchronize_session="fetch")
        await  self.db_session.execute(q)

    
    async def update_bookmarks(self, article_id: str, increase_bookmark: Optional[int]= None, decrease_bookmark: Optional[int]= None,):
        article = await self.get_article_by_id(article_id)
        article = article._mapping.Article
        q = update(Article).where(Article.id == article_id)
        if increase_bookmark:
            print(f"Increasing the likes")
            new_bookmark = (article.bookmarks or 0) + increase_bookmark
            q = q.values(bookmarks=new_bookmark)
        if decrease_bookmark:
            print(f"Decreasing the likes")
            new_bookmark = (article.bookmarks or 0) - decrease_bookmark
            q = q.values(bookmarks=new_bookmark)
        q.execution_options(synchronize_session="fetch")
        await  self.db_session.execute(q)

    

    async def update_comments(self,  article_id: str,):
        article = await self.get_article_by_id(article_id)
        article = article._mapping.Article
        commentdb = Comments(self.db_session)
        total_comments = len(await commentdb.get_comments_by_article(article_id))
        q = update(Article).where(Article.id == article_id)
        q = q.values(total_comments=total_comments)
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
