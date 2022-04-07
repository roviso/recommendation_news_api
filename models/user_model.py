from enum import unique
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String,ForeignKey, DateTime
from database import Base
from sqlalchemy.orm import relationship
from typing import List, Optional
from sqlalchemy_utils import EmailType



class User(Base):
    __tablename__ = 'user'
    # id = Column(Integer, primary_key =True, index=True)
    
    id = Column(String, primary_key =True, index=True)
    device_name = Column(String)
    device_id = Column(String)
    ip_address = Column(String)
    registered = Column(Boolean)

    liked_articles = relationship("UserArticleLikes", back_populates="liked_user")
    viewed_articles = relationship("UserArticleViewed", back_populates="viewed_user")
    commened_articles = relationship("UserArticleComments", back_populates="commented_user")
    __mapper_args__ = {'polymorphic_on': registered,
        'polymorphic_identity':'user'
        }

class RegisteredUser(User):
    # __tablename__ = "registereduser"
    username = Column(String(50))
    password = Column(String)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(EmailType)
    __mapper_args__ = {'polymorphic_identity': True}
    # id = Column(
    #     String, ForeignKey("user.id", ondelete="CASCADE"), primary_key=True
    # )
    

class NonRegisteredUser(User):
    __mapper_args__ = {'polymorphic_identity': False}





class UserArticleLikes(Base):
    __tablename__ = 'likes'

    user_id = Column(ForeignKey('user.id'), primary_key=True)
    article_id = Column(ForeignKey('article.id'), primary_key=True)

    liked_user = relationship("User", back_populates="liked_articles")
    liked_article = relationship("Article", back_populates="liked_by")






class UserArticleViewed(Base):
    __tablename__ = 'viewed'

    user_id = Column(ForeignKey('user.id'), primary_key=True)
    article_id = Column(ForeignKey('article.id'), primary_key=True)

    start_time = Column(DateTime)
    end_time = Column(DateTime)
    total_time_spend = Column(Integer)

    viewed_user = relationship("User", back_populates="viewed_articles")
    viewed_article = relationship("Article", back_populates="viewed_by")


class UserArticleComments(Base):
    __tablename__ = 'comments'

    user_id = Column(ForeignKey('user.id'), primary_key=True)
    article_id = Column(ForeignKey('article.id'), primary_key=True)

    comment = Column(String)

    commented_user = relationship("User", back_populates="commened_articles")
    commented_article = relationship("Article", back_populates="commented_by")
