"""
Example: Basic Marketo API Usage
=================================

This script demonstrates the most common Marketo API operations:
- Initializing the client
- Looking up leads
- Creating/updating leads
- Querying activities
- Triggering campaigns

Prerequisites:
    pip install marketo-rest-api-wrapper

    Set environment variables:
        MARKETO_MUNCHKIN_ID=123-ABC-456
        MARKETO_CLIENT_ID=your-client-id
        MARKETO_CLIENT_SECRET=your-client-secret
"""

from marketo_api import MarketoClient, MarketoAPIError, MarketoNotFoundError


def main():
    # ── Initialize from environment variables ─────────────────────────
    client = MarketoClient.from_env()
    print(f"Connected to: {client}")
    print(f"Daily calls remaining: {client.daily_calls_remaining}")

    # ── Look up a lead by email ───────────────────────────────────────
    print("\n--- Lead Lookup ---")
    lead = client.leads.get_by_email(
        "test@example.com",
        fields=["email", "firstName", "lastName", "company", "leadScore"],
    )
    if lead:
        print(f"Found: {lead['firstName']} {lead['lastName']} ({lead['email']})")
        print(f"  Company: {lead.get('company', 'N/A')}")
        print(f"  Score: {lead.get('leadScore', 0)}")
    else:
        print("Lead not found")

    # ── Create or update leads ────────────────────────────────────────
    print("\n--- Create/Update Leads ---")
    result = client.leads.create_or_update(
        leads=[
            {
                "email": "alice@example.com",
                "firstName": "Alice",
                "lastName": "Smith",
                "company": "Acme Corp",
            },
            {
                "email": "bob@example.com",
                "firstName": "Bob",
                "lastName": "Jones",
                "company": "Globex",
            },
        ],
        action="createOrUpdate",
        lookup_field="email",
    )
    for item in result.get("result", []):
        print(f"  Lead {item['id']}: {item['status']}")

    # ── Get lead schema ───────────────────────────────────────────────
    print("\n--- Lead Schema (first 10 fields) ---")
    schema = client.leads.describe()
    for field in schema[:10]:
        print(f"  {field['rest']['name']} ({field['dataType']})")

    # ── Query activities ──────────────────────────────────────────────
    print("\n--- Recent Activities ---")
    try:
        # Activity type 1 = Visit Web Page, 12 = New Lead
        activities = client.activities.get(
            activity_type_ids=[1, 12],
            since_datetime="2025-01-01T00:00:00Z",
        )
        print(f"Found {len(activities)} activities")
        for act in activities[:5]:
            print(f"  [{act['activityTypeId']}] Lead {act['leadId']} at {act['activityDate']}")
    except MarketoAPIError as e:
        print(f"Activity query error: {e}")

    # ── Get activity types ────────────────────────────────────────────
    print("\n--- Activity Types (first 10) ---")
    types = client.activities.get_types()
    for t in types[:10]:
        print(f"  {t['id']}: {t['name']}")

    # ── Check rate limit status ───────────────────────────────────────
    print(f"\n--- Rate Limits ---")
    print(f"Daily calls remaining: {client.daily_calls_remaining}")
    print(f"Window calls remaining: {client.window_calls_remaining}")


if __name__ == "__main__":
    main()
