from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from config import Config

engine = create_async_engine(Config.DATABASE_URL)
SessionLocal = async_sessionmaker(autoflush=False, autocommit = False, bind=engine)

async def get_db():
    with SessionLocal() as db:
        yield db
