"""Tests for Payment API client."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from reflexia import ReflexiaClient


class TestPaymentClient:
    """Test PaymentClient methods."""

    @patch("reflexia.client.requests.Session")
    def test_verify_success(self, mock_session_class, client):
        """Test successful payment verification."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}

        response = Mock()
        response.ok = True
        response.status_code = 200
        response.json.return_value = {
            "verified": True,
            "payment_id": "pay-123",
            "amount": 100,
        }
        response.headers = {}

        mock_session.request.return_value = response
        client._session = mock_session

        result = client.payment.verify(
            payment_header="x402 <base64-payment>", operation="sense_field"
        )

        assert result["verified"] is True

    @patch("reflexia.client.requests.Session")
    def test_get_pricing_success(self, mock_session_class, client):
        """Test successful get pricing."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}

        response = Mock()
        response.ok = True
        response.status_code = 200
        response.json.return_value = {
            "sense_field": {"price": 10, "unit": "sats"},
            "modify_field": {"price": 5, "unit": "sats"},
        }
        response.headers = {}

        mock_session.request.return_value = response
        client._session = mock_session

        result = client.payment.get_pricing()
        assert "sense_field" in result
        assert result["sense_field"]["price"] == 10

    @patch("reflexia.client.requests.Session")
    def test_get_pricing_with_operation(self, mock_session_class, client):
        """Test get pricing for specific operation."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}

        response = Mock()
        response.ok = True
        response.status_code = 200
        response.json.return_value = {"sense_field": {"price": 10, "unit": "sats"}}
        response.headers = {}

        mock_session.request.return_value = response
        client._session = mock_session

        result = client.payment.get_pricing(operation="sense_field")
        assert "sense_field" in result

    @patch("reflexia.client.requests.Session")
    def test_get_usage_success(self, mock_session_class, client):
        """Test successful get usage."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}

        response = Mock()
        response.ok = True
        response.status_code = 200
        response.json.return_value = {
            "total_operations": 1000,
            "total_cost": 5000,
            "operations_by_type": {
                "sense_field": 500,
                "modify_field": 300,
            },
        }
        response.headers = {}

        mock_session.request.return_value = response
        client._session = mock_session

        result = client.payment.get_usage()
        assert result["total_operations"] == 1000
        assert result["total_cost"] == 5000

    @patch("reflexia.client.requests.Session")
    def test_settle_success(self, mock_session_class, client):
        """Test successful payment settlement."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}

        response = Mock()
        response.ok = True
        response.status_code = 200
        response.json.return_value = {
            "settled": True,
            "settlement_id": "settle-123",
        }
        response.headers = {}

        mock_session.request.return_value = response
        client._session = mock_session

        result = client.payment.settle(
            payment_header="x402 <base64-payment>",
            operation="sense_field",
            compute_units=1,
            duration_ms=150,
        )

        assert result["settled"] is True

