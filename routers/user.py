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
import secrets

router = APIRouter(
    prefix = "/user",
    tags=['user']
)




oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, authconfig.SECRET_KEY, algorithms=[authconfig.ALGORITHM])

#         user_id: str = payload.get("user_id")user_schema

#     user = crud_user.get_user(db, user_id=token_data.user_id)
#     print(user,"user")
#     if user is None:
#         raise credentials_exception
#     return user


async def get_current_active_user(current_user: user_model.User = Depends()):
    current_user_schema = user_schema.User(user_id = current_user.user_id) 
 
    # if current_user.disabled:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user_schema

@router.post("/create_user_id/", response_model=user_schema.User)
def create_user_id(device_id: str, device_name: str,ip_address: str, db: Session = Depends(database.get_db)):
    # db_user = crud_user.get_user(db, id = user.id)
    # if db_user:
    #     raise HTTPException(status_code=400, detail="Email already registered")
    
    user_exists = crud_user.user_exists(db=db, device_id=device_id, device_name=device_name)
    if user_exists:
        return user_exists
    else:
        user = user_model.User(
            id = secrets.token_urlsafe(32),
            device_id = device_id,
            device_name = device_name,
            ip_address = ip_address
        )
        # print(user,user.__dict__)
        return crud_user.create_user(db=db, user=user)
         

@router.get("/get_user", response_model=user_schema.UserInDB)
async def read_user(current_user: user_schema.User = Depends(), db: Session = Depends(database.get_db)):
    return crud_user.get_user(db=db, user_id=current_user.id)

# @router.post("/user_exists",)
# async def user_exists(device_id: str, device_name: str, db: Session = Depends(database.get_db)):
#     user_exists = crud_user.user_exists(db=db, device_id=device_id, device_name=device_name)
#     print(user_exists, type(user_exists))
#     if not user_exists:
#         print("NO USER FOUND")
#         return "NO USER FOUND"
#     else:
#         print(f"USER FOUND: {user_exists.id}")
#         return user_exists.id


@router.get("/get_user_liked_articles")
async def read_liked_articles(current_user: user_schema.User = Depends(), db: Session = Depends(database.get_db)):

    return crud_user.get_all_liked_articles(db=db, user_id=current_user.id)

@router.get("/get_user_viewed_articles")
async def read_viewed_articles(current_user: user_schema.User = Depends(), db: Session = Depends(database.get_db)):

    return crud_user.get_all_viewed_articles(db=db, user_id=current_user.id)


# @router.get("/users/me/items/")
# async def read_own_items(current_user: user_schema.User = Depends(get_current_active_user)):
#     return [{"item_id": "Foo", "owner": current_user.username}]
