from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from schemas import user_schema
from models import user_model,article_model, author_model
from crud.crud_article import get_article, create_article
from crud.crud_author import get_author_by_name, create_author
import secrets
import datetime
from timefhuman import timefhuman

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db: Session, user_id: str):
    # if username in db:
    #     user_dict = db[username]
    #     return user_schema.UserInDB(**user_dict)
    return db.query(user_model.User).filter(user_model.User.id == user_id).first()

def user_exists(db: Session, device_id: str, device_name: str,):
    return db.query(user_model.User).filter(user_model.User.device_id == device_id, user_model.User.device_name == device_name,).first()


def create_user(db: Session, user: user_model.User):
    db.add(user)
    db.commit()
    db.refresh(user)
    print('Created new User: ',user)
    return user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def get_liked_article(db: Session, user_id: str, article_id: str):
    return db.query(user_model.UserArticleLikes).filter(user_model.UserArticleLikes.article_id == article_id,user_model.UserArticleLikes.user_id == user_id ).first()


def get_all_liked_articles(db: Session,user_id: str,  skip: int = 0, limit: int = 100):
    return db.query(user_model.UserArticleLikes).filter(user_model.UserArticleLikes.user_id == user_id).offset(skip).limit(limit).all()

def create_likes(db: Session, article_liked:user_schema.CreateUserArticleLikes,):
    user = get_user(db,article_liked.id)
    article = get_article(db, article_liked.article.url)
    author = get_author_by_name(db, article_liked.author.author_name)

    if not author:
        author_id = secrets.token_urlsafe(32)
        new_author = author_model.Author(id = author_id,**article_liked.author.dict())
        print('no author found in db... Adding the author in db.')
        # db_author = create_author(db, new_author)
        try:
            db_author = create_author(db, new_author)
            print(db_author)
            if db_author:
                author = db_author
                print("Successfully added article in db")
                
        except:
            print("Unable to add author in db")
            # return JSONResponse(status_code=status.HTTP_201_CREATED, content=item)

            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Author not added in database")


    if not article:
        article_id = secrets.token_urlsafe(32)
        new_article = article_model.Article(id = article_id,**article_liked.article.dict(),author_id=author.id )
        print('no article found in db... Adding the article in db.')
        # author_article = author_model.AuthorArticle(author_id = author.id, article_id = new_article.id)
        # create_article(db, new_article)
        try:
            db_article =  create_article(db, new_article)
            if db_article:
                article = db_article
                print("Successfully added article in db")

            # db_author_article = create_author_article_relation(db, new_article)
            # if db_author_article:
            #     print("Successfully added author article relation in db")
                
        except Exception as e:
            print("Unable to add article in db")
            # return JSONResponse(status_code=status.HTTP_201_CREATED, content=item)

            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Article not added in database, {e}")


    
    article_already_liked = get_liked_article(db,user.id,article.id)
    
    if article_already_liked:
        print("user already liked the article")
        # return article_already_liked
        return JSONResponse(status_code=status.HTTP_201_CREATED, content="article already liked")
    else:
        print("adding likes to the article")
        article_already_liked = user_model.UserArticleLikes(user_id = user.id,article_id = article.id)
        db.add(article_already_liked)
        db.commit()
        db.refresh(article_already_liked)
        # return article_already_liked
        return JSONResponse(status_code=status.HTTP_201_CREATED, content="article Successfully liked")


def get_viewed_article(db: Session, user_id: str, article_id: str):
    return db.query(user_model.UserArticleViewed).filter(user_model.UserArticleViewed.article_id == article_id,user_model.UserArticleViewed.user_id == user_id).first()


def get_all_viewed_articles(db: Session,user_id: str,  skip: int = 0):
    return db.query(user_model.UserArticleViewed).filter(user_model.UserArticleViewed.user_id == user_id).offset(skip).all()


