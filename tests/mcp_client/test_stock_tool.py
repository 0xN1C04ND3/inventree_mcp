"""MCP client tests for stock tool (mocked API)."""

import json

import pytest
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_stock_list_via_mcp(mcp_server_with_mock_client):
    """Test stock list operation via MCP protocol."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        result = await client.call_tool("stock", {"operation": "list", "limit": 25})

        assert result is not None
        assert hasattr(result, "content")
        assert len(result.content) > 0

        data = json.loads(result.content[0].text)
        assert isinstance(data, list)


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_stock_get_via_mcp(mcp_server_with_mock_client):
    """Test stock get operation via MCP protocol."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        result = await client.call_tool("stock", {"operation": "get", "pk": 1})

        assert result is not None
        assert hasattr(result, "content")
        assert len(result.content) > 0

        data = json.loads(result.content[0].text)
        assert "pk" in data
        assert data["pk"] == 1


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_stock_filter_by_part(mcp_server_with_mock_client):
    """Test stock filtering by part ID via MCP."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        result = await client.call_tool("stock", {"operation": "list", "part_id": 1})

        assert result is not None
        assert hasattr(result, "content")
        assert len(result.content) > 0


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_stock_filter_by_location(mcp_server_with_mock_client):
    """Test stock filtering by location via MCP."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        result = await client.call_tool(
            "stock", {"operation": "list", "location_id": 1}
        )

        assert result is not None
        assert hasattr(result, "content")
        assert len(result.content) > 0


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_stock_tool_registration(mcp_server_with_mock_client):
    """Test that stock tool is properly registered with correct schema."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        tools = await client.list_tools()

        tool_names = [tool.name for tool in tools]
        assert "stock" in tool_names

        stock_tool = next(t for t in tools if t.name == "stock")
        assert stock_tool.inputSchema is not None

        schema = stock_tool.inputSchema
        assert "operation" in schema.get("properties", {})
