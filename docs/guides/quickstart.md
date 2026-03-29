# Quick Start

This guide walks through the most common operations in under 5 minutes.

## Initialize the Client

```python
from marketo_api import MarketoClient

client = MarketoClient(
    munchkin_id="123-ABC-456",
    client_id="your-client-id",
    client_secret="your-client-secret"
)
```

Or use environment variables:

```bash
export MARKETO_MUNCHKIN_ID="123-ABC-456"
export MARKETO_CLIENT_ID="your-client-id"
export MARKETO_CLIENT_SECRET="your-client-secret"
```

```python
client = MarketoClient.from_env()
```

## Look Up a Lead

```python
# By email
lead = client.leads.get_by_email("john@example.com")
if lead:
    print(f"{lead['firstName']} {lead['lastName']} — Score: {lead.get('leadScore', 0)}")

# By ID
lead = client.leads.get_by_id(12345)

# By any field
leads = client.leads.get_by_filter(
    filter_type="company",
    filter_values=["Acme Corp"],
    fields=["email", "firstName", "lastName", "leadScore"]
)
```

## Create or Update Leads

```python
result = client.leads.create_or_update(
    leads=[
        {"email": "alice@acme.com", "firstName": "Alice", "company": "Acme"},
        {"email": "bob@globex.com", "firstName": "Bob", "company": "Globex"},
    ],
    action="createOrUpdate",   # also: "createOnly", "updateOnly"
    lookup_field="email"
)

for item in result.get("result", []):
    print(f"Lead {item['id']}: {item['status']}")
```

## Query Activities

```python
# Get recent "New Lead" (type 12) and "Visit Web Page" (type 1) activities
activities = client.activities.get(
    activity_type_ids=[1, 12],
    since_datetime="2025-01-01T00:00:00Z"
)

for act in activities[:10]:
    print(f"Type {act['activityTypeId']} — Lead {act['leadId']} — {act['activityDate']}")
```

## Trigger a Smart Campaign

```python
client.campaigns.trigger(
    campaign_id=1001,
    leads=[{"id": 5}, {"id": 10}],
    tokens=[
        {"name": "{{my.discount-code}}", "value": "SAVE20"}
    ]
)
```

## Work with Static Lists

```python
# Get leads in a list
leads = client.lists.get_leads(list_id=100, fields=["email", "firstName"])

# Add leads to a list
client.lists.add_leads(list_id=100, lead_ids=[5, 10, 15])

# Remove leads from a list
client.lists.remove_leads(list_id=100, lead_ids=[15])
```

## Manage My Tokens

```python
# Get all tokens on a program
tokens = client.tokens.get(folder_id=1001, folder_type="Program")

# Create or update a token
client.tokens.create(
    folder_id=1001,
    folder_type="Program",
    name="{{my.webinar-date}}",
    type="text",
    value="2025-09-15"
)
```

## Check Rate Limit Status

```python
print(f"Daily calls remaining: {client.daily_calls_remaining}")
print(f"Window calls remaining: {client.window_calls_remaining}")
```

## Error Handling

```python
from marketo_api.exceptions import (
    MarketoNotFoundError,
    MarketoRateLimitError,
    MarketoAuthError,
)

try:
    lead = client.leads.get_by_id(99999)
except MarketoNotFoundError:
    print("Lead doesn't exist")
except MarketoRateLimitError as e:
    print(f"Slow down! Retry after {e.retry_after}s")
except MarketoAuthError:
    print("Check your credentials")
```

## Next Steps

- [Configuration](configuration.md) — Fine-tune timeouts, rate limits, retries
- [Bulk Operations Cookbook](bulk-operations.md) — Import/export large datasets
- [API Reference](../api/client.md) — Full method documentation
