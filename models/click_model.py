from enum import unique
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String,ForeignKey, DateTime
from database import Base
from sqlalchemy.orm import relationship
from typing import List, Optional
from sqlalchemy_utils import EmailType

class Clicks(Base):
    __tablename__ = 'clicks'

    user_id = Column(ForeignKey('user.id'), primary_key=True)
    article_id = Column(ForeignKey('article.id'), primary_key=True)
    date_of_click = Column(DateTime)
    source = Column(String)

    clicked_user = relationship("User", back_populates="clicked_articles")
    clicked_article = relationship("Article", back_populates="clicked_by")