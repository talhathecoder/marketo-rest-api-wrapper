# Configuration

The `MarketoConfig` class controls all client behavior — credentials, timeouts, rate limits, retry logic, and logging. You can configure via constructor arguments, a config object, or environment variables.

## Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `munchkin_id` | `str` | *required* | Your Marketo Munchkin Account ID (e.g., `"123-ABC-456"`) |
| `client_id` | `str` | *required* | OAuth 2.0 Client ID from LaunchPoint |
| `client_secret` | `str` | *required* | OAuth 2.0 Client Secret from LaunchPoint |
| `max_retries` | `int` | `3` | Max retry attempts for transient errors |
| `retry_backoff_factor` | `float` | `2.0` | Multiplier for exponential backoff (1s, 2s, 4s, ...) |
| `timeout` | `int` | `30` | HTTP request timeout in seconds |
| `rate_limit_calls_per_20s` | `int` | `80` | Pre-emptive throttle for the 100/20s hard limit |
| `rate_limit_daily_max` | `int` | `45000` | Pre-emptive throttle for the 50k/day hard limit |
| `daily_warning_threshold` | `float` | `0.9` | Log a warning when daily usage exceeds this fraction |
| `log_level` | `str` | `"INFO"` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `token_refresh_buffer` | `int` | `60` | Seconds before token expiry to trigger a refresh |

## Method 1: Direct Arguments

The simplest approach — pass credentials directly to `MarketoClient`:

```python
from marketo_api import MarketoClient

client = MarketoClient(
    munchkin_id="123-ABC-456",
    client_id="your-client-id",
    client_secret="your-client-secret"
)
```

This uses all default settings for retries, timeouts, and rate limits.

## Method 2: Config Object

For full control, create a `MarketoConfig` and pass it to the client:

```python
from marketo_api import MarketoClient, MarketoConfig

config = MarketoConfig(
    munchkin_id="123-ABC-456",
    client_id="your-client-id",
    client_secret="your-client-secret",

    # Retry behavior
    max_retries=5,
    retry_backoff_factor=1.5,
    timeout=60,

    # Rate limiting — stay well under Marketo's hard limits
    rate_limit_calls_per_20s=60,     # hard limit is 100
    rate_limit_daily_max=40000,      # hard limit is 50,000
    daily_warning_threshold=0.85,    # warn at 85% usage

    # Auth
    token_refresh_buffer=120,        # refresh token 2 min before expiry

    # Logging
    log_level="DEBUG",
)

client = MarketoClient(config=config)
```

## Method 3: Environment Variables

Ideal for deployments, CI/CD, and containers:

```bash
# Required
export MARKETO_MUNCHKIN_ID="123-ABC-456"
export MARKETO_CLIENT_ID="your-client-id"
export MARKETO_CLIENT_SECRET="your-client-secret"

# Optional overrides
export MARKETO_MAX_RETRIES="5"
export MARKETO_TIMEOUT="60"
export MARKETO_LOG_LEVEL="DEBUG"
```

```python
client = MarketoClient.from_env()
```

## Using a `.env` File

With [python-dotenv](https://pypi.org/project/python-dotenv/):

```bash
pip install python-dotenv
```

Create a `.env` file (add to `.gitignore`!):

```
MARKETO_MUNCHKIN_ID=123-ABC-456
MARKETO_CLIENT_ID=your-client-id
MARKETO_CLIENT_SECRET=your-client-secret
MARKETO_LOG_LEVEL=DEBUG
```

```python
from dotenv import load_dotenv
from marketo_api import MarketoClient

load_dotenv()
client = MarketoClient.from_env()
```

## Tuning Rate Limits

Marketo enforces two rate limit tiers:

| Tier | Hard Limit | Default Wrapper Setting | Recommendation |
|------|-----------|------------------------|----------------|
| Short-term | 100 calls / 20 seconds | 80 / 20s | Leave headroom for other integrations |
| Daily | 50,000 calls / day | 45,000 / day | Reserve 5k for UI users and other services |

If your Marketo instance has no other API integrations, you can safely increase these closer to the hard limits:

```python
config = MarketoConfig(
    # ...credentials...
    rate_limit_calls_per_20s=95,
    rate_limit_daily_max=49000,
)
```

If you share the API quota with Salesforce sync, webhooks, or other integrations, lower them accordingly.

## Tuning Retries

The default retry strategy uses exponential backoff with a factor of 2.0:

| Attempt | Wait Time |
|---------|-----------|
| 1st retry | 2 seconds |
| 2nd retry | 4 seconds |
| 3rd retry | 8 seconds |

For high-throughput batch jobs, you may want faster retries:

```python
config = MarketoConfig(
    # ...
    max_retries=5,
    retry_backoff_factor=1.0,  # 1s, 1s, 1s, 1s, 1s
)
```

For long-running bulk exports, increase the timeout:

```python
config = MarketoConfig(
    # ...
    timeout=120,  # 2 minutes per request
)
```

## Logging

The wrapper uses Python's standard `logging` module under the `marketo_api` namespace. Set the log level via config:

```python
config = MarketoConfig(log_level="DEBUG")
```

Log namespaces you can configure individually:

| Logger Name | What It Logs |
|-------------|-------------|
| `marketo_api` | Top-level client events |
| `marketo_api.auth` | Token acquisition and refresh |
| `marketo_api.transport` | Every HTTP request and response |
| `marketo_api.rate_limiter` | Throttling events and daily counter resets |
| `marketo_api.retry` | Retry attempts and backoff waits |
| `marketo_api.pagination` | Page fetches and completion |
| `marketo_api.bulk_import` | Bulk import job status polling |
| `marketo_api.bulk_extract` | Bulk export job status polling |

Example — silence transport noise but keep auth visible:

```python
import logging

logging.getLogger("marketo_api.transport").setLevel(logging.WARNING)
logging.getLogger("marketo_api.auth").setLevel(logging.DEBUG)
```

## Accessing Config at Runtime

```python
client = MarketoClient.from_env()

print(client.config.munchkin_id)
print(client.config.base_url)
print(client.config.max_retries)
print(client.daily_calls_remaining)
print(client.window_calls_remaining)
```
