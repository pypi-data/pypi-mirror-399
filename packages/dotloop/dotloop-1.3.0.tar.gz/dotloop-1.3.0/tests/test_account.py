"""Tests for the AccountClient."""

import pytest
import responses

from dotloop.account import AccountClient
from dotloop.exceptions import AuthenticationError, DotloopError


class TestAccountClientInit:
    """Test AccountClient initialization."""

    def test_init_with_api_key(self) -> None:
        """Test initialization with provided API key."""
        client = AccountClient(api_key="test_key")
        assert client._api_key == "test_key"

    def test_init_without_api_key_raises_error(self) -> None:
        """Test initialization without API key raises error."""
        with pytest.raises(AuthenticationError):
            AccountClient()


class TestAccountClientMethods:
    """Test AccountClient methods."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = AccountClient(api_key="test_key")

    @responses.activate
    def test_get_account_success(self) -> None:
        """Test successful account retrieval."""
        # Mock API response
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/account",
            json={
                "data": {
                    "id": 1,
                    "firstName": "John",
                    "lastName": "Doe",
                    "email": "john@example.com",
                    "defaultProfileId": 42,
                }
            },
            status=200,
        )

        result = self.client.get_account()

        assert result["data"]["id"] == 1
        assert result["data"]["firstName"] == "John"
        assert result["data"]["lastName"] == "Doe"
        assert result["data"]["email"] == "john@example.com"

    @responses.activate
    def test_get_account_authentication_error(self) -> None:
        """Test account retrieval with authentication error."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/account",
            json={"message": "Invalid token"},
            status=401,
        )

        with pytest.raises(AuthenticationError) as exc_info:
            self.client.get_account()

        assert "Authentication failed" in str(exc_info.value)
        assert exc_info.value.status_code == 401

    @responses.activate
    def test_get_account_server_error(self) -> None:
        """Test account retrieval with server error."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/account",
            json={"message": "Internal server error"},
            status=500,
        )

        with pytest.raises(DotloopError) as exc_info:
            self.client.get_account()

        assert exc_info.value.status_code == 500
