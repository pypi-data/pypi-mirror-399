"""Tests for Field Engine API client."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from reflexia import ReflexiaClient
from reflexia.exceptions import ReflexiaAPIError


class TestFieldClient:
    """Test FieldClient methods."""

    @patch("reflexia.client.requests.Session")
    def test_register_agent_success(
        self, mock_session_class, client, mock_register_agent_response
    ):
        """Test successful agent registration."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}

        response = Mock()
        response.ok = True
        response.status_code = 200
        response.json.return_value = mock_register_agent_response
        response.headers = {}

        mock_session.request.return_value = response
        client._session = mock_session

        result = client.field.register_agent(
            agent_id="test-agent-1", agent_type="researcher"
        )

        assert result["agent_id"] == "test-agent-1"
        assert "position" in result
        assert "session_token" in result
        mock_session.request.assert_called_once()

    @patch("reflexia.client.requests.Session")
    def test_register_agent_with_embedding(
        self, mock_session_class, client, mock_register_agent_response
    ):
        """Test agent registration with semantic embedding."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}

        response = Mock()
        response.ok = True
        response.status_code = 200
        response.json.return_value = mock_register_agent_response
        response.headers = {}

        mock_session.request.return_value = response
        client._session = mock_session

        result = client.field.register_agent(
            agent_id="test-agent-1",
            agent_type="researcher",
            semantic_embedding=[0.1, 0.2, 0.3],
        )

        # Verify embedding was included in request
        call_args = mock_session.request.call_args
        assert call_args[1]["json"]["semantic_embedding"] == [0.1, 0.2, 0.3]

    @patch("reflexia.client.requests.Session")
    def test_sense_success(self, mock_session_class, client, mock_sense_response):
        """Test successful field sensing."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}

        response = Mock()
        response.ok = True
        response.status_code = 200
        response.json.return_value = mock_sense_response
        response.headers = {}

        mock_session.request.return_value = response
        client._session = mock_session

        result = client.field.sense(
            agent_id="test-agent-1", session_token="test-token"
        )

        assert result["local_value"] == 0.65
        assert result["should_activate"] is True
        assert "gradient_magnitude" in result
        assert "nearby_agents" in result

    @patch("reflexia.client.requests.Session")
    def test_modify_success(self, mock_session_class, client, mock_modify_response):
        """Test successful field modification."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}

        response = Mock()
        response.ok = True
        response.status_code = 200
        response.json.return_value = mock_modify_response
        response.headers = {}

        mock_session.request.return_value = response
        client._session = mock_session

        result = client.field.modify(
            agent_id="test-agent-1",
            session_token="test-token",
            delta=0.5,
            outcome="success",
        )

        assert result["accepted"] is True
        assert result["new_local_value"] == 0.75

    def test_modify_invalid_outcome(self, client):
        """Test modify with invalid outcome value."""
        with pytest.raises(ValueError, match="outcome must be"):
            client.field.modify(
                agent_id="test-agent-1",
                session_token="test-token",
                delta=0.5,
                outcome="invalid",
            )

    @patch("reflexia.client.requests.Session")
    def test_batch_modify_success(self, mock_session_class, client):
        """Test successful batch modification."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}

        response = Mock()
        response.ok = True
        response.status_code = 200
        response.json.return_value = {"accepted": True, "modifications": []}
        response.headers = {}

        mock_session.request.return_value = response
        client._session = mock_session

        result = client.field.batch_modify(
            agent_id="test-agent-1",
            session_token="test-token",
            modifications=[
                {"delta": 0.5, "outcome": "success"},
                {"delta": -0.2, "outcome": "uncertain"},
            ],
        )

        assert result["accepted"] is True

    @patch("reflexia.client.requests.Session")
    def test_get_agents_success(self, mock_session_class, client):
        """Test successful get agents."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}

        response = Mock()
        response.ok = True
        response.status_code = 200
        response.json.return_value = {
            "agents": [
                {
                    "agent_id": "agent-1",
                    "agent_type": "researcher",
                    "position": {"x": 10.0, "y": 20.0},
                }
            ]
        }
        response.headers = {}

        mock_session.request.return_value = response
        client._session = mock_session

        result = client.field.get_agents()
        assert "agents" in result
        assert len(result["agents"]) == 1

    @patch("reflexia.client.requests.Session")
    def test_get_metrics_success(self, mock_session_class, client):
        """Test successful get metrics."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}

        response = Mock()
        response.ok = True
        response.status_code = 200
        response.json.return_value = {
            "coherence": 0.85,
            "energy": 0.72,
            "agent_count": 5,
        }
        response.headers = {}

        mock_session.request.return_value = response
        client._session = mock_session

        result = client.field.get_metrics()
        assert result["coherence"] == 0.85
        assert result["agent_count"] == 5

