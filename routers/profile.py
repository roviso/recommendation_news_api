
from fastapi import  Depends,APIRouter, HTTPException, status
from schemas import user_schema, profile_schema
from crud.crud_user import UserCrud
from crud.crud_author import AuthorCrud
from database import async_session
import database
from sqlalchemy.orm import Session



router = APIRouter(
    prefix = "/profile",
    tags=['profile']
)

# ,response_model=profile_schema.UserProfile
@router.get("/get_user_profile")
async def user_profile(current_user: user_schema.User = Depends(), async_session: Session = Depends(database.get_session)):
    # return UserCrud.get_user(user_id=current_user.id)\
    async with async_session as session:
        async with session.begin():
            usercrud= UserCrud(session)
            user_prfile =  await usercrud.get_user_profile(current_user.id)
            print('user Profile is: ',user_prfile)
    
    return user_prfile


@router.get("/get_author_profile")
async def author_profile(author_id: str, async_session: Session = Depends(database.get_session)):
    # return UserCrud.get_user(user_id=current_user.id)\
    async with async_session as session:
        async with session.begin():
            authorcrud= AuthorCrud(session)
            author_profile =  await authorcrud.get_author_profile(author_id)
            print('user Profile is: ',author_profile)

            # user_bookmarked = author_profile.articles

            # print('user bookmark : ',user_bookmarked )
    
    return author_profile