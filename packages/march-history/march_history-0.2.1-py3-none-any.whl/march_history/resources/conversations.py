"""Conversation resource for march-history SDK."""

from __future__ import annotations

from collections.abc import Iterator

from march_history.models.conversation import Conversation, ConversationStatus
from march_history.models.requests import (
    CreateConversationRequest,
    UpdateConversationRequest,
)
from march_history.pagination import SyncPaginator
from march_history.resources._base import BaseResource


class ConversationResource(BaseResource):
    """
    Conversation management resource.

    Provides methods for creating, reading, updating, and deleting conversations.
    """

    def create(
        self,
        tenant_name: str,
        user_id: str,
        title: str | None = None,
        agent_identifier: str | None = None,
        status: ConversationStatus = ConversationStatus.ACTIVE,
        metadata: dict | None = None,
    ) -> Conversation:
        """
        Create a new conversation.

        The tenant is automatically created if it doesn't exist.

        Args:
            tenant_name: Tenant name (auto-creates if not exists)
            user_id: User identifier within the tenant
            title: Conversation title or summary
            agent_identifier: Identifier for the AI agent
            status: Conversation status (active or archived)
            metadata: Additional metadata

        Returns:
            Created conversation

        Raises:
            ValidationError: If validation fails

        Example:
            >>> conv = client.conversations.create(
            ...     tenant_name="acme-corp",
            ...     user_id="user-123",
            ...     title="Support Chat",
            ...     metadata={"session_id": "sess-456"}
            ... )
        """
        request = CreateConversationRequest(
            tenant_name=tenant_name,
            user_id=user_id,
            title=title,
            agent_identifier=agent_identifier,
            status=status,
            metadata=metadata or {},
        )

        data = self._post("/conversations/", json=request.model_dump(exclude_none=True))
        return Conversation(**data)

    def list(
        self,
        tenant_name: str | None = None,
        tenant_id: int | None = None,
        user_id: str | None = None,
        agent_identifier: str | None = None,
        status: ConversationStatus | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Conversation]:
        """
        List conversations with optional filtering.

        Args:
            tenant_name: Filter by tenant name
            tenant_id: Filter by tenant ID
            user_id: Filter by user ID
            agent_identifier: Filter by agent identifier
            status: Filter by status (active or archived)
            offset: Number of items to skip (default: 0)
            limit: Number of items to return (default: 100, max: 1000)

        Returns:
            List of conversations

        Example:
            >>> conversations = client.conversations.list(
            ...     tenant_name="acme-corp",
            ...     status=ConversationStatus.ACTIVE
            ... )
        """
        params = {"offset": offset, "limit": limit}
        if tenant_name:
            params["tenant_name"] = tenant_name
        if tenant_id:
            params["tenant_id"] = tenant_id
        if user_id:
            params["user_id"] = user_id
        if agent_identifier:
            params["agent_identifier"] = agent_identifier
        if status:
            params["status"] = status.value

        data = self._get("/conversations/", params=params)
        return [Conversation(**item) for item in data]

    def list_iter(
        self,
        tenant_name: str | None = None,
        tenant_id: int | None = None,
        user_id: str | None = None,
        agent_identifier: str | None = None,
        status: ConversationStatus | None = None,
        page_size: int = 100,
        max_items: int | None = None,
    ) -> Iterator[Conversation]:
        """
        Iterate over all conversations with auto-pagination.

        Args:
            tenant_name: Filter by tenant name
            tenant_id: Filter by tenant ID
            user_id: Filter by user ID
            agent_identifier: Filter by agent identifier
            status: Filter by status (active or archived)
            page_size: Number of items per page (default: 100)
            max_items: Maximum total items to fetch (default: unlimited)

        Returns:
            Iterator yielding conversations

        Example:
            >>> for conv in client.conversations.list_iter(tenant_name="acme"):
            ...     print(conv.title)
        """

        def fetch_page(offset: int, limit: int) -> list[Conversation]:
            return self.list(
                tenant_name=tenant_name,
                tenant_id=tenant_id,
                user_id=user_id,
                agent_identifier=agent_identifier,
                status=status,
                offset=offset,
                limit=limit,
            )

        return SyncPaginator(fetch_page, page_size, max_items)

    def get(
        self,
        conversation_id: int,
        include_messages: bool = False,
    ) -> Conversation:
        """
        Get a conversation by ID.

        Args:
            conversation_id: Conversation ID
            include_messages: Include messages in response (default: False)

        Returns:
            Conversation object

        Raises:
            NotFoundError: If conversation not found
            ValidationError: If conversation_id is invalid

        Example:
            >>> conv = client.conversations.get(1, include_messages=True)
            >>> print(f"Messages: {len(conv.messages or [])}")
        """
        params = {"include_messages": include_messages}
        data = self._get(f"/conversations/{conversation_id}", params=params)
        return Conversation(**data)

    def update(
        self,
        conversation_id: int,
        user_id: str | None = None,
        title: str | None = None,
        status: ConversationStatus | None = None,
        metadata: dict | None = None,
    ) -> Conversation:
        """
        Update a conversation.

        All fields are optional for partial updates.

        Args:
            conversation_id: Conversation ID
            user_id: New user identifier
            title: New conversation title
            status: New conversation status
            metadata: New metadata (replaces entire metadata field)

        Returns:
            Updated conversation

        Raises:
            NotFoundError: If conversation not found
            ValidationError: If validation fails

        Example:
            >>> conv = client.conversations.update(
            ...     1,
            ...     title="Updated Title",
            ...     status=ConversationStatus.ARCHIVED
            ... )
        """
        request = UpdateConversationRequest(
            user_id=user_id,
            title=title,
            status=status,
            metadata=metadata,
        )

        data = self._patch(
            f"/conversations/{conversation_id}",
            json=request.model_dump(exclude_none=True),
        )
        return Conversation(**data)

    def archive(self, conversation_id: int) -> Conversation:
        """
        Archive a conversation.

        Sets status to 'archived'.

        Args:
            conversation_id: Conversation ID

        Returns:
            Archived conversation

        Raises:
            NotFoundError: If conversation not found

        Example:
            >>> conv = client.conversations.archive(1)
            >>> assert conv.status == ConversationStatus.ARCHIVED
        """
        data = self._post(f"/conversations/{conversation_id}/archive")
        return Conversation(**data)

    def unarchive(self, conversation_id: int) -> Conversation:
        """
        Unarchive a conversation.

        Sets status to 'active'.

        Args:
            conversation_id: Conversation ID

        Returns:
            Unarchived conversation

        Raises:
            NotFoundError: If conversation not found

        Example:
            >>> conv = client.conversations.unarchive(1)
            >>> assert conv.status == ConversationStatus.ACTIVE
        """
        data = self._post(f"/conversations/{conversation_id}/unarchive")
        return Conversation(**data)

    def delete(self, conversation_id: int) -> None:
        """
        Delete a conversation and all its messages.

        This is a permanent operation and cannot be undone.

        Args:
            conversation_id: Conversation ID

        Raises:
            NotFoundError: If conversation not found

        Example:
            >>> client.conversations.delete(1)
        """
        self._delete(f"/conversations/{conversation_id}")

    def search(
        self,
        q: str | None = None,
        metadata_key: str | None = None,
        metadata_value: str | None = None,
        tenant_name: str | None = None,
        tenant_id: int | None = None,
        user_id: str | None = None,
        agent_identifier: str | None = None,
        status: ConversationStatus | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Conversation]:
        """
        Search conversations by title or metadata.

        Args:
            q: Search query for title (case-insensitive partial match)
            metadata_key: Metadata key to search
            metadata_value: Metadata value to match (requires metadata_key)
            tenant_name: Filter by tenant name
            tenant_id: Filter by tenant ID
            user_id: Filter by user ID
            agent_identifier: Filter by agent identifier
            status: Filter by status (active or archived)
            offset: Number of items to skip (default: 0)
            limit: Number of items to return (default: 100, max: 1000)

        Returns:
            List of matching conversations

        Example:
            >>> # Search by title
            >>> results = client.conversations.search(q="support")
            >>>
            >>> # Search by metadata
            >>> results = client.conversations.search(
            ...     metadata_key="environment",
            ...     metadata_value="production"
            ... )
        """
        params = {"offset": offset, "limit": limit}
        if q:
            params["q"] = q
        if metadata_key:
            params["metadata_key"] = metadata_key
        if metadata_value:
            params["metadata_value"] = metadata_value
        if tenant_name:
            params["tenant_name"] = tenant_name
        if tenant_id:
            params["tenant_id"] = tenant_id
        if user_id:
            params["user_id"] = user_id
        if agent_identifier:
            params["agent_identifier"] = agent_identifier
        if status:
            params["status"] = status.value

        data = self._get("/conversations/search", params=params)
        return [Conversation(**item) for item in data]

    def search_iter(
        self,
        q: str | None = None,
        metadata_key: str | None = None,
        metadata_value: str | None = None,
        tenant_name: str | None = None,
        tenant_id: int | None = None,
        user_id: str | None = None,
        agent_identifier: str | None = None,
        status: ConversationStatus | None = None,
        page_size: int = 100,
        max_items: int | None = None,
    ) -> Iterator[Conversation]:
        """
        Search conversations with auto-pagination.

        Args:
            q: Search query for title
            metadata_key: Metadata key to search
            metadata_value: Metadata value to match
            tenant_name: Filter by tenant name
            tenant_id: Filter by tenant ID
            user_id: Filter by user ID
            agent_identifier: Filter by agent identifier
            status: Filter by status
            page_size: Number of items per page (default: 100)
            max_items: Maximum total items to fetch (default: unlimited)

        Returns:
            Iterator yielding matching conversations

        Example:
            >>> for conv in client.conversations.search_iter(q="support"):
            ...     print(conv.title)
        """

        def fetch_page(offset: int, limit: int) -> list[Conversation]:
            return self.search(
                q=q,
                metadata_key=metadata_key,
                metadata_value=metadata_value,
                tenant_name=tenant_name,
                tenant_id=tenant_id,
                user_id=user_id,
                agent_identifier=agent_identifier,
                status=status,
                offset=offset,
                limit=limit,
            )

        return SyncPaginator(fetch_page, page_size, max_items)
