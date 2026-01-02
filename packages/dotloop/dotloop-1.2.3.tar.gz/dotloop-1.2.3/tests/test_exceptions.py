"""Tests for the exceptions module."""

import pytest

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


class TestDotloopError:
    """Test DotloopError base exception."""

    def test_dotloop_error_basic(self) -> None:
        """Test basic DotloopError creation."""
        error = DotloopError("Test error")
        assert str(error) == "Test error"
        assert error.status_code is None
        assert error.response_data is None

    def test_dotloop_error_with_status_code(self) -> None:
        """Test DotloopError with status code."""
        error = DotloopError("Test error", status_code=400)
        assert str(error) == "Test error"
        assert error.status_code == 400

    def test_dotloop_error_with_response(self) -> None:
        """Test DotloopError with response."""
        response_data = {"error": "test"}
        error = DotloopError("Test error", response_data=response_data)
        assert str(error) == "Test error"
        assert error.response_data == response_data


class TestSpecificExceptions:
    """Test specific exception types."""

    def test_authentication_error(self) -> None:
        """Test AuthenticationError."""
        error = AuthenticationError("Auth failed", status_code=401)
        assert str(error) == "Auth failed"
        assert error.status_code == 401
        assert isinstance(error, DotloopError)

    def test_authorization_error(self) -> None:
        """Test AuthorizationError."""
        error = AuthorizationError("Access denied", status_code=403)
        assert str(error) == "Access denied"
        assert error.status_code == 403
        assert isinstance(error, DotloopError)

    def test_validation_error(self) -> None:
        """Test ValidationError."""
        error = ValidationError("Invalid input", status_code=400)
        assert str(error) == "Invalid input"
        assert error.status_code == 400
        assert isinstance(error, DotloopError)

    def test_not_found_error(self) -> None:
        """Test NotFoundError."""
        error = NotFoundError("Resource not found", status_code=404)
        assert str(error) == "Resource not found"
        assert error.status_code == 404
        assert isinstance(error, DotloopError)

    def test_rate_limit_error(self) -> None:
        """Test RateLimitError."""
        error = RateLimitError("Rate limit exceeded", status_code=429)
        assert str(error) == "Rate limit exceeded"
        assert error.status_code == 429
        assert isinstance(error, DotloopError)

    def test_server_error(self) -> None:
        """Test ServerError."""
        error = ServerError("Internal server error", status_code=500)
        assert str(error) == "Internal server error"
        assert error.status_code == 500
        assert isinstance(error, DotloopError)

    def test_redirect_error(self) -> None:
        """Test RedirectError."""
        error = RedirectError("Resource moved", status_code=301)
        assert str(error) == "Resource moved"
        assert error.status_code == 301
        assert isinstance(error, DotloopError)

    def test_exception_inheritance(self) -> None:
        """Test that all exceptions inherit from DotloopError."""
        exceptions = [
            AuthenticationError("test"),
            AuthorizationError("test"),
            ValidationError("test"),
            NotFoundError("test"),
            RateLimitError("test"),
            ServerError("test"),
            RedirectError("test"),
        ]

        for exc in exceptions:
            assert isinstance(exc, DotloopError)
            assert isinstance(exc, Exception)

    def test_exception_with_all_params(self) -> None:
        """Test exception with all parameters."""
        response_data = {"error": "detailed error"}
        error = ValidationError(
            "Validation failed", status_code=422, response_data=response_data
        )

        assert str(error) == "Validation failed"
        assert error.status_code == 422
        assert error.response_data == response_data
