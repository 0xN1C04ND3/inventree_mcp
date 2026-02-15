"""Shared test fixtures and configuration for InvenTree MCP tests."""

import json
import os
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.utilities.tests import run_server_async


@pytest.fixture(scope="session")
def event_loop_policy():
    """Use default event loop policy."""
    import asyncio

    return asyncio.DefaultEventLoopPolicy()


@pytest.fixture
def mock_inventree_client():
    """Create a mocked InvenTree client for unit/mcp_client tests."""
    client = MagicMock()

    client.part_list = AsyncMock(
        return_value=[
            {"pk": 1, "name": "Resistor 10k", "IPN": "R-10K-001"},
            {"pk": 2, "name": "Capacitor 100nF", "IPN": "C-100N-001"},
        ]
    )
    client.part_get = AsyncMock(
        return_value={
            "pk": 1,
            "name": "Resistor 10k",
            "IPN": "R-10K-001",
            "description": "10k Ohm resistor",
        }
    )
    client.part_create = AsyncMock(
        return_value={
            "pk": 3,
            "name": "New Part",
            "IPN": "NEW-001",
        }
    )
    client.part_update = AsyncMock(
        return_value={
            "pk": 1,
            "name": "Updated Resistor",
            "IPN": "R-10K-001",
        }
    )
    client.part_delete = AsyncMock(return_value={"success": True})

    client.stock_list = AsyncMock(
        return_value=[
            {"pk": 1, "part": 1, "quantity": 100, "location": 1},
            {"pk": 2, "part": 2, "quantity": 500, "location": 1},
        ]
    )
    client.stock_get = AsyncMock(
        return_value={
            "pk": 1,
            "part": 1,
            "quantity": 100,
            "location": 1,
        }
    )

    client.po_list = AsyncMock(
        return_value=[
            {"pk": 1, "reference": "PO-001", "status": 10},
            {"pk": 2, "reference": "PO-002", "status": 20},
        ]
    )
    client.po_get = AsyncMock(
        return_value={
            "pk": 1,
            "reference": "PO-001",
            "status": 10,
            "supplier": 1,
        }
    )
    client.po_create = AsyncMock(
        return_value={
            "pk": 3,
            "reference": "PO-TEST-001",
            "status": 10,
        }
    )

    client.build_order_list = AsyncMock(
        return_value=[
            {"pk": 1, "reference": "BO-001", "status": 10},
        ]
    )
    client.build_order_get = AsyncMock(
        return_value={
            "pk": 1,
            "reference": "BO-001",
            "status": 10,
        }
    )

    client.sales_order_list = AsyncMock(
        return_value=[
            {"pk": 1, "reference": "SO-001", "status": 10},
        ]
    )
    client.sales_order_get = AsyncMock(
        return_value={
            "pk": 1,
            "reference": "SO-001",
            "status": 10,
        }
    )

    client.return_order_list = AsyncMock(
        return_value=[
            {"pk": 1, "reference": "RO-001", "status": 10},
        ]
    )
    client.return_order_get = AsyncMock(
        return_value={
            "pk": 1,
            "reference": "RO-001",
            "status": 10,
        }
    )

    client.company_list = AsyncMock(
        return_value=[
            {"pk": 1, "name": "Test Supplier", "type": "supplier"},
        ]
    )
    client.company_get = AsyncMock(
        return_value={
            "pk": 1,
            "name": "Test Supplier",
            "type": "supplier",
        }
    )

    client.barcode_lookup = AsyncMock(
        return_value={
            "pk": 1,
            "model": "part",
            "data": {"pk": 1, "name": "Resistor 10k"},
        }
    )

    client.label_print = AsyncMock(return_value={"success": True})

    client.report_print = AsyncMock(return_value={"success": True})

    client.attachment_upload = AsyncMock(
        return_value={
            "pk": 1,
            "attachment": "test.pdf",
        }
    )

    client.system_health = AsyncMock(
        return_value={
            "server": "InvenTree",
            "version": "0.15.0",
            "up": True,
        }
    )
    client.system_version = AsyncMock(
        return_value={
            "server": "http://localhost:8000",
            "api_version": "v3",
        }
    )
    client.system_settings = AsyncMock(
        return_value=[{"key": "setting1", "value": "value1"}]
    )

    return client


@pytest.fixture(scope="function")
async def mcp_server_with_mock_client(mock_inventree_client, monkeypatch):
    """Create MCP server with mocked InvenTree client."""
    import importlib
    import inventree_mcp.server

    importlib.reload(inventree_mcp.server)
    from inventree_mcp import server

    async def mock_get_client():
        return mock_inventree_client

    monkeypatch.setattr(server, "get_client", mock_get_client)

    async with run_server_async(server.mcp) as url:
        yield url


@pytest.fixture
def sample_part_data():
    """Sample part data for create/update tests."""
    return {
        "name": "Test Resistor",
        "description": "10k Ohm resistor for testing",
        "IPN": "TEST-R-10K",
        "category": 1,
        "active": True,
    }


@pytest.fixture
def sample_purchase_order_data():
    """Sample purchase order data for create tests."""
    return {
        "reference": "PO-TEST-001",
        "supplier": 1,
        "description": "Test purchase order",
    }


@pytest.fixture
def sample_stock_data():
    """Sample stock data for create tests."""
    return {
        "part": 1,
        "location": 1,
        "quantity": 100,
    }


@pytest.fixture
def inventree_connection_params():
    """Get InvenTree connection params from environment."""
    url = os.getenv("INVENTREE_URL")
    token = os.getenv("INVENTREE_TOKEN")

    if not url or not token:
        pytest.skip(
            "INVENTREE_URL and INVENTREE_TOKEN must be set for integration tests"
        )

    return {"url": url, "token": token}


@pytest.fixture
async def mcp_server_with_real_client(inventree_connection_params):
    """Create MCP server with real InvenTree connection."""
    from inventree_mcp import server

    os.environ["INVENTREE_URL"] = inventree_connection_params["url"]
    os.environ["INVENTREE_TOKEN"] = inventree_connection_params["token"]

    async with run_server_async(server.mcp) as url:
        yield url


def assert_mcp_tool_response(result, expected_keys=None):
    """Assert MCP tool response is valid."""
    assert result is not None, "MCP tool result should not be None"
    assert hasattr(result, "content"), "MCP tool result should have content"
    assert len(result.content) > 0, "MCP tool result should have at least one content"

    content = result.content[0]
    assert hasattr(content, "text"), "MCP tool content should have text"

    if expected_keys:
        data = json.loads(content.text)
        for key in expected_keys:
            assert key in data, f"Expected key '{key}' not found in response: {data}"
