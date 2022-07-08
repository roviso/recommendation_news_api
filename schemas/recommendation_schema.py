from pydantic import BaseModel



class RecommendationSchema(BaseModel):
    user_id: str
    article_id : str

    class Config:
        orm_mode = True