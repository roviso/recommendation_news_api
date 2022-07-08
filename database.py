from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base,sessionmaker
from typing import  AsyncIterator
from config import settings


# SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:ravi123@localhost:3306/atm_logs"
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
# print(SQLALCHEMY_DATABASE_URL)

engine = create_async_engine(SQLALCHEMY_DATABASE_URL,future=True, echo=True)

db_engine = create_engine(settings.SYNC_DB_URL)

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()

async def get_session():
    session = async_session()
    try:
        yield session
    finally:
        await session.close()



async def get_db() -> AsyncIterator[AsyncSession]:
    async with async_session() as session:
        yield session
