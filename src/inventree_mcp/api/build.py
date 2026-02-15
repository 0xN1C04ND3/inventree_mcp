"""Manufacturing build order management operations for InvenTree."""

from ..utils import _json


async def build_order_operations(
    client,
    operation: str,
    pk: int = None,
    data: dict = None,
    items: list = None,
    search: str = None,
    limit: int = 25,
    offset: int = 0,
) -> str:
    """Execute build order operations.

    Args:
        client: InvenTree client instance
        operation: Operation name
        pk: Build order ID
        data: Data for create/update/complete operations
        items: List of allocation dicts for allocate
        search: Search text filter
        limit: Max results for list operations
        offset: Pagination offset

    Returns:
        JSON string with result or error
    """
    if operation == "list":
        filters = {"limit": limit, "offset": offset}
        if search:
            filters["search"] = search
        return _json(await client.build_list(**filters))

    elif operation == "get":
        return _json(await client.build_get(pk))

    elif operation == "create":
        return _json(await client.build_create(data or {}))

    elif operation == "update":
        return _json(await client.build_update(pk, data or {}))

    elif operation == "allocate":
        return _json(await client.build_allocate(pk, items or []))

    elif operation == "complete":
        return _json(await client.build_complete(pk, **(data or {})))

    elif operation == "cancel":
        return _json(await client.build_cancel(pk))

    elif operation == "get_outputs":
        return _json(await client.build_get_outputs(pk))

    elif operation == "get_lines":
        return _json(await client.build_get_lines(pk))

    else:
        return _json({"error": f"Unknown operation: {operation}"})


# Alias for consistency with import
build_operations = build_order_operations
