from typing import List, Optional

from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import update, delete
from sqlalchemy.future import select
from schemas import clicks_schema
from crud import crud_article, crud_author, crud_user
from helper.username_generator import username_generator
import secrets
from models  import author_model,article_model,user_model,click_model
from datetime import datetime


class ClicksCrud():
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.articledb = crud_article.ArticleCrud(db_session)
        self.authordb = crud_author.AuthorCrud(db_session)
        self.userdb = crud_user.UserCrud(db_session)

    async def check_article_is_clicked(self, user_id: str, article_id:str):
        query = select(click_model.Clicks).where(click_model.Clicks.article_id == article_id,click_model.Clicks.user_id == user_id)
        results = await self.db_session.execute(query)
        return results.fetchone()


    async def click_article(self, article_clicked:clicks_schema.CreateUserArticleClicks,):
        user = await self.userdb.get_user(article_clicked.user_id)

        if not user:
            # raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such User Found")
            username = username_generator.generate_username(1)[0]
            user = user_model.User(
                    id = article_clicked.user_id,
                    username = username,
                    device_id = "from web",
                    device_name = "from web",
                    ip_address = "from web",
                    registered = False
                )
            self.userdb.create_user(user)


            
        article = await self.articledb.search_article(article_clicked.article_id)

        
        if not article:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No Article in database")


        date_of_click = datetime.now()
        referrer = article_clicked.referrer

        already_clicked = await self.check_article_is_clicked(user.id,article.id)

        if already_clicked:
            await self.articledb.update_views(article_id = article.id, increase_view= 1)
        else:
            clicked_article = click_model.Clicks(user_id = user.id,article_id = article.id, date_of_click= date_of_click, referrer=referrer)
            self.db_session.add(clicked_article)
            await self.db_session.flush()
            await self.articledb.update_views(article_id = article.id, increase_view = 1)
            return JSONResponse(status_code=status.HTTP_201_CREATED, content="article Successfully clicked")

       