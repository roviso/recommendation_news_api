
from fileinput import filename
from fastapi import  Depends,APIRouter, HTTPException, status, UploadFile, File, BackgroundTasks
from schemas import user_schema, profile_schema
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
async def user_profile(current_user: user_schema.User = Depends(), async_session: Session = Depends(database.get_session)):
    # return UserCrud.get_user(user_id=current_user.id)\
    async with async_session as session:
        async with session.begin():
            usercrud= UserCrud(session)
            followcrud = Follow(session)
            user_profile =  await usercrud.get_user_profile(current_user.id)
            follower_count = await followcrud.get_followers_count(current_user.id)
            following_count = await followcrud.get_following_count(current_user.id)

    print(f"user profile: {user_profile}")
    setattr(user_profile,'followers',int(follower_count))
    setattr(user_profile,'following',int(following_count))
    return user_profile


@router.post("/upload/profilePic")
async def upload_profile_Image(background_tasks: BackgroundTasks, current_user: user_schema.User = Depends(), async_session: Session = Depends(database.get_session), file: UploadFile = File(...)):
    async with async_session as session:
        async with session.begin():
            usercrud= UserCrud(session)
            user_profile =  await usercrud.get_user_profile(current_user.id)
    # SAVE FILE ORIGINAL
            file_name = user_profile.username+ f"{user_profile.email.split('@')[0]}" + ".png"
            with open(imgconfig.IMG_SAVED_PATH + file_name , "wb") as myfile:
                content = await file.read()
                myfile.write(content)
                myfile.close()

            await usercrud.upload_profile_Image(current_user.id, file_name)

    # RESIZE IMAGES
    background_tasks.add_task(resize_image, filename=file_name)
    return JSONResponse(content={"message": "success"})

@router.get("/get_source_profile", status_code = 200  , response_model=profile_schema.SourceProfile)
async def spurce_profile(source_id: int, async_session: Session = Depends(database.get_session)):
    # return UserCrud.get_user(user_id=current_user.id)\
    async with async_session as session:
        async with session.begin():
            sourcecrud= SourceCrud(session)
            followcrud = Follow(session)
            
            source_profile =  await sourcecrud.get_source_profile(source_id)
    #         print()
            follower_count = await followcrud.get_source_followers(source_id)
    #         following_count = await followcrud.get_source_followings(source_id)
            total_articles = source_profile.articles
            total_likes = sum(articles.__dict__['likes'] for articles in total_articles)
            total_views = sum(articles.__dict__['views'] for articles in total_articles)

            
    setattr(source_profile,'followers',int(len(follower_count)))
    setattr(source_profile,'total_articles',len(total_articles))
    setattr(source_profile,'total_likes',total_likes)
    setattr(source_profile,'total_views',total_views)
            # user_bookmarked = author_profile.articles

            # print('user bookmark : ',user_bookmarked )
    
    return source_profile


@router.get("/get_author_profile", status_code = 200 , response_model=profile_schema.AuthorProfile)
async def author_profile(author_id: str, async_session: Session = Depends(database.get_session)):
    # return UserCrud.get_user(user_id=current_user.id)\
    async with async_session as session:
        async with session.begin():
            authorcrud= AuthorCrud(session)
            followcrud = Follow(session)
            
            author_profile =  await authorcrud.get_author_profile(author_id)
            follower_count = await followcrud.get_author_followers(author_id)
            following_count = await followcrud.get_author_followings(author_id)
            total_articles = author_profile.articles
            total_likes = sum(articles.__dict__['likes'] for articles in total_articles)
            total_views = sum(articles.__dict__['views'] for articles in total_articles)

            
    setattr(author_profile,'followers',int(len(follower_count)))
    setattr(author_profile,'following',int(len(following_count)))
    setattr(author_profile,'total_articles',len(total_articles))
    setattr(author_profile,'total_likes',total_likes)
    setattr(author_profile,'total_views',total_views)
            # user_bookmarked = author_profile.articles

            # print('user bookmark : ',user_bookmarked )
    
    return author_profile

