"""Lists resource — static list operations.

Reference: https://developers.marketo.com/rest-api/lead-database/static-lists/
"""

from __future__ import annotations

from typing import Any

from marketo_api.resources.base import BaseResource
from marketo_api.utils.pagination import collect_all, paginate_with_token, paginate_with_offset


class ListsResource(BaseResource):
    """Operations on Marketo static lists."""

    ENDPOINT = "/rest/v1/lists.json"

    def get(
        self,
        list_ids: list[int] | None = None,
        names: list[str] | None = None,
        program_names: list[str] | None = None,
        workspace_names: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Get static lists with optional filters.

        Args:
            list_ids: Filter by list IDs.
            names: Filter by list names.
            program_names: Filter by parent program names.
            workspace_names: Filter by workspace names.

        Returns:
            List of static list records.
        """
        params: dict[str, Any] = {}
        if list_ids:
            params["id"] = ",".join(str(lid) for lid in list_ids)
        if names:
            params["name"] = ",".join(names)
        if program_names:
            params["programName"] = ",".join(program_names)
        if workspace_names:
            params["workspaceName"] = ",".join(workspace_names)

        return collect_all(
            paginate_with_offset(self._get, self.ENDPOINT, params=params)
        )

    def get_by_id(self, list_id: int) -> dict[str, Any] | None:
        """Get a single static list by ID.

        Args:
            list_id: The static list ID.

        Returns:
            List record dict, or None if not found.
        """
        endpoint = f"/rest/v1/lists/{list_id}.json"
        response = self._get(endpoint)
        results = response.get("result", [])
        return results[0] if results else None

    def get_leads(
        self,
        list_id: int,
        fields: list[str] | None = None,
        batch_size: int = 300,
    ) -> list[dict[str, Any]]:
        """Get all leads in a static list.

        Args:
            list_id: The static list ID.
            fields: Optional list of fields to return.
            batch_size: Results per page (max 300).

        Returns:
            List of lead records belonging to the list.
        """
        endpoint = f"/rest/v1/lists/{list_id}/leads.json"
        params: dict[str, Any] = {"batchSize": min(batch_size, 300)}
        if fields:
            params["fields"] = ",".join(fields)

        return collect_all(
            paginate_with_token(self._get, endpoint, params=params)
        )

    def add_leads(
        self,
        list_id: int,
        lead_ids: list[int],
    ) -> dict[str, Any]:
        """Add leads to a static list.

        Args:
            list_id: The static list ID.
            lead_ids: List of lead IDs to add.

        Returns:
            API response with status per lead.
        """
        endpoint = f"/rest/v1/lists/{list_id}/leads.json"
        body = {"input": [{"id": lid} for lid in lead_ids]}
        return self._post(endpoint, json_body=body)

    def remove_leads(
        self,
        list_id: int,
        lead_ids: list[int],
    ) -> dict[str, Any]:
        """Remove leads from a static list.

        Args:
            list_id: The static list ID.
            lead_ids: List of lead IDs to remove.

        Returns:
            API response with status per lead.
        """
        endpoint = f"/rest/v1/lists/{list_id}/leads.json"
        body = {"input": [{"id": lid} for lid in lead_ids]}
        return self._delete(endpoint, json_body=body)

    def is_member(
        self,
        list_id: int,
        lead_ids: list[int],
    ) -> list[dict[str, Any]]:
        """Check if leads are members of a static list.

        Args:
            list_id: The static list ID.
            lead_ids: Lead IDs to check.

        Returns:
            List of membership status records.
        """
        endpoint = f"/rest/v1/lists/{list_id}/leads/ismember.json"
        params = {"id": ",".join(str(lid) for lid in lead_ids)}
        response = self._get(endpoint, params=params)
        return response.get("result", [])
