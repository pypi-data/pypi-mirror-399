"""Tests for main client and HTTP operations."""

import pytest
import respx
from httpx import Response

from march_history import MarchHistoryClient
from march_history.exceptions import (
    BadRequestError,
    ConflictError,
    NotFoundError,
    ServerError,
    ValidationError,
)
from march_history.models import ConversationStatus, MessageRole


class TestClientInitialization:
    """Test client initialization."""

    def test_default_initialization(self):
        """Test client with default settings."""
        client = MarchHistoryClient()
        assert client._config.base_url == "http://localhost:8000"
        assert client._config.timeout == 30.0
        assert client._config.retry_config.max_retries == 3

    def test_custom_initialization(self):
        """Test client with custom settings."""
        client = MarchHistoryClient(
            base_url="https://api.example.com",
            timeout=60.0,
            max_retries=5,
        )
        assert client._config.base_url == "https://api.example.com"
        assert client._config.timeout == 60.0
        assert client._config.retry_config.max_retries == 5

    def test_initialization_with_api_key(self):
        """Test client with API key."""
        client = MarchHistoryClient(
            base_url="https://api.example.com",
            api_key="test-key-123",
        )
        assert client._config.api_key == "test-key-123"

    def test_base_url_normalization(self):
        """Test that trailing slash is removed from base URL."""
        client = MarchHistoryClient(base_url="http://localhost:8000/")
        assert client._config.base_url == "http://localhost:8000"

    def test_resource_initialization(self):
        """Test that resources are initialized."""
        client = MarchHistoryClient()
        assert client.tenants is not None
        assert client.conversations is not None
        assert client.messages is not None

    def test_context_manager(self):
        """Test using client as context manager."""
        with MarchHistoryClient() as client:
            assert client is not None


class TestHTTPHeaders:
    """Test HTTP headers including API key."""

    @respx.mock
    def test_api_key_header_sent(self, base_url):
        """Test that X-API-Key header is sent when api_key is provided."""
        client = MarchHistoryClient(
            base_url=base_url,
            api_key="test-api-key-123",
        )

        # Mock the API endpoint
        route = respx.get(f"{base_url}/tenants/").mock(
            return_value=Response(200, json=[])
        )

        # Make request
        client.tenants.list()

        # Verify X-API-Key header was sent
        assert route.called
        request = route.calls.last.request
        assert request.headers.get("X-API-Key") == "test-api-key-123"

    @respx.mock
    def test_no_api_key_header_when_not_provided(self, base_url):
        """Test that X-API-Key header is not sent when api_key is None."""
        client = MarchHistoryClient(base_url=base_url)

        # Mock the API endpoint
        route = respx.get(f"{base_url}/tenants/").mock(
            return_value=Response(200, json=[])
        )

        # Make request
        client.tenants.list()

        # Verify X-API-Key header was not sent
        assert route.called
        request = route.calls.last.request
        assert "X-API-Key" not in request.headers

    @respx.mock
    def test_user_agent_header(self, base_url):
        """Test that User-Agent header is sent."""
        client = MarchHistoryClient(base_url=base_url)

        route = respx.get(f"{base_url}/tenants/").mock(
            return_value=Response(200, json=[])
        )

        client.tenants.list()

        request = route.calls.last.request
        assert "march-history-python" in request.headers.get("User-Agent", "")

    @respx.mock
    def test_custom_headers(self, base_url):
        """Test that custom headers are sent."""
        client = MarchHistoryClient(
            base_url=base_url,
            custom_headers={"X-Custom": "custom-value"},
        )

        route = respx.get(f"{base_url}/tenants/").mock(
            return_value=Response(200, json=[])
        )

        client.tenants.list()

        request = route.calls.last.request
        assert request.headers.get("X-Custom") == "custom-value"


class TestErrorHandling:
    """Test error handling for different HTTP status codes."""

    @respx.mock
    def test_404_not_found(self, client, base_url):
        """Test 404 raises NotFoundError."""
        respx.get(f"{base_url}/tenants/999").mock(
            return_value=Response(
                404,
                json={"error": "not_found", "message": "Tenant not found"},
            )
        )

        with pytest.raises(NotFoundError) as exc:
            client.tenants.get(999)

        assert exc.value.status_code == 404
        assert "not found" in exc.value.message.lower()

    @respx.mock
    def test_422_validation_error(self, client, base_url):
        """Test 422 raises ValidationError."""
        respx.post(f"{base_url}/conversations/").mock(
            return_value=Response(
                422,
                json={
                    "error": "validation_error",
                    "message": "Validation failed",
                    "details": [
                        {"field": "tenant_name", "message": "Required", "code": "required"}
                    ],
                },
            )
        )

        with pytest.raises(ValidationError) as exc:
            client.conversations.create(tenant_name="")

        assert exc.value.status_code == 422
        assert len(exc.value.details) == 1

    @respx.mock
    def test_409_conflict_error(self, client, base_url, conversation_response):
        """Test 409 raises ConflictError."""
        # First create conversation
        respx.post(f"{base_url}/conversations/").mock(
            return_value=Response(201, json=conversation_response)
        )

        # Then conflict on duplicate sequence number
        respx.post(f"{base_url}/conversations/1/messages").mock(
            return_value=Response(
                409,
                json={
                    "error": "conflict",
                    "message": "Duplicate sequence number",
                },
            )
        )

        conv = client.conversations.create(tenant_name="test", title="Test")

        with pytest.raises(ConflictError) as exc:
            client.messages.create(
                conversation_id=conv.id,
                role=MessageRole.USER,
                content="Test",
                sequence_number=0,
            )

        assert exc.value.status_code == 409

    @respx.mock
    def test_400_bad_request(self, client, base_url):
        """Test 400 raises BadRequestError."""
        respx.get(f"{base_url}/conversations/").mock(
            return_value=Response(
                400,
                json={"error": "bad_request", "message": "Invalid parameter"},
            )
        )

        with pytest.raises(BadRequestError) as exc:
            client.conversations.list()

        assert exc.value.status_code == 400

    @respx.mock
    def test_500_server_error(self, client, base_url):
        """Test 500 raises ServerError."""
        respx.get(f"{base_url}/tenants/").mock(
            return_value=Response(
                500,
                json={"error": "internal_error", "message": "Server error"},
            )
        )

        with pytest.raises(ServerError) as exc:
            client.tenants.list()

        assert exc.value.status_code == 500
