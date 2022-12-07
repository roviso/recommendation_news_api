
from fileinput import filename
from fastapi import  Depends,APIRouter, HTTPException, status, UploadFile, File, BackgroundTasks
from schemas import user_schema, profile_schema
from models import user_model
from crud.crud_user import UserCrud
from crud.crud_source import SourceCrud
from crud.crud_author import AuthorCrud
from crud.crud_follow import Follow
from crud.crud_likes import Likes
from database import async_session
import database
from sqlalchemy.orm import Session
from PIL import Image
from config import imgconfig
from fastapi.responses import JSONResponse
from schemas import profile_schema
from apis.newstalk.routers.user import get_current_user
import os
import boto3
import uuid


session = boto3.Session(
    aws_access_key_id='AKIAT2O2SZBBDI4Q3EFJ',
    aws_secret_access_key='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',
)

s3 = session.resource('s3')
BUCKET = "riri.prixacdn.net"

bucket_session = s3.Bucket(BUCKET)


router = APIRouter(
    prefix = "/profile",
    tags=['profile']
)


def resize_image(filename: str):
    sizes = [{
        "width": 640,
        "height": 480
    }]

    for size in sizes:
        size_defined = size['width'], size['height']

        image = Image.open(imgconfig.IMG_SAVED_PATH + filename, mode="r")
        image.thumbnail(size_defined)
        image.save(imgconfig.IMG_SAVED_PATH + filename)
    print("success")



@router.get("/get_user_profile", status_code = 200, response_model=profile_schema.UserProfile)
# ,response_model=profile_schema.UserProfile)
async def user_profile(current_user: user_model.User = Depends(get_current_user), async_session: Session = Depends(database.get_session)):
    # return UserCrud.get_user(user_id=current_user.id)\
    async with async_session as session:
        async with session.begin():
            usercrud= UserCrud(session)
            user_profile =  await usercrud.get_user_profile(current_user.id)
            return user_profile
            
    #         followcrud = Follow(session)
    #         user_profile =  await usercrud.get_user_profile(current_user.id)
    #         follower_count = await followcrud.get_followers_count(current_user.id)
    #         following_count = await followcrud.get_following_count(current_user.id)

    # print(f"user profile: {user_profile}")
    # setattr(user_profile,'followers',int(follower_count))
    # setattr(user_profile,'following',int(following_count))
    # return user_profile


@router.post("/upload/profilePic")
async def upload_profile_Image(current_user: user_model.User = Depends(get_current_user), file: UploadFile = File(...)):
    async with async_session() as session:
        async with session.begin():
            try:
                usercrud= UserCrud(session)
                user_profile =  await usercrud.get_user_profile(current_user.id)
                extension = file.filename.split('.')[-1]
                file_name = str(uuid.uuid1())+ "." +extension
                
                op_path = "profile/"+file_name
                content = await file.read()
                s3.Object(BUCKET,op_path).put(Body=content)


                cdn_path = "https://riri.prixacdn.net/"+op_path
                await usercrud.upload_profile_Image(user_id = current_user.id,profile_Image = cdn_path)
                # os.remove(file_path)
                
            except Exception:
                return {"message": "There was an error Reading/Uploading the wav file"}
            finally:
                file.file.close()

            return cdn_path


@router.patch('/update_profile', response_model=profile_schema.UserProfile)
async def update_profile(user_info: user_schema.EditProfile , async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    async with async_session as session:
        async with session.begin():
            usercrud= UserCrud(session)
            await usercrud.update_user(user_id= current_user.id, username=user_info.username,
                first_name = user_info.first_name,last_name =user_info.last_name)

            user_profile =  await usercrud.get_user_profile(current_user.id)
            return user_profile

    



@router.get("/get_source_profile", status_code = 200  , response_model=profile_schema.SourceProfile)
async def spurce_profile(source_id: int, async_session: Session = Depends(database.get_session), current_user: user_model.User = Depends(get_current_user)):
    # return UserCrud.get_user(user_id=current_user.id)\
    async with async_session as session:
        async with session.begin():
            sourcecrud= SourceCrud(session)
            source_profile =  await sourcecrud.get_source_profile(source_id)
    
    return source_profile


@router.get("/get_author_profile", status_code = 200 , response_model=profile_schema.AuthorProfile)
async def author_profile(author_id: str, async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    # return UserCrud.get_user(user_id=current_user.id)\
    async with async_session as session:
        async with session.begin():
            authorcrud= AuthorCrud(session)
            author_profile =  await authorcrud.get_author_profile(author_id)

    return author_profile

