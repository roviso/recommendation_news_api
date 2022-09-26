from fastapi import FastAPI
from database import engine, Base
# from fastapi.logger import logger
# from apis.keyword.main import keywordApi
# from apis.tts.main import ttsApi
from routers import article,cache,source, author,user,likes, views, token, latest , comments, replies, follow, bookmarks, profile, scrap, search , clicks , scrap, keywords , label ,recommend
# , recommendation, 
import db_loader
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import Page, add_pagination
from models import label_model

# from pydantic import BaseSettings



app = FastAPI(title='News Recommendation')



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


# app.mount("/api/keyword", keywordApi)


# app.mount("/api/tts", ttsApi)

@app.on_event("startup")
async def startup():
    # create db tables
    async with engine.begin() as conn:
        #await conn.run_sync(Base.metadata.drop_all)
        # db_loader.load_model_data()
        await conn.run_sync(Base.metadata.create_all)

app.include_router(scrap.router)
app.include_router(source.router)

# app.include_router(recommendation.router)
app.include_router(keywords.router)

app.include_router(search.router)
app.include_router(recommend.router)

app.include_router(profile.router)


app.include_router(user.router)
app.include_router(follow.router)







app.include_router(article.router)
app.include_router(latest.router)




app.include_router(cache.router)
app.include_router(author.router)


app.include_router(label.router)

app.include_router(clicks.router)
app.include_router(likes.router)
app.include_router(bookmarks.router)
app.include_router(views.router)

app.include_router(comments.router)
app.include_router(replies.router)

app.include_router(token.router)

add_pagination(app)


if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn
    

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
