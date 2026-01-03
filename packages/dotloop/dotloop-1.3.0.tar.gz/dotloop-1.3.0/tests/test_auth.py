"""Tests for the AuthClient."""

from unittest.mock import MagicMock, patch

import pytest
import responses

from dotloop.auth import AuthClient
from dotloop.exceptions import AuthenticationError, DotloopError


class TestAuthClientInit:
    """Test AuthClient initialization."""

    def test_init_with_credentials(self) -> None:
        """Test initialization with OAuth credentials."""
        client = AuthClient(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="https://test.com/callback",
            api_key="dummy_key",
        )
        assert client._client_id == "test_client_id"
        assert client._client_secret == "test_client_secret"
        assert client._redirect_uri == "https://test.com/callback"
        assert "auth.dotloop.com" in client._oauth_base_url

    def test_init_with_custom_base_url(self) -> None:
        """Test initialization with custom base URL."""
        client = AuthClient(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="https://test.com/callback",
            base_url="https://custom-api-gateway.dotloop.com",
            api_key="dummy_key",
        )
        assert "auth.dotloop.com" in client._oauth_base_url


class TestAuthClientMethods:
    """Test AuthClient methods."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = AuthClient(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="https://test.com/callback",
            api_key="dummy_key",  # OAuth client doesn't need real API key for most operations
        )

    def test_get_authorization_url_basic(self) -> None:
        """Test basic authorization URL generation."""
        url = self.client.get_authorization_url()

        assert "auth.dotloop.com/oauth/authorize" in url
        assert "response_type=code" in url
        assert "client_id=test_client_id" in url
        assert "redirect_uri=https%3A%2F%2Ftest.com%2Fcallback" in url

    def test_get_authorization_url_with_scope_and_state(self) -> None:
        """Test authorization URL with scope and state."""
        url = self.client.get_authorization_url(
            scope=["account", "profile", "loop"], state="csrf_token_123"
        )

        assert "scope=account+profile+loop" in url
        assert "state=csrf_token_123" in url

    @responses.activate
    def test_exchange_code_for_token_success(self) -> None:
        """Test successful token exchange."""
        responses.add(
            responses.POST,
            "https://auth.dotloop.com/oauth/token",
            json={
                "access_token": "access_token_123",
                "refresh_token": "refresh_token_123",
                "expires_in": 3600,
                "token_type": "Bearer",
            },
            status=200,
        )

        result = self.client.exchange_code_for_token("auth_code_123")

        assert result["access_token"] == "access_token_123"
        assert result["refresh_token"] == "refresh_token_123"
        assert result["expires_in"] == 3600

    @responses.activate
    def test_exchange_code_for_token_error(self) -> None:
        """Test token exchange with error."""
        responses.add(
            responses.POST,
            "https://auth.dotloop.com/oauth/token",
            json={"error": "invalid_grant"},
            status=400,
        )

        with pytest.raises(DotloopError):
            self.client.exchange_code_for_token("invalid_code")

    @responses.activate
    def test_refresh_access_token_success(self) -> None:
        """Test successful token refresh."""
        responses.add(
            responses.POST,
            "https://auth.dotloop.com/oauth/token",
            json={
                "access_token": "new_access_token_123",
                "refresh_token": "new_refresh_token_123",
                "expires_in": 3600,
                "token_type": "Bearer",
            },
            status=200,
        )

        result = self.client.refresh_access_token("refresh_token_123")

        assert result["access_token"] == "new_access_token_123"
        assert result["refresh_token"] == "new_refresh_token_123"

    @responses.activate
    def test_revoke_token_success(self) -> None:
        """Test successful token revocation."""
        responses.add(
            responses.POST,
            "https://auth.dotloop.com/oauth/token/revoke",
            json={"message": "Token revoked successfully"},
            status=200,
        )

        result = self.client.revoke_token("token_to_revoke")

        assert "message" in result

    def test_revoke_token_with_refresh_token_hint(self) -> None:
        """Test token revocation with refresh token hint."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                "https://auth.dotloop.com/oauth/token/revoke",
                json={"message": "Refresh token revoked"},
                status=200,
            )

            result = self.client.revoke_token(
                "refresh_token_123", token_type_hint="refresh_token"
            )

            assert "message" in result

    @patch("dotloop.account.AccountClient.get_account")
    def test_validate_token_success(self, mock_get_account: MagicMock) -> None:
        """Test successful token validation."""
        mock_get_account.return_value = {"data": {"id": 123, "name": "Test Account"}}

        result = self.client.validate_token("valid_token_123")

        assert result["valid"] is True
        assert result["token"] == "valid_token_123"
        assert "account_info" in result

    @patch("dotloop.account.AccountClient.get_account")
    def test_validate_token_failure(self, mock_get_account: MagicMock) -> None:
        """Test token validation failure."""
        mock_get_account.side_effect = Exception("Invalid token")

        result = self.client.validate_token("invalid_token_123")

        assert result["valid"] is False
        assert result["token"] == "invalid_token_123"
        assert "error" in result

    def test_get_oauth_flow_helper_basic(self) -> None:
        """Test OAuth flow helper with basic parameters."""
        flow = self.client.get_oauth_flow_helper()

        assert "authorization_url" in flow
        assert "redirect_uri" in flow
        assert "client_id" in flow
        assert "instructions" in flow
        assert len(flow["instructions"]) == 8
        assert flow["redirect_uri"] == "https://test.com/callback"
        assert flow["client_id"] == "test_client_id"

    def test_get_oauth_flow_helper_with_params(self) -> None:
        """Test OAuth flow helper with scope and state."""
        flow = self.client.get_oauth_flow_helper(
            scope=["account", "profile"], state="test_state"
        )

        assert flow["scope"] == ["account", "profile"]
        assert flow["state"] == "test_state"
        assert "scope=account+profile" in flow["authorization_url"]
        assert "state=test_state" in flow["authorization_url"]
