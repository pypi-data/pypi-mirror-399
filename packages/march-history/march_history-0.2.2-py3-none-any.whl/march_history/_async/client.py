from __future__ import annotations

"""Async client for march-history SDK."""

from march_history._async.resources import (
    AsyncConversationResource,
    AsyncMessageResource,
    AsyncTenantResource,
)
from march_history.config import ClientConfig, RetryConfig


class AsyncMarchHistoryClient:
    """
    Asynchronous client for March Conversation History API.

    Provides the same API as MarchHistoryClient but with async/await support.

    Example:
        >>> import asyncio
        >>> from march_history import AsyncMarchHistoryClient
        >>>
        >>> async def main():
        ...     # No context manager needed - automatic cleanup!
        ...     client = AsyncMarchHistoryClient(base_url="http://localhost:8000")
        ...
        ...     # Create conversation
        ...     conv = await client.conversations.create(
        ...         tenant_name="acme-corp",
        ...         user_id="user-123",
        ...         title="Async Chat"
        ...     )
        ...
        ...     # Add message
        ...     msg = await client.messages.create(
        ...         conversation_id=conv.id,
        ...         role="user",
        ...         content="Hello async world!"
        ...     )
        ...
        ...     # Auto-pagination with async for
        ...     async for conversation in client.conversations.list_iter(
        ...         tenant_name="acme"
        ...     ):
        ...         print(conversation.title)
        ...
        ...     # Automatic cleanup!
        ...
        >>> asyncio.run(main())

        >>> # Optional: Use async context manager for explicit control
        >>> async def with_context():
        ...     async with AsyncMarchHistoryClient(
        ...         base_url="http://localhost:8000"
        ...     ) as client:
        ...         conv = await client.conversations.create(
        ...             tenant_name="acme",
        ...             user_id="user-123",
        ...             title="Chat"
        ...         )
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        *,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_config: RetryConfig | None = None,
        api_key: str | None = None,
        custom_headers: dict[str, str] | None = None,
    ) -> None:
        """
        Initialize the async client.

        Args:
            base_url: API base URL (default: "http://localhost:8000")
            timeout: Request timeout in seconds (default: 30.0)
            max_retries: Maximum retry attempts (default: 3)
            retry_config: Full retry configuration (overrides max_retries)
            api_key: Optional API key for authentication (sent as X-API-Key)
            custom_headers: Additional headers for all requests
        """
        if retry_config is None:
            retry_config = RetryConfig(max_retries=max_retries)

        self._config = ClientConfig(
            base_url=base_url,
            timeout=timeout,
            retry_config=retry_config,
            api_key=api_key,
            custom_headers=custom_headers,
        )

        # Initialize resource instances
        self.tenants = AsyncTenantResource(self._config)
        self.conversations = AsyncConversationResource(self._config)
        self.messages = AsyncMessageResource(self._config)

    async def close(self) -> None:
        """Close all HTTP connections."""
        await self.tenants.close()
        await self.conversations.close()
        await self.messages.close()

    async def __aenter__(self) -> "AsyncMarchHistoryClient":
        """Enter async context manager."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        """Exit async context manager and close connections."""
        await self.close()

    def __del__(self) -> None:
        """Automatic cleanup when object is garbage collected."""
        # Note: Cannot await in __del__, handled by resource cleanup
        pass
