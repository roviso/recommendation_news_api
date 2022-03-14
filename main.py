from fastapi import FastAPI,WebSocket,Cookie,Query,Depends,status
from typing import Optional
from fastapi.responses import HTMLResponse
from models import user_model, author_model
from database import engine
from repository.ncf_recommender.preprocessor import preprocessor
from routers import user, token, recommendation_ncf, latest_recommender
from preprocessor import preprocessor
import aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend


user_model.Base.metadata.create_all(bind=engine)
author_model.Base.metadata.create_all(bind=engine)


app = FastAPI()

app.include_router(latest_recommender.router)

app.include_router(recommendation_ncf.router)



app.include_router(token.router)

app.include_router(user.router)

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url(url="redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")



if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn
    

    uvicorn.run(app, host="0.0.0.0", port=8848, log_level="debug")