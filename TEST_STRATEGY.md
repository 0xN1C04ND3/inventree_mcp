# InvenTree MCP Test Strategy

## Overview

This document outlines the test strategy for the InvenTree MCP server. It defines a three-tier testing approach focused on essential functionality while maintaining fast feedback loops.

**Last Updated**: February 15, 2026  
**Status**: Planning Document - Tests to be implemented

---

## Test Architecture

### Three-Tier Testing Model

```
┌─────────────────────────────────────────────────────────────┐
│                    @pytest.mark.integration                  │
│              Real InvenTree API + MCP Protocol               │
│                    ~20-30 sec per test                       │
│                      (5-8 tests)                             │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────┐
│                   @pytest.mark.mcp_client                    │
│             MCP Protocol Tests (Mocked API)                  │
│                     ~2-5 sec per test                        │
│                      (8-12 tests)                            │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────┐
│                      @pytest.mark.unit                       │
│           Fast Unit Tests (No Dependencies)                  │
│                    ~0.1 sec per test                         │
│                      (10-15 tests)                           │
└─────────────────────────────────────────────────────────────┘
```

### Test Markers

```python
@pytest.mark.unit          # Fast, no external deps, no MCP server
@pytest.mark.mcp_client    # MCP protocol tests (mocked or real API)
@pytest.mark.integration   # Real InvenTree API required
```

---

## Priority Coverage: Tier 1 + Purchase Order

### Tools to Test

| Tool | Priority | Operations | Reasoning |
|------|----------|------------|-----------|
| `system` | 🔴 Critical | status | Health checks, connectivity validation |
| `part` | 🔴 Critical | list, get, create, update | Core inventory management |
| `stock` | 🔴 Critical | list, get | Stock tracking is essential |
| `purchase_order` | 🟡 High | list, get, create | Critical procurement workflow |

**Total Test Count**: ~25-30 tests across all tiers

---

## Directory Structure

```
mcp-servers/inventree/
├── tests/
│   ├── __init__.py
│   ├── conftest.py                    # Shared fixtures and configuration
│   │
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_client.py             # Client initialization
│   │   ├── test_utils.py              # Utility functions
│   │   └── test_validation.py         # Input validation
│   │
│   ├── mcp_client/
│   │   ├── __init__.py
│   │   ├── test_system_tool.py        # System tool via MCP (mocked)
│   │   ├── test_part_tool.py          # Part tool via MCP (mocked)
│   │   ├── test_stock_tool.py         # Stock tool via MCP (mocked)
│   │   └── test_purchase_tool.py      # Purchase order tool via MCP (mocked)
│   │
│   └── integration/
│       ├── __init__.py
│       ├── test_system_integration.py # System tool + real API
│       ├── test_part_integration.py   # Part tool + real API
│       ├── test_stock_integration.py  # Stock tool + real API
│       └── test_purchase_integration.py # PO tool + real API
│
├── pyproject.toml                     # Updated with test config
└── TEST_STRATEGY.md                   # This document
```

---

## Test Implementation Details

### 1. Configuration (`conftest.py`)

```python
"""Shared test fixtures and configuration for InvenTree MCP tests."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastmcp import FastMCP, Client
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.utilities.tests import run_server_async


# ── Fixtures for mocked InvenTree client ────────────────────────────

@pytest.fixture
def mock_inventree_client():
    """Create a mocked InvenTree client for unit/mcp_client tests."""
    client = MagicMock()
    
    # Mock common methods
    client.part_list = AsyncMock(return_value=[
        {"pk": 1, "name": "Resistor 10k", "IPN": "R-10K-001"},
        {"pk": 2, "name": "Capacitor 100nF", "IPN": "C-100N-001"},
    ])
    client.part_get = AsyncMock(return_value={
        "pk": 1, "name": "Resistor 10k", "IPN": "R-10K-001"
    })
    client.part_create = AsyncMock(return_value={
        "pk": 3, "name": "New Part", "IPN": "NEW-001"
    })
    
    client.stock_list = AsyncMock(return_value=[
        {"pk": 1, "part": 1, "quantity": 100},
    ])
    
    client.purchase_order_list = AsyncMock(return_value=[
        {"pk": 1, "reference": "PO-001", "status": 10},
    ])
    
    client.system_status = AsyncMock(return_value={
        "server": "InvenTree", "version": "0.15.0", "up": True
    })
    
    return client


@pytest.fixture
async def mcp_server_with_mock_client(mock_inventree_client, monkeypatch):
    """Create MCP server with mocked InvenTree client."""
    from inventree_mcp import server
    
    # Replace the get_client function to return our mock
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


# ── Fixtures for real integration tests ─────────────────────────────

@pytest.fixture
def inventree_connection_params():
    """Get InvenTree connection params from environment."""
    import os
    url = os.getenv("INVENTREE_URL")
    token = os.getenv("INVENTREE_TOKEN")
    
    if not url or not token:
        pytest.skip("INVENTREE_URL and INVENTREE_TOKEN must be set for integration tests")
    
    return {"url": url, "token": token}


@pytest.fixture
async def mcp_server_with_real_client(inventree_connection_params):
    """Create MCP server with real InvenTree connection."""
    from inventree_mcp import server
    
    # Server will use real environment variables
    async with run_server_async(server.mcp) as url:
        yield url


# ── Helper functions ─────────────────────────────────────────────────

def assert_mcp_tool_response(result, expected_keys=None):
    """Assert MCP tool response is valid."""
    assert result is not None
    assert hasattr(result, 'content')
    assert len(result.content) > 0
    
    # First content should be text with JSON
    content = result.content[0]
    assert hasattr(content, 'text')
    
    if expected_keys:
        import json
        data = json.loads(content.text)
        for key in expected_keys:
            assert key in data, f"Expected key '{key}' not found in response"
```

