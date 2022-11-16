from fastapi import FastAPI
from fastapi_pagination import add_pagination

from apis.newstalk.routers import user, token, profile, recommend, top, latest, author, source, bookmarks, comments

newstalkApi = FastAPI(title="NewsTalk", openapi_url="/openapi.json")

newstalkApi.include_router(user.router)

newstalkApi.include_router(token.router)

newstalkApi.include_router(profile.router)

newstalkApi.include_router(recommend.router)

newstalkApi.include_router(top.router)

newstalkApi.include_router(latest.router)

newstalkApi.include_router(source.router)

newstalkApi.include_router(author.router)

newstalkApi.include_router(bookmarks.router)

newstalkApi.include_router(comments.router)
add_pagination(newstalkApi)