from typing import List
from pydantic import BaseModel
from typing import Optional
from schemas import user_schema
from datetime import date


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


class CommentedUser(BaseModel):
    id: str 
    username: str 
    # registered: bool

    class Config:
        orm_mode = True

class CommentReplies(BaseModel):
    id: str 
    user_id: str 
    reply: str 
    date_of_replies: date 
    likes: int

    class Config:
        orm_mode = True

class GetComments(BaseModel):
    id: str 
    user_id: str 
    date_of_comment: date 
    totalreplies: Optional[str] = None
    # article_id: str 
    likes: int 
    comments: str
    commented_user: Optional[CommentedUser]
    comment_replies: List[CommentReplies]


    class Config:
        orm_mode = True


