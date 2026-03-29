# Authentication

The wrapper handles Marketo's OAuth 2.0 `client_credentials` flow automatically. You never need to manually acquire or refresh tokens — the `MarketoAuth` class manages this behind the scenes.

## How It Works

1. **First API call** — The client detects no valid token exists and requests one from `https://{munchkin_id}.mktorest.com/identity/oauth/token`
2. **Token caching** — The token is cached in memory and reused for subsequent requests
3. **Auto-refresh** — Before each request, the client checks if the token will expire within `token_refresh_buffer` seconds (default: 60). If so, it acquires a new one transparently
4. **Retry on auth error** — If Marketo returns error code `601` (invalid token) or `602` (expired token), the retry logic invalidates the cached token, acquires a new one, and replays the request

## Token Lifecycle

```
Request #1 ──→ No token → Acquire token (expires in 3600s) → Make API call
Request #2 ──→ Token valid → Make API call (no auth overhead)
   ...
Request #N ──→ Token expires in <60s → Acquire new token → Make API call
Request #N+1 → Marketo returns 601 → Invalidate → Re-acquire → Retry
```

## Configuration

The only auth-related setting you might want to tune is the refresh buffer:

```python
from marketo_api import MarketoConfig

config = MarketoConfig(
    # ...credentials...
    token_refresh_buffer=120,  # Refresh 2 minutes before expiry instead of 1
)
```

This is useful if you have long-running operations (bulk exports, large paginated queries) where a token might expire mid-operation.

## Marketo Token Details

| Property | Value |
|----------|-------|
| Grant type | `client_credentials` |
| Token endpoint | `https://{munchkin_id}.mktorest.com/identity/oauth/token` |
| Token lifetime | 3600 seconds (1 hour) |
| Token type | Bearer |
| Concurrent tokens | Up to 10 per service |

## Multiple Instances

Each `MarketoClient` instance manages its own token independently. You can safely create multiple clients for different Marketo subscriptions:

```python
client_prod = MarketoClient(
    munchkin_id="111-AAA-111",
    client_id="prod-id",
    client_secret="prod-secret"
)

client_sandbox = MarketoClient(
    munchkin_id="222-BBB-222",
    client_id="sandbox-id",
    client_secret="sandbox-secret"
)
```

## Troubleshooting

### Error 601: Access token missing or invalid

**Causes:**
- Incorrect `client_id` or `client_secret`
- LaunchPoint service was deleted or disabled
- API-only user was deactivated

**Fix:** Verify your credentials in Admin → Integration → LaunchPoint. The wrapper will automatically retry once with a fresh token before raising `MarketoAuthError`.

### Error 602: Access token expired

This is handled automatically by the retry logic. If you see this error bubble up, it means all retry attempts failed. This typically indicates a configuration issue rather than a timing problem.

### Token Endpoint Returns HTML

If the identity endpoint returns HTML instead of JSON, your `munchkin_id` is likely incorrect. Double-check it matches the format `XXX-XXX-XXX`.

### Rate Limits on Token Requests

Token requests count toward your API rate limits. The wrapper minimizes token requests by caching and pre-emptive refresh, but if you're creating many short-lived `MarketoClient` instances, consider sharing a single instance instead.
