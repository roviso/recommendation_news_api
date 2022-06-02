from typing import List
from pydantic import BaseModel
from typing import Optional

class FollowUser(BaseModel):
    follower_id : str 
    following_id: str 

