from typing import List
from pydantic import BaseModel
from typing import Optional
from schemas import article_schema

class CreateUserArticleViews(BaseModel):
    user_id : str 
    article_id: str 
    viewed: article_schema.ArticleViewed

