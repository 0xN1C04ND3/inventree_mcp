"""Integration tests for part tool with real InvenTree API."""

import json
import os

import pytest
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.utilities.tests import run_server_async


def is_integration_configured():
    """Check if integration tests can run."""
    return bool(os.getenv("INVENTREE_URL") and os.getenv("INVENTREE_TOKEN"))


@pytest.mark.integration
@pytest.mark.asyncio
async def test_part_list_real_api():
    """Test part list with real InvenTree API."""
    if not is_integration_configured():
        pytest.skip(
            "INVENTREE_URL and INVENTREE_TOKEN must be set for integration tests"
        )

    os.environ.setdefault("INVENTREE_URL", os.getenv("INVENTREE_URL"))
    os.environ.setdefault("INVENTREE_TOKEN", os.getenv("INVENTREE_TOKEN"))

    from inventree_mcp import server

    async with run_server_async(server.mcp) as url:
        async with Client(StreamableHttpTransport(url)) as client:
            result = await client.call_tool("part", {"operation": "list", "limit": 5})

            assert result is not None
            assert hasattr(result, "content")
            assert len(result.content) > 0

            data = json.loads(result.content[0].text)
            print(
                f"✓ Retrieved {len(data) if isinstance(data, list) else 'error'} parts from InvenTree"
            )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_part_search_real_api():
    """Test part search with real InvenTree API."""
    if not is_integration_configured():
        pytest.skip(
            "INVENTREE_URL and INVENTREE_TOKEN must be set for integration tests"
        )

    os.environ.setdefault("INVENTREE_URL", os.getenv("INVENTREE_URL"))
    os.environ.setdefault("INVENTREE_TOKEN", os.getenv("INVENTREE_TOKEN"))

    from inventree_mcp import server

    async with run_server_async(server.mcp) as url:
        async with Client(StreamableHttpTransport(url)) as client:
            result = await client.call_tool(
                "part", {"operation": "list", "search": "test", "limit": 5}
            )

            assert result is not None
            assert hasattr(result, "content")
            assert len(result.content) > 0
