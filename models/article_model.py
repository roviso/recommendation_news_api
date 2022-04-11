from xmlrpc.client import Boolean
from sqlalchemy import Column, ForeignKey, Integer, String,ForeignKey, DateTime
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
    likes = Column(Integer)
    shares = Column(Integer)

    label = Column(String)
    
    author_id = Column(String, ForeignKey('author.id'))
    type = Column(String)

    written_by = relationship("Author", back_populates="articles")
    liked_by = relationship("UserArticleLikes", back_populates="liked_article")


    viewed_by = relationship("UserArticleViewed", back_populates="viewed_article")
    ignored_by = relationship("UserArticleIgnored", back_populates="ignored_article")

    commented_by = relationship("UserArticleComments", back_populates="commented_article")
    # author = Column(String)
    # author_img = Column(String)
    __mapper_args__ = {'polymorphic_on': type,
        'polymorphic_identity':'article'
        }

class LatestArticle(Article):
    # __tablename__ = "latest"
    __mapper_args__ = {'polymorphic_identity': 'latest'}
    # id = Column(
    #     String, ForeignKey("article.id"), primary_key=True
    # )
    
class RecommendedArticle(Article):
    # __tablename__ = "recommended"
    __mapper_args__ = {'polymorphic_identity': 'recommended'}
    views = Column(Integer)
    ignores = Column(Integer)
    comments = Column(Integer)
    bookmarks = Column(Integer)

# class HomescreenArticle(Article):
#     likes = Column(Integer)
#     shares = Column(Integer)


# class LatestArticle(Base):
#     __tablename__ = 'latest'
#     id = Column(String, primary_key =True, index=True)
#     url = Column(String)
#     heading = Column(String)
#     content = Column(String)
    
    
#     date = Column(String)
#     head_image = Column(String)
    
#     additional_img = Column(String)
#     label = Column(String)

#     author = Column(String)

#     author_img = Column(String)

#     source = Column(String)
#     likes = Column(Integer)
#     shares = Column(Integer)