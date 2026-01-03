"""Tool discovery and dynamic execution for lazy loading mode.

When SIIGO_LAZY_TOOLS=true, only these 3 meta-tools are loaded:
- list_siigo_tools: Discover available tools
- get_tool_schema: Get full parameter schema for a tool
- call_siigo_tool: Execute any tool dynamically
"""

import inspect
from typing import Any, get_type_hints

from fastmcp import Context

from siigo_mcp.server import mcp, _mode, _should_keep_tool

# Compact tool index - name, category, and one-line summary
TOOL_INDEX = [
    # Reference data
    {"name": "get_taxes", "category": "reference", "summary": "Get all configured taxes"},
    {"name": "get_payment_types", "category": "reference", "summary": "Get all payment types/methods"},
    {"name": "get_document_types", "category": "reference", "summary": "Get all document types (FV, NC, etc.)"},
    {"name": "get_warehouses", "category": "reference", "summary": "Get all warehouse locations"},
    {"name": "get_users", "category": "reference", "summary": "Get all users in the account"},
    {"name": "get_account_groups", "category": "reference", "summary": "Get all account groups"},
    # Customers
    {"name": "list_customers", "category": "customers", "summary": "List customers with pagination and filters"},
    {"name": "get_customer", "category": "customers", "summary": "Get a customer by ID"},
    {"name": "create_customer", "category": "customers", "summary": "Create a new customer"},
    {"name": "update_customer", "category": "customers", "summary": "Update an existing customer"},
    {"name": "delete_customer", "category": "customers", "summary": "Delete a customer"},
    # Products
    {"name": "list_products", "category": "products", "summary": "List products with pagination and filters"},
    {"name": "get_product", "category": "products", "summary": "Get a product by ID"},
    {"name": "create_product", "category": "products", "summary": "Create a new product"},
    {"name": "update_product", "category": "products", "summary": "Update an existing product"},
    {"name": "delete_product", "category": "products", "summary": "Delete a product"},
    # Invoices
    {"name": "list_invoices", "category": "invoices", "summary": "List invoices with pagination and filters"},
    {"name": "get_invoice", "category": "invoices", "summary": "Get an invoice by ID"},
    {"name": "create_invoice", "category": "invoices", "summary": "Create a new invoice"},
    {"name": "update_invoice", "category": "invoices", "summary": "Update an existing invoice"},
    {"name": "delete_invoice", "category": "invoices", "summary": "Delete an invoice"},
    {"name": "stamp_invoice", "category": "invoices", "summary": "Send invoice to DIAN for stamping"},
    {"name": "get_stamp_errors", "category": "invoices", "summary": "Get DIAN rejection errors"},
    {"name": "get_invoice_pdf", "category": "invoices", "summary": "Download invoice as PDF"},
    {"name": "send_invoice_email", "category": "invoices", "summary": "Email invoice to customer"},
    {"name": "annul_invoice", "category": "invoices", "summary": "Annul/cancel an invoice"},
    # Credit notes
    {"name": "list_credit_notes", "category": "credit_notes", "summary": "List credit notes with pagination"},
    {"name": "get_credit_note", "category": "credit_notes", "summary": "Get a credit note by ID"},
    {"name": "create_credit_note", "category": "credit_notes", "summary": "Create a new credit note"},
    {"name": "get_credit_note_pdf", "category": "credit_notes", "summary": "Download credit note as PDF"},
    # Journals
    {"name": "list_journals", "category": "journals", "summary": "List journal entries with pagination"},
    {"name": "get_journal", "category": "journals", "summary": "Get a journal entry by ID"},
    {"name": "create_journal", "category": "journals", "summary": "Create a new journal entry"},
]

# Cached tool functions map
_tool_functions: dict[str, Any] | None = None


def _get_tool_functions() -> dict[str, Any]:
    """Lazily import and map all tool functions."""
    global _tool_functions
    if _tool_functions is not None:
        return _tool_functions

    from siigo_mcp.tools import reference, customers, products, invoices, credit_notes, journals

    _tool_functions = {
        # Reference
        "get_taxes": reference.get_taxes,
        "get_payment_types": reference.get_payment_types,
        "get_document_types": reference.get_document_types,
        "get_warehouses": reference.get_warehouses,
        "get_users": reference.get_users,
        "get_account_groups": reference.get_account_groups,
        # Customers
        "list_customers": customers.list_customers,
        "get_customer": customers.get_customer,
        "create_customer": customers.create_customer,
        "update_customer": customers.update_customer,
        "delete_customer": customers.delete_customer,
        # Products
        "list_products": products.list_products,
        "get_product": products.get_product,
        "create_product": products.create_product,
        "update_product": products.update_product,
        "delete_product": products.delete_product,
        # Invoices
        "list_invoices": invoices.list_invoices,
        "get_invoice": invoices.get_invoice,
        "create_invoice": invoices.create_invoice,
        "update_invoice": invoices.update_invoice,
        "delete_invoice": invoices.delete_invoice,
        "stamp_invoice": invoices.stamp_invoice,
        "get_stamp_errors": invoices.get_stamp_errors,
        "get_invoice_pdf": invoices.get_invoice_pdf,
        "send_invoice_email": invoices.send_invoice_email,
        "annul_invoice": invoices.annul_invoice,
        # Credit notes
        "list_credit_notes": credit_notes.list_credit_notes,
        "get_credit_note": credit_notes.get_credit_note,
        "create_credit_note": credit_notes.create_credit_note,
        "get_credit_note_pdf": credit_notes.get_credit_note_pdf,
        # Journals
        "list_journals": journals.list_journals,
        "get_journal": journals.get_journal,
        "create_journal": journals.create_journal,
    }
    return _tool_functions


