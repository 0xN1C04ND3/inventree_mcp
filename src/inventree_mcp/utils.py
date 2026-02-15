"""Utility functions for InvenTree MCP server."""

import json
import logging
from typing import Any
from functools import wraps

logger = logging.getLogger(__name__)


def _json(data: Any) -> str:
    """Serialize response data to JSON string."""
    return json.dumps(data, indent=2, default=str)


def _error(e: Exception, context: str = "") -> str:
    """Format an actionable error message for the agent."""
    msg = str(e)
    if "404" in msg or "not found" in msg.lower():
        hint = "Check that the ID exists. Use the list/search operation first to find valid IDs."
    elif "403" in msg or "permission" in msg.lower() or "forbidden" in msg.lower():
        hint = "The API token lacks permission for this operation. Check INVENTREE_TOKEN roles."
    elif "400" in msg or "bad request" in msg.lower():
        hint = "Invalid request data. Check required fields in the 'data' parameter."
    elif "timeout" in msg.lower() or "connect" in msg.lower():
        hint = "Connection failed. Verify INVENTREE_URL is reachable."
    elif "INVENTREE_URL" in msg or "INVENTREE_TOKEN" in msg:
        hint = "Set INVENTREE_URL and INVENTREE_TOKEN environment variables."
    else:
        hint = "Check the operation name and parameters."
    prefix = f"[{context}] " if context else ""
    logger.error(f"{prefix}{msg}")
    return _json({"error": f"{prefix}{msg}", "hint": hint})


def _safe(tool_name: str):
    """Decorator to add error handling to tool functions."""

    def decorator(fn):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            try:
                return await fn(*args, **kwargs)
            except Exception as e:
                op = kwargs.get("operation", args[0] if args else "unknown")
                return _error(e, f"{tool_name}.{op}")

        return wrapper

    return decorator
