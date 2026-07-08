import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.mcp.server import create_mcp


@pytest.mark.asyncio
@pytest.mark.usefixtures("setup_async_database")
class TestMcpIntegration:
    """Integration tests for the MCP server mounted on the FastAPI app."""

    @pytest_asyncio.fixture
    async def client(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

    async def test_mcp_endpoint_exists(self, client: AsyncClient):
        """The /mcp route should be registered (not 404)."""
        resp = await client.get("/mcp")
        assert resp.status_code != 404

    async def test_mcp_route_accepts_post(self, client: AsyncClient):
        """POST /mcp should be accepted (not 404 or 405)."""
        resp = await client.post(
            "/mcp",
            json={},
            headers={"Content-Type": "application/json"}
        )
        # Route exists and accepts POST — may return 500 in test env
        # due to session manager lifecycle, but NOT 404/405
        assert resp.status_code not in (404, 405)

    async def test_mcp_route_accepts_delete(self, client: AsyncClient):
        """DELETE /mcp should be accepted (not 404 or 405)."""
        resp = await client.delete("/mcp")
        assert resp.status_code not in (404, 405)

    def test_mcp_tools_registered(self):
        """The MCP server should have tools for all FastAPI endpoints."""
        mcp = create_mcp(app)
        tool_names = {tool.name for tool in mcp.tools}

        expected_tools = {
            "token_auth_token_post",
            "create_user_users_post",
            "get_current_user_users_me_get",
            "update_current_user_users_me_put",
            "delete_current_user_users_me_delete",
            "create_short_url_urls_create_short_url_post",
            "redirect_short_url_urls__short_url__get",
            "get_short_url_details_urls__short_url__details_get",
            "list_user_urls_urls_get",
            "update_short_url_urls__short_url__put",
            "delete_short_url_urls__short_url__delete",
            "health_check_health_get",
        }
        assert expected_tools.issubset(tool_names), (
            f"Missing tools: {expected_tools - tool_names}"
        )
