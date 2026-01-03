from __future__ import annotations

"""Async base resource class for march-history SDK."""

from typing import Any

from march_history._async._base_client import AsyncBaseHTTPClient
from march_history.config import ClientConfig


class AsyncBaseResource:
    """Base class for all async resource classes."""

    def __init__(self, config: ClientConfig) -> None:
        self._config = config
        self._http_client = AsyncBaseHTTPClient(config)

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """Make async GET request."""
        return await self._http_client.get(path, params=params)

    async def _post(self, path: str, json: dict[str, Any] | None = None) -> Any:
        """Make async POST request."""
        return await self._http_client.post(path, json=json)

    async def _patch(self, path: str, json: dict[str, Any] | None = None) -> Any:
        """Make async PATCH request."""
        return await self._http_client.patch(path, json=json)

    async def _delete(self, path: str) -> None:
        """Make async DELETE request."""
        await self._http_client.delete(path)

    async def close(self) -> None:
        """Close HTTP connections."""
        await self._http_client.close()
