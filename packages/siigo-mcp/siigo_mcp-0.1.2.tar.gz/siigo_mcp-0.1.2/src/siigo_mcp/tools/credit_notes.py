"""Credit note CRUD tools."""

import base64
from typing import Any

from fastmcp import Context

from siigo_mcp.server import mcp, get_client


@mcp.tool
async def list_credit_notes(
    ctx: Context,
    page: int = 1,
    page_size: int = 25,
    date_start: str | None = None,
    date_end: str | None = None,
) -> dict[str, Any]:
    """List credit notes with pagination and optional filters.

    Args:
        page: Page number (starts at 1)
        page_size: Number of results per page (max 100)
        date_start: Filter by start date (YYYY-MM-DD format)
        date_end: Filter by end date (YYYY-MM-DD format)

    Returns paginated list of credit notes with navigation links.
    """
    params: dict[str, Any] = {"page": page, "page_size": min(page_size, 100)}
    if date_start:
        params["date_start"] = date_start
    if date_end:
        params["date_end"] = date_end

    return await get_client(ctx).get("/credit-notes", params=params)


@mcp.tool
async def get_credit_note(ctx: Context, credit_note_id: str) -> dict[str, Any]:
    """Get a credit note by ID.

    Args:
        credit_note_id: The credit note's GUID

    Returns the full credit note details.
    """
    return await get_client(ctx).get(f"/credit-notes/{credit_note_id}")


@mcp.tool
async def create_credit_note(
    ctx: Context,
    document_type: int,
    customer_id: str,
    items: list[dict[str, Any]],
    reason: str,
    invoice_id: str | None = None,
    date: str | None = None,
    cost_center: int | None = None,
    observations: str | None = None,
    stamp: bool = False,
) -> dict[str, Any]:
    """Create a new credit note.

    Args:
        document_type: Document type ID for credit notes (get from get_document_types with type=NC)
        customer_id: Customer GUID
        items: List of credit note items, each with:
            - code: Product code
            - quantity: Item quantity
            - price: Unit price
            - taxes: List of tax objects with id
        reason: Reason for the credit note (required by DIAN)
        invoice_id: Optional reference to the original invoice being credited
        date: Credit note date (YYYY-MM-DD), defaults to today
        cost_center: Cost center ID
        observations: Credit note notes/observations
        stamp: If True, immediately send to DIAN for electronic stamping

    Returns the created credit note with its assigned number and ID.
    """
    data: dict[str, Any] = {
        "document": {"id": document_type},
        "customer": {"id": customer_id},
        "items": items,
        "reason": reason,
    }

    if invoice_id:
        data["invoice"] = {"id": invoice_id}
    if date:
        data["date"] = date
    if cost_center:
        data["cost_center"] = cost_center
    if observations:
        data["observations"] = observations
    if stamp:
        data["stamp"] = {"send": True}

    return await get_client(ctx).post("/credit-notes", data)


@mcp.tool
async def get_credit_note_pdf(ctx: Context, credit_note_id: str) -> str:
    """Download a credit note as PDF.

    Args:
        credit_note_id: The credit note's GUID

    Returns the PDF content as base64-encoded string.
    Decode with base64.b64decode() to get binary PDF.
    """
    pdf_bytes = await get_client(ctx).get_pdf(f"/credit-notes/{credit_note_id}/pdf")
    return base64.b64encode(pdf_bytes).decode("utf-8")
