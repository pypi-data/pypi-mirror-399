"""Pattern Store API client."""

from typing import Optional, Dict, Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from reflexia.client import ReflexiaClient


class PatternClient:
    """
    Client for Pattern Store API operations.

    Provides methods for storing, querying, and aggregating patterns.
    Pattern storage uses k-anonymity for cross-tenant aggregation.
    The actual pattern matching and aggregation happens on Reflexia's backend.
    """

    def __init__(self, client: "ReflexiaClient"):
        self._client = client

    def store(
        self,
        agent_id: str,
        agent_type: str,
        entity_hash: str,
        outcome_hash: str,
        confidence: float,
        context_hashes: Optional[Dict[str, str]] = None,
        storage_policy: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Store a pattern observation.

        Args:
            agent_id: Agent identifier
            agent_type: Type of agent
            entity_hash: Hash of entity being classified/matched (hex string, max 64 chars)
            outcome_hash: Hash of outcome (hex string, max 64 chars)
            confidence: Confidence value between 0 and 1
            context_hashes: Optional hashed context keys
            storage_policy: Optional storage policy controls

        Returns:
            Pattern storage result with pattern_id and occurrence count

        Example:
            ```python
            result = client.patterns.store(
                agent_id="worker-1",
                agent_type="researcher",
                entity_hash="abc123",
                outcome_hash="def456",
                confidence=0.9
            )
            print(f"Pattern ID: {result['pattern_id']}")
            print(f"Is new: {result['is_new']}")
            ```
        """
        if not (0 <= confidence <= 1):
            raise ValueError("confidence must be between 0 and 1")

        # Validate hash formats
        if not all(c in "0123456789abcdefABCDEF" for c in entity_hash) or len(entity_hash) > 64:
            raise ValueError("entity_hash must be a hexadecimal string (max 64 chars)")
        if not all(c in "0123456789abcdefABCDEF" for c in outcome_hash) or len(outcome_hash) > 64:
            raise ValueError("outcome_hash must be a hexadecimal string (max 64 chars)")

        payload = {
            "agent_id": agent_id,
            "agent_type": agent_type,
            "entity_hash": entity_hash,
            "outcome_hash": outcome_hash,
            "confidence": confidence,
        }
        if context_hashes:
            payload["context_hashes"] = context_hashes
        if storage_policy:
            payload["storage_policy"] = storage_policy

        return self._client.post("/api/v1/patterns/store", json=payload)

    def query(
        self,
        entity_hash: str,
        agent_type: Optional[str] = None,
        limit: Optional[int] = None,
        min_confidence: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Query patterns for an entity (tenant-scoped).

        Args:
            entity_hash: Hash of entity to look up
            agent_type: Optional filter by agent type
            limit: Maximum results (default: 10)
            min_confidence: Confidence threshold (default: 0.0)

        Returns:
            List of matching patterns

        Example:
            ```python
            results = client.patterns.query(
                entity_hash="abc123",
                min_confidence=0.7,
                limit=5
            )
            for pattern in results.get("patterns", []):
                print(f"Outcome: {pattern['outcome_hash']}, Confidence: {pattern['confidence']}")
            ```
        """
        payload: Dict[str, Any] = {
            "entity_hash": entity_hash,
        }
        if agent_type:
            payload["agent_type"] = agent_type
        if limit is not None:
            payload["limit"] = limit
        if min_confidence is not None:
            payload["min_confidence"] = min_confidence

        return self._client.post("/api/v1/patterns/query", json=payload)

    def aggregate(
        self,
        entity_hash: str,
        agent_type: str,
        min_tenant_count: Optional[int] = None,
        min_occurrences: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get cross-tenant aggregate patterns (k-anonymity protected).

        Args:
            entity_hash: Hash of entity to look up
            agent_type: Agent type filter
            min_tenant_count: K-anonymity threshold (default: 3)
            min_occurrences: Minimum observations (default: 5)

        Returns:
            Aggregate patterns with k-anonymity status

        Example:
            ```python
            aggregates = client.patterns.aggregate(
                entity_hash="abc123",
                agent_type="researcher",
                min_tenant_count=5
            )
            if aggregates["k_anonymity_met"]:
                for pattern in aggregates["patterns"]:
                    print(f"Outcome: {pattern['outcome_hash']}")
                    print(f"Avg confidence: {pattern['avg_confidence']}")
            ```
        """
        payload: Dict[str, Any] = {
            "entity_hash": entity_hash,
            "agent_type": agent_type,
        }
        if min_tenant_count is not None:
            payload["min_tenant_count"] = min_tenant_count
        if min_occurrences is not None:
            payload["min_occurrences"] = min_occurrences

        return self._client.post("/api/v1/patterns/aggregate", json=payload)

