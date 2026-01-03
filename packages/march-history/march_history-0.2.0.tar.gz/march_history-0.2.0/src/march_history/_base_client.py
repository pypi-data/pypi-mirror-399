from __future__ import annotations

"""Base HTTP client with retry logic for march-history SDK."""

import random
import time
from functools import wraps
from typing import Any, Callable, TypeVar

import httpx

from march_history._version import __version__
from march_history.config import ClientConfig
from march_history.exceptions import (
    APIError,
    BadRequestError,
    ConflictError,
    NetworkError,
    NotFoundError,
    RetryError,
    ServerError,
    ValidationError,
)

F = TypeVar("F", bound=Callable[..., Any])


def with_retry(func: F) -> F:
    """
    Decorator for retry logic with exponential backoff.

    Retries failed requests based on the retry configuration. Implements
    exponential backoff with jitter to avoid thundering herd.

    Args:
        func: Function to wrap with retry logic

    Returns:
        Wrapped function with retry behavior
    """

    @wraps(func)
    def wrapper(self: "BaseHTTPClient", *args: Any, **kwargs: Any) -> Any:
        config = self._config.retry_config
        last_exception: Exception | None = None

        for attempt in range(config.max_retries + 1):
            try:
                return func(self, *args, **kwargs)
            except httpx.NetworkError as e:
                last_exception = NetworkError(str(e))
            except httpx.TimeoutException as e:
                last_exception = NetworkError(f"Request timeout: {e}")
            except ServerError as e:
                if e.status_code not in config.retry_status_codes:
                    raise
                last_exception = e

            # Don't sleep after last attempt
            if attempt < config.max_retries:
                # Exponential backoff with jitter
                backoff = min(
                    config.backoff_factor**attempt,
                    config.max_backoff_seconds,
                )
                jitter = random.uniform(0, 0.1 * backoff)
                time.sleep(backoff + jitter)

        # All retries exhausted
        raise RetryError(
            f"Max retries ({config.max_retries}) exceeded",
            last_exception or Exception("Unknown error"),
        )

    return wrapper  # type: ignore


class BaseHTTPClient:
    """
    Base HTTP client with retry logic and error handling.

    Provides low-level HTTP operations with automatic retries, exponential
    backoff, and proper error mapping.
    """

    def __init__(self, config: ClientConfig) -> None:
        """
        Initialize HTTP client.

        Args:
            config: Client configuration
        """
        self._config = config
        self._client_instance: httpx.Client | None = None

    @property
    def _client(self) -> httpx.Client:
        """
        Lazy-create httpx client on first access.

        Returns:
            Configured httpx.Client instance
        """
        if self._client_instance is None:
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": f"march-history-python/{__version__}",
            }
            if self._config.api_key:
                headers["X-API-Key"] = self._config.api_key
            if self._config.custom_headers:
                headers.update(self._config.custom_headers)

            self._client_instance = httpx.Client(
                base_url=self._config.base_url,
                timeout=self._config.timeout,
                headers=headers,
                limits=httpx.Limits(
                    max_connections=self._config.max_connections,
                    max_keepalive_connections=self._config.max_keepalive_connections,
                ),
            )
        return self._client_instance

    @with_retry
    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """
        Make GET request.

        Args:
            path: URL path
            params: Query parameters

        Returns:
            Response data

        Raises:
            APIError: On API errors
            NetworkError: On network errors
            RetryError: If max retries exceeded
        """
        response = self._client.get(path, params=params)
        return self._handle_response(response)

    @with_retry
    def post(self, path: str, json: dict[str, Any] | None = None) -> Any:
        """
        Make POST request.

        Args:
            path: URL path
            json: JSON request body

        Returns:
            Response data

        Raises:
            APIError: On API errors
            NetworkError: On network errors
            RetryError: If max retries exceeded
        """
        response = self._client.post(path, json=json)
        return self._handle_response(response)

    @with_retry
    def patch(self, path: str, json: dict[str, Any] | None = None) -> Any:
        """
        Make PATCH request.

        Args:
            path: URL path
            json: JSON request body

        Returns:
            Response data

        Raises:
            APIError: On API errors
            NetworkError: On network errors
            RetryError: If max retries exceeded
        """
        response = self._client.patch(path, json=json)
        return self._handle_response(response)

    @with_retry
    def delete(self, path: str) -> None:
        """
        Make DELETE request.

        Args:
            path: URL path

        Raises:
            APIError: On API errors
            NetworkError: On network errors
            RetryError: If max retries exceeded
        """
        response = self._client.delete(path)
        if not response.is_success:
            self._handle_response(response)

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """
        Handle HTTP response and raise appropriate exceptions.

        Args:
            response: HTTP response

        Returns:
            Parsed response data

        Raises:
            APIError: On API errors (4xx, 5xx)
        """
        if response.is_success:
            # Return empty dict for 204 No Content
            return response.json() if response.content else {}

        # Parse error response
        try:
            error_body = response.json()
        except Exception:
            error_body = {"message": response.text or "Unknown error"}

        message = error_body.get("message", f"HTTP {response.status_code}")

        # Map status codes to exception classes
        error_map: dict[int, type[APIError]] = {
            400: BadRequestError,
            404: NotFoundError,
            409: ConflictError,
            422: ValidationError,
        }

        exception_class = error_map.get(response.status_code)
        if exception_class:
            raise exception_class(message, response.status_code, error_body)
        elif response.status_code >= 500:
            raise ServerError(message, response.status_code, error_body)
        else:
            raise APIError(message, response.status_code, error_body)

    def close(self) -> None:
        """Close HTTP client connections."""
        if self._client_instance is not None:
            self._client_instance.close()

    def __del__(self) -> None:
        """Automatic cleanup when object is garbage collected."""
        if self._client_instance is not None:
            self._client_instance.close()
