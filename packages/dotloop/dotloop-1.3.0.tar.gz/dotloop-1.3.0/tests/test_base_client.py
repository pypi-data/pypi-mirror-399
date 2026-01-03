"""Tests for the BaseClient."""

from unittest.mock import MagicMock, patch

import pytest
import responses

from dotloop.base_client import BaseClient
from dotloop.exceptions import (
    AuthenticationError,
    AuthorizationError,
    DotloopError,
    NotFoundError,
    RateLimitError,
    RedirectError,
    ServerError,
    ValidationError,
)


class TestBaseClientInit:
    """Test BaseClient initialization."""

    def test_init_with_api_key(self) -> None:
        """Test initialization with provided API key."""
        client = BaseClient(api_key="test_key")
        assert client._api_key == "test_key"

    def test_init_without_api_key_raises_error(self) -> None:
        """Test initialization without API key raises error."""
        with pytest.raises(AuthenticationError):
            BaseClient()

    def test_init_with_custom_base_url(self) -> None:
        """Test initialization with custom base URL."""
        client = BaseClient(api_key="test_key", base_url="https://custom.api.com")
        assert client._base_url == "https://custom.api.com"

    def test_init_with_custom_timeout(self) -> None:
        """Test initialization with custom timeout."""
        client = BaseClient(api_key="test_key", timeout=60)
        assert client._timeout == 60


class TestBaseClientErrorHandling:
    """Test BaseClient error handling."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = BaseClient(api_key="test_key")

    @responses.activate
    def test_handle_response_401_unauthorized(self) -> None:
        """Test handling 401 Unauthorized error."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/test",
            json={"message": "Unauthorized"},
            status=401,
        )

        with pytest.raises(AuthenticationError) as exc_info:
            self.client.get("/test")

        assert "Authentication failed" in str(exc_info.value)
        assert exc_info.value.status_code == 401

    @responses.activate
    def test_handle_response_403_forbidden(self) -> None:
        """Test handling 403 Forbidden error."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/test",
            json={"message": "Forbidden"},
            status=403,
        )

        with pytest.raises(AuthorizationError) as exc_info:
            self.client.get("/test")

        assert "Authorization failed" in str(exc_info.value)
        assert exc_info.value.status_code == 403

    @responses.activate
    def test_handle_response_404_not_found(self) -> None:
        """Test handling 404 Not Found error."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/test",
            json={"message": "Not found"},
            status=404,
        )

        with pytest.raises(NotFoundError) as exc_info:
            self.client.get("/test")

        assert "Resource not found" in str(exc_info.value)
        assert exc_info.value.status_code == 404

    @responses.activate
    def test_handle_response_400_validation_error(self) -> None:
        """Test handling 400 Validation error."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/test",
            json={"message": "Invalid input"},
            status=400,
        )

        with pytest.raises(ValidationError) as exc_info:
            self.client.get("/test")

        assert "Bad request" in str(exc_info.value)
        assert exc_info.value.status_code == 400

    @responses.activate
    def test_handle_response_422_validation_error(self) -> None:
        """Test handling 422 Validation error."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/test",
            json={"message": "Unprocessable entity"},
            status=422,
        )

        with pytest.raises(DotloopError) as exc_info:
            self.client.get("/test")

        assert "Unexpected error" in str(exc_info.value)
        assert exc_info.value.status_code == 422

    @responses.activate
    def test_handle_response_429_rate_limit(self) -> None:
        """Test handling 429 Rate Limit error."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/test",
            json={"message": "Rate limit exceeded"},
            status=429,
        )

        with pytest.raises(RateLimitError) as exc_info:
            self.client.get("/test")

        assert "Rate limit exceeded" in str(exc_info.value)
        assert exc_info.value.status_code == 429

    @responses.activate
    def test_handle_response_500_server_error(self) -> None:
        """Test handling 500 Server error."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/test",
            json={"message": "Internal server error"},
            status=500,
        )

        with pytest.raises(ServerError) as exc_info:
            self.client.get("/test")

        assert "Server error" in str(exc_info.value)
        assert exc_info.value.status_code == 500

    @responses.activate
    def test_handle_response_301_redirect(self) -> None:
        """Test handling 301 Redirect."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/test",
            json={"message": "Moved permanently"},
            status=301,
        )

        with pytest.raises(RedirectError) as exc_info:
            self.client.get("/test")

        assert "Resource has been moved" in str(exc_info.value)
        assert exc_info.value.status_code == 301

    @responses.activate
    def test_handle_response_unknown_error(self) -> None:
        """Test handling unknown error status."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/test",
            json={"message": "Unknown error"},
            status=418,  # I'm a teapot
        )

        with pytest.raises(DotloopError) as exc_info:
            self.client.get("/test")

        assert "Unexpected error" in str(exc_info.value)
        assert exc_info.value.status_code == 418

    @responses.activate
    def test_handle_response_non_json_error(self) -> None:
        """Test handling non-JSON error response."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/test",
            body="Plain text error",
            status=500,
        )

        with pytest.raises(ServerError) as exc_info:
            self.client.get("/test")

        assert "Server error" in str(exc_info.value)
        assert exc_info.value.status_code == 500

    @responses.activate
    def test_handle_response_204_no_content(self) -> None:
        """Test handling 204 No Content as a successful response."""
        responses.add(
            responses.DELETE,
            "https://api-gateway.dotloop.com/public/v2/test",
            status=204,
        )

        result = self.client.delete("/test")

        assert result == {}

    @responses.activate
    def test_post_with_data(self) -> None:
        """Test POST request with data."""
        responses.add(
            responses.POST,
            "https://api-gateway.dotloop.com/public/v2/test",
            json={"data": {"id": 123}},
            status=201,
        )

        result = self.client.post("/test", data={"name": "test"})
        assert result["data"]["id"] == 123

    @responses.activate
    def test_patch_with_data(self) -> None:
        """Test PATCH request with data."""
        responses.add(
            responses.PATCH,
            "https://api-gateway.dotloop.com/public/v2/test/123",
            json={"data": {"id": 123, "updated": True}},
            status=200,
        )

        result = self.client.patch("/test/123", data={"name": "updated"})
        assert result["data"]["updated"] is True

    @responses.activate
    def test_delete_request(self) -> None:
        """Test DELETE request."""
        responses.add(
            responses.DELETE,
            "https://api-gateway.dotloop.com/public/v2/test/123",
            json={"message": "Deleted"},
            status=200,
        )

        result = self.client.delete("/test/123")
        assert result["message"] == "Deleted"

    @responses.activate
    def test_get_with_params(self) -> None:
        """Test GET request with query parameters."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/test",
            json={"data": []},
            status=200,
        )

        result = self.client.get("/test", params={"page": 1, "size": 10})
        assert "data" in result

    def test_build_url_with_leading_slash(self) -> None:
        """Test URL building with leading slash."""
        url = self.client._build_url("/test/path")
        assert url == "https://api-gateway.dotloop.com/public/v2/test/path"

    def test_build_url_without_leading_slash(self) -> None:
        """Test URL building without leading slash."""
        url = self.client._build_url("test/path")
        assert url == "https://api-gateway.dotloop.com/public/v2/test/path"
