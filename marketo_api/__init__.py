"""
Marketo REST API Wrapper
========================

A comprehensive Python wrapper for the Marketo REST API with built-in
authentication management, rate limiting, pagination, retry logic, and
structured error handling.

Usage:
    from marketo_api import MarketoClient

    client = MarketoClient(
        munchkin_id="123-ABC-456",
        client_id="your-client-id",
        client_secret="your-client-secret"
    )

    lead = client.leads.get_by_email("john@example.com")
"""

from marketo_api.client import MarketoClient
from marketo_api.config import MarketoConfig
from marketo_api.exceptions import (
    MarketoAPIError,
    MarketoAuthError,
    MarketoNotFoundError,
    MarketoRateLimitError,
    MarketoValidationError,
)

__version__ = "1.0.0"
__all__ = [
    "MarketoClient",
    "MarketoConfig",
    "MarketoAPIError",
    "MarketoAuthError",
    "MarketoNotFoundError",
    "MarketoRateLimitError",
    "MarketoValidationError",
]
