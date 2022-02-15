from typing import List
from pydantic import BaseModel
from typing import Optional




class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    


class UserInDB(User):
    disabled: Optional[bool] = None
    hashed_password: str

    class Config:
        orm_mode = True

