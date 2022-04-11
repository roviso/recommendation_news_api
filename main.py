from fastapi import FastAPI
from database import engine, Base
from routers import article,cache, author,user,likes, views, token, latest , recommendation

app = FastAPI(title='News Recommendation')


@app.on_event("startup")
async def startup():
    # create db tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


app.include_router(recommendation.router)
app.include_router(token.router)
app.include_router(user.router)
app.include_router(article.router)
app.include_router(latest.router)
app.include_router(cache.router)
app.include_router(author.router)
app.include_router(likes.router)
app.include_router(views.router)


if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn
    

    uvicorn.run(app, host="0.0.0.0", port=8848, log_level="debug")