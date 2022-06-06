from typing import List
from pydantic import BaseModel
from typing import Optional
from schemas import article_schema


class UserProfile(BaseModel):
    id: str
    username: str
    password: str
    first_name: Optional[str] = None 
    last_name: Optional[str] = None
    email: Optional[str] = None
    followers: int 
    following: int

    

    # bookmarked_articles : List[article_schema.GetAllArticle]

    class Config:
        orm_mode = True


