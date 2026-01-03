from __future__ import annotations

"""Pydantic models for march-history SDK."""

from march_history.models.common import BaseAPIModel, TimestampedModel
from march_history.models.conversation import Conversation, ConversationStatus
from march_history.models.message import Message, MessageRole
from march_history.models.requests import (
    BatchMessagesRequest,
    CreateConversationRequest,
    CreateMessageRequest,
    UpdateConversationRequest,
)
from march_history.models.tenant import Tenant

# Rebuild Conversation model to resolve forward references
Conversation.model_rebuild()

__all__ = [
    # Base models
    "BaseAPIModel",
    "TimestampedModel",
    # Domain models
    "Tenant",
    "Conversation",
    "ConversationStatus",
    "Message",
    "MessageRole",
    # Request models
    "CreateConversationRequest",
    "UpdateConversationRequest",
    "CreateMessageRequest",
    "BatchMessagesRequest",
]
