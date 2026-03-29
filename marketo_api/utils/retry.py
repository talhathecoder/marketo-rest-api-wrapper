"""Retry logic with exponential backoff for transient Marketo API errors."""

from __future__ import annotations

import logging
import time
from typing import Any, Callable, TypeVar

import requests

from marketo_api.exceptions import MarketoAPIError, MarketoAuthError, MarketoRateLimitError

logger = logging.getLogger("marketo_api.retry")

T = TypeVar("T")

# HTTP status codes worth retrying
RETRYABLE_HTTP_CODES = {429, 500, 502, 503, 504}

# Marketo error codes worth retrying
RETRYABLE_MARKETO_CODES = {
    "601",  # Access token invalid (may be stale — re-auth and retry)
    "602",  # Access token expired
    "606",  # Rate limit exceeded
    "608",  # API temporarily unavailable
}


def retry_with_backoff(
    func: Callable[..., T],
    max_retries: int = 3,
    backoff_factor: float = 2.0,
    on_auth_error: Callable[[], None] | None = None,
) -> Callable[..., T]:
    """Wrap a function with retry logic and exponential backoff.

    Args:
        func: The function to wrap.
        max_retries: Maximum number of retry attempts.
        backoff_factor: Multiplier for wait time between retries.
        on_auth_error: Callback to invoke when an auth error occurs
            (e.g., to refresh the token before retrying).

    Returns:
        A wrapped version of `func` that retries on transient errors.
    """

    def wrapper(*args: Any, **kwargs: Any) -> T:
        last_exception: Exception | None = None

        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)

            except MarketoRateLimitError as e:
                last_exception = e
                wait = e.retry_after if e.retry_after else backoff_factor ** attempt
                logger.warning(
                    "Rate limit hit (attempt %d/%d). Waiting %ds...",
                    attempt + 1,
                    max_retries + 1,
                    wait,
                )
                if attempt < max_retries:
                    time.sleep(wait)
                    continue
                raise

            except MarketoAuthError as e:
                last_exception = e
                if on_auth_error and attempt < max_retries:
                    logger.info(
                        "Auth error (attempt %d/%d). Refreshing token...",
                        attempt + 1,
                        max_retries + 1,
                    )
                    on_auth_error()
                    continue
                raise

            except requests.exceptions.HTTPError as e:
                last_exception = e
                status_code = e.response.status_code if e.response is not None else 0
                if status_code in RETRYABLE_HTTP_CODES and attempt < max_retries:
                    wait = backoff_factor ** attempt
                    logger.warning(
                        "HTTP %d error (attempt %d/%d). Retrying in %.1fs...",
                        status_code,
                        attempt + 1,
                        max_retries + 1,
                        wait,
                    )
                    time.sleep(wait)
                    continue
                raise

            except requests.exceptions.ConnectionError as e:
                last_exception = e
                if attempt < max_retries:
                    wait = backoff_factor ** attempt
                    logger.warning(
                        "Connection error (attempt %d/%d). Retrying in %.1fs...",
                        attempt + 1,
                        max_retries + 1,
                        wait,
                    )
                    time.sleep(wait)
                    continue
                raise

            except requests.exceptions.Timeout as e:
                last_exception = e
                if attempt < max_retries:
                    wait = backoff_factor ** attempt
                    logger.warning(
                        "Timeout (attempt %d/%d). Retrying in %.1fs...",
                        attempt + 1,
                        max_retries + 1,
                        wait,
                    )
                    time.sleep(wait)
                    continue
                raise

        # Should not reach here, but just in case
        if last_exception:
            raise last_exception
        raise MarketoAPIError(message="Retry exhausted with no result")

    return wrapper
