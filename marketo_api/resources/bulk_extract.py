"""Bulk Extract resource — export leads, activities, and program members.

Reference: https://developers.marketo.com/rest-api/bulk-extract/
"""

from __future__ import annotations

import logging
import time
from typing import Any

from marketo_api.exceptions import MarketoBulkOperationError
from marketo_api.resources.base import BaseResource

logger = logging.getLogger("marketo_api.bulk_extract")


class BulkExtractResource(BaseResource):
    """Bulk extract (export) operations for large data sets."""

    # ── Lead Export ───────────────────────────────────────────────────────

    def create_lead_job(
        self,
        fields: list[str],
        filter: dict[str, Any],
        format: str = "CSV",
    ) -> dict[str, Any]:
        """Create a bulk lead export job.

        Args:
            fields: List of lead field API names to export.
            filter: Filter dict (e.g., {"createdAt": {"startAt": "...", "endAt": "..."}}).
            format: Output format ("CSV" or "TSV").

        Returns:
            Job descriptor dict with exportId.
        """
        endpoint = "/bulk/v1/leads/export/create.json"
        body: dict[str, Any] = {
            "fields": fields,
            "filter": filter,
            "format": format,
        }
        response = self._post(endpoint, json_body=body)
        results = response.get("result", [])
        if not results:
            raise MarketoBulkOperationError(
                message="No result returned from bulk lead export job creation",
                response_data=response,
            )
        return results[0]

    def enqueue_lead_job(self, export_id: str) -> dict[str, Any]:
        """Enqueue a lead export job for processing.

        Args:
            export_id: The export ID from create_lead_job.

        Returns:
            Updated job status dict.
        """
        endpoint = f"/bulk/v1/leads/export/{export_id}/enqueue.json"
        response = self._post(endpoint)
        results = response.get("result", [])
        return results[0] if results else {}

    def get_lead_job_status(self, export_id: str) -> dict[str, Any]:
        """Get the status of a lead export job.

        Args:
            export_id: The export ID.

        Returns:
            Job status dict.
        """
        endpoint = f"/bulk/v1/leads/export/{export_id}/status.json"
        response = self._get(endpoint)
        results = response.get("result", [])
        return results[0] if results else {}

    def download_lead_file(self, export_id: str) -> str:
        """Download the output file of a completed lead export.

        Args:
            export_id: The export ID.

        Returns:
            CSV/TSV string of exported data.
        """
        endpoint = f"/bulk/v1/leads/export/{export_id}/file.json"
        response = self._get(endpoint)
        return response.get("result", "")

    # ── Activity Export ───────────────────────────────────────────────────

    def create_activity_job(
        self,
        filter: dict[str, Any],
        fields: list[str] | None = None,
        format: str = "CSV",
    ) -> dict[str, Any]:
        """Create a bulk activity export job.

        Args:
            filter: Filter dict with "createdAt" and optionally "activityTypeIds".
            fields: Optional list of activity field names.
            format: Output format ("CSV" or "TSV").

        Returns:
            Job descriptor dict with exportId.
        """
        endpoint = "/bulk/v1/activities/export/create.json"
        body: dict[str, Any] = {
            "filter": filter,
            "format": format,
        }
        if fields:
            body["fields"] = fields

        response = self._post(endpoint, json_body=body)
        results = response.get("result", [])
        if not results:
            raise MarketoBulkOperationError(
                message="No result returned from bulk activity export job creation",
                response_data=response,
            )
        return results[0]

    def enqueue_activity_job(self, export_id: str) -> dict[str, Any]:
        """Enqueue an activity export job for processing."""
        endpoint = f"/bulk/v1/activities/export/{export_id}/enqueue.json"
        response = self._post(endpoint)
        results = response.get("result", [])
        return results[0] if results else {}

    def get_activity_job_status(self, export_id: str) -> dict[str, Any]:
        """Get the status of an activity export job."""
        endpoint = f"/bulk/v1/activities/export/{export_id}/status.json"
        response = self._get(endpoint)
        results = response.get("result", [])
        return results[0] if results else {}

    def download_activity_file(self, export_id: str) -> str:
        """Download the output file of a completed activity export."""
        endpoint = f"/bulk/v1/activities/export/{export_id}/file.json"
        response = self._get(endpoint)
        return response.get("result", "")

    # ── Generic helpers ───────────────────────────────────────────────────

    def enqueue(self, export_id: str, object_type: str = "leads") -> dict[str, Any]:
        """Enqueue an export job (convenience method).

        Args:
            export_id: The export ID.
            object_type: "leads" or "activities".

        Returns:
            Updated job status dict.
        """
        if object_type == "leads":
            return self.enqueue_lead_job(export_id)
        elif object_type == "activities":
            return self.enqueue_activity_job(export_id)
        else:
            raise ValueError(f"Unsupported object_type: {object_type}")

    def get_status(self, export_id: str, object_type: str = "leads") -> dict[str, Any]:
        """Get export job status (convenience method)."""
        if object_type == "leads":
            return self.get_lead_job_status(export_id)
        elif object_type == "activities":
            return self.get_activity_job_status(export_id)
        else:
            raise ValueError(f"Unsupported object_type: {object_type}")

    def download_file(self, export_id: str, object_type: str = "leads") -> str:
        """Download export file (convenience method)."""
        if object_type == "leads":
            return self.download_lead_file(export_id)
        elif object_type == "activities":
            return self.download_activity_file(export_id)
        else:
            raise ValueError(f"Unsupported object_type: {object_type}")

    def poll_until_complete(
        self,
        export_id: str,
        object_type: str = "leads",
        poll_interval: int = 30,
        max_wait: int = 7200,
    ) -> dict[str, Any]:
        """Poll an export job until it completes.

        Args:
            export_id: The export ID.
            object_type: "leads" or "activities".
            poll_interval: Seconds between status checks.
            max_wait: Maximum total seconds to wait.

        Returns:
            Final job status dict.

        Raises:
            MarketoBulkOperationError: If the job fails or times out.
        """
        elapsed = 0
        terminal_statuses = {"Completed", "Failed", "Cancelled"}

        while elapsed < max_wait:
            status = self.get_status(export_id, object_type)
            current_status = status.get("status", "Unknown")

            logger.info(
                "Bulk export job %s status: %s (elapsed: %ds)",
                export_id,
                current_status,
                elapsed,
            )

            if current_status in terminal_statuses:
                if current_status == "Failed":
                    raise MarketoBulkOperationError(
                        message=f"Bulk export job {export_id} failed",
                        response_data=status,
                    )
                return status

            time.sleep(poll_interval)
            elapsed += poll_interval

        raise MarketoBulkOperationError(
            message=f"Bulk export job {export_id} timed out after {max_wait}s",
        )
