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
    username = Column(String)
    device_name = Column(String)
    device_id = Column(String)
    ip_address = Column(String)
    registered = Column(Boolean)

    liked_articles = relationship("UserArticleLikes", back_populates="liked_user")

    viewed_articles = relationship("UserArticleViewed", back_populates="viewed_user")
    ignored_articles = relationship("UserArticleIgnored", back_populates="ignored_user")
    
    commented_articles = relationship("Comments", back_populates="commented_user")
    liked_comments = relationship("UserCommentLikes", back_populates="liked_user")

    replied_comments = relationship("Replies", back_populates="replied_user")
    liked_replies = relationship("Replies", back_populates="replied_user")
    
    __mapper_args__ = {'polymorphic_on': registered,
        'polymorphic_identity':'user'
        }

class RegisteredUser(User):
    # __tablename__ = "registereduser"
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




class UserArticleIgnored(Base):
    __tablename__ = 'ignored'

    user_id = Column(ForeignKey('user.id'), primary_key=True)
    article_id = Column(ForeignKey('article.id'), primary_key=True)

    total_time_spend = Column(Integer)

    ignored_user = relationship("User", back_populates="ignored_articles")
    ignored_article = relationship("Article", back_populates="ignored_by")

    


