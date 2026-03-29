# API Reference: Campaigns

Trigger and manage Marketo smart campaigns via the API.

**Access:** `client.campaigns`  
**Marketo docs:** [Assets — Smart Campaigns](https://developers.marketo.com/rest-api/assets/smart-campaigns/)

---

## Methods

### `get(campaign_ids, names, program_names, workspace_names, batch_size) → list[dict]`

Get smart campaigns with optional filters. Automatically paginates.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `campaign_ids` | `list[int] \| None` | `None` | Filter by campaign IDs |
| `names` | `list[str] \| None` | `None` | Filter by campaign names |
| `program_names` | `list[str] \| None` | `None` | Filter by parent program names |
| `workspace_names` | `list[str] \| None` | `None` | Filter by workspace names |
| `batch_size` | `int` | `200` | Results per page |

**Returns:** List of campaign records.

**Marketo endpoint:** `GET /rest/v1/campaigns.json`

```python
# All campaigns
campaigns = client.campaigns.get()

# Filter by program
campaigns = client.campaigns.get(program_names=["Q3-Webinar"])

# Specific campaigns
campaigns = client.campaigns.get(campaign_ids=[1001, 1002])
```

---

### `trigger(campaign_id, leads, tokens) → dict`

Trigger (request) a smart campaign for specific leads. The campaign must be set to "Campaign is Requested" trigger.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `campaign_id` | `int` | *required* | The triggerable smart campaign ID |
| `leads` | `list[dict]` | *required* | Lead dicts, e.g., `[{"id": 5}]` |
| `tokens` | `list[dict] \| None` | `None` | My Tokens to override for this execution |

**Returns:** API response confirming the trigger.

**Marketo endpoint:** `POST /rest/v1/campaigns/{id}/trigger.json`

```python
# Simple trigger
client.campaigns.trigger(campaign_id=1001, leads=[{"id": 5}, {"id": 10}])

# With token overrides
client.campaigns.trigger(
    campaign_id=1001,
    leads=[{"id": 5}],
    tokens=[
        {"name": "{{my.discount-code}}", "value": "SAVE20"},
        {"name": "{{my.expiry-date}}", "value": "2025-12-31"}
    ]
)
```

**Limit:** Up to 100 leads per trigger call.

---

### `schedule(campaign_id, run_at, clone_to_program_name, tokens) → dict`

Schedule a batch smart campaign to run at a specific time.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `campaign_id` | `int` | *required* | The batch smart campaign ID |
| `run_at` | `str \| None` | `None` | ISO 8601 datetime for when to run |
| `clone_to_program_name` | `str \| None` | `None` | Clone to a new program before running |
| `tokens` | `list[dict] \| None` | `None` | My Tokens to override |

**Returns:** API response confirming the schedule.

**Marketo endpoint:** `POST /rest/v1/campaigns/{id}/schedule.json`

```python
# Schedule for a specific time
client.campaigns.schedule(
    campaign_id=2001,
    run_at="2025-09-15T09:00:00Z"
)

# Clone and schedule
client.campaigns.schedule(
    campaign_id=2001,
    run_at="2025-09-15T09:00:00Z",
    clone_to_program_name="Q3-Webinar-Sept",
    tokens=[{"name": "{{my.webinar-date}}", "value": "September 15, 2025"}]
)
```

---

## Return Value Shapes

### Campaign Record

```python
{
    "id": 1001,
    "name": "Send Welcome Email",
    "type": "trigger",
    "programId": 500,
    "programName": "Onboarding",
    "workspaceName": "Default",
    "createdAt": "2025-01-01T00:00:00Z",
    "updatedAt": "2025-03-10T12:00:00Z",
    "active": True
}
```
