from typing import List, Optional

from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import update, delete
from sqlalchemy.future import select
from schemas import user_schema, views_schema
from crud import crud_article, crud_author, crud_user
import secrets
from models.article_model import Article
from models  import author_model,article_model,user_model
from config import timeconfig
from timefhuman import timefhuman


class Views():
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.articledb = crud_article.ArticleCrud(db_session)
        self.authordb = crud_author.AuthorCrud(db_session)
        self.userdb = crud_user.UserCrud(db_session)

    async def check_viewed_articles(self, user_id: str, article_id:str):
        query = select(user_model.UserArticleViewed).where(user_model.UserArticleViewed.article_id == article_id,user_model.UserArticleViewed.user_id == user_id)
        results = await self.db_session.execute(query)
        return results.fetchone()


    async def check_ignored_articles(self, user_id: str, article_id:str):
        query = select(user_model.UserArticleIgnored).where(user_model.UserArticleIgnored.article_id == article_id,user_model.UserArticleIgnored.user_id == user_id)
        results = await self.db_session.execute(query)
        return results.fetchone()


    async def remove_ignored_articles(self, user_id: str, article_id:str):
        query = delete(user_model.UserArticleIgnored).where(user_model.UserArticleIgnored.article_id == article_id,user_model.UserArticleIgnored.user_id == user_id)
        await self.db_session.execute(query)

    async def get_all_viewed_articles(self, user_id: str):
        query = select(user_model.UserArticleViewed).where(user_model.UserArticleViewed.user_id == user_id)
        results = await self.db_session.execute(query)
        return results.scalars().all()

    async def update_views(self, article_id: str, increase_views: Optional[int]):
        article = await self.articledb.get_article_by_id(article_id)
        article = article._mapping.Article
        q = update(Article).where(Article.id == article_id)
        if increase_views:
            print(f"Increasing the Views")
            new_views = (article.views or 0) + increase_views
            q = q.values(views=new_views)
        q.execution_options(synchronize_session="fetch")
        await  self.db_session.execute(q)

    
    async def update_ignores(self, article_id: str, increase_ignores: Optional[int] = None, decrease_ignores: Optional[int] = None):
        article = await self.articledb.get_article_by_id(article_id)
        article = article._mapping.Article
        q = update(Article).where(Article.id == article_id)
        if increase_ignores:
            print(f"Increasing the Ignores")
            if article.ignores == None:
                article.ignores = 0
            new_ignores = (article.ignores or 0) + increase_ignores
            q = q.values(ignores=new_ignores)
        if decrease_ignores:
            print(f"Decrease the Ignores")
            new_ignores = (article.ignores or 0) - decrease_ignores
            q = q.values(ignores=new_ignores)
        q.execution_options(synchronize_session="fetch")
        await  self.db_session.execute(q)


    async def view_article(self, article_viewed:views_schema.CreateUserArticleViews,):
        user = await self.userdb.get_user(article_viewed.user_id)
        article = await self.articledb.get_article_by_id(article_viewed.article_id)
        start_time = timefhuman(article_viewed.viewed.start_time)
        end_time = timefhuman(article_viewed.viewed.end_time)
        total_time_spend = article_viewed.viewed.total_time_spend

        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such User Found")
        else:
            user = user._mapping.User

        if not article:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such article Found")
        else:
            article = article._mapping.Article

        already_ignored = await self.check_ignored_articles(user.id,article.id)
        # already_viewed = await self.check_viewed_articles(user.id,article.id)
        if already_ignored and total_time_spend >= timeconfig.IGNORE_TIME:
            await self.update_ignores(article_id= article.id, decrease_ignores = 1)
            await self.remove_ignored_articles(user.id,article.id)

        

        # if already_viewed:
        #     return JSONResponse(status_code=status.HTTP_201_CREATED, content="article already viewed")
        # else:
        elif total_time_spend < timeconfig.IGNORE_TIME:
            if not already_ignored:
                await self.update_ignores(article_id= article.id, increase_ignores = 1)
                ignore_article = user_model.UserArticleIgnored(user_id = user.id,article_id = article.id,total_time_spend= total_time_spend)
                self.db_session.add(ignore_article)
                await self.db_session.flush()
                return JSONResponse(status_code=status.HTTP_201_CREATED, content="article has been ignored")
            else:
                return JSONResponse(status_code=status.HTTP_201_CREATED, content="article has already been ignored")
        else:
            await self.update_views(article_id= article.id, increase_views = 1)
            view_article = user_model.UserArticleViewed(user_id = user.id,article_id = article.id,start_time= start_time, end_time= end_time, total_time_spend= total_time_spend)
            self.db_session.add(view_article)
            await self.db_session.flush()
            return JSONResponse(status_code=status.HTTP_201_CREATED, content="article Successfully viewed")


    # async def view_article(self, article_viewed:user_schema.CreateUserArticleViewed,):
    #     user = await self.userdb.get_user(article_viewed.id)
    #     article = await self.articledb.get_article(article_viewed.article.url)
    #     author = await self.authordb.get_author_by_name(article_viewed.article.author.author_name)
    #     start_time = timefhuman(article_viewed.viewed.start_time)
    #     end_time = timefhuman(article_viewed.viewed.end_time)
    #     total_time_spend = article_viewed.viewed.total_time_spend

    #     if not user:
    #         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such User Found")
    #     else:
    #         user = user._mapping.User

    #     if not author:
    #         author_id = secrets.token_urlsafe(32)
    #         new_author = author_model.Author(id = author_id,**article_viewed.article.author.dict())
    #         print('no author found in db... Adding the author in db.')
    #         try:
    #             await self.authordb.create_author(new_author)

    #             author = new_author
    #             print("Successfully added article in db")
    #         except:
    #             print("Unable to add author in db")
    #             # return JSONResponse(status_code=status.HTTP_201_CREATED, content=item)
    #             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Author not added in database")
    #     else:
    #         author = author._mapping.Author

    #     if not article:
    #         article_id = secrets.token_urlsafe(32)
    #         article_dict = article_viewed.article.dict()

    #         article_dict['views'] = 0
    #         article_dict['ignores'] = 0

    #         del article_dict['author'] 

    #         new_article = article_model.RecommendedArticle(id = article_id,**article_dict,author_id=author.id )
    #         print('no article found in db... Adding the article in db.')
    #         # author_article = author_model.AuthorArticle(author_id = author.id, article_id = new_article.id)
    #         # create_article(db, new_article)
    #         try:
    #             await self.articledb.create_article(new_article)
    
    #             article = new_article
    #             print("Successfully added article in db")

    #         except Exception as e:
    #             print("Unable to add article in db")
    #             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unable to add Article in database, {e}")
    #     else:
    #         article = article._mapping.Article
        

    #     already_ignored = await self.check_ignored_articles(user.id,article.id)
    #     if already_ignored and total_time_spend >= timeconfig.IGNORE_TIME:
    #         await self.articledb.update_ignores(article_id= article.id, decrease_ignores = 1)
    #         await self.remove_ignored_articles(user.id,article.id)

    #     already_viewed = await self.check_viewed_articles(user.id,article.id)

    #     if already_viewed:
    #         return JSONResponse(status_code=status.HTTP_201_CREATED, content="article already viewed")
    #     else:
    #         if total_time_spend < timeconfig.IGNORE_TIME:
    #             if not already_ignored:
    #                 await self.articledb.update_ignores(article_id= article.id, increase_ignores = 1)
    #                 ignore_article = user_model.UserArticleIgnored(user_id = user.id,article_id = article.id,total_time_spend= total_time_spend)
    #                 self.db_session.add(ignore_article)
    #                 await self.db_session.flush()
    #                 return JSONResponse(status_code=status.HTTP_201_CREATED, content="article has been ignored")
    #             else:
    #                 return JSONResponse(status_code=status.HTTP_201_CREATED, content="article has already been ignored")
    #         else:
    #             await self.articledb.update_views(article_id= article.id, increase_views = 1)
    #             view_article = user_model.UserArticleViewed(user_id = user.id,article_id = article.id,start_time= start_time, end_time= end_time, total_time_spend= total_time_spend)
    #             self.db_session.add(view_article)
    #             await self.db_session.flush()
    #             return JSONResponse(status_code=status.HTTP_201_CREATED, content="article Successfully viewed")