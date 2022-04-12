from sqlalchemy import Boolean, Column, ForeignKey, Integer, String,ForeignKey, DateTime
from database import Base
from sqlalchemy.orm import relationship



class Replies(Base):
    __tablename__ = 'replies'

    id = Column(String, primary_key =True, index=True)

    comment_id = Column(ForeignKey('comments.id'))
    user_id = Column(ForeignKey('user.id'))

    reply = Column(String)

    replied_user = relationship("User", back_populates="commented_articles")
    replied_comment = relationship("Comments", back_populates="comment_replies")
    replies_liked_by = relationship("replieslikes", back_populates="replies_likes")


class UserRepliesLikes(Base):
    __tablename__ = 'replieslikes'

    user_id = Column(ForeignKey('user.id'), primary_key =True)
    replies_id = Column(ForeignKey('replies.id'), primary_key =True)

    liked_user = relationship("User", back_populates="liked_replies")
    replies_likes = relationship("replies", back_populates="replies_liked_by")
