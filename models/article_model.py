from sqlalchemy import Column, ForeignKey, Integer, String,ForeignKey
from database import Base
from sqlalchemy.orm import relationship

class Article(Base):
    __tablename__ = 'article'

    id = Column(String, primary_key =True, index=True)
    url = Column(String, index=True)
    head_image = Column(String)
    heading = Column(String)
    date = Column(String)

    content = Column(String)
    additional_img = Column(String)
    source = Column(String)
    author_id = Column(String, ForeignKey('author.id'))

    written_by = relationship("Author", back_populates="articles")
    liked_by = relationship("UserArticleLikes", back_populates="liked_article")


    viewed_by = relationship("UserArticleViewed", back_populates="viewed_article")
    commented_by = relationship("UserArticleComments", back_populates="commented_article")
    # author = Column(String)
    # author_img = Column(String)


class LatestArticle(Base):
    __tablename__ = 'latest'
    id = Column(String, primary_key =True, index=True)
    url = Column(String)
    heading = Column(String)
    content = Column(String)
    
    
    date = Column(String)
    head_image = Column(String)
    
    additional_img = Column(String)
    label = Column(String)

    author = Column(String)

    author_img = Column(String)

    source = Column(String)
    likes = Column(Integer)
    shares = Column(Integer)