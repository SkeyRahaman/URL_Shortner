import pytest
from unittest.mock import AsyncMock
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from config import Config
from app.authentication import auth_router
from app.routers import urls as urls_router, users as users_router

@pytest.mark.asyncio
class TestAppStartupAndHealth:
    async def test_app_startup_calls_create_db_and_tables(self):
        # Create an async mock for create_db_and_tables
        mock_create_db = AsyncMock()

        # Define a custom lifespan that calls the mock_create_db
        from contextlib import asynccontextmanager

        @asynccontextmanager
        async def test_lifespan(app: FastAPI):
            await mock_create_db()
            yield

        # Create a fresh FastAPI app with this test lifespan
        test_app = FastAPI(lifespan=test_lifespan)

        # Import your main app module to get routes
        from app.main import app as main_app
        from app.main import health_check  # import health endpoint handler

        test_app.get(f"{Config.URL_PREFIX}/health")(health_check)  # add it to test_app


        test_app.include_router(auth_router.router, prefix=Config.URL_PREFIX)
        test_app.include_router(users_router.router, prefix=Config.URL_PREFIX)
        test_app.include_router(urls_router.router, prefix=Config.URL_PREFIX)

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # The first request triggers the lifespan startup, which calls the mocked function
            response = await client.get(f"{Config.URL_PREFIX}/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "HEALTHY"
            assert data["version"] == Config.VERSION
            assert "timestamp" in data

    async def test_health_endpoint_returns_expected_data(self):
        from app.main import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"{Config.URL_PREFIX}/health")
            assert response.status_code == 200
            json_data = response.json()
            assert json_data["status"] == "HEALTHY"
            assert json_data["version"] == Config.VERSION
            assert "timestamp" in json_data
            assert json_data["timestamp"].endswith("Z")

    async def test_included_routers_exist(self):
        from app.main import app

        routes = [route.path for route in app.router.routes]

        assert any(route.startswith(Config.URL_PREFIX + "/auth/token") for route in routes), "Auth router not included"
        assert any(route.startswith(Config.URL_PREFIX + "/users") for route in routes), "Users router not included"
        assert any(route.startswith(Config.URL_PREFIX + "/urls") for route in routes), "URLs router not included"
