"""Error handling examples for march-history SDK."""

from march_history import MarchHistoryClient
from march_history.exceptions import (
    NotFoundError,
    ValidationError,
    ConflictError,
    RetryError,
    APIError,
)
from march_history.models import MessageRole


def handle_not_found():
    """Example of handling 404 Not Found errors."""
    client = MarchHistoryClient(base_url="http://localhost:8000")

    print("=== Handling Not Found Errors ===")

    try:
        # Try to get a non-existent conversation
        conv = client.conversations.get(99999)
    except NotFoundError as e:
        print(f"✓ Caught NotFoundError")
        print(f"  Message: {e.message}")
        print(f"  Status Code: {e.status_code}")
        print(f"  Error Code: {e.error_code}")


def handle_validation_error():
    """Example of handling 422 Validation errors."""
    client = MarchHistoryClient(base_url="http://localhost:8000")

    print("\n=== Handling Validation Errors ===")

    # Create a valid conversation first
    conv = client.conversations.create(
        tenant_name="test-tenant",
        title="Error Handling Test"
    )

    try:
        # Try to create a message with invalid data
        client.messages.create(
            conversation_id=conv.id,
            role="invalid_role",  # This will fail validation
            content="Test message"
        )
    except ValidationError as e:
        print(f"✓ Caught ValidationError")
        print(f"  Message: {e.message}")
        print(f"  Status Code: {e.status_code}")
        print(f"  Details:")
        for detail in e.details:
            print(f"    - Field: {detail.get('field')}")
            print(f"      Message: {detail.get('message')}")
            print(f"      Code: {detail.get('code')}")

    # Cleanup
    client.conversations.delete(conv.id)


def handle_conflict_error():
    """Example of handling 409 Conflict errors."""
    client = MarchHistoryClient(base_url="http://localhost:8000")

    print("\n=== Handling Conflict Errors ===")

    # Create a conversation
    conv = client.conversations.create(
        tenant_name="test-tenant",
        title="Conflict Test"
    )

    # Create a message with explicit sequence number
    client.messages.create(
        conversation_id=conv.id,
        role=MessageRole.USER,
        content="First message",
        sequence_number=0
    )

    try:
        # Try to create another message with same sequence number
        client.messages.create(
            conversation_id=conv.id,
            role=MessageRole.USER,
            content="Duplicate sequence",
            sequence_number=0  # This will conflict
        )
    except ConflictError as e:
        print(f"✓ Caught ConflictError")
        print(f"  Message: {e.message}")
        print(f"  Status Code: {e.status_code}")

    # Cleanup
    client.conversations.delete(conv.id)


def handle_retry_error():
    """Example of handling retry exhaustion."""
    from march_history.config import RetryConfig

    print("\n=== Handling Retry Errors ===")

    # Create client with very aggressive retry settings
    client = MarchHistoryClient(
        base_url="http://invalid-host-that-does-not-exist.local",
        retry_config=RetryConfig(
            max_retries=2,  # Only retry twice
            backoff_factor=0.1,  # Very short backoff
            max_backoff_seconds=1.0
        )
    )

    try:
        # This will fail because the host doesn't exist
        client.tenants.list()
    except RetryError as e:
        print(f"✓ Caught RetryError")
        print(f"  Message: {str(e)}")
        print(f"  Last Exception Type: {type(e.last_exception).__name__}")


def comprehensive_error_handling():
    """Example of comprehensive error handling."""
    client = MarchHistoryClient(base_url="http://localhost:8000")

    print("\n=== Comprehensive Error Handling ===")

    conversation_id = None

    try:
        # Try to create and work with a conversation
        conv = client.conversations.create(
            tenant_name="test-tenant",
            title="Comprehensive Test"
        )
        conversation_id = conv.id
        print(f"✓ Created conversation {conversation_id}")

        # Try to add a message
        msg = client.messages.create(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content="Test message"
        )
        print(f"✓ Created message {msg.id}")

        # Try to get a non-existent message
        try:
            client.messages.get(99999)
        except NotFoundError:
            print("✓ Handled NotFoundError for message")

        # Try to search with invalid parameters
        try:
            results = client.messages.search(
                conversation_id=conversation_id,
                q=""  # Empty search query might fail
            )
        except ValidationError:
            print("✓ Handled ValidationError for search")

    except APIError as e:
        # Catch all API errors
        print(f"❌ API Error: {e}")
        print(f"   Status: {e.status_code}")
        print(f"   Details: {e.response_body}")

    except Exception as e:
        # Catch any other errors
        print(f"❌ Unexpected Error: {type(e).__name__}: {e}")

    finally:
        # Always cleanup
        if conversation_id:
            try:
                client.conversations.delete(conversation_id)
                print("✓ Cleaned up test conversation")
            except Exception as e:
                print(f"⚠ Cleanup failed: {e}")


def main():
    """Run all error handling examples."""
    try:
        handle_not_found()
        handle_validation_error()
        handle_conflict_error()
        handle_retry_error()
        comprehensive_error_handling()

        print("\n✅ All error handling examples completed!")

    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        raise


if __name__ == "__main__":
    main()
