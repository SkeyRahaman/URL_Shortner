from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import links
from datetime import datetime, timezone
from config import Config
from app.middlewares.logger_middleware import LogCorrelationIdMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from app.utils.logger import log

app = FastAPI(
    title="url_service",
    description="This API powers a URL shortener app built with FastAPI.",
    version=Config.VERSION
)

@app.on_event("startup")
async def startup_event():
    log.info("Starting up url_service API", version=Config.VERSION)

@app.on_event("shutdown")
async def shutdown_event():
    log.info("Shutting down url_service API")

# 2. Define allowed origins
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "https://skeyrahaman.github.io",
    "https://SkeyRahaman.github.io",
]

# 3. Add the middleware to the app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(links.router, prefix=Config.URL_PREFIX)

app.add_middleware(LogCorrelationIdMiddleware)

@app.get(
    f"{Config.URL_PREFIX}/health",
    operation_id="health_check",
    summary="Check API health status",
    response_description="Current health status, timestamp, and version"
)
async def health_check():
    """
    Check if the API is running and healthy. No authentication required.

    Returns the current health status, server timestamp (UTC), and API version.
    Use this tool to verify the service is available before making other calls.

    - **Returns**: {"status": "HEALTHY", "timestamp": "<ISO 8601 UTC>", "version": "<semver>"}
    - **Auth**: Not required (public endpoint)
    """
    log.info("health_check_requested")
    return {
            "status": "HEALTHY",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "version": Config.VERSION
        }

# Initialize and expose the /metrics endpoint
Instrumentator().instrument(app).expose(app)
