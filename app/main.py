from fastapi import FastAPI
from app.authentication import auth_router
from app.database import engine, models
from app.routers import urls, users
from datetime import datetime,timezone
from config import Config
import os
import signal

app = FastAPI(
    title="URL_Shortner",
    description="This API powers a URL shortener app built with FastAPI.",
    version=Config.VERSION
)
models.Base.metadata.create_all(engine)

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

@app.get(f"{Config.URL_PREFIX}/CRASH")
async def crash_app():
    os.kill(os.getpid(), signal.SIGTERM)  # or SIGKILL
    return {"status": "CRASHED"}  # This line will not execute