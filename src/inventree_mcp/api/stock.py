"""Stock item & location management operations for InvenTree."""

from ..utils import _json


async def stock_operations(
    client,
    operation: str,
    pk: int = None,
    data: dict = None,
    part_id: int = None,
    location_id: int = None,
    quantity: float = None,
    test_name: str = None,
    test_result: bool = None,
    search: str = None,
    limit: int = 25,
    offset: int = 0,
) -> str:
    """Execute stock and location operations.

    Args:
        client: InvenTree client instance
        operation: Operation name
        pk: Stock item or location ID
        data: Data for create/update operations
        part_id: Filter stock by part
        location_id: Filter stock by location or transfer destination
        quantity: Quantity for transfer/count/add/remove operations
        test_name: Name for upload_test_result
        test_result: Boolean pass/fail for upload_test_result
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
        if part_id is not None:
            filters["part"] = part_id
        if location_id is not None:
            filters["location"] = location_id
        return _json(await client.stock_list(**filters))

    elif operation == "get":
        return _json(await client.stock_get(pk))

    elif operation == "create":
        return _json(await client.stock_create(data or {}))

    elif operation == "update":
        return _json(await client.stock_update(pk, data or {}))

    elif operation == "transfer":
        return _json(await client.stock_transfer(pk, location_id, quantity))

    elif operation == "count":
        return _json(await client.stock_count(pk, quantity))

    elif operation == "add":
        return _json(await client.stock_add(pk, quantity))

    elif operation == "remove":
        return _json(await client.stock_remove(pk, quantity))

    elif operation == "get_by_location":
        return _json(await client.stock_get_by_location(location_id))

    elif operation == "get_by_part":
        return _json(await client.stock_get_by_part(part_id))

    elif operation == "list_locations":
        filters = {}
        if search:
            filters["search"] = search
        return _json(await client.stock_list_locations(**filters))

    elif operation == "get_location":
        return _json(await client.stock_get_location(pk))

    elif operation == "create_location":
        return _json(await client.stock_create_location(data or {}))

    elif operation == "get_tracking":
        return _json(await client.stock_get_tracking(pk))

    elif operation == "upload_test_result":
        extra = {}
        if "notes" in (data or {}):
            extra["notes"] = data["notes"]
        if "value" in (data or {}):
            extra["value"] = data["value"]
        return _json(
            await client.stock_upload_test_result(pk, test_name, test_result, **extra)
        )

    elif operation == "get_test_results":
        return _json(await client.stock_get_test_results(pk))

    else:
        return _json({"error": f"Unknown operation: {operation}"})
