#!/usr/bin/env python3
"""InvenTree MCP Server — 12 parameterized tools, 117 operations.

Dual transport: STDIO (default) or SSE (pass 'sse' argument).
Uses inventree-python library wrapped in asyncio.to_thread() for async safety.
"""

import asyncio
import logging
import os
import sys

from dotenv import load_dotenv
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

from .client import InvenTreeClient
from .utils import _safe
from .api import (
    part_operations,
    stock_operations,
    build_operations,
    purchase_operations,
    sales_operations,
    returns_operations,
    company_operations,
    barcode_operations,
    label_operations,
    report_operations,
    attachment_operations,
    system_operations,
)

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

mcp = FastMCP(
    "inventree_mcp",
    host=os.getenv("HOST", "0.0.0.0"),
    port=int(os.getenv("PORT", "3000")),
)

# ── Lazy client singleton ────────────────────────────────────────────

_client = None
_client_lock = asyncio.Lock()


async def get_client():
    """Get or create the InvenTree client singleton."""
    global _client
    if _client is not None:
        return _client
    async with _client_lock:
        if _client is not None:
            return _client

        url = os.getenv("INVENTREE_URL")
        token = os.getenv("INVENTREE_TOKEN")
        if not url or not token:
            raise RuntimeError(
                "INVENTREE_URL and INVENTREE_TOKEN must be set in environment"
            )
        _client = InvenTreeClient(url, token)
        await _client.connect()
        logger.info(f"InvenTree client connected to {url}")
    return _client


@mcp.custom_route("/health", methods=["GET"])
async def health(request: Request):
    return JSONResponse({"status": "ok", "service": "inventree-mcp"})


# ═══════════════════════════════════════════════════════════════════════
# Tool Definitions — 12 parameterized tools
# ═══════════════════════════════════════════════════════════════════════


@mcp.tool(
    annotations={
        "title": "InvenTree Part & Category Management",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": True,
    }
)
@_safe("part")
async def part(
    operation: str,
    pk: int = None,
    data: dict = None,
    search: str = None,
    category: int = None,
    limit: int = 25,
    offset: int = 0,
) -> str:
    """Part & category management in InvenTree.

    Operations:
      Read: list, get, get_stock, get_bom, get_bom_usage, get_suppliers,
        get_manufacturers, get_parameters, get_parameter_templates,
        get_test_templates, get_related, get_builds, get_internal_prices,
        get_sale_prices, list_categories, get_category, get_category_parameters
      Write: create, update, create_category
      Delete: delete

    Args:
        operation: One of the operations listed above.
        pk: Part or category ID (required for get/update/delete and sub-queries).
        data: Dict of fields for create/update (e.g. {"name": "Seal Kit", "category": 5}).
        search: Text search filter for list/list_categories.
        category: Category ID filter for list.
        limit: Max results for list (default 25).
        offset: Pagination offset for list.

    Returns:
        JSON string with part/category data or {"error": "..."}.
    """
    c = await get_client()
    return await part_operations(
        c, operation, pk, data, search, category, limit, offset
    )


@mcp.tool(
    annotations={
        "title": "InvenTree Stock & Location Management",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    }
)
@_safe("stock")
async def stock(
    operation: str,
    pk: int = None,
    data: dict = None,
    part_id: int = None,
    location_id: int = None,
    quantity: float = None,
    notes: str = None,
    include_variants: bool = None,
    search: str = None,
    limit: int = 25,
    offset: int = 0,
) -> str:
    """Stock item & location management in InvenTree.

    Operations:
      Read: list, get, get_by_location, get_by_part, list_locations, get_location,
        get_tracking, get_test_results
      Write: create, update, transfer, count, add, remove, create_location, upload_test_result
      Delete: delete (not implemented yet)

    Args:
        operation: One of the operations listed above.
        pk: Stock item or location ID.
        data: Dict of fields for create/update.
        part_id: Filter by part ID.
        location_id: Location ID for filters or transfer target.
        quantity: Quantity for add/remove/transfer.
        notes: Notes for add/remove/transfer/count.
        include_variants: Include part variants in get_by_part (default False).
        search: Text search filter for list.
        limit: Max results for list (default 25).
        offset: Pagination offset for list.

    Returns:
        JSON string with stock/location data or {"error": "..."}.
    """
    c = await get_client()
    return await stock_operations(
        c,
        operation,
        pk,
        data,
        part_id,
        location_id,
        quantity,
        notes,
        include_variants,
        search,
        limit,
        offset,
    )


