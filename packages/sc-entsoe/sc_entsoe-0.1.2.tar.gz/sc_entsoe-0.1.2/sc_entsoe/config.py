"""Configuration for ENTSOE client."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EntsoeConfig(BaseSettings):
    """Configuration for ENTSOE client."""

    model_config = SettingsConfigDict(
        env_prefix="ENTSOE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # API Configuration
    api_base_url: str = Field(
        default="https://web-api.tp.entsoe.eu/api",
        description="ENTSOE API base URL",
    )
    api_timeout: int = Field(
        default=30,
        description="Request timeout in seconds",
    )

    # Rate Limiting
    rate_limit_requests: int = Field(
        default=10,
        description="Maximum requests per second",
    )
    rate_limit_burst: int = Field(
        default=20,
        description="Maximum burst requests",
    )

    # Retry Configuration
    retry_attempts: int = Field(
        default=3,
        description="Maximum retry attempts",
    )
    retry_max_wait: int = Field(
        default=10,
        description="Maximum wait time between retries (seconds)",
    )

    # Circuit Breaker
    circuit_breaker_threshold: int = Field(
        default=5,
        description="Number of consecutive failures before opening circuit",
    )
    circuit_breaker_timeout: int = Field(
        default=60,
        description="Circuit breaker cool-down period (seconds)",
    )

    # Cache Configuration
    cache_enabled: bool = Field(
        default=False,
        description="Enable caching",
    )
    cache_ttl: int = Field(
        default=3600,
        description="Cache TTL in seconds (1 hour default)",
    )
    cache_max_size: int = Field(
        default=1000,
        description="Maximum cache entries",
    )

    # Logging
    debug_logging: bool = Field(
        default=False,
        description="Enable debug logging (includes request URLs)",
    )
    safe_logging: bool = Field(
        default=True,
        description="Safe logging mode (redact sensitive data)",
    )

    # Data Processing
    fill_missing: bool = Field(
        default=True,
        description="Fill missing intervals (ENTSOE duplicate omission handling)",
    )
    strict_schema: bool = Field(
        default=False,
        description="Strict schema validation (raise on unexpected format)",
    )