---

### 2. Unit Tests (`tests/unit/`)

#### `test_client.py`
```python
"""Unit tests for InvenTree client initialization and configuration."""

import pytest
from inventree_mcp.client import InvenTreeClient


@pytest.mark.unit
def test_client_initialization():
    """Test client can be initialized with valid params."""
    client = InvenTreeClient("http://localhost:8000", "test-token-123")
    assert client.url == "http://localhost:8000"
    assert client.token == "test-token-123"


@pytest.mark.unit
def test_client_requires_url():
    """Test client initialization fails without URL."""
    with pytest.raises(TypeError):
        InvenTreeClient(token="test-token")


@pytest.mark.unit
def test_client_requires_token():
    """Test client initialization fails without token."""
    with pytest.raises(TypeError):
        InvenTreeClient(url="http://localhost:8000")
```

#### `test_utils.py`
```python
"""Unit tests for utility functions."""

import pytest
from inventree_mcp.utils import _json, _safe


@pytest.mark.unit
def test_json_serialization():
    """Test _json utility serializes dictionaries."""
    data = {"key": "value", "number": 42}
    result = _json(data)
    assert isinstance(result, str)
    assert "key" in result
    assert "42" in result


@pytest.mark.unit
def test_json_handles_lists():
    """Test _json utility handles list data."""
    data = [{"id": 1}, {"id": 2}]
    result = _json(data)
    assert isinstance(result, str)
    assert "id" in result
```

#### `test_validation.py`
```python
"""Unit tests for input validation."""

import pytest


@pytest.mark.unit
def test_operation_validation():
    """Test that invalid operations are rejected."""
    # This would test any validation logic in the API modules
    # Example placeholder - adjust based on actual validation logic
    pass


@pytest.mark.unit
def test_pk_validation():
    """Test that invalid primary keys are rejected."""
    # Test validation of pk parameters
    pass
```

---

### 3. MCP Client Tests (`tests/mcp_client/`)

These tests verify the MCP protocol layer works correctly with mocked InvenTree API.

#### `test_system_tool.py`
```python
"""MCP client tests for system tool (mocked API)."""

import pytest
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_system_status_via_mcp(mcp_server_with_mock_client):
    """Test system status tool via MCP protocol with mocked API."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        result = await client.call_tool("system", {
            "operation": "status"
        })
        
        assert_mcp_tool_response(result, expected_keys=["server", "version"])
        
        import json
        data = json.loads(result.content[0].text)
        assert data["server"] == "InvenTree"
        assert "version" in data


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_system_tool_registration(mcp_server_with_mock_client):
    """Test that system tool is properly registered in MCP."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        tools = await client.list_tools()
        
        tool_names = [tool.name for tool in tools.tools]
        assert "system" in tool_names
        
        # Find system tool and verify it has expected schema
        system_tool = next(t for t in tools.tools if t.name == "system")
        assert system_tool.inputSchema is not None
```

