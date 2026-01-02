"""Tests for the FolderClient."""

import pytest
import responses

from dotloop.exceptions import AuthenticationError, DotloopError, NotFoundError
from dotloop.folder import FolderClient


class TestFolderClientInit:
    """Test FolderClient initialization."""

    def test_init_with_api_key(self) -> None:
        """Test initialization with provided API key."""
        client = FolderClient(api_key="test_key")
        assert client._api_key == "test_key"

    def test_init_without_api_key_raises_error(self) -> None:
        """Test initialization without API key raises error."""
        with pytest.raises(AuthenticationError):
            FolderClient()


class TestFolderClientMethods:
    """Test FolderClient methods."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = FolderClient(api_key="test_key")

    @responses.activate
    def test_list_folders_success(self) -> None:
        """Test successful folders listing."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/folder",
            json={
                "data": [
                    {
                        "id": 1,
                        "name": "Purchase Agreement",
                        "created": "2024-01-15T10:00:00Z",
                        "documentCount": 5,
                    },
                    {
                        "id": 2,
                        "name": "Inspection Reports",
                        "created": "2024-01-14T09:00:00Z",
                        "documentCount": 3,
                    },
                ],
                "meta": {"total": 2},
            },
            status=200,
        )

        result = self.client.list_folders(profile_id=123, loop_id=456)

        assert len(result["data"]) == 2
        assert result["data"][0]["name"] == "Purchase Agreement"
        assert result["data"][1]["name"] == "Inspection Reports"

    @responses.activate
    def test_get_folder_success(self) -> None:
        """Test successful folder retrieval."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/folder/789",
            json={
                "data": {
                    "id": 789,
                    "name": "Purchase Agreement",
                    "created": "2024-01-15T10:00:00Z",
                    "documentCount": 5,
                    "description": "All purchase agreement documents",
                }
            },
            status=200,
        )

        result = self.client.get_folder(profile_id=123, loop_id=456, folder_id=789)

        assert result["data"]["name"] == "Purchase Agreement"
        assert result["data"]["documentCount"] == 5
        assert result["data"]["description"] == "All purchase agreement documents"

    @responses.activate
    def test_create_folder_success(self) -> None:
        """Test successful folder creation."""
        responses.add(
            responses.POST,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/folder",
            json={
                "data": {
                    "id": 999,
                    "name": "New Folder",
                    "created": "2024-01-15T12:00:00Z",
                    "documentCount": 0,
                }
            },
            status=201,
        )

        result = self.client.create_folder(
            profile_id=123, loop_id=456, name="New Folder"
        )

        assert result["data"]["name"] == "New Folder"
        assert result["data"]["documentCount"] == 0

    @responses.activate
    def test_update_folder_success(self) -> None:
        """Test successful folder update."""
        responses.add(
            responses.PATCH,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/folder/789",
            json={
                "data": {
                    "id": 789,
                    "name": "Updated Folder Name",
                    "created": "2024-01-15T10:00:00Z",
                    "documentCount": 5,
                }
            },
            status=200,
        )

        result = self.client.update_folder(
            profile_id=123, loop_id=456, folder_id=789, name="Updated Folder Name"
        )

        assert result["data"]["name"] == "Updated Folder Name"

    @responses.activate
    def test_get_folder_not_found(self) -> None:
        """Test folder retrieval with not found error."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/folder/999",
            json={"message": "Folder not found"},
            status=404,
        )

        with pytest.raises(NotFoundError) as exc_info:
            self.client.get_folder(profile_id=123, loop_id=456, folder_id=999)

        assert "Resource not found" in str(exc_info.value)
        assert exc_info.value.status_code == 404
