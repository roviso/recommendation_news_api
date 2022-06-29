from ast import keyword
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
    likes: Optional[int] = 0
    shares: Optional[int] = 0
    class Config:
        orm_mode = True

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


class CreateLatestArticle(BaseModel):
    # author : author_schema.Author
    url: str
    head_image : Optional[str]
    heading : Optional[str]
    date : Optional[str]

    label: Optional[str]

    content : List[Optional[str]]
    additional_img : List[Optional[str]] = None
    source : Optional[str]
    likes: Optional[int] = 0
    shares: Optional[int] = 0


    views: Optional[int] = 0
    ignores: Optional[int] = 0
    total_comments: Optional[int] = 0
    bookmarks: Optional[int] = 0
    author_id: str
    type : str
    class Config:
        orm_mode = True


class LatestArticle(Article):
    # author : author_schema.Author
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

class SearchArticleByTag(BaseModel):
    id: str
    url: str
    head_image : Optional[str]
    heading : Optional[str]
    date : Optional[str]
    label: Optional[str]
    source : Optional[str]
    likes: Optional[int]
    shares: Optional[int]

    class Config:
        orm_mode = True


class KeywordTags(BaseModel):
    tag: str

    class Config:
        orm_mode = True

class KeywordArticle(BaseModel):
    keywords_id: str 
    keyword: KeywordTags

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
    additional_img : Optional[List[Optional[str]]] = None
    source : Optional[str]

    views: Optional[int]
    likes: Optional[int]
    shares: Optional[int]
    total_comments: Optional[int]
    bookmarks: Optional[int]
    
    type: str 


    author: author_schema.GetAllAuthors

    keywords: Optional[List[KeywordArticle]] = None

    class Config:
        orm_mode = True