#### `test_part_tool.py`
```python
"""MCP client tests for part tool (mocked API)."""

import pytest
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_part_list_via_mcp(mcp_server_with_mock_client):
    """Test part list operation via MCP protocol."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        result = await client.call_tool("part", {
            "operation": "list",
            "limit": 10
        })
        
        assert_mcp_tool_response(result)
        
        import json
        data = json.loads(result.content[0].text)
        assert isinstance(data, list)
        assert len(data) > 0
        assert "name" in data[0]


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_part_get_via_mcp(mcp_server_with_mock_client):
    """Test part get operation via MCP protocol."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        result = await client.call_tool("part", {
            "operation": "get",
            "pk": 1
        })
        
        assert_mcp_tool_response(result, expected_keys=["pk", "name"])


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_part_create_via_mcp(mcp_server_with_mock_client, sample_part_data):
    """Test part create operation via MCP protocol."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        result = await client.call_tool("part", {
            "operation": "create",
            "data": sample_part_data
        })
        
        assert_mcp_tool_response(result, expected_keys=["pk", "name"])
        
        import json
        data = json.loads(result.content[0].text)
        assert data["pk"] is not None


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_part_search_via_mcp(mcp_server_with_mock_client):
    """Test part search via MCP protocol."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        result = await client.call_tool("part", {
            "operation": "list",
            "search": "resistor"
        })
        
        assert_mcp_tool_response(result)


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_part_tool_registration(mcp_server_with_mock_client):
    """Test that part tool is properly registered with correct schema."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        tools = await client.list_tools()
        
        tool_names = [tool.name for tool in tools.tools]
        assert "part" in tool_names
        
        part_tool = next(t for t in tools.tools if t.name == "part")
        assert part_tool.inputSchema is not None
        
        # Verify required parameters
        schema = part_tool.inputSchema
        assert "operation" in schema.get("properties", {})
```

#### `test_stock_tool.py`
```python
"""MCP client tests for stock tool (mocked API)."""

import pytest
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_stock_list_via_mcp(mcp_server_with_mock_client):
    """Test stock list operation via MCP protocol."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        result = await client.call_tool("stock", {
            "operation": "list",
            "limit": 25
        })
        
        assert_mcp_tool_response(result)
        
        import json
        data = json.loads(result.content[0].text)
        assert isinstance(data, list)


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_stock_get_via_mcp(mcp_server_with_mock_client):
    """Test stock get operation via MCP protocol."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        result = await client.call_tool("stock", {
            "operation": "get",
            "pk": 1
        })
        
        assert_mcp_tool_response(result, expected_keys=["pk", "part", "quantity"])


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_stock_filter_by_part(mcp_server_with_mock_client):
    """Test stock filtering by part ID via MCP."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        result = await client.call_tool("stock", {
            "operation": "list",
            "part": 1
        })
        
        assert_mcp_tool_response(result)
```

#### `test_purchase_tool.py`
```python
"""MCP client tests for purchase_order tool (mocked API)."""

import pytest
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_purchase_order_list_via_mcp(mcp_server_with_mock_client):
    """Test purchase order list operation via MCP protocol."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        result = await client.call_tool("purchase_order", {
            "operation": "list",
            "limit": 25
        })
        
        assert_mcp_tool_response(result)
        
        import json
        data = json.loads(result.content[0].text)
        assert isinstance(data, list)


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_purchase_order_get_via_mcp(mcp_server_with_mock_client):
    """Test purchase order get operation via MCP protocol."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        result = await client.call_tool("purchase_order", {
            "operation": "get",
            "pk": 1
        })
        
        assert_mcp_tool_response(result, expected_keys=["pk", "reference"])


@pytest.mark.mcp_client
@pytest.mark.asyncio
async def test_purchase_order_create_via_mcp(
    mcp_server_with_mock_client,
    sample_purchase_order_data
):
    """Test purchase order create operation via MCP protocol."""
    async with Client(StreamableHttpTransport(mcp_server_with_mock_client)) as client:
        result = await client.call_tool("purchase_order", {
            "operation": "create",
            "data": sample_purchase_order_data
        })
        
        assert_mcp_tool_response(result, expected_keys=["pk", "reference"])
```

---

### 4. Integration Tests (`tests/integration/`)

These tests use a real InvenTree instance. **Requires test environment setup.**

#### `test_system_integration.py`
```python
"""Integration tests for system tool with real InvenTree API."""

import pytest
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


@pytest.mark.integration
@pytest.mark.asyncio
async def test_system_status_real_api(mcp_server_with_real_client):
    """Test system status with real InvenTree connection."""
    async with Client(StreamableHttpTransport(mcp_server_with_real_client)) as client:
        result = await client.call_tool("system", {
            "operation": "status"
        })
        
        assert_mcp_tool_response(result, expected_keys=["server"])
        
        import json
        data = json.loads(result.content[0].text)
        assert "version" in data or "server" in data
        print(f"✓ Connected to InvenTree: {data}")
```

