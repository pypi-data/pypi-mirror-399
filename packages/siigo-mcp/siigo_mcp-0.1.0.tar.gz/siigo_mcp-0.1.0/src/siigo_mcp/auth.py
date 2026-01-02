"""Siigo API authentication management."""

import time
from dataclasses import dataclass

import httpx


AUTH_URL = "https://services.siigo.com/alliances/api/siigoapi-users/v1/sign-in"
TOKEN_EXPIRY_BUFFER = 300  # Refresh 5 minutes before expiry


@dataclass
class TokenInfo:
    access_token: str
    expires_at: float


class SiigoAuth:
    """Manages Siigo API authentication tokens."""

    def __init__(self, username: str, access_key: str):
        self.username = username
        self.access_key = access_key
        self._token_info: TokenInfo | None = None

    async def get_token(self, client: httpx.AsyncClient) -> str:
        """Get a valid access token, refreshing if necessary."""
        if self._token_info and self._is_token_valid():
            return self._token_info.access_token

        await self._refresh_token(client)
        assert self._token_info is not None
        return self._token_info.access_token

    def _is_token_valid(self) -> bool:
        """Check if current token is still valid."""
        if not self._token_info:
            return False
        return time.time() < (self._token_info.expires_at - TOKEN_EXPIRY_BUFFER)

    async def _refresh_token(self, client: httpx.AsyncClient) -> None:
        """Fetch a new token from Siigo."""
        response = await client.post(
            AUTH_URL,
            json={
                "username": self.username,
                "access_key": self.access_key,
            },
        )
        response.raise_for_status()
        data = response.json()

        # Token is valid for 24 hours
        self._token_info = TokenInfo(
            access_token=data["access_token"],
            expires_at=time.time() + 24 * 60 * 60,
        )
