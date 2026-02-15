"""MCP client tests for part tool (mocked API)."""

import json

import pytest
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_part_list_via_mcp(mcp_server_with_mock_client):
    """Test part list operation via MCP protocol."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        result = await client.call_tool("part", {"operation": "list", "limit": 10})

        assert result is not None
        assert hasattr(result, "content")
        assert len(result.content) > 0

        data = json.loads(result.content[0].text)
        assert isinstance(data, list)
        assert len(data) > 0
        assert "name" in data[0]


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_part_get_via_mcp(mcp_server_with_mock_client):
    """Test part get operation via MCP protocol."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        result = await client.call_tool("part", {"operation": "get", "pk": 1})

        assert result is not None
        assert hasattr(result, "content")
        assert len(result.content) > 0

        data = json.loads(result.content[0].text)
        assert "pk" in data
        assert data["pk"] == 1
        assert "name" in data


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_part_create_via_mcp(mcp_server_with_mock_client, sample_part_data):
    """Test part create operation via MCP protocol."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        result = await client.call_tool(
            "part", {"operation": "create", "data": sample_part_data}
        )

        assert result is not None
        assert hasattr(result, "content")
        assert len(result.content) > 0

        data = json.loads(result.content[0].text)
        assert "pk" in data
        assert data["pk"] is not None


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_part_search_via_mcp(mcp_server_with_mock_client):
    """Test part search via MCP protocol."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        result = await client.call_tool(
            "part", {"operation": "list", "search": "resistor"}
        )

        assert result is not None
        assert hasattr(result, "content")
        assert len(result.content) > 0

        data = json.loads(result.content[0].text)
        assert isinstance(data, list)


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_part_update_via_mcp(mcp_server_with_mock_client):
    """Test part update operation via MCP protocol."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        update_data = {"name": "Updated Resistor"}
        result = await client.call_tool(
            "part", {"operation": "update", "pk": 1, "data": update_data}
        )

        assert result is not None
        assert hasattr(result, "content")
        assert len(result.content) > 0


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_part_tool_registration(mcp_server_with_mock_client):
    """Test that part tool is properly registered with correct schema."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        tools = await client.list_tools()

        tool_names = [tool.name for tool in tools]
        assert "part" in tool_names

        part_tool = next(t for t in tools if t.name == "part")
        assert part_tool.inputSchema is not None

        schema = part_tool.inputSchema
        assert "operation" in schema.get("properties", {})


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_part_with_limit_and_offset(mcp_server_with_mock_client):
    """Test part list with pagination via MCP protocol."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        result = await client.call_tool(
            "part", {"operation": "list", "limit": 5, "offset": 10}
        )

        assert result is not None
        assert hasattr(result, "content")
        assert len(result.content) > 0
