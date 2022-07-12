from typing import List
from pydantic import BaseModel
from typing import Optional



class Author(BaseModel):
    author_name :str
    author_img :str
    source: str

    class Config:
        orm_mode :True
    
class AuthorInDB(Author):
    id :str
    class Config:
        orm_mode :True


    
class GetAllAuthors(BaseModel):
    id: str
    author_name :str
    author_img :str
    source: Optional[str] = None


    class Config:
        orm_mode = True