"""Product CRUD tools."""

from typing import Any

from fastmcp import Context

from siigo_mcp.server import mcp, get_client


@mcp.tool
async def list_products(
    ctx: Context,
    page: int = 1,
    page_size: int = 25,
    code: str | None = None,
    name: str | None = None,
) -> dict[str, Any]:
    """List products with pagination and optional filters.

    Args:
        page: Page number (starts at 1)
        page_size: Number of results per page (max 100)
        code: Filter by product code (partial match)
        name: Filter by product name (partial match)

    Returns paginated list of products with navigation links.
    """
    params: dict[str, Any] = {"page": page, "page_size": min(page_size, 100)}
    if code:
        params["code"] = code
    if name:
        params["name"] = name

    return await get_client(ctx).get("/products", params=params)


@mcp.tool
async def get_product(ctx: Context, product_id: str) -> dict[str, Any]:
    """Get a product by ID.

    Args:
        product_id: The product's GUID

    Returns the full product details including prices and taxes.
    """
    return await get_client(ctx).get(f"/products/{product_id}")


@mcp.tool
async def create_product(
    ctx: Context,
    code: str,
    name: str,
    account_group: int,
    product_type: str = "Product",
    stock_control: bool = False,
    unit: str = "94",
    description: str | None = None,
    prices: list[dict[str, Any]] | None = None,
    taxes: list[dict[str, Any]] | None = None,
    warehouses: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Create a new product.

    Args:
        code: Unique product code/SKU
        name: Product name
        account_group: Account group ID for categorization
        product_type: "Product" for physical goods, "Service" for services
        stock_control: Whether to track inventory
        unit: Unit of measure code (94=Unit, default)
        description: Optional product description
        prices: List of price objects with price_list and value
        taxes: List of tax objects with id
        warehouses: List of warehouse objects for inventory

    Returns the created product with its assigned ID.
    """
    data: dict[str, Any] = {
        "code": code,
        "name": name,
        "account_group": account_group,
        "type": product_type,
        "stock_control": stock_control,
        "unit": unit,
    }

    if description:
        data["description"] = description
    if prices:
        data["prices"] = prices
    if taxes:
        data["taxes"] = taxes
    if warehouses:
        data["warehouses"] = warehouses

    return await get_client(ctx).post("/products", data)


@mcp.tool
async def update_product(
    ctx: Context,
    product_id: str,
    code: str | None = None,
    name: str | None = None,
    account_group: int | None = None,
    product_type: str | None = None,
    stock_control: bool | None = None,
    unit: str | None = None,
    description: str | None = None,
    prices: list[dict[str, Any]] | None = None,
    taxes: list[dict[str, Any]] | None = None,
    warehouses: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Update an existing product.

    Args:
        product_id: The product's GUID to update
        code: Product code/SKU
        name: Product name
        account_group: Account group ID
        product_type: "Product" or "Service"
        stock_control: Whether to track inventory
        unit: Unit of measure code
        description: Product description
        prices: List of price objects
        taxes: List of tax objects
        warehouses: List of warehouse objects

    Returns the updated product.
    """
    data: dict[str, Any] = {}

    if code:
        data["code"] = code
    if name:
        data["name"] = name
    if account_group:
        data["account_group"] = account_group
    if product_type:
        data["type"] = product_type
    if stock_control is not None:
        data["stock_control"] = stock_control
    if unit:
        data["unit"] = unit
    if description:
        data["description"] = description
    if prices:
        data["prices"] = prices
    if taxes:
        data["taxes"] = taxes
    if warehouses:
        data["warehouses"] = warehouses

    return await get_client(ctx).put(f"/products/{product_id}", data)


@mcp.tool
async def delete_product(ctx: Context, product_id: str) -> dict[str, Any]:
    """Delete a product.

    Args:
        product_id: The product's GUID to delete

    Returns confirmation of deletion.
    Note: Products with associated documents cannot be deleted.
    """
    return await get_client(ctx).delete(f"/products/{product_id}")
