# InvenTree MCP Server

MCP server for [InvenTree](https://inventree.org) inventory management. Provides 12 parameterized tools covering 117 operations for parts, stock, build orders, purchase/sales/return orders, companies, barcodes, labels, reports, attachments, and system administration.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- An InvenTree instance with API access enabled
- An API token (generate from InvenTree > Settings > API Tokens)

## Setup

```bash
# Clone the repository
git clone https://github.com/puran-water/inventree-mcp.git
cd inventree-mcp

# Copy the example environment file and fill in your values
cp .env.example .env

# Install dependencies
uv sync
```

Edit `.env` with your InvenTree instance URL and API token:

```
INVENTREE_URL=https://your-inventree-instance.example.com
INVENTREE_TOKEN=your-api-token-here
```

## Usage

### STDIO mode (default)

```bash
# Using entry point (recommended)
uv run inventree-mcp

# Or using module
uv run python -m inventree_mcp
```

### SSE mode (HTTP transport)

```bash
uv run python -m inventree_mcp sse --port 3074
```

### Claude Desktop / MCP client configuration

Add to your MCP client config (e.g. `~/.claude/mcp.json`):

```json
{
  "mcpServers": {
    "inventree-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/inventree-mcp", "inventree-mcp"],
      "env": {
        "INVENTREE_URL": "https://your-inventree-instance.example.com",
        "INVENTREE_TOKEN": "your-api-token-here"
      }
    }
  }
}
```

Or for SSE transport:

```json
{
  "mcpServers": {
    "inventree-mcp": {
      "url": "http://localhost:3074/sse"
    }
  }
}
```

## Tools

Each tool uses a parameterized `operation` field to select the specific action.

| Tool | Operations | Description |
|------|-----------|-------------|
| `part` | 21 | Part & category management (list, get, create, update, delete, BOM, suppliers, parameters) |
| `stock` | 16 | Stock item & location management (list, get, create, transfer, count, add, remove) |
| `build_order` | 9 | Manufacturing build orders (list, get, create, update, allocate, complete, cancel) |
| `purchase_order` | 12 | Purchase order lifecycle (list, get, create, update, issue, receive, complete) |
| `sales_order` | 14 | Sales order lifecycle (list, get, create, shipments, allocations) |
| `return_order` | 8 | Return order management |
| `company` | 12 | Suppliers, manufacturers, customers, contacts, addresses |
| `barcode` | 4 | Barcode scan, assign, unassign, lookup |
| `label` | 5 | Label template listing and printing |
| `report` | 3 | Report template listing and generation |
| `attachment` | 5 | File attachments on any object (upload, download, delete) |
| `system` | 8 | Health, version, settings, users, groups, currencies |

## Architecture

The server follows a modular structure for better maintainability:

```
inventree/
├── src/inventree_mcp/
│   ├── server.py          # FastMCP server with tool registration
│   ├── client.py          # Async adapter wrapping inventree-python
│   ├── utils.py           # Helper functions (_json, _error, _safe)
│   └── api/               # Modular API operation modules
│       ├── part.py        # Part operations (21 operations)
│       ├── stock.py       # Stock operations (16 operations)
│       ├── build.py       # Build order operations (9 operations)
│       ├── purchase.py    # Purchase order operations (12 operations)
│       ├── sales.py       # Sales order operations (14 operations)
│       ├── returns.py     # Return order operations (8 operations)
│       ├── company.py     # Company operations (12 operations)
│       ├── barcode.py     # Barcode operations (4 operations)
│       ├── label.py       # Label operations (5 operations)
│       ├── report.py      # Report operations (3 operations)
│       ├── attachment.py  # Attachment operations (5 operations)
│       └── system.py      # System operations (8 operations)
├── pyproject.toml         # Package configuration with entry point
└── README.md
```

The `inventree-python` library is synchronous (requests-based). All calls are offloaded to threads via `asyncio.to_thread()` to maintain async compatibility with the MCP framework.

## Testing

This project uses a three-tier testing strategy:

- **Unit tests** - Fast validation tests (no external dependencies)
- **MCP client tests** - Protocol-level tests with mocked APIs
- **Integration tests** - Full stack tests with real InvenTree API

See [TEST_STRATEGY.md](./TEST_STRATEGY.md) for detailed implementation plan and testing guidelines.

### Quick Start

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run fast unit tests
pytest -m "unit" -v

# Run MCP protocol tests (mocked API)
pytest -m "mcp_client" -v

# Run all tests except integration
pytest -m "not integration" -v

# Run integration tests (requires InvenTree instance)
pytest -m "integration" -v
```

## License

MIT
