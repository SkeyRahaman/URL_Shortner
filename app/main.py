from fastapi import FastAPI
from app.authentication import auth_router
from app.database import create_db_and_tables
from app.routers import urls, users
from datetime import datetime,timezone
from config import Config
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    # Code before yield runs at startup
    await create_db_and_tables()
    yield
    # Code after yield runs at shutdown


app = FastAPI(
    title="URL_Shortner",
    description="This API powers a URL shortener app built with FastAPI.",
    version=Config.VERSION,
    lifespan=lifespan
)
app.include_router(auth_router.router, prefix=Config.URL_PREFIX)
app.include_router(users.router, prefix=Config.URL_PREFIX)
app.include_router(urls.router, prefix=Config.URL_PREFIX)

@app.get(f"{Config.URL_PREFIX}/health")
async def health_check():
    return {
            "status": "HEALTHY",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "version": Config.VERSION
        }