"""
Example: Bulk Import & Export Operations
=========================================

Demonstrates how to use the Bulk API for large-scale data operations:
- Bulk lead export with date filter
- Bulk lead import from CSV
- Job polling and status monitoring

Prerequisites:
    pip install marketo-rest-api-wrapper

    Set environment variables:
        MARKETO_MUNCHKIN_ID=123-ABC-456
        MARKETO_CLIENT_ID=your-client-id
        MARKETO_CLIENT_SECRET=your-client-secret
"""

from marketo_api import MarketoClient
from marketo_api.exceptions import MarketoBulkOperationError


def bulk_export_example(client: MarketoClient):
    """Export all leads created in Q1 2025."""
    print("=== Bulk Lead Export ===\n")

    # Step 1: Create the export job
    job = client.bulk_extract.create_lead_job(
        fields=["id", "email", "firstName", "lastName", "createdAt", "company"],
        filter={
            "createdAt": {
                "startAt": "2025-01-01T00:00:00Z",
                "endAt": "2025-04-01T00:00:00Z",
            }
        },
    )
    export_id = job["exportId"]
    print(f"Created export job: {export_id}")

    # Step 2: Enqueue the job
    client.bulk_extract.enqueue(export_id)
    print("Job enqueued for processing...")

    # Step 3: Poll until complete
    try:
        status = client.bulk_extract.poll_until_complete(
            export_id,
            poll_interval=15,
            max_wait=1800,
        )
        print(f"Job completed! Status: {status['status']}")
        print(f"File size: {status.get('fileSize', 'N/A')} bytes")
        print(f"Number of rows: {status.get('numberOfRows', 'N/A')}")
    except MarketoBulkOperationError as e:
        print(f"Export failed: {e}")
        return

    # Step 4: Download the file
    csv_data = client.bulk_extract.download_file(export_id)
    output_path = "exported_leads.csv"
    with open(output_path, "w") as f:
        f.write(csv_data)
    print(f"Data saved to {output_path}")


def bulk_import_example(client: MarketoClient):
    """Import leads from a CSV file."""
    print("\n=== Bulk Lead Import ===\n")

    csv_path = "leads_to_import.csv"

    # Step 1: Create and upload the import job
    try:
        job = client.bulk_import.create_lead_job(
            file_path=csv_path,
            format="csv",
            lookup_field="email",
        )
    except FileNotFoundError:
        print(f"File not found: {csv_path}")
        print("Create a CSV with columns: email, firstName, lastName, company")
        return

    batch_id = job["batchId"]
    print(f"Created import job: {batch_id}")
    print(f"Status: {job['status']}")

    # Step 2: Poll until complete
    try:
        status = client.bulk_import.poll_until_complete(
            batch_id,
            poll_interval=10,
            max_wait=600,
        )
        print(f"\nImport complete!")
        print(f"  Rows processed: {status.get('numOfRowsProcessed', 'N/A')}")
        print(f"  Rows failed: {status.get('numOfRowsFailed', 'N/A')}")
        print(f"  Leads created: {status.get('numOfLeadsCreated', 'N/A')}")
        print(f"  Leads updated: {status.get('numOfLeadsUpdated', 'N/A')}")
    except MarketoBulkOperationError as e:
        print(f"Import failed: {e}")
        return

    # Step 3: Check for failures
    failures = client.bulk_import.get_lead_job_failures(batch_id)
    if failures:
        print(f"\nFailed rows:\n{failures}")

    warnings = client.bulk_import.get_lead_job_warnings(batch_id)
    if warnings:
        print(f"\nWarnings:\n{warnings}")


def bulk_activity_export_example(client: MarketoClient):
    """Export activities for a specific time range."""
    print("\n=== Bulk Activity Export ===\n")

    job = client.bulk_extract.create_activity_job(
        filter={
            "createdAt": {
                "startAt": "2025-01-01T00:00:00Z",
                "endAt": "2025-02-01T00:00:00Z",
            },
            "activityTypeIds": [1, 2, 6, 12],  # Visit, Click, Email Send, New Lead
        },
    )
    export_id = job["exportId"]
    print(f"Created activity export job: {export_id}")

    client.bulk_extract.enqueue_activity_job(export_id)
    print("Job enqueued...")

    try:
        status = client.bulk_extract.poll_until_complete(
            export_id,
            object_type="activities",
            poll_interval=15,
        )
        print(f"Completed: {status.get('numberOfRows', 'N/A')} rows")

        csv_data = client.bulk_extract.download_file(export_id, object_type="activities")
        with open("exported_activities.csv", "w") as f:
            f.write(csv_data)
        print("Data saved to exported_activities.csv")
    except MarketoBulkOperationError as e:
        print(f"Activity export failed: {e}")


def main():
    client = MarketoClient.from_env()
    print(f"Connected: {client}\n")

    bulk_export_example(client)
    bulk_import_example(client)
    bulk_activity_export_example(client)


if __name__ == "__main__":
    main()
