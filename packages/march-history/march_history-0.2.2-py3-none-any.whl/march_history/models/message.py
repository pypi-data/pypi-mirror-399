from __future__ import annotations

"""Message model for march-history SDK."""

from enum import Enum
from typing import Any

from march_history.models.common import TimestampedModel


class MessageRole(str, Enum):
    """Role of the message sender."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(TimestampedModel):
    """
    Represents a message in a conversation.

    Messages are immutable once created and automatically sequenced within
    conversations.

    Attributes:
        id: Unique message identifier
        conversation_id: ID of the conversation this message belongs to
        sequence_number: Order of message in conversation (0-indexed)
        role: Role of the message sender (user, assistant, or system)
        content: Message content/text
        metadata: Additional metadata (tool calls, tokens, model info, etc.)
        created_at: Timestamp when message was created
        updated_at: Timestamp when message was last updated
    """

    id: int
    conversation_id: int
    sequence_number: int
    role: MessageRole
    content: str
    metadata: dict[str, Any] = {}
