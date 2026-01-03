"""Field Engine API client."""

from typing import Optional, List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from reflexia.client import ReflexiaClient


class FieldClient:
    """
    Client for Field Engine API operations.

    Provides methods for agent registration, field sensing, modification,
    and metrics. The actual field computation happens on Reflexia's backend.
    """

    def __init__(self, client: "ReflexiaClient"):
        self._client = client

    def register_agent(
        self,
        agent_id: str,
        agent_type: str,
        semantic_embedding: Optional[List[float]] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Register an agent in the field.

        Args:
            agent_id: Unique identifier for the agent
            agent_type: Type of agent (opaque string, not interpreted)
            semantic_embedding: Optional semantic embedding for positioning
            config: Optional agent configuration

        Returns:
            Response containing agent_id, position, and session_token

        Example:
            ```python
            response = client.field.register_agent(
                agent_id="worker-1",
                agent_type="researcher"
            )
            session_token = response["session_token"]
            ```
        """
        payload = {
            "agent_id": agent_id,
            "agent_type": agent_type,
        }
        if semantic_embedding is not None:
            payload["semantic_embedding"] = semantic_embedding
        if config is not None:
            payload["config"] = config

        return self._client.post("/api/v1/field/agents", json=payload)

    def sense(self, agent_id: str, session_token: str) -> Dict[str, Any]:
        """
        Sense the field at the agent's position.

        Args:
            agent_id: Agent identifier
            session_token: Session token from register_agent

        Returns:
            Field sense result with nearby agents, gradients, etc.

        Example:
            ```python
            sense_result = client.field.sense(
                agent_id="worker-1",
                session_token=session_token
            )
            nearby_agents = sense_result.get("nearby_agents", [])
            ```
        """
        payload = {
            "agent_id": agent_id,
            "session_token": session_token,
        }
        return self._client.post("/api/v1/field/sense", json=payload)

    def modify(
        self,
        agent_id: str,
        session_token: str,
        delta: float,
        outcome: str,
    ) -> Dict[str, Any]:
        """
        Modify the field at the agent's position.

        Args:
            agent_id: Agent identifier
            session_token: Session token from register_agent
            delta: Field modification delta (positive = success, negative = uncertainty)
            outcome: Outcome type ("success", "uncertain", or "failure")

        Returns:
            Response with accepted status and new field value

        Example:
            ```python
            result = client.field.modify(
                agent_id="worker-1",
                session_token=session_token,
                delta=0.5,
                outcome="success"
            )
            ```
        """
        if outcome not in ["success", "uncertain", "failure"]:
            raise ValueError("outcome must be 'success', 'uncertain', or 'failure'")

        payload = {
            "agent_id": agent_id,
            "session_token": session_token,
            "delta": delta,
            "outcome": outcome,
        }
        return self._client.post("/api/v1/field/modify", json=payload)

    def batch_modify(
        self,
        agent_id: str,
        session_token: str,
        modifications: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Batch modify the field with multiple deltas.

        Args:
            agent_id: Agent identifier
            session_token: Session token from register_agent
            modifications: List of modification objects with delta and outcome

        Returns:
            Batch modification result

        Example:
            ```python
            result = client.field.batch_modify(
                agent_id="worker-1",
                session_token=session_token,
                modifications=[
                    {"delta": 0.5, "outcome": "success"},
                    {"delta": -0.2, "outcome": "uncertain"},
                ]
            )
            ```
        """
        payload = {
            "agent_id": agent_id,
            "session_token": session_token,
            "modifications": modifications,
        }
        return self._client.post("/api/v1/field/batch-modify", json=payload)

    def get_agents(self) -> Dict[str, Any]:
        """
        Get all registered agents for the tenant.

        Returns:
            List of agents with their positions and metadata

        Example:
            ```python
            agents = client.field.get_agents()
            for agent in agents.get("agents", []):
                print(f"Agent {agent['agent_id']} at {agent['position']}")
            ```
        """
        return self._client.get("/api/v1/field/agents")

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get field metrics for the tenant.

        Returns:
            Field metrics including coherence, energy, agent count, etc.

        Example:
            ```python
            metrics = client.field.get_metrics()
            print(f"Coherence: {metrics.get('coherence')}")
            print(f"Active agents: {metrics.get('agent_count')}")
            ```
        """
        return self._client.get("/api/v1/field/metrics")

    def stream(
        self,
        session_token: str,
        tenant_id: Optional[str] = None,
        interval_ms: Optional[int] = None,
    ):
        """
        Stream field updates via Server-Sent Events (SSE).

        Args:
            session_token: Session token from register_agent
            tenant_id: Optional tenant ID
            interval_ms: Update interval in milliseconds

        Yields:
            Field update messages

        Example:
            ```python
            for update in client.field.stream(session_token=session_token):
                print(f"Iteration {update['iteration']}: coherence={update['coherence']}")
            ```
        """
        payload = {
            "session_token": session_token,
        }
        if tenant_id:
            payload["tenant_id"] = tenant_id
        if interval_ms:
            payload["interval_ms"] = interval_ms

        # Note: This is a simplified version. Full SSE streaming would require
        # additional implementation with requests or aiohttp for async support.
        response = self._client.post("/api/v1/field/stream", json=payload)
        return response

