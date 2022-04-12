from typing import List
from pydantic import BaseModel
from typing import Optional
from schemas import user_schema, article_schema, comments_schema


class Replies(BaseModel):
    id : str
    


class CreateReplies(user_schema.User):
    comment: comments_schema.Comment
    date_of_replies: str
    replies: str

    class Config:
        orm_mode = True



class LikeReplies(user_schema.User):
    replies: Replies

    class Config:
        orm_mode = True


class ArticleReplies(user_schema.CommentedUsers):
    date_of_comment: str
    replies: str
    likes: int

    class Config:
        orm_mode = True
