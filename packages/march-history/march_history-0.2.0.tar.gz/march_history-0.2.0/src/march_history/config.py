from __future__ import annotations

"""Configuration classes for march-history SDK."""

from dataclasses import dataclass, field


@dataclass
class RetryConfig:
    """
    Configuration for retry behavior with exponential backoff.

    Attributes:
        max_retries: Maximum number of retry attempts (default: 3)
        backoff_factor: Exponential backoff multiplier (default: 1.5)
        retry_status_codes: HTTP status codes that trigger a retry
        max_backoff_seconds: Maximum backoff time in seconds (default: 60.0)
    """

    max_retries: int = 3
    backoff_factor: float = 1.5
    retry_status_codes: tuple[int, ...] = (408, 429, 500, 502, 503, 504)
    max_backoff_seconds: float = 60.0


@dataclass
class ClientConfig:
    """
    Main client configuration.

    Attributes:
        base_url: API base URL (e.g., "http://localhost:8000")
        timeout: Request timeout in seconds (default: 30.0)
        retry_config: Retry configuration
        max_connections: Maximum number of HTTP connections (default: 100)
        max_keepalive_connections: Maximum keepalive connections (default: 20)
        api_key: Optional API key for authentication (sent as X-API-Key header)
        custom_headers: Additional headers to include in all requests
    """

    base_url: str
    timeout: float = 30.0
    retry_config: RetryConfig = field(default_factory=RetryConfig)
    max_connections: int = 100
    max_keepalive_connections: int = 20
    api_key: str | None = None
    custom_headers: dict[str, str] | None = None

    def __post_init__(self) -> None:
        """Normalize base URL by removing trailing slashes."""
        self.base_url = self.base_url.rstrip("/")