#### `test_part_integration.py`
```python
"""Integration tests for part tool with real InvenTree API."""

import pytest
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


@pytest.mark.integration
@pytest.mark.asyncio
async def test_part_list_real_api(mcp_server_with_real_client):
    """Test part list with real InvenTree API."""
    async with Client(StreamableHttpTransport(mcp_server_with_real_client)) as client:
        result = await client.call_tool("part", {
            "operation": "list",
            "limit": 5
        })
        
        assert_mcp_tool_response(result)
        
        import json
        data = json.loads(result.content[0].text)
        assert isinstance(data, list)
        print(f"✓ Retrieved {len(data)} parts from InvenTree")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_part_search_real_api(mcp_server_with_real_client):
    """Test part search with real InvenTree API."""
    async with Client(StreamableHttpTransport(mcp_server_with_real_client)) as client:
        result = await client.call_tool("part", {
            "operation": "list",
            "search": "test",
            "limit": 5
        })
        
        assert_mcp_tool_response(result)


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.skip(reason="Creates real data - only run manually")
async def test_part_create_real_api(mcp_server_with_real_client, sample_part_data):
    """Test part creation with real InvenTree API.
    
    WARNING: This creates real data in InvenTree.
    Only run in test environments.
    """
    async with Client(StreamableHttpTransport(mcp_server_with_real_client)) as client:
        result = await client.call_tool("part", {
            "operation": "create",
            "data": sample_part_data
        })
        
        assert_mcp_tool_response(result, expected_keys=["pk"])
        
        import json
        data = json.loads(result.content[0].text)
        created_pk = data["pk"]
        print(f"✓ Created part with PK: {created_pk}")
        
        # TODO: Clean up - delete the created part
```

#### `test_stock_integration.py`
```python
"""Integration tests for stock tool with real InvenTree API."""

import pytest
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


@pytest.mark.integration
@pytest.mark.asyncio
async def test_stock_list_real_api(mcp_server_with_real_client):
    """Test stock list with real InvenTree API."""
    async with Client(StreamableHttpTransport(mcp_server_with_real_client)) as client:
        result = await client.call_tool("stock", {
            "operation": "list",
            "limit": 10
        })
        
        assert_mcp_tool_response(result)
        
        import json
        data = json.loads(result.content[0].text)
        print(f"✓ Retrieved {len(data)} stock items from InvenTree")
```

#### `test_purchase_integration.py`
```python
"""Integration tests for purchase_order tool with real InvenTree API."""

import pytest
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


@pytest.mark.integration
@pytest.mark.asyncio
async def test_purchase_order_list_real_api(mcp_server_with_real_client):
    """Test purchase order list with real InvenTree API."""
    async with Client(StreamableHttpTransport(mcp_server_with_real_client)) as client:
        result = await client.call_tool("purchase_order", {
            "operation": "list",
            "limit": 10
        })
        
        assert_mcp_tool_response(result)
        
        import json
        data = json.loads(result.content[0].text)
        print(f"✓ Retrieved {len(data)} purchase orders from InvenTree")


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.skip(reason="Creates real data - only run manually")
async def test_purchase_order_create_real_api(
    mcp_server_with_real_client,
    sample_purchase_order_data
):
    """Test purchase order creation with real InvenTree API.
    
    WARNING: This creates real data in InvenTree.
    Only run in test environments.
    """
    async with Client(StreamableHttpTransport(mcp_server_with_real_client)) as client:
        result = await client.call_tool("purchase_order", {
            "operation": "create",
            "data": sample_purchase_order_data
        })
        
        assert_mcp_tool_response(result, expected_keys=["pk", "reference"])
```

---

## pyproject.toml Configuration

Add the following to `pyproject.toml`:

```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-mock>=3.12.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
markers = [
    "unit: marks tests as unit tests (no external dependencies)",
    "mcp_client: marks tests as MCP client protocol tests",
    "integration: marks tests as integration tests (require real InvenTree API)",
]
# Ignore warnings from dependencies
filterwarnings = [
    "ignore::DeprecationWarning",
]
```

---

## Running Tests

### Development Workflow

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Fast feedback - unit tests only (~2 seconds)
pytest -m "unit" -v

