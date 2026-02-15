"""API operation modules for InvenTree MCP server."""

from .part import part_operations
from .stock import stock_operations
from .build import build_operations
from .purchase import purchase_operations
from .sales import sales_operations
from .returns import returns_operations
from .company import company_operations
from .barcode import barcode_operations
from .label import label_operations
from .report import report_operations
from .attachment import attachment_operations
from .system import system_operations

__all__ = [
    "part_operations",
    "stock_operations",
    "build_operations",
    "purchase_operations",
    "sales_operations",
    "returns_operations",
    "company_operations",
    "barcode_operations",
    "label_operations",
    "report_operations",
    "attachment_operations",
    "system_operations",
]
