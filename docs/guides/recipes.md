# Common Recipes

Copy-paste solutions for everyday Marketo API tasks.

---

## Lead Management

### Find leads by multiple criteria

```python
# By company
leads = client.leads.get_by_filter(
    filter_type="company",
    filter_values=["Acme Corp", "Globex", "Initech"],
    fields=["email", "firstName", "lastName", "company", "leadScore"]
)

# By lead source
leads = client.leads.get_by_filter(
    filter_type="leadSource",
    filter_values=["Web Form", "Trade Show"],
    fields=["email", "leadSource", "createdAt"]
)
```

### Get all fields for a lead

```python
# First, get all field names
schema = client.leads.describe()
all_fields = [f["rest"]["name"] for f in schema if not f["rest"].get("readOnly")]

# Then fetch with all fields
lead = client.leads.get_by_id(12345, fields=all_fields)
```

### Deduplicate leads by email

```python
from collections import defaultdict

# Get leads that share an email domain
leads = client.leads.get_by_filter(
    filter_type="company",
    filter_values=["Acme Corp"],
    fields=["id", "email", "createdAt", "leadScore"]
)

# Group by email
by_email = defaultdict(list)
for lead in leads:
    by_email[lead["email"]].append(lead)

# Find duplicates
for email, dupes in by_email.items():
    if len(dupes) > 1:
        # Keep the highest-scored lead
        dupes.sort(key=lambda l: l.get("leadScore", 0), reverse=True)
        winner = dupes[0]
        losers = dupes[1:]
        print(f"Merge {email}: keep {winner['id']}, merge {[l['id'] for l in losers]}")

        client.leads.merge(
            winning_lead_id=winner["id"],
            losing_lead_ids=[l["id"] for l in losers]
        )
```

---

## Program Operations

### Clone a program with token overrides

```python
# Clone the template program
clone = client.programs.clone(
    program_id=1001,  # Template program
    name="Webinar-2025-10-AI-Workshop",
    folder={"id": 50, "type": "Folder"}
)

# Set program-specific tokens
tokens_to_set = {
    "{{my.event-name}}": "AI Workshop 2025",
    "{{my.event-date}}": "October 15, 2025",
    "{{my.event-time}}": "2:00 PM EST",
    "{{my.registration-url}}": "https://example.com/register/ai-workshop",
}

for name, value in tokens_to_set.items():
    client.tokens.create(
        folder_id=clone["id"],
        folder_type="Program",
        name=name,
        type="text",
        value=value
    )

print(f"Program cloned: {clone['name']} (ID: {clone['id']})")
```

### Audit all programs in a workspace

```python
programs = client.programs.get(workspace="Default")

active = [p for p in programs if p.get("status") == "active"]
inactive = [p for p in programs if p.get("status") != "active"]

print(f"Total: {len(programs)}, Active: {len(active)}, Inactive: {len(inactive)}")

# Find programs with no members
for p in active[:20]:
    members = client.programs.get_members(p["id"])
    if not members:
        print(f"  Empty active program: {p['name']} (ID: {p['id']})")
```

---

## Activity Analysis

### Get form fills for a date range

```python
# Activity type 2 = Fill Out Form
form_fills = client.activities.get(
    activity_type_ids=[2],
    since_datetime="2025-06-01T00:00:00Z"
)

# Parse form details from attributes
for fill in form_fills[:20]:
    attrs = {a["name"]: a["value"] for a in fill.get("attributes", [])}
    print(f"Lead {fill['leadId']} filled '{attrs.get('Form Name', 'Unknown')}' "
          f"on {fill['activityDate']}")
```

### Track email performance

```python
from collections import Counter

# Activity types: Send(6), Open(10), Click(11), Bounce(8)
activities = client.activities.get(
    activity_type_ids=[6, 10, 11, 8],
    since_datetime="2025-06-01T00:00:00Z"
)

# Count by type
counts = Counter(a["activityTypeId"] for a in activities)
sends = counts.get(6, 0)
opens = counts.get(10, 0)
clicks = counts.get(11, 0)
bounces = counts.get(8, 0)

print(f"Sends: {sends}")
print(f"Opens: {opens} ({opens/max(sends,1)*100:.1f}%)")
print(f"Clicks: {clicks} ({clicks/max(sends,1)*100:.1f}%)")
print(f"Bounces: {bounces} ({bounces/max(sends,1)*100:.1f}%)")
```

---

## Campaign Automation

### Trigger a campaign with dynamic tokens

```python
# Trigger a personalized follow-up email
leads_to_contact = [
    {"id": 100, "discount": "20%", "product": "Enterprise Plan"},
    {"id": 200, "discount": "15%", "product": "Pro Plan"},
]

for lead_info in leads_to_contact:
    client.campaigns.trigger(
        campaign_id=3001,
        leads=[{"id": lead_info["id"]}],
        tokens=[
            {"name": "{{my.discount-amount}}", "value": lead_info["discount"]},
            {"name": "{{my.product-name}}", "value": lead_info["product"]},
        ]
    )
    print(f"Triggered campaign for lead {lead_info['id']}")
```

---

## Instance Administration

### Export lead field schema to CSV

```python
import csv

schema = client.leads.describe()

with open("lead_fields.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "name", "displayName", "dataType", "length", "readOnly"
    ])
    writer.writeheader()
    for field in schema:
        writer.writerow({
            "name": field["rest"]["name"],
            "displayName": field.get("displayName", ""),
            "dataType": field.get("dataType", ""),
            "length": field.get("length", ""),
            "readOnly": field["rest"].get("readOnly", False),
        })

print(f"Exported {len(schema)} fields to lead_fields.csv")
```

### Find unused static lists

```python
all_lists = client.lists.get()

for lst in all_lists:
    leads = client.lists.get_leads(lst["id"], fields=["id"])
    if not leads:
        print(f"Empty list: {lst['name']} (ID: {lst['id']})")
```

### Browse the folder tree

```python
def print_tree(folder_id, indent=0):
    """Recursively print the folder tree."""
    folder = client.folders.get_by_id(folder_id)
    if folder:
        print(" " * indent + f"📁 {folder['name']} ({folder['id']})")

    contents = client.folders.get_contents(folder_id)
    for item in contents:
        if item.get("type") == "Folder":
            print_tree(item["id"], indent + 2)
        else:
            print(" " * (indent + 2) + f"📄 {item['type']}: {item['name']}")

# Start from root (folder ID varies by instance)
print_tree(1)
```
