# Salesforce Sync Patterns

Common patterns for working with Marketo data that syncs to/from Salesforce.

---

## Understanding the Sync

Marketo's native Salesforce sync runs every ~5 minutes and synchronizes leads, contacts, accounts, opportunities, and campaigns. When working with the API, you need to account for this sync behavior.

**Key points:**
- Changes made via API are picked up by the next sync cycle
- Salesforce-sourced fields may be overwritten by the sync if the SFDC value is newer
- Some fields are "blocked" from API updates when Salesforce is the source of truth
- Lead/contact merge in SFDC triggers a merge in Marketo (and vice versa if configured)

---

## Pattern: Update Marketo Without Triggering SFDC Sync

If you need to update a Marketo-only field (one that doesn't sync to Salesforce), just use the standard API:

```python
client.leads.create_or_update(
    leads=[{"email": "alice@acme.com", "customMarketoField": "new-value"}],
    lookup_field="email"
)
```

For fields that DO sync, be aware the value may flow to Salesforce on the next sync cycle. If you don't want that, use a Marketo-only custom field instead.

---

## Pattern: Check Sync Status Before Updates

Before updating a field that syncs with Salesforce, verify the lead's sync state:

```python
lead = client.leads.get_by_email(
    "alice@acme.com",
    fields=["email", "sfdcId", "sfdcLeadId", "sfdcContactId", "sfdcType"]
)

if lead:
    sfdc_id = lead.get("sfdcId")
    sfdc_type = lead.get("sfdcType")
    print(f"SFDC record: {sfdc_type} {sfdc_id}")

    if sfdc_id:
        print("This lead syncs with Salesforce — updates will propagate")
    else:
        print("This lead is Marketo-only — no SFDC sync impact")
```

---

## Pattern: Reconcile Marketo–SFDC Data Mismatches

Export leads and compare with Salesforce data to find sync issues:

```python
# Export Marketo leads with SFDC fields
job = client.bulk_extract.create_lead_job(
    fields=[
        "id", "email", "firstName", "lastName",
        "sfdcId", "sfdcLeadId", "sfdcContactId",
        "sfdcType", "company", "leadScore"
    ],
    filter={
        "updatedAt": {
            "startAt": "2025-06-01T00:00:00Z",
            "endAt": "2025-07-01T00:00:00Z"
        }
    }
)

client.bulk_extract.enqueue(job["exportId"])
status = client.bulk_extract.poll_until_complete(job["exportId"])
csv_data = client.bulk_extract.download_file(job["exportId"])

# Parse and check for orphaned records (no SFDC ID)
import csv
import io

reader = csv.DictReader(io.StringIO(csv_data))
orphans = [row for row in reader if not row.get("sfdcId")]
print(f"Found {len(orphans)} leads without Salesforce records")
```

---

## Pattern: Handle Merge Conflicts

When duplicates exist across Marketo and Salesforce, use the merge API carefully:

```python
# Find duplicates by email domain
leads = client.leads.get_by_filter(
    filter_type="email",
    filter_values=["alice@acme.com"],
    fields=["id", "email", "sfdcId", "createdAt", "leadScore"]
)

if len(leads) > 1:
    # Pick the winner: prefer the one with an SFDC ID, then highest score
    leads.sort(key=lambda l: (bool(l.get("sfdcId")), l.get("leadScore", 0)), reverse=True)
    winner = leads[0]
    losers = leads[1:]

    print(f"Merging into lead {winner['id']} (score: {winner.get('leadScore')})")
    client.leads.merge(
        winning_lead_id=winner["id"],
        losing_lead_ids=[l["id"] for l in losers],
        merge_in_crm=True  # Also merge in Salesforce
    )
```

---

## Pattern: Monitor Sync Errors via Activities

Track sync failures by querying the "Sync Lead to SFDC" activity:

```python
# Activity type 39 = Sync Lead to SFDC (check your instance for exact ID)
# Use get_types() to find the right ID
activity_types = client.activities.get_types()
sync_types = [t for t in activity_types if "sync" in t["name"].lower() and "sfdc" in t["name"].lower()]

if sync_types:
    sync_type_id = sync_types[0]["id"]
    activities = client.activities.get(
        activity_type_ids=[sync_type_id],
        since_datetime="2025-06-01T00:00:00Z"
    )

    for act in activities[:10]:
        attrs = {a["name"]: a["value"] for a in act.get("attributes", [])}
        print(f"Lead {act['leadId']}: {attrs}")
```

---

## Pattern: Batch Update with SFDC Campaign Sync

Associate leads with Salesforce campaigns via Marketo programs:

```python
# Get program members with their SFDC campaign status
members = client.programs.get_members(
    program_id=1001,
    fields=["email", "sfdcId", "programStatus"]
)

# Update program membership status (syncs to SFDC campaign status)
# This is done via the Marketo UI or smart campaigns, not directly via REST API.
# However, you can trigger a smart campaign that changes program status:
client.campaigns.trigger(
    campaign_id=2001,  # Smart campaign that changes status to "Attended"
    leads=[{"id": m["id"]} for m in members if m.get("sfdcId")]
)
```

---

## Field Mapping Audit

Generate a report of all Marketo fields and their Salesforce mappings:

```python
schema = client.leads.describe()

synced_fields = []
marketo_only = []

for field in schema:
    name = field["rest"]["name"]
    data_type = field["dataType"]

    # Fields with "sfdc" or SOAP mappings typically sync
    soap_name = field.get("soap", {}).get("name", "")
    is_synced = bool(soap_name) or name.startswith("sfdc")

    entry = {"name": name, "dataType": data_type, "soapName": soap_name}
    if is_synced:
        synced_fields.append(entry)
    else:
        marketo_only.append(entry)

print(f"Synced fields: {len(synced_fields)}")
print(f"Marketo-only fields: {len(marketo_only)}")
```
