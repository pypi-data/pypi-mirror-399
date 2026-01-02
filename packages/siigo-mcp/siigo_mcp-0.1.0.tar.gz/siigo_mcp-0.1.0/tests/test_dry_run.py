"""Tests for dry-run mode - verify mutations are mocked correctly."""

import pytest


@pytest.mark.asyncio
async def test_dry_run_post_returns_mock(dry_run_client):
    """Test that POST in dry-run mode returns mock response."""
    result = await dry_run_client.post("/customers", {"name": ["Test", "Customer"]})

    assert result["dry_run"] is True
    assert result["action"] == "create"
    assert result["path"] == "/customers"
    assert "id" in result  # Should have a mock UUID
    assert result["validated_data"] == {"name": ["Test", "Customer"]}


@pytest.mark.asyncio
async def test_dry_run_put_returns_mock(dry_run_client):
    """Test that PUT in dry-run mode returns mock response."""
    result = await dry_run_client.put("/customers/123", {"name": ["Updated", "Name"]})

    assert result["dry_run"] is True
    assert result["action"] == "update"
    assert result["path"] == "/customers/123"


@pytest.mark.asyncio
async def test_dry_run_delete_returns_mock(dry_run_client):
    """Test that DELETE in dry-run mode returns mock response."""
    result = await dry_run_client.delete("/customers/123")

    assert result["dry_run"] is True
    assert result["action"] == "delete"
    assert result["path"] == "/customers/123"


@pytest.mark.asyncio
async def test_dry_run_get_works_normally(dry_run_client):
    """Test that GET in dry-run mode still hits the real API."""
    # GET should work normally even in dry-run mode
    result = await dry_run_client.get("/taxes")

    # This should be real data, not a mock
    assert isinstance(result, list)
    assert "dry_run" not in result if isinstance(result, dict) else True
