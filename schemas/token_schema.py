from typing import List
from pydantic import BaseModel
from typing import Optional

class CreateUser(BaseModel):
    device_id: str
    device_name: str
    ip_address: str

    class Config:
        orm_mode = True
        
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    class Config:
        orm_mode = True

class RefreshToken(BaseModel):
    refresh_token: str
    class Config:
        orm_mode = True
class TokenData(BaseModel):
    user_id: Optional[str] = None

