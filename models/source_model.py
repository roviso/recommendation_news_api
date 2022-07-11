from xmlrpc.client import DateTime
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String,ForeignKey, DateTime
from database import Base
from sqlalchemy.orm import relationship

class Source(Base):
    __tablename__ = 'source'
    id = Column(Integer, primary_key =True, index=True,autoincrement=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)

    name = Column(String)

    image = Column(String)

    domain = Column(String)
    link = Column(String)

    link_prefix = Column(String)

    link_type = Column(String)

    content_selector = Column(String)

    exception_selector = Column(String) 

    priority = Column(Integer)

    image_selector = Column(String)
    author_selector = Column(String)
    label_selector = Column(String)

    default_image = Column(String)

    disable = Column(Boolean)

    analytics_id = Column(String)

    category_id = Column(Integer)

    pubDate = Column(String)

    debug = Column(Boolean)

    debug_link = Column(Boolean)

    disable = Column(Boolean)
    

    # authors = relationship("Author", back_populates="from_source", lazy = True)

    
