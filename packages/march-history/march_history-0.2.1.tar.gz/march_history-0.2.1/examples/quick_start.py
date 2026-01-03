#!/usr/bin/env python3
"""
Quick start script for march-history SDK.

This is the simplest possible example to get started.
"""

from march_history import MarchHistoryClient
from march_history.models import MessageRole


def main():
    # 1. Create client (update base_url to your API endpoint)
    client = MarchHistoryClient(base_url="http://localhost:8000")

    # 2. Create a conversation
    conversation = client.conversations.create(
        tenant_name="my-company",
        user_id="user-123",
        title="My First Conversation"
    )
    print(f"✓ Created conversation: {conversation.id}")

    # 3. Add a message
    message = client.messages.create(
        conversation_id=conversation.id,
        role=MessageRole.USER,
        content="Hello, world!"
    )
    print(f"✓ Added message: {message.content}")

    # 4. Get all messages
    messages = client.messages.list(conversation_id=conversation.id)
    print(f"✓ Total messages: {len(messages)}")

    # That's it! No cleanup needed - automatic resource management.
    print("\n🎉 Success! You're ready to use the SDK.")


if __name__ == "__main__":
    main()
