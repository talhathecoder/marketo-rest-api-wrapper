"""Custom exception hierarchy for Marketo API errors.

Maps Marketo REST API error codes to meaningful Python exceptions.
Reference: https://developers.marketo.com/rest-api/error-codes/
"""

from __future__ import annotations

from typing import Any, Optional


class MarketoAPIError(Exception):
    """Base exception for all Marketo API errors.

    Attributes:
        error_code: The Marketo error code (e.g., "601", "606").
        message: Human-readable error message from the API.
        request_id: The Marketo request ID for debugging.
        response_data: Full response payload for inspection.
    """

    def __init__(
        self,
        message: str = "Unknown Marketo API error",
        error_code: str = "",
        request_id: str = "",
        response_data: Optional[dict[str, Any]] = None,
    ):
        self.error_code = error_code
        self.message = message
        self.request_id = request_id
        self.response_data = response_data or {}
        super().__init__(f"[{error_code}] {message}")


class MarketoAuthError(MarketoAPIError):
    """Authentication or authorization failure.

    Covers Marketo error codes:
        601 — Access token missing/invalid
        602 — Access token expired
    """

    pass


class MarketoRateLimitError(MarketoAPIError):
    """Rate limit exceeded.

    Covers Marketo error codes:
        606 — Max rate limit exceeded (100 calls / 20s)
        607 — Daily quota reached (50,000 calls / day)

    Attributes:
        retry_after: Suggested seconds to wait before retrying.
    """

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        error_code: str = "606",
        request_id: str = "",
        response_data: Optional[dict[str, Any]] = None,
        retry_after: int = 20,
    ):
        super().__init__(message, error_code, request_id, response_data)
        self.retry_after = retry_after


class MarketoNotFoundError(MarketoAPIError):
    """Requested resource was not found.

    Covers Marketo error codes:
        610 — Resource not found
        702 — Record not found
    """

    pass


class MarketoValidationError(MarketoAPIError):
    """Request validation failure.

    Covers Marketo error codes:
        609 — Invalid filter type
        611 — Missing required field
        612 — Invalid value
        1003 — Missing required parameter
        1004 — Invalid parameter value
    """

    pass


class MarketoRequestError(MarketoAPIError):
    """Invalid request structure.

    Covers Marketo error codes:
        600 — Unsupported HTTP method or content type
        608 — API temporarily unavailable
        614 — Invalid subscription
    """

    pass


class MarketoBulkOperationError(MarketoAPIError):
    """Error during bulk import or export operations.

    Covers errors specific to bulk API endpoints such as
    file too large, job already enqueued, or concurrent job limit reached.
    """

    pass


# ── Error code → Exception class mapping ──────────────────────────────────────

ERROR_CODE_MAP: dict[str, type[MarketoAPIError]] = {
    # Auth errors
    "601": MarketoAuthError,
    "602": MarketoAuthError,
    # Rate limit errors
    "606": MarketoRateLimitError,
    "607": MarketoRateLimitError,
    # Not found
    "610": MarketoNotFoundError,
    "702": MarketoNotFoundError,
    # Validation errors
    "609": MarketoValidationError,
    "611": MarketoValidationError,
    "612": MarketoValidationError,
    "1003": MarketoValidationError,
    "1004": MarketoValidationError,
    # Request errors
    "600": MarketoRequestError,
    "608": MarketoRequestError,
    "614": MarketoRequestError,
}


def raise_for_error(response_data: dict[str, Any], request_id: str = "") -> None:
    """Inspect a Marketo API response and raise the appropriate exception.

    Marketo returns `{"success": false, "errors": [{"code": "...", "message": "..."}]}`
    for error responses. This function parses that structure and raises a
    specific exception.

    Args:
        response_data: The parsed JSON response from the Marketo API.
        request_id: Optional request ID for debugging.

    Raises:
        MarketoAPIError: (or subclass) if the response indicates an error.
    """
    if response_data.get("success", True):
        return

    errors = response_data.get("errors", [])
    if not errors:
        raise MarketoAPIError(
            message="Unknown error (no error details in response)",
            request_id=request_id,
            response_data=response_data,
        )

    error = errors[0]
    code = str(error.get("code", ""))
    message = error.get("message", "Unknown error")

    exception_class = ERROR_CODE_MAP.get(code, MarketoAPIError)

    kwargs: dict[str, Any] = {
        "message": message,
        "error_code": code,
        "request_id": request_id,
        "response_data": response_data,
    }

    if exception_class is MarketoRateLimitError:
        kwargs["retry_after"] = 20 if code == "606" else 86400

    raise exception_class(**kwargs)
