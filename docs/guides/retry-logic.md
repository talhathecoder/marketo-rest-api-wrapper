# Retry Logic

The wrapper automatically retries requests that fail due to transient errors — rate limits, expired tokens, server errors, network timeouts, and connection drops. Non-transient errors (validation, not found, bad request) are raised immediately.

## Retry Behavior Summary

| Error Type | Retried? | Strategy |
|-----------|----------|----------|
| Marketo 601/602 (auth) | Yes | Invalidate token → re-acquire → retry |
| Marketo 606 (rate limit) | Yes | Wait `retry_after` seconds → retry |
| Marketo 607 (daily quota) | No | Raised immediately |
| Marketo 608 (API unavailable) | Yes | Exponential backoff |
| HTTP 429 | Yes | Exponential backoff |
| HTTP 500/502/503/504 | Yes | Exponential backoff |
| Connection error | Yes | Exponential backoff |
| Request timeout | Yes | Exponential backoff |
| HTTP 400/403/404 | No | Raised immediately |
| Validation errors (609, 611, etc.) | No | Raised immediately |

## Exponential Backoff

By default, the wrapper uses a backoff factor of 2.0:

```
Attempt 1: immediate
Attempt 2: wait 2 seconds
Attempt 3: wait 4 seconds
Attempt 4: wait 8 seconds  (if max_retries >= 4)
```

The formula is: `wait = backoff_factor ^ attempt_number`

## Configuration

```python
from marketo_api import MarketoConfig

config = MarketoConfig(
    # ...credentials...
    max_retries=3,             # Default: 3 (total 4 attempts)
    retry_backoff_factor=2.0,  # Default: 2.0
    timeout=30,                # Per-request timeout in seconds
)
```

### Profiles

**Conservative (default):** Good for most production workloads.
```python
config = MarketoConfig(max_retries=3, retry_backoff_factor=2.0, timeout=30)
# Waits: 2s, 4s, 8s — total max wait: 14s
```

**Aggressive:** For batch jobs that need to push through transient errors.
```python
config = MarketoConfig(max_retries=5, retry_backoff_factor=1.5, timeout=60)
# Waits: 1.5s, 2.25s, 3.4s, 5.1s, 7.6s — total max wait: ~20s
```

**Fast-fail:** For real-time applications where latency matters.
```python
config = MarketoConfig(max_retries=1, retry_backoff_factor=1.0, timeout=10)
# Waits: 1s — total max wait: 1s
```

**Bulk operations:** For long-running exports where Marketo may be slow.
```python
config = MarketoConfig(max_retries=3, retry_backoff_factor=3.0, timeout=120)
# Waits: 3s, 9s, 27s — total max wait: 39s
```

## Auth Error Flow

When Marketo returns a 601 or 602 error, the retry logic follows a special path:

```
Request → 601 "Access token invalid"
  └→ Invalidate cached token
  └→ Acquire new token from identity endpoint
  └→ Retry original request with new token
  └→ If still fails → repeat up to max_retries
  └→ If all retries fail → raise MarketoAuthError
```

This handles the common case where a token becomes stale (e.g., Marketo rotated it server-side, or another process consumed all available tokens).

## Rate Limit Error Flow

```
Request → 606 "Max rate limit exceeded"
  └→ Wait retry_after seconds (20s for 606)
  └→ Retry
  └→ If 606 again → wait again → retry
  └→ If max_retries exceeded → raise MarketoRateLimitError

Request → 607 "Daily quota reached"
  └→ Raise MarketoRateLimitError immediately (no retry)
  └→ retry_after = 86400 (24 hours)
```

## Observing Retries

Enable DEBUG logging to see retry behavior:

```python
import logging
logging.getLogger("marketo_api.retry").setLevel(logging.DEBUG)
```

Output:
```
WARNING: Rate limit hit (attempt 1/4). Waiting 20s...
INFO: Auth error (attempt 1/4). Refreshing token...
WARNING: HTTP 503 error (attempt 2/4). Retrying in 4.0s...
WARNING: Timeout (attempt 3/4). Retrying in 8.0s...
```
