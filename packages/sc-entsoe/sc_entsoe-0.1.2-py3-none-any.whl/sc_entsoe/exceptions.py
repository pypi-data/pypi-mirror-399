"""Custom exceptions for ENTSOE API interactions."""

from typing import Any


class EntsoeAPIError(Exception):
    """Base exception for ENTSOE API errors."""

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        offending_params: dict[str, Any] | None = None,
        retryable: bool = False,
        response_text: str | None = None,
    ):
        """Initialize ENTSOE API error.

        Args:
            message: Human-readable error message
            error_code: ENTSOE error code if available
            offending_params: Sanitized request parameters (API key redacted)
            retryable: Whether retrying the request makes sense
            response_text: Raw response text for debugging
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.offending_params = offending_params or {}
        self.retryable = retryable
        self.response_text = response_text

    def __str__(self) -> str:
        """String representation with sanitized params."""
        parts = [self.message]
        if self.error_code:
            parts.append(f"Error code: {self.error_code}")
        if self.offending_params:
            parts.append(f"Parameters: {self.offending_params}")
        return " | ".join(parts)


class AuthenticationError(EntsoeAPIError):
    """Invalid API key or authentication failure (401)."""

    def __init__(self, message: str = "Invalid API key", **kwargs: Any):
        super().__init__(message, error_code="401", retryable=False, **kwargs)


class RateLimitError(EntsoeAPIError):
    """Rate limit exceeded (429)."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: int | None = None,
        **kwargs: Any,
    ):
        super().__init__(message, error_code="429", retryable=True, **kwargs)
        self.retry_after = retry_after


class NoDataError(EntsoeAPIError):
    """No data available for the requested query (200 but empty response)."""

    def __init__(self, message: str = "No data available", **kwargs: Any):
        super().__init__(message, error_code="NO_DATA", retryable=False, **kwargs)


class InvalidParameterError(EntsoeAPIError):
    """Invalid query parameters (400)."""

    def __init__(self, message: str, **kwargs: Any):
        super().__init__(message, error_code="400", retryable=False, **kwargs)


class CircuitBreakerOpenError(EntsoeAPIError):
    """Circuit breaker is open, preventing requests."""

    def __init__(
        self, message: str = "Circuit breaker is open", failure_count: int = 0, **kwargs: Any
    ):
        super().__init__(message, error_code="CIRCUIT_OPEN", retryable=True, **kwargs)
        self.failure_count = failure_count


class ParseError(EntsoeAPIError):
    """Failed to parse ENTSOE response."""

    def __init__(self, message: str, **kwargs: Any):
        super().__init__(message, error_code="PARSE_ERROR", retryable=False, **kwargs)
