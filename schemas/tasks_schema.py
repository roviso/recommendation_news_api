
from pydantic import BaseModel

class tasks(BaseModel):
    id: str
    status: str 
    result: str

    class Config:
        orm_mode = True
