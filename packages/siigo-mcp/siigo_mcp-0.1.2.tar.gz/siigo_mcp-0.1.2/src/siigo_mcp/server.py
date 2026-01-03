"""Siigo MCP Server - Main entry point."""

import os
from importlib.metadata import version

__version__ = version("siigo-mcp")

import logfire
from fastmcp import Context, FastMCP

from siigo_mcp.client import DryRunSiigoClient, SiigoClient


if os.environ.get("LOGFIRE_TOKEN"):
    logfire.configure(send_to_logfire='if-token-present')

mcp = FastMCP(
    "Siigo MCP",
    instructions="""
    MCP server for Siigo invoicing software. Provides tools for managing:
    - Customers (create, read, update, delete)
    - Products (create, read, update, delete)
    - Invoices (create, read, update, delete, stamp to DIAN, PDF, email)
    - Credit notes (create, read, PDF)
    - Journals (accounting vouchers)
    - Reference data (taxes, payment types, document types, warehouses)
    """,
)

# Transport mode: "http" for hosted multi-tenant, "stdio" (default) for local single-tenant
_transport = os.environ.get("MCP_TRANSPORT", "stdio")

# Dry-run mode: mutations are logged but not executed
_dry_run = os.environ.get("DRY_RUN", "").lower() == "true"

# Tool mode: controls which tools are available
# - read_only (default): Only list_* and get_* tools
# - standard: Read + create/update/delete (no DIAN operations)
# - full: All tools including dangerous ones (stamp_invoice, annul_invoice, etc.)
_mode = os.environ.get("SIIGO_MODE", "read_only")

# Lazy tools mode: only load discovery tools initially (saves ~5K tokens)
# LLM can call list_siigo_tools() and get_tool_schema() to discover and load tools on demand
_lazy_tools = os.environ.get("SIIGO_LAZY_TOOLS", "").lower() == "true"

# Dangerous tools that require explicit "full" mode
DANGEROUS_TOOLS = {"stamp_invoice", "annul_invoice", "send_invoice_email"}


def _is_read_only_tool(name: str) -> bool:
    """Check if a tool is read-only (safe)."""
    return name.startswith(("list_", "get_"))


def _should_keep_tool(name: str) -> bool:
    """Check if a tool should be available based on current mode."""
    if _mode == "read_only":
        return _is_read_only_tool(name)
    if _mode == "standard":
        return name not in DANGEROUS_TOOLS
    return True  # full mode - all tools

# Lazy-initialized global client (for stdio mode)
_client: SiigoClient | None = None


def _get_client_class() -> type[SiigoClient]:
    """Get the appropriate client class based on dry-run mode."""
    return DryRunSiigoClient if _dry_run else SiigoClient


def _get_global_client() -> SiigoClient:
    """Get or create the global Siigo API client (stdio mode)."""
    global _client
    if _client is None:
        client_class = _get_client_class()
        _client = client_class(
            username=os.environ["SIIGO_USERNAME"],
            access_key=os.environ["SIIGO_ACCESS_KEY"],
            partner_id=os.environ["SIIGO_PARTNER_ID"],
        )
    return _client


def get_client(ctx: Context) -> SiigoClient:
    """Get Siigo client - from headers (HTTP mode) or env vars (stdio mode)."""
    if _transport == "http":
        if not ctx.request_context:
            raise ValueError("No request context available in HTTP mode")
        headers = ctx.request_context.request.headers
        username = headers.get("x-siigo-username")
        access_key = headers.get("x-siigo-access-key")
        partner_id = headers.get("x-siigo-partner-id")
        if not all([username, access_key, partner_id]):
            raise ValueError(
                "Missing required headers: x-siigo-username, x-siigo-access-key, x-siigo-partner-id"
            )
        client_class = _get_client_class()
        return client_class(username=username, access_key=access_key, partner_id=partner_id)

    return _get_global_client()


# Import tools to register them with the server
if _lazy_tools:
    # Lazy mode: only load discovery tools (~400 tokens instead of ~5600)
    from siigo_mcp.tools import discovery  # noqa: E402, F401
else:
    # Full mode: load all tools upfront
    from siigo_mcp.tools import reference  # noqa: E402, F401
    from siigo_mcp.tools import customers  # noqa: E402, F401
    from siigo_mcp.tools import products  # noqa: E402, F401
    from siigo_mcp.tools import invoices  # noqa: E402, F401
    from siigo_mcp.tools import credit_notes  # noqa: E402, F401
    from siigo_mcp.tools import journals  # noqa: E402, F401

    # Filter tools based on SIIGO_MODE (only applies in non-lazy mode)
    if _mode != "full":
        tool_names = list(mcp._tool_manager._tools.keys())
        for name in tool_names:
            if not _should_keep_tool(name):
                mcp.remove_tool(name)


def main():
    """Entry point for uvx/pip installation."""
    print(f"siigo-mcp v{__version__}")
    if _transport == "http":
        mcp.run(transport="http", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
    else:
        mcp.run()


if __name__ == "__main__":
    main()
