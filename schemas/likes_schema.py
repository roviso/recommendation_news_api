from typing import List
from pydantic import BaseModel
from typing import Optional

class CreateUserArticleLikes(BaseModel):
    user_id : str 
    article_id: str 

