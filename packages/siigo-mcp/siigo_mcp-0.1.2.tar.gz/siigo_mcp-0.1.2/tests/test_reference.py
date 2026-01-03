"""Tests for reference data tools (read-only, safe to run with real credentials)."""

import pytest


@pytest.mark.asyncio
async def test_get_taxes(siigo_client):
    """Test fetching taxes from Siigo API."""
    result = await siigo_client.get("/taxes")
    assert isinstance(result, list)
    # Taxes should have id and name at minimum
    if result:
        assert "id" in result[0]
        assert "name" in result[0]


@pytest.mark.asyncio
async def test_get_payment_types(siigo_client):
    """Test fetching payment types from Siigo API."""
    result = await siigo_client.get("/payment-types")
    assert isinstance(result, list)
    if result:
        assert "id" in result[0]
        assert "name" in result[0]


@pytest.mark.asyncio
async def test_get_document_types(siigo_client):
    """Test fetching document types from Siigo API."""
    result = await siigo_client.get("/document-types")
    assert isinstance(result, list)
    if result:
        assert "id" in result[0]


@pytest.mark.asyncio
async def test_get_warehouses(siigo_client):
    """Test fetching warehouses from Siigo API."""
    result = await siigo_client.get("/warehouses")
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_get_users(siigo_client):
    """Test fetching users from Siigo API."""
    result = await siigo_client.get("/users")
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_get_account_groups(siigo_client):
    """Test fetching account groups from Siigo API."""
    result = await siigo_client.get("/account-groups")
    assert isinstance(result, list)
