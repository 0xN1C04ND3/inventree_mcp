"""Integration tests for system tool with real InvenTree API."""

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
async def test_system_status_real_api():
    """Test system status with real InvenTree connection."""
    if not is_integration_configured():
        pytest.skip(
            "INVENTREE_URL and INVENTREE_TOKEN must be set for integration tests"
        )

    os.environ.setdefault("INVENTREE_URL", os.getenv("INVENTREE_URL"))
    os.environ.setdefault("INVENTREE_TOKEN", os.getenv("INVENTREE_TOKEN"))

    from inventree_mcp import server

    async with run_server_async(server.mcp) as url:
        async with Client(StreamableHttpTransport(url)) as client:
            result = await client.call_tool("system", {"operation": "status"})

            assert result is not None
            assert hasattr(result, "content")
            assert len(result.content) > 0

            data = json.loads(result.content[0].text)
            assert "server" in data or "version" in data or "error" not in data
            print(f"✓ Connected to InvenTree: {data}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_system_version_real_api():
    """Test system version with real InvenTree connection."""
    if not is_integration_configured():
        pytest.skip(
            "INVENTREE_URL and INVENTREE_TOKEN must be set for integration tests"
        )

    os.environ.setdefault("INVENTREE_URL", os.getenv("INVENTREE_URL"))
    os.environ.setdefault("INVENTREE_TOKEN", os.getenv("INVENTREE_TOKEN"))

    from inventree_mcp import server

    async with run_server_async(server.mcp) as url:
        async with Client(StreamableHttpTransport(url)) as client:
            result = await client.call_tool("system", {"operation": "version"})

            assert result is not None
            assert hasattr(result, "content")
            assert len(result.content) > 0
