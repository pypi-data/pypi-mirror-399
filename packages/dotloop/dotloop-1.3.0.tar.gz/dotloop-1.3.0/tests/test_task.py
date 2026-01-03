"""Tests for the TaskClient."""

import pytest
import responses

from dotloop.exceptions import AuthenticationError, DotloopError, NotFoundError
from dotloop.task import TaskClient


class TestTaskClientInit:
    """Test TaskClient initialization."""

    def test_init_with_api_key(self) -> None:
        """Test initialization with provided API key."""
        client = TaskClient(api_key="test_key")
        assert client._api_key == "test_key"

    def test_init_without_api_key_raises_error(self) -> None:
        """Test initialization without API key raises error."""
        with pytest.raises(AuthenticationError):
            TaskClient()


class TestTaskClientMethods:
    """Test TaskClient methods."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = TaskClient(api_key="test_key")

    @responses.activate
    def test_list_task_lists_success(self) -> None:
        """Test successful task lists listing."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/tasklist",
            json={
                "data": [
                    {
                        "id": 1,
                        "name": "Pre-Listing",
                        "description": "Tasks before listing",
                    },
                    {
                        "id": 2,
                        "name": "Under Contract",
                        "description": "Tasks after contract",
                    },
                ],
                "meta": {"total": 2},
            },
            status=200,
        )

        result = self.client.list_task_lists(profile_id=123, loop_id=456)

        assert len(result["data"]) == 2
        assert result["data"][0]["name"] == "Pre-Listing"
        assert result["data"][1]["name"] == "Under Contract"

    @responses.activate
    def test_get_task_list_success(self) -> None:
        """Test successful task list retrieval."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/tasklist/789",
            json={
                "data": {
                    "id": 789,
                    "name": "Pre-Listing",
                    "description": "Tasks before listing",
                    "taskCount": 5,
                }
            },
            status=200,
        )

        result = self.client.get_task_list(profile_id=123, loop_id=456, tasklist_id=789)

        assert result["data"]["name"] == "Pre-Listing"
        assert result["data"]["taskCount"] == 5

    @responses.activate
    def test_list_tasks_success(self) -> None:
        """Test successful tasks listing."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/tasklist/789/task",
            json={
                "data": [
                    {
                        "id": 1,
                        "name": "Order CMA",
                        "status": "PENDING",
                        "dueDate": "2024-01-15",
                    },
                    {
                        "id": 2,
                        "name": "Schedule Photos",
                        "status": "COMPLETE",
                        "completedDate": "2024-01-10",
                    },
                ],
                "meta": {"total": 2},
            },
            status=200,
        )

        result = self.client.list_tasks(profile_id=123, loop_id=456, tasklist_id=789)

        assert len(result["data"]) == 2
        assert result["data"][0]["name"] == "Order CMA"
        assert result["data"][0]["status"] == "PENDING"
        assert result["data"][1]["status"] == "COMPLETE"

    @responses.activate
    def test_get_task_success(self) -> None:
        """Test successful task retrieval."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/tasklist/789/task/101",
            json={
                "data": {
                    "id": 101,
                    "name": "Order CMA",
                    "status": "PENDING",
                    "dueDate": "2024-01-15",
                    "description": "Order comparative market analysis",
                }
            },
            status=200,
        )

        result = self.client.get_task(
            profile_id=123, loop_id=456, tasklist_id=789, task_id=101
        )

        assert result["data"]["name"] == "Order CMA"
        assert result["data"]["status"] == "PENDING"
        assert result["data"]["dueDate"] == "2024-01-15"

    @responses.activate
    def test_get_all_tasks_in_loop_success(self) -> None:
        """Test successful retrieval of all tasks in a loop."""
        # Mock task lists
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/tasklist",
            json={
                "data": [
                    {"id": 1, "name": "Pre-Listing"},
                    {"id": 2, "name": "Under Contract"},
                ],
                "meta": {"total": 2},
            },
            status=200,
        )

        # Mock tasks for first task list
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/tasklist/1/task",
            json={
                "data": [
                    {"id": 1, "name": "Task 1", "status": "PENDING"},
                    {"id": 2, "name": "Task 2", "status": "COMPLETE"},
                ],
                "meta": {"total": 2},
            },
            status=200,
        )

        # Mock tasks for second task list
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/tasklist/2/task",
            json={
                "data": [{"id": 3, "name": "Task 3", "status": "PENDING"}],
                "meta": {"total": 1},
            },
            status=200,
        )

        result = self.client.get_all_tasks_in_loop(profile_id=123, loop_id=456)

        assert "Pre-Listing" in result
        assert "Under Contract" in result
        assert len(result["Pre-Listing"]) == 2
        assert len(result["Under Contract"]) == 1

    @responses.activate
    def test_get_task_summary_success(self) -> None:
        """Test successful task summary generation."""
        # Mock the get_all_tasks_in_loop method
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/tasklist",
            json={"data": [{"id": 1, "name": "Test List"}], "meta": {"total": 1}},
            status=200,
        )

        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/tasklist/1/task",
            json={
                "data": [
                    {"id": 1, "name": "Task 1", "status": "COMPLETE"},
                    {"id": 2, "name": "Task 2", "status": "PENDING"},
                    {"id": 3, "name": "Task 3", "status": "PENDING"},
                ],
                "meta": {"total": 3},
            },
            status=200,
        )

        result = self.client.get_task_summary(profile_id=123, loop_id=456)

        assert result["total_tasks"] == 3
        assert result["completed_tasks"] == 1
        assert result["pending_tasks"] == 2
        assert abs(result["completion_percentage"] - 33.333333333333336) < 0.001

    @responses.activate
    def test_get_task_list_not_found(self) -> None:
        """Test task list retrieval with not found error."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/tasklist/789",
            json={"message": "Task list not found"},
            status=404,
        )

        with pytest.raises(NotFoundError) as exc_info:
            self.client.get_task_list(profile_id=123, loop_id=456, tasklist_id=789)

        assert "Resource not found" in str(exc_info.value)
        assert exc_info.value.status_code == 404

    @responses.activate
    def test_get_pending_tasks_success(self) -> None:
        """Test getting pending tasks."""
        # Mock task lists
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/tasklist",
            json={
                "data": [
                    {"id": 1, "name": "Pre-Closing Tasks"},
                    {"id": 2, "name": "Closing Tasks"},
                ],
                "meta": {"total": 2},
            },
            status=200,
        )

        # Mock tasks for first task list
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/tasklist/1/task",
            json={
                "data": [
                    {"id": 1, "name": "Task 1", "status": "PENDING"},
                    {"id": 2, "name": "Task 2", "status": "COMPLETE"},
                ],
                "meta": {"total": 2},
            },
            status=200,
        )

        # Mock tasks for second task list
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/tasklist/2/task",
            json={
                "data": [
                    {"id": 3, "name": "Task 3", "status": "IN_PROGRESS"},
                    {"id": 4, "name": "Task 4", "status": "DONE"},
                ],
                "meta": {"total": 2},
            },
            status=200,
        )

        result = self.client.get_pending_tasks(profile_id=123, loop_id=456)

        assert "Pre-Closing Tasks" in result
        assert "Closing Tasks" in result
        assert len(result["Pre-Closing Tasks"]) == 1  # Only pending task
        assert len(result["Closing Tasks"]) == 1  # Only in-progress task
        assert result["Pre-Closing Tasks"][0]["status"] == "PENDING"
        assert result["Closing Tasks"][0]["status"] == "IN_PROGRESS"

    @responses.activate
    def test_get_completed_tasks_success(self) -> None:
        """Test getting completed tasks."""
        # Mock task lists
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/tasklist",
            json={
                "data": [
                    {"id": 1, "name": "Pre-Closing Tasks"},
                    {"id": 2, "name": "Closing Tasks"},
                ],
                "meta": {"total": 2},
            },
            status=200,
        )

        # Mock tasks for first task list
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/tasklist/1/task",
            json={
                "data": [
                    {"id": 1, "name": "Task 1", "status": "PENDING"},
                    {"id": 2, "name": "Task 2", "status": "COMPLETE"},
                ],
                "meta": {"total": 2},
            },
            status=200,
        )

        # Mock tasks for second task list
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/tasklist/2/task",
            json={
                "data": [
                    {"id": 3, "name": "Task 3", "status": "IN_PROGRESS"},
                    {"id": 4, "name": "Task 4", "status": "COMPLETED"},
                ],
                "meta": {"total": 2},
            },
            status=200,
        )

        result = self.client.get_completed_tasks(profile_id=123, loop_id=456)

        assert "Pre-Closing Tasks" in result
        assert "Closing Tasks" in result
        assert len(result["Pre-Closing Tasks"]) == 1  # Only completed task
        assert len(result["Closing Tasks"]) == 1  # Only completed task
        assert result["Pre-Closing Tasks"][0]["status"] == "COMPLETE"
        assert result["Closing Tasks"][0]["status"] == "COMPLETED"

    @responses.activate
    def test_get_pending_tasks_empty(self) -> None:
        """Test getting pending tasks when all are complete."""
        # Mock task lists
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/tasklist",
            json={
                "data": [{"id": 1, "name": "All Complete Tasks"}],
                "meta": {"total": 1},
            },
            status=200,
        )

        # Mock tasks - all complete
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/tasklist/1/task",
            json={
                "data": [
                    {"id": 1, "name": "Task 1", "status": "COMPLETE"},
                    {"id": 2, "name": "Task 2", "status": "DONE"},
                ],
                "meta": {"total": 2},
            },
            status=200,
        )

        result = self.client.get_pending_tasks(profile_id=123, loop_id=456)

        assert result == {}  # No pending tasks

    @responses.activate
    def test_get_completed_tasks_empty(self) -> None:
        """Test getting completed tasks when none are complete."""
        # Mock task lists
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/tasklist",
            json={
                "data": [{"id": 1, "name": "All Pending Tasks"}],
                "meta": {"total": 1},
            },
            status=200,
        )

        # Mock tasks - all pending
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/tasklist/1/task",
            json={
                "data": [
                    {"id": 1, "name": "Task 1", "status": "PENDING"},
                    {"id": 2, "name": "Task 2", "status": "IN_PROGRESS"},
                ],
                "meta": {"total": 2},
            },
            status=200,
        )

        result = self.client.get_completed_tasks(profile_id=123, loop_id=456)

        assert result == {}  # No completed tasks

    @responses.activate
    def test_get_task_summary_with_zero_tasks(self) -> None:
        """Test task summary with zero tasks."""
        # Mock empty task lists
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/tasklist",
            json={"data": [], "meta": {"total": 0}},
            status=200,
        )

        result = self.client.get_task_summary(profile_id=123, loop_id=456)

        assert result["total_tasks"] == 0
        assert result["completed_tasks"] == 0
        assert result["pending_tasks"] == 0
        assert result["completion_percentage"] == 0
        assert result["task_lists"] == {}
