from sqlalchemy import Column, ForeignKey, Integer, String,ForeignKey, DateTime
from database import Base
from sqlalchemy.orm import relationship


class Keywords(Base):
    __tablename__ = 'keywords'

    id = Column(Integer, primary_key = True)
    word = Column(String, nullable = False)

    articles = relationship("AricleKeywords", back_populates = "keyword")