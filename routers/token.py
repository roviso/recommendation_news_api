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
from crud.crud_user import UserCrud

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


async def authenticate_user(async_session: Session, user_id: str):
    async with async_session as session:
        async with session.begin():
            usercrud= UserCrud(session)
            user = await usercrud.get_user(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such User Found")
    else:
        user = user._mapping.User

    # if not verify_password(password, user.hashed_password):
    #     return False
    return user

@router.post("/token", response_model=token_schema.Token)
async def login_for_access_token(async_session: Session = Depends(database.get_session), form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(async_session, form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=authconfig.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"user_id": user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}