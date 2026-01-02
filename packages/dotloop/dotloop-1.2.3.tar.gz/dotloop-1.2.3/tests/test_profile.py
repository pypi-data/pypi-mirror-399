"""Tests for the ProfileClient."""

import pytest
import responses

from dotloop.enums import ProfileType
from dotloop.exceptions import AuthenticationError, DotloopError, NotFoundError
from dotloop.profile import ProfileClient


class TestProfileClientInit:
    """Test ProfileClient initialization."""

    def test_init_with_api_key(self) -> None:
        """Test initialization with provided API key."""
        client = ProfileClient(api_key="test_key")
        assert client._api_key == "test_key"

    def test_init_without_api_key_raises_error(self) -> None:
        """Test initialization without API key raises error."""
        with pytest.raises(AuthenticationError):
            ProfileClient()


class TestProfileClientMethods:
    """Test ProfileClient methods."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = ProfileClient(api_key="test_key")

    @responses.activate
    def test_list_profiles_success(self) -> None:
        """Test successful profiles listing."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile",
            json={
                "data": [
                    {
                        "id": 1,
                        "name": "John Doe Real Estate",
                        "type": "AGENT",
                        "email": "john@realestate.com",
                        "phone": "+1 (555) 123-4567",
                    },
                    {
                        "id": 2,
                        "name": "Premium Realty Group",
                        "type": "BROKERAGE",
                        "email": "info@premiumrealty.com",
                        "phone": "+1 (555) 987-6543",
                    },
                ],
                "meta": {"total": 2},
            },
            status=200,
        )

        result = self.client.list_profiles()

        assert len(result["data"]) == 2
        assert result["data"][0]["name"] == "John Doe Real Estate"
        assert result["data"][1]["type"] == "BROKERAGE"

    @responses.activate
    def test_get_profile_success(self) -> None:
        """Test successful profile retrieval."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123",
            json={
                "data": {
                    "id": 123,
                    "name": "John Doe Real Estate",
                    "type": "AGENT",
                    "email": "john@realestate.com",
                    "phone": "+1 (555) 123-4567",
                    "address": "123 Main St",
                    "city": "San Francisco",
                    "state": "CA",
                    "zipCode": "94105",
                }
            },
            status=200,
        )

        result = self.client.get_profile(profile_id=123)

        assert result["data"]["name"] == "John Doe Real Estate"
        assert result["data"]["type"] == "AGENT"
        assert result["data"]["city"] == "San Francisco"

    @responses.activate
    def test_get_profile_not_found(self) -> None:
        """Test profile retrieval with not found error."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/999",
            json={"message": "Profile not found"},
            status=404,
        )

        with pytest.raises(NotFoundError) as exc_info:
            self.client.get_profile(profile_id=999)

        assert "Resource not found" in str(exc_info.value)
        assert exc_info.value.status_code == 404

    @responses.activate
    def test_create_profile_success(self) -> None:
        """Test successful profile creation."""
        responses.add(
            responses.POST,
            "https://api-gateway.dotloop.com/public/v2/profile",
            json={
                "data": {
                    "id": 999,
                    "name": "New Real Estate Profile",
                    "type": "AGENT",
                    "email": "new@realestate.com",
                    "phone": "+1 (555) 111-2222",
                }
            },
            status=201,
        )

        result = self.client.create_profile(
            name="New Real Estate Profile",
            company="Real Estate Co",
            phone="+1 (555) 111-2222",
        )

        assert result["data"]["name"] == "New Real Estate Profile"
        assert result["data"]["type"] == "AGENT"
        assert result["data"]["email"] == "new@realestate.com"

    @responses.activate
    def test_create_profile_with_string_type(self) -> None:
        """Test profile creation with string profile type."""
        responses.add(
            responses.POST,
            "https://api-gateway.dotloop.com/public/v2/profile",
            json={
                "data": {
                    "id": 999,
                    "name": "Brokerage Profile",
                    "type": "BROKERAGE",
                    "email": "info@brokerage.com",
                }
            },
            status=201,
        )

        result = self.client.create_profile(
            name="Brokerage Profile", company="Brokerage Company"
        )

        assert result["data"]["type"] == "BROKERAGE"

    @responses.activate
    def test_create_profile_with_optional_fields(self) -> None:
        """Test profile creation with optional fields."""
        responses.add(
            responses.POST,
            "https://api-gateway.dotloop.com/public/v2/profile",
            json={
                "data": {
                    "id": 999,
                    "name": "Complete Profile",
                    "type": "AGENT",
                    "email": "complete@realestate.com",
                    "phone": "+1 (555) 111-2222",
                    "address": "456 Oak St",
                    "city": "Los Angeles",
                    "state": "CA",
                    "zipCode": "90210",
                }
            },
            status=201,
        )

        result = self.client.create_profile(
            name="Complete Profile",
            company="Complete Real Estate",
            phone="+1 (555) 111-2222",
            address="456 Oak St",
            city="Los Angeles",
            state="CA",
            zip_code="90210",
        )

        assert result["data"]["address"] == "456 Oak St"
        assert result["data"]["city"] == "Los Angeles"

    @responses.activate
    def test_update_profile_success(self) -> None:
        """Test successful profile update."""
        responses.add(
            responses.PATCH,
            "https://api-gateway.dotloop.com/public/v2/profile/123",
            json={
                "data": {
                    "id": 123,
                    "name": "Updated Real Estate Profile",
                    "type": "AGENT",
                    "email": "updated@realestate.com",
                    "phone": "+1 (555) 999-8888",
                }
            },
            status=200,
        )

        result = self.client.update_profile(
            profile_id=123,
            name="Updated Real Estate Profile",
            company="Updated Real Estate Co",
            phone="+1 (555) 999-8888",
        )

        assert result["data"]["name"] == "Updated Real Estate Profile"
        assert result["data"]["email"] == "updated@realestate.com"

    @responses.activate
    def test_update_profile_partial(self) -> None:
        """Test partial profile update."""
        responses.add(
            responses.PATCH,
            "https://api-gateway.dotloop.com/public/v2/profile/123",
            json={
                "data": {
                    "id": 123,
                    "name": "John Doe Real Estate",
                    "type": "AGENT",
                    "email": "john@realestate.com",
                    "phone": "+1 (555) 999-0000",
                }
            },
            status=200,
        )

        result = self.client.update_profile(profile_id=123, phone="+1 (555) 999-0000")

        assert result["data"]["phone"] == "+1 (555) 999-0000"

    @responses.activate
    def test_update_profile_with_enum_type(self) -> None:
        """Test profile update with enum profile type."""
        responses.add(
            responses.PATCH,
            "https://api-gateway.dotloop.com/public/v2/profile/123",
            json={"data": {"id": 123, "name": "Updated Profile", "type": "BROKERAGE"}},
            status=200,
        )

        result = self.client.update_profile(profile_id=123, company="Updated Brokerage")

        assert result["data"]["type"] == "BROKERAGE"
