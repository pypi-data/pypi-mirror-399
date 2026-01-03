"""sc-entsoe: Modern, high-performance Python library for ENTSOE Transparency Platform.

Example usage:
    >>> from sc_entsoe import EntsoeClient
    >>> with EntsoeClient() as client:
    ...     result = client.get_day_ahead_prices("DE", "2024-01-01", "2024-01-02")
    ...     print(result.df)
"""

__version__ = "0.1.0"

# Import main classes for convenience
from app.client import AsyncEntsoeClient
from app.config import EntsoeConfig
from app.exceptions import (
    AuthenticationError,
    CircuitBreakerOpenError,
    EntsoeAPIError,
    InvalidParameterError,
    NoDataError,
    ParseError,
    RateLimitError,
)
from app.models import (
    Area,
    AuctionType,
    BusinessType,
    DocStatus,
    DocumentType,
    EntsoeFrame,
    MarketAgreementType,
    ProcessType,
    PSRType,
    Resolution,
)
from app.sync_client import EntsoeClient

__all__ = [
    # Version
    "__version__",
    # Clients
    "EntsoeClient",
    "AsyncEntsoeClient",
    # Configuration
    "EntsoeConfig",
    # Models
    "EntsoeFrame",
    "Area",
    "AuctionType",
    "BusinessType",
    "DocStatus",
    "DocumentType",
    "MarketAgreementType",
    "ProcessType",
    "PSRType",
    "Resolution",
    # Exceptions
    "EntsoeAPIError",
    "AuthenticationError",
    "RateLimitError",
    "NoDataError",
    "InvalidParameterError",
    "CircuitBreakerOpenError",
    "ParseError",
]
