# API Reference: Bulk Extract

Export large datasets (leads, activities) as CSV files.

**Access:** `client.bulk_extract`  
**Marketo docs:** [Bulk Extract](https://developers.marketo.com/rest-api/bulk-extract/)

---

## Overview

The bulk extract API follows a 4-step workflow:

1. **Create job** — Define the fields and filter criteria
2. **Enqueue** — Submit the job for processing
3. **Poll status** — Monitor until the job completes
4. **Download file** — Retrieve the CSV output

Bulk extract is far more efficient than paginating through REST endpoints for large datasets (10k+ records). Each job uses only a handful of API calls regardless of how many records are exported.

---

## Lead Export Methods

### `create_lead_job(fields, filter, format) → dict`

Create a bulk lead export job definition.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `fields` | `list[str]` | *required* | Lead field API names to export |
| `filter` | `dict` | *required* | Filter criteria (see filter examples below) |
| `format` | `str` | `"CSV"` | Output format: `"CSV"` or `"TSV"` |

**Returns:** Job descriptor dict with `exportId`.

**Marketo endpoint:** `POST /bulk/v1/leads/export/create.json`

```python
job = client.bulk_extract.create_lead_job(
    fields=["id", "email", "firstName", "lastName", "createdAt", "company", "leadScore"],
    filter={
        "createdAt": {
            "startAt": "2025-01-01T00:00:00Z",
            "endAt": "2025-07-01T00:00:00Z"
        }
    }
)
export_id = job["exportId"]
```

**Filter examples:**

```python
# By creation date
filter = {
    "createdAt": {
        "startAt": "2025-01-01T00:00:00Z",
        "endAt": "2025-04-01T00:00:00Z"
    }
}

# By update date
filter = {
    "updatedAt": {
        "startAt": "2025-06-01T00:00:00Z",
        "endAt": "2025-06-30T00:00:00Z"
    }
}

# By static list membership
filter = {
    "staticListId": 100
}

# By smart list
filter = {
    "smartListId": 200
}
```

---

### `enqueue_lead_job(export_id) → dict`

Submit a lead export job for processing.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `export_id` | `str` | *required* | The export ID from `create_lead_job` |

**Returns:** Updated job status dict.

**Marketo endpoint:** `POST /bulk/v1/leads/export/{id}/enqueue.json`

```python
client.bulk_extract.enqueue_lead_job(export_id)
```

---

### `get_lead_job_status(export_id) → dict`

Check the status of a lead export job.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `export_id` | `str` | *required* | The export ID |

**Returns:** Job status dict.

**Status values:** `"Created"`, `"Queued"`, `"Processing"`, `"Completed"`, `"Failed"`, `"Cancelled"`

```python
status = client.bulk_extract.get_lead_job_status(export_id)
print(f"Status: {status['status']}, Rows: {status.get('numberOfRows', 'N/A')}")
```

---

### `download_lead_file(export_id) → str`

Download the output file of a completed lead export.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `export_id` | `str` | *required* | The export ID |

**Returns:** CSV/TSV string of exported data.

```python
csv_data = client.bulk_extract.download_lead_file(export_id)
with open("leads_export.csv", "w") as f:
    f.write(csv_data)
```

---

## Activity Export Methods

### `create_activity_job(filter, fields, format) → dict`

Create a bulk activity export job.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `filter` | `dict` | *required* | Filter criteria with `createdAt` range |
| `fields` | `list[str] \| None` | `None` | Activity field names (optional) |
| `format` | `str` | `"CSV"` | Output format |

**Returns:** Job descriptor dict with `exportId`.

```python
job = client.bulk_extract.create_activity_job(
    filter={
        "createdAt": {
            "startAt": "2025-01-01T00:00:00Z",
            "endAt": "2025-02-01T00:00:00Z"
        },
        "activityTypeIds": [1, 2, 6, 7, 10, 11, 12]
    }
)
```

**Common activity type IDs for filtering:**

| ID | Activity |
|----|----------|
| 1 | Visit Web Page |
| 2 | Fill Out Form |
| 6 | Send Email |
| 7 | Email Delivered |
| 8 | Email Bounced |
| 10 | Open Email |
| 11 | Click Email |
| 12 | New Lead |
| 13 | Change Data Value |
| 46 | Interesting Moment |

---

### `enqueue_activity_job(export_id) → dict`

Submit an activity export job for processing.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `export_id` | `str` | *required* | The export ID |

**Returns:** Updated job status dict.

---

### `get_activity_job_status(export_id) → dict`

Check the status of an activity export job.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `export_id` | `str` | *required* | The export ID |

**Returns:** Job status dict.

---

### `download_activity_file(export_id) → str`

Download the output file of a completed activity export.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `export_id` | `str` | *required* | The export ID |

**Returns:** CSV/TSV string of exported activity data.

---

## Convenience Methods

These generic methods dispatch to the correct lead or activity method based on `object_type`.

### `enqueue(export_id, object_type) → dict`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `export_id` | `str` | *required* | The export ID |
| `object_type` | `str` | `"leads"` | `"leads"` or `"activities"` |

### `get_status(export_id, object_type) → dict`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `export_id` | `str` | *required* | The export ID |
| `object_type` | `str` | `"leads"` | `"leads"` or `"activities"` |

### `download_file(export_id, object_type) → str`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `export_id` | `str` | *required* | The export ID |
| `object_type` | `str` | `"leads"` | `"leads"` or `"activities"` |

---

### `poll_until_complete(export_id, object_type, poll_interval, max_wait) → dict`

Poll an export job until it reaches a terminal state.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `export_id` | `str` | *required* | The export ID |
| `object_type` | `str` | `"leads"` | `"leads"` or `"activities"` |
| `poll_interval` | `int` | `30` | Seconds between status checks |
| `max_wait` | `int` | `7200` | Maximum seconds to wait (default: 2 hours) |

**Returns:** Final job status dict.

**Raises:** `MarketoBulkOperationError` if the job fails or times out.

```python
status = client.bulk_extract.poll_until_complete(
    export_id,
    object_type="leads",
    poll_interval=15,
    max_wait=3600
)
```

---

## Full Workflow Example

```python
# 1. Create the export job
job = client.bulk_extract.create_lead_job(
    fields=["id", "email", "firstName", "lastName", "createdAt"],
    filter={
        "createdAt": {
            "startAt": "2025-01-01T00:00:00Z",
            "endAt": "2025-07-01T00:00:00Z"
        }
    }
)
export_id = job["exportId"]
print(f"Created job: {export_id}")

# 2. Enqueue for processing
client.bulk_extract.enqueue(export_id)
print("Job enqueued")

# 3. Poll until complete
status = client.bulk_extract.poll_until_complete(export_id, poll_interval=15)
print(f"Completed: {status.get('numberOfRows', 0)} rows, {status.get('fileSize', 0)} bytes")

# 4. Download the file
csv_data = client.bulk_extract.download_file(export_id)
with open("export.csv", "w", encoding="utf-8") as f:
    f.write(csv_data)
print("Saved to export.csv")
```

---

## Limits

| Limit | Value |
|-------|-------|
| Max concurrent export jobs | 2 |
| Max date range per job | 31 days |
| Max queued jobs | 10 |
| Max file retention | 12 days after completion |
| API calls per job | ~4 (create + enqueue + poll + download) |
| Daily export quota | 500 MB total file size |

---

## Tips

- **Date range:** Each job can span a maximum of 31 days. For longer ranges, create multiple jobs with sequential date windows.
- **Polling interval:** Start with 30 seconds. For jobs expected to return millions of rows, increase to 60 seconds to avoid unnecessary API calls.
- **File size:** Large exports can produce files of several hundred MB. Ensure you have sufficient disk space and memory before calling `download_file`.
- **Use over REST pagination:** If you need more than ~10,000 records, bulk extract is significantly more efficient than paginated REST queries.
