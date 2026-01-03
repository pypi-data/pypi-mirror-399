"""Epistemic Service API client."""

from typing import Optional, List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from reflexia.client import ReflexiaClient


class EpistemicClient:
    """
    Client for Epistemic Service API operations.

    Provides methods for multi-trajectory consistency checking using
    hash-based majority voting. The actual voting logic runs on Reflexia's backend.
    """

    def __init__(self, client: "ReflexiaClient"):
        self._client = client

    def check_consistency(
        self,
        agent_id: str,
        trajectories: List[Dict[str, Any]],
        request_id: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Check consistency of multiple trajectories using majority voting.

        Args:
            agent_id: Agent identifier
            trajectories: List of trajectory objects with answer_hash and confidence
            request_id: Optional request ID for idempotency
            config: Optional configuration (abstention_threshold, etc.)

        Returns:
            Consistency result with winning hash, confidence, and abstention status

        Example:
            ```python
            result = client.epistemic.check_consistency(
                agent_id="worker-1",
                trajectories=[
                    {"answer_hash": "abc123", "confidence": 0.9},
                    {"answer_hash": "abc123", "confidence": 0.85},
                    {"answer_hash": "def456", "confidence": 0.7},
                ]
            )
            if not result["abstained"]:
                print(f"Winning answer: {result['winning_hash']}")
            ```
        """
        if not trajectories:
            raise ValueError("trajectories must be a non-empty list")

        payload = {
            "agent_id": agent_id,
            "trajectories": trajectories,
        }
        if request_id:
            payload["request_id"] = request_id
        if config:
            payload["config"] = config

        return self._client.post("/api/v1/epistemic/consistency", json=payload)

    def stream_consistency(
        self,
        agent_id: str,
        session_id: str,
        trajectory: Dict[str, Any],
        is_final: bool = False,
    ) -> Dict[str, Any]:
        """
        Stream consistency checks incrementally as trajectories arrive.

        Args:
            agent_id: Agent identifier
            session_id: Session ID for grouping trajectories
            trajectory: Trajectory object with answer_hash and confidence
            is_final: Whether this is the final trajectory in the stream

        Returns:
            Partial or final consistency result

        Example:
            ```python
            # Stream first trajectory
            result = client.epistemic.stream_consistency(
                agent_id="worker-1",
                session_id="session-123",
                trajectory={"answer_hash": "abc123", "confidence": 0.9},
                is_final=False
            )

            # Stream final trajectory
            result = client.epistemic.stream_consistency(
                agent_id="worker-1",
                session_id="session-123",
                trajectory={"answer_hash": "abc123", "confidence": 0.85},
                is_final=True
            )
            ```
        """
        payload = {
            "agent_id": agent_id,
            "session_id": session_id,
            "trajectory": trajectory,
            "is_final": is_final,
        }
        return self._client.post("/api/v1/epistemic/stream", json=payload)

    def recommend_k(
        self,
        estimated_tokens: Optional[int] = None,
        complexity_hint: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get recommended number of trajectories (k) based on task complexity.

        Args:
            estimated_tokens: Estimated token count for the task
            complexity_hint: Complexity hint ("trivial", "medium", "complex", "unknown")

        Returns:
            Recommended k value with cost multiplier and reasoning

        Example:
            ```python
            recommendation = client.epistemic.recommend_k(
                complexity_hint="complex"
            )
            print(f"Recommended k: {recommendation['recommended_k']}")
            print(f"Reasoning: {recommendation['reasoning']}")
            ```
        """
        payload = {}
        if estimated_tokens is not None:
            payload["estimated_tokens"] = estimated_tokens
        if complexity_hint:
            if complexity_hint not in ["trivial", "medium", "complex", "unknown"]:
                raise ValueError(
                    "complexity_hint must be 'trivial', 'medium', 'complex', or 'unknown'"
                )
            payload["complexity_hint"] = complexity_hint

        return self._client.post("/api/v1/epistemic/recommend-k", json=payload)

    def adaptive_check(
        self,
        agent_id: str,
        trajectories: List[Dict[str, Any]],
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Adaptive consistency check that adjusts k based on confidence.

        Args:
            agent_id: Agent identifier
            trajectories: List of trajectory objects
            request_id: Optional request ID for idempotency

        Returns:
            Consistency result with adaptive k value

        Example:
            ```python
            result = client.epistemic.adaptive_check(
                agent_id="worker-1",
                trajectories=[...]
            )
            ```
        """
        payload = {
            "agent_id": agent_id,
            "trajectories": trajectories,
        }
        if request_id:
            payload["request_id"] = request_id

        return self._client.post("/api/v1/epistemic/adaptive-check", json=payload)

