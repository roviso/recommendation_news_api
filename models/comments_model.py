
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String,ForeignKey, DateTime
from database import Base
from sqlalchemy.orm import relationship


class Comments(Base):
    __tablename__ = 'comments'

    id = Column(String, primary_key =True, index=True)

    user_id = Column(ForeignKey('user.id'))
    article_id = Column(ForeignKey('article.id'))
    date_of_comment = Column(DateTime)
    likes = Column(Integer)
    totalreplies = Column(Integer)

    comments = Column(String)


    commented_user = relationship("User", back_populates="commented_articles",lazy='selectin')
    commented_article = relationship("Article", back_populates="article_comments")

    
    comment_liked_by = relationship("UserCommentLikes", back_populates="comment_likes")
    comment_replies = relationship("Replies", back_populates="replied_comment",lazy='selectin')


class UserCommentLikes(Base):
    __tablename__ = 'commentlikes'

    user_id = Column(ForeignKey('user.id'), primary_key =True)
    comments_id = Column(ForeignKey('comments.id'), primary_key =True)

    liked_user = relationship("User", back_populates="liked_comments")
    comment_likes = relationship("Comments", back_populates="comment_liked_by")



class Replies(Base):
    __tablename__ = 'replies'
    
    id = Column(String, primary_key =True, index=True)

    comment_id = Column(ForeignKey('comments.id'))
    user_id = Column(ForeignKey('user.id'))
    date_of_replies = Column(DateTime)

    reply = Column(String)
    likes = Column(Integer)

    replied_user = relationship("User", back_populates="replied_comments")
    replied_comment = relationship("Comments", back_populates="comment_replies")

    replies_liked_by = relationship("UserRepliesLikes", back_populates="replies_likes")


class UserRepliesLikes(Base):
    __tablename__ = 'replieslikes'

    user_id = Column(ForeignKey('user.id'), primary_key =True)
    replies_id = Column(ForeignKey('replies.id'), primary_key =True)

    liked_user = relationship("User", back_populates="liked_replies")
    replies_likes = relationship("Replies", back_populates="replies_liked_by")
