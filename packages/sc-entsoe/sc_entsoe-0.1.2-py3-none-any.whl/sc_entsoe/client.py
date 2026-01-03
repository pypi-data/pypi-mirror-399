"""Async HTTP client for ENTSOE API with retry logic, rate limiting, and circuit breaker."""

import asyncio
import hashlib
import time
from collections.abc import Callable
from datetime import datetime
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from sc_entsoe.auth import CredentialManager, sanitize_params
from sc_entsoe.config import EntsoeConfig
from sc_entsoe.core.log import get_logger
from sc_entsoe.exceptions import (
    AuthenticationError,
    CircuitBreakerOpenError,
    EntsoeAPIError,
    InvalidParameterError,
    NoDataError,
    ParseError,
    RateLimitError,
)
from sc_entsoe.models import EntsoeFrame
from sc_entsoe.parsers.converters import canonicalize_params
from sc_entsoe.parsers.xml_parser import parse_entsoe_xml

logger = get_logger(__name__)


class RateLimiter:
    """Token bucket rate limiter."""

    def __init__(self, requests_per_second: float, burst: int):
        """Initialize rate limiter.

        Args:
            requests_per_second: Maximum requests per second
            burst: Maximum burst requests
        """
        self.rate = requests_per_second
        self.burst = burst
        self.tokens = float(burst)
        self.last_update = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Acquire a token, waiting if necessary."""
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_update
            self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
            self.last_update = now

            if self.tokens < 1:
                wait_time = (1 - self.tokens) / self.rate
                await asyncio.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= 1


class CircuitBreaker:
    """Circuit breaker pattern implementation."""

    def __init__(self, threshold: int, timeout: int):
        """Initialize circuit breaker.

        Args:
            threshold: Number of failures before opening
            timeout: Cool-down period in seconds
        """
        self.threshold = threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time: float | None = None
        self.state = "closed"  # closed, open, half-open
        self._lock = asyncio.Lock()

    async def call(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        """Execute function with circuit breaker protection.

        Args:
            func: Async function to call
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            CircuitBreakerOpenError: If circuit is open
        """
        async with self._lock:
            if self.state == "open":
                # Check if cool-down period has elapsed
                if (
                    self.last_failure_time
                    and time.monotonic() - self.last_failure_time >= self.timeout
                ):
                    self.state = "half-open"
                    logger.info("circuit_breaker_half_open")
                else:
                    raise CircuitBreakerOpenError(failure_count=self.failure_count)

        try:
            result = await func(*args, **kwargs)

            # Success - reset circuit
            async with self._lock:
                if self.state == "half-open":
                    self.state = "closed"
                    self.failure_count = 0
                    logger.info("circuit_breaker_closed")

            return result

        except Exception:
            async with self._lock:
                self.failure_count += 1
                self.last_failure_time = time.monotonic()

                if self.failure_count >= self.threshold:
                    self.state = "open"
                    logger.warning(
                        "circuit_breaker_opened",
                        failure_count=self.failure_count,
                        threshold=self.threshold,
                    )

            raise


class RequestDeduplicator:
    """Deduplicate concurrent identical requests."""

    def __init__(self):
        self._in_flight: dict[str, asyncio.Future] = {}
        self._lock = asyncio.Lock()

    def _make_key(self, params: dict[str, Any]) -> str:
        """Generate cache key from parameters."""
        canonical = canonicalize_params(params)
        key_str = str(sorted(canonical.items()))
        return hashlib.sha256(key_str.encode()).hexdigest()

    async def get_or_fetch(self, params: dict[str, Any], fetch_func: Callable) -> Any:
        """Get result from in-flight request or start new one.

        Args:
            params: Request parameters
            fetch_func: Async function to fetch data

        Returns:
            Fetch result
        """
        key = self._make_key(params)

        async with self._lock:
            if key in self._in_flight:
                # Request already in flight - wait for it
                logger.debug("request_deduplicated", cache_key=key)
                existing_future = self._in_flight[key]
                # Release lock while waiting
                async with self._lock:
                    pass
                return await existing_future

            # Start new request
            new_future: asyncio.Future = asyncio.Future()
            self._in_flight[key] = new_future

        try:
            result = await fetch_func()
            new_future.set_result(result)
            return result
        except Exception as e:
            new_future.set_exception(e)
            raise
        finally:
            async with self._lock:
                self._in_flight.pop(key, None)


class AsyncEntsoeClient:
    """Async ENTSOE API client with retry, rate limiting, and circuit breaker."""

    def __init__(
        self,
        api_key: str | None = None,
        config: EntsoeConfig | None = None,
        hooks: Any | None = None,
    ):
        """Initialize ENTSOE client.

        Args:
            api_key: ENTSOE API key (optional, can load from env)
            config: Configuration object
            hooks: Observability hooks
        """
        self.config = config or EntsoeConfig()
        self.credential_manager = CredentialManager(api_key=api_key)
        self.hooks = hooks

        # HTTP client
        self._client: httpx.AsyncClient | None = None

        # Rate limiter
        self.rate_limiter = RateLimiter(
            requests_per_second=self.config.rate_limit_requests,
            burst=self.config.rate_limit_burst,
        )

        # Circuit breaker
        self.circuit_breaker = CircuitBreaker(
            threshold=self.config.circuit_breaker_threshold,
            timeout=self.config.circuit_breaker_timeout,
        )

        # Request deduplicator
        self.deduplicator = RequestDeduplicator()

        # Metrics
        self.metrics = {
            "requests": 0,
            "retries": 0,
            "errors": 0,
            "cache_hits": 0,
        }

    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            timeout=self.config.api_timeout,
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()

    def set_api_key(self, api_key: str) -> None:
        """Update API key (for credential rotation).

        Args:
            api_key: New API key
        """
        self.credential_manager.set_api_key(api_key)

    @retry(
        retry=retry_if_exception_type((httpx.HTTPError, EntsoeAPIError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential_jitter(initial=1, max=10),
        reraise=True,
    )
    async def _make_request(
        self,
        params: dict[str, Any],
        method: str = "GET",
    ) -> str:
        """Make HTTP request to ENTSOE API with retry logic.

        Args:
            params: Query parameters
            method: HTTP method

        Returns:
            Response text

        Raises:
            AuthenticationError: Invalid API key
            RateLimitError: Rate limit exceeded
            EntsoeAPIError: Other API errors
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use async with context manager.")

        # Add API key
        api_key = self.credential_manager.get_api_key()
        params["securityToken"] = api_key

        # Rate limiting
        await self.rate_limiter.acquire()

        # Observability hook
        start_time = time.monotonic()
        if self.hooks and hasattr(self.hooks, "on_request_start"):
            await self.hooks.on_request_start(method, sanitize_params(params))

        # Log request (safe mode)
        if self.config.debug_logging:
            logger.debug("api_request", params=sanitize_params(params))

        try:
            response = await self._client.request(
                method,
                self.config.api_base_url,
                params=params,
            )

            # Track metrics
            self.metrics["requests"] += 1
            duration_ms = (time.monotonic() - start_time) * 1000

            # Observability hook
            if self.hooks and hasattr(self.hooks, "on_request_end"):
                await self.hooks.on_request_end(method, duration_ms, response.status_code)

            # Handle errors
            if response.status_code == 401:
                raise AuthenticationError(
                    offending_params=sanitize_params(params),
                    response_text=response.text,
                )
            elif response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                retry_after_int = int(retry_after) if retry_after else None
                raise RateLimitError(
                    retry_after=retry_after_int,
                    offending_params=sanitize_params(params),
                    response_text=response.text,
                )
            elif response.status_code == 400:
                raise InvalidParameterError(
                    f"Invalid parameters: {response.text}",
                    offending_params=sanitize_params(params),
                    response_text=response.text,
                )
            elif response.status_code >= 500:
                raise EntsoeAPIError(
                    f"Server error: {response.status_code}",
                    error_code=str(response.status_code),
                    retryable=True,
                    offending_params=sanitize_params(params),
                    response_text=response.text,
                )

            response.raise_for_status()

            return response.text

        except httpx.HTTPError as e:
            self.metrics["errors"] += 1
            logger.error("http_error", error=str(e))
            raise EntsoeAPIError(
                f"HTTP error: {e}",
                retryable=True,
                offending_params=sanitize_params(params),
            ) from e

    async def query(
        self,
        params: dict[str, Any],
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Execute ENTSOE API query.

        Args:
            params: Query parameters
            fill_missing: Fill missing intervals (default from config)

        Returns:
            EntsoeFrame with data and metadata

        Raises:
            CircuitBreakerOpenError: Circuit breaker is open
            EntsoeAPIError: API or parsing errors
        """
        if fill_missing is None:
            fill_missing = self.config.fill_missing

        # Request deduplication
        async def fetch():
            # Circuit breaker protection
            return await self.circuit_breaker.call(self._make_request, params)

        xml_response = await self.deduplicator.get_or_fetch(params, fetch)

        # Parse response
        try:
            frame = parse_entsoe_xml(
                xml_response,
                fill_missing=fill_missing,
                strict_schema=self.config.strict_schema,
            )

            # Check if empty
            if frame.df.is_empty():
                raise NoDataError(
                    "No data available for query",
                    offending_params=sanitize_params(params),
                )

            return frame

        except ParseError as e:
            if self.hooks and hasattr(self.hooks, "on_parse_error"):
                await self.hooks.on_parse_error(xml_response, e)
            raise

    # Convenience methods for common queries

    async def get_day_ahead_prices(
        self,
        area: str,
        start: datetime | str,
        end: datetime | str,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get day-ahead electricity prices.

        Args:
            area: Area code or country code (e.g., "DE", "FR", Area.DE_LU)
            start: Start datetime or ISO string
            end: End datetime or ISO string
            fill_missing: Fill missing intervals

        Returns:
            EntsoeFrame with price data
        """
        from sc_entsoe.api.prices import build_day_ahead_prices_params

        params = build_day_ahead_prices_params(area, start, end)
        return await self.query(params, fill_missing=fill_missing)

    async def get_generation_actual(
        self,
        area: str,
        start: datetime | str,
        end: datetime | str,
        psr_type: str | None = None,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get actual generation data.

        Args:
            area: Area code or country code
            start: Start datetime or ISO string
            end: End datetime or ISO string
            psr_type: Power system resource type (optional, e.g., PSRType.SOLAR)
            fill_missing: Fill missing intervals

        Returns:
            EntsoeFrame with generation data
        """
        from sc_entsoe.api.generation import build_generation_actual_params

        params = build_generation_actual_params(area, start, end, psr_type)
        return await self.query(params, fill_missing=fill_missing)

    async def get_generation_forecast(
        self,
        area: str,
        start: datetime | str,
        end: datetime | str,
        psr_type: str | None = None,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get generation forecast data.

        Args:
            area: Area code or country code
            start: Start datetime or ISO string
            end: End datetime or ISO string
            psr_type: Power system resource type (optional)
            fill_missing: Fill missing intervals

        Returns:
            EntsoeFrame with forecast data
        """
        from sc_entsoe.api.generation import build_generation_forecast_params

        params = build_generation_forecast_params(area, start, end, psr_type)
        return await self.query(params, fill_missing=fill_missing)

    # Load methods

    async def get_load_actual(
        self,
        area: str,
        start: datetime | str,
        end: datetime | str,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get actual total load data.

        Args:
            area: Area code or country code
            start: Start datetime or ISO string
            end: End datetime or ISO string
            fill_missing: Fill missing intervals

        Returns:
            EntsoeFrame with load data
        """
        from sc_entsoe.api.load import build_load_actual_params

        params = build_load_actual_params(area, start, end)
        return await self.query(params, fill_missing=fill_missing)

    async def get_load_forecast(
        self,
        area: str,
        start: datetime | str,
        end: datetime | str,
        process_type: str = "A01",  # Day-ahead
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get load forecast data.

        Args:
            area: Area code or country code
            start: Start datetime or ISO string
            end: End datetime or ISO string
            process_type: Forecast type (A01=day-ahead, A31=week-ahead, A32=month-ahead)
            fill_missing: Fill missing intervals

        Returns:
            EntsoeFrame with forecast data
        """
        from sc_entsoe.api.load import build_load_forecast_params

        params = build_load_forecast_params(area, start, end, process_type)
        return await self.query(params, fill_missing=fill_missing)

    # Transmission methods

    async def get_crossborder_flows(
        self,
        from_area: str,
        to_area: str,
        start: datetime | str,
        end: datetime | str,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get cross-border physical flows.

        Args:
            from_area: Source area code or country code
            to_area: Destination area code or country code
            start: Start datetime or ISO string
            end: End datetime or ISO string
            fill_missing: Fill missing intervals

        Returns:
            EntsoeFrame with flow data
        """
        from sc_entsoe.api.transmission import build_crossborder_flows_params

        params = build_crossborder_flows_params(from_area, to_area, start, end)
        return await self.query(params, fill_missing=fill_missing)

    async def get_scheduled_exchanges(
        self,
        from_area: str,
        to_area: str,
        start: datetime | str,
        end: datetime | str,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get scheduled commercial exchanges.

        Args:
            from_area: Source area code or country code
            to_area: Destination area code or country code
            start: Start datetime or ISO string
            end: End datetime or ISO string
            fill_missing: Fill missing intervals

        Returns:
            EntsoeFrame with exchange data
        """
        from sc_entsoe.api.transmission import build_scheduled_exchanges_params

        params = build_scheduled_exchanges_params(from_area, to_area, start, end)
        return await self.query(params, fill_missing=fill_missing)

    async def get_transmission_capacity(
        self,
        from_area: str,
        to_area: str,
        start: datetime | str,
        end: datetime | str,
        contract_type: str = "A01",  # Day-ahead
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get available transfer capacity.

        Args:
            from_area: Source area code or country code
            to_area: Destination area code or country code
            start: Start datetime or ISO string
            end: End datetime or ISO string
            contract_type: Contract type (A01=day-ahead, A02=intraday)
            fill_missing: Fill missing intervals

        Returns:
            EntsoeFrame with capacity data
        """
        from sc_entsoe.api.transmission import build_transmission_capacity_params

        params = build_transmission_capacity_params(from_area, to_area, start, end, contract_type)
        return await self.query(params, fill_missing=fill_missing)

    # Balancing methods

    async def get_imbalance_prices(
        self,
        area: str,
        start: datetime | str,
        end: datetime | str,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get imbalance prices.

        Args:
            area: Area code or country code
            start: Start datetime or ISO string
            end: End datetime or ISO string
            fill_missing: Fill missing intervals

        Returns:
            EntsoeFrame with imbalance price data
        """
        from sc_entsoe.api.prices import build_imbalance_prices_params

        params = build_imbalance_prices_params(area, start, end)
        return await self.query(params, fill_missing=fill_missing)

    async def get_procured_balancing_capacity(
        self,
        area: str,
        start: datetime | str,
        end: datetime | str,
        process_type: str = "A01",  # Day-ahead
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get procured balancing capacity.

        Args:
            area: Area code or country code
            start: Start datetime or ISO string
            end: End datetime or ISO string
            process_type: Process type (A01=day-ahead, A31=week-ahead)
            fill_missing: Fill missing intervals

        Returns:
            EntsoeFrame with capacity data
        """
        from sc_entsoe.api.balancing import build_procured_balancing_capacity_params

        params = build_procured_balancing_capacity_params(area, start, end, process_type)
        return await self.query(params, fill_missing=fill_missing)

    async def get_activated_balancing_energy(
        self,
        area: str,
        start: datetime | str,
        end: datetime | str,
        business_type: str = "A95",  # Frequency restoration reserve
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get activated balancing energy.

        Args:
            area: Area code or country code
            start: Start datetime or ISO string
            end: End datetime or ISO string
            business_type: Business type (A95=FRR, A96=RR)
            fill_missing: Fill missing intervals

        Returns:
            EntsoeFrame with activated energy data
        """
        from sc_entsoe.api.balancing import build_activated_balancing_energy_params

        params = build_activated_balancing_energy_params(area, start, end, business_type)
        return await self.query(params, fill_missing=fill_missing)

    async def get_imbalance_volumes(
        self,
        area: str,
        start: datetime | str,
        end: datetime | str,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get system imbalance volumes.

        Args:
            area: Area code or country code
            start: Start datetime or ISO string
            end: End datetime or ISO string
            fill_missing: Fill missing intervals

        Returns:
            EntsoeFrame with imbalance volume data
        """
        from sc_entsoe.api.balancing import build_imbalance_volumes_params

        params = build_imbalance_volumes_params(area, start, end)
        return await self.query(params, fill_missing=fill_missing)

    # Generation - Extended methods

    async def get_wind_solar_forecast(
        self,
        area: str,
        start: datetime | str,
        end: datetime | str,
        psr_type: str | None = None,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get wind and solar forecast.

        Args:
            area: Area code or country code
            start: Start datetime or ISO string
            end: End datetime or ISO string
            psr_type: Power system resource type (B16=Solar, B18=Wind Offshore, B19=Wind Onshore)
            fill_missing: Fill missing intervals

        Returns:
            EntsoeFrame with forecast data
        """
        from sc_entsoe.api.generation import build_wind_solar_forecast_params

        params = build_wind_solar_forecast_params(area, start, end, psr_type)
        return await self.query(params, fill_missing=fill_missing)

    async def get_intraday_wind_solar_forecast(
        self,
        area: str,
        start: datetime | str,
        end: datetime | str,
        psr_type: str | None = None,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get intraday wind and solar forecast.

        Args:
            area: Area code or country code
            start: Start datetime or ISO string
            end: End datetime or ISO string
            psr_type: Power system resource type (B16=Solar, B18=Wind Offshore, B19=Wind Onshore)
            fill_missing: Fill missing intervals

        Returns:
            EntsoeFrame with intraday forecast data
        """
        from sc_entsoe.api.generation import build_intraday_wind_solar_forecast_params

        params = build_intraday_wind_solar_forecast_params(area, start, end, psr_type)
        return await self.query(params, fill_missing=fill_missing)

    async def get_generation_per_plant(
        self,
        area: str,
        start: datetime | str,
        end: datetime | str,
        psr_type: str | None = None,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get actual generation per plant.

        Args:
            area: Area code or country code
            start: Start datetime or ISO string
            end: End datetime or ISO string
            psr_type: Power system resource type (optional)
            fill_missing: Fill missing intervals

        Returns:
            EntsoeFrame with per-plant generation data
        """
        from sc_entsoe.api.generation import build_generation_per_plant_params

        params = build_generation_per_plant_params(area, start, end, psr_type)
        return await self.query(params, fill_missing=fill_missing)

    async def get_installed_capacity(
        self,
        area: str,
        start: datetime | str,
        end: datetime | str,
        psr_type: str | None = None,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get installed generation capacity per type.

        Args:
            area: Area code or country code
            start: Start datetime or ISO string
            end: End datetime or ISO string
            psr_type: Power system resource type (optional)
            fill_missing: Fill missing intervals

        Returns:
            EntsoeFrame with installed capacity data
        """
        from sc_entsoe.api.generation import build_installed_capacity_params

        params = build_installed_capacity_params(area, start, end, psr_type)
        return await self.query(params, fill_missing=fill_missing)

    async def get_installed_capacity_per_unit(
        self,
        area: str,
        start: datetime | str,
        end: datetime | str,
        psr_type: str | None = None,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get installed generation capacity per unit.

        Args:
            area: Area code or country code
            start: Start datetime or ISO string
            end: End datetime or ISO string
            psr_type: Power system resource type (optional)
            fill_missing: Fill missing intervals

        Returns:
            EntsoeFrame with per-unit capacity data
        """
        from sc_entsoe.api.generation import build_installed_capacity_per_unit_params

        params = build_installed_capacity_per_unit_params(area, start, end, psr_type)
        return await self.query(params, fill_missing=fill_missing)

    # Network & Market methods

    async def get_net_position(
        self,
        area: str,
        start: datetime | str,
        end: datetime | str,
        dayahead: bool = True,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get net position (day-ahead or intraday).

        Args:
            area: Area code or country code
            start: Start datetime or ISO string
            end: End datetime or ISO string
            dayahead: True for day-ahead, False for intraday
            fill_missing: Fill missing intervals

        Returns:
            EntsoeFrame with net position data
        """
        from sc_entsoe.api.network import build_net_position_params

        params = build_net_position_params(area, start, end, dayahead)
        return await self.query(params, fill_missing=fill_missing)

    async def get_aggregated_bids(
        self,
        area: str,
        start: datetime | str,
        end: datetime | str,
        process_type: str = "A01",
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get aggregated bids.

        Args:
            area: Area code or country code
            start: Start datetime or ISO string
            end: End datetime or ISO string
            process_type: Process type (A01=day-ahead, A18=intraday)
            fill_missing: Fill missing intervals

        Returns:
            EntsoeFrame with aggregated bids data
        """
        from sc_entsoe.api.network import build_aggregated_bids_params

        params = build_aggregated_bids_params(area, start, end, process_type)
        return await self.query(params, fill_missing=fill_missing)

    # Transmission - Extended NTC methods

    async def get_net_transfer_capacity_dayahead(
        self,
        from_area: str,
        to_area: str,
        start: datetime | str,
        end: datetime | str,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get day-ahead net transfer capacity.

        Args:
            from_area: Source area
            to_area: Destination area
            start: Start datetime or ISO string
            end: End datetime or ISO string
            fill_missing: Fill missing intervals

        Returns:
            EntsoeFrame with NTC data
        """
        from sc_entsoe.api.transmission import build_net_transfer_capacity_dayahead_params

        params = build_net_transfer_capacity_dayahead_params(from_area, to_area, start, end)
        return await self.query(params, fill_missing=fill_missing)

    async def get_net_transfer_capacity_weekahead(
        self,
        from_area: str,
        to_area: str,
        start: datetime | str,
        end: datetime | str,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get week-ahead net transfer capacity.

        Args:
            from_area: Source area
            to_area: Destination area
            start: Start datetime or ISO string
            end: End datetime or ISO string
            fill_missing: Fill missing intervals

        Returns:
            EntsoeFrame with NTC data
        """
        from sc_entsoe.api.transmission import build_net_transfer_capacity_weekahead_params

        params = build_net_transfer_capacity_weekahead_params(from_area, to_area, start, end)
        return await self.query(params, fill_missing=fill_missing)

    async def get_net_transfer_capacity_monthahead(
        self,
        from_area: str,
        to_area: str,
        start: datetime | str,
        end: datetime | str,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get month-ahead net transfer capacity.

        Args:
            from_area: Source area
            to_area: Destination area
            start: Start datetime or ISO string
            end: End datetime or ISO string
            fill_missing: Fill missing intervals

        Returns:
            EntsoeFrame with NTC data
        """
        from sc_entsoe.api.transmission import build_net_transfer_capacity_monthahead_params

        params = build_net_transfer_capacity_monthahead_params(from_area, to_area, start, end)
        return await self.query(params, fill_missing=fill_missing)

    async def get_net_transfer_capacity_yearahead(
        self,
        from_area: str,
        to_area: str,
        start: datetime | str,
        end: datetime | str,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get year-ahead net transfer capacity.

        Args:
            from_area: Source area
            to_area: Destination area
            start: Start datetime or ISO string
            end: End datetime or ISO string
            fill_missing: Fill missing intervals

        Returns:
            EntsoeFrame with NTC data
        """
        from sc_entsoe.api.transmission import build_net_transfer_capacity_yearahead_params

        params = build_net_transfer_capacity_yearahead_params(from_area, to_area, start, end)
        return await self.query(params, fill_missing=fill_missing)

    async def get_intraday_offered_capacity(
        self,
        from_area: str,
        to_area: str,
        start: datetime | str,
        end: datetime | str,
        implicit: bool = True,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get intraday offered capacity.

        Args:
            from_area: Source area
            to_area: Destination area
            start: Start datetime or ISO string
            end: End datetime or ISO string
            implicit: True for implicit auction, False for explicit
            fill_missing: Fill missing intervals

        Returns:
            EntsoeFrame with offered capacity data
        """
        from sc_entsoe.api.transmission import build_intraday_offered_capacity_params

        params = build_intraday_offered_capacity_params(from_area, to_area, start, end, implicit)
        return await self.query(params, fill_missing=fill_missing)

    async def get_offered_capacity(
        self,
        from_area: str,
        to_area: str,
        start: datetime | str,
        end: datetime | str,
        contract_type: str = "A01",
        implicit: bool = True,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get offered capacity.

        Args:
            from_area: Source area
            to_area: Destination area
            start: Start datetime or ISO string
            end: End datetime or ISO string
            contract_type: Contract market agreement type
            implicit: True for implicit auction, False for explicit
            fill_missing: Fill missing intervals

        Returns:
            EntsoeFrame with offered capacity data
        """
        from sc_entsoe.api.transmission import build_offered_capacity_params

        params = build_offered_capacity_params(
            from_area, to_area, start, end, contract_type, implicit
        )
        return await self.query(params, fill_missing=fill_missing)

    # Balancing - Extended reserve methods

    async def get_contracted_reserve_prices(
        self,
        area: str,
        start: datetime | str,
        end: datetime | str,
        type_marketagreement_type: str,
        psr_type: str | None = None,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get contracted reserve prices.

        Args:
            area: Area code or country code
            start: Start datetime or ISO string
            end: End datetime or ISO string
            type_marketagreement_type: Type of reserves
            psr_type: Power system resource type (optional)
            fill_missing: Fill missing intervals

        Returns:
            EntsoeFrame with reserve price data
        """
        from sc_entsoe.api.balancing import build_contracted_reserve_prices_params

        params = build_contracted_reserve_prices_params(
            area, start, end, type_marketagreement_type, psr_type
        )
        return await self.query(params, fill_missing=fill_missing)

    async def get_contracted_reserve_amount(
        self,
        area: str,
        start: datetime | str,
        end: datetime | str,
        type_marketagreement_type: str,
        psr_type: str | None = None,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get contracted reserve amounts.

        Args:
            area: Area code or country code
            start: Start datetime or ISO string
            end: End datetime or ISO string
            type_marketagreement_type: Type of reserves
            psr_type: Power system resource type (optional)
            fill_missing: Fill missing intervals

        Returns:
            EntsoeFrame with reserve amount data
        """
        from sc_entsoe.api.balancing import build_contracted_reserve_amount_params

        params = build_contracted_reserve_amount_params(
            area, start, end, type_marketagreement_type, psr_type
        )
        return await self.query(params, fill_missing=fill_missing)

    async def get_activated_balancing_energy_prices(
        self,
        area: str,
        start: datetime | str,
        end: datetime | str,
        process_type: str = "A16",
        psr_type: str | None = None,
        business_type: str | None = None,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get activated balancing energy prices.

        Args:
            area: Area code or country code
            start: Start datetime or ISO string
            end: End datetime or ISO string
            process_type: Process type (default A16=Realised)
            psr_type: Power system resource type (optional)
            business_type: Business type (optional)
            fill_missing: Fill missing intervals

        Returns:
            EntsoeFrame with activated balancing price data
        """
        from sc_entsoe.api.balancing import build_activated_balancing_energy_prices_params

        params = build_activated_balancing_energy_prices_params(
            area, start, end, process_type, psr_type, business_type
        )
        return await self.query(params, fill_missing=fill_missing)

    async def get_balancing_energy_prices(
        self,
        area: str,
        start: datetime | str,
        end: datetime | str,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get balancing energy prices.

        Args:
            area: Area code or country code
            start: Start datetime or ISO string
            end: End datetime or ISO string
            fill_missing: Fill missing intervals

        Returns:
            EntsoeFrame with balancing energy price data
        """
        from sc_entsoe.api.balancing import build_balancing_energy_prices_params

        params = build_balancing_energy_prices_params(area, start, end)
        return await self.query(params, fill_missing=fill_missing)

    # Hydro methods

    async def get_aggregate_water_reservoirs(
        self,
        area: str,
        start: datetime | str,
        end: datetime | str,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get aggregate water reservoirs and hydro storage.

        Args:
            area: Area code or country code
            start: Start datetime or ISO string
            end: End datetime or ISO string
            fill_missing: Fill missing intervals

        Returns:
            EntsoeFrame with water reservoir data
        """
        from sc_entsoe.api.hydro import build_aggregate_water_reservoirs_params

        params = build_aggregate_water_reservoirs_params(area, start, end)
        return await self.query(params, fill_missing=fill_missing)

    # Unavailability methods

    async def get_unavailability_generation(
        self,
        area: str,
        start: datetime | str,
        end: datetime | str,
        docstatus: str | None = None,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get unavailability of generation units.

        Args:
            area: Area code or country code
            start: Start datetime or ISO string
            end: End datetime or ISO string
            docstatus: Document status (optional, e.g., A05=Active)
            fill_missing: Fill missing intervals

        Returns:
            EntsoeFrame with generation unavailability data
        """
        from sc_entsoe.api.unavailability import build_unavailability_generation_params

        params = build_unavailability_generation_params(area, start, end, docstatus)
        return await self.query(params, fill_missing=fill_missing)

    async def get_unavailability_production(
        self,
        area: str,
        start: datetime | str,
        end: datetime | str,
        docstatus: str | None = None,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get unavailability of production units.

        Args:
            area: Area code or country code
            start: Start datetime or ISO string
            end: End datetime or ISO string
            docstatus: Document status (optional)
            fill_missing: Fill missing intervals

        Returns:
            EntsoeFrame with production unavailability data
        """
        from sc_entsoe.api.unavailability import build_unavailability_production_params

        params = build_unavailability_production_params(area, start, end, docstatus)
        return await self.query(params, fill_missing=fill_missing)

    async def get_unavailability_transmission(
        self,
        from_area: str,
        to_area: str,
        start: datetime | str,
        end: datetime | str,
        docstatus: str | None = None,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get unavailability of transmission infrastructure.

        Args:
            from_area: Source area
            to_area: Destination area
            start: Start datetime or ISO string
            end: End datetime or ISO string
            docstatus: Document status (optional)
            fill_missing: Fill missing intervals

        Returns:
            EntsoeFrame with transmission unavailability data
        """
        from sc_entsoe.api.unavailability import build_unavailability_transmission_params

        params = build_unavailability_transmission_params(from_area, to_area, start, end, docstatus)
        return await self.query(params, fill_missing=fill_missing)

    async def get_unavailability_offshore_grid(
        self,
        area: str,
        start: datetime | str,
        end: datetime | str,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get unavailability of offshore grid infrastructure.

        Args:
            area: Area code or country code
            start: Start datetime or ISO string
            end: End datetime or ISO string
            fill_missing: Fill missing intervals

        Returns:
            EntsoeFrame with offshore grid unavailability data
        """
        from sc_entsoe.api.unavailability import build_unavailability_offshore_grid_params

        params = build_unavailability_offshore_grid_params(area, start, end)
        return await self.query(params, fill_missing=fill_missing)

    async def get_withdrawn_unavailability_generation(
        self,
        area: str,
        start: datetime | str,
        end: datetime | str,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get withdrawn unavailability of generation units.

        Args:
            area: Area code or country code
            start: Start datetime or ISO string
            end: End datetime or ISO string
            fill_missing: Fill missing intervals

        Returns:
            EntsoeFrame with withdrawn unavailability data
        """
        from sc_entsoe.api.unavailability import build_withdrawn_unavailability_generation_params

        params = build_withdrawn_unavailability_generation_params(area, start, end)
        return await self.query(params, fill_missing=fill_missing)
