# Marketo REST API Wrapper

A comprehensive, production-ready Python wrapper for the [Marketo REST API](https://developers.marketo.com/rest-api/) with built-in authentication management, automatic rate limiting, pagination handling, retry logic, and structured error reporting.

Built by a certified Adobe Marketo Engage Architect Master & Business Practitioner Expert.

---

## Features

- **Auto-authentication** — Handles OAuth 2.0 token acquisition and automatic refresh before expiry
- **Rate limiting** — Respects Marketo's 100 calls/20s and 50,000 calls/day limits with configurable backoff
- **Pagination** — Transparent cursor-based and offset-based pagination across all list endpoints
- **Bulk operations** — Full support for Bulk Import and Bulk Extract APIs with job polling
- **Retry logic** — Configurable exponential backoff for transient errors (5xx, 429, network timeouts)
- **Structured errors** — Custom exception hierarchy mapping Marketo error codes to meaningful Python exceptions
- **Logging** — Built-in structured logging with configurable verbosity
- **Type hints** — Full type annotations for IDE autocompletion and static analysis
- **Resource-based API** — Clean, intuitive interface organized by Marketo object type

## Installation

```bash
pip install marketo-rest-api-wrapper
```

Or install from source:

```bash
git clone https://github.com/talhathecoder/marketo-rest-api-wrapper.git
cd marketo-rest-api-wrapper
pip install -e .
```

## Quick Start

```python
from marketo_api import MarketoClient

# Initialize the client
client = MarketoClient(
    munchkin_id="123-ABC-456",
    client_id="your-client-id",
    client_secret="your-client-secret"
)

# Get a lead by email
lead = client.leads.get_by_email("john@example.com")
print(lead)

# Create or update leads
result = client.leads.create_or_update([
    {"email": "new@example.com", "firstName": "Jane", "lastName": "Doe"}
])

# Get lead activities
activities = client.activities.get(
    activity_type_ids=[1, 12],
    since_datetime="2025-01-01T00:00:00Z"
)

# Run a smart campaign
client.campaigns.trigger(campaign_id=1001, leads=[{"id": 5}])
```

## Configuration

```python
from marketo_api import MarketoClient, MarketoConfig

config = MarketoConfig(
    munchkin_id="123-ABC-456",
    client_id="your-client-id",
    client_secret="your-client-secret",
    max_retries=3,
    retry_backoff_factor=2.0,
    timeout=30,
    rate_limit_calls_per_20s=80,   # stay under the 100/20s hard limit
    rate_limit_daily_max=45000,    # stay under the 50k/day hard limit
    log_level="INFO"
)

client = MarketoClient(config=config)
```

### Environment Variables

You can also configure via environment variables:

```bash
export MARKETO_MUNCHKIN_ID="123-ABC-456"
export MARKETO_CLIENT_ID="your-client-id"
export MARKETO_CLIENT_SECRET="your-client-secret"
```

```python
client = MarketoClient.from_env()
```

## API Resources

| Resource | Description | Key Methods |
|----------|-------------|-------------|
| `client.leads` | Lead database operations | `get_by_id`, `get_by_email`, `create_or_update`, `delete`, `merge`, `describe` |
| `client.activities` | Activity log queries | `get`, `get_types`, `get_paging_token` |
| `client.campaigns` | Smart campaign triggers | `get`, `trigger`, `schedule`, `request` |
| `client.programs` | Program management | `get`, `create`, `update`, `clone`, `get_members` |
| `client.lists` | Static list operations | `get`, `get_leads`, `add_leads`, `remove_leads` |
| `client.folders` | Folder tree navigation | `get`, `get_by_name`, `create`, `get_contents` |
| `client.tokens` | Program tokens (My Tokens) | `get`, `create`, `delete` |
| `client.custom_objects` | Custom object CRUD | `get`, `describe`, `create_or_update`, `delete` |
| `client.bulk_import` | Bulk lead/CO import | `create_job`, `upload_file`, `enqueue`, `get_status` |
| `client.bulk_extract` | Bulk lead/activity export | `create_job`, `enqueue`, `get_status`, `download_file` |

## Detailed Examples

### Leads

```python
# Get lead by ID with specific fields
lead = client.leads.get_by_id(12345, fields=["email", "firstName", "lastName", "score"])

# Search leads by filter
leads = client.leads.get_by_filter(
    filter_type="company",
    filter_values=["Acme Corp", "Globex"],
    fields=["email", "firstName", "company", "leadScore"]
)

# Upsert leads with lookup field
client.leads.create_or_update(
    leads=[
        {"email": "a@test.com", "firstName": "Alice", "company": "Acme"},
        {"email": "b@test.com", "firstName": "Bob", "company": "Globex"}
    ],
    action="createOrUpdate",
    lookup_field="email"
)

# Describe the lead object (fields, data types)
schema = client.leads.describe()
for field in schema:
    print(f"{field['name']} ({field['dataType']})")
```

### Bulk Extract

```python
# Create and run a bulk lead extract
job = client.bulk_extract.create_lead_job(
    fields=["id", "email", "firstName", "lastName", "createdAt"],
    filter={
        "createdAt": {
            "startAt": "2025-01-01T00:00:00Z",
            "endAt": "2025-06-01T00:00:00Z"
        }
    }
)

# Enqueue and poll until complete
client.bulk_extract.enqueue(job["exportId"])
status = client.bulk_extract.poll_until_complete(job["exportId"], poll_interval=30)

# Download results as CSV
csv_data = client.bulk_extract.download_file(job["exportId"])
```

### Bulk Import

```python
# Import leads from a CSV file
job = client.bulk_import.create_lead_job(
    file_path="leads_to_import.csv",
    format="csv",
    lookup_field="email",
    partition_name="Default"
)

# Poll until complete
status = client.bulk_import.poll_until_complete(job["batchId"])
print(f"Imported: {status['numOfRowsProcessed']} rows, "
      f"Failed: {status['numOfRowsFailed']}")
```

### Programs & Tokens

```python
# Get all programs in a workspace
programs = client.programs.get(max_return=200, status="active")

# Clone a program
clone = client.programs.clone(
    program_id=1001,
    name="Q3-Webinar-Clone",
    folder={"id": 50, "type": "Folder"}
)

# Manage My Tokens
client.tokens.create(
    folder_id=1001,
    folder_type="Program",
    name="{{my.event-date}}",
    type="text",
    value="2025-09-15"
)
```

## Error Handling

```python
from marketo_api.exceptions import (
    MarketoAuthError,
    MarketoRateLimitError,
    MarketoNotFoundError,
    MarketoAPIError
)

try:
    lead = client.leads.get_by_id(99999)
except MarketoNotFoundError:
    print("Lead not found")
except MarketoRateLimitError as e:
    print(f"Rate limited — retry after {e.retry_after}s")
except MarketoAuthError:
    print("Authentication failed — check credentials")
except MarketoAPIError as e:
    print(f"API error {e.error_code}: {e.message}")
```

## Rate Limiting Details

Marketo enforces two rate limit tiers:

| Limit | Threshold | Wrapper Behavior |
|-------|-----------|-----------------|
| Short-term | 100 calls / 20 seconds | Pre-emptive throttling with sliding window |
| Daily | 50,000 calls / day | Tracks count, raises warning at 90% |

The wrapper handles both transparently. You can customize thresholds in the config.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License — see [LICENSE](LICENSE) for details.
