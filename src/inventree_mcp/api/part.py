"""Part & category management operations for InvenTree."""

from ..utils import _json


async def part_operations(
    client,
    operation: str,
    pk: int = None,
    data: dict = None,
    search: str = None,
    category: int = None,
    limit: int = 25,
    offset: int = 0,
) -> str:
    """Execute part and category operations.

    Args:
        client: InvenTree client instance
        operation: Operation name
        pk: Part or category ID
        data: Data for create/update operations
        search: Search text filter
        category: Category ID filter
        limit: Max results for list operations
        offset: Pagination offset

    Returns:
        JSON string with result or error
    """
    if operation == "list":
        filters = {}
        if search:
            filters["search"] = search
        if category is not None:
            filters["category"] = category
        filters["limit"] = limit
        filters["offset"] = offset
        return _json(await client.part_list(**filters))

    elif operation == "get":
        return _json(await client.part_get(pk))

    elif operation == "create":
        return _json(await client.part_create(data or {}))

    elif operation == "update":
        return _json(await client.part_update(pk, data or {}))

    elif operation == "delete":
        return _json(await client.part_delete(pk))

    elif operation == "get_stock":
        return _json(await client.part_get_stock(pk))

    elif operation == "get_bom":
        return _json(await client.part_get_bom(pk))

    elif operation == "get_bom_usage":
        return _json(await client.part_get_bom_usage(pk))

    elif operation == "get_suppliers":
        return _json(await client.part_get_suppliers(pk))

    elif operation == "get_manufacturers":
        return _json(await client.part_get_manufacturers(pk))

    elif operation == "get_parameters":
        return _json(await client.part_get_parameters(pk))

    elif operation == "get_parameter_templates":
        return _json(await client.part_get_parameter_templates())

    elif operation == "get_test_templates":
        return _json(await client.part_get_test_templates(pk))

    elif operation == "get_related":
        return _json(await client.part_get_related(pk))

    elif operation == "get_builds":
        return _json(await client.part_get_builds(pk))

    elif operation == "get_internal_prices":
        return _json(await client.part_get_internal_prices(pk))

    elif operation == "get_sale_prices":
        return _json(await client.part_get_sale_prices(pk))

    elif operation == "list_categories":
        filters = {}
        if search:
            filters["search"] = search
        return _json(await client.part_list_categories(**filters))

    elif operation == "get_category":
        return _json(await client.part_get_category(pk))

    elif operation == "create_category":
        return _json(await client.part_create_category(data or {}))

    elif operation == "get_category_parameters":
        return _json(await client.part_get_category_parameters(pk))

    else:
        return _json({"error": f"Unknown operation: {operation}"})
