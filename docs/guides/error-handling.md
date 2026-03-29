# Error Handling

The wrapper provides a structured exception hierarchy that maps Marketo's error codes to specific Python exceptions. This lets you handle different failure modes precisely.

## Exception Hierarchy

```
MarketoAPIError (base)
├── MarketoAuthError          — 601, 602 (token issues)
├── MarketoRateLimitError     — 606, 607 (throttling)
├── MarketoNotFoundError      — 610, 702 (missing resources)
├── MarketoValidationError    — 609, 611, 612, 1003, 1004 (bad input)
├── MarketoRequestError       — 600, 608, 614 (request-level issues)
└── MarketoBulkOperationError — bulk job failures and timeouts
```

## Exception Attributes

Every exception carries these attributes:

| Attribute | Type | Description |
|-----------|------|-------------|
| `error_code` | `str` | The Marketo error code (e.g., `"601"`) |
| `message` | `str` | Human-readable error message from the API |
| `request_id` | `str` | Marketo's request ID for support tickets |
| `response_data` | `dict` | Full API response payload for inspection |

`MarketoRateLimitError` also has:

| Attribute | Type | Description |
|-----------|------|-------------|
| `retry_after` | `int` | Suggested wait time in seconds (20 for 606, 86400 for 607) |

## Basic Error Handling

```python
from marketo_api import MarketoClient
from marketo_api.exceptions import MarketoAPIError

client = MarketoClient.from_env()

try:
    lead = client.leads.get_by_id(12345)
except MarketoAPIError as e:
    print(f"Error {e.error_code}: {e.message}")
    print(f"Request ID: {e.request_id}")
```

## Granular Error Handling

```python
from marketo_api.exceptions import (
    MarketoAuthError,
    MarketoRateLimitError,
    MarketoNotFoundError,
    MarketoValidationError,
    MarketoRequestError,
    MarketoAPIError,
)

try:
    leads = client.leads.get_by_filter(
        filter_type="email",
        filter_values=["test@example.com"]
    )
except MarketoAuthError as e:
    # Token invalid or expired — retry logic already attempted re-auth
    log.error("Authentication failed after retries: %s", e.message)
    notify_ops_team("Marketo auth failure — check LaunchPoint credentials")

except MarketoRateLimitError as e:
    # 606 (short-term) or 607 (daily quota)
    if e.error_code == "607":
        log.critical("Daily API quota exhausted!")
        schedule_retry_tomorrow()
    else:
        log.warning("Rate limited. Retry after %ds", e.retry_after)
        time.sleep(e.retry_after)

except MarketoNotFoundError:
    # Resource doesn't exist — safe to handle as "no results"
    leads = []

except MarketoValidationError as e:
    # Bad filter type, missing field, invalid value
    log.error("Validation error: %s (code %s)", e.message, e.error_code)
    raise  # Fix the calling code

except MarketoRequestError as e:
    # 608 = API temporarily unavailable
    if e.error_code == "608":
        log.warning("Marketo API temporarily unavailable")
        time.sleep(60)
    else:
        raise

except MarketoAPIError as e:
    # Catch-all for unmapped error codes
    log.error("Unexpected Marketo error: [%s] %s", e.error_code, e.message)
    raise
```

## Error Code Reference

### Authentication Errors

| Code | Exception | Description | Auto-Retry? |
|------|-----------|-------------|-------------|
| 601 | `MarketoAuthError` | Access token missing or invalid | Yes (re-acquires token) |
| 602 | `MarketoAuthError` | Access token expired | Yes (re-acquires token) |

### Rate Limit Errors

| Code | Exception | Description | Auto-Retry? |
|------|-----------|-------------|-------------|
| 606 | `MarketoRateLimitError` | Max rate limit exceeded (100/20s) | Yes (waits `retry_after`) |
| 607 | `MarketoRateLimitError` | Daily quota reached (50k/day) | No (raises immediately) |

### Not Found Errors

| Code | Exception | Description | Auto-Retry? |
|------|-----------|-------------|-------------|
| 610 | `MarketoNotFoundError` | Requested resource not found | No |
| 702 | `MarketoNotFoundError` | Record not found | No |

### Validation Errors

| Code | Exception | Description | Auto-Retry? |
|------|-----------|-------------|-------------|
| 609 | `MarketoValidationError` | Invalid filter type | No |
| 611 | `MarketoValidationError` | Missing required field | No |
| 612 | `MarketoValidationError` | Invalid value | No |
| 1003 | `MarketoValidationError` | Missing required parameter | No |
| 1004 | `MarketoValidationError` | Invalid parameter value | No |

### Request Errors

| Code | Exception | Description | Auto-Retry? |
|------|-----------|-------------|-------------|
| 600 | `MarketoRequestError` | Unsupported method or content type | No |
| 608 | `MarketoRequestError` | API temporarily unavailable | Yes (backoff) |
| 614 | `MarketoRequestError` | Invalid subscription | No |

## HTTP-Level Errors

Network and HTTP errors are also retried automatically:

| Error Type | Auto-Retry? | Behavior |
|-----------|-------------|----------|
| HTTP 429 (Too Many Requests) | Yes | Exponential backoff |
| HTTP 500, 502, 503, 504 | Yes | Exponential backoff |
| Connection errors | Yes | Exponential backoff |
| Timeouts | Yes | Exponential backoff |
| HTTP 4xx (except 429) | No | Raises immediately |

## Bulk Operation Errors

Bulk import/export operations have their own error class:

```python
from marketo_api.exceptions import MarketoBulkOperationError

try:
    status = client.bulk_import.poll_until_complete(batch_id=123)
except MarketoBulkOperationError as e:
    print(f"Bulk job failed: {e.message}")
    print(f"Job details: {e.response_data}")
```

Bulk operation errors include job failures, timeouts (exceeded `max_wait`), and empty responses from job creation endpoints.

## Inspecting the Full Response

Every exception stores the full API response for debugging:

```python
try:
    client.leads.create_or_update([{"email": ""}])
except MarketoAPIError as e:
    # Full response from Marketo
    print(e.response_data)
    # {
    #     "requestId": "abc123",
    #     "success": false,
    #     "errors": [{"code": "1003", "message": "Value for required field 'email' ..."}]
    # }
```

## Using Request IDs for Support

Marketo returns a `requestId` with every response. The wrapper captures this on exceptions so you can include it in support tickets:

```python
except MarketoAPIError as e:
    support_ticket = {
        "error_code": e.error_code,
        "message": e.message,
        "marketo_request_id": e.request_id,  # Send this to Marketo Support
    }
```
