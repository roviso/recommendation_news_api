from sqlalchemy.orm import Session
from schemas import article_schema
from models import article_model



def get_article(db: Session, article_url: str):
    # if username in db:
    #     user_dict = db[username]
    #     return user_schema.UserInDB(**user_dict)
    return db.query(article_model.Article).filter(article_model.Article.url == article_url).first()


def create_article(db: Session, article: article_model.Article):
    db.add(article)
    db.commit()
    db.refresh(article)
    print('Created new User: ',article)
    return article
