"""Unit tests for utility functions."""

import json

import pytest
from inventree_mcp.utils import _json, _error, _safe


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


@pytest.mark.unit
def test_json_handles_none():
    """Test _json utility handles None values."""
    data = {"key": None, "value": "test"}
    result = _json(data)
    assert isinstance(result, str)
    assert "null" in result.lower()


@pytest.mark.unit
def test_json_uses_default_str():
    """Test _json uses default=str for non-serializable objects."""

    class NonSerializable:
        def __str__(self):
            return "custom-object"

    data = {"obj": NonSerializable()}
    result = _json(data)
    assert "custom-object" in result


@pytest.mark.unit
def test_error_404_not_found():
    """Test _error provides hint for 404 errors."""
    e = Exception("404 Not Found: /api/part/1/")
    result = _error(e, "part.get")
    data = json.loads(result)
    assert "error" in data
    assert "hint" in data
    assert "ID exists" in data["hint"]


@pytest.mark.unit
def test_error_403_permission():
    """Test _error provides hint for 403 permission errors."""
    e = Exception("403 Forbidden: Permission denied")
    result = _error(e, "part.create")
    data = json.loads(result)
    assert "permission" in data["hint"].lower()


@pytest.mark.unit
def test_error_400_bad_request():
    """Test _error provides hint for 400 bad request."""
    e = Exception("400 Bad Request: Invalid data")
    result = _error(e, "part.update")
    data = json.loads(result)
    assert "invalid" in data["hint"].lower()


@pytest.mark.unit
def test_error_timeout():
    """Test _error provides hint for timeout errors."""
    e = Exception("Connection timeout")
    result = _error(e, "part.list")
    data = json.loads(result)
    assert "reachable" in data["hint"].lower()


@pytest.mark.unit
def test_error_missing_env():
    """Test _error provides hint for missing environment variables."""
    e = Exception("INVENTREE_URL not set")
    result = _error(e, "connect")
    data = json.loads(result)
    assert "environment" in data["hint"].lower()


@pytest.mark.unit
def test_error_generic():
    """Test _error provides generic hint for unknown errors."""
    e = Exception("Some unknown error")
    result = _error(e, "unknown")
    data = json.loads(result)
    assert "error" in data
    assert "hint" in data


@pytest.mark.unit
def test_error_with_context():
    """Test _error includes context in error message."""
    e = Exception("Test error")
    result = _error(e, "part.get")
    data = json.loads(result)
    assert "part.get" in data["error"]


@pytest.mark.unit
def test_error_without_context():
    """Test _error works without context."""
    e = Exception("Test error")
    result = _error(e)
    data = json.loads(result)
    assert "error" in data


@pytest.mark.unit
def test_safe_decorator_returns_function():
    """Test _safe decorator returns a function."""

    @_safe("test")
    async def test_func():
        return "result"

    assert callable(test_func)


@pytest.mark.unit
def test_safe_decorator_preserves_function_name():
    """Test _safe decorator preserves function name."""

    @_safe("test")
    async def my_function():
        return "result"

    assert my_function.__name__ == "my_function"


@pytest.mark.unit
def test_safe_decorator_catches_exceptions():
    """Test _safe decorator catches exceptions and returns error."""

    @_safe("test")
    async def failing_func():
        raise ValueError("test error")

    import asyncio

    result = asyncio.get_event_loop().run_until_complete(failing_func())
    data = json.loads(result)
    assert "error" in data
    assert "hint" in data
