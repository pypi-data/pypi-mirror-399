"""Tests for ReflexiaClient core functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests

from reflexia import ReflexiaClient
from reflexia.exceptions import (
    ReflexiaError,
    ReflexiaAPIError,
    ReflexiaAuthenticationError,
    ReflexiaRateLimitError,
    ReflexiaNotFoundError,
    ReflexiaNetworkError,
)


class TestReflexiaClient:
    """Test ReflexiaClient initialization and core methods."""

    def test_client_initialization_success(self, mock_api_key):
        """Test successful client initialization."""
        client = ReflexiaClient(api_key=mock_api_key)
        assert client.api_key == mock_api_key
        assert client.base_url == "https://api.reflexia.io"
        assert client.timeout == 30

    def test_client_initialization_custom_base_url(self, mock_api_key):
        """Test client initialization with custom base URL."""
        client = ReflexiaClient(
            api_key=mock_api_key, base_url="https://staging-api.reflexia.io"
        )
        assert client.base_url == "https://staging-api.reflexia.io"

    def test_client_initialization_custom_timeout(self, mock_api_key):
        """Test client initialization with custom timeout."""
        client = ReflexiaClient(api_key=mock_api_key, timeout=60)
        assert client.timeout == 60

    def test_client_initialization_invalid_api_key_empty(self):
        """Test client initialization fails with empty API key."""
        with pytest.raises(ValueError, match="api_key is required"):
            ReflexiaClient(api_key="")

    def test_client_initialization_invalid_api_key_format(self):
        """Test client initialization fails with invalid API key format."""
        with pytest.raises(ValueError, match="api_key must start with 'rk_'"):
            ReflexiaClient(api_key="invalid_key")

    def test_client_initialization_service_clients(self, mock_api_key):
        """Test that service clients are initialized."""
        client = ReflexiaClient(api_key=mock_api_key)
        assert client.field is not None
        assert client.epistemic is not None
        assert client.patterns is not None
        assert client.payment is not None
        assert client.account is not None

    @patch("reflexia.client.requests.Session")
    def test_get_request_success(self, mock_session_class, client, mock_success_response):
        """Test successful GET request."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.request.return_value = mock_success_response
        mock_session.headers = {}

        # Reinitialize client to use mocked session
        client._session = mock_session

        result = client.get("/api/v1/test")
        assert result == {"success": True}
        mock_session.request.assert_called_once()

    @patch("reflexia.client.requests.Session")
    def test_post_request_success(self, mock_session_class, client, mock_success_response):
        """Test successful POST request."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.request.return_value = mock_success_response
        mock_session.headers = {}

        client._session = mock_session

        result = client.post("/api/v1/test", json={"test": "data"})
        assert result == {"success": True}
        mock_session.request.assert_called_once()

    @patch("reflexia.client.requests.Session")
    def test_request_authentication_error(self, mock_session_class, client):
        """Test authentication error handling."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}

        response = Mock()
        response.ok = False
        response.status_code = 401
        response.text = "Unauthorized"
        response.reason = "Unauthorized"
        response.json.return_value = {
            "error": {
                "code": "UNAUTHORIZED",
                "message": "Authentication failed",
                "details": {},
            }
        }
        response.headers = {}

        mock_session.request.return_value = response
        client._session = mock_session

        with pytest.raises(ReflexiaAuthenticationError):
            client.get("/api/v1/test")

    @patch("reflexia.client.requests.Session")
    def test_request_not_found_error(self, mock_session_class, client):
        """Test not found error handling."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}

        response = Mock()
        response.ok = False
        response.status_code = 404
        response.text = "Not Found"
        response.reason = "Not Found"
        response.json.return_value = {
            "error": {
                "code": "NOT_FOUND",
                "message": "Resource not found",
                "details": {},
            }
        }
        response.headers = {}

        mock_session.request.return_value = response
        client._session = mock_session

        with pytest.raises(ReflexiaNotFoundError):
            client.get("/api/v1/test")

    @patch("reflexia.client.requests.Session")
    def test_request_rate_limit_error(self, mock_session_class, client):
        """Test rate limit error handling."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}

        response = Mock()
        response.ok = False
        response.status_code = 429
        response.text = "Too Many Requests"
        response.reason = "Too Many Requests"
        response.json.return_value = {
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": "Rate limit exceeded",
                "details": {},
            }
        }
        response.headers = {"Retry-After": "60"}

        mock_session.request.return_value = response
        client._session = mock_session

        with pytest.raises(ReflexiaRateLimitError) as exc_info:
            client.get("/api/v1/test")
        assert exc_info.value.retry_after == 60

    @patch("reflexia.client.requests.Session")
    def test_request_network_error(self, mock_session_class, client):
        """Test network error handling."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}
        mock_session.request.side_effect = requests.exceptions.ConnectionError("Connection failed")
        client._session = mock_session

        with pytest.raises(ReflexiaNetworkError):
            client.get("/api/v1/test")

    @patch("reflexia.client.requests.Session")
    def test_request_generic_api_error(self, mock_session_class, client):
        """Test generic API error handling."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}

        response = Mock()
        response.ok = False
        response.status_code = 500
        response.text = "Internal Server Error"
        response.reason = "Internal Server Error"
        response.json.return_value = {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Internal server error",
                "details": {},
            },
            "request_id": "req-test-123",
        }
        response.headers = {}

        mock_session.request.return_value = response
        client._session = mock_session

        with pytest.raises(ReflexiaAPIError) as exc_info:
            client.get("/api/v1/test")
        assert exc_info.value.code == "INTERNAL_ERROR"
        assert exc_info.value.request_id == "req-test-123"

