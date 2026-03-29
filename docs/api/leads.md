# API Reference: Leads

CRUD operations on the Marketo lead database.

**Access:** `client.leads`  
**Marketo docs:** [Lead Database — Leads](https://developers.marketo.com/rest-api/lead-database/leads/)

---

## Methods

### `get_by_id(lead_id, fields) → dict | None`

Get a single lead by its Marketo ID.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lead_id` | `int` | *required* | The Marketo lead ID |
| `fields` | `list[str] \| None` | `None` | Field API names to return. If `None`, returns default fields. |

**Returns:** Lead record dict, or `None` if not found.

**Marketo endpoint:** `GET /rest/v1/lead/{id}.json`

```python
lead = client.leads.get_by_id(12345)
lead = client.leads.get_by_id(12345, fields=["email", "firstName", "leadScore"])
```

---

### `get_by_email(email, fields) → dict | None`

Get a single lead by email address.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `email` | `str` | *required* | The lead's email address |
| `fields` | `list[str] \| None` | `None` | Fields to return |

**Returns:** Lead record dict, or `None` if not found.

```python
lead = client.leads.get_by_email("john@example.com")
lead = client.leads.get_by_email("john@example.com", fields=["email", "company", "leadScore"])
```

---

### `get_by_filter(filter_type, filter_values, fields, batch_size) → list[dict]`

Get leads matching a filter. Automatically paginates through all results.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `filter_type` | `str` | *required* | Lead field API name to filter on (e.g., `"email"`, `"company"`, `"id"`) |
| `filter_values` | `list[str]` | *required* | Values to match |
| `fields` | `list[str] \| None` | `None` | Fields to return |
| `batch_size` | `int` | `300` | Results per page (max 300) |

**Returns:** List of matching lead records.

**Marketo endpoint:** `GET /rest/v1/leads.json?filterType=...&filterValues=...`

```python
leads = client.leads.get_by_filter(
    filter_type="company",
    filter_values=["Acme Corp", "Globex"],
    fields=["email", "firstName", "lastName", "company"]
)
```

---

### `get_multiple(lead_ids, fields) → list[dict]`

Get multiple leads by their IDs. Convenience wrapper around `get_by_filter`.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lead_ids` | `list[int]` | *required* | List of Marketo lead IDs |
| `fields` | `list[str] \| None` | `None` | Fields to return |

**Returns:** List of lead records.

```python
leads = client.leads.get_multiple([100, 200, 300], fields=["email", "firstName"])
```

---

### `create_or_update(leads, action, lookup_field, partition_name) → dict`

Create or update leads in the database.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `leads` | `list[dict]` | *required* | Lead records with field values |
| `action` | `str` | `"createOrUpdate"` | One of: `"createOrUpdate"`, `"createOnly"`, `"updateOnly"`, `"createDuplicate"` |
| `lookup_field` | `str` | `"email"` | Field used for deduplication |
| `partition_name` | `str \| None` | `None` | Lead partition name (for partitioned instances) |

**Returns:** API response with `result` array containing status per lead.

**Marketo endpoint:** `POST /rest/v1/leads.json`

```python
result = client.leads.create_or_update(
    leads=[
        {"email": "alice@acme.com", "firstName": "Alice", "company": "Acme"},
        {"email": "bob@globex.com", "firstName": "Bob", "company": "Globex"},
    ],
    action="createOrUpdate",
    lookup_field="email"
)

for item in result["result"]:
    print(f"Lead {item['id']}: {item['status']}")
    # status is one of: "created", "updated", "skipped"
```

**Batch limit:** Up to 300 leads per call.

---

### `delete(leads) → dict`

Delete leads by ID.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `leads` | `list[dict]` | *required* | List of dicts with `"id"` keys |

**Returns:** API response with status per lead.

**Marketo endpoint:** `DELETE /rest/v1/leads.json`

```python
result = client.leads.delete([{"id": 123}, {"id": 456}])
```

---

### `merge(winning_lead_id, losing_lead_ids, merge_in_crm) → dict`

Merge duplicate leads. The winning lead survives; losing leads are merged in and removed.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `winning_lead_id` | `int` | *required* | Lead ID that survives the merge |
| `losing_lead_ids` | `list[int]` | *required* | Lead IDs to merge into the winner |
| `merge_in_crm` | `bool` | `False` | Also merge the corresponding records in the CRM |

**Returns:** API response confirming the merge.

**Marketo endpoint:** `POST /rest/v1/leads/{id}/merge.json`

```python
client.leads.merge(
    winning_lead_id=100,
    losing_lead_ids=[200, 300],
    merge_in_crm=True
)
```

---

### `describe() → list[dict]`

Get the schema for the lead object — all fields, data types, and metadata.

**Returns:** List of field descriptor dicts with keys like `rest.name`, `dataType`, `length`, `rest.readOnly`.

**Marketo endpoint:** `GET /rest/v1/leads/describe.json`

```python
schema = client.leads.describe()
for field in schema:
    print(f"{field['rest']['name']} ({field['dataType']}) — readOnly: {field['rest'].get('readOnly')}")
```

---

### `describe2() → dict`

Get the extended schema (v2) with searchable fields and relationships.

**Returns:** Extended schema dict.

**Marketo endpoint:** `GET /rest/v1/leads/describe2.json`

```python
schema = client.leads.describe2()
searchable = schema.get("searchableFields", [])
```

---

## Return Value Shapes

### Lead Record

```python
{
    "id": 12345,
    "firstName": "John",
    "lastName": "Doe",
    "email": "john@example.com",
    "company": "Acme Corp",
    "leadScore": 85,
    "createdAt": "2025-01-15T10:30:00Z",
    "updatedAt": "2025-03-20T14:22:00Z",
    # ... additional fields based on your `fields` parameter
}
```

### Create/Update Result

```python
{
    "requestId": "abc123",
    "success": True,
    "result": [
        {"id": 100, "status": "created"},
        {"id": 101, "status": "updated"},
        {"id": 0, "status": "skipped", "reasons": [{"code": "1005", "message": "..."}]}
    ]
}
```

### Field Descriptor (from describe)

```python
{
    "id": 1,
    "displayName": "Email Address",
    "dataType": "email",
    "length": 255,
    "rest": {
        "name": "email",
        "readOnly": False
    },
    "soap": {
        "name": "Email",
        "readOnly": False
    }
}
```
