from sqlalchemy import Boolean, Column, ForeignKey, Integer, String,ForeignKey, DateTime
from database import Base

class Tasks(Base):
    __tablename__ = 'tasks'
    id = Column(String, primary_key =True)
    status = Column(String)
    result = Column(String)