def _extract_param_schema(func: Any) -> dict[str, Any]:
    """Extract parameter schema from function signature."""
    sig = inspect.signature(func)
    properties: dict[str, Any] = {}
    required: list[str] = []

    for name, param in sig.parameters.items():
        if name == "ctx":
            continue

        prop: dict[str, Any] = {}

        # Get type annotation
        if param.annotation != inspect.Parameter.empty:
            annotation = param.annotation
            origin = getattr(annotation, "__origin__", None)

            if origin is None:
                if annotation == str:
                    prop["type"] = "string"
                elif annotation == int:
                    prop["type"] = "integer"
                elif annotation == bool:
                    prop["type"] = "boolean"
                elif annotation == float:
                    prop["type"] = "number"
            elif str(origin) == "typing.Union" or origin is type(None):
                # Handle Optional types (Union[X, None])
                args = getattr(annotation, "__args__", ())
                non_none = [a for a in args if a is not type(None)]
                if non_none:
                    inner = non_none[0]
                    if inner == str:
                        prop["type"] = "string"
                    elif inner == int:
                        prop["type"] = "integer"
                    elif inner == bool:
                        prop["type"] = "boolean"
            elif origin == list:
                prop["type"] = "array"
            elif origin == dict:
                prop["type"] = "object"

        # Check if required (no default)
        if param.default == inspect.Parameter.empty:
            required.append(name)
        else:
            prop["default"] = param.default

        properties[name] = prop

    schema: dict[str, Any] = {"type": "object", "properties": properties}
    if required:
        schema["required"] = required
    return schema


@mcp.tool
async def list_siigo_tools(
    ctx: Context,
    category: str | None = None,
) -> list[dict[str, str]]:
    """List available Siigo API tools.

    Args:
        category: Optional filter. Options: reference, customers, products,
                  invoices, credit_notes, journals

    Returns compact list with name, category, and summary.
    Use get_tool_schema() for full parameter details.
    Use call_siigo_tool() to execute any tool.
    """
    tools = TOOL_INDEX
    if category:
        tools = [t for t in tools if t["category"] == category]
    # Apply SIIGO_MODE filtering
    return [t for t in tools if _should_keep_tool(t["name"])]


@mcp.tool
async def get_tool_schema(
    ctx: Context,
    tool_name: str,
) -> dict[str, Any]:
    """Get full parameter schema for a specific tool.

    Args:
        tool_name: Name of the tool (from list_siigo_tools)

    Returns the tool's description and parameter schema.
    """
    # Check if tool is allowed in current mode
    if not _should_keep_tool(tool_name):
        return {"error": f"Tool '{tool_name}' not available in {_mode} mode"}

    funcs = _get_tool_functions()
    if tool_name not in funcs:
        return {"error": f"Unknown tool: {tool_name}"}

    tool = funcs[tool_name]
    # FunctionTool wraps the actual function in .fn
    func = tool.fn if hasattr(tool, "fn") else tool
    return {
        "name": tool_name,
        "description": func.__doc__,
        "parameters": _extract_param_schema(func),
    }


@mcp.tool
async def call_siigo_tool(
    ctx: Context,
    tool_name: str,
    params: dict[str, Any],
) -> Any:
    """Execute any Siigo tool by name.

    Args:
        tool_name: Name of the tool (from list_siigo_tools)
        params: Parameters for the tool (see get_tool_schema for details)

    Returns the tool's result.
    """
    # Check if tool is allowed in current mode
    if not _should_keep_tool(tool_name):
        return {"error": f"Tool '{tool_name}' not available in {_mode} mode"}

    funcs = _get_tool_functions()
    if tool_name not in funcs:
        return {"error": f"Unknown tool: {tool_name}"}

    tool = funcs[tool_name]
    # FunctionTool wraps the actual function in .fn
    func = tool.fn if hasattr(tool, "fn") else tool
    return await func(ctx, **params)
