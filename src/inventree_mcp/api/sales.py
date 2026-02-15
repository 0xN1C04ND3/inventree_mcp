"""Sales order lifecycle management operations for InvenTree."""

from ..utils import _json


async def sales_order_operations(
    client,
    operation: str,
    pk: int = None,
    data: dict = None,
    shipment_id: int = None,
    reference: str = None,
    search: str = None,
    limit: int = 25,
    offset: int = 0,
) -> str:
    """Execute sales order operations.

    Args:
        client: InvenTree client instance
        operation: Operation name
        pk: Sales order ID
        data: Data for create/update/add_line_item operations
        shipment_id: Shipment ID for complete_shipment
        reference: Reference string for create_shipment
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
        return _json(await client.so_list(**filters))

    elif operation == "get":
        return _json(await client.so_get(pk))

    elif operation == "create":
        return _json(await client.so_create(data or {}))

    elif operation == "update":
        return _json(await client.so_update(pk, data or {}))

    elif operation == "complete":
        return _json(await client.so_complete(pk))

    elif operation == "cancel":
        return _json(await client.so_cancel(pk))

    elif operation == "hold":
        return _json(await client.so_hold(pk))

    elif operation == "add_line_item":
        return _json(await client.so_add_line_item(pk, data or {}))

    elif operation == "add_extra_line_item":
        return _json(await client.so_add_extra_line_item(pk, data or {}))

    elif operation == "get_line_items":
        return _json(await client.so_get_line_items(pk))

    elif operation == "create_shipment":
        return _json(await client.so_create_shipment(pk, reference, **(data or {})))

    elif operation == "complete_shipment":
        return _json(await client.so_complete_shipment(shipment_id, **(data or {})))

    elif operation == "get_allocations":
        return _json(await client.so_get_allocations(pk))

    else:
        return _json({"error": f"Unknown operation: {operation}"})
