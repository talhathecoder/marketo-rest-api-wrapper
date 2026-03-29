"""Programs resource — manage Marketo programs.

Reference: https://developers.marketo.com/rest-api/assets/programs/
"""

from __future__ import annotations

from typing import Any

from marketo_api.resources.base import BaseResource
from marketo_api.utils.pagination import collect_all, paginate_with_offset


class ProgramsResource(BaseResource):
    """Operations on Marketo programs."""

    ENDPOINT = "/rest/asset/v1/programs.json"

    def get(
        self,
        max_return: int = 200,
        offset: int = 0,
        status: str | None = None,
        workspace: str | None = None,
    ) -> list[dict[str, Any]]:
        """Browse programs with optional filters.

        Args:
            max_return: Results per page.
            offset: Starting offset.
            status: Filter by status (e.g., "active").
            workspace: Filter by workspace name.

        Returns:
            List of program records.
        """
        params: dict[str, Any] = {"offset": offset}
        if status:
            params["status"] = status
        if workspace:
            params["workspace"] = workspace

        return collect_all(
            paginate_with_offset(
                self._get, self.ENDPOINT, params=params, max_return=max_return
            )
        )

    def get_by_id(self, program_id: int) -> dict[str, Any] | None:
        """Get a program by ID.

        Args:
            program_id: The program ID.

        Returns:
            Program record dict, or None if not found.
        """
        endpoint = f"/rest/asset/v1/program/{program_id}.json"
        response = self._get(endpoint)
        results = response.get("result", [])
        return results[0] if results else None

    def get_by_name(self, name: str) -> dict[str, Any] | None:
        """Get a program by name.

        Args:
            name: Exact program name.

        Returns:
            Program record dict, or None if not found.
        """
        endpoint = "/rest/asset/v1/program/byName.json"
        response = self._get(endpoint, params={"name": name})
        results = response.get("result", [])
        return results[0] if results else None

    def create(
        self,
        name: str,
        folder: dict[str, Any],
        program_type: str,
        channel: str,
        description: str = "",
    ) -> dict[str, Any]:
        """Create a new program.

        Args:
            name: Program name.
            folder: Folder dict, e.g., {"id": 50, "type": "Folder"}.
            program_type: Type of program (e.g., "Default", "Event", "Email").
            channel: Channel name (e.g., "Webinar", "Content").
            description: Optional description.

        Returns:
            Created program record.
        """
        body: dict[str, Any] = {
            "name": name,
            "folder": folder,
            "type": program_type,
            "channel": channel,
        }
        if description:
            body["description"] = description

        response = self._post(self.ENDPOINT, json_body=body)
        results = response.get("result", [])
        return results[0] if results else response

    def update(
        self,
        program_id: int,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Update a program's metadata.

        Args:
            program_id: The program ID.
            **kwargs: Fields to update (name, description, etc.).

        Returns:
            Updated program record.
        """
        endpoint = f"/rest/asset/v1/program/{program_id}.json"
        return self._post(endpoint, json_body=kwargs)

    def clone(
        self,
        program_id: int,
        name: str,
        folder: dict[str, Any],
        description: str = "",
    ) -> dict[str, Any]:
        """Clone a program.

        Args:
            program_id: Source program ID.
            name: Name for the clone.
            folder: Target folder dict.
            description: Optional description for the clone.

        Returns:
            Cloned program record.
        """
        endpoint = f"/rest/asset/v1/program/{program_id}/clone.json"
        body: dict[str, Any] = {
            "name": name,
            "folder": folder,
        }
        if description:
            body["description"] = description

        response = self._post(endpoint, json_body=body)
        results = response.get("result", [])
        return results[0] if results else response

    def get_members(
        self,
        program_id: int,
        max_return: int = 200,
        fields: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Get program members.

        Args:
            program_id: The program ID.
            max_return: Results per page.
            fields: Optional list of fields to return.

        Returns:
            List of program member records.
        """
        endpoint = f"/rest/v1/programs/{program_id}/members.json"
        params: dict[str, Any] = {}
        if fields:
            params["fields"] = ",".join(fields)

        return collect_all(
            paginate_with_offset(
                self._get, endpoint, params=params, max_return=max_return
            )
        )
