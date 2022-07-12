from typing import List
from pydantic import BaseModel
from typing import Optional



class LabelSchema(BaseModel):
    label_name: str

    class Config:
        orm_mode = True
  
class GetAllLabel(BaseModel):
    id: int 
    label_name: str 

    class Config:
        orm_mode = True