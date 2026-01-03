from __future__ import annotations

"""Async base HTTP client with retry logic for march-history SDK."""

import asyncio
import random
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


def async_with_retry(func: F) -> F:
    """Decorator for async retry logic with exponential backoff."""

    @wraps(func)
    async def wrapper(self: "AsyncBaseHTTPClient", *args: Any, **kwargs: Any) -> Any:
        config = self._config.retry_config
        last_exception: Exception | None = None

        for attempt in range(config.max_retries + 1):
            try:
                return await func(self, *args, **kwargs)
            except httpx.NetworkError as e:
                last_exception = NetworkError(str(e))
            except httpx.TimeoutException as e:
                last_exception = NetworkError(f"Request timeout: {e}")
            except ServerError as e:
                if e.status_code not in config.retry_status_codes:
                    raise
                last_exception = e

            if attempt < config.max_retries:
                backoff = min(
                    config.backoff_factor**attempt,
                    config.max_backoff_seconds,
                )
                jitter = random.uniform(0, 0.1 * backoff)
                await asyncio.sleep(backoff + jitter)

        raise RetryError(
            f"Max retries ({config.max_retries}) exceeded",
            last_exception or Exception("Unknown error"),
        )

    return wrapper  # type: ignore


class AsyncBaseHTTPClient:
    """Async HTTP client with retry logic and error handling."""

    def __init__(self, config: ClientConfig) -> None:
        self._config = config
        self._client_instance: httpx.AsyncClient | None = None

    @property
    def _client(self) -> httpx.AsyncClient:
        """Lazy-create async httpx client on first access."""
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

            self._client_instance = httpx.AsyncClient(
                base_url=self._config.base_url,
                timeout=self._config.timeout,
                headers=headers,
                limits=httpx.Limits(
                    max_connections=self._config.max_connections,
                    max_keepalive_connections=self._config.max_keepalive_connections,
                ),
            )
        return self._client_instance

    @async_with_retry
    async def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """Make async GET request."""
        response = await self._client.get(path, params=params)
        return self._handle_response(response)

    @async_with_retry
    async def post(self, path: str, json: dict[str, Any] | None = None) -> Any:
        """Make async POST request."""
        response = await self._client.post(path, json=json)
        return self._handle_response(response)

    @async_with_retry
    async def patch(self, path: str, json: dict[str, Any] | None = None) -> Any:
        """Make async PATCH request."""
        response = await self._client.patch(path, json=json)
        return self._handle_response(response)

    @async_with_retry
    async def delete(self, path: str) -> None:
        """Make async DELETE request."""
        response = await self._client.delete(path)
        if not response.is_success:
            self._handle_response(response)

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """Handle HTTP response and raise appropriate exceptions."""
        if response.is_success:
            return response.json() if response.content else {}

        try:
            error_body = response.json()
        except Exception:
            error_body = {"message": response.text or "Unknown error"}

        message = error_body.get("message", f"HTTP {response.status_code}")

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

    async def close(self) -> None:
        """Close async HTTP client connections."""
        if self._client_instance is not None:
            await self._client_instance.aclose()

    def __del__(self) -> None:
        """Automatic cleanup when object is garbage collected."""
        if self._client_instance is not None:
            # Note: Cannot use await in __del__, so we create a task if event loop exists
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self._client_instance.aclose())
                else:
                    loop.run_until_complete(self._client_instance.aclose())
            except Exception:
                # Best effort cleanup - ignore errors
                pass
