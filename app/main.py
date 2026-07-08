from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.authentication import auth_router
from app.database import create_db_and_tables
from app.routers import urls, users
from datetime import datetime, timezone
from config import Config
from contextlib import asynccontextmanager
from app.middlewares.logger_middleware import LogCorrelationIdMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

@asynccontextmanager
async def lifespan(app):
    await create_db_and_tables()
    yield

app = FastAPI(
    title="URL_Shortner",
    description="This API powers a URL shortener app built with FastAPI.",
    version=Config.VERSION,
    lifespan=lifespan
)

# 2. Define allowed origins
origins = [
    "http://localhost:5173",
]

# 3. Add the middleware to the app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix=Config.URL_PREFIX)
app.include_router(users.router, prefix=Config.URL_PREFIX)
app.include_router(urls.router, prefix=Config.URL_PREFIX)

app.add_middleware(LogCorrelationIdMiddleware)

@app.get(f"{Config.URL_PREFIX}/health")
async def health_check():
    return {
            "status": "HEALTHY",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "version": Config.VERSION
        }

# Initialize and expose the /metrics endpoint
Instrumentator().instrument(app).expose(app)

# Mount the MCP server at /mcp
from app.mcp.server import setup_mcp
setup_mcp(app)
