"""Pagination helpers for Marketo REST API responses.

Marketo uses two pagination styles:
1. Token-based (nextPageToken) — used by lead, activity, and most endpoints
2. Offset-based (offset + maxReturn) — used by some list endpoints

This module provides transparent iteration over paginated results.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Generator, Optional

logger = logging.getLogger("marketo_api.pagination")


def paginate_with_token(
    request_fn: Callable[..., dict[str, Any]],
    endpoint: str,
    params: dict[str, Any] | None = None,
    result_key: str = "result",
    max_pages: int = 100,
    **kwargs: Any,
) -> Generator[dict[str, Any], None, None]:
    """Iterate through token-paginated Marketo results.

    Marketo signals more pages with `"moreResult": true` and provides
    a `nextPageToken` for continuation.

    Args:
        request_fn: The HTTP request function (e.g., client._get).
        endpoint: The API endpoint path.
        params: Query parameters for the request.
        result_key: The key in the response containing the result list.
        max_pages: Safety limit on the number of pages to fetch.
        **kwargs: Additional keyword args passed to request_fn.

    Yields:
        Individual result records from each page.
    """
    params = dict(params) if params else {}
    pages_fetched = 0

    while pages_fetched < max_pages:
        response = request_fn(endpoint, params=params, **kwargs)
        results = response.get(result_key, [])

        for record in results:
            yield record

        pages_fetched += 1

        if not response.get("moreResult", False):
            logger.debug(
                "Pagination complete after %d page(s), endpoint=%s",
                pages_fetched,
                endpoint,
            )
            break

        next_token = response.get("nextPageToken")
        if not next_token:
            logger.warning(
                "moreResult=true but no nextPageToken. Stopping. endpoint=%s",
                endpoint,
            )
            break

        params["nextPageToken"] = next_token
    else:
        logger.warning(
            "Reached max_pages=%d for endpoint=%s. There may be more results.",
            max_pages,
            endpoint,
        )


def paginate_with_offset(
    request_fn: Callable[..., dict[str, Any]],
    endpoint: str,
    params: dict[str, Any] | None = None,
    result_key: str = "result",
    max_return: int = 200,
    max_pages: int = 100,
    **kwargs: Any,
) -> Generator[dict[str, Any], None, None]:
    """Iterate through offset-paginated Marketo results.

    Used by endpoints that accept `offset` and `maxReturn` parameters.

    Args:
        request_fn: The HTTP request function.
        endpoint: The API endpoint path.
        params: Query parameters for the request.
        result_key: The key in the response containing the result list.
        max_return: Number of records per page (Marketo max is usually 200).
        max_pages: Safety limit on the number of pages to fetch.
        **kwargs: Additional keyword args passed to request_fn.

    Yields:
        Individual result records from each page.
    """
    params = dict(params) if params else {}
    params["maxReturn"] = max_return
    offset = params.get("offset", 0)
    pages_fetched = 0

    while pages_fetched < max_pages:
        params["offset"] = offset
        response = request_fn(endpoint, params=params, **kwargs)
        results = response.get(result_key, [])

        for record in results:
            yield record

        pages_fetched += 1

        # If we got fewer results than requested, we've reached the end
        if len(results) < max_return:
            logger.debug(
                "Offset pagination complete after %d page(s), endpoint=%s",
                pages_fetched,
                endpoint,
            )
            break

        offset += max_return
    else:
        logger.warning(
            "Reached max_pages=%d for endpoint=%s. There may be more results.",
            max_pages,
            endpoint,
        )


def collect_all(
    generator: Generator[dict[str, Any], None, None],
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """Collect results from a pagination generator into a list.

    Args:
        generator: A pagination generator from paginate_with_token or
            paginate_with_offset.
        limit: Optional maximum number of records to collect.

    Returns:
        A list of result records.
    """
    results: list[dict[str, Any]] = []
    for record in generator:
        results.append(record)
        if limit and len(results) >= limit:
            break
    return results
