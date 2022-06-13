from fastapi import FastAPI
from database import engine, Base
from routers import article,cache, author,user,likes, views, token, latest , comments, replies, follow, bookmarks, profile, search
# , explore,redirect
# , recommendation, 
import db_loader
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import Page, add_pagination


app = FastAPI(title='News Recommendation')

origins = [
    "*"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.on_event("startup")
async def startup():
    # create db tables
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        # db_loader.load_model_data()
        await conn.run_sync(Base.metadata.create_all)


# app.include_router(recommendation.router)

# app.include_router(explore.router)
app.include_router(search.router)
app.include_router(profile.router)
# app.include_router(redirect.router)
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