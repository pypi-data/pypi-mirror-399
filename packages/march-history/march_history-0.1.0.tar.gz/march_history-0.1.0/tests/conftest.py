"""Pytest configuration and fixtures for march-history SDK tests."""

import pytest
import respx
from httpx import Response

from march_history import MarchHistoryClient
from march_history.config import ClientConfig, RetryConfig


@pytest.fixture
def base_url() -> str:
    """Return base URL for tests."""
    return "http://test-api.example.com"


@pytest.fixture
def client_config(base_url: str) -> ClientConfig:
    """Return test client configuration."""
    return ClientConfig(
        base_url=base_url,
        timeout=10.0,
        retry_config=RetryConfig(max_retries=2, backoff_factor=0.1),
    )


@pytest.fixture
def client(base_url: str) -> MarchHistoryClient:
    """Return test client instance."""
    return MarchHistoryClient(
        base_url=base_url,
        timeout=10.0,
        max_retries=2,
    )


@pytest.fixture
def client_with_api_key(base_url: str) -> MarchHistoryClient:
    """Return test client with API key."""
    return MarchHistoryClient(
        base_url=base_url,
        api_key="test-api-key-123",
        timeout=10.0,
    )


@pytest.fixture
def mock_api():
    """Provide mocked HTTP responses using respx."""
    with respx.mock:
        yield respx


@pytest.fixture
def tenant_response() -> dict:
    """Return sample tenant response."""
    return {
        "id": 1,
        "name": "test-tenant",
        "created_at": "2025-01-15T10:00:00Z",
        "updated_at": "2025-01-15T10:00:00Z",
    }


@pytest.fixture
def conversation_response() -> dict:
    """Return sample conversation response."""
    return {
        "id": 1,
        "tenant_id": 1,
        "agent_identifier": "test-agent",
        "title": "Test Conversation",
        "status": "active",
        "metadata": {"key": "value"},
        "created_at": "2025-01-15T10:00:00Z",
        "updated_at": "2025-01-15T10:00:00Z",
    }


@pytest.fixture
def message_response() -> dict:
    """Return sample message response."""
    return {
        "id": 1,
        "conversation_id": 1,
        "sequence_number": 0,
        "role": "user",
        "content": "Test message",
        "metadata": {},
        "created_at": "2025-01-15T10:00:00Z",
        "updated_at": "2025-01-15T10:00:00Z",
    }
