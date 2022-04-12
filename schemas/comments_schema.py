from typing import List
from pydantic import BaseModel
from typing import Optional
from schemas import user_schema, article_schema


class Comment(BaseModel):
    id : str
    


class CreateComments(user_schema.User):
    article: article_schema.RecommendedArticle
    date_of_comment: str
    comment: str

    class Config:
        orm_mode = True



class LikeComments(user_schema.User):
    comment: Comment

    class Config:
        orm_mode = True


class ArticleComments(user_schema.CommentedUsers):
    date_of_comment: str
    comment: str
    likes: int

    class Config:
        orm_mode = True
