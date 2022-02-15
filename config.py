import os
from dotenv import load_dotenv

from pathlib import Path
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

class Settings:
    PROJECT_NAME:str = "news_recommendation"
    PROJECT_VERSION: str = "1.0.0"

    POSTGRES_USER : str = os.getenv("POSTGRES_USER","ravi")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD","techprixa1234")
    POSTGRES_SERVER : str = os.getenv("POSTGRES_SERVER","127.0.0.1")
    POSTGRES_PORT : str = os.getenv("POSTGRES_PORT",5432) # default postgres port is 5432
    POSTGRES_DB : str = os.getenv("POSTGRES_DB","news_recommendation")
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

settings = Settings()


class AuthConfig:
    SECRET_KEY:str  ='9cd0545638607dc61ec68d09f116aa27138b1290273035dd78c7d00480d8c4c8'
    ALGORITHM:str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES:int = 30


authconfig = AuthConfig()


