"""Tests for Pydantic models."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from march_history.models import (
    Conversation,
    ConversationStatus,
    Message,
    MessageRole,
    Tenant,
)
from march_history.models.requests import (
    BatchMessagesRequest,
    CreateConversationRequest,
    CreateMessageRequest,
    UpdateConversationRequest,
)


class TestTenant:
    """Tests for Tenant model."""

    def test_tenant_creation(self):
        """Test creating a tenant."""
        tenant = Tenant(
            id=1,
            name="test-tenant",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert tenant.id == 1
        assert tenant.name == "test-tenant"
        assert isinstance(tenant.created_at, datetime)

    def test_tenant_from_dict(self, tenant_response):
        """Test creating tenant from API response."""
        tenant = Tenant(**tenant_response)
        assert tenant.id == 1
        assert tenant.name == "test-tenant"


class TestConversation:
    """Tests for Conversation model."""

    def test_conversation_creation(self):
        """Test creating a conversation."""
        conv = Conversation(
            id=1,
            tenant_id=1,
            user_id="user-123",
            title="Test",
            status=ConversationStatus.ACTIVE,
            metadata={"key": "value"},
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert conv.id == 1
        assert conv.user_id == "user-123"
        assert conv.status == ConversationStatus.ACTIVE
        assert conv.metadata == {"key": "value"}

    def test_conversation_status_enum(self):
        """Test conversation status enum."""
        assert ConversationStatus.ACTIVE == "active"
        assert ConversationStatus.ARCHIVED == "archived"

    def test_conversation_from_dict(self, conversation_response):
        """Test creating conversation from API response."""
        conv = Conversation(**conversation_response)
        assert conv.id == 1
        assert conv.user_id == "user-123"
        assert conv.title == "Test Conversation"
        assert conv.status == ConversationStatus.ACTIVE

    def test_conversation_optional_fields(self):
        """Test conversation with optional fields."""
        conv = Conversation(
            id=1,
            tenant_id=1,
            user_id="user-456",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert conv.user_id == "user-456"
        assert conv.title is None
        assert conv.agent_identifier is None
        assert conv.metadata == {}


class TestMessage:
    """Tests for Message model."""

    def test_message_creation(self):
        """Test creating a message."""
        msg = Message(
            id=1,
            conversation_id=1,
            sequence_number=0,
            role=MessageRole.USER,
            content="Hello",
            metadata={},
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert msg.id == 1
        assert msg.role == MessageRole.USER
        assert msg.content == "Hello"

    def test_message_role_enum(self):
        """Test message role enum."""
        assert MessageRole.USER == "user"
        assert MessageRole.ASSISTANT == "assistant"
        assert MessageRole.SYSTEM == "system"

    def test_message_from_dict(self, message_response):
        """Test creating message from API response."""
        msg = Message(**message_response)
        assert msg.id == 1
        assert msg.conversation_id == 1
        assert msg.sequence_number == 0
        assert msg.role == MessageRole.USER


class TestRequestModels:
    """Tests for request body models."""

    def test_create_conversation_request(self):
        """Test conversation creation request."""
        req = CreateConversationRequest(
            tenant_name="test-tenant",
            user_id="user-123",
            title="Test",
            agent_identifier="agent-1",
            status=ConversationStatus.ACTIVE,
            metadata={"key": "value"},
        )
        assert req.tenant_name == "test-tenant"
        assert req.user_id == "user-123"
        assert req.title == "Test"
        assert req.metadata == {"key": "value"}

    def test_create_conversation_request_validation(self):
        """Test validation of conversation request."""
        with pytest.raises(ValidationError) as exc:
            CreateConversationRequest(
                tenant_name="",  # Too short
                user_id="user-123",
                title="Test",
            )
        assert "tenant_name" in str(exc.value)

    def test_create_conversation_request_title_too_long(self):
        """Test title length validation."""
        with pytest.raises(ValidationError):
            CreateConversationRequest(
                tenant_name="test",
                user_id="user-123",
                title="x" * 501,  # Too long
            )

    def test_update_conversation_request(self):
        """Test conversation update request."""
        req = UpdateConversationRequest(
            title="Updated",
            status=ConversationStatus.ARCHIVED,
            metadata={"new": "data"},
        )
        assert req.title == "Updated"
        assert req.status == ConversationStatus.ARCHIVED

    def test_create_message_request(self):
        """Test message creation request."""
        req = CreateMessageRequest(
            role=MessageRole.USER,
            content="Hello",
            sequence_number=0,
            metadata={"user_id": "123"},
        )
        assert req.role == MessageRole.USER
        assert req.content == "Hello"
        assert req.sequence_number == 0

    def test_create_message_request_validation(self):
        """Test message validation."""
        with pytest.raises(ValidationError):
            CreateMessageRequest(
                role=MessageRole.USER,
                content="",  # Empty content
            )

    def test_batch_messages_request(self):
        """Test batch messages request."""
        req = BatchMessagesRequest(
            messages=[
                CreateMessageRequest(role=MessageRole.USER, content="Hello"),
                CreateMessageRequest(role=MessageRole.ASSISTANT, content="Hi"),
            ]
        )
        assert len(req.messages) == 2
        assert req.messages[0].role == MessageRole.USER

    def test_batch_messages_empty_validation(self):
        """Test batch messages requires at least one message."""
        with pytest.raises(ValidationError):
            BatchMessagesRequest(messages=[])

    def test_model_dump_exclude_none(self):
        """Test that model_dump excludes None values."""
        req = CreateConversationRequest(
            tenant_name="test",
            user_id="user-123",
            title=None,  # Optional field
        )
        dumped = req.model_dump(exclude_none=True)
        assert "title" not in dumped
        assert dumped["tenant_name"] == "test"
        assert dumped["user_id"] == "user-123"
