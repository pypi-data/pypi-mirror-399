"""Invoice CRUD and DIAN tools."""

import base64
from typing import Any

from fastmcp import Context

from siigo_mcp.server import mcp, get_client


@mcp.tool
async def list_invoices(
    ctx: Context,
    page: int = 1,
    page_size: int = 25,
    date_start: str | None = None,
    date_end: str | None = None,
    customer_name: str | None = None,
) -> dict[str, Any]:
    """List invoices with pagination and optional filters.

    Args:
        page: Page number (starts at 1)
        page_size: Number of results per page (max 100)
        date_start: Filter by start date (YYYY-MM-DD format)
        date_end: Filter by end date (YYYY-MM-DD format)
        customer_name: Filter by customer name (partial match)

    Returns paginated list of invoices with navigation links.
    """
    params: dict[str, Any] = {"page": page, "page_size": min(page_size, 100)}
    if date_start:
        params["date_start"] = date_start
    if date_end:
        params["date_end"] = date_end
    if customer_name:
        params["name"] = customer_name

    return await get_client(ctx).get("/invoices", params=params)


@mcp.tool
async def get_invoice(ctx: Context, invoice_id: str) -> dict[str, Any]:
    """Get an invoice by ID.

    Args:
        invoice_id: The invoice's GUID

    Returns the full invoice details including items, taxes, and payments.
    """
    return await get_client(ctx).get(f"/invoices/{invoice_id}")


@mcp.tool
async def create_invoice(
    ctx: Context,
    document_type: int,
    customer_id: str,
    items: list[dict[str, Any]],
    payments: list[dict[str, Any]],
    date: str | None = None,
    seller: int | None = None,
    cost_center: int | None = None,
    currency: dict[str, Any] | None = None,
    observations: str | None = None,
    stamp: bool = False,
) -> dict[str, Any]:
    """Create a new invoice.

    Args:
        document_type: Document type ID (get from get_document_types)
        customer_id: Customer GUID
        items: List of invoice items, each with:
            - code: Product code
            - quantity: Item quantity
            - price: Unit price
            - discount: Discount percentage (optional)
            - taxes: List of tax objects with id
        payments: List of payments, each with:
            - id: Payment type ID
            - value: Payment amount
            - due_date: Payment due date (YYYY-MM-DD)
        date: Invoice date (YYYY-MM-DD), defaults to today
        seller: Seller user ID
        cost_center: Cost center ID
        currency: Currency object with code and exchange_rate
        observations: Invoice notes/observations
        stamp: If True, immediately send to DIAN for electronic stamping

    Returns the created invoice with its assigned number and ID.
    """
    data: dict[str, Any] = {
        "document": {"id": document_type},
        "customer": {"id": customer_id},
        "items": items,
        "payments": payments,
    }

    if date:
        data["date"] = date
    if seller:
        data["seller"] = seller
    if cost_center:
        data["cost_center"] = cost_center
    if currency:
        data["currency"] = currency
    if observations:
        data["observations"] = observations
    if stamp:
        data["stamp"] = {"send": True}

    return await get_client(ctx).post("/invoices", data)


@mcp.tool
async def update_invoice(
    ctx: Context,
    invoice_id: str,
    document_type: int | None = None,
    customer_id: str | None = None,
    items: list[dict[str, Any]] | None = None,
    payments: list[dict[str, Any]] | None = None,
    date: str | None = None,
    seller: int | None = None,
    cost_center: int | None = None,
    currency: dict[str, Any] | None = None,
    observations: str | None = None,
) -> dict[str, Any]:
    """Update an existing invoice.

    Args:
        invoice_id: The invoice's GUID to update
        document_type: Document type ID
        customer_id: Customer GUID
        items: List of invoice items
        payments: List of payments
        date: Invoice date (YYYY-MM-DD)
        seller: Seller user ID
        cost_center: Cost center ID
        currency: Currency object
        observations: Invoice notes

    Returns the updated invoice.
    Note: Cannot update invoices that have been stamped with DIAN.
    """
    data: dict[str, Any] = {}

    if document_type:
        data["document"] = {"id": document_type}
    if customer_id:
        data["customer"] = {"id": customer_id}
    if items:
        data["items"] = items
    if payments:
        data["payments"] = payments
    if date:
        data["date"] = date
    if seller:
        data["seller"] = seller
    if cost_center:
        data["cost_center"] = cost_center
    if currency:
        data["currency"] = currency
    if observations:
        data["observations"] = observations

    return await get_client(ctx).put(f"/invoices/{invoice_id}", data)


@mcp.tool
async def delete_invoice(ctx: Context, invoice_id: str) -> dict[str, Any]:
    """Delete an invoice.

    Args:
        invoice_id: The invoice's GUID to delete

    Returns confirmation of deletion.
    Note: Cannot delete invoices that have been stamped with DIAN.
    """
    return await get_client(ctx).delete(f"/invoices/{invoice_id}")


@mcp.tool
async def stamp_invoice(ctx: Context, invoice_id: str) -> dict[str, Any]:
    """Send an invoice to DIAN for electronic stamping.

    Args:
        invoice_id: The invoice's GUID to stamp

    Returns the stamping result including CUFE (electronic invoice code).
    This makes the invoice official and legally valid in Colombia.
    """
    return await get_client(ctx).post(f"/invoices/{invoice_id}/stamp", {})


@mcp.tool
async def get_stamp_errors(ctx: Context, invoice_id: str) -> dict[str, Any]:
    """Get DIAN rejection errors for an invoice.

    Args:
        invoice_id: The invoice's GUID

    Returns any errors from DIAN if the stamp was rejected.
    Use this to understand why an invoice failed DIAN validation.
    """
    return await get_client(ctx).get(f"/invoices/{invoice_id}/stamp/errors")


@mcp.tool
async def get_invoice_pdf(ctx: Context, invoice_id: str) -> str:
    """Download an invoice as PDF.

    Args:
        invoice_id: The invoice's GUID

    Returns the PDF content as base64-encoded string.
    Decode with base64.b64decode() to get binary PDF.
    """
    pdf_bytes = await get_client(ctx).get_pdf(f"/invoices/{invoice_id}/pdf")
    return base64.b64encode(pdf_bytes).decode("utf-8")


@mcp.tool
async def send_invoice_email(ctx: Context, invoice_id: str, email: str) -> dict[str, Any]:
    """Send an invoice by email.

    Args:
        invoice_id: The invoice's GUID
        email: Recipient email address

    Returns confirmation of email sent.
    The email includes the invoice PDF and XML (for electronic invoices).
    """
    return await get_client(ctx).post(f"/invoices/{invoice_id}/mail", {"email": email})


@mcp.tool
async def annul_invoice(ctx: Context, invoice_id: str) -> dict[str, Any]:
    """Annul an invoice.

    Args:
        invoice_id: The invoice's GUID to annul

    Returns confirmation of annulment.
    For electronic invoices, this creates a credit note to cancel.
    """
    return await get_client(ctx).post(f"/invoices/{invoice_id}/annul", {})
