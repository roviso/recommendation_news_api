from typing import List
from pydantic import BaseModel
from typing import Optional




class Source(BaseModel):

    name: str

    image: str
    domain: str
    link: str 


    content_selector: str
    image_selector: str
    author_img_selector: str
    author_name_selector: str

    label_selector: str 

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


