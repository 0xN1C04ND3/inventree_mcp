"""Purchase order lifecycle management operations for InvenTree."""

from ..utils import _json


async def purchase_order_operations(
    client,
    operation: str,
    pk: int = None,
    data: dict = None,
    location_id: int = None,
    items: list = None,
    search: str = None,
    limit: int = 25,
    offset: int = 0,
) -> str:
    """Execute purchase order operations.

    Args:
        client: InvenTree client instance
        operation: Operation name
        pk: Purchase order ID
        data: Data for create/update/add_line_item operations
        location_id: Receiving location for receive operation
        items: Line items to receive
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
        return _json(await client.po_list(**filters))

    elif operation == "get":
        return _json(await client.po_get(pk))

    elif operation == "create":
        return _json(await client.po_create(data or {}))

    elif operation == "update":
        return _json(await client.po_update(pk, data or {}))

    elif operation == "issue":
        return _json(await client.po_issue(pk))

    elif operation == "receive":
        return _json(await client.po_receive(pk, location_id, items))

    elif operation == "complete":
        return _json(await client.po_complete(pk))

    elif operation == "cancel":
        return _json(await client.po_cancel(pk))

    elif operation == "hold":
        return _json(await client.po_hold(pk))

    elif operation == "add_line_item":
        return _json(await client.po_add_line_item(pk, data or {}))

    elif operation == "add_extra_line_item":
        return _json(await client.po_add_extra_line_item(pk, data or {}))

    elif operation == "get_line_items":
        return _json(await client.po_get_line_items(pk))

    else:
        return _json({"error": f"Unknown operation: {operation}"})


# Alias for consistency with import
purchase_operations = purchase_order_operations
