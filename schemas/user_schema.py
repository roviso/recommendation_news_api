from typing import List
from pydantic import BaseModel
from typing import Optional
from schemas import article_schema


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

class RegisterUser(BaseModel):
    username: str
    password: str
    first_name: Optional[str] = None 
    last_name: Optional[str] = None
    email: Optional[str] = None
    class Config:
        orm_mode = True

# class CommentedUsers(User):
#     username: str 

#     class Config:
#         orm_mode = True

class EditProfile(BaseModel):
    username: str
    first_name: Optional[str] = None 
    last_name: Optional[str] = None
    # email: Optional[str] = None
    class Config:
        orm_mode = True



class CreateUserArticleLikes(User):
    article: article_schema.RecommendedArticle
    # author: author_schema.Author

    class Config:
        orm_mode = True


class CreateUserArticleLikes(User):
    article: article_schema.RecommendedArticle
    # author: author_schema.Author

    class Config:
        orm_mode = True


class CreateUserArticleViewed(User):
    article: article_schema.RecommendedArticle
    # author: author_schema.Author
    viewed: article_schema.ArticleViewed

    class Config:
        orm_mode = True


class SearchUsers(BaseModel):
    id: str
    username: str 
    profile_Image: Optional[str] = None

    class Config:
        orm_mode = True




class GetRegisteredUsers(BaseModel):
    id: str
    username: str 
    email: str
    first_name: str
    last_name: str

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: str 
    password: str

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

