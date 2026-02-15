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
def test_client_url_stored_correctly():
    """Test URL is stored correctly."""
    client = InvenTreeClient("https://inventree.example.com", "token")
    assert client.url == "https://inventree.example.com"


@pytest.mark.unit
def test_client_token_stored_correctly():
    """Test token is stored correctly."""
    client = InvenTreeClient("http://localhost:8000", "my-secret-token")
    assert client.token == "my-secret-token"


@pytest.mark.unit
def test_client_api_initially_none():
    """Test that _api is initially None before connection."""
    client = InvenTreeClient("http://localhost:8000", "test-token")
    assert client._api is None


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


@pytest.mark.unit
def test_client_equality():
    """Test client instances with same params are equal."""
    client1 = InvenTreeClient("http://localhost:8000", "token")
    client2 = InvenTreeClient("http://localhost:8000", "token")
    assert client1.url == client2.url
    assert client1.token == client2.token
