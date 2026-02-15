"""Supplier, manufacturer, and customer management operations for InvenTree."""

from ..utils import _json


async def company_operations(
    client,
    operation: str,
    pk: int = None,
    data: dict = None,
    company_id: int = None,
    supplier_part_id: int = None,
    search: str = None,
    is_supplier: bool = None,
    is_manufacturer: bool = None,
    is_customer: bool = None,
    limit: int = 25,
    offset: int = 0,
) -> str:
    """Execute company operations.

    Args:
        client: InvenTree client instance
        operation: Operation name
        pk: Company, supplier part, or manufacturer part ID
        data: Data for create/update operations
        company_id: Company ID for list operations
        supplier_part_id: Supplier part ID for get_price_breaks
        search: Search text filter
        is_supplier: Filter for suppliers
        is_manufacturer: Filter for manufacturers
        is_customer: Filter for customers
        limit: Max results for list operations
        offset: Pagination offset

    Returns:
        JSON string with result or error
    """
    if operation == "list":
        filters = {"limit": limit, "offset": offset}
        if search:
            filters["search"] = search
        if is_supplier is not None:
            filters["is_supplier"] = is_supplier
        if is_manufacturer is not None:
            filters["is_manufacturer"] = is_manufacturer
        if is_customer is not None:
            filters["is_customer"] = is_customer
        return _json(await client.company_list(**filters))

    elif operation == "get":
        return _json(await client.company_get(pk))

    elif operation == "create":
        return _json(await client.company_create(data or {}))

    elif operation == "update":
        return _json(await client.company_update(pk, data or {}))

    elif operation == "delete":
        return _json(await client.company_delete(pk))

    elif operation == "list_supplier_parts":
        filters = {}
        if company_id is not None:
            filters["supplier"] = company_id
        if search:
            filters["search"] = search
        return _json(await client.company_list_supplier_parts(**filters))

    elif operation == "get_supplier_part":
        return _json(await client.company_get_supplier_part(pk))

    elif operation == "list_manufacturer_parts":
        filters = {}
        if company_id is not None:
            filters["manufacturer"] = company_id
        if search:
            filters["search"] = search
        return _json(await client.company_list_manufacturer_parts(**filters))

    elif operation == "get_manufacturer_part":
        return _json(await client.company_get_manufacturer_part(pk))

    elif operation == "list_contacts":
        return _json(await client.company_list_contacts(company_id or pk))

    elif operation == "list_addresses":
        return _json(await client.company_list_addresses(company_id or pk))

    elif operation == "get_price_breaks":
        return _json(await client.company_get_price_breaks(supplier_part_id or pk))

    else:
        return _json({"error": f"Unknown operation: {operation}"})
