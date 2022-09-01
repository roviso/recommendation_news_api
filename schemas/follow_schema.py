from typing import List
from pydantic import BaseModel
from typing import Optional

class FollowUser(BaseModel):
    follower_id : str 
    following_id: str 

    class Config:
        orm_mode :True

class FollowAuthor(BaseModel):
    user_id : str 
    author_id: str

    class Config:
        orm_mode :True 


class FollowSource(BaseModel):
    user_id : str 
    source_id: int

    class Config:
        orm_mode :True 


    
class UserResponse(BaseModel):
    id: str
    username: str 
    profile_Image: Optional[str] = None

    class Config:
        orm_mode = True


class AuthorResponse(BaseModel):
    id: str
    author_name :str
    author_img : Optional[str] = None
    class Config:
        orm_mode = True


class SourceResponse(BaseModel):
    id: int
    name: str
    image: str

    class Config:
        orm_mode = True