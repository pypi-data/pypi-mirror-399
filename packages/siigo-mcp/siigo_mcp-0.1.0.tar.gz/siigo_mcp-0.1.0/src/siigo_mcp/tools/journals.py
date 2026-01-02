"""Journal (accounting voucher) tools."""

from typing import Any

from fastmcp import Context

from siigo_mcp.server import mcp, get_client


@mcp.tool
async def list_journals(
    ctx: Context,
    page: int = 1,
    page_size: int = 25,
    date_start: str | None = None,
    date_end: str | None = None,
) -> dict[str, Any]:
    """List journal entries (accounting vouchers) with pagination.

    Args:
        page: Page number (starts at 1)
        page_size: Number of results per page (max 100)
        date_start: Filter by start date (YYYY-MM-DD format)
        date_end: Filter by end date (YYYY-MM-DD format)

    Returns paginated list of journal entries with navigation links.
    """
    params: dict[str, Any] = {"page": page, "page_size": min(page_size, 100)}
    if date_start:
        params["date_start"] = date_start
    if date_end:
        params["date_end"] = date_end

    return await get_client(ctx).get("/journals", params=params)


@mcp.tool
async def get_journal(ctx: Context, journal_id: str) -> dict[str, Any]:
    """Get a journal entry by ID.

    Args:
        journal_id: The journal's GUID

    Returns the full journal entry details including all line items.
    """
    return await get_client(ctx).get(f"/journals/{journal_id}")


@mcp.tool
async def create_journal(
    ctx: Context,
    document_type: int,
    date: str,
    items: list[dict[str, Any]],
    cost_center: int | None = None,
    observations: str | None = None,
) -> dict[str, Any]:
    """Create a new journal entry (accounting voucher).

    Args:
        document_type: Document type ID for journals (get from get_document_types with type=CC)
        date: Journal date (YYYY-MM-DD)
        items: List of journal items, each with:
            - account: Account code (PUC code)
            - customer: Optional customer object with id
            - description: Line item description
            - debit: Debit amount (use 0 if credit)
            - credit: Credit amount (use 0 if debit)
            - cost_center: Optional cost center ID
        cost_center: Default cost center ID for all items
        observations: Journal notes/observations

    Returns the created journal entry with its assigned number and ID.
    Note: Total debits must equal total credits for a valid journal entry.
    """
    data: dict[str, Any] = {
        "document": {"id": document_type},
        "date": date,
        "items": items,
    }

    if cost_center:
        data["cost_center"] = cost_center
    if observations:
        data["observations"] = observations

    return await get_client(ctx).post("/journals", data)
