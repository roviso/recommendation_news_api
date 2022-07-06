
from ast import keyword
from typing import List, Union
from pydantic import BaseModel
from typing import Optional
from schemas import author_schema, comments_schema



class keyword(BaseModel):
    tag: str

    class Config:
        orm_mode = True

class CreateKeyword(keyword):
    keywords_id: str 

    class Config:
        orm_mode = True