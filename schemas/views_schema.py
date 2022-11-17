from typing import List
from pydantic import BaseModel
from typing import Optional
from schemas import article_schema

class CreateUserArticleViewsRequest(BaseModel):
    article_id: str 
    start_time: str
    end_time: str 
    total_time_spend: int

    class Config:
        orm_mode = True



class CreateUserArticleViews(CreateUserArticleViewsRequest):
    user_id : str 
    class Config:
        orm_mode = True




