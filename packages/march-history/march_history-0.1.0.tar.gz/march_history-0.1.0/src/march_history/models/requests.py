from __future__ import annotations

"""Request body models for march-history SDK."""

from typing import Any

from pydantic import Field

from march_history.models.common import BaseAPIModel
from march_history.models.conversation import ConversationStatus
from march_history.models.message import MessageRole


class CreateConversationRequest(BaseAPIModel):
    """
    Request body for creating a new conversation.

    Attributes:
        tenant_name: Tenant name (auto-creates tenant if not exists)
        title: Conversation title or summary
        agent_identifier: Identifier for the AI agent
        status: Conversation status (active or archived)
        metadata: Additional metadata
    """

    tenant_name: str = Field(min_length=1, max_length=255)
    title: str | None = Field(None, max_length=500)
    agent_identifier: str | None = Field(None, max_length=255)
    status: ConversationStatus = ConversationStatus.ACTIVE
    metadata: dict[str, Any] = {}


class UpdateConversationRequest(BaseAPIModel):
    """
    Request body for updating a conversation.

    All fields are optional for partial updates.

    Attributes:
        title: New conversation title
        status: New conversation status
        metadata: New metadata (replaces entire metadata field)
    """

    title: str | None = Field(None, max_length=500)
    status: ConversationStatus | None = None
    metadata: dict[str, Any] | None = None


class CreateMessageRequest(BaseAPIModel):
    """
    Request body for creating a single message.

    Attributes:
        role: Message role (user, assistant, or system)
        content: Message content/text
        sequence_number: Order in conversation (auto-generated if not provided)
        metadata: Additional metadata
    """

    role: MessageRole
    content: str = Field(min_length=1)
    sequence_number: int | None = Field(None, ge=0)
    metadata: dict[str, Any] = {}


class BatchMessagesRequest(BaseAPIModel):
    """
    Request body for creating multiple messages atomically.

    Attributes:
        messages: List of messages to create
    """

    messages: list[CreateMessageRequest] = Field(min_length=1)
