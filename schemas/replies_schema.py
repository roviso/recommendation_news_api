from typing import List
from pydantic import BaseModel
from typing import Optional
from schemas import user_schema, article_schema, comments_schema


class Replies(BaseModel):
    id : str
    

class CreateRepliesRequest(BaseModel):
    
    comment_id: str
    date_of_replies: str
    replies: str

    class Config:
        orm_mode = True


class CreateReplies(CreateRepliesRequest):
    user_id: str

    class Config:
        orm_mode = True



# class CreateReplies(user_schema.User):
#     comment: comments_schema.Comment
#     date_of_replies: str
#     replies: str

#     class Config:
#         orm_mode = True



class LikeReplies(BaseModel):
    user_id: str
    replies_id: str

    class Config:
        orm_mode = True


class ArticleReplies(BaseModel):
    username: str
    date_of_comment: str
    replies: str
    likes: int

    class Config:
        orm_mode = True
