"""Payment API client."""

from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from reflexia.client import ReflexiaClient


class PaymentClient:
    """
    Client for Payment API operations.

    Provides methods for x402 payment verification, pricing, and usage tracking.
    The actual payment processing happens on Reflexia's backend.
    """

    def __init__(self, client: "ReflexiaClient"):
        self._client = client

    def verify(
        self,
        payment_header: str,
        operation: str,
        compute_units: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Verify an x402 payment header.

        Args:
            payment_header: x402 payment header (base64-encoded)
            operation: Operation being paid for
            compute_units: Optional compute units for the operation

        Returns:
            Payment verification result

        Example:
            ```python
            result = client.payment.verify(
                payment_header="x402 <base64-payment>",
                operation="sense_field"
            )
            if result["verified"]:
                print("Payment verified")
            ```
        """
        payload: Dict[str, Any] = {
            "payment_header": payment_header,
            "operation": operation,
        }
        if compute_units is not None:
            payload["compute_units"] = compute_units

        return self._client.post("/api/v1/payment/verify", json=payload)

    def get_pricing(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """
        Get pricing information for operations.

        Args:
            operation: Optional operation name to get specific pricing

        Returns:
            Pricing information

        Example:
            ```python
            pricing = client.payment.get_pricing()
            print(f"Sense field: {pricing.get('sense_field', {}).get('price')} sats")
            ```
        """
        params = {}
        if operation:
            params["operation"] = operation

        return self._client.get("/api/v1/payment/pricing", params=params)

    def get_usage(self) -> Dict[str, Any]:
        """
        Get usage statistics for the tenant.

        Returns:
            Usage statistics including total operations, costs, etc.

        Example:
            ```python
            usage = client.payment.get_usage()
            print(f"Total operations: {usage.get('total_operations')}")
            print(f"Total cost: {usage.get('total_cost')} sats")
            ```
        """
        return self._client.get("/api/v1/payment/usage")

    def settle(
        self,
        payment_header: str,
        operation: str,
        compute_units: int,
        duration_ms: int,
    ) -> Dict[str, Any]:
        """
        Settle a payment after operation completion.

        Args:
            payment_header: x402 payment header
            operation: Operation that was performed
            compute_units: Compute units consumed
            duration_ms: Operation duration in milliseconds

        Returns:
            Settlement result

        Example:
            ```python
            result = client.payment.settle(
                payment_header="x402 <base64-payment>",
                operation="sense_field",
                compute_units=1,
                duration_ms=150
            )
            ```
        """
        payload = {
            "payment_header": payment_header,
            "operation": operation,
            "compute_units": compute_units,
            "duration_ms": duration_ms,
        }
        return self._client.post("/api/v1/payment/settle", json=payload)

