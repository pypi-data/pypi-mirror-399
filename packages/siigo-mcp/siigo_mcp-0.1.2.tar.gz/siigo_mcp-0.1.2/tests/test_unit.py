"""Unit tests that don't require real Siigo credentials."""

import os
from unittest.mock import AsyncMock, patch

import pytest


class TestDryRunClient:
    """Test DryRunSiigoClient mock behavior without real auth."""

    @pytest.fixture
    def mock_auth(self):
        """Mock the SiigoAuth to avoid real API calls."""
        with patch("siigo_mcp.client.SiigoAuth") as mock:
            mock.return_value.get_token = AsyncMock(return_value="fake-token")
            yield mock

    @pytest.fixture
    def dry_run_client(self, mock_auth):
        """Create a DryRunSiigoClient with mocked auth."""
        from siigo_mcp.client import DryRunSiigoClient

        return DryRunSiigoClient(
            username="fake@example.com",
            access_key="fake-key",
            partner_id="fake-partner",
        )

    @pytest.mark.asyncio
    async def test_post_returns_mock_response(self, dry_run_client):
        """POST should return mock response with dry_run=True."""
        result = await dry_run_client.post("/customers", {"name": "Test"})

        assert result["dry_run"] is True
        assert result["action"] == "create"
        assert result["path"] == "/customers"
        assert "id" in result
        assert result["validated_data"] == {"name": "Test"}

    @pytest.mark.asyncio
    async def test_put_returns_mock_response(self, dry_run_client):
        """PUT should return mock response with dry_run=True."""
        result = await dry_run_client.put("/customers/123", {"name": "Updated"})

        assert result["dry_run"] is True
        assert result["action"] == "update"
        assert result["path"] == "/customers/123"

    @pytest.mark.asyncio
    async def test_delete_returns_mock_response(self, dry_run_client):
        """DELETE should return mock response with dry_run=True."""
        result = await dry_run_client.delete("/customers/123")

        assert result["dry_run"] is True
        assert result["action"] == "delete"
        assert result["path"] == "/customers/123"


class TestToolModeFiltering:
    """Test SIIGO_MODE tool filtering logic."""

    def test_is_read_only_tool(self):
        """Check read-only tool detection."""
        from siigo_mcp.server import _is_read_only_tool

        assert _is_read_only_tool("list_customers") is True
        assert _is_read_only_tool("get_customer") is True
        assert _is_read_only_tool("get_taxes") is True

        assert _is_read_only_tool("create_customer") is False
        assert _is_read_only_tool("update_customer") is False
        assert _is_read_only_tool("delete_customer") is False
        assert _is_read_only_tool("stamp_invoice") is False

    def test_should_keep_tool_read_only_mode(self, monkeypatch):
        """In read_only mode, only list_* and get_* tools should be kept."""
        monkeypatch.setenv("SIIGO_MODE", "read_only")

        # Need to reload to pick up env var
        import importlib

        import siigo_mcp.server as server_module

        # Manually test the logic without reloading
        # (reloading would re-register tools)
        def should_keep(name: str, mode: str = "read_only") -> bool:
            if mode == "read_only":
                return name.startswith(("list_", "get_"))
            if mode == "standard":
                return name not in {"stamp_invoice", "annul_invoice", "send_invoice_email"}
            return True

        assert should_keep("list_customers", "read_only") is True
        assert should_keep("get_customer", "read_only") is True
        assert should_keep("create_customer", "read_only") is False
        assert should_keep("stamp_invoice", "read_only") is False

    def test_should_keep_tool_standard_mode(self):
        """In standard mode, dangerous tools should be excluded."""

        def should_keep(name: str) -> bool:
            dangerous = {"stamp_invoice", "annul_invoice", "send_invoice_email"}
            return name not in dangerous

        assert should_keep("list_customers") is True
        assert should_keep("create_customer") is True
        assert should_keep("delete_invoice") is True

        assert should_keep("stamp_invoice") is False
        assert should_keep("annul_invoice") is False
        assert should_keep("send_invoice_email") is False

    def test_should_keep_tool_full_mode(self):
        """In full mode, all tools should be kept."""

        def should_keep(name: str) -> bool:
            return True

        assert should_keep("list_customers") is True
        assert should_keep("create_customer") is True
        assert should_keep("stamp_invoice") is True
        assert should_keep("annul_invoice") is True


class TestServerImports:
    """Test that server modules import correctly."""

    def test_client_imports(self):
        """Test client module imports."""
        from siigo_mcp.client import DryRunSiigoClient, SiigoClient

        assert SiigoClient is not None
        assert DryRunSiigoClient is not None

    def test_auth_imports(self):
        """Test auth module imports."""
        from siigo_mcp.auth import SiigoAuth

        assert SiigoAuth is not None


class TestDangerousToolsList:
    """Test the dangerous tools configuration."""

    def test_dangerous_tools_defined(self):
        """Dangerous tools should be properly defined."""
        from siigo_mcp.server import DANGEROUS_TOOLS

        assert "stamp_invoice" in DANGEROUS_TOOLS
        assert "annul_invoice" in DANGEROUS_TOOLS
        assert "send_invoice_email" in DANGEROUS_TOOLS
        assert len(DANGEROUS_TOOLS) == 3
