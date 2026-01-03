"""Account API client."""

from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from reflexia.client import ReflexiaClient


class AccountClient:
    """
    Client for Account API operations.

    Provides methods for account management, balance, subscriptions, and API keys.
    """

    def __init__(self, client: "ReflexiaClient"):
        self._client = client

    def register(self, email: str, password: str, tenant_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Register a new account.

        Args:
            email: User email
            password: User password
            tenant_name: Optional tenant name

        Returns:
            Registration result with tenant_id and API key

        Example:
            ```python
            result = client.account.register(
                email="user@example.com",
                password="secure-password"
            )
            print(f"Tenant ID: {result['tenant_id']}")
            ```
        """
        payload: Dict[str, Any] = {
            "email": email,
            "password": password,
        }
        if tenant_name:
            payload["tenant_name"] = tenant_name

        return self._client.post("/api/v1/account/register", json=payload)

    def get_balance(self) -> Dict[str, Any]:
        """
        Get account balance and credit information.

        Returns:
            Balance information including credits, sats, etc.

        Example:
            ```python
            balance = client.account.get_balance()
            print(f"Credits: {balance.get('credits')}")
            print(f"Sats: {balance.get('sats')}")
            ```
        """
        return self._client.get("/api/v1/account/balance")

    def get_wallet(self) -> Dict[str, Any]:
        """
        Get wallet information.

        Returns:
            Wallet information including address, balance, etc.

        Example:
            ```python
            wallet = client.account.get_wallet()
            print(f"Address: {wallet.get('address')}")
            ```
        """
        return self._client.get("/api/v1/account/wallet")

    def get_subscription(self) -> Dict[str, Any]:
        """
        Get subscription information.

        Returns:
            Subscription details including plan, status, etc.

        Example:
            ```python
            subscription = client.account.get_subscription()
            print(f"Plan: {subscription.get('plan')}")
            print(f"Status: {subscription.get('status')}")
            ```
        """
        return self._client.get("/api/v1/account/subscription")

    def create_api_key(self, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new API key.

        Args:
            name: Optional name for the API key

        Returns:
            API key information including the key itself

        Example:
            ```python
            result = client.account.create_api_key(name="production-key")
            print(f"API Key: {result['api_key']}")
            print(f"Key ID: {result['key_id']}")
            ```
        """
        payload = {}
        if name:
            payload["name"] = name

        return self._client.post("/api/v1/api-keys", json=payload)

    def list_api_keys(self) -> Dict[str, Any]:
        """
        List all API keys for the tenant.

        Returns:
            List of API keys with metadata

        Example:
            ```python
            keys = client.account.list_api_keys()
            for key in keys.get("keys", []):
                print(f"Key: {key['name']} ({key['key_id']})")
            ```
        """
        return self._client.get("/api/v1/api-keys")

    def revoke_api_key(self, key_id: str) -> Dict[str, Any]:
        """
        Revoke an API key.

        Args:
            key_id: ID of the API key to revoke

        Returns:
            Revocation result

        Example:
            ```python
            result = client.account.revoke_api_key(key_id="key_123")
            print("API key revoked")
            ```
        """
        return self._client.post(f"/api/v1/api-keys/{key_id}/revoke")

