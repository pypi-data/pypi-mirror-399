"""Pagination examples for march-history SDK."""

from march_history import MarchHistoryClient
from march_history.models import MessageRole

def manual_pagination():
    """Example of manual pagination with explicit offset/limit."""
    client = MarchHistoryClient(base_url="http://localhost:8000")

    print("=== Manual Pagination ===")
    page_size = 10
    offset = 0

    while True:
        # Fetch one page
        conversations = client.conversations.list(
            offset=offset,
            limit=page_size
        )

        if not conversations:
            break

        print(f"Page starting at offset {offset}: {len(conversations)} conversations")
        for conv in conversations:
            print(f"  - {conv.title}")

        # Move to next page
        offset += len(conversations)

        # Break if we got fewer items than page_size (last page)
        if len(conversations) < page_size:
            break


def auto_pagination():
    """Example of automatic pagination with iterators."""
    client = MarchHistoryClient(base_url="http://localhost:8000")

    print("\n=== Auto-Pagination ===")

    # Iterate over all conversations automatically
    count = 0
    for conv in client.conversations.list_iter(
        tenant_name="acme-corp",
        page_size=50  # Fetch 50 items per API call
    ):
        count += 1
        print(f"{count}. {conv.title}")

    print(f"Total conversations: {count}")


def limited_pagination():
    """Example of pagination with a maximum item limit."""
    client = MarchHistoryClient(base_url="http://localhost:8000")

    print("\n=== Limited Pagination ===")

    # Only fetch first 100 items, even if more exist
    count = 0
    for conv in client.conversations.list_iter(
        tenant_name="acme-corp",
        page_size=25,
        max_items=100  # Stop after 100 items
    ):
        count += 1
        print(f"{count}. {conv.title}")

    print(f"Fetched {count} conversations (max: 100)")


def search_with_pagination():
    """Example of paginated search."""
    client = MarchHistoryClient(base_url="http://localhost:8000")

    print("\n=== Search with Pagination ===")

    # Search and iterate over all results
    for conv in client.conversations.search_iter(
        q="support",
        page_size=20
    ):
        print(f"  - {conv.title}")


def message_pagination():
    """Example of paginating messages in a conversation."""
    client = MarchHistoryClient(base_url="http://localhost:8000")

    # First, create a conversation with many messages
    print("\n=== Creating Test Data ===")
    conv = client.conversations.create(
        tenant_name="test-tenant",
        title="Pagination Test Conversation"
    )
    print(f"Created conversation {conv.id}")

    # Add 50 messages
    for i in range(50):
        client.messages.create(
            conversation_id=conv.id,
            role=MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT,
            content=f"Message number {i+1}"
        )
    print("Added 50 messages")

    print("\n=== Paginating Messages ===")

    # Auto-paginate through all messages
    count = 0
    for msg in client.messages.list_iter(
        conversation_id=conv.id,
        page_size=10  # Fetch 10 messages per page
    ):
        count += 1
        print(f"{count}. [{msg.sequence_number}] {msg.role}: {msg.content}")

    print(f"Total messages: {count}")

    # Cleanup
    client.conversations.delete(conv.id)
    print("\nTest conversation deleted")


def main():
    """Run all pagination examples."""
    try:
        manual_pagination()
        auto_pagination()
        limited_pagination()
        search_with_pagination()
        message_pagination()

        print("\n✅ All pagination examples completed successfully!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
