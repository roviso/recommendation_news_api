from typing import List
from pydantic import BaseModel
from typing import Optional

class CreateUserArticleLikes(BaseModel):
    user_id : str 
    article_id: str 
    class Config:
        orm_mode = True

class GetUserArticleLikes(BaseModel):
    user_id : str 
    article_id: str
    class Config:
        orm_mode = True

class LikedUser(BaseModel):
    id: str 
    username: str 
    profile_Image: Optional[str]
    # registered: bool

    class Config:
        orm_mode = True

class GetUserArticleLikesResponse(BaseModel):
    liked: bool 
    total_likes: int 
    liked_users: Optional[List[LikedUser]]

