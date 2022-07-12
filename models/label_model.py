from sqlalchemy import Column, ForeignKey, Integer, String,ForeignKey
from database import Base
from sqlalchemy.orm import relationship

class Label(Base):
    __tablename__ = 'label'

    id = Column(Integer, primary_key=True, index=True)
    label_name = Column(String)

    # source_id = Column(Integer, ForeignKey('source.id'))
    # from_source = relationship("Source", back_populates="authors")

    articles = relationship("Article", back_populates="label", lazy = True)