@mcp.tool(
    annotations={
        "title": "InvenTree Build Order Management",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    }
)
@_safe("build_order")
async def build_order(
    operation: str,
    pk: int = None,
    data: dict = None,
    allocation: list = None,
    search: str = None,
    limit: int = 25,
    offset: int = 0,
) -> str:
    """Build order management for manufacturing in InvenTree.

    Operations:
      Read: list, get, get_outputs, get_lines
      Write: create, update, allocate, complete, cancel

    Args:
        operation: One of the operations listed above.
        pk: Build order ID.
        data: Dict of fields for create/update (e.g. {"part": 10, "quantity": 100}).
        allocation: List of stock allocations for allocate (e.g. [{"bom_item": 5, "stock_item": 100, "quantity": 10}]).
        search: Text search filter for list.
        limit: Max results for list (default 25).
        offset: Pagination offset for list.

    Returns:
        JSON string with build order data or {"error": "..."}.
    """
    c = await get_client()
    return await build_operations(
        c, operation, pk, data, allocation, search, limit, offset
    )


@mcp.tool(
    annotations={
        "title": "InvenTree Purchase Order Management",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    }
)
@_safe("purchase_order")
async def purchase_order(
    operation: str,
    pk: int = None,
    data: dict = None,
    line_item_data: dict = None,
    search: str = None,
    limit: int = 25,
    offset: int = 0,
) -> str:
    """Purchase order management in InvenTree.

    Operations:
      Read: list, get, get_line_items
      Write: create, update, issue, receive, complete, cancel, hold, add_line_item, add_extra_line_item

    Args:
        operation: One of the operations listed above.
        pk: Purchase order ID.
        data: Dict of fields for create/update (e.g. {"supplier": 5, "description": "PCBs"}).
        line_item_data: Dict for add_line_item/add_extra_line_item operations.
        search: Text search filter for list.
        limit: Max results for list (default 25).
        offset: Pagination offset for list.

    Returns:
        JSON string with purchase order data or {"error": "..."}.
    """
    c = await get_client()
    return await purchase_operations(
        c, operation, pk, data, line_item_data, search, limit, offset
    )


@mcp.tool(
    annotations={
        "title": "InvenTree Sales Order Management",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    }
)
@_safe("sales_order")
async def sales_order(
    operation: str,
    pk: int = None,
    data: dict = None,
    line_item_data: dict = None,
    shipment_data: dict = None,
    search: str = None,
    limit: int = 25,
    offset: int = 0,
) -> str:
    """Sales order management in InvenTree.

    Operations:
      Read: list, get, get_line_items, get_allocations
      Write: create, update, complete, cancel, hold, add_line_item, add_extra_line_item,
        create_shipment, complete_shipment

    Args:
        operation: One of the operations listed above.
        pk: Sales order ID.
        data: Dict of fields for create/update (e.g. {"customer": 10, "description": "Order 123"}).
        line_item_data: Dict for add_line_item/add_extra_line_item operations.
        shipment_data: Dict for create_shipment operation.
        search: Text search filter for list.
        limit: Max results for list (default 25).
        offset: Pagination offset for list.

    Returns:
        JSON string with sales order data or {"error": "..."}.
    """
    c = await get_client()
    return await sales_operations(
        c, operation, pk, data, line_item_data, shipment_data, search, limit, offset
    )


@mcp.tool(
    annotations={
        "title": "InvenTree Return Order Management",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    }
)
@_safe("return_order")
async def return_order(
    operation: str,
    pk: int = None,
    data: dict = None,
    line_item_data: dict = None,
    search: str = None,
    limit: int = 25,
    offset: int = 0,
) -> str:
    """Return order management in InvenTree.

    Operations:
      Read: list, get, get_line_items
      Write: create, update, complete, cancel, add_line_item

    Args:
        operation: One of the operations listed above.
        pk: Return order ID.
        data: Dict of fields for create/update (e.g. {"customer": 10, "description": "RMA 456"}).
        line_item_data: Dict for add_line_item operation.
        search: Text search filter for list.
        limit: Max results for list (default 25).
        offset: Pagination offset for list.

    Returns:
        JSON string with return order data or {"error": "..."}.
    """
    c = await get_client()
    return await returns_operations(
        c, operation, pk, data, line_item_data, search, limit, offset
    )


