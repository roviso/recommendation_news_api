
from fastapi import  Depends,APIRouter, HTTPException, status
from schemas import user_schema, profile_schema
from crud.crud_user import UserCrud
from database import async_session
import database
from sqlalchemy.orm import Session



router = APIRouter(
    prefix = "/profile",
    tags=['profile']
)


@router.get("/get_user", response_model=profile_schema.UserProfile)
async def read_user(current_user: user_schema.User = Depends(), async_session: Session = Depends(database.get_session)):
    # return UserCrud.get_user(user_id=current_user.id)\
    async with async_session as session:
        async with session.begin():
            usercrud= UserCrud(session)
            return await usercrud.get_user_profile(current_user.id)
