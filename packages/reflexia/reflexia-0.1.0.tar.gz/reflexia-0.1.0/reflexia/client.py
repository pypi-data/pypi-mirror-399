"""Main Reflexia client class."""

from typing import Optional, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from reflexia.exceptions import (
    ReflexiaAPIError,
    ReflexiaAuthenticationError,
    ReflexiaRateLimitError,
    ReflexiaNotFoundError,
    ReflexiaNetworkError,
)
from reflexia.field import FieldClient
from reflexia.epistemic import EpistemicClient
from reflexia.patterns import PatternClient
from reflexia.payment import PaymentClient
from reflexia.account import AccountClient


class ReflexiaClient:
    """
    Main client for interacting with the Reflexia API.

    This is a convenience wrapper around HTTP requests to the Reflexia API.
    The actual value (field computation, state persistence, etc.) is provided
    by the Reflexia backend infrastructure.

    Args:
        api_key: Your Reflexia API key (starts with 'rk_')
        base_url: Base URL for the API (defaults to production)
        tenant_id: Optional tenant ID (usually extracted from API key)
        timeout: Request timeout in seconds (default: 30)
        max_retries: Maximum number of retries for failed requests (default: 2)

    Example:
        ```python
        from reflexia import ReflexiaClient

        client = ReflexiaClient(api_key="rk_YOUR_API_KEY")

        # Register an agent
        response = client.field.register_agent(
            agent_id="worker-1",
            agent_type="researcher"
        )
        ```
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.reflexia.io",
        tenant_id: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 2,
    ):
        if not api_key:
            raise ValueError("api_key is required")
        if not api_key.startswith("rk_"):
            raise ValueError("api_key must start with 'rk_'")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.tenant_id = tenant_id
        self.timeout = timeout

        # Create session with retry strategy
        self._session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

        # Set default headers
        self._session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
        )
        if tenant_id:
            self._session.headers.update({"X-Tenant-ID": tenant_id})

        # Initialize service clients
        self.field = FieldClient(self)
        self.epistemic = EpistemicClient(self)
        self.patterns = PatternClient(self)
        self.payment = PaymentClient(self)
        self.account = AccountClient(self)

    def _request(
        self,
        method: str,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the Reflexia API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path (e.g., '/api/v1/field/sense')
            json: JSON body for request
            params: Query parameters
            headers: Additional headers

        Returns:
            Response JSON as dict

        Raises:
            ReflexiaAPIError: If API returns an error
            ReflexiaNetworkError: If network request fails
        """
        url = f"{self.base_url}{endpoint}"

        request_headers = self._session.headers.copy()
        if headers:
            request_headers.update(headers)

        try:
            response = self._session.request(
                method=method,
                url=url,
                json=json,
                params=params,
                headers=request_headers,
                timeout=self.timeout,
            )
        except requests.exceptions.RequestException as e:
            raise ReflexiaNetworkError(f"Network error: {str(e)}") from e

        # Parse error response
        if not response.ok:
            error_data = {}
            try:
                error_data = response.json()
            except ValueError:
                pass

            error_info = error_data.get("error", {})
            error_code = error_info.get("code", f"HTTP_{response.status_code}")
            error_message = error_info.get("message", response.text or response.reason)
            error_details = error_info.get("details", {})
            request_id = error_data.get("request_id")

            # Raise specific exception types
            if response.status_code == 401:
                raise ReflexiaAuthenticationError(error_message, error_details)
            elif response.status_code == 404:
                raise ReflexiaNotFoundError(error_message, error_details)
            elif response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                retry_after_int = int(retry_after) if retry_after and retry_after.isdigit() else None
                raise ReflexiaRateLimitError(
                    error_message, retry_after=retry_after_int, details=error_details
                )
            else:
                raise ReflexiaAPIError(
                    error_message,
                    error_code,
                    response.status_code,
                    error_details,
                    request_id,
                )

        return response.json()

    def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Make a GET request."""
        return self._request("GET", endpoint, params=params, headers=headers)

    def post(
        self, endpoint: str, json: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Make a POST request."""
        return self._request("POST", endpoint, json=json, headers=headers)

    def put(
        self, endpoint: str, json: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Make a PUT request."""
        return self._request("PUT", endpoint, json=json, headers=headers)

    def patch(
        self, endpoint: str, json: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Make a PATCH request."""
        return self._request("PATCH", endpoint, json=json, headers=headers)

    def delete(self, endpoint: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Make a DELETE request."""
        return self._request("DELETE", endpoint, headers=headers)

