from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_mcp import FastApiMCP


def create_mcp(app: FastAPI) -> FastApiMCP:
    """
    Create an MCP server from the FastAPI app.

    All existing FastAPI endpoints become MCP tools automatically.
    Tool names are derived from each route's `name` parameter.
    """
    mcp = FastApiMCP(app, name=app.title, description=app.description)
    return mcp


def setup_mcp(app: FastAPI) -> FastApiMCP:
    """
    Create an MCP server and mount it at /mcp using HTTP transport.
    """
    mcp = create_mcp(app)
    mcp.mount_http()
    return mcp
