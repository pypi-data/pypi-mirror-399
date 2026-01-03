"""
Reflexia Python SDK

A convenience wrapper around the Reflexia API for quantum coordination
infrastructure for autonomous agent swarms.

Example:
    ```python
    from reflexia import ReflexiaClient

    client = ReflexiaClient(api_key="rk_YOUR_API_KEY")
    
    # Register an agent
    response = client.field.register_agent(
        agent_id="worker-1",
        agent_type="researcher"
    )
    
    # Sense the field
    sense = client.field.sense(
        agent_id="worker-1",
        session_token=response.session_token
    )
    ```
"""

from reflexia.client import ReflexiaClient
from reflexia.exceptions import (
    ReflexiaError,
    ReflexiaAPIError,
    ReflexiaAuthenticationError,
    ReflexiaRateLimitError,
    ReflexiaNotFoundError,
)

__version__ = "0.1.0"
__all__ = [
    "ReflexiaClient",
    "ReflexiaError",
    "ReflexiaAPIError",
    "ReflexiaAuthenticationError",
    "ReflexiaRateLimitError",
    "ReflexiaNotFoundError",
]

