"""
Agimus SDK Exceptions.

All exceptions inherit from AgimusError for easy catching.
"""
from typing import Any, Optional


class AgimusError(Exception):
    """Base exception for all Agimus SDK errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class AuthenticationError(AgimusError):
    """Raised when API key is invalid or missing."""

    pass


class NotFoundError(AgimusError):
    """Raised when entity or object is not found."""

    def __init__(self, entity: str, pk: Optional[str] = None):
        self.entity = entity
        self.pk = pk
        if pk:
            message = f"Object '{pk}' not found in '{entity}'"
        else:
            message = f"Entity '{entity}' not found"
        super().__init__(message)


class ValidationError(AgimusError):
    """Raised when request data is invalid."""

    def __init__(self, message: str, field: Optional[str] = None, details: Optional[dict] = None):
        self.field = field
        self.details = details
        super().__init__(message)


class AccessDeniedError(AgimusError):
    """Raised when user lacks permission."""

    pass


class RateLimitError(AgimusError):
    """Raised when rate limit is exceeded."""

    def __init__(self, retry_after: Optional[int] = None):
        self.retry_after = retry_after
        message = "Rate limit exceeded"
        if retry_after:
            message += f". Retry after {retry_after} seconds"
        super().__init__(message)


class ServerError(AgimusError):
    """Raised when server returns 5xx error."""

    def __init__(self, message: str, status_code: int = 500):
        self.status_code = status_code
        super().__init__(message)


class APIError(AgimusError):
    """
    General API error with full error details.

    Attributes:
        code: Error code from API (e.g., "ENTITY_NOT_FOUND")
        message: Human-readable error message
        status_code: HTTP status code
        request_id: Request ID for support/debugging
        field: Related field (for validation errors)
    """

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int,
        request_id: Optional[str] = None,
        field: Optional[str] = None,
    ):
        self.code = code
        self.status_code = status_code
        self.request_id = request_id
        self.field = field
        super().__init__(message)

    def __str__(self) -> str:
        parts = [f"[{self.code}] {self.message}"]
        if self.request_id:
            parts.append(f"(request_id: {self.request_id})")
        return " ".join(parts)
