from enum import unique
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String,ForeignKey, DateTime, Table
from database import Base
from sqlalchemy.orm import relationship
from typing import List, Optional
from sqlalchemy_utils import EmailType

class UserFollowing(Base):
    __tablename__ = 'user_following'

    follower_id =  Column(String, ForeignKey('user.id'), primary_key=True)
    following_id = Column(String, ForeignKey('user.id'), primary_key=True)


class User(Base):
    __tablename__ = 'user'
    # id = Column(Integer, primary_key =True, index=True)
    
    id = Column(String, primary_key =True, index=True)
    username = Column(String)
    device_name = Column(String)
    device_id = Column(String)
    ip_address = Column(String)
    registered = Column(Boolean)

    # following = relationship(
    #     'User', lambda: user_following,
    #     primaryjoin=lambda: User.id == user_following.c.user_id,
    #     secondaryjoin=lambda: User.id == user_following.c.following_id,
    #     backref='followers'
    # )

    user_followers = relationship(
        'User',
        secondary='user_following',
        primaryjoin=id==UserFollowing.follower_id,
        secondaryjoin=id==UserFollowing.following_id,
        backref='followers'
    )

    user_followings = relationship(
        'User',
        secondary='user_following',
        primaryjoin=id==UserFollowing.following_id,
        secondaryjoin=id==UserFollowing.follower_id,
        backref='followings'
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
    
    __mapper_args__ = {'polymorphic_on': registered,
        'polymorphic_identity':'user'
        }

    def __repr__(self) -> str:
        return f"<User(name={self.username})>"

    # def follow(self, user):
    #     if user not in self.following:
    #         self.following.append(user)
    #         user.following.append(self)

    # def unfollow(self, user):
    #     if user in self.following:
    #         self.following.remove(user)
    #         user.following.remove(self)


# user_following = Table(
#     'user_following', Base.metadata,
#     Column('user_id', String, ForeignKey(User.id), primary_key=True),
#     Column('following_id', String, ForeignKey(User.id), primary_key=True)
# )

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

    


