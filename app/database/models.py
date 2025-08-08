from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import Relationship
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class DBUser(Base):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String(100))
    email = Column(String(100))
    password = Column(String(200))
    urls = Relationship("DBUrl", back_populates="user")

class DBUrl(Base):
    __tablename__ = "Urls"
    id = Column(Integer, primary_key=True, index=True)
    long_url = Column(String(200))
    short_url = Column(String(50))
    description = Column(String(400))
    user_id = Column(Integer, ForeignKey("Users.id"))
    user = Relationship("DBUser", back_populates="urls")
    