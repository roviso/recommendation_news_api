from sqlalchemy import Column, ForeignKey, Integer, String,ForeignKey
from database import Base
from sqlalchemy.orm import relationship

class Author(Base):
    __tablename__ = 'author'

    id = Column(String, primary_key=True, index=True)
    author_name = Column(String)
    author_img = Column(String)

    articles = relationship("Article", back_populates="written_by")



# class AuthorArticle(Base):
#     __tablename__ = 'authorArticles'

#     author_id = Column(ForeignKey('author.id'), primary_key=True)
#     article_id = Column(ForeignKey('article.id'), primary_key=True)

#     author = relationship("Author", back_populates="authorArticles")
#     article = relationship("Article", back_populates="author_articles")



