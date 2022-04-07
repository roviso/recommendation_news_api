from typing import List
from pydantic import BaseModel
from typing import Optional



class Article(BaseModel):
    url: str
    head_image : Optional[str]
    heading : Optional[str]
    date : Optional[str]

    content : Optional[str]
    additional_img : Optional[str] = None
    source : Optional[str]

class CreateArticle(Article):
    author_id = str
    class Config:
        orm_mode = True

class ArticleInDB(Article):
    id: str
    class Config:
        orm_mode = True


class ArticleViewed(BaseModel):
    start_time: str
    end_time: str 
    total_time_spend: int


    class Config:
        orm_mode = True


class ArticleComments(BaseModel):
    comment: str 

    class Config:
        orm_mode = True

