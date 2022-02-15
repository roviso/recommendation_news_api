from sqlalchemy.orm import Session
from passlib.context import CryptContext
from schemas import user_schema
from models import user_model


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db: Session, email: str):
    # if username in db:
    #     user_dict = db[username]
    #     return user_schema.UserInDB(**user_dict)
    return db.query(user_model.User).filter(user_model.User.email == email).first()


def create_user(db: Session, user: user_schema.UserInDB,):
    hashed_password = get_password_hash(user.hashed_password)
    new_user = user_model.User(
        username = user.username,
        email = user.email,
        full_name = user.full_name,
        disabled = user.disabled,
        hashed_password = hashed_password
    )
    print('new_user: ',new_user,'11111111111111111111111111111111111')
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


