"""Campaigns resource — trigger and manage smart campaigns.

Reference: https://developers.marketo.com/rest-api/assets/smart-campaigns/
"""

from __future__ import annotations

from typing import Any

from marketo_api.resources.base import BaseResource
from marketo_api.utils.pagination import collect_all, paginate_with_offset


class CampaignsResource(BaseResource):
    """Operations on Marketo smart campaigns."""

    ENDPOINT = "/rest/v1/campaigns.json"

    def get(
        self,
        campaign_ids: list[int] | None = None,
        names: list[str] | None = None,
        program_names: list[str] | None = None,
        workspace_names: list[str] | None = None,
        batch_size: int = 200,
    ) -> list[dict[str, Any]]:
        """Get smart campaigns with optional filters.

        Args:
            campaign_ids: Filter by campaign IDs.
            names: Filter by campaign names.
            program_names: Filter by parent program names.
            workspace_names: Filter by workspace names.
            batch_size: Results per page (max 200).

        Returns:
            List of campaign records.
        """
        params: dict[str, Any] = {}
        if campaign_ids:
            params["id"] = ",".join(str(c) for c in campaign_ids)
        if names:
            params["name"] = ",".join(names)
        if program_names:
            params["programName"] = ",".join(program_names)
        if workspace_names:
            params["workspaceName"] = ",".join(workspace_names)

        return collect_all(
            paginate_with_offset(
                self._get,
                self.ENDPOINT,
                params=params,
                max_return=batch_size,
            )
        )

    def trigger(
        self,
        campaign_id: int,
        leads: list[dict[str, Any]],
        tokens: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Request (trigger) a smart campaign for specific leads.

        Args:
            campaign_id: The ID of the triggerable smart campaign.
            leads: List of lead dicts, e.g., [{"id": 5}].
            tokens: Optional My Tokens to override for this execution.

        Returns:
            API response confirming the trigger.
        """
        endpoint = f"/rest/v1/campaigns/{campaign_id}/trigger.json"
        body: dict[str, Any] = {"input": {"leads": leads}}
        if tokens:
            body["input"]["tokens"] = tokens

        return self._post(endpoint, json_body=body)

    def schedule(
        self,
        campaign_id: int,
        run_at: str | None = None,
        clone_to_program_name: str | None = None,
        tokens: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Schedule a batch campaign.

        Args:
            campaign_id: The ID of the batch smart campaign.
            run_at: ISO 8601 datetime for when to run.
            clone_to_program_name: If provided, clones to a new program first.
            tokens: Optional My Tokens to override.

        Returns:
            API response confirming the schedule.
        """
        endpoint = f"/rest/v1/campaigns/{campaign_id}/schedule.json"
        body: dict[str, Any] = {"input": {}}
        if run_at:
            body["input"]["runAt"] = run_at
        if clone_to_program_name:
            body["input"]["cloneToProgramName"] = clone_to_program_name
        if tokens:
            body["input"]["tokens"] = tokens

        return self._post(endpoint, json_body=body)
