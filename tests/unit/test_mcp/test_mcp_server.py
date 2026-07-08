import pytest
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

from app.mcp.server import setup_mcp


class TestSetupMcp:
    """Unit tests for the setup_mcp function."""

    def test_setup_mcp_returns_mcp_instance(self):
        """setup_mcp should return a FastApiMCP instance."""
        test_app = FastAPI()
        mcp = setup_mcp(test_app)
        assert isinstance(mcp, FastApiMCP)

    def test_setup_mcp_mounts_mcp_route(self):
        """After setup_mcp, the app should have a /mcp route registered."""
        test_app = FastAPI()
        setup_mcp(test_app)
        route_paths = [route.path for route in test_app.routes]
        assert any("/mcp" in path for path in route_paths)

    def test_setup_mcp_uses_correct_name(self):
        """The MCP server should be created with the app title as its name."""
        test_app = FastAPI(title="Test App")
        mcp = setup_mcp(test_app)
        assert mcp.name == "Test App"
