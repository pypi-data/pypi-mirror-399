"""Basic usage example for march-history SDK."""

from march_history import MarchHistoryClient
from march_history.models import MessageRole, ConversationStatus

def main():
    """Demonstrate basic SDK usage."""

    # Initialize client - no context manager needed!
    client = MarchHistoryClient(base_url="http://localhost:8000")

    print("=== Creating Conversation ===")
    # Create a conversation
    conv = client.conversations.create(
        tenant_name="acme-corp",
        user_id="user-123",
        title="Customer Support Session",
        agent_identifier="support-bot-v1",
        metadata={
            "session_id": "sess-456",
            "source": "web_chat"
        }
    )
    print(f"Created conversation ID: {conv.id}")
    print(f"Tenant ID: {conv.tenant_id}")
    print(f"Status: {conv.status}")

    print("\n=== Adding Messages ===")
    # Add messages to the conversation
    msg1 = client.messages.create(
        conversation_id=conv.id,
        role=MessageRole.USER,
        content="Hello, I need help with my order #12345",
        metadata={"user_id": "user-123"}
    )
    print(f"Message 1 created (sequence: {msg1.sequence_number})")

    msg2 = client.messages.create(
        conversation_id=conv.id,
        role=MessageRole.ASSISTANT,
        content="I'd be happy to help you with order #12345. Let me look that up for you.",
        metadata={"model": "gpt-4", "tokens": 25}
    )
    print(f"Message 2 created (sequence: {msg2.sequence_number})")

    msg3 = client.messages.create(
        conversation_id=conv.id,
        role=MessageRole.USER,
        content="Thank you! I need to change the shipping address.",
    )
    print(f"Message 3 created (sequence: {msg3.sequence_number})")

    print("\n=== Batch Creating Messages ===")
    # Create multiple messages at once
    batch_msgs = client.messages.create_batch(
        conversation_id=conv.id,
        messages=[
            {
                "role": "assistant",
                "content": "I can help you update the shipping address. What's the new address?",
            },
            {
                "role": "user",
                "content": "123 Main St, New York, NY 10001",
            },
            {
                "role": "assistant",
                "content": "Perfect! I've updated your shipping address. Is there anything else I can help with?",
            },
        ]
    )
    print(f"Created {len(batch_msgs)} messages in batch")

    print("\n=== Listing Messages ===")
    # Get all messages in the conversation
    messages = client.messages.list(conversation_id=conv.id)
    print(f"Total messages: {len(messages)}")
    for msg in messages:
        print(f"  [{msg.sequence_number}] {msg.role}: {msg.content[:50]}...")

    print("\n=== Searching Messages ===")
    # Search for specific content
    search_results = client.messages.search(
        conversation_id=conv.id,
        q="address"
    )
    print(f"Found {len(search_results)} messages containing 'address':")
    for msg in search_results:
        print(f"  {msg.content}")

    print("\n=== Getting Conversation with Messages ===")
    # Retrieve conversation with all messages
    conv_with_msgs = client.conversations.get(
        conversation_id=conv.id,
        include_messages=True
    )
    print(f"Conversation '{conv_with_msgs.title}' has {len(conv_with_msgs.messages or [])} messages")

    print("\n=== Listing Conversations ===")
    # List all conversations for the tenant
    conversations = client.conversations.list(
        tenant_name="acme-corp",
        status=ConversationStatus.ACTIVE
    )
    print(f"Active conversations for acme-corp: {len(conversations)}")

    print("\n=== Searching Conversations ===")
    # Search conversations by title
    conv_results = client.conversations.search(
        q="support",
        tenant_name="acme-corp"
    )
    print(f"Found {len(conv_results)} conversations matching 'support'")

    print("\n=== Updating Conversation ===")
    # Update conversation
    updated_conv = client.conversations.update(
        conversation_id=conv.id,
        title="Customer Support - Shipping Address Update",
        metadata={
            **conv.metadata,
            "resolved": True,
            "resolution_type": "address_change"
        }
    )
    print(f"Updated title: {updated_conv.title}")

    print("\n=== Archiving Conversation ===")
    # Archive the conversation when done
    archived_conv = client.conversations.archive(conv.id)
    print(f"Conversation archived: {archived_conv.status == ConversationStatus.ARCHIVED}")

    print("\n=== Listing Tenants ===")
    # List all tenants
    tenants = client.tenants.list()
    print(f"Total tenants: {len(tenants)}")
    for tenant in tenants:
        print(f"  - {tenant.name} (ID: {tenant.id})")

    print("\n=== Cleanup ===")
    # Clean up - delete the test conversation
    client.conversations.delete(conv.id)
    print("Conversation deleted")

    # No need to call client.close() - automatic cleanup!
    print("\n✅ Example completed successfully!")


if __name__ == "__main__":
    main()
