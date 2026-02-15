"""Return order lifecycle management operations for InvenTree."""

from ..utils import _json


async def return_order_operations(
    client,
    operation: str,
    pk: int = None,
    data: dict = None,
    search: str = None,
    limit: int = 25,
    offset: int = 0,
) -> str:
    """Execute return order operations.

    Args:
        client: InvenTree client instance
        operation: Operation name
        pk: Return order ID
        data: Data for create/update/add_line_item operations
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
        return _json(await client.ro_list(**filters))

    elif operation == "get":
        return _json(await client.ro_get(pk))

    elif operation == "create":
        return _json(await client.ro_create(data or {}))

    elif operation == "update":
        return _json(await client.ro_update(pk, data or {}))

    elif operation == "complete":
        return _json(await client.ro_complete(pk))

    elif operation == "cancel":
        return _json(await client.ro_cancel(pk))

    elif operation == "add_line_item":
        return _json(await client.ro_add_line_item(pk, data or {}))

    elif operation == "get_line_items":
        return _json(await client.ro_get_line_items(pk))

    else:
        return _json({"error": f"Unknown operation: {operation}"})
