# Rate Limiting

Marketo enforces two tiers of API rate limits. The wrapper handles both transparently so you never need to manually throttle your code.

## Marketo's Rate Limits

| Tier | Hard Limit | Reset Window | Consequence |
|------|-----------|-------------|-------------|
| Short-term | 100 calls per 20 seconds | Rolling 20-second window | HTTP 606 error |
| Daily | 50,000 calls per day | Midnight CT (Central Time) | HTTP 607 error |

## How the Wrapper Handles It

### Pre-emptive Throttling (Sliding Window)

Before every API call, the `RateLimiter` checks a sliding window of recent calls. If the window is full, it **sleeps** until there's room — your code blocks but never gets a 606 error.

```
Call 1   ──→ Window: [1/80] → Proceed
Call 2   ──→ Window: [2/80] → Proceed
  ...
Call 80  ──→ Window: [80/80] → FULL → Sleep 2.3s → Proceed
Call 81  ──→ Window: [43/80] → Proceed (old calls fell off the window)
```

### Daily Quota Tracking

The wrapper tracks a running daily counter. When the counter hits the configured maximum, it raises a `RuntimeError` immediately rather than burning an API call on a guaranteed 607.

At 90% usage (configurable), it logs a warning:

```
WARNING: Approaching daily API limit: 40500 / 45000 calls used (90%)
```

### Reactive Rate Limit Handling

If Marketo returns a 606 or 607 despite pre-emptive throttling (e.g., another integration consumed quota), the retry logic handles it:

- **606** — Waits 20 seconds and retries
- **607** — Raises `MarketoRateLimitError` with `retry_after=86400` (no retry — daily limit is exhausted)

## Configuration

```python
from marketo_api import MarketoConfig

config = MarketoConfig(
    # ...credentials...

    # Short-term: stay under the 100/20s hard limit
    rate_limit_calls_per_20s=80,     # Default: 80

    # Daily: stay under the 50k/day hard limit
    rate_limit_daily_max=45000,      # Default: 45,000

    # Warn when daily usage crosses this threshold
    daily_warning_threshold=0.9,     # Default: 0.9 (90%)
)
```

### Choosing Your Limits

| Scenario | `calls_per_20s` | `daily_max` | Rationale |
|----------|----------------|-------------|-----------|
| **Solo integration** (only API consumer) | 90–95 | 48,000 | Max throughput, small buffer |
| **Shared with Salesforce sync** | 60–70 | 35,000 | Sync uses ~30% of quota |
| **Multiple integrations** | 40–50 | 25,000 | Split quota across consumers |
| **Conservative / production** | 80 (default) | 45,000 (default) | Safe for most cases |

## Monitoring Usage

Check remaining quota at any time:

```python
client = MarketoClient.from_env()

# How many calls left in the current 20-second window?
print(client.window_calls_remaining)  # e.g., 73

# How many calls left today?
print(client.daily_calls_remaining)   # e.g., 42,150
```

## Thread Safety

The rate limiter is thread-safe. If you're making concurrent API calls from multiple threads, they'll all share the same rate limiter and collectively stay within limits:

```python
import threading

client = MarketoClient.from_env()

def process_batch(lead_ids):
    # Each thread's calls go through the same rate limiter
    for lid in lead_ids:
        lead = client.leads.get_by_id(lid)
        process(lead)

threads = [
    threading.Thread(target=process_batch, args=(batch,))
    for batch in chunked_ids
]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

## Tips for Minimizing API Calls

1. **Use batch endpoints** — `get_by_filter` with multiple values instead of individual `get_by_id` calls
2. **Request only needed fields** — Pass `fields=["email", "firstName"]` instead of fetching all fields
3. **Use bulk APIs for large data sets** — Bulk extract/import are far more efficient than individual REST calls
4. **Cache lead schemas** — Call `client.leads.describe()` once and reuse the result
5. **Paginate wisely** — Use `batch_size=300` (max) to minimize page fetches
