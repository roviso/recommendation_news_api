from fastapi import FastAPI, Depends,APIRouter, HTTPException, status
from datetime import datetime, timedelta
from typing import Optional
from config import authconfig
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from config import authconfig
from crud import crud_user
from schemas import token_schema
import database
from sqlalchemy.orm import Session


router = APIRouter(
    prefix = "/token",
    tags=['token']
)



def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, authconfig.SECRET_KEY, algorithm=authconfig.ALGORITHM)
    return encoded_jwt




@router.post("/token", response_model=token_schema.Token)
async def login_for_access_token(db: Session = Depends(database.get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = crud_user.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=authconfig.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"username": user.username,"email": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}