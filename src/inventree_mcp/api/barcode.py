"""Barcode scanning and assignment operations for InvenTree."""

from ..utils import _json


async def barcode_operations(
    client,
    operation: str,
    barcode_data: str = None,
    model_type: str = None,
    pk: int = None,
) -> str:
    """Execute barcode operations.

    Args:
        client: InvenTree client instance
        operation: Operation name
        barcode_data: Barcode string for scan/assign/lookup
        model_type: Model type for assign/unassign
        pk: Object ID for assign/unassign

    Returns:
        JSON string with result or error
    """
    if operation == "scan":
        return _json(await client.barcode_scan(barcode_data))

    elif operation == "assign":
        return _json(await client.barcode_assign(model_type, pk, barcode_data))

    elif operation == "unassign":
        return _json(await client.barcode_unassign(model_type, pk))

    elif operation == "lookup":
        return _json(await client.barcode_lookup(barcode_data))

    else:
        return _json({"error": f"Unknown operation: {operation}"})
