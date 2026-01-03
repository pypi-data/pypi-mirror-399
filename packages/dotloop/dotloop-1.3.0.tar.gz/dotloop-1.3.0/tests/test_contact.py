"""Tests for the ContactClient."""

import pytest
import responses

from dotloop.contact import ContactClient
from dotloop.exceptions import AuthenticationError, DotloopError, NotFoundError


class TestContactClientInit:
    """Test ContactClient initialization."""

    def test_init_with_api_key(self) -> None:
        """Test initialization with provided API key."""
        client = ContactClient(api_key="test_key")
        assert client._api_key == "test_key"

    def test_init_without_api_key_raises_error(self) -> None:
        """Test initialization without API key raises error."""
        with pytest.raises(AuthenticationError):
            ContactClient()


class TestContactClientMethods:
    """Test ContactClient methods."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = ContactClient(api_key="test_key")

    @responses.activate
    def test_list_contacts_success(self) -> None:
        """Test successful contacts listing."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/contact",
            json={
                "data": [
                    {
                        "id": 1,
                        "firstName": "John",
                        "lastName": "Doe",
                        "email": "john.doe@example.com",
                        "phone": "+1 (555) 123-4567",
                    },
                    {
                        "id": 2,
                        "firstName": "Jane",
                        "lastName": "Smith",
                        "email": "jane.smith@example.com",
                        "phone": "+1 (555) 987-6543",
                    },
                ],
                "meta": {"total": 2},
            },
            status=200,
        )

        result = self.client.list_contacts()

        assert len(result["data"]) == 2
        assert result["data"][0]["firstName"] == "John"
        assert result["data"][1]["firstName"] == "Jane"

    @responses.activate
    def test_list_contacts_with_params(self) -> None:
        """Test contacts listing with query parameters."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/contact",
            json={
                "data": [
                    {
                        "id": 1,
                        "firstName": "John",
                        "lastName": "Doe",
                        "email": "john.doe@example.com",
                    }
                ],
                "meta": {"total": 1},
            },
            status=200,
        )

        result = self.client.list_contacts()

        assert len(result["data"]) == 1

    @responses.activate
    def test_get_contact_success(self) -> None:
        """Test successful contact retrieval."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/contact/123",
            json={
                "data": {
                    "id": 123,
                    "firstName": "John",
                    "lastName": "Doe",
                    "email": "john.doe@example.com",
                    "phone": "+1 (555) 123-4567",
                    "company": "Real Estate Co",
                }
            },
            status=200,
        )

        result = self.client.get_contact(contact_id=123)

        assert result["data"]["firstName"] == "John"
        assert result["data"]["lastName"] == "Doe"
        assert result["data"]["company"] == "Real Estate Co"

    @responses.activate
    def test_get_contact_not_found(self) -> None:
        """Test contact retrieval with not found error."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/contact/999",
            json={"message": "Contact not found"},
            status=404,
        )

        with pytest.raises(NotFoundError) as exc_info:
            self.client.get_contact(contact_id=999)

        assert "Resource not found" in str(exc_info.value)
        assert exc_info.value.status_code == 404

    @responses.activate
    def test_create_contact_success(self) -> None:
        """Test successful contact creation."""
        responses.add(
            responses.POST,
            "https://api-gateway.dotloop.com/public/v2/contact",
            json={
                "data": {
                    "id": 999,
                    "firstName": "New",
                    "lastName": "Contact",
                    "email": "new.contact@example.com",
                    "phone": "+1 (555) 111-2222",
                }
            },
            status=201,
        )

        result = self.client.create_contact(
            first_name="New",
            last_name="Contact",
            email="new.contact@example.com",
            phone="+1 (555) 111-2222",
        )

        assert result["data"]["firstName"] == "New"
        assert result["data"]["lastName"] == "Contact"
        assert result["data"]["email"] == "new.contact@example.com"

    @responses.activate
    def test_create_contact_with_optional_fields(self) -> None:
        """Test contact creation with optional fields."""
        responses.add(
            responses.POST,
            "https://api-gateway.dotloop.com/public/v2/contact",
            json={
                "data": {
                    "id": 999,
                    "firstName": "Complete",
                    "lastName": "Contact",
                    "email": "complete@example.com",
                    "phone": "+1 (555) 111-2222",
                    "company": "Test Company",
                    "address": "123 Main St",
                    "city": "Test City",
                    "state": "CA",
                    "zipCode": "12345",
                    "country": "USA",
                }
            },
            status=201,
        )

        result = self.client.create_contact(
            first_name="Complete",
            last_name="Contact",
            email="complete@example.com",
            phone="+1 (555) 111-2222",
            company="Test Company",
            address="123 Main St",
            city="Test City",
            state="CA",
            zip_code="12345",
            country="USA",
        )

        assert result["data"]["company"] == "Test Company"
        assert result["data"]["address"] == "123 Main St"

    @responses.activate
    def test_update_contact_success(self) -> None:
        """Test successful contact update."""
        responses.add(
            responses.PATCH,
            "https://api-gateway.dotloop.com/public/v2/contact/123",
            json={
                "data": {
                    "id": 123,
                    "firstName": "Updated",
                    "lastName": "Contact",
                    "email": "updated@example.com",
                    "phone": "+1 (555) 999-8888",
                }
            },
            status=200,
        )

        result = self.client.update_contact(
            contact_id=123,
            first_name="Updated",
            email="updated@example.com",
            phone="+1 (555) 999-8888",
        )

        assert result["data"]["firstName"] == "Updated"
        assert result["data"]["email"] == "updated@example.com"

    @responses.activate
    def test_update_contact_partial(self) -> None:
        """Test partial contact update."""
        responses.add(
            responses.PATCH,
            "https://api-gateway.dotloop.com/public/v2/contact/123",
            json={
                "data": {
                    "id": 123,
                    "firstName": "John",
                    "lastName": "Doe",
                    "email": "john.doe@example.com",
                    "phone": "+1 (555) 999-0000",
                }
            },
            status=200,
        )

        result = self.client.update_contact(contact_id=123, phone="+1 (555) 999-0000")

        assert result["data"]["phone"] == "+1 (555) 999-0000"

    @responses.activate
    def test_delete_contact_success(self) -> None:
        """Test successful contact deletion."""
        responses.add(
            responses.DELETE,
            "https://api-gateway.dotloop.com/public/v2/contact/123",
            status=204,
        )

        result = self.client.delete_contact(contact_id=123)

        assert result == {}

    @responses.activate
    def test_delete_contact_not_found(self) -> None:
        """Test contact deletion with not found error."""
        responses.add(
            responses.DELETE,
            "https://api-gateway.dotloop.com/public/v2/contact/999",
            json={"message": "Contact not found"},
            status=404,
        )

        with pytest.raises(NotFoundError):
            self.client.delete_contact(contact_id=999)
