"""Leads resource — CRUD operations on the Marketo lead database.

Reference: https://developers.marketo.com/rest-api/lead-database/leads/
"""

from __future__ import annotations

from typing import Any, Optional

from marketo_api.resources.base import BaseResource
from marketo_api.utils.pagination import collect_all, paginate_with_token


class LeadsResource(BaseResource):
    """Operations on Marketo leads."""

    ENDPOINT = "/rest/v1/leads.json"
    DESCRIBE_ENDPOINT = "/rest/v1/leads/describe.json"
    DESCRIBE2_ENDPOINT = "/rest/v1/leads/describe2.json"

    # ── Read ──────────────────────────────────────────────────────────────

    def get_by_id(
        self,
        lead_id: int,
        fields: list[str] | None = None,
    ) -> dict[str, Any] | None:
        """Get a single lead by its Marketo ID.

        Args:
            lead_id: The Marketo lead ID.
            fields: Optional list of field API names to return.

        Returns:
            Lead record dict, or None if not found.
        """
        endpoint = f"/rest/v1/lead/{lead_id}.json"
        params: dict[str, Any] = {}
        if fields:
            params["fields"] = ",".join(fields)

        response = self._get(endpoint, params=params)
        results = response.get("result", [])
        return results[0] if results else None

    def get_by_email(
        self,
        email: str,
        fields: list[str] | None = None,
    ) -> dict[str, Any] | None:
        """Get a single lead by email address.

        Args:
            email: The lead's email address.
            fields: Optional list of fields to return.

        Returns:
            Lead record dict, or None if not found.
        """
        results = self.get_by_filter(
            filter_type="email",
            filter_values=[email],
            fields=fields,
        )
        return results[0] if results else None

    def get_by_filter(
        self,
        filter_type: str,
        filter_values: list[str],
        fields: list[str] | None = None,
        batch_size: int = 300,
    ) -> list[dict[str, Any]]:
        """Get leads matching a filter.

        Args:
            filter_type: The lead field API name to filter on.
            filter_values: List of values to match.
            fields: Optional list of fields to return.
            batch_size: Number of results per page (max 300).

        Returns:
            List of matching lead records.
        """
        params: dict[str, Any] = {
            "filterType": filter_type,
            "filterValues": ",".join(str(v) for v in filter_values),
            "batchSize": min(batch_size, 300),
        }
        if fields:
            params["fields"] = ",".join(fields)

        return collect_all(
            paginate_with_token(self._get, self.ENDPOINT, params=params)
        )

    def get_multiple(
        self,
        lead_ids: list[int],
        fields: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Get multiple leads by their IDs.

        Args:
            lead_ids: List of Marketo lead IDs.
            fields: Optional list of fields to return.

        Returns:
            List of lead records.
        """
        return self.get_by_filter(
            filter_type="id",
            filter_values=[str(lid) for lid in lead_ids],
            fields=fields,
        )

    # ── Write ─────────────────────────────────────────────────────────────

    def create_or_update(
        self,
        leads: list[dict[str, Any]],
        action: str = "createOrUpdate",
        lookup_field: str = "email",
        partition_name: str | None = None,
    ) -> dict[str, Any]:
        """Create or update leads in the database.

        Args:
            leads: List of lead record dicts with field values.
            action: One of "createOrUpdate", "createOnly",
                "updateOnly", "createDuplicate".
            lookup_field: The field used for deduplication.
            partition_name: Optional lead partition name.

        Returns:
            API response with status per lead.
        """
        body: dict[str, Any] = {
            "action": action,
            "lookupField": lookup_field,
            "input": leads,
        }
        if partition_name:
            body["partitionName"] = partition_name

        return self._post(self.ENDPOINT, json_body=body)

    def delete(
        self,
        leads: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Delete leads by ID.

        Args:
            leads: List of dicts with "id" keys, e.g., [{"id": 123}].

        Returns:
            API response with status per lead.
        """
        return self._delete(self.ENDPOINT, json_body={"input": leads})

    def merge(
        self,
        winning_lead_id: int,
        losing_lead_ids: list[int],
        merge_in_crm: bool = False,
    ) -> dict[str, Any]:
        """Merge duplicate leads.

        Args:
            winning_lead_id: The lead ID that will survive the merge.
            losing_lead_ids: Lead IDs to merge into the winner.
            merge_in_crm: Whether to also merge in the CRM.

        Returns:
            API response confirming the merge.
        """
        endpoint = f"/rest/v1/leads/{winning_lead_id}/merge.json"
        params: dict[str, Any] = {
            "leadIds": ",".join(str(lid) for lid in losing_lead_ids),
        }
        if merge_in_crm:
            params["mergeInCRM"] = "true"

        return self._post(endpoint, params=params)

    # ── Describe ──────────────────────────────────────────────────────────

    def describe(self) -> list[dict[str, Any]]:
        """Get the schema for the lead object (fields, data types, etc.).

        Returns:
            List of field descriptor dicts.
        """
        response = self._get(self.DESCRIBE_ENDPOINT)
        return response.get("result", [])

    def describe2(self) -> dict[str, Any]:
        """Get the extended schema for the lead object (v2).

        Returns:
            Extended schema dict with searchable fields and relationships.
        """
        response = self._get(self.DESCRIBE2_ENDPOINT)
        results = response.get("result", [])
        return results[0] if results else {}
