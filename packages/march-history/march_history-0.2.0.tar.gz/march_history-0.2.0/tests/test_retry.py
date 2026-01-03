"""Tests for retry logic and error handling."""

import pytest
import respx
from httpx import Response

from march_history.config import RetryConfig
from march_history.exceptions import NetworkError, RetryError, ServerError


class TestRetryLogic:
    """Test retry logic with exponential backoff."""

    @respx.mock
    def test_retry_on_500_error(self, base_url):
        """Test that 500 errors trigger retry."""
        from march_history import MarchHistoryClient

        client = MarchHistoryClient(
            base_url=base_url,
            retry_config=RetryConfig(
                max_retries=2,
                backoff_factor=0.01,  # Very short for tests
                max_backoff_seconds=0.1,
            ),
        )

        # Fail twice, then succeed
        route = respx.get(f"{base_url}/tenants/")
        route.side_effect = [
            Response(500, json={"error": "server_error"}),
            Response(500, json={"error": "server_error"}),
            Response(200, json=[]),
        ]

        # Should succeed after retries
        result = client.tenants.list()

        assert result == []
        assert route.call_count == 3  # Initial + 2 retries

    @respx.mock
    def test_retry_exhaustion(self, base_url):
        """Test that retry gives up after max_retries."""
        from march_history import MarchHistoryClient

        client = MarchHistoryClient(
            base_url=base_url,
            retry_config=RetryConfig(
                max_retries=1,
                backoff_factor=0.01,
            ),
        )

        # Always fail
        route = respx.get(f"{base_url}/tenants/")
        route.mock(return_value=Response(500, json={"error": "server_error"}))

        with pytest.raises(RetryError) as exc:
            client.tenants.list()

        # Should try 2 times total (1 initial + 1 retry)
        assert route.call_count == 2
        assert "Max retries" in str(exc.value)
        assert isinstance(exc.value.last_exception, ServerError)

    @respx.mock
    def test_no_retry_on_404(self, base_url):
        """Test that 404 errors don't trigger retry."""
        from march_history import MarchHistoryClient
        from march_history.exceptions import NotFoundError

        client = MarchHistoryClient(
            base_url=base_url,
            retry_config=RetryConfig(max_retries=3),
        )

        route = respx.get(f"{base_url}/tenants/999")
        route.mock(return_value=Response(404, json={"error": "not_found"}))

        with pytest.raises(NotFoundError):
            client.tenants.get(999)

        # Should not retry on 404
        assert route.call_count == 1

    @respx.mock
    def test_no_retry_on_422(self, base_url):
        """Test that validation errors don't trigger retry."""
        from march_history import MarchHistoryClient
        from march_history.exceptions import ValidationError

        client = MarchHistoryClient(
            base_url=base_url,
            retry_config=RetryConfig(max_retries=3),
        )

        route = respx.post(f"{base_url}/conversations/")
        route.mock(
            return_value=Response(
                422,
                json={"error": "validation_error", "message": "Invalid"},
            )
        )

        with pytest.raises(ValidationError):
            client.conversations.create(
                tenant_name="test", user_id="user-123", title="Test"
            )

        # Should not retry on validation error
        assert route.call_count == 1

    @respx.mock
    def test_retry_on_network_error(self, base_url):
        """Test retry on network errors."""
        from march_history import MarchHistoryClient
        import httpx

        client = MarchHistoryClient(
            base_url=base_url,
            retry_config=RetryConfig(
                max_retries=2,
                backoff_factor=0.01,
            ),
        )

        # Simulate network errors then success
        route = respx.get(f"{base_url}/tenants/")
        route.side_effect = [
            httpx.ConnectError("Connection failed"),
            httpx.ConnectError("Connection failed"),
            Response(200, json=[]),
        ]

        # Should succeed after retries
        result = client.tenants.list()

        assert result == []
        assert route.call_count == 3

    @respx.mock
    def test_retry_status_codes_configurable(self, base_url):
        """Test that retry status codes are configurable."""
        from march_history import MarchHistoryClient

        # Configure to only retry on 503
        client = MarchHistoryClient(
            base_url=base_url,
            retry_config=RetryConfig(
                max_retries=2,
                backoff_factor=0.01,
                retry_status_codes=(503,),  # Only 503
            ),
        )

        # 502 should not be retried
        route = respx.get(f"{base_url}/tenants/")
        route.mock(return_value=Response(502, json={"error": "bad_gateway"}))

        with pytest.raises(ServerError):
            client.tenants.list()

        # Should not retry
        assert route.call_count == 1

    @respx.mock
    def test_successful_request_no_retry(self, base_url, tenant_response):
        """Test that successful requests don't retry."""
        from march_history import MarchHistoryClient

        client = MarchHistoryClient(
            base_url=base_url,
            retry_config=RetryConfig(max_retries=3),
        )

        route = respx.get(f"{base_url}/tenants/1")
        route.mock(return_value=Response(200, json=tenant_response))

        tenant = client.tenants.get(1)

        assert tenant.id == 1
        assert route.call_count == 1  # No retries needed


class TestRetryConfiguration:
    """Test retry configuration options."""

    def test_default_retry_config(self):
        """Test default retry configuration."""
        config = RetryConfig()

        assert config.max_retries == 3
        assert config.backoff_factor == 1.5
        assert 500 in config.retry_status_codes
        assert 502 in config.retry_status_codes
        assert config.max_backoff_seconds == 60.0

    def test_custom_retry_config(self):
        """Test custom retry configuration."""
        config = RetryConfig(
            max_retries=5,
            backoff_factor=2.0,
            retry_status_codes=(500, 503),
            max_backoff_seconds=120.0,
        )

        assert config.max_retries == 5
        assert config.backoff_factor == 2.0
        assert config.retry_status_codes == (500, 503)
        assert config.max_backoff_seconds == 120.0

    def test_client_with_max_retries_shorthand(self, base_url):
        """Test client initialization with max_retries shorthand."""
        from march_history import MarchHistoryClient

        client = MarchHistoryClient(
            base_url=base_url,
            max_retries=5,
        )

        assert client._config.retry_config.max_retries == 5

    def test_client_with_full_retry_config(self, base_url):
        """Test client with full RetryConfig object."""
        from march_history import MarchHistoryClient

        retry_config = RetryConfig(
            max_retries=10,
            backoff_factor=3.0,
        )

        client = MarchHistoryClient(
            base_url=base_url,
            retry_config=retry_config,
        )

        assert client._config.retry_config.max_retries == 10
        assert client._config.retry_config.backoff_factor == 3.0
