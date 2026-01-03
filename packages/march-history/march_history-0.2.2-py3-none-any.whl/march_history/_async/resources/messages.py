from __future__ import annotations

"""Async message resource for march-history SDK."""

from collections.abc import AsyncIterator

from march_history._async.resources._base import AsyncBaseResource
from march_history.models.message import Message, MessageRole
from march_history.models.requests import BatchMessagesRequest, CreateMessageRequest
from march_history.pagination import AsyncPaginator


class AsyncMessageResource(AsyncBaseResource):
    """
    Async message management resource.

    Provides methods for creating and reading messages. Messages are immutable
    once created and automatically sequenced within conversations.
    """

    async def create(
        self,
        conversation_id: int,
        role: MessageRole,
        content: str,
        sequence_number: int | None = None,
        metadata: dict | None = None,
    ) -> Message:
        """
        Create a single message in a conversation.

        Sequence number is auto-generated if not provided.

        Args:
            conversation_id: Conversation ID
            role: Message role (user, assistant, or system)
            content: Message content/text
            sequence_number: Order in conversation (auto-generated if not provided)
            metadata: Additional metadata (tool calls, tokens, model info, etc.)

        Returns:
            Created message

        Raises:
            NotFoundError: If conversation not found
            ConflictError: If sequence number already exists
            ValidationError: If validation fails

        Example:
            >>> msg = await client.messages.create(
            ...     conversation_id=1,
            ...     role=MessageRole.USER,
            ...     content="Hello!",
            ...     metadata={"user_id": "user-123"}
            ... )
        """
        request = CreateMessageRequest(
            role=role,
            content=content,
            sequence_number=sequence_number,
            metadata=metadata or {},
        )

        data = await self._post(
            f"/conversations/{conversation_id}/messages",
            json=request.model_dump(exclude_none=True),
        )
        return Message(**data)

    async def create_batch(
        self,
        conversation_id: int,
        messages: list[dict],
    ) -> list[Message]:
        """
        Create multiple messages atomically in a conversation.

        All messages are created in a single transaction. Sequence numbers
        are auto-generated for messages without explicit sequence_number.

        Args:
            conversation_id: Conversation ID
            messages: List of message dictionaries with keys:
                - role: MessageRole (required)
                - content: str (required)
                - sequence_number: int (optional)
                - metadata: dict (optional)

        Returns:
            List of created messages

        Raises:
            NotFoundError: If conversation not found
            ConflictError: If duplicate sequence number
            ValidationError: If validation fails

        Example:
            >>> msgs = await client.messages.create_batch(
            ...     conversation_id=1,
            ...     messages=[
            ...         {"role": "user", "content": "Hello"},
            ...         {"role": "assistant", "content": "Hi! How can I help?"},
            ...     ]
            ... )
        """
        # Convert dict messages to CreateMessageRequest objects
        message_requests = [CreateMessageRequest(**msg) for msg in messages]
        request = BatchMessagesRequest(messages=message_requests)

        data = await self._post(
            f"/conversations/{conversation_id}/messages/batch",
            json=request.model_dump(exclude_none=True),
        )
        return [Message(**item) for item in data]

    async def list(
        self,
        conversation_id: int,
        role: MessageRole | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Message]:
        """
        List messages in a conversation.

        Messages are ordered by sequence number.

        Args:
            conversation_id: Conversation ID
            role: Filter by role (user, assistant, or system)
            offset: Number of items to skip (default: 0)
            limit: Number of items to return (default: 100, max: 1000)

        Returns:
            List of messages

        Example:
            >>> messages = await client.messages.list(
            ...     conversation_id=1,
            ...     role=MessageRole.USER
            ... )
        """
        params = {"offset": offset, "limit": limit}
        if role:
            params["role"] = role.value

        data = await self._get(f"/conversations/{conversation_id}/messages", params=params)
        return [Message(**item) for item in data]

    def list_iter(
        self,
        conversation_id: int,
        role: MessageRole | None = None,
        page_size: int = 100,
        max_items: int | None = None,
    ) -> AsyncIterator[Message]:
        """
        Iterate over messages in a conversation with auto-pagination.

        Args:
            conversation_id: Conversation ID
            role: Filter by role
            page_size: Number of items per page (default: 100)
            max_items: Maximum total items to fetch (default: unlimited)

        Returns:
            AsyncIterator yielding messages

        Example:
            >>> async for msg in client.messages.list_iter(conversation_id=1):
            ...     print(msg.content)
        """

        async def fetch_page(offset: int, limit: int) -> list[Message]:
            return await self.list(
                conversation_id=conversation_id,
                role=role,
                offset=offset,
                limit=limit,
            )

        return AsyncPaginator(fetch_page, page_size, max_items)

    async def get(self, message_id: int) -> Message:
        """
        Get a specific message by ID.

        Args:
            message_id: Message ID

        Returns:
            Message object

        Raises:
            NotFoundError: If message not found
            ValidationError: If message_id is invalid

        Example:
            >>> msg = await client.messages.get(1)
            >>> print(msg.content)
        """
        data = await self._get(f"/messages/{message_id}")
        return Message(**data)

    async def search(
        self,
        conversation_id: int,
        q: str,
        role: MessageRole | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Message]:
        """
        Search messages within a specific conversation.

        Uses PostgreSQL full-text search.

        Args:
            conversation_id: Conversation ID
            q: Search query for message content
            role: Filter by role
            offset: Number of items to skip (default: 0)
            limit: Number of items to return (default: 100, max: 1000)

        Returns:
            List of matching messages

        Raises:
            ValidationError: If search query is empty

        Example:
            >>> results = await client.messages.search(
            ...     conversation_id=1,
            ...     q="python programming"
            ... )
        """
        params = {"q": q, "offset": offset, "limit": limit}
        if role:
            params["role"] = role.value

        data = await self._get(f"/conversations/{conversation_id}/messages/search", params=params)
        return [Message(**item) for item in data]

    async def search_global(
        self,
        q: str,
        conversation_id: int | None = None,
        role: MessageRole | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Message]:
        """
        Search messages across all conversations.

        Uses PostgreSQL full-text search.

        Args:
            q: Search query for message content
            conversation_id: Filter by conversation ID
            role: Filter by role
            offset: Number of items to skip (default: 0)
            limit: Number of items to return (default: 100, max: 1000)

        Returns:
            List of matching messages

        Raises:
            ValidationError: If search query is empty

        Example:
            >>> # Search all messages
            >>> results = await client.messages.search_global(q="error")
            >>>
            >>> # Search with filters
            >>> results = await client.messages.search_global(
            ...     q="python",
            ...     role=MessageRole.ASSISTANT
            ... )
        """
        params = {"q": q, "offset": offset, "limit": limit}
        if conversation_id:
            params["conversation_id"] = conversation_id
        if role:
            params["role"] = role.value

        data = await self._get("/messages/search", params=params)
        return [Message(**item) for item in data]

    def search_global_iter(
        self,
        q: str,
        conversation_id: int | None = None,
        role: MessageRole | None = None,
        page_size: int = 100,
        max_items: int | None = None,
    ) -> AsyncIterator[Message]:
        """
        Search messages globally with auto-pagination.

        Args:
            q: Search query
            conversation_id: Filter by conversation ID
            role: Filter by role
            page_size: Number of items per page (default: 100)
            max_items: Maximum total items to fetch (default: unlimited)

        Returns:
            AsyncIterator yielding matching messages

        Example:
            >>> async for msg in client.messages.search_global_iter(q="error"):
            ...     print(f"{msg.conversation_id}: {msg.content}")
        """

        async def fetch_page(offset: int, limit: int) -> list[Message]:
            return await self.search_global(
                q=q,
                conversation_id=conversation_id,
                role=role,
                offset=offset,
                limit=limit,
            )

        return AsyncPaginator(fetch_page, page_size, max_items)
