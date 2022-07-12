from typing import List
from pydantic import BaseModel
from typing import Optional




class Source(BaseModel):

    name: str

    image: str
    domain: str
    category_id: int
    link: str 
    link_prefix: Optional[str] = None
    link_type: str
    priority: int

    content_selector: str
    image_selector: str
    author_selector: str
    label_selector: str 

    exception_selector:str

    default_image: Optional[str] = None
    pubDate:  Optional[str] = None
    debug: bool
    disable: bool
    analytics_id: str

    class Config:
        orm_mode = True

class GetAllScource(BaseModel):
    id: int
    name: str
    image: str

    class Config:
        orm_mode = True