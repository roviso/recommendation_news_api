from fastapi import FastAPI
from models import user_model 
from database import engine
from routers import user, token



user_model.Base.metadata.create_all(bind=engine)


app = FastAPI()


# app.include_router(cashwithdrawal.router)

app.include_router(token.router)

app.include_router(user.router)



if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8848, log_level="debug")