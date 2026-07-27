from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config import Config
from .models import Base

engine = create_async_engine(Config.DATABASE_URL)
SessionLocal = async_sessionmaker(autoflush=False, autocommit=False, bind=engine, expire_on_commit=False)
