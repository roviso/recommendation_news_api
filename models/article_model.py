from xmlrpc.client import Boolean
from sqlalchemy import Column, ForeignKey, Integer, String,ForeignKey, DateTime
from database import Base
from sqlalchemy.orm import relationship

from sqlalchemy.dialects.postgresql import ARRAY

from sqlalchemy.ext.associationproxy import association_proxy


class Keywords(Base):
    """Base Class for Keyword Model"""
    __tablename__ = 'keywords'

    id = Column(Integer, primary_key = True, autoincrement=True)
    tag = Column(String, nullable = False)

    articles = relationship("AricleKeywords", back_populates = "keyword")
    users = relationship("UserKeywords", back_populates = "keyword")
    
class AricleKeywords(Base):
    """Base Class for Aricle Keyword relationship"""
    __tablename__ = 'article_keywords'
    article_id = Column(String, ForeignKey('article.id'), primary_key=True)
    keywords_id = Column(Integer, ForeignKey('keywords.id'), primary_key=True)
    # blurb = Column(String, nullable=False)
    article = relationship("Article", back_populates="keywords")
    keyword = relationship("Keywords", back_populates="articles", lazy='selectin')

    keyword_word = association_proxy(target_collection='keyword', attr='tag')


class Article(Base):
    """Base Class for Article Model"""
    __tablename__ = 'article'

    id = Column(String, primary_key =True, index=True)
    url = Column(String, index=True)
    head_image = Column(String)
    heading = Column(String)
    date = Column(String)

    content = Column(ARRAY(String))
    additional_img = Column(ARRAY(String))
    source = Column(String)
    likes = Column(Integer)
    shares = Column(Integer)

    # label_id = Column(String, ForeignKey('author.id'))
    # label = relationship("Label", back_populates="articles", lazy='selectin')
    label = Column(String)
    
    author_id = Column(String, ForeignKey('author.id'))
    author = relationship("Author", back_populates="articles", lazy='selectin')

    type = Column(String)

    keywords = relationship("AricleKeywords", back_populates= "article", lazy='selectin')

    views = Column(Integer)
    ignores = Column(Integer)
    total_comments = Column(Integer)
    bookmarks = Column(Integer)

    
    liked_by = relationship("UserArticleLikes", back_populates="liked_article")

    bookmarked_by = relationship("UserArticleBookmarks", back_populates="bookmarked_article")

    clicked_by = relationship("Clicks", back_populates="clicked_article")


    viewed_by = relationship("UserArticleViewed", back_populates="viewed_article")
    ignored_by = relationship("UserArticleIgnored", back_populates="ignored_article")

    article_comments = relationship("Comments", back_populates="commented_article")

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
    
