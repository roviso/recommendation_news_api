from fastapi import FastAPI, Depends,APIRouter, HTTPException, status
from datetime import datetime, timedelta
from typing import Optional
from config import authconfig
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from config import authconfig
from crud import crud_user

from models import user_model

from schemas import token_schema

import secrets
import database
from sqlalchemy.orm import Session
from helper.username_generator import username_generator

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
            usercrud= crud_user.UserCrud(session)
            user = await usercrud.get_user(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such User Found")
    else:
        user = user

    # if not verify_password(password, user.hashed_password):
    #     return False
    return user


def generate_access_token(user_id: str):
    access_token_expires = timedelta(minutes=authconfig.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"user_id": user_id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

def create_new_user_model(device_id: str, device_name: str,ip_address: str):
    user_id = secrets.token_urlsafe(32)
    username = username_generator.generate_username(1)[0]
    user = user_model.User(
            id = user_id,
            username = username,
            device_id = device_id,
            device_name = device_name,
            ip_address = ip_address,
            registered = False
        )
    return user

@router.post("/create_user", response_model=token_schema.Token)
async def create_user(create_user: token_schema.CreateUser, async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            usercrud= crud_user.UserCrud(session)
            user_exists = await usercrud.check_user_exists(device_id=create_user.device_id, device_name=create_user.device_name)
    if not user_exists:
        user = create_new_user_model(create_user.device_id,create_user.device_name,create_user.ip_address)
        await usercrud.create_user(user)
        access_token = generate_access_token(user.id)
        # return {'user_id':user_exists.User.id,
        #         'username': user_exists.User.username}
    else:
        user = await usercrud.get_existing_user(device_id=create_user.device_id, device_name=create_user.device_name)
        if not user.registered:
            access_token = generate_access_token(user.id)
        else:
            new_user = create_new_user_model(create_user.device_id,create_user.device_name,create_user.ip_address)
            await usercrud.create_user(new_user)
            access_token =generate_access_token(new_user.id)
    
    return access_token




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
