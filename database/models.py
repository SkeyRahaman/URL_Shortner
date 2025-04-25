from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Relationship

Base = declarative_base()

class DBUser(Base):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String)
    email = Column(String)
    password = Column(String)
    urls = Relationship("DBUrl", back_populates="user")

class DBUrl(Base):
    __tablename__ = "Urls"
    id = Column(Integer, primary_key=True, index=True)
    long_url = Column(String)
    short_url = Column(String)
    description = Column(String)
    user_id = Column(Integer, ForeignKey("Users.id"))
    user = Relationship("DBUser", back_populates="urls")