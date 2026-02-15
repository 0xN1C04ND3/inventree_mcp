"""Report generation and template management operations for InvenTree."""

from ..utils import _json


async def report_operations(
    client,
    operation: str,
    template_id: int = None,
    item_ids: list = None,
    model_type: str = None,
    destination: str = None,
) -> str:
    """Execute report operations.

    Args:
        client: InvenTree client instance
        operation: Operation name
        template_id: Report template ID for print_report/download_template
        item_ids: List of item IDs to include in report
        model_type: Model type for print_report
        destination: File path to save downloaded template to

    Returns:
        JSON string with result or error
    """
    if operation == "list_templates":
        return _json(await client.report_list_templates())

    elif operation == "print_report":
        return _json(await client.report_print(template_id, item_ids or [], model_type))

    elif operation == "download_template":
        return _json(await client.report_download_template(template_id, destination))

    else:
        return _json({"error": f"Unknown operation: {operation}"})
