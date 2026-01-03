"""Reference data tools - taxes, payment types, document types, etc."""

from typing import Any

from fastmcp import Context

from siigo_mcp.server import mcp, get_client


@mcp.tool
async def get_taxes(ctx: Context) -> list[dict[str, Any]]:
    """Get all configured taxes in the Siigo account.

    Returns a list of taxes with their IDs, names, and percentages.
    Use these tax IDs when creating invoices or products.
    """
    return await get_client(ctx).get("/taxes")


@mcp.tool
async def get_payment_types(ctx: Context) -> list[dict[str, Any]]:
    """Get all configured payment types/methods.

    Returns a list of payment types (cash, credit card, bank transfer, etc.)
    Use these payment type IDs when creating invoices or cash receipts.
    """
    return await get_client(ctx).get("/payment-types")


@mcp.tool
async def get_document_types(
    ctx: Context,
    document_type: str | None = None,
) -> list[dict[str, Any]]:
    """Get all configured document types.

    Args:
        document_type: Optional filter by type (FV=invoice, NC=credit note, etc.)

    Returns a list of document types configured in the account.
    Common types: FV (factura), NC (nota crédito), RC (recibo de caja).
    """
    params: dict[str, Any] = {}
    if document_type:
        params["type"] = document_type
    return await get_client(ctx).get("/document-types", params=params or None)


@mcp.tool
async def get_warehouses(ctx: Context) -> list[dict[str, Any]]:
    """Get all configured warehouses/locations.

    Returns a list of warehouses for inventory management.
    Use warehouse IDs when creating products or invoices with inventory.
    """
    return await get_client(ctx).get("/warehouses")


@mcp.tool
async def get_users(ctx: Context) -> list[dict[str, Any]]:
    """Get all users in the Siigo account.

    Returns a list of users who can be assigned as sellers or responsible parties.
    """
    return await get_client(ctx).get("/users")


@mcp.tool
async def get_account_groups(ctx: Context) -> list[dict[str, Any]]:
    """Get all account groups/classifications.

    Returns a list of account groups for categorizing products or customers.
    """
    return await get_client(ctx).get("/account-groups")
