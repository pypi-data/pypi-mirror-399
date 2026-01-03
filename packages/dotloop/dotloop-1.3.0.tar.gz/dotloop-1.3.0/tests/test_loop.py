"""Tests for the LoopClient."""

import pytest
import responses

from dotloop.enums import LoopStatus, SortDirection, TransactionType
from dotloop.exceptions import AuthenticationError, DotloopError, NotFoundError
from dotloop.loop import LoopClient


class TestLoopClientInit:
    """Test LoopClient initialization."""

    def test_init_with_api_key(self) -> None:
        """Test initialization with provided API key."""
        client = LoopClient(api_key="test_key")
        assert client._api_key == "test_key"

    def test_init_without_api_key_raises_error(self) -> None:
        """Test initialization without API key raises error."""
        with pytest.raises(AuthenticationError):
            LoopClient()


class TestLoopClientMethods:
    """Test LoopClient methods."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = LoopClient(api_key="test_key")

    @responses.activate
    def test_list_loops_success(self) -> None:
        """Test successful loops listing."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop",
            json={
                "data": [
                    {
                        "id": 1,
                        "name": "123 Main St Purchase",
                        "status": "PRE_OFFER",
                        "transactionType": "PURCHASE_OFFER",
                        "created": "2024-01-15T10:00:00Z",
                    },
                    {
                        "id": 2,
                        "name": "456 Oak Ave Listing",
                        "status": "ACTIVE",
                        "transactionType": "LISTING_AGREEMENT",
                        "created": "2024-01-14T09:00:00Z",
                    },
                ],
                "meta": {"total": 2},
            },
            status=200,
        )

        result = self.client.list_loops(profile_id=123)

        assert len(result["data"]) == 2
        assert result["data"][0]["name"] == "123 Main St Purchase"
        assert result["data"][1]["transactionType"] == "LISTING_AGREEMENT"

    @responses.activate
    def test_list_loops_with_params(self) -> None:
        """Test loops listing with query parameters."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop",
            json={
                "data": [{"id": 1, "name": "Active Loop", "status": "ACTIVE"}],
                "meta": {"total": 1},
            },
            status=200,
        )

        result = self.client.list_loops(
            profile_id=123, batch_number=1, batch_size=10, sort="name:asc"
        )

        assert len(result["data"]) == 1

    @responses.activate
    def test_get_loop_success(self) -> None:
        """Test successful loop retrieval."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456",
            json={
                "data": {
                    "id": 456,
                    "name": "123 Main St Purchase",
                    "status": "PRE_OFFER",
                    "transactionType": "PURCHASE_OFFER",
                    "created": "2024-01-15T10:00:00Z",
                    "loopUrl": "https://dotloop.com/loop/456",
                }
            },
            status=200,
        )

        result = self.client.get_loop(profile_id=123, loop_id=456)

        assert result["data"]["name"] == "123 Main St Purchase"
        assert result["data"]["status"] == "PRE_OFFER"
        assert result["data"]["transactionType"] == "PURCHASE_OFFER"

    @responses.activate
    def test_get_loop_not_found(self) -> None:
        """Test loop retrieval with not found error."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/999",
            json={"message": "Loop not found"},
            status=404,
        )

        with pytest.raises(NotFoundError) as exc_info:
            self.client.get_loop(profile_id=123, loop_id=999)

        assert "Resource not found" in str(exc_info.value)
        assert exc_info.value.status_code == 404

    @responses.activate
    def test_create_loop_success(self) -> None:
        """Test successful loop creation."""
        responses.add(
            responses.POST,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop",
            json={
                "data": {
                    "id": 999,
                    "name": "New Transaction Loop",
                    "status": "PRE_OFFER",
                    "transactionType": "PURCHASE_OFFER",
                    "loopUrl": "https://dotloop.com/loop/999",
                }
            },
            status=201,
        )

        result = self.client.create_loop(
            profile_id=123,
            name="New Transaction Loop",
            transaction_type=TransactionType.PURCHASE_OFFER,
            status=LoopStatus.PRE_OFFER,
        )

        assert result["data"]["name"] == "New Transaction Loop"
        assert result["data"]["transactionType"] == "PURCHASE_OFFER"
        assert result["data"]["status"] == "PRE_OFFER"

    @responses.activate
    def test_create_loop_with_string_enums(self) -> None:
        """Test loop creation with string enum values."""
        responses.add(
            responses.POST,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop",
            json={
                "data": {
                    "id": 999,
                    "name": "String Enum Loop",
                    "status": "ACTIVE",
                    "transactionType": "LISTING_AGREEMENT",
                }
            },
            status=201,
        )

        result = self.client.create_loop(
            profile_id=123,
            name="String Enum Loop",
            transaction_type="LISTING_AGREEMENT",
            status="ACTIVE",
        )

        assert result["data"]["transactionType"] == "LISTING_AGREEMENT"
        assert result["data"]["status"] == "ACTIVE"

    @responses.activate
    def test_update_loop_success(self) -> None:
        """Test successful loop update."""
        responses.add(
            responses.PATCH,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456",
            json={
                "data": {
                    "id": 456,
                    "name": "Updated Loop Name",
                    "status": "SOLD",
                    "transactionType": "PURCHASE_OFFER",
                }
            },
            status=200,
        )

        result = self.client.update_loop(
            profile_id=123,
            loop_id=456,
            name="Updated Loop Name",
            status=LoopStatus.SOLD,
        )

        assert result["data"]["name"] == "Updated Loop Name"
        assert result["data"]["status"] == "SOLD"

    @responses.activate
    def test_update_loop_partial(self) -> None:
        """Test partial loop update."""
        responses.add(
            responses.PATCH,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456",
            json={
                "data": {
                    "id": 456,
                    "name": "123 Main St Purchase",
                    "status": "UNDER_CONTRACT",
                    "transactionType": "PURCHASE_OFFER",
                }
            },
            status=200,
        )

        result = self.client.update_loop(
            profile_id=123, loop_id=456, status=LoopStatus.UNDER_CONTRACT
        )

        assert result["data"]["status"] == "UNDER_CONTRACT"
