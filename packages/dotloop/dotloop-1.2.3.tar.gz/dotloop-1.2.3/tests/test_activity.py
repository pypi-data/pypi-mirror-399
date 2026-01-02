"""Tests for the ActivityClient."""

import pytest
import responses

from dotloop.activity import ActivityClient
from dotloop.exceptions import AuthenticationError, DotloopError, NotFoundError


class TestActivityClientInit:
    """Test ActivityClient initialization."""

    def test_init_with_api_key(self) -> None:
        """Test initialization with provided API key."""
        client = ActivityClient(api_key="test_key")
        assert client._api_key == "test_key"

    def test_init_without_api_key_raises_error(self) -> None:
        """Test initialization without API key raises error."""
        with pytest.raises(AuthenticationError):
            ActivityClient()


class TestActivityClientMethods:
    """Test ActivityClient methods."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = ActivityClient(api_key="test_key")

    @responses.activate
    def test_list_loop_activity_success(self) -> None:
        """Test successful loop activity listing."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/activity",
            json={
                "data": [
                    {
                        "id": 1,
                        "type": "DOCUMENT_UPLOADED",
                        "description": "Document uploaded: Purchase Agreement",
                        "createdDate": "2024-01-15T10:00:00Z",
                        "userId": 789,
                        "userName": "John Agent",
                    },
                    {
                        "id": 2,
                        "type": "PARTICIPANT_ADDED",
                        "description": "Participant added: Jane Buyer",
                        "createdDate": "2024-01-15T09:00:00Z",
                        "userId": 790,
                        "userName": "Sarah Agent",
                    },
                ],
                "meta": {"total": 2},
            },
            status=200,
        )

        result = self.client.list_loop_activity(profile_id=123, loop_id=456)

        assert len(result["data"]) == 2
        assert result["data"][0]["type"] == "DOCUMENT_UPLOADED"
        assert result["data"][1]["type"] == "PARTICIPANT_ADDED"

    @responses.activate
    def test_list_loop_activity_with_params(self) -> None:
        """Test loop activity listing with parameters."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/activity",
            json={
                "data": [
                    {
                        "id": 1,
                        "type": "DOCUMENT_UPLOADED",
                        "description": "Recent document upload",
                        "createdDate": "2024-01-15T10:00:00Z",
                    }
                ],
                "meta": {"total": 1},
            },
            status=200,
        )

        result = self.client.list_loop_activity(
            profile_id=123, loop_id=456, batch_number=1, batch_size=10
        )

        assert len(result["data"]) == 1

    @responses.activate
    def test_get_recent_activity_success(self) -> None:
        """Test successful recent activity retrieval."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/activity",
            json={
                "data": [
                    {
                        "id": 1,
                        "type": "DOCUMENT_UPLOADED",
                        "createdDate": "2024-01-15T10:00:00Z",
                    },
                    {
                        "id": 2,
                        "type": "PARTICIPANT_ADDED",
                        "createdDate": "2024-01-15T09:00:00Z",
                    },
                    {
                        "id": 3,
                        "type": "TASK_COMPLETED",
                        "createdDate": "2024-01-15T08:00:00Z",
                    },
                ],
                "meta": {"total": 3},
            },
            status=200,
        )

        result = self.client.get_recent_activity(profile_id=123, loop_id=456, limit=2)

        assert (
            len(result["data"]) == 3
        )  # get_recent_activity returns all activities from list_loop_activity

    @responses.activate
    def test_get_activity_by_type_success(self) -> None:
        """Test filtering activities by type."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/activity",
            json={
                "data": [
                    {
                        "id": 1,
                        "type": "DOCUMENT_UPLOADED",
                        "description": "Document 1 uploaded",
                    },
                    {
                        "id": 2,
                        "type": "PARTICIPANT_ADDED",
                        "description": "Participant added",
                    },
                    {
                        "id": 3,
                        "type": "DOCUMENT_UPLOADED",
                        "description": "Document 2 uploaded",
                    },
                ],
                "meta": {"total": 3},
            },
            status=200,
        )

        result = self.client.get_activity_by_type(
            profile_id=123, loop_id=456, activity_type="DOCUMENT_UPLOADED"
        )

        assert len(result["data"]) == 2
        for activity in result["data"]:
            assert activity["type"] == "DOCUMENT_UPLOADED"

    @responses.activate
    def test_get_activity_by_user_success(self) -> None:
        """Test filtering activities by user."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/activity",
            json={
                "data": [
                    {
                        "id": 1,
                        "createdBy": {"name": "John Agent"},
                        "description": "Activity 1",
                    },
                    {
                        "id": 2,
                        "createdBy": {"name": "Jane Agent"},
                        "description": "Activity 2",
                    },
                    {
                        "id": 3,
                        "createdBy": {"name": "John Agent"},
                        "description": "Activity 3",
                    },
                ],
                "meta": {"total": 3},
            },
            status=200,
        )

        result = self.client.get_activity_by_user(
            profile_id=123, loop_id=456, user_name="John Agent"
        )

        assert len(result["data"]) == 2
        for activity in result["data"]:
            assert activity["createdBy"]["name"] == "John Agent"

    @responses.activate
    def test_get_activity_summary_success(self) -> None:
        """Test activity summary generation."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/activity",
            json={
                "data": [
                    {
                        "id": 1,
                        "type": "DOCUMENT_UPLOADED",
                        "createdBy": {"name": "John Agent"},
                    },
                    {
                        "id": 2,
                        "type": "PARTICIPANT_ADDED",
                        "createdBy": {"name": "Jane Agent"},
                    },
                    {
                        "id": 3,
                        "type": "DOCUMENT_UPLOADED",
                        "createdBy": {"name": "John Agent"},
                    },
                    {
                        "id": 4,
                        "type": "TASK_COMPLETED",
                        "createdBy": {"name": "Bob Agent"},
                    },
                ],
                "meta": {"total": 4},
            },
            status=200,
        )

        result = self.client.get_activity_summary(profile_id=123, loop_id=456)

        assert result["total_activities"] == 4
        assert result["unique_users"] == 3
        assert result["most_active_user"] == "John Agent"
        assert result["activity_types"]["DOCUMENT_UPLOADED"] == 2
        assert result["activity_types"]["PARTICIPANT_ADDED"] == 1
        assert result["activity_types"]["TASK_COMPLETED"] == 1

    @responses.activate
    def test_get_activity_summary_empty(self) -> None:
        """Test activity summary with no activities."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/activity",
            json={"data": [], "meta": {"total": 0}},
            status=200,
        )

        result = self.client.get_activity_summary(profile_id=123, loop_id=456)

        assert result["total_activities"] == 0
        assert result["unique_users"] == 0
        assert result["most_active_user"] == "None"
        assert result["activity_types"] == {}

    @responses.activate
    def test_list_loop_activity_not_found(self) -> None:
        """Test loop activity listing with not found error."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/999/activity",
            json={"message": "Loop not found"},
            status=404,
        )

        with pytest.raises(NotFoundError) as exc_info:
            self.client.list_loop_activity(profile_id=123, loop_id=999)

        assert "Resource not found" in str(exc_info.value)
        assert exc_info.value.status_code == 404
