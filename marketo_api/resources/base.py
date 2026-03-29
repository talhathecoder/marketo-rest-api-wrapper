"""Base resource class that all API resources inherit from."""

from __future__ import annotations

from typing import Any

from marketo_api.transport import HttpTransport


class BaseResource:
    """Base class for all Marketo API resource classes.

    Provides access to the HTTP transport layer and common
    helper methods for building requests.

    Args:
        transport: The HttpTransport instance for making API calls.
    """

    def __init__(self, transport: HttpTransport) -> None:
        self._transport = transport

    def _get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Shortcut for GET requests."""
        return self._transport.get(endpoint, params=params)

    def _post(
        self,
        endpoint: str,
        json_body: dict[str, Any] | list[Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Shortcut for POST requests."""
        return self._transport.post(endpoint, json_body=json_body, params=params)

    def _delete(
        self,
        endpoint: str,
        json_body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Shortcut for DELETE requests."""
        return self._transport.delete(endpoint, json_body=json_body, params=params)
