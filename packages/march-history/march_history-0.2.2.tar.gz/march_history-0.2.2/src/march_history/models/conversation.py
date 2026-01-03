from __future__ import annotations

"""Conversation model for march-history SDK."""

from enum import Enum
from typing import TYPE_CHECKING, Any

from march_history.models.common import TimestampedModel

if TYPE_CHECKING:
    from march_history.models.message import Message


class ConversationStatus(str, Enum):
    """Status of a conversation."""

    ACTIVE = "active"
    ARCHIVED = "archived"


class Conversation(TimestampedModel):
    """
    Represents a conversation between a user and an AI agent.

    Conversations contain messages and support metadata for custom fields.

    Attributes:
        id: Unique conversation identifier
        tenant_id: ID of the tenant this conversation belongs to
        user_id: User identifier within the tenant
        agent_identifier: Identifier for the AI agent handling this conversation
        title: Conversation title or summary
        status: Conversation status (active or archived)
        metadata: Additional metadata for custom fields
        messages: List of messages (only when include_messages=true)
        created_at: Timestamp when conversation was created
        updated_at: Timestamp when conversation was last updated
    """

    id: int
    tenant_id: int
    user_id: str
    agent_identifier: str | None = None
    title: str | None = None
    status: ConversationStatus = ConversationStatus.ACTIVE
    metadata: dict[str, Any] = {}
    messages: list["Message"] | None = None
