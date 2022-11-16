from fastapi import FastAPI, Depends,APIRouter, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from schemas import token_schema, user_schema
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from config import authconfig
from crud import crud_user
import database
from models import user_model

router = APIRouter(
    prefix = "/user",
    tags=['user']
)




oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme), async_session: Session = Depends(database.get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, authconfig.SECRET_KEY, algorithms=[authconfig.ALGORITHM])

        user_id: str = payload.get("user_id")
        # if email is None:
        #     raise credentials_exception
        token_data = token_schema.TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception

    async with async_session as session:
        async with session.begin():
            usercrud= crud_user.UserCrud(session)

            user = await usercrud.get_user(user_id=token_data.user_id)
    # print(user,"user")
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: user_model.User = Depends(get_current_user)):
    # current_user_schema = user_schema.User(username = current_user.username,
    # email = current_user.email,
    # full_name = current_user.full_name,
    # ) 
 
    # if current_user.disabled:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@router.post("/sign_up/", response_model=user_schema.User)
def signup(user: user_schema.UserInDB, db: Session = Depends(database.get_db)):
    db_user = crud_user.get_user(db, email = user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud_user.create_user(db=db, user=user)

@router.get("/users/me/", response_model=user_schema.GetRegisteredUsers)
async def read_users_me(current_user: user_schema.User = Depends(get_current_active_user)):
    return current_user


@router.get("/users/me/items/")
async def read_own_items(current_user: user_schema.User = Depends(get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.username}]