def create_views(db: Session, article_viewed:user_schema.CreateUserArticleViewed):
    now = datetime.date.today()
    user = get_user(db,article_viewed.id)
    article = get_article(db, article_viewed.article.url)
    author = get_author_by_name(db, article_viewed.author.author_name)

    if not author:
        author_id = secrets.token_urlsafe(32)
        new_author = author_model.Author(id = author_id,**article_viewed.author.dict())
        print('no author found in db... Adding the author in db.')
        # db_author = create_author(db, new_author)
        try:
            db_author = create_author(db, new_author)
            # print(db_author)
            if db_author:
                author = db_author
                print("Successfully added article in db")
                
        except:
            print("Unable to add author in db")
            # return JSONResponse(status_code=status.HTTP_201_CREATED, content=item)

            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Author not added in database")
        
    if not article:
        article_id = secrets.token_urlsafe(32)
        # print(article_id)
        # print(article_viewed.article.__dict__)
        new_article = article_model.Article(id = article_id,**article_viewed.article.dict(), )
        # print(new_article,type(new_article),new_article.__dict__)
        print('no article found in db... Adding the article in db.')
        # create_article(db, new_article)
        try:
            if create_article(db, new_article):
                article = new_article
                print("Successfully added article in db")
                
        except:
            # print("Unable to add article in db")
            raise HTTPException(status_code=status.HTTP_400_Bad_Request, detail="Article not added in database")

    # start_time = timefhuman(article_viewed.viewed.start_time, now=now)
    # end_time = timefhuman(article_viewed.viewed.end_time, now=now)
    # total_time_spend = (end_time - start_time).seconds

    start_time = article_viewed.viewed.start_time
    end_time = article_viewed.viewed.end_time
    total_time_spend = article_viewed.viewed.total_time_spend

    # print(article_viewed)
    # return article_viewed
    
    article_already_viewed = get_viewed_article(db,user.id,article.id)
    if article_already_viewed:
        print("user already viewed the article")
        # return article_already_viewed
        return JSONResponse(status_code=status.HTTP_201_CREATED, content="article already viewed")
    else:
        print("adding views to the article")
        article_already_viewed = user_model.UserArticleViewed(user_id = user.id,article_id = article.id,start_time= start_time, end_time= end_time, total_time_spend= total_time_spend)
        db.add(article_already_viewed)
        db.commit()
        db.refresh(article_already_viewed)
        # return article_already_viewed
        return JSONResponse(status_code=status.HTTP_201_CREATED, content="article Successfully viewed")




def create_comments(db: Session, article_comment:user_schema.CreateUserArticleComments,):
    user = get_user(db,article_comment.id)
    article = get_article(db, article_comment.article.url)
    author = get_author_by_name(db, article_comment.author.author_name)
    comment = article_comment.comment.comment

    if not author:
        author_id = secrets.token_urlsafe(32)
        new_author = author_model.Author(id = author_id,**article_comment.author.dict())
        print('no author found in db... Adding the author in db.')
        # db_author = create_author(db, new_author)
        try:
            db_author = create_author(db, new_author)
            print(db_author)
            if db_author:
                author = db_author
                print("Successfully added article in db")
                
        except:
            print("Unable to add author in db")
            # return JSONResponse(status_code=status.HTTP_201_CREATED, content=item)

            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Author not added in database")


    if not article:
        article_id = secrets.token_urlsafe(32)
        new_article = article_model.Article(id = article_id,**article_comment.article.dict(),author_id=author.id )
        print('no article found in db... Adding the article in db.')
        # author_article = author_model.AuthorArticle(author_id = author.id, article_id = new_article.id)
        # create_article(db, new_article)
        try:
            db_article =  create_article(db, new_article)
            if db_article:
                article = db_article
                print("Successfully added article in db")

            # db_author_article = create_author_article_relation(db, new_article)
            # if db_author_article:
            #     print("Successfully added author article relation in db")
                
        except Exception as e:
            print("Unable to add article in db")
            # return JSONResponse(status_code=status.HTTP_201_CREATED, content=item)

            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Article not added in database, {e}")


    

    print("adding Comments to the article")
    article_commented = user_model.UserArticleComments(user_id = user.id,article_id = article.id, comment = comment)
    db.add(article_commented)
    db.commit()
    db.refresh(article_commented)

    return JSONResponse(status_code=status.HTTP_201_CREATED, content="Successfully added comment")
