# API Reference: Bulk Import

Import large datasets (leads, custom objects) via CSV upload.

**Access:** `client.bulk_import`  
**Marketo docs:** [Bulk Import](https://developers.marketo.com/rest-api/bulk-import/)

---

## Overview

The bulk import API follows a 3-step workflow:

1. **Create job** — Upload a CSV file and configure the import
2. **Poll status** — Monitor the job until it completes
3. **Check results** — Download failures and warnings

Bulk import does **not** count individual records against your API rate limit — only the job management calls (create, status, failures, warnings) count.

---

## Methods

### `create_lead_job(file_path, format, lookup_field, list_id, partition_name) → dict`

Create and upload a bulk lead import job.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file_path` | `str` | *required* | Path to the CSV/TSV file |
| `format` | `str` | `"csv"` | File format: `"csv"`, `"tsv"`, `"ssv"` |
| `lookup_field` | `str` | `"email"` | Deduplication field |
| `list_id` | `int \| None` | `None` | Static list ID to import into |
| `partition_name` | `str \| None` | `None` | Lead partition name |

**Returns:** Job status dict with `batchId`.

**File requirements:**
- Max 10 MB per file
- UTF-8 encoding
- First row must be column headers matching Marketo field API names

```python
job = client.bulk_import.create_lead_job(
    file_path="leads.csv",
    format="csv",
    lookup_field="email"
)
print(f"Job created: batch {job['batchId']}, status: {job['status']}")
```

---

### `get_lead_job_status(batch_id) → dict`

Check the status of a bulk lead import job.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `batch_id` | `int` | *required* | The batch ID from `create_lead_job` |

**Returns:** Job status dict.

**Status values:** `"Queued"`, `"Importing"`, `"Complete"`, `"Failed"`, `"Cancelled"`

```python
status = client.bulk_import.get_lead_job_status(123)
print(f"Status: {status['status']}")
print(f"Rows processed: {status.get('numOfRowsProcessed', 0)}")
print(f"Rows failed: {status.get('numOfRowsFailed', 0)}")
```

---

### `get_lead_job_failures(batch_id) → str`

Download the failure file for a completed import.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `batch_id` | `int` | *required* | The batch ID |

**Returns:** CSV string of failed rows with error reasons.

```python
failures = client.bulk_import.get_lead_job_failures(123)
if failures:
    with open("import_failures.csv", "w") as f:
        f.write(failures)
```

---

### `get_lead_job_warnings(batch_id) → str`

Download the warnings file for a completed import.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `batch_id` | `int` | *required* | The batch ID |

**Returns:** CSV string of rows that imported with warnings.

---

### `create_custom_object_job(api_name, file_path, format) → dict`

Create a bulk custom object import job.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_name` | `str` | *required* | The custom object API name |
| `file_path` | `str` | *required* | Path to the CSV file |
| `format` | `str` | `"csv"` | File format |

**Returns:** Job status dict with `batchId`.

```python
job = client.bulk_import.create_custom_object_job(
    api_name="car_c",
    file_path="cars.csv"
)
```

---

### `poll_until_complete(batch_id, poll_interval, max_wait, object_type) → dict`

Poll a bulk import job until it reaches a terminal state.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `batch_id` | `int` | *required* | The batch ID |
| `poll_interval` | `int` | `30` | Seconds between status checks |
| `max_wait` | `int` | `3600` | Maximum seconds to wait |
| `object_type` | `str` | `"leads"` | `"leads"` or custom object API name |

**Returns:** Final job status dict.

**Raises:** `MarketoBulkOperationError` if the job fails or times out.

```python
status = client.bulk_import.poll_until_complete(
    batch_id=123,
    poll_interval=15,
    max_wait=1800
)
print(f"Imported {status['numOfRowsProcessed']} rows")
```

---

## Full Workflow Example

```python
# 1. Create and upload
job = client.bulk_import.create_lead_job("leads.csv", lookup_field="email")

# 2. Poll until done
status = client.bulk_import.poll_until_complete(job["batchId"])

# 3. Report results
print(f"Processed: {status.get('numOfRowsProcessed', 0)}")
print(f"Created:   {status.get('numOfLeadsCreated', 0)}")
print(f"Updated:   {status.get('numOfLeadsUpdated', 0)}")
print(f"Failed:    {status.get('numOfRowsFailed', 0)}")

# 4. Check failures
failures = client.bulk_import.get_lead_job_failures(job["batchId"])
if failures:
    print(f"\nFailed rows:\n{failures}")
```

---

## Limits

| Limit | Value |
|-------|-------|
| Max file size | 10 MB |
| Max concurrent import jobs | 2 |
| Max rows per file | No hard limit (10 MB constraint) |
| API calls per job | ~3-5 (create + poll + failures + warnings) |
