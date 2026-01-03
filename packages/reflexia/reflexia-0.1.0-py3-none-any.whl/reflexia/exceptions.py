"""Custom exceptions for Reflexia SDK."""

from typing import Optional, Dict, Any


class ReflexiaError(Exception):
    """Base exception for all Reflexia SDK errors."""

    pass


class ReflexiaAPIError(ReflexiaError):
    """Error returned by the Reflexia API."""

    def __init__(
        self,
        message: str,
        code: str,
        status_code: int,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        self.request_id = request_id

    def __str__(self) -> str:
        parts = [f"{self.code}: {self.message}"]
        if self.request_id:
            parts.append(f"(request_id: {self.request_id})")
        return " ".join(parts)


class ReflexiaAuthenticationError(ReflexiaAPIError):
    """Authentication failed (401)."""

    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "UNAUTHORIZED", 401, details)


class ReflexiaRateLimitError(ReflexiaAPIError):
    """Rate limit exceeded (429)."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, "RATE_LIMIT_EXCEEDED", 429, details)
        self.retry_after = retry_after


class ReflexiaNotFoundError(ReflexiaAPIError):
    """Resource not found (404)."""

    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "NOT_FOUND", 404, details)


class ReflexiaNetworkError(ReflexiaError):
    """Network error (connection failed, timeout, etc.)."""

    pass

