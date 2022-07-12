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
        Path(__file__).parent,'repository','trained_models','NCF_checkpoint_cpu.pth.tar'
    ).resolve()

    REDIRECT_DICT_PATH: Path = Path(
        Path(__file__).parent,'redirect_dictionary.pkl'
    ).resolve()

pathconfig = PathConfig()


class ImgConfig:
    IMG_SAVED_PATH = Path(
        Path(__file__).parent,'repository','profileImg'
    ).resolve()
    IMG_SAVED_PATH = str(IMG_SAVED_PATH) + '/'

imgconfig = ImgConfig()

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
    POSTGRES_DB : str = os.getenv("POSTGRES_DB","news_recommendation")
    DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
    SYNC_DB_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

settings = Settings()


class AuthConfig:
    SECRET_KEY:str  ='9cd0545638607dc61ec68d09f116aa27138b1290273035dd78c7d00480d8c4c8'
    ALGORITHM:str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES:int = 30


authconfig = AuthConfig()


class CacheConfig(BaseSettings):
    redis_url: str = 'redis://localhost'
    URL_EXPIRY_TIME = 60*60*3 ##3 hours
    TFIDF_EXPIRY_TIME = 60*2 ## 2min
    KEYWORDS_EXPIRY_TIME = 60*5 ##5 min
    EXPIRY_TIME = 60 * 20 # 20 min
    LATEST_EXPIRY_TIME = 60*20

cacheconfig = CacheConfig()

