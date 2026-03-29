# API Reference: MarketoClient

The main entry point for the Marketo REST API wrapper. Provides access to all resources and manages authentication, rate limiting, and retries.

**Import:**
```python
from marketo_api import MarketoClient
```

---

## Constructor

### `MarketoClient(munchkin_id, client_id, client_secret, config)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `munchkin_id` | `str` | `""` | Marketo Munchkin Account ID |
| `client_id` | `str` | `""` | OAuth 2.0 Client ID |
| `client_secret` | `str` | `""` | OAuth 2.0 Client Secret |
| `config` | `MarketoConfig \| None` | `None` | Full config object (overrides individual params) |

```python
# Simple
client = MarketoClient(
    munchkin_id="123-ABC-456",
    client_id="your-id",
    client_secret="your-secret"
)

# With config
from marketo_api import MarketoConfig
config = MarketoConfig(munchkin_id="123-ABC-456", client_id="id", client_secret="secret", max_retries=5)
client = MarketoClient(config=config)
```

---

## Class Methods

### `MarketoClient.from_env() → MarketoClient`

Create a client from environment variables.

**Required env vars:** `MARKETO_MUNCHKIN_ID`, `MARKETO_CLIENT_ID`, `MARKETO_CLIENT_SECRET`

```python
client = MarketoClient.from_env()
```

---

## Properties

### `client.config → MarketoConfig`
Access the client's configuration object.

### `client.daily_calls_remaining → int`
Number of API calls remaining for the current day.

### `client.window_calls_remaining → int`
Number of API calls remaining in the current 20-second window.

---

## Resources

All API operations are accessed through resource attributes:

| Attribute | Type | Reference |
|-----------|------|-----------|
| `client.leads` | `LeadsResource` | [leads.md](leads.md) |
| `client.activities` | `ActivitiesResource` | [activities.md](activities.md) |
| `client.campaigns` | `CampaignsResource` | [campaigns.md](campaigns.md) |
| `client.programs` | `ProgramsResource` | [programs.md](programs.md) |
| `client.lists` | `ListsResource` | [lists.md](lists.md) |
| `client.folders` | `FoldersResource` | [folders.md](folders.md) |
| `client.tokens` | `TokensResource` | [tokens.md](tokens.md) |
| `client.custom_objects` | `CustomObjectsResource` | [custom-objects.md](custom-objects.md) |
| `client.bulk_import` | `BulkImportResource` | [bulk-import.md](bulk-import.md) |
| `client.bulk_extract` | `BulkExtractResource` | [bulk-extract.md](bulk-extract.md) |
