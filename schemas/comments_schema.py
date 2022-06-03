from typing import List
from pydantic import BaseModel
from typing import Optional
from schemas import user_schema



# class GetComment(BaseModel):
#     id : str
#     user_id: str
#     date_of_comment: str
#     comments: str

#     class Config:
#         orm_mode = True

class CreateComments(BaseModel):
    user_id : str 
    article_id: str 
    date_of_comment: str
    comment: str

    class Config:
        orm_mode = True


class Comment(BaseModel):
    id : str
    

class LikeComments(BaseModel):
    user_id: str
    comment: Comment

    class Config:
        orm_mode = True


class ArticleComments():
    username: str
    date_of_comment: str
    comment: str
    likes: int

    class Config:
        orm_mode = True


