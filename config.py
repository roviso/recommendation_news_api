import os
from dotenv import load_dotenv
from pydantic import BaseSettings
from pathlib import Path
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
from pathlib import Path

class PathConfig:
    PRE_PKL_PATH: Path = Path(
        Path(__file__).parent,'repository','data-processing','processed_data','train_data','pre.pkl'
    ).resolve()

    TRAIN_CSV_PATH: Path = Path(
        Path(__file__).parent,'repository','data','train.csv'
    ).resolve()

    MODEL_PATH: Path = Path(
        Path(__file__).parent,'repository','trained_models','NCF_checkpoint_cuda.pth.tar'
    ).resolve()

    REDIRECT_DICT_PATH: Path = Path(
        Path(__file__).parent,'redirect_dictionary.pkl'
    ).resolve()

pathconfig = PathConfig()


class TimeConfig:
    IGNORE_TIME = 5 #5 second ignore time

timeconfig = TimeConfig()

class Settings:
    PROJECT_NAME:str = "news_recommendation_dev"
    PROJECT_VERSION: str = "1.0.0"

    POSTGRES_USER : str = os.getenv("POSTGRES_USER","ravi")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD","techprixa1234")
    POSTGRES_SERVER : str = os.getenv("POSTGRES_SERVER","127.0.0.1")
    POSTGRES_PORT : str = os.getenv("POSTGRES_PORT",5432) # default postgres port is 5432
    POSTGRES_DB : str = os.getenv("POSTGRES_DB","news_recommendation_dev")
    DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

settings = Settings()


class AuthConfig:
    SECRET_KEY:str  ='9cd0545638607dc61ec68d09f116aa27138b1290273035dd78c7d00480d8c4c8'
    ALGORITHM:str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES:int = 30


authconfig = AuthConfig()


class CacheConfig(BaseSettings):
    redis_url: str = 'redis://localhost'
    URL_EXPIRY_TIME = 60*60*3 ##3 hours
    EXPIRY_TIME = 60 * 60
    LATEST_EXPIRY_TIME = 60*5

cacheconfig = CacheConfig()

