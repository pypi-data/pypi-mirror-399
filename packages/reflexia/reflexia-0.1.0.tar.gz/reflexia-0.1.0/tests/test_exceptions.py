"""Tests for exception classes."""

import pytest

from reflexia.exceptions import (
    ReflexiaError,
    ReflexiaAPIError,
    ReflexiaAuthenticationError,
    ReflexiaRateLimitError,
    ReflexiaNotFoundError,
    ReflexiaNetworkError,
)


class TestExceptions:
    """Test exception classes."""

    def test_reflexia_error(self):
        """Test base ReflexiaError."""
        error = ReflexiaError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_reflexia_api_error(self):
        """Test ReflexiaAPIError."""
        error = ReflexiaAPIError(
            "API error",
            "ERROR_CODE",
            400,
            details={"field": "value"},
            request_id="req-123",
        )
        assert error.message == "API error"
        assert error.code == "ERROR_CODE"
        assert error.status_code == 400
        assert error.details == {"field": "value"}
        assert error.request_id == "req-123"
        assert "ERROR_CODE: API error" in str(error)
        assert "req-123" in str(error)

    def test_reflexia_authentication_error(self):
        """Test ReflexiaAuthenticationError."""
        error = ReflexiaAuthenticationError("Auth failed", details={"reason": "invalid_key"})
        assert error.message == "Auth failed"
        assert error.code == "UNAUTHORIZED"
        assert error.status_code == 401
        assert error.details == {"reason": "invalid_key"}

    def test_reflexia_rate_limit_error(self):
        """Test ReflexiaRateLimitError."""
        error = ReflexiaRateLimitError("Rate limited", retry_after=60)
        assert error.message == "Rate limited"
        assert error.code == "RATE_LIMIT_EXCEEDED"
        assert error.status_code == 429
        assert error.retry_after == 60

    def test_reflexia_not_found_error(self):
        """Test ReflexiaNotFoundError."""
        error = ReflexiaNotFoundError("Not found", details={"resource": "agent"})
        assert error.message == "Not found"
        assert error.code == "NOT_FOUND"
        assert error.status_code == 404
        assert error.details == {"resource": "agent"}

    def test_reflexia_network_error(self):
        """Test ReflexiaNetworkError."""
        error = ReflexiaNetworkError("Network error")
        assert str(error) == "Network error"
        assert isinstance(error, ReflexiaError)

