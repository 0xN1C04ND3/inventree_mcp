"""MCP client tests for system tool (mocked API)."""

import json

import pytest
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_system_status_via_mcp(mcp_server_with_mock_client):
    """Test system status tool via MCP protocol with mocked API."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        result = await client.call_tool("system", {"operation": "health"})

        assert result is not None
        assert hasattr(result, "content")
        assert len(result.content) > 0

        data = json.loads(result.content[0].text)
        assert "server" in data or "version" in data


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_system_version_via_mcp(mcp_server_with_mock_client):
    """Test system version via MCP protocol."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        result = await client.call_tool("system", {"operation": "version"})

        assert result is not None
        assert hasattr(result, "content")
        assert len(result.content) > 0


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_system_tool_registration(mcp_server_with_mock_client):
    """Test that system tool is properly registered in MCP."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        tools = await client.list_tools()

        tool_names = [tool.name for tool in tools]
        assert "system" in tool_names

        system_tool = next(t for t in tools if t.name == "system")
        assert system_tool.inputSchema is not None


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_system_settings_via_mcp(mcp_server_with_mock_client):
    """Test system settings via MCP protocol."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        result = await client.call_tool("system", {"operation": "settings"})

        assert result is not None
        assert hasattr(result, "content")
