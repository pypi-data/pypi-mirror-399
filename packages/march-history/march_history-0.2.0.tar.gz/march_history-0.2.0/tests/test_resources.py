"""Tests for resource classes."""

import pytest
import respx
from httpx import Response

from march_history.models import ConversationStatus, MessageRole


class TestTenantResource:
    """Test tenant resource operations."""

    @respx.mock
    def test_list_tenants(self, client, base_url, tenant_response):
        """Test listing tenants."""
        respx.get(f"{base_url}/tenants/").mock(
            return_value=Response(200, json=[tenant_response])
        )

        tenants = client.tenants.list()

        assert len(tenants) == 1
        assert tenants[0].id == 1
        assert tenants[0].name == "test-tenant"

    @respx.mock
    def test_list_tenants_with_pagination(self, client, base_url, tenant_response):
        """Test listing tenants with pagination params."""
        route = respx.get(f"{base_url}/tenants/").mock(
            return_value=Response(200, json=[tenant_response])
        )

        client.tenants.list(offset=10, limit=5)

        request = route.calls.last.request
        assert "offset=10" in str(request.url)
        assert "limit=5" in str(request.url)

    @respx.mock
    def test_get_tenant_by_id(self, client, base_url, tenant_response):
        """Test getting tenant by ID."""
        respx.get(f"{base_url}/tenants/1").mock(
            return_value=Response(200, json=tenant_response)
        )

        tenant = client.tenants.get(1)

        assert tenant.id == 1
        assert tenant.name == "test-tenant"

    @respx.mock
    def test_get_tenant_by_name(self, client, base_url, tenant_response):
        """Test getting tenant by name."""
        respx.get(f"{base_url}/tenants/by-name/test-tenant").mock(
            return_value=Response(200, json=tenant_response)
        )

        tenant = client.tenants.get_by_name("test-tenant")

        assert tenant.id == 1
        assert tenant.name == "test-tenant"


class TestConversationResource:
    """Test conversation resource operations."""

    @respx.mock
    def test_create_conversation(self, client, base_url, conversation_response):
        """Test creating a conversation."""
        route = respx.post(f"{base_url}/conversations/").mock(
            return_value=Response(201, json=conversation_response)
        )

        conv = client.conversations.create(
            tenant_name="test-tenant",
            user_id="user-123",
            title="Test Conversation",
            metadata={"key": "value"},
        )

        assert conv.id == 1
        assert conv.title == "Test Conversation"
        assert conv.status == ConversationStatus.ACTIVE

        # Verify request body
        request_body = route.calls.last.request.content
        assert b"test-tenant" in request_body
        assert b"Test Conversation" in request_body

    @respx.mock
    def test_list_conversations(self, client, base_url, conversation_response):
        """Test listing conversations."""
        respx.get(f"{base_url}/conversations/").mock(
            return_value=Response(200, json=[conversation_response])
        )

        convs = client.conversations.list()

        assert len(convs) == 1
        assert convs[0].id == 1

    @respx.mock
    def test_list_conversations_with_filters(self, client, base_url):
        """Test listing conversations with filters."""
        route = respx.get(f"{base_url}/conversations/").mock(
            return_value=Response(200, json=[])
        )

        client.conversations.list(
            tenant_name="test-tenant",
            status=ConversationStatus.ACTIVE,
            offset=5,
            limit=10,
        )

        request = route.calls.last.request
        assert "tenant_name=test-tenant" in str(request.url)
        assert "status=active" in str(request.url)
        assert "offset=5" in str(request.url)
        assert "limit=10" in str(request.url)

    @respx.mock
    def test_get_conversation(self, client, base_url, conversation_response):
        """Test getting a conversation."""
        respx.get(f"{base_url}/conversations/1").mock(
            return_value=Response(200, json=conversation_response)
        )

        conv = client.conversations.get(1)

        assert conv.id == 1
        assert conv.title == "Test Conversation"

    @respx.mock
    def test_get_conversation_with_messages(self, client, base_url, conversation_response, message_response):
        """Test getting conversation with messages included."""
        response_with_messages = {
            **conversation_response,
            "messages": [message_response],
        }

        route = respx.get(f"{base_url}/conversations/1").mock(
            return_value=Response(200, json=response_with_messages)
        )

        conv = client.conversations.get(1, include_messages=True)

        assert conv.id == 1
        assert conv.messages is not None
        assert len(conv.messages) == 1

        # Verify query parameter
        request = route.calls.last.request
        assert "include_messages=true" in str(request.url).lower()

    @respx.mock
    def test_update_conversation(self, client, base_url, conversation_response):
        """Test updating a conversation."""
        updated_response = {
            **conversation_response,
            "title": "Updated Title",
            "status": "archived",
        }

        route = respx.patch(f"{base_url}/conversations/1").mock(
            return_value=Response(200, json=updated_response)
        )

        conv = client.conversations.update(
            1,
            title="Updated Title",
            status=ConversationStatus.ARCHIVED,
        )

        assert conv.title == "Updated Title"
        assert conv.status == ConversationStatus.ARCHIVED

    @respx.mock
    def test_archive_conversation(self, client, base_url, conversation_response):
        """Test archiving a conversation."""
        archived_response = {
            **conversation_response,
            "status": "archived",
        }

        respx.post(f"{base_url}/conversations/1/archive").mock(
            return_value=Response(200, json=archived_response)
        )

        conv = client.conversations.archive(1)

        assert conv.status == ConversationStatus.ARCHIVED

    @respx.mock
    def test_unarchive_conversation(self, client, base_url, conversation_response):
        """Test unarchiving a conversation."""
        respx.post(f"{base_url}/conversations/1/unarchive").mock(
            return_value=Response(200, json=conversation_response)
        )

        conv = client.conversations.unarchive(1)

        assert conv.status == ConversationStatus.ACTIVE

    @respx.mock
    def test_delete_conversation(self, client, base_url):
        """Test deleting a conversation."""
        route = respx.delete(f"{base_url}/conversations/1").mock(
            return_value=Response(204)
        )

        client.conversations.delete(1)

        assert route.called

    @respx.mock
    def test_search_conversations(self, client, base_url, conversation_response):
        """Test searching conversations."""
        route = respx.get(f"{base_url}/conversations/search").mock(
            return_value=Response(200, json=[conversation_response])
        )

        results = client.conversations.search(
            q="test",
            tenant_name="test-tenant",
            status=ConversationStatus.ACTIVE,
        )

        assert len(results) == 1

        request = route.calls.last.request
        assert "q=test" in str(request.url)
        assert "tenant_name=test-tenant" in str(request.url)


