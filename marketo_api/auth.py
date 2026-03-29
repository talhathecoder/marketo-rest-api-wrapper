"""OAuth 2.0 authentication handler for the Marketo REST API.

Manages token acquisition, caching, and automatic refresh before expiry.
"""

from __future__ import annotations

import logging
import time
from typing import Optional

import requests

from marketo_api.config import MarketoConfig
from marketo_api.exceptions import MarketoAuthError

logger = logging.getLogger("marketo_api.auth")


class MarketoAuth:
    """Handles Marketo OAuth 2.0 client_credentials flow.

    Automatically acquires a new access token when:
    - No token has been acquired yet
    - The current token is within `token_refresh_buffer` seconds of expiry

    Attributes:
        config: The MarketoConfig containing credentials.
        access_token: The current valid access token (or None).
        token_expiry: Unix timestamp when the current token expires.
    """

    def __init__(self, config: MarketoConfig) -> None:
        self.config = config
        self.access_token: Optional[str] = None
        self.token_expiry: float = 0.0
        self._session = requests.Session()

    @property
    def is_token_valid(self) -> bool:
        """Check if the current token is still valid (with buffer)."""
        if not self.access_token:
            return False
        return time.time() < (self.token_expiry - self.config.token_refresh_buffer)

    def get_token(self) -> str:
        """Return a valid access token, refreshing if necessary.

        Returns:
            A valid OAuth access token string.

        Raises:
            MarketoAuthError: If token acquisition fails.
        """
        if self.is_token_valid:
            return self.access_token  # type: ignore[return-value]

        logger.debug("Acquiring new access token...")
        return self._acquire_token()

    def _acquire_token(self) -> str:
        """Request a new access token from the Marketo identity endpoint.

        Returns:
            The new access token.

        Raises:
            MarketoAuthError: If the token request fails.
        """
        url = f"{self.config.identity_url}/oauth/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
        }

        try:
            response = self._session.get(url, params=params, timeout=self.config.timeout)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise MarketoAuthError(
                message=f"Failed to acquire access token: {e}",
                error_code="AUTH_REQUEST_FAILED",
            ) from e

        data = response.json()

        if "access_token" not in data:
            error_msg = data.get("error_description", data.get("error", "Unknown auth error"))
            raise MarketoAuthError(
                message=f"Token response missing access_token: {error_msg}",
                error_code=data.get("error", "AUTH_FAILED"),
                response_data=data,
            )

        self.access_token = data["access_token"]
        expires_in = data.get("expires_in", 3600)
        self.token_expiry = time.time() + expires_in

        logger.info("Access token acquired (expires in %ds)", expires_in)
        return self.access_token

    def invalidate(self) -> None:
        """Force token refresh on next call to get_token()."""
        logger.debug("Invalidating current access token")
        self.access_token = None
        self.token_expiry = 0.0

    def get_auth_header(self) -> dict[str, str]:
        """Return the Authorization header dict with a valid token.

        Returns:
            Dict suitable for passing to requests as headers.
        """
        token = self.get_token()
        return {"Authorization": f"Bearer {token}"}
