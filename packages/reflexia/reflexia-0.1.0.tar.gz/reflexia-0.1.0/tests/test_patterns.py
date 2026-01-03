"""Tests for Pattern Store API client."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from reflexia import ReflexiaClient


class TestPatternClient:
    """Test PatternClient methods."""

    @patch("reflexia.client.requests.Session")
    def test_store_success(
        self, mock_session_class, client, mock_pattern_store_response
    ):
        """Test successful pattern storage."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}

        response = Mock()
        response.ok = True
        response.status_code = 200
        response.json.return_value = mock_pattern_store_response
        response.headers = {}

        mock_session.request.return_value = response
        client._session = mock_session

        result = client.patterns.store(
            agent_id="test-agent-1",
            agent_type="researcher",
            entity_hash="abc123",
            outcome_hash="def456",
            confidence=0.9,
        )

        assert result["pattern_id"] == "pattern-123"
        assert result["is_new"] is True
        assert result["occurrence_count"] == 1

    def test_store_invalid_confidence_too_high(self, client):
        """Test store with confidence > 1."""
        with pytest.raises(ValueError, match="confidence must be between 0 and 1"):
            client.patterns.store(
                agent_id="test-agent-1",
                agent_type="researcher",
                entity_hash="abc123",
                outcome_hash="def456",
                confidence=1.5,
            )

    def test_store_invalid_confidence_too_low(self, client):
        """Test store with confidence < 0."""
        with pytest.raises(ValueError, match="confidence must be between 0 and 1"):
            client.patterns.store(
                agent_id="test-agent-1",
                agent_type="researcher",
                entity_hash="abc123",
                outcome_hash="def456",
                confidence=-0.1,
            )

    def test_store_invalid_entity_hash(self, client):
        """Test store with invalid entity hash format."""
        with pytest.raises(ValueError, match="entity_hash must be a hexadecimal string"):
            client.patterns.store(
                agent_id="test-agent-1",
                agent_type="researcher",
                entity_hash="not-hex!",
                outcome_hash="def456",
                confidence=0.9,
            )

    def test_store_invalid_outcome_hash(self, client):
        """Test store with invalid outcome hash format."""
        with pytest.raises(ValueError, match="outcome_hash must be a hexadecimal string"):
            client.patterns.store(
                agent_id="test-agent-1",
                agent_type="researcher",
                entity_hash="abc123",
                outcome_hash="not-hex!",
                confidence=0.9,
            )

    @patch("reflexia.client.requests.Session")
    def test_store_with_context_hashes(
        self, mock_session_class, client, mock_pattern_store_response
    ):
        """Test store with context hashes."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}

        response = Mock()
        response.ok = True
        response.status_code = 200
        response.json.return_value = mock_pattern_store_response
        response.headers = {}

        mock_session.request.return_value = response
        client._session = mock_session

        result = client.patterns.store(
            agent_id="test-agent-1",
            agent_type="researcher",
            entity_hash="abc123",
            outcome_hash="def456",
            confidence=0.9,
            context_hashes={"source": "xyz789", "timestamp": "timestamp123"},
        )

        # Verify context_hashes were included
        call_args = mock_session.request.call_args
        assert "context_hashes" in call_args[1]["json"]

    @patch("reflexia.client.requests.Session")
    def test_query_success(
        self, mock_session_class, client, mock_pattern_query_response
    ):
        """Test successful pattern query."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}

        response = Mock()
        response.ok = True
        response.status_code = 200
        response.json.return_value = mock_pattern_query_response
        response.headers = {}

        mock_session.request.return_value = response
        client._session = mock_session

        result = client.patterns.query(
            entity_hash="abc123", min_confidence=0.7, limit=10
        )

        assert "patterns" in result
        assert len(result["patterns"]) == 1
        assert result["patterns"][0]["confidence"] == 0.9

    @patch("reflexia.client.requests.Session")
    def test_query_with_filters(self, mock_session_class, client, mock_pattern_query_response):
        """Test query with all filters."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}

        response = Mock()
        response.ok = True
        response.status_code = 200
        response.json.return_value = mock_pattern_query_response
        response.headers = {}

        mock_session.request.return_value = response
        client._session = mock_session

        result = client.patterns.query(
            entity_hash="abc123",
            agent_type="researcher",
            min_confidence=0.8,
            limit=5,
        )

        # Verify filters were included
        call_args = mock_session.request.call_args
        assert call_args[1]["json"]["agent_type"] == "researcher"
        assert call_args[1]["json"]["min_confidence"] == 0.8
        assert call_args[1]["json"]["limit"] == 5

    @patch("reflexia.client.requests.Session")
    def test_aggregate_success(
        self, mock_session_class, client, mock_aggregate_response
    ):
        """Test successful pattern aggregation."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}

        response = Mock()
        response.ok = True
        response.status_code = 200
        response.json.return_value = mock_aggregate_response
        response.headers = {}

        mock_session.request.return_value = response
        client._session = mock_session

        result = client.patterns.aggregate(
            entity_hash="abc123",
            agent_type="researcher",
            min_tenant_count=5,
            min_occurrences=10,
        )

        assert result["k_anonymity_met"] is True
        assert len(result["patterns"]) == 1
        assert result["patterns"][0]["tenant_count"] == 5

