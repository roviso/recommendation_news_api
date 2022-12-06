from fastapi import FastAPI, Depends,APIRouter, HTTPException, status
from datetime import datetime, timedelta
from typing import Optional
from config import authconfig
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from config import authconfig
from crud import crud_user
from passlib.context import CryptContext
from models import user_model

from schemas import token_schema, user_schema
from database import async_session
import secrets
import database
from sqlalchemy.orm import Session
from helper.username_generator import username_generator
from apis.newstalk.routers.user import get_current_user

router = APIRouter(
    prefix = "/auth",
    tags=['auth']
)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=555)
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

    return user


async def authenticate_registered_user(async_session: Session, user_email: str, user_password: str):
    async with async_session as session:
        async with session.begin():
            usercrud= crud_user.UserCrud(session)
            
            user = await usercrud.check_user_exists_by_email(user_email)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such User Found")
    else:
        user = await usercrud.get_user_by_email(user_email)
        if not verify_password(user_password, user.password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password Incorrect.")

        return user


def generate_access_token(user_id: str):
    access_token_expires = timedelta(minutes=authconfig.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"user_id": user_id}, expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(minutes=authconfig.REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_access_token(
        data={"user_id": user_id}, expires_delta=refresh_token_expires
    )
    return {"access_token": access_token,"refresh_token": refresh_token ,"token_type": "bearer"}



def create_new_user_model(device_id: str, device_name: str,ip_address: str):
    user_id = secrets.token_urlsafe(32)
    username = username_generator.generate_username(1)[0]
    user = user_model.NonRegisteredUser(
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
            else:
                user = await usercrud.get_existing_user(device_id=create_user.device_id, device_name=create_user.device_name)
                if not user.registered:
                    access_token = generate_access_token(user.id)
                else:
                    new_user = create_new_user_model(create_user.device_id,create_user.device_name,create_user.ip_address)
                    await usercrud.create_user(new_user)
                    access_token =generate_access_token(new_user.id)
    
            return access_token


@router.post("/refresh_token", response_model = token_schema.Token)
async def refresh_token(token: token_schema.RefreshToken,async_session: Session = Depends(database.get_session)):
    payload = jwt.decode(token.refresh_token, authconfig.SECRET_KEY, algorithms=[authconfig.ALGORITHM])

    user_id: str = payload.get("user_id")
    async with async_session as session:
        async with session.begin():
            usercrud= crud_user.UserCrud(session)
            user = await usercrud.check_userid_exists(user_id)

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                access_token =generate_access_token(user_id)
                return access_token





@router.post("/login", response_model = token_schema.Token)
async def login(login_form: token_schema.LoginUser, async_session: Session = Depends(database.get_session)):

    user = await authenticate_registered_user(async_session, login_form.email, login_form.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token =generate_access_token(user.id)
    return access_token


@router.post("/logout", response_model = token_schema.Token)
async def logout(logout_user: token_schema.CreateUser, async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    access_token = await create_user(logout_user,async_session)
    return access_token



@router.post('/SignUp', response_model = token_schema.Token)
async def sign_up(user_info: user_schema.RegisterUser,current_user: user_model.User = Depends(get_current_user)):
    async with async_session() as session:
        async with session.begin():
            usercrud= crud_user.UserCrud(session)
            hashed_password = get_password_hash(user_info.password)
            await usercrud.register_user(user_id= current_user.id, username=user_info.username, password = hashed_password,
                first_name = user_info.first_name,last_name =user_info.last_name,email = user_info.email)

            access_token =generate_access_token(current_user.id)

    return access_token
