"""
Basic usage examples for Reflexia Python SDK.

This demonstrates the core workflow: register agent, sense field, modify field.
"""

from reflexia import ReflexiaClient

# Initialize client
client = ReflexiaClient(api_key="rk_YOUR_API_KEY")

# 1. Register an agent
print("Registering agent...")
agent_response = client.field.register_agent(
    agent_id="worker-1",
    agent_type="researcher",
    semantic_embedding=[0.1, 0.2, 0.3],  # Optional: for positioning
)

session_token = agent_response["session_token"]
print(f"Agent registered. Position: {agent_response['position']}")
print(f"Session token: {session_token[:20]}...")

# 2. Sense the field
print("\nSensing field...")
sense_result = client.field.sense(
    agent_id="worker-1",
    session_token=session_token,
)

print(f"Local field value: {sense_result.get('local_value')}")
print(f"Nearby agents: {len(sense_result.get('nearby_agents', []))}")

# 3. Modify the field after an action
print("\nModifying field...")
modify_result = client.field.modify(
    agent_id="worker-1",
    session_token=session_token,
    delta=0.5,  # Positive = success signal
    outcome="success",
)

print(f"Modification accepted: {modify_result['accepted']}")
print(f"New local value: {modify_result['new_local_value']}")

# 4. Get field metrics
print("\nField metrics:")
metrics = client.field.get_metrics()
print(f"Coherence: {metrics.get('coherence')}")
print(f"Energy: {metrics.get('energy')}")
print(f"Agent count: {metrics.get('agent_count')}")

