from typing import List
from pydantic import BaseModel
from typing import Optional
from schemas import article_schema, author_schema


class User(BaseModel):
    id: str

    class Config:
        orm_mode = True


class UserInDB(User):
    device_id: Optional[str] = None
    device_name: Optional[str] = None
    ip_address: Optional[str] = None

    class Config:
        orm_mode = True



class CreateUserArticleLikes(User):
    article: article_schema.Article
    author: author_schema.Author

    class Config:
        orm_mode = True


class CreateUserArticleViewed(User):
    article: article_schema.Article
    author: author_schema.Author
    viewed: article_schema.ArticleViewed

    class Config:
        orm_mode = True



class CreateUserArticleComments(User):
    article: article_schema.Article
    author: author_schema.Author
    comment: article_schema.ArticleComments

    class Config:
        orm_mode = True

# class User(BaseModel):
#     user_id: str
#     email: Optional[str] = None
#     full_name: Optional[str] = None
    


# class UserInDB(User):
#     disabled: Optional[bool] = None
#     hashed_password: str

#     class Config:
#         orm_mode = True

