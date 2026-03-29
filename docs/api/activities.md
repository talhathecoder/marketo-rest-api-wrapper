# API Reference: Activities

Query lead activity logs from the Marketo activity stream.

**Access:** `client.activities`  
**Marketo docs:** [Lead Database — Activities](https://developers.marketo.com/rest-api/lead-database/activities/)

---

## Methods

### `get(activity_type_ids, since_datetime, next_page_token, lead_ids, batch_size, collect) → list[dict]`

Get lead activities with filters.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `activity_type_ids` | `list[int]` | *required* | Activity type IDs to filter |
| `since_datetime` | `str \| None` | `None` | ISO 8601 datetime to start from |
| `next_page_token` | `str \| None` | `None` | Existing paging token (overrides `since_datetime`) |
| `lead_ids` | `list[int] \| None` | `None` | Filter to specific leads |
| `batch_size` | `int` | `300` | Results per page (max 300) |
| `collect` | `bool` | `True` | If `True`, collects all pages. If `False`, returns first page only. |

**Returns:** List of activity records.

**Marketo endpoint:** `GET /rest/v1/activities.json`

```python
# All "New Lead" and "Visit Web Page" activities since Jan 1
activities = client.activities.get(
    activity_type_ids=[1, 12],
    since_datetime="2025-01-01T00:00:00Z"
)

# Activities for specific leads
activities = client.activities.get(
    activity_type_ids=[1],
    since_datetime="2025-06-01T00:00:00Z",
    lead_ids=[100, 200, 300]
)

# First page only (for sampling)
first_page = client.activities.get(
    activity_type_ids=[1, 12],
    since_datetime="2025-01-01T00:00:00Z",
    collect=False
)
```

**Note:** Either `since_datetime` or `next_page_token` is required. If both are provided, `next_page_token` takes precedence.

---

### `get_types() → list[dict]`

Get all available activity types in the Marketo instance.

**Returns:** List of activity type descriptors.

**Marketo endpoint:** `GET /rest/v1/activities/types.json`

```python
types = client.activities.get_types()
for t in types:
    print(f"{t['id']}: {t['name']}")
```

**Common activity types:**

| ID | Name |
|----|------|
| 1 | Visit Web Page |
| 2 | Fill Out Form |
| 3 | Click Link |
| 6 | Send Email |
| 7 | Email Delivered |
| 8 | Email Bounced |
| 9 | Unsubscribe Email |
| 10 | Open Email |
| 11 | Click Email |
| 12 | New Lead |
| 13 | Change Data Value |
| 46 | Interesting Moment |

---

### `get_paging_token(since_datetime) → str`

Get a paging token for activity queries. You generally don't need to call this directly — `get()` handles it automatically.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `since_datetime` | `str` | *required* | ISO 8601 datetime string |

**Returns:** Paging token string.

**Marketo endpoint:** `GET /rest/v1/activities/pagingtoken.json`

```python
token = client.activities.get_paging_token("2025-01-01T00:00:00Z")
```

---

## Return Value Shapes

### Activity Record

```python
{
    "id": 987654,
    "leadId": 12345,
    "activityDate": "2025-03-15T14:30:00Z",
    "activityTypeId": 1,
    "primaryAttributeValueId": 100,
    "primaryAttributeValue": "https://example.com/page",
    "attributes": [
        {"name": "Web Page", "value": "https://example.com/page"},
        {"name": "Referrer URL", "value": "https://google.com"},
        {"name": "Client IP Address", "value": "192.168.1.1"},
        {"name": "User Agent", "value": "Mozilla/5.0 ..."}
    ]
}
```

### Activity Type Descriptor

```python
{
    "id": 1,
    "name": "Visit Web Page",
    "description": "User visits a web page tracked by Munchkin",
    "primaryAttribute": {
        "name": "Web Page",
        "dataType": "string"
    },
    "attributes": [
        {"name": "Referrer URL", "dataType": "string"},
        {"name": "Client IP Address", "dataType": "string"},
        {"name": "User Agent", "dataType": "string"},
        {"name": "Query Parameters", "dataType": "string"}
    ]
}
```
