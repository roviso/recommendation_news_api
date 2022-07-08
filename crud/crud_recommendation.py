from typing import List, Optional
from sqlalchemy.orm import Session,load_only
from sqlalchemy import update
from sqlalchemy.future import select
# from schemas import article_schema
from models import article_model, user_model, comments_model
import pandas as pd
from database import db_engine

class RecommendationCrud():
    def __init__(self, db_session: Session):
        self.db_session = db_session

    
    async def get_user_article(self):
        likes_query = select(user_model.UserArticleLikes)
        fields = ['user_id','article_id']
        viewes_query = select(user_model.UserArticleViewed).options(load_only(*fields))


        likes_df = pd.read_sql(likes_query, db_engine)
        likes_df['score'] = 2.0
        view_df = pd.read_sql(viewes_query, db_engine)
        view_df['score'] = 1.0
        df = pd.concat([likes_df,view_df], ignore_index=True, sort=False)

        df = df.groupby(fields)[['score']].sum().reset_index()

        
        return df