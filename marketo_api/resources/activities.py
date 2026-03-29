"""Activities resource — query lead activity logs.

Reference: https://developers.marketo.com/rest-api/lead-database/activities/
"""

from __future__ import annotations

from typing import Any

from marketo_api.resources.base import BaseResource
from marketo_api.utils.pagination import collect_all, paginate_with_token


class ActivitiesResource(BaseResource):
    """Operations on Marketo activity records."""

    ENDPOINT = "/rest/v1/activities.json"
    TYPES_ENDPOINT = "/rest/v1/activities/types.json"
    PAGING_TOKEN_ENDPOINT = "/rest/v1/activities/pagingtoken.json"

    def get_paging_token(self, since_datetime: str) -> str:
        """Get a paging token for activity queries.

        Args:
            since_datetime: ISO 8601 datetime string (e.g., "2025-01-01T00:00:00Z").

        Returns:
            A paging token string for use with the get() method.
        """
        response = self._get(
            self.PAGING_TOKEN_ENDPOINT,
            params={"sinceDatetime": since_datetime},
        )
        return response.get("nextPageToken", "")

    def get(
        self,
        activity_type_ids: list[int],
        since_datetime: str | None = None,
        next_page_token: str | None = None,
        lead_ids: list[int] | None = None,
        batch_size: int = 300,
        collect: bool = True,
    ) -> list[dict[str, Any]]:
        """Get lead activities.

        Args:
            activity_type_ids: List of activity type IDs to filter.
            since_datetime: ISO datetime to start from (used to get paging token).
            next_page_token: An existing paging token (overrides since_datetime).
            lead_ids: Optional list of lead IDs to filter.
            batch_size: Number of results per page (max 300).
            collect: If True, collects all pages. If False, returns first page only.

        Returns:
            List of activity records.
        """
        if not next_page_token:
            if not since_datetime:
                raise ValueError("Either since_datetime or next_page_token is required")
            next_page_token = self.get_paging_token(since_datetime)

        params: dict[str, Any] = {
            "activityTypeIds": ",".join(str(t) for t in activity_type_ids),
            "nextPageToken": next_page_token,
            "batchSize": min(batch_size, 300),
        }
        if lead_ids:
            params["leadIds"] = ",".join(str(lid) for lid in lead_ids)

        if collect:
            return collect_all(
                paginate_with_token(self._get, self.ENDPOINT, params=params)
            )
        else:
            response = self._get(self.ENDPOINT, params=params)
            return response.get("result", [])

    def get_types(self) -> list[dict[str, Any]]:
        """Get all available activity types.

        Returns:
            List of activity type descriptors with id, name, and attributes.
        """
        response = self._get(self.TYPES_ENDPOINT)
        return response.get("result", [])
