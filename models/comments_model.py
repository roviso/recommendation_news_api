
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


    comment = Column(String)

    commented_user = relationship("User", back_populates="commented_articles")
    commented_article = relationship("Article", back_populates="article_comments")
    comment_liked_by = relationship("UserCommentLikes", back_populates="comment_likes")
    comment_replies = relationship("replies", back_populates="replied_comment")


class UserCommentLikes(Base):
    __tablename__ = 'commentlikes'

    user_id = Column(ForeignKey('user.id'), primary_key =True)
    comments_id = Column(ForeignKey('comments.id'), primary_key =True)

    liked_user = relationship("User", back_populates="liked_comments")
    comment_likes = relationship("comments", back_populates="comment_liked_by")



