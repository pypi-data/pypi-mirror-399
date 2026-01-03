from __future__ import annotations

"""Async client for march-history SDK.

Note: This implementation uses placeholder resources. To complete the async implementation,
copy the sync resource files from src/march_history/resources/ and:
1. Change class names: TenantResource -> AsyncTenantResource
2. Change base class: BaseResource -> AsyncBaseResource
3. Add 'async' to all method definitions
4. Add 'await' to all HTTP calls (_get, _post, _patch, _delete)
5. Change SyncPaginator to AsyncPaginator in list_iter methods
6. Update imports to use async versions
"""

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
        ...     async for conversation in client.conversations.list_iter(tenant_name="acme"):
        ...         print(conversation.title)
        ...
        ...     # Automatic cleanup!
        ...
        >>> asyncio.run(main())

        >>> # Optional: Use async context manager for explicit control
        >>> async def with_context():
        ...     async with AsyncMarchHistoryClient(base_url="http://localhost:8000") as client:
        ...         conv = await client.conversations.create(tenant_name="acme", title="Chat")
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        *,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_config: RetryConfig | None = None,
        custom_headers: dict[str, str] | None = None,
    ) -> None:
        """
        Initialize the async client.

        Args:
            base_url: API base URL (default: "http://localhost:8000")
            timeout: Request timeout in seconds (default: 30.0)
            max_retries: Maximum retry attempts (default: 3)
            retry_config: Full retry configuration (overrides max_retries if provided)
            custom_headers: Additional headers for all requests
        """
        if retry_config is None:
            retry_config = RetryConfig(max_retries=max_retries)

        self._config = ClientConfig(
            base_url=base_url,
            timeout=timeout,
            retry_config=retry_config,
            custom_headers=custom_headers,
        )

        # Note: To complete async implementation, import and instantiate async resources here
        # from march_history._async.resources import AsyncTenantResource, etc.
        # self.tenants = AsyncTenantResource(self._config)
        # self.conversations = AsyncConversationResource(self._config)
        # self.messages = AsyncMessageResource(self._config)

        raise NotImplementedError(
            "Async resources not yet fully implemented. "
            "See docstring in client.py for implementation instructions. "
            "For now, use the sync client (MarchHistoryClient) which is fully functional."
        )

    async def close(self) -> None:
        """Close all HTTP connections."""
        # await self.tenants.close()
        # await self.conversations.close()
        # await self.messages.close()
        pass

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
