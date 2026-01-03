from __future__ import annotations

"""
March Conversation History SDK.

A Python SDK for the March AI Conversation History API with full type safety,
automatic retries, and pagination support.

Example:
    >>> from march_history import MarchHistoryClient
    >>> from march_history.models import MessageRole, ConversationStatus
    >>>
    >>> # Create client - automatic cleanup, no context manager needed!
    >>> client = MarchHistoryClient(base_url="http://localhost:8000")
    >>>
    >>> # Create conversation
    >>> conv = client.conversations.create(
    ...     tenant_name="acme-corp",
    ...     title="Support Chat",
    ...     metadata={"user_id": "user-123"}
    ... )
    >>>
    >>> # Add messages
    >>> msg = client.messages.create(
    ...     conversation_id=conv.id,
    ...     role=MessageRole.USER,
    ...     content="Hello!"
    ... )
    >>>
    >>> # Auto-pagination
    >>> for conversation in client.conversations.list_iter(tenant_name="acme"):
    ...     print(conversation.title)
"""

from march_history._async.client import AsyncMarchHistoryClient
from march_history._version import __version__
from march_history.client import MarchHistoryClient
from march_history.config import ClientConfig, RetryConfig
from march_history.exceptions import (
    APIError,
    BadRequestError,
    ConflictError,
    ConfigurationError,
    MarchHistoryError,
    NetworkError,
    NotFoundError,
    RetryError,
    ServerError,
    ValidationError,
)
from march_history.models import (
    Conversation,
    ConversationStatus,
    Message,
    MessageRole,
    Tenant,
)

__all__ = [
    # Version
    "__version__",
    # Clients
    "MarchHistoryClient",
    "AsyncMarchHistoryClient",
    # Configuration
    "ClientConfig",
    "RetryConfig",
    # Models
    "Tenant",
    "Conversation",
    "ConversationStatus",
    "Message",
    "MessageRole",
    # Exceptions
    "MarchHistoryError",
    "APIError",
    "ValidationError",
    "NotFoundError",
    "ConflictError",
    "BadRequestError",
    "ServerError",
    "NetworkError",
    "ConfigurationError",
    "RetryError",
]
