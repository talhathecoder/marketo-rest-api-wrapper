"""Custom Objects resource — CRUD operations on Marketo custom objects.

Reference: https://developers.marketo.com/rest-api/lead-database/custom-objects/
"""

from __future__ import annotations

from typing import Any

from marketo_api.resources.base import BaseResource
from marketo_api.utils.pagination import collect_all, paginate_with_token


class CustomObjectsResource(BaseResource):
    """Operations on Marketo custom objects."""

    ENDPOINT = "/rest/v1/customobjects.json"

    def list_types(self) -> list[dict[str, Any]]:
        """List all custom object types in the instance.

        Returns:
            List of custom object type descriptors.
        """
        response = self._get(self.ENDPOINT)
        return response.get("result", [])

    def describe(self, api_name: str) -> dict[str, Any]:
        """Describe a custom object type's schema.

        Args:
            api_name: The API name of the custom object (e.g., "car_c").

        Returns:
            Schema descriptor dict with fields and relationships.
        """
        endpoint = f"/rest/v1/customobjects/{api_name}/describe.json"
        response = self._get(endpoint)
        results = response.get("result", [])
        return results[0] if results else {}

    def get(
        self,
        api_name: str,
        filter_type: str,
        filter_values: list[str],
        fields: list[str] | None = None,
        batch_size: int = 300,
    ) -> list[dict[str, Any]]:
        """Query custom object records.

        Args:
            api_name: The API name of the custom object.
            filter_type: The field to filter on (must be a searchable field).
            filter_values: Values to match.
            fields: Optional list of fields to return.
            batch_size: Results per page (max 300).

        Returns:
            List of matching custom object records.
        """
        endpoint = f"/rest/v1/customobjects/{api_name}.json"
        params: dict[str, Any] = {
            "filterType": filter_type,
            "filterValues": ",".join(str(v) for v in filter_values),
            "batchSize": min(batch_size, 300),
        }
        if fields:
            params["fields"] = ",".join(fields)

        return collect_all(
            paginate_with_token(self._get, endpoint, params=params)
        )

    def create_or_update(
        self,
        api_name: str,
        records: list[dict[str, Any]],
        action: str = "createOrUpdate",
        dedupe_by: str = "dedupeFields",
    ) -> dict[str, Any]:
        """Create or update custom object records.

        Args:
            api_name: The API name of the custom object.
            records: List of record dicts with field values.
            action: One of "createOrUpdate", "createOnly", "updateOnly".
            dedupe_by: Deduplication mode ("dedupeFields" or "idField").

        Returns:
            API response with status per record.
        """
        endpoint = f"/rest/v1/customobjects/{api_name}.json"
        body: dict[str, Any] = {
            "action": action,
            "dedupeBy": dedupe_by,
            "input": records,
        }
        return self._post(endpoint, json_body=body)

    def delete(
        self,
        api_name: str,
        records: list[dict[str, Any]],
        delete_by: str = "dedupeFields",
    ) -> dict[str, Any]:
        """Delete custom object records.

        Args:
            api_name: The API name of the custom object.
            records: List of record dicts identifying records to delete.
            delete_by: Deletion mode ("dedupeFields" or "idField").

        Returns:
            API response with status per record.
        """
        endpoint = f"/rest/v1/customobjects/{api_name}/delete.json"
        body: dict[str, Any] = {
            "deleteBy": delete_by,
            "input": records,
        }
        return self._post(endpoint, json_body=body)
