from typing import List
from pydantic import BaseModel
from typing import Optional
from schemas import article_schema, user_schema




class CreateUserArticleClicks(BaseModel):
    user_id : str 
    article_id: str 
    referrer: Optional[str]

    class Config:
        orm_mode = True


# class Clicks(user_schema.User):
#     s: str 

#     class Config:
#         orm_mode = True