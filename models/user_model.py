from enum import unique
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String,ForeignKey, DateTime, Table
from database import Base
from sqlalchemy.orm import relationship
from typing import List, Optional
from sqlalchemy_utils import EmailType
from sqlalchemy import case
from sqlalchemy import text

class UserKeywords(Base):
    __tablename__ = 'user_keywords'
    user_id = Column(ForeignKey('user.id'), primary_key=True)
    keywords_id = Column(ForeignKey('keywords.id'), primary_key=True)

    user = relationship("User", back_populates="keywords")
    keyword = relationship("Keywords", back_populates="users", lazy='selectin')


class UserFollowing(Base):
    __tablename__ = 'user_following'

    follower_id =  Column(String, ForeignKey('user.id'), primary_key=True)
    following_id = Column(String, ForeignKey('user.id'), primary_key=True)

    followers = relationship("User", foreign_keys=[follower_id])
    followings = relationship("User", foreign_keys=[following_id])


class AuthorFollowing(Base):
    __tablename__ = 'author_following'

    follower_id =  Column(String, ForeignKey('user.id'), primary_key=True)
    following_id = Column(String, ForeignKey('author.id'), primary_key=True)


class SourceFollowing(Base):
    __tablename__ = 'source_following'

    follower_id =  Column(String, ForeignKey('user.id'), primary_key=True)
    following_id = Column(Integer, ForeignKey('source.id'), primary_key=True)


class DeactivatedUser(Base):
    __tablename__ = "deactivateduser"
    id = Column(Integer, primary_key =True, index=True,autoincrement=True)
    user_id = Column(String)
    username = Column(String)
    device_name = Column(String)
    device_id = Column(String)
    ip_address = Column(String)
    registered = Column(Boolean)
    status = Column(String, nullable=False, default=text('deactivated'))
    profile_Image = Column(String(250))
    date_of_deactivation = Column(DateTime)
    activated = Column(Boolean)
    date_of_activation = Column(DateTime)


class DeletedUser(Base):
    __tablename__ = "deleteduser"
    id = Column(Integer, primary_key =True, index=True,autoincrement=True)
    user_id = Column(String)
    username = Column(String)
    password = Column(String)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(EmailType)

    device_name = Column(String)
    device_id = Column(String)
    ip_address = Column(String)
    registered = Column(Boolean)
    status = Column(String, nullable=False, default=text('deleted'))
    profile_Image = Column(String(250))
    date_of_deletion = Column(DateTime)




class User(Base):
    __tablename__ = 'user'
    
    id = Column(String, primary_key =True, index=True)
    username = Column(String)

    device_name = Column(String)
    device_id = Column(String)
    ip_address = Column(String)
    registered = Column(Boolean)
    status = Column(String, nullable=False, default=text('active'))
    
    profile_Image = Column(String(250))
    

    user_followers = relationship(
        'User',
        secondary='user_following',
        primaryjoin=id==UserFollowing.follower_id,
        secondaryjoin=id==UserFollowing.following_id
        # backref='followers'
    )

    user_followings = relationship(
        'User',
        secondary='user_following',
        primaryjoin=id==UserFollowing.following_id,
        secondaryjoin=id==UserFollowing.follower_id,
        # lazy='selectin',
        # backref='followings'
    )

    author_followings = relationship(
        'Author',
        secondary='author_following',
        primaryjoin=id==AuthorFollowing.following_id,
        secondaryjoin=id==AuthorFollowing.follower_id,
        # lazy='selectin',
        # backref='followings'
    )


    source_followings = relationship(
        'Source',
        secondary='source_following',
        primaryjoin=id==SourceFollowing.following_id,
        secondaryjoin=id==SourceFollowing.follower_id,
        # lazy='selectin',
        # backref='followings'
    )


    clicked_articles = relationship("Clicks", back_populates="clicked_user")

    liked_articles = relationship("UserArticleLikes", back_populates="liked_user")

    bookmarked_articles = relationship("UserArticleBookmarks", back_populates="bookmarked_user")


    viewed_articles = relationship("UserArticleViewed", back_populates="viewed_user")
    ignored_articles = relationship("UserArticleIgnored", back_populates="ignored_user")
    
    commented_articles = relationship("Comments", back_populates="commented_user")
    liked_comments = relationship("UserCommentLikes", back_populates="liked_user")

    replied_comments = relationship("Replies", back_populates="replied_user")
    liked_replies = relationship("UserRepliesLikes", back_populates="liked_user")

    keywords = relationship("UserKeywords", back_populates= "user", lazy='selectin')

    # __mapper_args__ = {'polymorphic_on': status,
    #     'polymorphic_identity':'user'}
    
    __mapper_args__ = {'polymorphic_on': registered,
        'polymorphic_identity':'user'
        }

    # __mapper_args__ = {'polymorphic_on': building_type}

    # def __repr__(self) -> str:
    #     return f"<User(name={self.username})>"


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
    
# class DeactivatedUser(User):
#     __mapper_args__ = {'polymorphic_identity': 'deactivated'}


# class DeletedUser(User):
#     __mapper_args__ = {'polymorphic_identity': 'deleted'}


# class ActiveUser(User):
#     __mapper_args__ = {'polymorphic_identity': 'active'}


class NonRegisteredUser(User):
    __mapper_args__ = {'polymorphic_identity': False}



class UserArticleLikes(Base):
    __tablename__ = 'likes'

    user_id = Column(ForeignKey('user.id'), primary_key=True)
    article_id = Column(ForeignKey('article.id'), primary_key=True)

    liked_user = relationship("User", back_populates="liked_articles")
    liked_article = relationship("Article", back_populates="liked_by")



class UserArticleBookmarks(Base):
    __tablename__ = 'bookmarks'

    user_id = Column(ForeignKey('user.id'), primary_key=True)
    article_id = Column(ForeignKey('article.id'), primary_key=True)

    bookmarked_user = relationship("User", back_populates="bookmarked_articles")
    bookmarked_article = relationship("Article", back_populates="bookmarked_by")




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
