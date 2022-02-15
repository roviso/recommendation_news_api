from sqlalchemy import Boolean, Column, ForeignKey, Integer, String,ForeignKey
from database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'user'
    # id = Column(Integer, primary_key =True, index=True)
    username = Column(String)
    email = Column(String, primary_key =True)
    full_name = Column(String)
    disabled = Column(Boolean)

    hashed_password = Column(String)
