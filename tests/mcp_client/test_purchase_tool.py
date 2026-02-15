"""MCP client tests for purchase_order tool (mocked API)."""

import json

import pytest
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_purchase_order_list_via_mcp(mcp_server_with_mock_client):
    """Test purchase order list operation via MCP protocol."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        result = await client.call_tool(
            "purchase_order", {"operation": "list", "limit": 25}
        )

        assert result is not None
        assert hasattr(result, "content")
        assert len(result.content) > 0

        data = json.loads(result.content[0].text)
        assert isinstance(data, list)
        assert len(data) > 0


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_purchase_order_get_via_mcp(mcp_server_with_mock_client):
    """Test purchase order get operation via MCP protocol."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        result = await client.call_tool("purchase_order", {"operation": "get", "pk": 1})

        assert result is not None
        assert hasattr(result, "content")
        assert len(result.content) > 0

        data = json.loads(result.content[0].text)
        assert "pk" in data
        assert "reference" in data


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_purchase_order_create_via_mcp(
    mcp_server_with_mock_client, sample_purchase_order_data
):
    """Test purchase order create operation via MCP protocol."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        result = await client.call_tool(
            "purchase_order",
            {"operation": "create", "data": sample_purchase_order_data},
        )

        assert result is not None
        assert hasattr(result, "content")
        assert len(result.content) > 0

        data = json.loads(result.content[0].text)
        assert "pk" in data
        assert "reference" in data


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_purchase_order_tool_registration(mcp_server_with_mock_client):
    """Test that purchase_order tool is properly registered with correct schema."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        tools = await client.list_tools()

        tool_names = [tool.name for tool in tools]
        assert "purchase_order" in tool_names

        po_tool = next(t for t in tools if t.name == "purchase_order")
        assert po_tool.inputSchema is not None

        schema = po_tool.inputSchema
        assert "operation" in schema.get("properties", {})


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_purchase_order_with_limit(mcp_server_with_mock_client):
    """Test purchase order list with limit via MCP protocol."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        result = await client.call_tool(
            "purchase_order", {"operation": "list", "limit": 5}
        )

        assert result is not None
        assert hasattr(result, "content")
        assert len(result.content) > 0
