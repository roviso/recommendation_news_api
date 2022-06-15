from fastapi import  Depends,APIRouter, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from schemas import token_schema, user_schema
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from config import authconfig
from crud.crud_user import UserCrud
import database
from models import user_model
import secrets
from database import async_session
from helper.username_generator import username_generator
from fastapi_pagination import Page, Params, paginate, LimitOffsetPage

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
            usercrud= UserCrud(session)

            user = await usercrud.get_user(user_id=token_data.user_id)
    # print(user,"user")
    if user is None:
        raise credentials_exception
    return user

# async def get_current_active_user(current_user: User = Depends(get_current_user)):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user

@router.get("/me")
async def read_users_me(current_user: user_model.User = Depends(get_current_user)):
    return current_user
    
@router.post('/create_user')
async def create_user(device_id: str, device_name: str,ip_address: str, async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            usercrud= UserCrud(session)
            user_exists = await usercrud.check_user_exists(device_id=device_id, device_name=device_name)
    if user_exists:
        return {'user_id':user_exists.User.id,
                'username': user_exists.User.username}
    else:
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
        async with async_session as session:
            async with session.begin():
                usercrud= UserCrud(session)
                await usercrud.create_user(user)
        return {'user_id': user_id,
                'username': username}



@router.get("/get_user")
async def read_user(current_user: user_schema.User = Depends(), async_session: Session = Depends(database.get_session)):
    # return UserCrud.get_user(user_id=current_user.id)\
    async with async_session as session:
        async with session.begin():
            usercrud= UserCrud(session)
            return await usercrud.get_user(current_user.id)

@router.get("/get_all_user", response_model = LimitOffsetPage[user_schema.SearchUsers])
async def read_all_user(async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            usercrud= UserCrud(session)
            users_list =  await usercrud.get_all_user()
            return paginate(users_list)


@router.get("/get_all_registered_user", response_model = LimitOffsetPage[user_schema.GetRegisteredUsers])
async def read_all_registered_user(async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            usercrud= UserCrud(session)
            users_list =  await usercrud.get_all_registered_user()
            return paginate(users_list)


        
@router.post('/register_user', response_model=user_schema.RegisterUser)
async def register_user(user_info: user_schema.RegisterUser, async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            usercrud= UserCrud(session)
            await usercrud.register_user(user_id= user_info.id, username=user_info.username, password = user_info.password,
                first_name = user_info.first_name,last_name =user_info.last_name,email = user_info.email)
    
    return user_info


@router.get("/get_registered_user")
async def get_registered_user(current_user: user_schema.User = Depends(), async_session: Session = Depends(database.get_session)):
    # return UserCrud.get_user(user_id=current_user.id)\
    async with async_session as session:
        async with session.begin():
            usercrud= UserCrud(session)
            return await usercrud.get_registered_user(current_user.id)
          

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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


# async def get_current_active_user(current_user: user_model.User = Depends()):
#     current_user_schema = user_schema.User(user_id = current_user.user_id) 
 
#     # if current_user.disabled:
#     #     raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user_schema

# @router.post("/create_user_id/", response_model=user_schema.User)
# def create_user_id(device_id: str, device_name: str,ip_address: str, db: Session = Depends(database.get_db)):
#     # db_user = crud_user.get_user(db, id = user.id)
#     # if db_user:
#     #     raise HTTPException(status_code=400, detail="Email already registered")
    
#     user_exists = crud_user.user_exists(db=db, device_id=device_id, device_name=device_name)
#     if user_exists:
#         return user_exists
#     else:
#         user = user_model.User(
#             id = secrets.token_urlsafe(32),
#             device_id = device_id,
#             device_name = device_name,
#             ip_address = ip_address
#         )
#         # print(user,user.__dict__)
#         return crud_user.create_user(db=db, user=user)
         

# @router.get("/get_user", response_model=user_schema.UserInDB)
# async def read_user(current_user: user_schema.User = Depends(), db: Session = Depends(database.get_db)):
#     return crud_user.get_user(db=db, user_id=current_user.id)

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


# @router.get("/get_user_liked_articles")
# async def read_liked_articles(current_user: user_schema.User = Depends(), db: Session = Depends(database.get_db)):

#     return crud_user.get_all_liked_articles(db=db, user_id=current_user.id)

# @router.get("/get_user_viewed_articles")
# async def read_viewed_articles(current_user: user_schema.User = Depends(), db: Session = Depends(database.get_db)):

#     return crud_user.get_all_viewed_articles(db=db, user_id=current_user.id)



# @router.post('/likes/',status_code = status.HTTP_201_CREATED)
# async def article_liked(article_liked: user_schema.CreateUserArticleLikes,db: Session = Depends(database.get_db)):
#     return crud_user.create_likes(db, article_liked)
#         # return JSONResponse(status_code=status.HTTP_201_CREATED, content=item)




# @router.post('/views/',status_code = status.HTTP_201_CREATED)
# async def article_viewed(article_viewed: user_schema.CreateUserArticleViewed,db: Session = Depends(database.get_db)):
    
#     return crud_user.create_views(db, article_viewed)



# @router.post('/comments/',status_code = status.HTTP_201_CREATED)
# async def article_commented(article_comment: user_schema.CreateUserArticleComments,db: Session = Depends(database.get_db)):
    
#     return crud_user.create_comments(db, article_comment)




# @router.get("/users/me/items/")
# async def read_own_items(current_user: user_schema.User = Depends(get_current_active_user)):
#     return [{"item_id": "Foo", "owner": current_user.username}]