@mcp.tool(
    annotations={
        "title": "InvenTree Company Management",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": True,
    }
)
@_safe("company")
async def company(
    operation: str,
    pk: int = None,
    data: dict = None,
    company_id: int = None,
    search: str = None,
    limit: int = 25,
    offset: int = 0,
) -> str:
    """Company (suppliers, manufacturers, customers) management in InvenTree.

    Operations:
      Read: list, get, list_supplier_parts, get_supplier_part, list_manufacturer_parts,
        get_manufacturer_part, list_contacts, list_addresses, get_price_breaks
      Write: create, update
      Delete: delete

    Args:
        operation: One of the operations listed above.
        pk: Company, supplier part, or manufacturer part ID.
        data: Dict of fields for create/update (e.g. {"name": "ACME Inc", "is_supplier": True}).
        company_id: Company ID for list_supplier_parts, list_manufacturer_parts, etc.
        search: Text search filter for list.
        limit: Max results for list (default 25).
        offset: Pagination offset for list.

    Returns:
        JSON string with company data or {"error": "..."}.
    """
    c = await get_client()
    return await company_operations(
        c, operation, pk, data, company_id, search, limit, offset
    )


@mcp.tool(
    annotations={
        "title": "InvenTree Barcode Operations",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
@_safe("barcode")
async def barcode(
    operation: str,
    barcode_data: str = None,
    item_id: int = None,
    item_type: str = None,
) -> str:
    """Barcode scanning and assignment in InvenTree.

    Operations:
      Read: scan, lookup
      Write: assign, unassign

    Args:
        operation: One of the operations listed above.
        barcode_data: The barcode string to scan/assign.
        item_id: ID of the item to assign/unassign barcode.
        item_type: Type of item (e.g. "stockitem", "part", "location").

    Returns:
        JSON string with barcode data or {"error": "..."}.
    """
    c = await get_client()
    return await barcode_operations(c, operation, barcode_data, item_id, item_type)


@mcp.tool(
    annotations={
        "title": "InvenTree Label Operations",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
@_safe("label")
async def label(
    operation: str,
    template_id: int = None,
    item_ids: list = None,
) -> str:
    """Label printing and template management in InvenTree.

    Operations:
      Read: list_templates, download_template
      Write: print_part, print_stock, print_location

    Args:
        operation: One of the operations listed above.
        template_id: Label template ID for download.
        item_ids: List of item IDs to print labels for.

    Returns:
        JSON string with label data or {"error": "..."}.
    """
    c = await get_client()
    return await label_operations(c, operation, template_id, item_ids)


@mcp.tool(
    annotations={
        "title": "InvenTree Report Operations",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
@_safe("report")
async def report(
    operation: str,
    template_id: int = None,
    item_id: int = None,
) -> str:
    """Report generation and template management in InvenTree.

    Operations:
      Read: list_templates, print_report, download_template

    Args:
        operation: One of the operations listed above.
        template_id: Report template ID.
        item_id: ID of the item to generate report for.

    Returns:
        JSON string with report data or {"error": "..."}.
    """
    c = await get_client()
    return await report_operations(c, operation, template_id, item_id)


@mcp.tool(
    annotations={
        "title": "InvenTree Attachment Management",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": True,
    }
)
@_safe("attachment")
async def attachment(
    operation: str,
    pk: int = None,
    model_type: str = None,
    model_id: int = None,
    file_path: str = None,
    link_url: str = None,
    comment: str = None,
) -> str:
    """File attachment management in InvenTree.

    Operations:
      Read: list, download
      Write: upload, upload_link
      Delete: delete

    Args:
        operation: One of the operations listed above.
        pk: Attachment ID for download/delete.
        model_type: Model type (e.g. "part", "stockitem", "purchaseorder").
        model_id: ID of the model to attach file to.
        file_path: Local file path for upload.
        link_url: URL for upload_link.
        comment: Optional comment for the attachment.

    Returns:
        JSON string with attachment data or {"error": "..."}.
    """
    c = await get_client()
    return await attachment_operations(
        c, operation, pk, model_type, model_id, file_path, link_url, comment
    )


@mcp.tool(
    annotations={
        "title": "InvenTree System Operations",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
@_safe("system")
async def system(
    operation: str,
    pk: int = None,
    setting_key: str = None,
) -> str:
    """System administration and health checks in InvenTree.

    Operations:
      Read: health, version, settings, list_users, get_user, list_groups, list_owners,
        get_project_codes, list_currencies

    Args:
        operation: One of the operations listed above.
        pk: User/group ID for get operations.
        setting_key: Setting key for settings operation.

    Returns:
        JSON string with system data or {"error": "..."}.
    """
    c = await get_client()
    return await system_operations(c, operation, pk, setting_key)


# ═══════════════════════════════════════════════════════════════════════
# Main entry point
# ═══════════════════════════════════════════════════════════════════════


def main():
    """Main entry point for the InvenTree MCP server."""
    # Check if SSE mode is requested
    if len(sys.argv) > 1 and sys.argv[1] == "sse":
        logger.info("Starting InvenTree MCP server in SSE mode")
        mcp.run(transport="sse")
    else:
        logger.info("Starting InvenTree MCP server in STDIO mode")
        mcp.run()


if __name__ == "__main__":
    main()
