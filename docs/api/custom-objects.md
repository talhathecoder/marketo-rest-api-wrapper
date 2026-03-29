# API Reference: Custom Objects

CRUD operations on Marketo custom objects.

**Access:** `client.custom_objects`  
**Marketo docs:** [Lead Database — Custom Objects](https://developers.marketo.com/rest-api/lead-database/custom-objects/)

---

## Methods

### `list_types() → list[dict]`

List all custom object types in the instance.

**Returns:** List of custom object type descriptors.

```python
types = client.custom_objects.list_types()
for t in types:
    print(f"{t['name']} (API name: {t['apiName']})")
```

---

### `describe(api_name) → dict`

Describe a custom object type's schema — fields, relationships, dedupe keys.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_name` | `str` | *required* | The API name (e.g., `"car_c"`) |

**Returns:** Schema descriptor dict.

```python
schema = client.custom_objects.describe("car_c")
for field in schema.get("fields", []):
    print(f"  {field['name']} ({field['dataType']})")
```

---

### `get(api_name, filter_type, filter_values, fields, batch_size) → list[dict]`

Query custom object records. Automatically paginates.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_name` | `str` | *required* | The custom object API name |
| `filter_type` | `str` | *required* | Searchable field to filter on |
| `filter_values` | `list[str]` | *required* | Values to match |
| `fields` | `list[str] \| None` | `None` | Fields to return |
| `batch_size` | `int` | `300` | Results per page (max 300) |

**Returns:** List of matching custom object records.

```python
cars = client.custom_objects.get(
    api_name="car_c",
    filter_type="leadId",
    filter_values=["12345"],
    fields=["make", "model", "year", "vin"]
)
```

---

### `create_or_update(api_name, records, action, dedupe_by) → dict`

Create or update custom object records.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_name` | `str` | *required* | The custom object API name |
| `records` | `list[dict]` | *required* | Records with field values |
| `action` | `str` | `"createOrUpdate"` | `"createOrUpdate"`, `"createOnly"`, `"updateOnly"` |
| `dedupe_by` | `str` | `"dedupeFields"` | `"dedupeFields"` or `"idField"` |

**Returns:** API response with status per record.

**Batch limit:** Up to 300 records per call.

```python
result = client.custom_objects.create_or_update(
    api_name="car_c",
    records=[
        {"leadId": 12345, "vin": "ABC123", "make": "Toyota", "model": "Camry", "year": 2024},
        {"leadId": 12345, "vin": "DEF456", "make": "Honda", "model": "Civic", "year": 2023},
    ]
)
```

---

### `delete(api_name, records, delete_by) → dict`

Delete custom object records.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_name` | `str` | *required* | The custom object API name |
| `records` | `list[dict]` | *required* | Records identifying what to delete |
| `delete_by` | `str` | `"dedupeFields"` | `"dedupeFields"` or `"idField"` |

**Returns:** API response with status per record.

```python
client.custom_objects.delete(
    api_name="car_c",
    records=[{"vin": "ABC123"}],
    delete_by="dedupeFields"
)
```
