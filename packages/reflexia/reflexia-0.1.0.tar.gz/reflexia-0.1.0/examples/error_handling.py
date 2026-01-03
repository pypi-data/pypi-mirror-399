"""
Example: Error handling with Reflexia SDK.

This demonstrates how to handle different types of errors that may occur
when using the SDK.
"""

from reflexia import (
    ReflexiaClient,
    ReflexiaAPIError,
    ReflexiaAuthenticationError,
    ReflexiaRateLimitError,
    ReflexiaNotFoundError,
    ReflexiaNetworkError,
)

client = ReflexiaClient(api_key="rk_YOUR_API_KEY")

# Example 1: Handle authentication errors
print("Example 1: Authentication error")
try:
    invalid_client = ReflexiaClient(api_key="rk_invalid_key")
    invalid_client.field.get_agents()
except ReflexiaAuthenticationError as e:
    print(f"❌ Authentication failed: {e.message}")
    print(f"   Error code: {e.code}")
    print(f"   Status: {e.status_code}")

# Example 2: Handle not found errors
print("\nExample 2: Not found error")
try:
    client.field.sense(agent_id="nonexistent-agent", session_token="invalid-token")
except ReflexiaNotFoundError as e:
    print(f"❌ Resource not found: {e.message}")
    print(f"   Error code: {e.code}")

# Example 3: Handle rate limit errors
print("\nExample 3: Rate limit error")
try:
    # Make many requests quickly to trigger rate limit
    for i in range(1000):
        client.field.get_metrics()
except ReflexiaRateLimitError as e:
    print(f"❌ Rate limit exceeded: {e.message}")
    print(f"   Retry after: {e.retry_after} seconds")
    print(f"   Error code: {e.code}")

# Example 4: Handle generic API errors
print("\nExample 4: Generic API error")
try:
    # Invalid request (missing required field)
    client.field.modify(
        agent_id="worker-1",
        session_token="token",
        delta=0.5,
        outcome="invalid_outcome",  # Invalid value
    )
except ReflexiaAPIError as e:
    print(f"❌ API error: {e.message}")
    print(f"   Error code: {e.code}")
    print(f"   Status: {e.status_code}")
    if e.request_id:
        print(f"   Request ID: {e.request_id}")

# Example 5: Handle network errors
print("\nExample 5: Network error")
try:
    # Use invalid base URL to simulate network error
    network_client = ReflexiaClient(
        api_key="rk_YOUR_API_KEY",
        base_url="https://invalid-url-that-does-not-exist.com",
        timeout=1,  # Short timeout
    )
    network_client.field.get_metrics()
except ReflexiaNetworkError as e:
    print(f"❌ Network error: {e}")

# Example 6: Best practice: Comprehensive error handling
print("\nExample 6: Comprehensive error handling")
try:
    result = client.field.sense(agent_id="worker-1", session_token="token")
    print("✅ Success")
except ReflexiaAuthenticationError:
    print("❌ Authentication failed - check your API key")
except ReflexiaRateLimitError as e:
    print(f"❌ Rate limited - retry after {e.retry_after} seconds")
except ReflexiaNotFoundError:
    print("❌ Resource not found - check agent_id and session_token")
except ReflexiaAPIError as e:
    print(f"❌ API error ({e.code}): {e.message}")
except ReflexiaNetworkError:
    print("❌ Network error - check your connection")
except Exception as e:
    print(f"❌ Unexpected error: {e}")

