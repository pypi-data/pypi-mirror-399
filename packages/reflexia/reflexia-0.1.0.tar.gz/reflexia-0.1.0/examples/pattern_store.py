"""
Example: Using Pattern Store for pattern observation and querying.

This demonstrates storing patterns, querying tenant-scoped patterns,
and getting cross-tenant aggregates with k-anonymity protection.
"""

from reflexia import ReflexiaClient
import hashlib

client = ReflexiaClient(api_key="rk_YOUR_API_KEY")

# Hash an entity (e.g., a document, image, or data point)
entity = "document_123"
entity_hash = hashlib.sha256(entity.encode()).hexdigest()[:64]

# Hash an outcome (e.g., classification result)
outcome = "positive_sentiment"
outcome_hash = hashlib.sha256(outcome.encode()).hexdigest()[:64]

# Store a pattern observation
print("Storing pattern...")
pattern_result = client.patterns.store(
    agent_id="worker-1",
    agent_type="researcher",
    entity_hash=entity_hash,
    outcome_hash=outcome_hash,
    confidence=0.9,
    context_hashes={
        "source": hashlib.sha256("api".encode()).hexdigest()[:64],
        "timestamp": hashlib.sha256("2025-01-01".encode()).hexdigest()[:64],
    },
)

print(f"Pattern ID: {pattern_result['pattern_id']}")
print(f"Is new: {pattern_result['is_new']}")
print(f"Occurrence count: {pattern_result['occurrence_count']}")

# Query patterns for the same entity
print("\nQuerying patterns...")
query_results = client.patterns.query(
    entity_hash=entity_hash,
    agent_type="researcher",
    min_confidence=0.7,
    limit=10,
)

print(f"Found {len(query_results.get('patterns', []))} patterns")
for pattern in query_results.get("patterns", [])[:5]:
    print(f"  - Outcome: {pattern['outcome_hash'][:16]}..., Confidence: {pattern['confidence']:.2f}")

# Get cross-tenant aggregates (k-anonymity protected)
print("\nGetting cross-tenant aggregates...")
aggregates = client.patterns.aggregate(
    entity_hash=entity_hash,
    agent_type="researcher",
    min_tenant_count=5,  # K-anonymity threshold
    min_occurrences=10,
)

if aggregates["k_anonymity_met"]:
    print("✅ K-anonymity threshold met")
    for pattern in aggregates["patterns"]:
        print(f"  - Outcome: {pattern['outcome_hash'][:16]}...")
        print(f"    Avg confidence: {pattern['avg_confidence']:.2f}")
        print(f"    Tenant count: {pattern['tenant_count']}")
        print(f"    Total occurrences: {pattern['total_occurrences']}")
else:
    print("❌ K-anonymity threshold not met (insufficient data)")