class TestMessageResource:
    """Test message resource operations."""

    @respx.mock
    def test_create_message(self, client, base_url, message_response):
        """Test creating a message."""
        route = respx.post(f"{base_url}/conversations/1/messages").mock(
            return_value=Response(201, json=message_response)
        )

        msg = client.messages.create(
            conversation_id=1,
            role=MessageRole.USER,
            content="Test message",
            metadata={"user_id": "123"},
        )

        assert msg.id == 1
        assert msg.content == "Test message"
        assert msg.role == MessageRole.USER

    @respx.mock
    def test_create_batch_messages(self, client, base_url, message_response):
        """Test creating batch messages."""
        batch_response = [
            {**message_response, "id": 1, "sequence_number": 0},
            {**message_response, "id": 2, "sequence_number": 1, "role": "assistant"},
        ]

        respx.post(f"{base_url}/conversations/1/messages/batch").mock(
            return_value=Response(201, json=batch_response)
        )

        msgs = client.messages.create_batch(
            conversation_id=1,
            messages=[
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi"},
            ],
        )

        assert len(msgs) == 2
        assert msgs[0].sequence_number == 0
        assert msgs[1].sequence_number == 1

    @respx.mock
    def test_list_messages(self, client, base_url, message_response):
        """Test listing messages."""
        respx.get(f"{base_url}/conversations/1/messages").mock(
            return_value=Response(200, json=[message_response])
        )

        msgs = client.messages.list(conversation_id=1)

        assert len(msgs) == 1
        assert msgs[0].id == 1

    @respx.mock
    def test_list_messages_with_role_filter(self, client, base_url):
        """Test listing messages with role filter."""
        route = respx.get(f"{base_url}/conversations/1/messages").mock(
            return_value=Response(200, json=[])
        )

        client.messages.list(conversation_id=1, role=MessageRole.USER)

        request = route.calls.last.request
        assert "role=user" in str(request.url)

    @respx.mock
    def test_get_message(self, client, base_url, message_response):
        """Test getting a message by ID."""
        respx.get(f"{base_url}/messages/1").mock(
            return_value=Response(200, json=message_response)
        )

        msg = client.messages.get(1)

        assert msg.id == 1
        assert msg.content == "Test message"

    @respx.mock
    def test_search_messages(self, client, base_url, message_response):
        """Test searching messages in a conversation."""
        route = respx.get(f"{base_url}/conversations/1/messages/search").mock(
            return_value=Response(200, json=[message_response])
        )

        results = client.messages.search(conversation_id=1, q="test")

        assert len(results) == 1

        request = route.calls.last.request
        assert "q=test" in str(request.url)

    @respx.mock
    def test_search_messages_global(self, client, base_url, message_response):
        """Test searching messages globally."""
        route = respx.get(f"{base_url}/messages/search").mock(
            return_value=Response(200, json=[message_response])
        )

        results = client.messages.search_global(
            q="test",
            role=MessageRole.USER,
        )

        assert len(results) == 1

        request = route.calls.last.request
        assert "q=test" in str(request.url)
        assert "role=user" in str(request.url)
