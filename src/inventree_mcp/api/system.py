"""InvenTree system administration and health check operations."""

from ..utils import _json


async def system_operations(
    client,
    operation: str,
    pk: int = None,
) -> str:
    """Execute system operations.

    Args:
        client: InvenTree client instance
        operation: Operation name
        pk: User ID for get_user

    Returns:
        JSON string with result or error
    """
    if operation == "health":
        return _json(await client.system_health())

    elif operation == "version":
        return _json(await client.system_version())

    elif operation == "settings":
        return _json(await client.system_settings())

    elif operation == "list_users":
        return _json(await client.system_list_users())

    elif operation == "get_user":
        return _json(await client.system_get_user(pk))

    elif operation == "list_groups":
        return _json(await client.system_list_groups())

    elif operation == "list_owners":
        return _json(await client.system_list_owners())

    elif operation == "get_project_codes":
        return _json(await client.system_get_project_codes())

    elif operation == "list_currencies":
        return _json(await client.system_list_currencies())

    else:
        return _json({"error": f"Unknown operation: {operation}"})
