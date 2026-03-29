"""Low-level HTTP transport for the Marketo REST API.

Handles request construction, authentication header injection,
rate limiting, retry logic, and response parsing. All resource
classes use this transport to communicate with the API.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

import requests

from marketo_api.auth import MarketoAuth
from marketo_api.config import MarketoConfig
from marketo_api.exceptions import MarketoAPIError, raise_for_error
from marketo_api.utils.rate_limiter import RateLimiter
from marketo_api.utils.retry import retry_with_backoff

logger = logging.getLogger("marketo_api.transport")


class HttpTransport:
    """HTTP transport layer for Marketo API requests.

    This class manages the underlying HTTP session, injects auth headers,
    applies rate limiting, and handles response parsing and error detection.

    Args:
        config: MarketoConfig instance with API credentials and settings.
        auth: MarketoAuth instance for token management.
        rate_limiter: RateLimiter instance for throttling.
    """

    def __init__(
        self,
        config: MarketoConfig,
        auth: MarketoAuth,
        rate_limiter: RateLimiter,
    ) -> None:
        self.config = config
        self.auth = auth
        self.rate_limiter = rate_limiter
        self._session = requests.Session()
        self._session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    def _build_url(self, endpoint: str) -> str:
        """Build the full API URL from an endpoint path.

        Args:
            endpoint: Relative API path (e.g., "/rest/v1/leads.json").

        Returns:
            Full URL string.
        """
        base = self.config.base_url.rstrip("/")
        endpoint = endpoint.lstrip("/")
        return f"{base}/{endpoint}"

    def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an authenticated GET request.

        Args:
            endpoint: API endpoint path.
            params: Query parameters.

        Returns:
            Parsed JSON response as a dict.
        """
        return self._request("GET", endpoint, params=params)

    def post(
        self,
        endpoint: str,
        json_body: dict[str, Any] | list[Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an authenticated POST request.

        Args:
            endpoint: API endpoint path.
            json_body: JSON request body.
            params: Query parameters.

        Returns:
            Parsed JSON response as a dict.
        """
        return self._request("POST", endpoint, json_body=json_body, params=params)

    def delete(
        self,
        endpoint: str,
        json_body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an authenticated DELETE request.

        Args:
            endpoint: API endpoint path.
            json_body: JSON request body.
            params: Query parameters.

        Returns:
            Parsed JSON response as a dict.
        """
        return self._request("DELETE", endpoint, json_body=json_body, params=params)

    def post_file(
        self,
        endpoint: str,
        file_path: str,
        params: dict[str, Any] | None = None,
        file_field: str = "file",
    ) -> dict[str, Any]:
        """Upload a file via multipart POST.

        Args:
            endpoint: API endpoint path.
            file_path: Path to the file to upload.
            params: Query parameters.
            file_field: The form field name for the file.

        Returns:
            Parsed JSON response as a dict.
        """
        url = self._build_url(endpoint)
        self.rate_limiter.wait_if_needed()
        headers = self.auth.get_auth_header()
        # Don't set Content-Type — requests will set multipart boundary

        with open(file_path, "rb") as f:
            files = {file_field: f}
            try:
                response = self._session.post(
                    url,
                    files=files,
                    params=params,
                    headers=headers,
                    timeout=self.config.timeout,
                )
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                raise MarketoAPIError(
                    message=f"File upload failed: {e}",
                    error_code="UPLOAD_FAILED",
                ) from e

        data = response.json()
        request_id = data.get("requestId", "")
        raise_for_error(data, request_id)
        return data

    def _request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | list[Any] | None = None,
    ) -> dict[str, Any]:
        """Execute an API request with auth, rate limiting, and error handling.

        This is the core request method used by get(), post(), and delete().
        """

        def _do_request() -> dict[str, Any]:
            url = self._build_url(endpoint)
            self.rate_limiter.wait_if_needed()
            headers = self.auth.get_auth_header()

            logger.debug("%s %s params=%s", method, url, params)

            try:
                response = self._session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_body,
                    headers=headers,
                    timeout=self.config.timeout,
                )
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                raise MarketoAPIError(
                    message=f"HTTP request failed: {e}",
                    error_code="HTTP_ERROR",
                ) from e

            data = response.json()
            request_id = data.get("requestId", "")

            logger.debug(
                "Response: success=%s requestId=%s",
                data.get("success"),
                request_id,
            )

            raise_for_error(data, request_id)
            return data

        # Wrap with retry logic
        retriable = retry_with_backoff(
            _do_request,
            max_retries=self.config.max_retries,
            backoff_factor=self.config.retry_backoff_factor,
            on_auth_error=self.auth.invalidate,
        )
        return retriable()
