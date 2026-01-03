"""Tests for Account API client."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from reflexia import ReflexiaClient


class TestAccountClient:
    """Test AccountClient methods."""

    @patch("reflexia.client.requests.Session")
    def test_register_success(self, mock_session_class, client):
        """Test successful account registration."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}

        response = Mock()
        response.ok = True
        response.status_code = 200
        response.json.return_value = {
            "tenant_id": "tenant-123",
            "api_key": "rk_test_key",
            "email": "user@example.com",
        }
        response.headers = {}

        mock_session.request.return_value = response
        client._session = mock_session

        result = client.account.register(
            email="user@example.com", password="secure-password"
        )

        assert result["tenant_id"] == "tenant-123"
        assert "api_key" in result

    @patch("reflexia.client.requests.Session")
    def test_get_balance_success(self, mock_session_class, client):
        """Test successful get balance."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}

        response = Mock()
        response.ok = True
        response.status_code = 200
        response.json.return_value = {
            "credits": 1000,
            "sats": 50000,
            "currency": "USD",
        }
        response.headers = {}

        mock_session.request.return_value = response
        client._session = mock_session

        result = client.account.get_balance()
        assert result["credits"] == 1000
        assert result["sats"] == 50000

    @patch("reflexia.client.requests.Session")
    def test_get_wallet_success(self, mock_session_class, client):
        """Test successful get wallet."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}

        response = Mock()
        response.ok = True
        response.status_code = 200
        response.json.return_value = {
            "address": "0x1234567890abcdef",
            "balance": 1000000,
            "network": "base",
        }
        response.headers = {}

        mock_session.request.return_value = response
        client._session = mock_session

        result = client.account.get_wallet()
        assert "address" in result
        assert result["address"] == "0x1234567890abcdef"

    @patch("reflexia.client.requests.Session")
    def test_get_subscription_success(self, mock_session_class, client):
        """Test successful get subscription."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}

        response = Mock()
        response.ok = True
        response.status_code = 200
        response.json.return_value = {
            "plan": "pro",
            "status": "active",
            "expires_at": "2025-12-31T23:59:59Z",
        }
        response.headers = {}

        mock_session.request.return_value = response
        client._session = mock_session

        result = client.account.get_subscription()
        assert result["plan"] == "pro"
        assert result["status"] == "active"

    @patch("reflexia.client.requests.Session")
    def test_create_api_key_success(self, mock_session_class, client):
        """Test successful API key creation."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}

        response = Mock()
        response.ok = True
        response.status_code = 200
        response.json.return_value = {
            "api_key": "rk_new_key_123",
            "key_id": "key-123",
            "name": "production-key",
        }
        response.headers = {}

        mock_session.request.return_value = response
        client._session = mock_session

        result = client.account.create_api_key(name="production-key")
        assert result["api_key"] == "rk_new_key_123"
        assert result["key_id"] == "key-123"

    @patch("reflexia.client.requests.Session")
    def test_list_api_keys_success(self, mock_session_class, client):
        """Test successful list API keys."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}

        response = Mock()
        response.ok = True
        response.status_code = 200
        response.json.return_value = {
            "keys": [
                {"key_id": "key-1", "name": "production", "created_at": "2025-01-01"},
                {"key_id": "key-2", "name": "staging", "created_at": "2025-01-02"},
            ]
        }
        response.headers = {}

        mock_session.request.return_value = response
        client._session = mock_session

        result = client.account.list_api_keys()
        assert "keys" in result
        assert len(result["keys"]) == 2

    @patch("reflexia.client.requests.Session")
    def test_revoke_api_key_success(self, mock_session_class, client):
        """Test successful API key revocation."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}

        response = Mock()
        response.ok = True
        response.status_code = 200
        response.json.return_value = {"revoked": True, "key_id": "key-123"}
        response.headers = {}

        mock_session.request.return_value = response
        client._session = mock_session

        result = client.account.revoke_api_key(key_id="key-123")
        assert result["revoked"] is True

