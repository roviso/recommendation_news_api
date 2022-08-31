from typing import List, Optional

from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import update, delete
from sqlalchemy.future import select
from schemas import user_schema, likes_schema
from crud import crud_article, crud_author, crud_user
import secrets
from models  import author_model,article_model,user_model



class Likes():
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.articledb = crud_article.ArticleCrud(db_session)
        self.authordb = crud_author.AuthorCrud(db_session)
        self.userdb = crud_user.UserCrud(db_session)

    async def check_liked_articles(self, user_id: str, article_id:str):
        query = select(user_model.UserArticleLikes).where(user_model.UserArticleLikes.article_id == article_id,user_model.UserArticleLikes.user_id == user_id)
        results = await self.db_session.execute(query)
        return results.fetchone()


    async def get_articles_like(self, article_id: str):
        query = select(user_model.User).join(
            user_model.UserArticleLikes
        ).join(
            article_model.Article
        ).filter(article_model.Article.id == article_id)
        # .where(user_model.UserArticleLikes.user_id == user_id)
        results = await self.db_session.execute(query)
        return results.scalars().all()


    async def get_all_liked_articles(self, user_id: str):
        # query = select(user_model.UserArticleLikes).where(user_model.UserArticleLikes.user_id == user_id)
        query = select(article_model.Article).join(
            user_model.UserArticleLikes).filter(user_model.UserArticleLikes.user_id == user_id)
        results = await self.db_session.execute(query)
        return results.scalars().all()

    async def remove_liked_articles(self, user_id: str, article_id:str):
        query = delete(user_model.UserArticleLikes).where(user_model.UserArticleLikes.article_id == article_id,user_model.UserArticleLikes.user_id == user_id)
        await self.db_session.execute(query)

    async def like_article(self, article_liked:likes_schema.CreateUserArticleLikes,):
        user = await self.userdb.get_user(article_liked.user_id)
        article = await self.articledb.get_article_by_id(article_liked.article_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such User Found")

        if not article:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such article Found")


        already_liked = await self.check_liked_articles(user.id,article.id)
        if already_liked:
            await self.remove_liked_articles(user_id = user.id,article_id = article.id)
            await self.articledb.update_like(article_id = article.id, increase_like= None, decrease_like = 1)
            return JSONResponse(status_code=status.HTTP_201_CREATED, content="article Successfully Unliked")

        else:
            like_article = user_model.UserArticleLikes(user_id = user.id,article_id = article.id)
            self.db_session.add(like_article)
            await self.db_session.flush()
            await self.articledb.update_like(article_id = article.id, increase_like = 1, decrease_like=None)
            return JSONResponse(status_code=status.HTTP_201_CREATED, content="article Successfully liked")


    # async def like_article(self, article_liked:user_schema.CreateUserArticleLikes,):
    #     user = await self.userdb.get_user(article_liked.id)
    #     article = await self.articledb.get_article(article_liked.article.url)
    #     author = await self.authordb.get_author_by_name(article_liked.article.author.author_name)

    #     if not user:
    #         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such User Found")
    #     else:
    #         user = user._mapping.User

    #     if not author:
    #         author_id = secrets.token_urlsafe(32)
    #         new_author = author_model.Author(id = author_id,**article_liked.article.author.dict())
    #         print('no author found in db... Adding the author in db.')
    #         try:
    #             await self.authordb.create_author(new_author)

    #             author = new_author
    #             print("Successfully added Author in db")
    #         except:
    #             print("Unable to add author in db")
    #             # return JSONResponse(status_code=status.HTTP_201_CREATED, content=item)
    #             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Author not added in database")
    #     else:
            
    #         author = author._mapping.Author
    #         # print(f"Author already present: {author}")

        
    #     if not article:
    #         article_id = secrets.token_urlsafe(32)
    #         article_dict = article_liked.article.dict()
    #         article_dict['likes'] += 0 ##Increasing like count
    #         article_dict['views'] = 1 ##Increasing views count
    #         del article_dict['author'] 
    #         new_article = article_model.RecommendedArticle(id = article_id,**article_dict,author_id=author.id )
    #         print('no article found in db... Adding the article in db.')
    #         try:
    #             await self.articledb.create_article(new_article)
    
    #             article = new_article
    #             print("Successfully added article in db")

    #         except Exception as e:
    #             print("Unable to add article in db")
    #             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unable to add Article in database, {e}")
    #     else:
    #         article = article._mapping.Article


    #     already_liked = await self.check_liked_articles(user.id,article.id)
    #     if already_liked:
    #         await self.remove_liked_articles(user_id = user.id,article_id = article.id)
    #         await self.articledb.update_like(article_id = article.id, increase_like= None, decrease_like = 1)
    #         return JSONResponse(status_code=status.HTTP_201_CREATED, content="article Successfully Unliked")

    #     else:
    #         like_article = user_model.UserArticleLikes(user_id = user.id,article_id = article.id)
    #         self.db_session.add(like_article)
    #         await self.db_session.flush()
    #         await self.articledb.update_like(article_id = article.id, increase_like = 1, decrease_like=None)
    #         return JSONResponse(status_code=status.HTTP_201_CREATED, content="article Successfully liked")

       