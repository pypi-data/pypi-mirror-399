"""Tests for the ParticipantClient."""

import pytest
import responses

from dotloop.enums import ParticipantRole
from dotloop.exceptions import AuthenticationError, DotloopError, NotFoundError
from dotloop.participant import ParticipantClient


class TestParticipantClientInit:
    """Test ParticipantClient initialization."""

    def test_init_with_api_key(self) -> None:
        """Test initialization with provided API key."""
        client = ParticipantClient(api_key="test_key")
        assert client._api_key == "test_key"

    def test_init_without_api_key_raises_error(self) -> None:
        """Test initialization without API key raises error."""
        with pytest.raises(AuthenticationError):
            ParticipantClient()


class TestParticipantClientMethods:
    """Test ParticipantClient methods."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = ParticipantClient(api_key="test_key")

    @responses.activate
    def test_list_participants_success(self) -> None:
        """Test successful participants listing."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/participant",
            json={
                "data": [
                    {
                        "id": 1,
                        "fullName": "John Buyer",
                        "email": "john@example.com",
                        "role": "BUYER",
                    },
                    {
                        "id": 2,
                        "fullName": "Jane Agent",
                        "email": "jane@realty.com",
                        "role": "BUYING_AGENT",
                    },
                ],
                "meta": {"total": 2},
            },
            status=200,
        )

        result = self.client.list_participants(profile_id=123, loop_id=456)

        assert len(result["data"]) == 2
        assert result["data"][0]["fullName"] == "John Buyer"
        assert result["data"][0]["role"] == "BUYER"

    @responses.activate
    def test_get_participant_success(self) -> None:
        """Test successful participant retrieval."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/participant/789",
            json={
                "data": {
                    "id": 789,
                    "fullName": "John Buyer",
                    "email": "john@example.com",
                    "role": "BUYER",
                    "phone": "+1 (555) 123-4567",
                }
            },
            status=200,
        )

        result = self.client.get_participant(
            profile_id=123, loop_id=456, participant_id=789
        )

        assert result["data"]["fullName"] == "John Buyer"
        assert result["data"]["role"] == "BUYER"

    @responses.activate
    def test_add_participant_success(self) -> None:
        """Test successful participant addition."""
        responses.add(
            responses.POST,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/participant",
            json={
                "data": {
                    "id": 999,
                    "fullName": "New Participant",
                    "email": "new@example.com",
                    "role": "BUYER",
                    "phone": "+1 (555) 999-9999",
                }
            },
            status=201,
        )

        result = self.client.add_participant(
            profile_id=123,
            loop_id=456,
            full_name="New Participant",
            email="new@example.com",
            role=ParticipantRole.BUYER,
            phone="+1 (555) 999-9999",
        )

        assert result["data"]["fullName"] == "New Participant"
        assert result["data"]["role"] == "BUYER"

    @responses.activate
    def test_add_participant_with_string_role(self) -> None:
        """Test participant addition with string role."""
        responses.add(
            responses.POST,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/participant",
            json={
                "data": {
                    "id": 999,
                    "fullName": "New Participant",
                    "email": "new@example.com",
                    "role": "SELLER",
                }
            },
            status=201,
        )

        result = self.client.add_participant(
            profile_id=123,
            loop_id=456,
            full_name="New Participant",
            email="new@example.com",
            role="SELLER",
        )

        assert result["data"]["role"] == "SELLER"

    @responses.activate
    def test_update_participant_success(self) -> None:
        """Test successful participant update."""
        responses.add(
            responses.PATCH,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/participant/789",
            json={
                "data": {
                    "id": 789,
                    "fullName": "Updated Name",
                    "email": "updated@example.com",
                    "role": "BUYER",
                    "phone": "+1 (555) 888-8888",
                }
            },
            status=200,
        )

        result = self.client.update_participant(
            profile_id=123,
            loop_id=456,
            participant_id=789,
            full_name="Updated Name",
            phone="+1 (555) 888-8888",
        )

        assert result["data"]["fullName"] == "Updated Name"
        assert result["data"]["phone"] == "+1 (555) 888-8888"

    @responses.activate
    def test_remove_participant_success(self) -> None:
        """Test successful participant removal."""
        responses.add(
            responses.DELETE,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/participant/789",
            status=204,
        )

        result = self.client.remove_participant(
            profile_id=123, loop_id=456, participant_id=789
        )

        assert result == {}

    @responses.activate
    def test_add_buyer_convenience_method(self) -> None:
        """Test add_buyer convenience method."""
        responses.add(
            responses.POST,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/participant",
            json={
                "data": {
                    "id": 999,
                    "fullName": "John Buyer",
                    "email": "john.buyer@example.com",
                    "role": "BUYER",
                }
            },
            status=201,
        )

        result = self.client.add_buyer(
            profile_id=123,
            loop_id=456,
            full_name="John Buyer",
            email="john.buyer@example.com",
        )

        assert result["data"]["role"] == "BUYER"

    @responses.activate
    def test_add_seller_convenience_method(self) -> None:
        """Test add_seller convenience method."""
        responses.add(
            responses.POST,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/participant",
            json={
                "data": {
                    "id": 999,
                    "fullName": "Jane Seller",
                    "email": "jane.seller@example.com",
                    "role": "SELLER",
                }
            },
            status=201,
        )

        result = self.client.add_seller(
            profile_id=123,
            loop_id=456,
            full_name="Jane Seller",
            email="jane.seller@example.com",
        )

        assert result["data"]["role"] == "SELLER"

    @responses.activate
    def test_add_agent_convenience_method(self) -> None:
        """Test add_agent convenience method."""
        responses.add(
            responses.POST,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/participant",
            json={
                "data": {
                    "id": 999,
                    "fullName": "Bob Agent",
                    "email": "bob.agent@realty.com",
                    "role": "LISTING_AGENT",
                }
            },
            status=201,
        )

        result = self.client.add_agent(
            profile_id=123,
            loop_id=456,
            full_name="Bob Agent",
            email="bob.agent@realty.com",
            role=ParticipantRole.LISTING_AGENT,
        )

        assert result["data"]["role"] == "LISTING_AGENT"

    @responses.activate
    def test_get_participant_not_found(self) -> None:
        """Test participant retrieval with not found error."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/participant/789",
            json={"message": "Participant not found"},
            status=404,
        )

        with pytest.raises(NotFoundError) as exc_info:
            self.client.get_participant(profile_id=123, loop_id=456, participant_id=789)

        assert "Resource not found" in str(exc_info.value)
        assert exc_info.value.status_code == 404

    @responses.activate
    def test_add_participant_with_all_fields(self) -> None:
        """Test adding participant with all optional fields."""
        responses.add(
            responses.POST,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/participant",
            json={
                "data": {
                    "id": 999,
                    "fullName": "John Complete",
                    "email": "john.complete@example.com",
                    "role": "BUYER",
                    "phone": "+1 (555) 123-4567",
                    "company": "ABC Corp",
                    "address": "123 Main St",
                    "city": "Anytown",
                    "state": "CA",
                    "zipCode": "12345",
                    "country": "USA",
                }
            },
            status=201,
        )

        result = self.client.add_participant(
            profile_id=123,
            loop_id=456,
            full_name="John Complete",
            email="john.complete@example.com",
            role=ParticipantRole.BUYER,
            phone="+1 (555) 123-4567",
            company="ABC Corp",
            address="123 Main St",
            city="Anytown",
            state="CA",
            zip_code="12345",
            country="USA",
        )

        assert result["data"]["fullName"] == "John Complete"
        assert result["data"]["company"] == "ABC Corp"
        assert result["data"]["address"] == "123 Main St"

    @responses.activate
    def test_update_participant_with_all_fields(self) -> None:
        """Test updating participant with all optional fields."""
        responses.add(
            responses.PATCH,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/participant/789",
            json={
                "data": {
                    "id": 789,
                    "fullName": "John Updated",
                    "email": "john.updated@example.com",
                    "role": "SELLER",
                    "phone": "+1 (555) 987-6543",
                    "company": "XYZ Corp",
                    "address": "456 Oak Ave",
                    "city": "Newtown",
                    "state": "NY",
                    "zipCode": "54321",
                    "country": "USA",
                }
            },
            status=200,
        )

        result = self.client.update_participant(
            profile_id=123,
            loop_id=456,
            participant_id=789,
            full_name="John Updated",
            email="john.updated@example.com",
            role=ParticipantRole.SELLER,
            phone="+1 (555) 987-6543",
            company="XYZ Corp",
            address="456 Oak Ave",
            city="Newtown",
            state="NY",
            zip_code="54321",
            country="USA",
        )

        assert result["data"]["fullName"] == "John Updated"
        assert result["data"]["role"] == "SELLER"
        assert result["data"]["company"] == "XYZ Corp"

    @responses.activate
    def test_update_participant_with_string_role(self) -> None:
        """Test updating participant with string role instead of enum."""
        responses.add(
            responses.PATCH,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/participant/789",
            json={
                "data": {"id": 789, "fullName": "John Updated", "role": "CUSTOM_ROLE"}
            },
            status=200,
        )

        result = self.client.update_participant(
            profile_id=123, loop_id=456, participant_id=789, role="CUSTOM_ROLE"
        )

        assert result["data"]["role"] == "CUSTOM_ROLE"
