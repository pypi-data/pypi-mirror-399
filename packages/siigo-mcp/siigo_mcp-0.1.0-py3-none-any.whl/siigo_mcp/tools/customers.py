"""Customer CRUD tools."""

from typing import Any

from fastmcp import Context

from siigo_mcp.server import mcp, get_client


@mcp.tool
async def list_customers(
    ctx: Context,
    page: int = 1,
    page_size: int = 25,
    name: str | None = None,
    identification: str | None = None,
) -> dict[str, Any]:
    """List customers with pagination and optional filters.

    Args:
        page: Page number (starts at 1)
        page_size: Number of results per page (max 100)
        name: Filter by customer name (partial match)
        identification: Filter by identification number (NIT/cédula)

    Returns paginated list of customers with navigation links.
    """
    params: dict[str, Any] = {"page": page, "page_size": min(page_size, 100)}
    if name:
        params["name"] = name
    if identification:
        params["identification"] = identification

    return await get_client(ctx).get("/customers", params=params)


@mcp.tool
async def get_customer(ctx: Context, customer_id: str) -> dict[str, Any]:
    """Get a customer by ID.

    Args:
        customer_id: The customer's GUID

    Returns the full customer details including contacts and addresses.
    """
    return await get_client(ctx).get(f"/customers/{customer_id}")


@mcp.tool
async def create_customer(
    ctx: Context,
    person_type: str,
    id_type: str,
    identification: str,
    name: list[str],
    commercial_name: str | None = None,
    vat_responsible: bool = False,
    fiscal_responsibilities: list[str] | None = None,
    address: dict[str, Any] | None = None,
    phones: list[dict[str, Any]] | None = None,
    contacts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Create a new customer.

    Args:
        person_type: "Person" for natural person, "Company" for legal entity
        id_type: Identification type code (13=Cédula, 31=NIT for Colombia)
        identification: The identification number
        name: List of name parts. For Person: [first_name, last_name].
              For Company: [company_name]
        commercial_name: Optional trade/commercial name
        vat_responsible: Whether customer is VAT responsible
        fiscal_responsibilities: List of fiscal responsibility codes (e.g., ["R-99-PN"])
        address: Address object with city, address, postal_code
        phones: List of phone objects with number and extension
        contacts: List of contact objects with name, email, phone

    Returns the created customer with its assigned ID.
    """
    data: dict[str, Any] = {
        "type": person_type,
        "id_type": {"code": id_type},
        "identification": identification,
        "name": name,
        "vat_responsible": vat_responsible,
    }

    if commercial_name:
        data["commercial_name"] = commercial_name
    if fiscal_responsibilities:
        data["fiscal_responsibilities"] = [
            {"code": code} for code in fiscal_responsibilities
        ]
    if address:
        data["address"] = address
    if phones:
        data["phones"] = phones
    if contacts:
        data["contacts"] = contacts

    return await get_client(ctx).post("/customers", data)


@mcp.tool
async def update_customer(
    ctx: Context,
    customer_id: str,
    person_type: str | None = None,
    id_type: str | None = None,
    identification: str | None = None,
    name: list[str] | None = None,
    commercial_name: str | None = None,
    vat_responsible: bool | None = None,
    fiscal_responsibilities: list[str] | None = None,
    address: dict[str, Any] | None = None,
    phones: list[dict[str, Any]] | None = None,
    contacts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Update an existing customer.

    Args:
        customer_id: The customer's GUID to update
        person_type: "Person" or "Company"
        id_type: Identification type code
        identification: The identification number
        name: List of name parts
        commercial_name: Trade/commercial name
        vat_responsible: Whether customer is VAT responsible
        fiscal_responsibilities: List of fiscal responsibility codes
        address: Address object
        phones: List of phone objects
        contacts: List of contact objects

    Returns the updated customer.
    """
    data: dict[str, Any] = {}

    if person_type:
        data["type"] = person_type
    if id_type:
        data["id_type"] = {"code": id_type}
    if identification:
        data["identification"] = identification
    if name:
        data["name"] = name
    if commercial_name:
        data["commercial_name"] = commercial_name
    if vat_responsible is not None:
        data["vat_responsible"] = vat_responsible
    if fiscal_responsibilities:
        data["fiscal_responsibilities"] = [
            {"code": code} for code in fiscal_responsibilities
        ]
    if address:
        data["address"] = address
    if phones:
        data["phones"] = phones
    if contacts:
        data["contacts"] = contacts

    return await get_client(ctx).put(f"/customers/{customer_id}", data)


@mcp.tool
async def delete_customer(ctx: Context, customer_id: str) -> dict[str, Any]:
    """Delete a customer.

    Args:
        customer_id: The customer's GUID to delete

    Returns confirmation of deletion.
    Note: Customers with associated documents cannot be deleted.
    """
    return await get_client(ctx).delete(f"/customers/{customer_id}")