# Medium - unit + MCP client tests with mocked API (~10 seconds)
pytest -m "unit or mcp_client" -v

# Full test suite excluding integration (~15 seconds)
pytest -m "not integration" -v

# Integration tests only (requires real InvenTree)
pytest -m "integration" -v --tb=short

# Everything (~30 seconds)
pytest -v

# Specific test file
pytest tests/mcp_client/test_part_tool.py -v

# With coverage
pytest --cov=inventree_mcp --cov-report=html
```

### CI/CD Pipeline

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  unit-tests:
    name: Unit Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install uv
          uv pip install -e ".[dev]"
      - name: Run unit tests
        run: pytest -m "unit" -v

  mcp-client-tests:
    name: MCP Client Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install uv
          uv pip install -e ".[dev]"
      - name: Run MCP client tests
        run: pytest -m "mcp_client" -v

  integration-tests:
    name: Integration Tests
    runs-on: ubuntu-latest
    # Only run on main branch or PRs
    if: github.ref == 'refs/heads/main' || github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Start InvenTree test instance
        run: |
          # TODO: Add docker-compose or test instance setup
          echo "Test InvenTree instance needed"
      - name: Install dependencies
        run: |
          pip install uv
          uv pip install -e ".[dev]"
      - name: Run integration tests
        run: pytest -m "integration" -v
        env:
          INVENTREE_URL: http://localhost:8000
          INVENTREE_TOKEN: ${{ secrets.INVENTREE_TEST_TOKEN }}
```

---

## Test Environment Setup

### For Integration Tests

Integration tests require a real InvenTree instance. Options:

#### Option 1: Local Docker Instance

```bash
# Start InvenTree for testing
docker run -d \
  --name inventree-test \
  -p 8000:8000 \
  -e INVENTREE_ADMIN_USER=admin \
  -e INVENTREE_ADMIN_PASSWORD=admin123 \
  -e INVENTREE_ADMIN_EMAIL=admin@test.com \
  inventree/inventree:latest

# Wait for startup
sleep 30

# Get API token
# (Visit http://localhost:8000 and create token in admin panel)

# Set environment variables
export INVENTREE_URL=http://localhost:8000
export INVENTREE_TOKEN=your-token-here

# Run integration tests
pytest -m "integration" -v

# Cleanup
docker stop inventree-test
docker rm inventree-test
```

#### Option 2: Dedicated Test Instance

Set up a persistent test InvenTree instance for CI/CD:

```bash
# .env.test
INVENTREE_URL=https://test.inventree.example.com
INVENTREE_TOKEN=test-token-from-admin-panel
```

---

## Coverage Goals

| Test Tier | Target Coverage | What's Covered |
|-----------|----------------|----------------|
| Unit | 80%+ | Utils, validation, client init |
| MCP Client | 100% | All 4 critical tools via MCP |
| Integration | Smoke tests | Real API connectivity |

**Overall Goal**: 70-80% code coverage with fast feedback loops

---

## Maintenance

### When to Update Tests

- ✅ **Adding new MCP tool** → Add mcp_client test
- ✅ **Changing API operation** → Update relevant unit/mcp tests
- ✅ **Changing response format** → Update assertions
- ✅ **FastMCP upgrade** → Verify all mcp_client tests still pass
- ✅ **InvenTree API changes** → Update integration tests

### Test Review Checklist

- [ ] All tests have clear docstrings
- [ ] Proper markers (@unit, @mcp_client, @integration)
- [ ] Integration tests skip gracefully without credentials
- [ ] No hardcoded secrets or credentials
- [ ] Tests are independent (no order dependencies)
- [ ] Fast tests run in <1 second each
- [ ] MCP tests use proper async patterns

---

## Future Enhancements

### Phase 2 (Optional)
- Add tests for remaining tools (build_order, sales_order, etc.)
- Add performance/load tests
- Add test coverage reporting
- Add mutation testing

### Phase 3 (Advanced)
- Contract testing with real InvenTree API
- Snapshot testing for responses
- Property-based testing with Hypothesis
- Test data factories

---

## References

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [FastMCP testing utilities](https://github.com/jlowin/fastmcp)
- [InvenTree API documentation](https://docs.inventree.org/en/latest/api/api/)

---

## Questions & Support

For questions about implementing these tests:
1. Review this document
2. Check existing test examples in the codebase
3. Consult FastMCP test utilities documentation
4. Create an issue in the project repository

**Document Status**: Ready for implementation ✅
