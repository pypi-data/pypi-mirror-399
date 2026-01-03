from __future__ import annotations

"""Main client for march-history SDK (sync version)."""

from march_history.config import ClientConfig, RetryConfig
from march_history.resources.conversations import ConversationResource
from march_history.resources.messages import MessageResource
from march_history.resources.tenants import TenantResource


class MarchHistoryClient:
    """
    Synchronous client for March Conversation History API.

    Provides access to all API resources with automatic retry logic,
    exponential backoff, and proper error handling.

    Example:
        >>> # Basic usage - no context manager needed!
        >>> client = MarchHistoryClient(base_url="http://localhost:8000")
        >>>
        >>> # Create conversation
        >>> conv = client.conversations.create(
        ...     tenant_name="acme-corp",
        ...     title="Support Chat"
        ... )
        >>>
        >>> # Add message
        >>> msg = client.messages.create(
        ...     conversation_id=conv.id,
        ...     role="user",
        ...     content="Hello!"
        ... )
        >>>
        >>> # Auto-pagination
        >>> for conversation in client.conversations.list_iter(tenant_name="acme"):
        ...     print(conversation.title)
        >>>
        >>> # Automatic cleanup - no need to call close()!

        >>> # Optional: Use context manager for explicit resource control
        >>> with MarchHistoryClient(base_url="http://localhost:8000") as client:
        ...     conv = client.conversations.create(tenant_name="acme", title="Chat")
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
        Initialize the client.

        Args:
            base_url: API base URL (default: "http://localhost:8000")
            timeout: Request timeout in seconds (default: 30.0)
            max_retries: Maximum retry attempts (default: 3)
            retry_config: Full retry configuration (overrides max_retries if provided)
            api_key: Optional API key for authentication (sent as X-API-Key header)
            custom_headers: Additional headers for all requests

        Example:
            >>> # Basic initialization
            >>> client = MarchHistoryClient()
            >>>
            >>> # With custom configuration
            >>> client = MarchHistoryClient(
            ...     base_url="https://api.example.com",
            ...     timeout=60.0,
            ...     max_retries=5
            ... )
            >>>
            >>> # With custom retry configuration
            >>> from march_history.config import RetryConfig
            >>> client = MarchHistoryClient(
            ...     retry_config=RetryConfig(
            ...         max_retries=5,
            ...         backoff_factor=2.0,
            ...         max_backoff_seconds=120.0
            ...     )
            ... )
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
        self.tenants = TenantResource(self._config)
        self.conversations = ConversationResource(self._config)
        self.messages = MessageResource(self._config)

    def close(self) -> None:
        """
        Close all HTTP connections.

        This is optional - connections are automatically closed when the
        client is garbage collected. Use this for explicit cleanup.

        Example:
            >>> client = MarchHistoryClient()
            >>> # ... use client ...
            >>> client.close()  # Explicit cleanup
        """
        self.tenants.close()
        self.conversations.close()
        self.messages.close()

    def __enter__(self) -> "MarchHistoryClient":
        """
        Enter context manager.

        Returns:
            Self for context manager usage
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        """Exit context manager and close connections."""
        self.close()

    def __del__(self) -> None:
        """Automatic cleanup when object is garbage collected."""
        self.close()
