"""Tests for Epistemic Service API client."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from reflexia import ReflexiaClient


class TestEpistemicClient:
    """Test EpistemicClient methods."""

    @patch("reflexia.client.requests.Session")
    def test_check_consistency_success(
        self, mock_session_class, client, mock_consistency_response
    ):
        """Test successful consistency check."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}

        response = Mock()
        response.ok = True
        response.status_code = 200
        response.json.return_value = mock_consistency_response
        response.headers = {}

        mock_session.request.return_value = response
        client._session = mock_session

        result = client.epistemic.check_consistency(
            agent_id="test-agent-1",
            trajectories=[
                {"answer_hash": "abc123", "confidence": 0.9},
                {"answer_hash": "abc123", "confidence": 0.85},
                {"answer_hash": "def456", "confidence": 0.7},
            ],
        )

        assert result["abstained"] is False
        assert result["winning_hash"] == "abc123def456"
        assert result["majority_vote"] == 0.8

    @patch("reflexia.client.requests.Session")
    def test_check_consistency_abstained(self, mock_session_class, client):
        """Test consistency check that abstains."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}

        response = Mock()
        response.ok = True
        response.status_code = 200
        response.json.return_value = {
            "abstained": True,
            "winning_hash": None,
            "majority_vote": 0.4,
            "confidence": 0.3,
        }
        response.headers = {}

        mock_session.request.return_value = response
        client._session = mock_session

        result = client.epistemic.check_consistency(
            agent_id="test-agent-1",
            trajectories=[
                {"answer_hash": "abc123", "confidence": 0.5},
                {"answer_hash": "def456", "confidence": 0.4},
                {"answer_hash": "ghi789", "confidence": 0.3},
            ],
        )

        assert result["abstained"] is True
        assert result["winning_hash"] is None

    def test_check_consistency_empty_trajectories(self, client):
        """Test consistency check with empty trajectories."""
        with pytest.raises(ValueError, match="trajectories must be a non-empty list"):
            client.epistemic.check_consistency(
                agent_id="test-agent-1", trajectories=[]
            )

    @patch("reflexia.client.requests.Session")
    def test_check_consistency_with_config(self, mock_session_class, client, mock_consistency_response):
        """Test consistency check with configuration."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}

        response = Mock()
        response.ok = True
        response.status_code = 200
        response.json.return_value = mock_consistency_response
        response.headers = {}

        mock_session.request.return_value = response
        client._session = mock_session

        result = client.epistemic.check_consistency(
            agent_id="test-agent-1",
            trajectories=[
                {"answer_hash": "abc123", "confidence": 0.9},
            ],
            config={
                "abstention_threshold": 0.66,
                "compute_entropy": True,
            },
        )

        # Verify config was included in request
        call_args = mock_session.request.call_args
        assert "config" in call_args[1]["json"]
        assert call_args[1]["json"]["config"]["abstention_threshold"] == 0.66

    @patch("reflexia.client.requests.Session")
    def test_recommend_k_success(self, mock_session_class, client):
        """Test successful k recommendation."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}

        response = Mock()
        response.ok = True
        response.status_code = 200
        response.json.return_value = {
            "recommended_k": 5,
            "estimated_cost_multiplier": 5.0,
            "reasoning": "Complex task requires multiple trajectories",
        }
        response.headers = {}

        mock_session.request.return_value = response
        client._session = mock_session

        result = client.epistemic.recommend_k(complexity_hint="complex")

        assert result["recommended_k"] == 5
        assert result["estimated_cost_multiplier"] == 5.0
        assert "reasoning" in result

    def test_recommend_k_invalid_complexity(self, client):
        """Test recommend_k with invalid complexity hint."""
        with pytest.raises(ValueError, match="complexity_hint must be"):
            client.epistemic.recommend_k(complexity_hint="invalid")

    @patch("reflexia.client.requests.Session")
    def test_stream_consistency_success(self, mock_session_class, client):
        """Test successful stream consistency."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}

        response = Mock()
        response.ok = True
        response.status_code = 200
        response.json.return_value = {
            "abstained": False,
            "winning_hash": "abc123",
            "partial": True,
        }
        response.headers = {}

        mock_session.request.return_value = response
        client._session = mock_session

        result = client.epistemic.stream_consistency(
            agent_id="test-agent-1",
            session_id="session-123",
            trajectory={"answer_hash": "abc123", "confidence": 0.9},
            is_final=False,
        )

        assert result["partial"] is True

    @patch("reflexia.client.requests.Session")
    def test_adaptive_check_success(self, mock_session_class, client):
        """Test successful adaptive check."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}

        response = Mock()
        response.ok = True
        response.status_code = 200
        response.json.return_value = {
            "abstained": False,
            "winning_hash": "abc123",
            "confidence": 0.85,
            "adaptive_k": 3,
        }
        response.headers = {}

        mock_session.request.return_value = response
        client._session = mock_session

        result = client.epistemic.adaptive_check(
            agent_id="test-agent-1",
            trajectories=[
                {"answer_hash": "abc123", "confidence": 0.9},
            ],
        )

        assert result["abstained"] is False

