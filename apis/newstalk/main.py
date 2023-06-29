from fastapi import FastAPI
from fastapi_pagination import add_pagination

from apis.newstalk.routers import user , token, profile, recommend, search, top, latest, author, source, bookmarks, comments, replies, follow, label, likes, views, keywords

newstalkApi = FastAPI(title="NewsTalk", openapi_url="/openapi.json")


newstalkApi.include_router(user.router)

newstalkApi.include_router(token.router)

newstalkApi.include_router(profile.router)

newstalkApi.include_router(recommend.router)

newstalkApi.include_router(search.router)

newstalkApi.include_router(keywords.router)

newstalkApi.include_router(top.router)

newstalkApi.include_router(latest.router)

newstalkApi.include_router(source.router)

newstalkApi.include_router(author.router)

newstalkApi.include_router(bookmarks.router)

newstalkApi.include_router(comments.router)

newstalkApi.include_router(replies.router)

newstalkApi.include_router(follow.router)

newstalkApi.include_router(likes.router)

newstalkApi.include_router(views.router)

newstalkApi.include_router(label.router)

add_pagination(newstalkApi)