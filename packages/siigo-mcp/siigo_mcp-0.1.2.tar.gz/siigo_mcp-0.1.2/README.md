# Siigo MCP Server

__Unofficial__ MCP server for [Siigo](https://www.siigo.com/) invoicing software (Colombian electronic invoicing) created by [@dsfaccini](https://github.com/dsfaccini).

Disclaimers: This is an independent project and is not affiliated with Siigo. The project is at early stages so extensive testing is recommended before production use. The MCP server doesn't include any custom logic beyond calling the documented Siigo API endpoints.

> **Security Warning**: This MCP server gives AI direct access to Siigo API endpoints. By default, only read-only tools are enabled. See [Safety Modes](#safety-modes-siigo_mode) before enabling write operations.

## Quick Start

```json
{
  "mcpServers": {
    "siigo": {
      "command": "uvx",
      "args": ["siigo-mcp"],
      "env": {
        "SIIGO_USERNAME": "your-email@example.com",
        "SIIGO_ACCESS_KEY": "your-access-key",
        "SIIGO_PARTNER_ID": "your-partner-id"
      }
    }
  }
}
```

Or run directly:

```bash
uvx siigo-mcp
```

## Installation

### Option 1: uvx (recommended, no install)

```bash
uvx siigo-mcp
```

### Option 2: pip/uv install

```bash
uv tool install siigo-mcp
# or
pip install siigo-mcp
```

### Option 3: From source

```bash
git clone https://github.com/dsfaccini/siigo-mcp.git
cd siigo-mcp
uv sync
uv run siigo-mcp
```

### Prerequisites

- [uv](https://docs.astral.sh/uv/) package manager

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SIIGO_USERNAME` | Yes | Siigo account email |
| `SIIGO_ACCESS_KEY` | Yes | Siigo API access key |
| `SIIGO_PARTNER_ID` | Yes | Siigo partner ID |
| `SIIGO_MODE` | No | Tool mode: `read_only` (default), `standard`, `full` |
| `SIIGO_LAZY_TOOLS` | No | Set to `true` for token-optimized lazy loading |
| `DRY_RUN` | No | Set to `true` to mock write operations |
| `LOGFIRE_TOKEN` | No | Pydantic Logfire token for observability |

### Safety Modes (SIIGO_MODE)

| Mode | Tools Available | Use Case |
|------|-----------------|----------|
| `read_only` | 19 tools: `list_*`, `get_*` only | Safe exploration, testing |
| `standard` | 30 tools: Read + create/update/delete | Normal usage (no DIAN) |
| `full` | 33 tools: All including DIAN operations | Production with caution |

**Dangerous tools** (only in `full` mode):
- `stamp_invoice` - Sends invoice to DIAN (legally binding)
- `annul_invoice` - Cancels official documents
- `send_invoice_email` - Sends emails to customers

### Lazy Tools Mode (SIIGO_LAZY_TOOLS)

For smaller context models or cost optimization, enable lazy loading:

| Mode | Tokens | Description |
|------|--------|-------------|
| Default | ~5,600 | All 33 tools loaded upfront |
| Lazy (`true`) | ~300 | Only 3 discovery tools |

In lazy mode, LLM uses these meta-tools:
- `list_siigo_tools(category?)` - Discover available tools
- `get_tool_schema(tool_name)` - Get full parameter schema
- `call_siigo_tool(tool_name, params)` - Execute any tool dynamically

```json
{
  "env": {
    "SIIGO_LAZY_TOOLS": "true"
  }
}
```

## MCP Client Setup

### Claude Desktop

**Config location:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "siigo": {
      "command": "uvx",
      "args": ["siigo-mcp"],
      "env": {
        "SIIGO_USERNAME": "your-email@example.com",
        "SIIGO_ACCESS_KEY": "your-access-key",
        "SIIGO_PARTNER_ID": "your-partner-id"
      }
    }
  }
}
```

### Claude Code

Add to `~/.claude.json` or `.mcp.json` in your project:

```json
{
  "mcpServers": {
    "siigo": {
      "type": "stdio",
      "command": "uvx",
      "args": ["siigo-mcp"],
      "env": {
        "SIIGO_USERNAME": "${SIIGO_USERNAME}",
        "SIIGO_ACCESS_KEY": "${SIIGO_ACCESS_KEY}",
        "SIIGO_PARTNER_ID": "${SIIGO_PARTNER_ID}"
      }
    }
  }
}
```

### Cursor

Add to `~/.cursor/mcp.json` or `.cursor/mcp.json` in your project:

```json
{
  "mcpServers": {
    "siigo": {
      "type": "stdio",
      "command": "uvx",
      "args": ["siigo-mcp"],
      "env": {
        "SIIGO_USERNAME": "${env:SIIGO_USERNAME}",
        "SIIGO_ACCESS_KEY": "${env:SIIGO_ACCESS_KEY}",
        "SIIGO_PARTNER_ID": "${env:SIIGO_PARTNER_ID}"
      }
    }
  }
}
```

### VS Code

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "siigo": {
      "command": "uvx",
      "args": ["siigo-mcp"],
      "env": {
        "SIIGO_USERNAME": "${env:SIIGO_USERNAME}",
        "SIIGO_ACCESS_KEY": "${env:SIIGO_ACCESS_KEY}",
        "SIIGO_PARTNER_ID": "${env:SIIGO_PARTNER_ID}"
      }
    }
  }
}
```

## Available Tools

### Read-Only (Safe)

**Reference Data:**
- `get_taxes` - Tax configurations
- `get_payment_types` - Payment methods
- `get_document_types` - Document types (FV, NC, etc.)
- `get_warehouses` - Warehouse locations
- `get_users` - System users
- `get_account_groups` - Account classifications

**Customers:**
- `list_customers` - List with pagination/filters
- `get_customer` - Get by ID

**Products:**
- `list_products` - List with pagination/filters
- `get_product` - Get by ID

**Invoices:**
- `list_invoices` - List with pagination/filters
- `get_invoice` - Get by ID
- `get_invoice_pdf` - Download PDF
- `get_stamp_errors` - DIAN rejection errors

**Credit Notes:**
- `list_credit_notes` - List with pagination/filters
- `get_credit_note` - Get by ID
- `get_credit_note_pdf` - Download PDF

**Journals:**
- `list_journals` - List with pagination/filters
- `get_journal` - Get by ID

### Write Operations (standard mode)

- `create_customer`, `update_customer`, `delete_customer`
- `create_product`, `update_product`, `delete_product`
- `create_invoice`, `update_invoice`, `delete_invoice`
- `create_credit_note`
- `create_journal`

### Dangerous (full mode only)

- `stamp_invoice` - Send to DIAN for electronic stamping
- `annul_invoice` - Annul/cancel an invoice
- `send_invoice_email` - Email invoice to customer

## Development

### Running Tests

```bash
# Tests that don't require credentials
uv run pytest tests/test_unit.py -v

# Tests with real credentials (read-only)
uv run pytest tests/test_reference.py -v

# All tests with dry-run mode
DRY_RUN=true uv run pytest tests/ -v
```

### Dry-Run Mode

Set `DRY_RUN=true` to mock all write operations:

```bash
DRY_RUN=true uvx siigo-mcp
```

In dry-run mode:
- GET requests work normally (real API)
- POST/PUT/DELETE return mock responses without executing

## Security Considerations

1. **No human-in-the-loop at MCP layer** - This server executes tool calls directly. Guardrails must be implemented in your application layer.

2. **Start with read_only mode** - Default mode only exposes read operations. Explicitly set `SIIGO_MODE=full` only when you understand the risks.

3. **Credentials in config files** - MCP configs store credentials. Use environment variable references (`${SIIGO_USERNAME}`) where supported.

4. **Production use** - Consider using `standard` mode for most use cases. Only enable `full` mode when DIAN operations are explicitly needed.

## HTTP Mode (Railway Deployment)

For multi-tenant hosting, set `MCP_TRANSPORT=http`:

```bash
MCP_TRANSPORT=http PORT=8000 uvx siigo-mcp
```

In HTTP mode, credentials are passed per-request via headers:
- `X-Siigo-Username`
- `X-Siigo-Access-Key`
- `X-Siigo-Partner-Id`

## License

MIT
