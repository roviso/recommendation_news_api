from typing import List, Union
from pydantic import BaseModel
from typing import Optional
from schemas import author_schema, comments_schema


class Article(BaseModel):
    url: str
    head_image : Optional[str]
    heading : Optional[str]
    date : Optional[str]

    label: Optional[str]

    content : List[Optional[str]]
    additional_img : List[Optional[str]] = None
    source : Optional[str]
    likes: Optional[int]
    shares: Optional[int]
    # class Config:
    #     orm_mode = True

# class CreateArticle(Article):
#     author_id = str
#     type = str
#     class Config:
#         orm_mode = True

class RecommendedArticle(Article):
    author : author_schema.Author
    type : str = "recommended"
    
    class Config:
        orm_mode = True


class CreateLatestArticle(Article):
    author : author_schema.Author
    class Config:
        orm_mode = True


class LatestArticle(RecommendedArticle):
    type : str
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


class GetAllArticle(BaseModel):
    id: str
    url: str
    head_image : Optional[str]
    heading : Optional[str]
    date : Optional[str]

    label: Optional[str]

    content : List[Optional[str]]
    additional_img : List[Optional[str]] = None
    source : Optional[str]
    likes: Optional[int]
    shares: Optional[int]

    type: str 

    author_id: str

    # author: Union[author_schema.AuthorInDB, None] = None
    # comments: comments_schema.GetComment

    class Config:
        orm_mode = True