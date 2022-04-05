# from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base,sessionmaker

from config import settings


# SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:ravi123@localhost:3306/atm_logs"
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
# print(SQLALCHEMY_DATABASE_URL)

engine = create_async_engine(SQLALCHEMY_DATABASE_URL,future=True, echo=True)

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()

def get_db():
    db = async_session()
    try:
        yield db
    finally:
        db.close()

