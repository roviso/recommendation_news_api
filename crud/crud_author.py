from sqlalchemy.orm import Session

from models import author_model


def get_author_by_id(db: Session, author_id: str):
    # if username in db:
    #     user_dict = db[username]
    #     return user_schema.UserInDB(**user_dict)
    return db.query(author_model.Author).filter(author_model.Author.id == author_id).first()

def get_author_by_name(db: Session, author_name: str):
    # if username in db:
    #     user_dict = db[username]
    #     return user_schema.UserInDB(**user_dict)
    return db.query(author_model.Author).filter(author_model.Author.author_name == author_name).first()


def create_author(db: Session, author: author_model.Author):
    db.add(author)
    db.commit()
    db.refresh(author)
    print('Created new Author: ',author)
    return author


