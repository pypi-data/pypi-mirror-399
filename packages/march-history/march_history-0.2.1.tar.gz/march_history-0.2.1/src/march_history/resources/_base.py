from __future__ import annotations

"""Base resource class for march-history SDK."""

from typing import Any

from march_history._base_client import BaseHTTPClient
from march_history.config import ClientConfig


class BaseResource:
    """
    Base class for all resource classes.

    Provides common HTTP methods and client management for API resources.
    """

    def __init__(self, config: ClientConfig) -> None:
        """
        Initialize resource.

        Args:
            config: Client configuration
        """
        self._config = config
        self._http_client = BaseHTTPClient(config)

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """
        Make GET request.

        Args:
            path: URL path
            params: Query parameters

        Returns:
            Response data
        """
        return self._http_client.get(path, params=params)

    def _post(self, path: str, json: dict[str, Any] | None = None) -> Any:
        """
        Make POST request.

        Args:
            path: URL path
            json: JSON request body

        Returns:
            Response data
        """
        return self._http_client.post(path, json=json)

    def _patch(self, path: str, json: dict[str, Any] | None = None) -> Any:
        """
        Make PATCH request.

        Args:
            path: URL path
            json: JSON request body

        Returns:
            Response data
        """
        return self._http_client.patch(path, json=json)

    def _delete(self, path: str) -> None:
        """
        Make DELETE request.

        Args:
            path: URL path
        """
        self._http_client.delete(path)

    def close(self) -> None:
        """Close HTTP connections."""
        self._http_client.close()
