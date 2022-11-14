from typing import List
from pydantic import BaseModel
from typing import Optional
from schemas import article_schema


class UserProfile(BaseModel):
    id: str
    username: str
    # password: str
    first_name: Optional[str] = None 
    last_name: Optional[str] = None
    email: Optional[str] = None
    registered: bool
    followers: int 
    following: int
    profile_Image: Optional[str] = None

    class Config:
        orm_mode = True


class AuthorProfile(BaseModel):
    id: str
    author_name: str
    author_img: Optional[str] = None 
    source_id: int

    followers: int 
    following: int
    total_articles: int
    total_likes: int
    total_views: int


    class Config:
        orm_mode = True


class SourceProfile(BaseModel):
    id: str
    name: str
    image: Optional[str] = None 
    domain: str

    followers: int 
    total_articles: int
    total_likes: int
    total_views: int


    class Config:
        orm_mode = True