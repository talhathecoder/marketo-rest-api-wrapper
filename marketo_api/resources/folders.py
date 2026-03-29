"""Folders resource — navigate and manage the Marketo folder tree.

Reference: https://developers.marketo.com/rest-api/assets/folders/
"""

from __future__ import annotations

from typing import Any

from marketo_api.resources.base import BaseResource
from marketo_api.utils.pagination import collect_all, paginate_with_offset


class FoldersResource(BaseResource):
    """Operations on Marketo folders."""

    ENDPOINT = "/rest/asset/v1/folders.json"

    def get_by_id(
        self,
        folder_id: int,
        folder_type: str = "Folder",
    ) -> dict[str, Any] | None:
        """Get a folder by ID.

        Args:
            folder_id: The folder ID.
            folder_type: "Folder" or "Program".

        Returns:
            Folder record dict, or None if not found.
        """
        endpoint = f"/rest/asset/v1/folder/{folder_id}.json"
        params = {"type": folder_type}
        response = self._get(endpoint, params=params)
        results = response.get("result", [])
        return results[0] if results else None

    def get_by_name(
        self,
        name: str,
        folder_type: str | None = None,
        root_folder_id: int | None = None,
        workspace: str | None = None,
    ) -> dict[str, Any] | None:
        """Get a folder by name.

        Args:
            name: Exact folder name.
            folder_type: Optional type filter ("Folder" or "Program").
            root_folder_id: Optional root folder to search within.
            workspace: Optional workspace name.

        Returns:
            Folder record dict, or None if not found.
        """
        endpoint = "/rest/asset/v1/folder/byName.json"
        params: dict[str, Any] = {"name": name}
        if folder_type:
            params["type"] = folder_type
        if root_folder_id:
            params["root"] = root_folder_id
        if workspace:
            params["workSpace"] = workspace

        response = self._get(endpoint, params=params)
        results = response.get("result", [])
        return results[0] if results else None

    def get_contents(
        self,
        folder_id: int,
        max_return: int = 200,
    ) -> list[dict[str, Any]]:
        """Get the contents of a folder.

        Args:
            folder_id: The folder ID.
            max_return: Results per page.

        Returns:
            List of folder content records (sub-folders, programs, assets).
        """
        endpoint = f"/rest/asset/v1/folder/{folder_id}/content.json"
        return collect_all(
            paginate_with_offset(
                self._get, endpoint, max_return=max_return
            )
        )

    def create(
        self,
        name: str,
        parent_id: int,
        parent_type: str = "Folder",
        description: str = "",
    ) -> dict[str, Any]:
        """Create a new folder.

        Args:
            name: Folder name.
            parent_id: Parent folder ID.
            parent_type: Parent type ("Folder" or "Program").
            description: Optional description.

        Returns:
            Created folder record.
        """
        body: dict[str, Any] = {
            "name": name,
            "parent": {"id": parent_id, "type": parent_type},
        }
        if description:
            body["description"] = description

        response = self._post(self.ENDPOINT, json_body=body)
        results = response.get("result", [])
        return results[0] if results else response

    def delete(self, folder_id: int) -> dict[str, Any]:
        """Delete a folder (must be empty).

        Args:
            folder_id: The folder ID to delete.

        Returns:
            API response confirming deletion.
        """
        endpoint = f"/rest/asset/v1/folder/{folder_id}/delete.json"
        return self._post(endpoint)
