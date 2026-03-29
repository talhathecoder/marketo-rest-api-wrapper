# Bulk Operations Cookbook

Practical patterns for handling large-scale data operations with the Marketo API.

---

## When to Use Bulk vs REST

| Scenario | Use | Why |
|----------|-----|-----|
| Look up 1–50 leads | REST (`get_by_filter`) | Immediate response, no job overhead |
| Export 1k–10k leads | REST with pagination | Simpler code, fast enough |
| Export 10k–1M leads | Bulk Extract | Fewer API calls, no rate limit pressure |
| Import 1–300 leads | REST (`create_or_update`) | Single call, instant |
| Import 300–500k leads | Bulk Import | File upload, async processing |

---

## Recipe: Export All Leads Created This Quarter

```python
from marketo_api import MarketoClient

client = MarketoClient.from_env()

# Create job for Q1 2025
job = client.bulk_extract.create_lead_job(
    fields=["id", "email", "firstName", "lastName", "company",
            "leadScore", "createdAt", "leadSource"],
    filter={
        "createdAt": {
            "startAt": "2025-01-01T00:00:00Z",
            "endAt": "2025-04-01T00:00:00Z"
        }
    }
)

# Enqueue and wait
client.bulk_extract.enqueue(job["exportId"])
status = client.bulk_extract.poll_until_complete(job["exportId"], poll_interval=15)

# Save to file
csv_data = client.bulk_extract.download_file(job["exportId"])
with open("q1_leads.csv", "w") as f:
    f.write(csv_data)

print(f"Exported {status.get('numberOfRows', 0)} leads")
```

---

## Recipe: Export a Full Year (Handling 31-Day Limit)

Bulk extract jobs are limited to 31-day windows. For longer ranges, chain multiple jobs:

```python
from datetime import datetime, timedelta

client = MarketoClient.from_env()

start = datetime(2025, 1, 1)
end = datetime(2026, 1, 1)
all_csv_parts = []

current = start
while current < end:
    window_end = min(current + timedelta(days=30), end)

    job = client.bulk_extract.create_lead_job(
        fields=["id", "email", "firstName", "lastName", "createdAt"],
        filter={
            "createdAt": {
                "startAt": current.strftime("%Y-%m-%dT00:00:00Z"),
                "endAt": window_end.strftime("%Y-%m-%dT00:00:00Z"),
            }
        },
    )

    client.bulk_extract.enqueue(job["exportId"])
    status = client.bulk_extract.poll_until_complete(job["exportId"])

    csv_part = client.bulk_extract.download_file(job["exportId"])
    all_csv_parts.append(csv_part)

    print(f"  {current.date()} → {window_end.date()}: {status.get('numberOfRows', 0)} rows")
    current = window_end

# Combine all parts (skip header row on subsequent parts)
lines = all_csv_parts[0].splitlines()
for part in all_csv_parts[1:]:
    lines.extend(part.splitlines()[1:])  # Skip header

with open("full_year_leads.csv", "w") as f:
    f.write("\n".join(lines))
```

---

## Recipe: Bulk Import with Error Reporting

```python
from marketo_api import MarketoClient
from marketo_api.exceptions import MarketoBulkOperationError

client = MarketoClient.from_env()

try:
    # Upload the file
    job = client.bulk_import.create_lead_job(
        file_path="new_leads.csv",
        lookup_field="email",
        partition_name="Default"
    )
    batch_id = job["batchId"]
    print(f"Import job created: {batch_id}")

    # Wait for completion
    status = client.bulk_import.poll_until_complete(batch_id, poll_interval=10)

    # Report
    print(f"\n--- Import Results ---")
    print(f"Rows processed: {status.get('numOfRowsProcessed', 0)}")
    print(f"Leads created:  {status.get('numOfLeadsCreated', 0)}")
    print(f"Leads updated:  {status.get('numOfLeadsUpdated', 0)}")
    print(f"Rows failed:    {status.get('numOfRowsFailed', 0)}")

    # Save failures for review
    failures = client.bulk_import.get_lead_job_failures(batch_id)
    if failures:
        with open("import_failures.csv", "w") as f:
            f.write(failures)
        print(f"\nFailures saved to import_failures.csv")

    warnings = client.bulk_import.get_lead_job_warnings(batch_id)
    if warnings:
        with open("import_warnings.csv", "w") as f:
            f.write(warnings)
        print(f"Warnings saved to import_warnings.csv")

except MarketoBulkOperationError as e:
    print(f"Import failed: {e.message}")
```

---

## Recipe: Export Email Engagement Data

Export send, open, click, and bounce activities for email analysis:

```python
client = MarketoClient.from_env()

# Email activity types: Send(6), Delivered(7), Bounced(8), Open(10), Click(11)
job = client.bulk_extract.create_activity_job(
    filter={
        "createdAt": {
            "startAt": "2025-06-01T00:00:00Z",
            "endAt": "2025-07-01T00:00:00Z"
        },
        "activityTypeIds": [6, 7, 8, 10, 11]
    }
)

client.bulk_extract.enqueue_activity_job(job["exportId"])
status = client.bulk_extract.poll_until_complete(
    job["exportId"],
    object_type="activities",
    poll_interval=20
)

csv_data = client.bulk_extract.download_file(job["exportId"], object_type="activities")
with open("email_engagement.csv", "w") as f:
    f.write(csv_data)

print(f"Exported {status.get('numberOfRows', 0)} email activity records")
```

---

## Recipe: Chunked REST Import (Under 300 Leads)

For smaller imports where bulk API is overkill:

```python
import csv

client = MarketoClient.from_env()

# Read CSV
with open("small_import.csv") as f:
    reader = csv.DictReader(f)
    leads = list(reader)

# Import in chunks of 300
CHUNK_SIZE = 300
created = 0
updated = 0
failed = 0

for i in range(0, len(leads), CHUNK_SIZE):
    chunk = leads[i:i + CHUNK_SIZE]
    result = client.leads.create_or_update(
        leads=chunk,
        action="createOrUpdate",
        lookup_field="email"
    )
    for item in result.get("result", []):
        if item["status"] == "created":
            created += 1
        elif item["status"] == "updated":
            updated += 1
        else:
            failed += 1

print(f"Created: {created}, Updated: {updated}, Failed: {failed}")
```

---

## Recipe: Sync Static List from External Source

```python
client = MarketoClient.from_env()

LIST_ID = 100

# Get current members
current_members = client.lists.get_leads(LIST_ID, fields=["email"])
current_emails = {lead["email"] for lead in current_members}

# Your desired member list
desired_emails = {"alice@acme.com", "bob@globex.com", "carol@initech.com"}

# Find leads by email to get their IDs
all_emails = current_emails | desired_emails
leads = client.leads.get_by_filter(
    filter_type="email",
    filter_values=list(all_emails),
    fields=["email"]
)
email_to_id = {lead["email"]: lead["id"] for lead in leads}

# Add missing members
to_add = desired_emails - current_emails
if to_add:
    add_ids = [email_to_id[e] for e in to_add if e in email_to_id]
    if add_ids:
        client.lists.add_leads(LIST_ID, add_ids)
        print(f"Added {len(add_ids)} leads")

# Remove extra members
to_remove = current_emails - desired_emails
if to_remove:
    remove_ids = [email_to_id[e] for e in to_remove if e in email_to_id]
    if remove_ids:
        client.lists.remove_leads(LIST_ID, remove_ids)
        print(f"Removed {len(remove_ids)} leads")
```
