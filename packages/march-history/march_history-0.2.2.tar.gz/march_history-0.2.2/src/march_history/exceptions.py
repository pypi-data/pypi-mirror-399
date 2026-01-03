from __future__ import annotations

"""Exception hierarchy for march-history SDK."""

from typing import Any


class MarchHistoryError(Exception):
    """Base exception for all SDK errors."""

    pass


class APIError(MarchHistoryError):
    """Base class for API-related errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize API error.

        Args:
            message: Human-readable error message
            status_code: HTTP status code
            response_body: Full API error response body
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_body = response_body or {}
        self.error_code = self.response_body.get("error")
        self.details = self.response_body.get("details", [])

    def __str__(self) -> str:
        """String representation of the error."""
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class ValidationError(APIError):
    """HTTP 422 Unprocessable Entity - Validation errors."""

    pass


class NotFoundError(APIError):
    """HTTP 404 Not Found - Resource not found."""

    pass


class ConflictError(APIError):
    """HTTP 409 Conflict - Resource conflict (e.g., duplicate sequence number)."""

    pass


class BadRequestError(APIError):
    """HTTP 400 Bad Request - Invalid request format."""

    pass


class ServerError(APIError):
    """HTTP 500+ Server errors."""

    pass


class NetworkError(MarchHistoryError):
    """Network-related errors (connection failures, timeouts)."""

    pass


class ConfigurationError(MarchHistoryError):
    """Invalid client configuration."""

    pass


class RetryError(MarchHistoryError):
    """Maximum retry attempts exceeded."""

    def __init__(self, message: str, last_exception: Exception) -> None:
        """
        Initialize retry error.

        Args:
            message: Error message
            last_exception: The last exception that caused the retry to fail
        """
        super().__init__(message)
        self.last_exception = last_exception

    def __str__(self) -> str:
        """String representation of the error."""
        return f"{self.args[0]}. Last error: {self.last_exception}"
