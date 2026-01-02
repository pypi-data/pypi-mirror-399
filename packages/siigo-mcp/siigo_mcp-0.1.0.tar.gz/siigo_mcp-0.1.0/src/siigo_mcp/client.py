"""Siigo API client wrapper."""

import logging
import uuid
from typing import Any

import httpx

from siigo_mcp.auth import SiigoAuth

logger = logging.getLogger(__name__)


BASE_URL = "https://api.siigo.com/v1"


class SiigoClient:
    """Async client for the Siigo API."""

    def __init__(self, username: str, access_key: str, partner_id: str):
        self.partner_id = partner_id
        self._auth = SiigoAuth(username, access_key)
        self._client = httpx.AsyncClient(
            base_url=BASE_URL,
            timeout=30.0,
        )

    async def _get_headers(self) -> dict[str, str]:
        """Get headers with current auth token."""
        token = await self._auth.get_token(self._client)
        return {
            "Authorization": f"Bearer {token}",
            "Partner-Id": self.partner_id,
            "Content-Type": "application/json",
        }

    async def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """Make a GET request to the Siigo API."""
        headers = await self._get_headers()
        response = await self._client.get(path, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    async def post(self, path: str, data: dict[str, Any]) -> Any:
        """Make a POST request to the Siigo API."""
        headers = await self._get_headers()
        response = await self._client.post(path, headers=headers, json=data)
        response.raise_for_status()
        return response.json()

    async def put(self, path: str, data: dict[str, Any]) -> Any:
        """Make a PUT request to the Siigo API."""
        headers = await self._get_headers()
        response = await self._client.put(path, headers=headers, json=data)
        response.raise_for_status()
        return response.json()

    async def delete(self, path: str) -> Any:
        """Make a DELETE request to the Siigo API."""
        headers = await self._get_headers()
        response = await self._client.delete(path, headers=headers)
        response.raise_for_status()
        if response.content:
            return response.json()
        return None

    async def get_pdf(self, path: str) -> bytes:
        """Get PDF content from the Siigo API."""
        headers = await self._get_headers()
        headers["Accept"] = "application/pdf"
        response = await self._client.get(path, headers=headers)
        response.raise_for_status()
        return response.content

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()


class DryRunSiigoClient(SiigoClient):
    """Client that validates but doesn't execute write operations.

    - GET requests work normally (read-only, safe)
    - POST/PUT/DELETE log the operation and return mock responses
    """

    def _log_operation(self, method: str, path: str, data: dict[str, Any] | None) -> None:
        """Log what would have been executed."""
        logger.info(f"[DRY RUN] {method} {path}", extra={"data": data})

    def _mock_response(self, action: str, path: str, data: dict[str, Any] | None) -> dict[str, Any]:
        """Generate a mock response for dry-run operations."""
        return {
            "id": str(uuid.uuid4()),
            "dry_run": True,
            "action": action,
            "path": path,
            "validated_data": data,
            "message": f"Dry run: would {action} at {path}",
        }

    async def post(self, path: str, data: dict[str, Any]) -> dict[str, Any]:
        """Mock POST - validate and log without executing."""
        self._log_operation("POST", path, data)
        return self._mock_response("create", path, data)

    async def put(self, path: str, data: dict[str, Any]) -> dict[str, Any]:
        """Mock PUT - validate and log without executing."""
        self._log_operation("PUT", path, data)
        return self._mock_response("update", path, data)

    async def delete(self, path: str) -> dict[str, Any]:
        """Mock DELETE - log without executing."""
        self._log_operation("DELETE", path, None)
        return self._mock_response("delete", path, None)
