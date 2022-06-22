from fastapi import FastAPI
from database import engine, Base
from fastapi.logger import logger
from apis.keyword.main import keywordApi
from routers import article,cache, author,user,likes, views, token, latest , comments, replies, follow, bookmarks, profile, search , clicks ,recommend
# , recommendation, 
# import db_loader
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import Page, add_pagination

import os
import sys

from pydantic import BaseSettings


class Settings(BaseSettings):
    # ... The rest of our FastAPI settings

    BASE_URL = "http://localhost:8000"
    USE_NGROK = os.environ.get("USE_NGROK", "False") == "True"


settings = Settings()

def init_webhooks(base_url):
    # Update inbound traffic via APIs to use the public-facing ngrok URL
    pass






app = FastAPI(title='News Recommendation')


if settings.USE_NGROK:
    # pyngrok should only ever be installed or initialized in a dev environment when this flag is set
    from pyngrok import ngrok

    # Get the dev server port (defaults to 8000 for Uvicorn, can be overridden with `--port`
    # when starting the server
    port = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else 8000

    # Open a ngrok tunnel to the dev server
    public_url = ngrok.connect(port).public_url
    logger.info("ngrok tunnel \"{}\" -> \"http://127.0.0.1:{}\"".format(public_url, port))

    # Update any base URLs or webhooks to use the public ngrok URL
    settings.BASE_URL = public_url
    init_webhooks(public_url)


origins = [
    "*"
]


app.add_middleware(
    CORSMiddleware,#/default/extract_keywords_from__get
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/api/keyword", keywordApi)




@app.on_event("startup")
async def startup():
    # create db tables
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        # db_loader.load_model_data()
        await conn.run_sync(Base.metadata.create_all)


# app.include_router(recommendation.router)


app.include_router(search.router)
app.include_router(profile.router)
app.include_router(recommend.router)
app.include_router(clicks.router)

app.include_router(token.router)
app.include_router(user.router)
app.include_router(follow.router)
app.include_router(article.router)
app.include_router(latest.router)
app.include_router(cache.router)
app.include_router(author.router)
app.include_router(likes.router)
app.include_router(bookmarks.router)
app.include_router(views.router)
app.include_router(comments.router)
app.include_router(replies.router)

add_pagination(app)


if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn
    

    uvicorn.run(app, host="0.0.0.0", port=8848, log_level="debug")