"""Label printing and template management operations for InvenTree."""

from ..utils import _json


async def label_operations(
    client,
    operation: str,
    label_type: str = "part",
    template_id: int = None,
    item_ids: list = None,
    destination: str = None,
) -> str:
    """Execute label operations.

    Args:
        client: InvenTree client instance
        operation: Operation name
        label_type: Filter for list_templates (part, stock, location)
        template_id: Label template ID for print/download operations
        item_ids: List of item IDs to print labels for
        destination: File path to save downloaded template to

    Returns:
        JSON string with result or error
    """
    if operation == "list_templates":
        return _json(await client.label_list_templates(label_type))

    elif operation in ("print_part", "print_stock", "print_location"):
        lt = operation.replace("print_", "")
        return _json(await client.label_print(lt, template_id, item_ids or []))

    elif operation == "download_template":
        return _json(await client.label_download_template(template_id, destination))

    else:
        return _json({"error": f"Unknown operation: {operation}"})
