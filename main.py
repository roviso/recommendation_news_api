from fastapi import FastAPI
from database import engine,Base, db_engine
# from sqlalchemy.ext.declarative import declarative_base
# from fastapi.logger import logger
from apis.sugariri.main import sugaApi
from apis.newstalk.main import newstalkApi
# from apis.keyword.main import keywordApi
# from apis.tts.main import ttsApi
from routers import clicks
# ,user, scrap,source
# article,cache,source, author,user,likes, views, token, latest , top ,comments, replies, follow, bookmarks, profile, , search , clicks , scrap, keywords , label  
#  ,recommend
# , recommendation, 
import db_loader
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import Page, add_pagination
from models import label_model
from fastapi.responses import FileResponse

# from pydantic import BaseSettings
from apis.newstalk.routers import recommend


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


app.mount("/api/sugariri", sugaApi)
app.mount("/api/newstalk", newstalkApi)

# app.mount("/api/tts", ttsApi)

# async def add_column(db_engine):
#     async with db_engine.acquire() as connection:
#         # Start a transaction
#         trans = await connection.begin()
#         # Add the new column to the table
#         await connection.execute(
#             "ALTER TABLE user ADD COLUMN status STRING DEFAULT 'active'"
#         )
#         # Commit the transaction
#         await trans.commit()

def add_column():
    connection = db_engine.connect()
    # Base = declarative_base()
    trans = connection.begin()
    query = f"ALTER TABLE public.user ADD COLUMN status VARCHAR(255) DEFAULT 'active'" 
    # query = f"ALTER TABLE clicks DROP status"
    # connection.execute(query)

    connection.execute(
    # 'ALTER TABLE user ADD COLUMN status VARCHAR DEFAULT "active" ;'
        query
    )
    trans.commit()
    connection.close()


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        # add_column()
        await conn.run_sync(Base.metadata.create_all)
        await recommend.startup_event()


    
    #     #await conn.run_sync(Base.metadata.drop_all)
    #     # db_loader.load_model_data()
    #     # await conn.run_sync(Base.metadata.drop_all(tables=['user']))
        
    #     # trans = await conn.begin()
    #     await conn.execute(
    #         "ALTER TABLE user ADD COLUMN status STRING DEFAULT 'active"
    #     )
    #     await conn.commit()
    

@app.get("/privacypolicy")  
def read_privacypolicy():
    return FileResponse("repository/staticHtml/PrivacyPolicyNewsTalk.html")


@app.get("/termsandconditions")  
def read_termsandconditions():
    return FileResponse("repository/staticHtml/TermsandConditionsNewsTalk.html")     

# app.include_router(scrap.router)
# app.include_router(source.router)

# app.include_router(recommendation.router)
# app.include_router(keywords.router)

# app.include_router(search.router)
# app.include_router(recommend.router)

# app.include_router(profile.router)


# app.include_router(top.router)

# app.include_router(user.router)
# app.include_router(follow.router)



# app.include_router(article.router)
# app.include_router(latest.router)


# app.include_router(cache.router)
# app.include_router(author.router)

# app.include_router(label.router)
app.include_router(clicks.router)
# app.include_router(likes.router)
# app.include_router(bookmarks.router)
# app.include_router(views.router)

# app.include_router(comments.router)
# app.include_router(replies.router)

# app.include_router(token.router)

add_pagination(app)


if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn
    

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
