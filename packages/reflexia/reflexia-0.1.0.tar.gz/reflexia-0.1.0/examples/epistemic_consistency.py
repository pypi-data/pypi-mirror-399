"""
Example: Using Epistemic Service for multi-trajectory consistency checking.

This demonstrates how to check consistency across multiple agent trajectories
using hash-based majority voting.
"""

from reflexia import ReflexiaClient

client = ReflexiaClient(api_key="rk_YOUR_API_KEY")

# Simulate multiple trajectories (e.g., from different LLM runs)
trajectories = [
    {"answer_hash": "abc123def456", "confidence": 0.9},
    {"answer_hash": "abc123def456", "confidence": 0.85},  # Same answer
    {"answer_hash": "xyz789uvw012", "confidence": 0.7},  # Different answer
    {"answer_hash": "abc123def456", "confidence": 0.88},  # Same answer
]

print("Checking consistency of trajectories...")
result = client.epistemic.check_consistency(
    agent_id="worker-1",
    trajectories=trajectories,
    config={
        "abstention_threshold": 0.66,  # Abstain if < 66% agreement
        "compute_entropy": True,
        "return_detailed_analysis": True,
    },
)

if result["abstained"]:
    print("❌ Abstained: Insufficient agreement")
else:
    print(f"✅ Consensus reached")
    print(f"Winning answer hash: {result['winning_hash']}")
    print(f"Majority vote: {result['majority_vote']:.2%}")
    print(f"Adjusted confidence: {result['confidence']:.2f}")

# Get recommended k value for a task
print("\nGetting recommended trajectory count...")
recommendation = client.epistemic.recommend_k(
    complexity_hint="complex",  # or "trivial", "medium", "unknown"
    estimated_tokens=5000,
)

print(f"Recommended k: {recommendation['recommended_k']}")
print(f"Cost multiplier: {recommendation['estimated_cost_multiplier']}x")
print(f"Reasoning: {recommendation['reasoning']}")

