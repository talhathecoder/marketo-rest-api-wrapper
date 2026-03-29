"""Tokens resource — manage My Tokens on programs and folders.

Reference: https://developers.marketo.com/rest-api/assets/tokens/
"""

from __future__ import annotations

from typing import Any

from marketo_api.resources.base import BaseResource


class TokensResource(BaseResource):
    """Operations on Marketo My Tokens."""

    def get(
        self,
        folder_id: int,
        folder_type: str = "Program",
    ) -> list[dict[str, Any]]:
        """Get all tokens for a folder or program.

        Args:
            folder_id: The folder or program ID.
            folder_type: "Folder" or "Program".

        Returns:
            List of token records.
        """
        endpoint = f"/rest/asset/v1/folder/{folder_id}/tokens.json"
        params = {"folderType": folder_type}
        response = self._get(endpoint, params=params)
        return response.get("result", [])

    def create(
        self,
        folder_id: int,
        folder_type: str = "Program",
        name: str = "",
        type: str = "text",
        value: str = "",
    ) -> dict[str, Any]:
        """Create or update a My Token.

        Args:
            folder_id: The folder or program ID.
            folder_type: "Folder" or "Program".
            name: Token name (e.g., "{{my.event-date}}").
            type: Token type ("text", "date", "rich text", "score", etc.).
            value: Token value.

        Returns:
            API response with the created/updated token.
        """
        endpoint = f"/rest/asset/v1/folder/{folder_id}/tokens.json"
        body: dict[str, Any] = {
            "folderType": folder_type,
            "name": name,
            "type": type,
            "value": value,
        }
        return self._post(endpoint, json_body=body)

    def delete(
        self,
        folder_id: int,
        folder_type: str = "Program",
        name: str = "",
        type: str = "text",
    ) -> dict[str, Any]:
        """Delete a My Token.

        Args:
            folder_id: The folder or program ID.
            folder_type: "Folder" or "Program".
            name: Token name to delete.
            type: Token type.

        Returns:
            API response confirming deletion.
        """
        endpoint = f"/rest/asset/v1/folder/{folder_id}/tokens/delete.json"
        body: dict[str, Any] = {
            "folderType": folder_type,
            "name": name,
            "type": type,
        }
        return self._post(endpoint, json_body=body)
