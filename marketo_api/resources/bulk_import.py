"""Bulk Import resource — import leads, custom objects, and program members via CSV.

Reference: https://developers.marketo.com/rest-api/bulk-import/
"""

from __future__ import annotations

import logging
import time
from typing import Any

from marketo_api.exceptions import MarketoBulkOperationError
from marketo_api.resources.base import BaseResource

logger = logging.getLogger("marketo_api.bulk_import")


class BulkImportResource(BaseResource):
    """Bulk import operations for large data sets."""

    # ── Lead Import ───────────────────────────────────────────────────────

    def create_lead_job(
        self,
        file_path: str,
        format: str = "csv",
        lookup_field: str = "email",
        list_id: int | None = None,
        partition_name: str | None = None,
    ) -> dict[str, Any]:
        """Create and upload a bulk lead import job.

        Args:
            file_path: Path to the CSV file to import.
            format: File format ("csv", "tsv", "ssv").
            lookup_field: Deduplication field.
            list_id: Optional static list ID to import into.
            partition_name: Optional lead partition name.

        Returns:
            Job status dict with batchId.
        """
        endpoint = "/bulk/v1/leads/import.json"
        params: dict[str, Any] = {
            "format": format,
            "lookupField": lookup_field,
        }
        if list_id:
            params["listId"] = list_id
        if partition_name:
            params["partitionName"] = partition_name

        response = self._transport.post_file(endpoint, file_path, params=params)
        results = response.get("result", [])
        if not results:
            raise MarketoBulkOperationError(
                message="No result returned from bulk import job creation",
                response_data=response,
            )
        return results[0]

    def get_lead_job_status(self, batch_id: int) -> dict[str, Any]:
        """Get the status of a bulk lead import job.

        Args:
            batch_id: The batch ID from create_lead_job.

        Returns:
            Job status dict with numOfRowsProcessed, numOfRowsFailed, etc.
        """
        endpoint = f"/bulk/v1/leads/batch/{batch_id}.json"
        response = self._get(endpoint)
        results = response.get("result", [])
        return results[0] if results else {}

    def get_lead_job_failures(self, batch_id: int) -> str:
        """Get the failure file for a bulk lead import job.

        Args:
            batch_id: The batch ID.

        Returns:
            CSV string of failed rows.
        """
        endpoint = f"/bulk/v1/leads/batch/{batch_id}/failures.json"
        response = self._get(endpoint)
        return response.get("result", "")

    def get_lead_job_warnings(self, batch_id: int) -> str:
        """Get the warnings file for a bulk lead import job.

        Args:
            batch_id: The batch ID.

        Returns:
            CSV string of rows with warnings.
        """
        endpoint = f"/bulk/v1/leads/batch/{batch_id}/warnings.json"
        response = self._get(endpoint)
        return response.get("result", "")

    # ── Custom Object Import ─────────────────────────────────────────────

    def create_custom_object_job(
        self,
        api_name: str,
        file_path: str,
        format: str = "csv",
    ) -> dict[str, Any]:
        """Create and upload a bulk custom object import job.

        Args:
            api_name: The custom object API name.
            file_path: Path to the CSV file.
            format: File format.

        Returns:
            Job status dict with batchId.
        """
        endpoint = f"/bulk/v1/customobjects/{api_name}/import.json"
        params = {"format": format}

        response = self._transport.post_file(endpoint, file_path, params=params)
        results = response.get("result", [])
        if not results:
            raise MarketoBulkOperationError(
                message="No result returned from bulk CO import job creation",
                response_data=response,
            )
        return results[0]

    # ── Polling ───────────────────────────────────────────────────────────

    def poll_until_complete(
        self,
        batch_id: int,
        poll_interval: int = 30,
        max_wait: int = 3600,
        object_type: str = "leads",
    ) -> dict[str, Any]:
        """Poll a bulk import job until it completes.

        Args:
            batch_id: The batch ID to monitor.
            poll_interval: Seconds between status checks.
            max_wait: Maximum total seconds to wait.
            object_type: "leads" or custom object API name.

        Returns:
            Final job status dict.

        Raises:
            MarketoBulkOperationError: If the job fails or times out.
        """
        elapsed = 0
        terminal_statuses = {"Complete", "Failed", "Cancelled"}

        while elapsed < max_wait:
            if object_type == "leads":
                status = self.get_lead_job_status(batch_id)
            else:
                endpoint = f"/bulk/v1/customobjects/{object_type}/batch/{batch_id}.json"
                response = self._get(endpoint)
                results = response.get("result", [])
                status = results[0] if results else {}

            current_status = status.get("status", "Unknown")
            logger.info(
                "Bulk import job %d status: %s (elapsed: %ds)",
                batch_id,
                current_status,
                elapsed,
            )

            if current_status in terminal_statuses:
                if current_status == "Failed":
                    raise MarketoBulkOperationError(
                        message=f"Bulk import job {batch_id} failed",
                        response_data=status,
                    )
                return status

            time.sleep(poll_interval)
            elapsed += poll_interval

        raise MarketoBulkOperationError(
            message=f"Bulk import job {batch_id} timed out after {max_wait}s",
        )
