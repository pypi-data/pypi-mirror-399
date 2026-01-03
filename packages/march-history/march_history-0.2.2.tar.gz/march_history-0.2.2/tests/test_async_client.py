"""Tests for async client and HTTP operations."""

import pytest
import respx
from httpx import Response

from march_history import AsyncMarchHistoryClient
from march_history.exceptions import (
    BadRequestError,
    ConflictError,
    NotFoundError,
    RetryError,
    ServerError,
    ValidationError,
)
from march_history.models import ConversationStatus, MessageRole


class TestAsyncClientInitialization:
    """Test async client initialization."""

    def test_default_initialization(self):
        """Test async client with default settings."""
        client = AsyncMarchHistoryClient()
        assert client._config.base_url == "http://localhost:8000"
        assert client._config.timeout == 30.0
        assert client._config.retry_config.max_retries == 3

    def test_custom_initialization(self):
        """Test async client with custom settings."""
        client = AsyncMarchHistoryClient(
            base_url="https://api.example.com",
            timeout=60.0,
            max_retries=5,
        )
        assert client._config.base_url == "https://api.example.com"
        assert client._config.timeout == 60.0
        assert client._config.retry_config.max_retries == 5

    def test_initialization_with_api_key(self):
        """Test async client with API key."""
        client = AsyncMarchHistoryClient(
            base_url="https://api.example.com",
            api_key="test-key-123",
        )
        assert client._config.api_key == "test-key-123"

    def test_base_url_normalization(self):
        """Test that trailing slash is removed from base URL."""
        client = AsyncMarchHistoryClient(base_url="http://localhost:8000/")
        assert client._config.base_url == "http://localhost:8000"

    def test_resource_initialization(self):
        """Test that async resources are initialized."""
        client = AsyncMarchHistoryClient()
        assert client.tenants is not None
        assert client.conversations is not None
        assert client.messages is not None

    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test using async client as context manager."""
        async with AsyncMarchHistoryClient() as client:
            assert client is not None


class TestAsyncHTTPHeaders:
    """Test async HTTP headers including API key."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_api_key_header_sent(self, base_url):
        """Test that X-API-Key header is sent when api_key is provided."""
        client = AsyncMarchHistoryClient(
            base_url=base_url,
            api_key="test-api-key-123",
        )

        route = respx.get(f"{base_url}/tenants/").mock(
            return_value=Response(200, json=[])
        )

        await client.tenants.list()

        assert route.called
        request = route.calls.last.request
        assert request.headers.get("X-API-Key") == "test-api-key-123"

    @pytest.mark.asyncio
    @respx.mock
    async def test_no_api_key_header_when_not_provided(self, base_url):
        """Test that X-API-Key header is not sent when api_key is None."""
        client = AsyncMarchHistoryClient(base_url=base_url)

        route = respx.get(f"{base_url}/tenants/").mock(
            return_value=Response(200, json=[])
        )

        await client.tenants.list()

        assert route.called
        request = route.calls.last.request
        assert "X-API-Key" not in request.headers

    @pytest.mark.asyncio
    @respx.mock
    async def test_user_agent_header(self, base_url):
        """Test that User-Agent header is sent."""
        client = AsyncMarchHistoryClient(base_url=base_url)

        route = respx.get(f"{base_url}/tenants/").mock(
            return_value=Response(200, json=[])
        )

        await client.tenants.list()

        request = route.calls.last.request
        assert "march-history-python" in request.headers.get("User-Agent", "")

    @pytest.mark.asyncio
    @respx.mock
    async def test_custom_headers(self, base_url):
        """Test that custom headers are sent."""
        client = AsyncMarchHistoryClient(
            base_url=base_url,
            custom_headers={"X-Custom": "custom-value"},
        )

        route = respx.get(f"{base_url}/tenants/").mock(
            return_value=Response(200, json=[])
        )

        await client.tenants.list()

        request = route.calls.last.request
        assert request.headers.get("X-Custom") == "custom-value"


class TestAsyncErrorHandling:
    """Test async error handling for different HTTP status codes."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_404_not_found(self, async_client, base_url):
        """Test 404 raises NotFoundError."""
        respx.get(f"{base_url}/tenants/999").mock(
            return_value=Response(
                404,
                json={"error": "not_found", "message": "Tenant not found"},
            )
        )

        with pytest.raises(NotFoundError) as exc:
            await async_client.tenants.get(999)

        assert exc.value.status_code == 404
        assert "not found" in exc.value.message.lower()

    @pytest.mark.asyncio
    @respx.mock
    async def test_422_validation_error(self, async_client, base_url):
        """Test 422 raises ValidationError."""
        respx.post(f"{base_url}/conversations/").mock(
            return_value=Response(
                422,
                json={
                    "error": "validation_error",
                    "message": "Validation failed",
                    "details": [
                        {
                            "field": "tenant_name",
                            "message": "Invalid format",
                            "code": "invalid",
                        }
                    ],
                },
            )
        )

        with pytest.raises(ValidationError) as exc:
            await async_client.conversations.create(
                tenant_name="test", user_id="user-123"
            )

        assert exc.value.status_code == 422
        assert len(exc.value.details) == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_409_conflict_error(
        self, async_client, base_url, conversation_response
    ):
        """Test 409 raises ConflictError."""
        respx.post(f"{base_url}/conversations/").mock(
            return_value=Response(201, json=conversation_response)
        )

        respx.post(f"{base_url}/conversations/1/messages").mock(
            return_value=Response(
                409,
                json={
                    "error": "conflict",
                    "message": "Duplicate sequence number",
                },
            )
        )

        conv = await async_client.conversations.create(
            tenant_name="test", user_id="user-123", title="Test"
        )

        with pytest.raises(ConflictError) as exc:
            await async_client.messages.create(
                conversation_id=conv.id,
                role=MessageRole.USER,
                content="Test",
                sequence_number=0,
            )

        assert exc.value.status_code == 409

    @pytest.mark.asyncio
    @respx.mock
    async def test_400_bad_request(self, async_client, base_url):
        """Test 400 raises BadRequestError."""
        respx.get(f"{base_url}/conversations/").mock(
            return_value=Response(
                400,
                json={"error": "bad_request", "message": "Invalid parameter"},
            )
        )

        with pytest.raises(BadRequestError) as exc:
            await async_client.conversations.list()

        assert exc.value.status_code == 400

    @pytest.mark.asyncio
    @respx.mock
    async def test_500_server_error(self, async_client, base_url):
        """Test 500 is retried and raises RetryError after exhaustion."""
        respx.get(f"{base_url}/tenants/").mock(
            return_value=Response(
                500,
                json={"error": "internal_error", "message": "Server error"},
            )
        )

        with pytest.raises(RetryError) as exc:
            await async_client.tenants.list()

        assert isinstance(exc.value.last_exception, ServerError)
        assert exc.value.last_exception.status_code == 500
