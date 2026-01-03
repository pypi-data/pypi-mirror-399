"""Custom exceptions for the Trix SDK."""

from typing import Any, Dict, Optional


class TrixError(Exception):
    """Base exception for all Trix errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response


class AuthenticationError(TrixError):
    """Raised when authentication fails (401)."""

    pass


class PermissionError(TrixError):
    """Raised when permission is denied (403)."""

    pass


class NotFoundError(TrixError):
    """Raised when a resource is not found (404)."""

    pass


class ValidationError(TrixError):
    """Raised when request validation fails (422)."""

    pass


class RateLimitError(TrixError):
    """Raised when rate limit is exceeded (429)."""

    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        status_code: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, status_code, response)
        self.retry_after = retry_after


class ServerError(TrixError):
    """Raised when server returns 5xx error."""

    pass


class APIError(TrixError):
    """Raised for other API errors."""

    pass


class ConnectionError(TrixError):
    """Raised when connection to API fails."""

    pass


class TimeoutError(TrixError):
    """Raised when request times out."""

    pass


class APIVersionMismatchError(TrixError):
    """Raised when SDK and API versions are incompatible."""

    def __init__(
        self,
        message: str,
        sdk_version: Optional[str] = None,
        api_version: Optional[str] = None,
        min_supported: Optional[str] = None,
        max_supported: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.sdk_version = sdk_version
        self.api_version = api_version
        self.min_supported = min_supported
        self.max_supported = max_supported
