"""Synchronous wrapper for AsyncEntsoeClient."""

import asyncio
from typing import Any

from sc_entsoe.client import AsyncEntsoeClient
from sc_entsoe.config import EntsoeConfig
from sc_entsoe.models import EntsoeFrame


class EntsoeClient:
    """Synchronous ENTSOE API client (wrapper around async client)."""

    def __init__(
        self,
        api_key: str | None = None,
        config: EntsoeConfig | None = None,
        hooks: Any | None = None,
    ):
        """Initialize synchronous ENTSOE client.

        Args:
            api_key: ENTSOE API key (optional, can load from env)
            config: Configuration object
            hooks: Observability hooks
        """
        self._async_client = AsyncEntsoeClient(api_key=api_key, config=config, hooks=hooks)
        self._loop: asyncio.AbstractEventLoop | None = None

    def __enter__(self):
        """Context manager entry."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._async_client.__aenter__())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._loop:
            self._loop.run_until_complete(self._async_client.__aexit__(exc_type, exc_val, exc_tb))
            self._loop.close()
            self._loop = None

    def set_api_key(self, api_key: str) -> None:
        """Update API key (for credential rotation).

        Args:
            api_key: New API key
        """
        self._async_client.set_api_key(api_key)

    def query(self, params: dict[str, Any], fill_missing: bool | None = None) -> EntsoeFrame:
        """Execute ENTSOE API query (synchronous).

        Args:
            params: Query parameters
            fill_missing: Fill missing intervals

        Returns:
            EntsoeFrame with data and metadata
        """
        if not self._loop:
            raise RuntimeError("Client not initialized. Use with context manager.")

        return self._loop.run_until_complete(self._async_client.query(params, fill_missing))

    # Prices

    def get_day_ahead_prices(
        self,
        area: str,
        start: Any,
        end: Any,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get day-ahead prices (synchronous)."""
        if not self._loop:
            raise RuntimeError("Client not initialized. Use with context manager.")
        return self._loop.run_until_complete(
            self._async_client.get_day_ahead_prices(area, start, end, fill_missing)
        )

    def get_imbalance_prices(
        self,
        area: str,
        start: Any,
        end: Any,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get imbalance prices (synchronous)."""
        if not self._loop:
            raise RuntimeError("Client not initialized. Use with context manager.")
        return self._loop.run_until_complete(
            self._async_client.get_imbalance_prices(area, start, end, fill_missing)
        )

    # Generation

    def get_generation_actual(
        self,
        area: str,
        start: Any,
        end: Any,
        psr_type: str | None = None,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get actual generation (synchronous)."""
        if not self._loop:
            raise RuntimeError("Client not initialized. Use with context manager.")
        return self._loop.run_until_complete(
            self._async_client.get_generation_actual(area, start, end, psr_type, fill_missing)
        )

    def get_generation_forecast(
        self,
        area: str,
        start: Any,
        end: Any,
        psr_type: str | None = None,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get generation forecast (synchronous)."""
        if not self._loop:
            raise RuntimeError("Client not initialized. Use with context manager.")
        return self._loop.run_until_complete(
            self._async_client.get_generation_forecast(area, start, end, psr_type, fill_missing)
        )

    def get_wind_solar_forecast(
        self,
        area: str,
        start: Any,
        end: Any,
        psr_type: str | None = None,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get wind & solar forecast (synchronous)."""
        if not self._loop:
            raise RuntimeError("Client not initialized. Use with context manager.")
        return self._loop.run_until_complete(
            self._async_client.get_wind_solar_forecast(area, start, end, psr_type, fill_missing)
        )

    def get_intraday_wind_solar_forecast(
        self,
        area: str,
        start: Any,
        end: Any,
        psr_type: str | None = None,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get intraday wind & solar forecast (synchronous)."""
        if not self._loop:
            raise RuntimeError("Client not initialized. Use with context manager.")
        return self._loop.run_until_complete(
            self._async_client.get_intraday_wind_solar_forecast(
                area, start, end, psr_type, fill_missing
            )
        )

    def get_generation_per_plant(
        self,
        area: str,
        start: Any,
        end: Any,
        psr_type: str | None = None,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get generation per plant (synchronous)."""
        if not self._loop:
            raise RuntimeError("Client not initialized. Use with context manager.")
        return self._loop.run_until_complete(
            self._async_client.get_generation_per_plant(area, start, end, psr_type, fill_missing)
        )

    def get_installed_capacity(
        self,
        area: str,
        start: Any,
        end: Any,
        psr_type: str | None = None,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get installed capacity (synchronous)."""
        if not self._loop:
            raise RuntimeError("Client not initialized. Use with context manager.")
        return self._loop.run_until_complete(
            self._async_client.get_installed_capacity(area, start, end, psr_type, fill_missing)
        )

    def get_installed_capacity_per_unit(
        self,
        area: str,
        start: Any,
        end: Any,
        psr_type: str | None = None,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get installed capacity per unit (synchronous)."""
        if not self._loop:
            raise RuntimeError("Client not initialized. Use with context manager.")
        return self._loop.run_until_complete(
            self._async_client.get_installed_capacity_per_unit(
                area, start, end, psr_type, fill_missing
            )
        )

    # Load

    def get_load_actual(
        self,
        area: str,
        start: Any,
        end: Any,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get actual load (synchronous)."""
        if not self._loop:
            raise RuntimeError("Client not initialized. Use with context manager.")
        return self._loop.run_until_complete(
            self._async_client.get_load_actual(area, start, end, fill_missing)
        )

    def get_load_forecast(
        self,
        area: str,
        start: Any,
        end: Any,
        process_type: str = "A01",
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get load forecast (synchronous)."""
        if not self._loop:
            raise RuntimeError("Client not initialized. Use with context manager.")
        return self._loop.run_until_complete(
            self._async_client.get_load_forecast(area, start, end, process_type, fill_missing)
        )

    # Network & Market

    def get_net_position(
        self,
        area: str,
        start: Any,
        end: Any,
        dayahead: bool = True,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get net position (synchronous)."""
        if not self._loop:
            raise RuntimeError("Client not initialized. Use with context manager.")
        return self._loop.run_until_complete(
            self._async_client.get_net_position(area, start, end, dayahead, fill_missing)
        )

    def get_aggregated_bids(
        self,
        area: str,
        start: Any,
        end: Any,
        process_type: str = "A01",
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get aggregated bids (synchronous)."""
        if not self._loop:
            raise RuntimeError("Client not initialized. Use with context manager.")
        return self._loop.run_until_complete(
            self._async_client.get_aggregated_bids(area, start, end, process_type, fill_missing)
        )

    # Transmission

    def get_crossborder_flows(
        self,
        from_area: str,
        to_area: str,
        start: Any,
        end: Any,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get cross-border flows (synchronous)."""
        if not self._loop:
            raise RuntimeError("Client not initialized. Use with context manager.")
        return self._loop.run_until_complete(
            self._async_client.get_crossborder_flows(from_area, to_area, start, end, fill_missing)
        )

    def get_scheduled_exchanges(
        self,
        from_area: str,
        to_area: str,
        start: Any,
        end: Any,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get scheduled exchanges (synchronous)."""
        if not self._loop:
            raise RuntimeError("Client not initialized. Use with context manager.")
        return self._loop.run_until_complete(
            self._async_client.get_scheduled_exchanges(from_area, to_area, start, end, fill_missing)
        )

    def get_transmission_capacity(
        self,
        from_area: str,
        to_area: str,
        start: Any,
        end: Any,
        contract_type: str = "A01",
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get transmission capacity (synchronous)."""
        if not self._loop:
            raise RuntimeError("Client not initialized. Use with context manager.")
        return self._loop.run_until_complete(
            self._async_client.get_transmission_capacity(
                from_area, to_area, start, end, contract_type, fill_missing
            )
        )

    def get_net_transfer_capacity_dayahead(
        self,
        from_area: str,
        to_area: str,
        start: Any,
        end: Any,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get day-ahead NTC (synchronous)."""
        if not self._loop:
            raise RuntimeError("Client not initialized. Use with context manager.")
        return self._loop.run_until_complete(
            self._async_client.get_net_transfer_capacity_dayahead(
                from_area, to_area, start, end, fill_missing
            )
        )

    def get_net_transfer_capacity_weekahead(
        self,
        from_area: str,
        to_area: str,
        start: Any,
        end: Any,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get week-ahead NTC (synchronous)."""
        if not self._loop:
            raise RuntimeError("Client not initialized. Use with context manager.")
        return self._loop.run_until_complete(
            self._async_client.get_net_transfer_capacity_weekahead(
                from_area, to_area, start, end, fill_missing
            )
        )

    def get_net_transfer_capacity_monthahead(
        self,
        from_area: str,
        to_area: str,
        start: Any,
        end: Any,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get month-ahead NTC (synchronous)."""
        if not self._loop:
            raise RuntimeError("Client not initialized. Use with context manager.")
        return self._loop.run_until_complete(
            self._async_client.get_net_transfer_capacity_monthahead(
                from_area, to_area, start, end, fill_missing
            )
        )

    def get_net_transfer_capacity_yearahead(
        self,
        from_area: str,
        to_area: str,
        start: Any,
        end: Any,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get year-ahead NTC (synchronous)."""
        if not self._loop:
            raise RuntimeError("Client not initialized. Use with context manager.")
        return self._loop.run_until_complete(
            self._async_client.get_net_transfer_capacity_yearahead(
                from_area, to_area, start, end, fill_missing
            )
        )

    def get_intraday_offered_capacity(
        self,
        from_area: str,
        to_area: str,
        start: Any,
        end: Any,
        implicit: bool = True,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get intraday offered capacity (synchronous)."""
        if not self._loop:
            raise RuntimeError("Client not initialized. Use with context manager.")
        return self._loop.run_until_complete(
            self._async_client.get_intraday_offered_capacity(
                from_area, to_area, start, end, implicit, fill_missing
            )
        )

    def get_offered_capacity(
        self,
        from_area: str,
        to_area: str,
        start: Any,
        end: Any,
        contract_type: str = "A01",
        implicit: bool = True,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get offered capacity (synchronous)."""
        if not self._loop:
            raise RuntimeError("Client not initialized. Use with context manager.")
        return self._loop.run_until_complete(
            self._async_client.get_offered_capacity(
                from_area, to_area, start, end, contract_type, implicit, fill_missing
            )
        )

    # Balancing

    def get_procured_balancing_capacity(
        self,
        area: str,
        start: Any,
        end: Any,
        process_type: str = "A01",
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get procured balancing capacity (synchronous)."""
        if not self._loop:
            raise RuntimeError("Client not initialized. Use with context manager.")
        return self._loop.run_until_complete(
            self._async_client.get_procured_balancing_capacity(
                area, start, end, process_type, fill_missing
            )
        )

    def get_activated_balancing_energy(
        self,
        area: str,
        start: Any,
        end: Any,
        business_type: str = "A95",
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get activated balancing energy (synchronous)."""
        if not self._loop:
            raise RuntimeError("Client not initialized. Use with context manager.")
        return self._loop.run_until_complete(
            self._async_client.get_activated_balancing_energy(
                area, start, end, business_type, fill_missing
            )
        )

    def get_activated_balancing_energy_prices(
        self,
        area: str,
        start: Any,
        end: Any,
        process_type: str = "A16",
        psr_type: str | None = None,
        business_type: str | None = None,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get activated balancing energy prices (synchronous)."""
        if not self._loop:
            raise RuntimeError("Client not initialized. Use with context manager.")
        return self._loop.run_until_complete(
            self._async_client.get_activated_balancing_energy_prices(
                area, start, end, process_type, psr_type, business_type, fill_missing
            )
        )

    def get_imbalance_volumes(
        self,
        area: str,
        start: Any,
        end: Any,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get imbalance volumes (synchronous)."""
        if not self._loop:
            raise RuntimeError("Client not initialized. Use with context manager.")
        return self._loop.run_until_complete(
            self._async_client.get_imbalance_volumes(area, start, end, fill_missing)
        )

    def get_contracted_reserve_prices(
        self,
        area: str,
        start: Any,
        end: Any,
        type_marketagreement_type: str,
        psr_type: str | None = None,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get contracted reserve prices (synchronous)."""
        if not self._loop:
            raise RuntimeError("Client not initialized. Use with context manager.")
        return self._loop.run_until_complete(
            self._async_client.get_contracted_reserve_prices(
                area, start, end, type_marketagreement_type, psr_type, fill_missing
            )
        )

    def get_contracted_reserve_amount(
        self,
        area: str,
        start: Any,
        end: Any,
        type_marketagreement_type: str,
        psr_type: str | None = None,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get contracted reserve amount (synchronous)."""
        if not self._loop:
            raise RuntimeError("Client not initialized. Use with context manager.")
        return self._loop.run_until_complete(
            self._async_client.get_contracted_reserve_amount(
                area, start, end, type_marketagreement_type, psr_type, fill_missing
            )
        )

    def get_balancing_energy_prices(
        self,
        area: str,
        start: Any,
        end: Any,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get balancing energy prices (synchronous)."""
        if not self._loop:
            raise RuntimeError("Client not initialized. Use with context manager.")
        return self._loop.run_until_complete(
            self._async_client.get_balancing_energy_prices(area, start, end, fill_missing)
        )

    # Hydro

    def get_aggregate_water_reservoirs(
        self,
        area: str,
        start: Any,
        end: Any,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get aggregate water reservoirs (synchronous)."""
        if not self._loop:
            raise RuntimeError("Client not initialized. Use with context manager.")
        return self._loop.run_until_complete(
            self._async_client.get_aggregate_water_reservoirs(area, start, end, fill_missing)
        )

    # Unavailability

    def get_unavailability_generation(
        self,
        area: str,
        start: Any,
        end: Any,
        docstatus: str | None = None,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get unavailability of generation units (synchronous)."""
        if not self._loop:
            raise RuntimeError("Client not initialized. Use with context manager.")
        return self._loop.run_until_complete(
            self._async_client.get_unavailability_generation(
                area, start, end, docstatus, fill_missing
            )
        )

    def get_unavailability_production(
        self,
        area: str,
        start: Any,
        end: Any,
        docstatus: str | None = None,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get unavailability of production units (synchronous)."""
        if not self._loop:
            raise RuntimeError("Client not initialized. Use with context manager.")
        return self._loop.run_until_complete(
            self._async_client.get_unavailability_production(
                area, start, end, docstatus, fill_missing
            )
        )

    def get_unavailability_transmission(
        self,
        from_area: str,
        to_area: str,
        start: Any,
        end: Any,
        docstatus: str | None = None,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get unavailability of transmission (synchronous)."""
        if not self._loop:
            raise RuntimeError("Client not initialized. Use with context manager.")
        return self._loop.run_until_complete(
            self._async_client.get_unavailability_transmission(
                from_area, to_area, start, end, docstatus, fill_missing
            )
        )

    def get_unavailability_offshore_grid(
        self,
        area: str,
        start: Any,
        end: Any,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get unavailability of offshore grid (synchronous)."""
        if not self._loop:
            raise RuntimeError("Client not initialized. Use with context manager.")
        return self._loop.run_until_complete(
            self._async_client.get_unavailability_offshore_grid(area, start, end, fill_missing)
        )

    def get_withdrawn_unavailability_generation(
        self,
        area: str,
        start: Any,
        end: Any,
        fill_missing: bool | None = None,
    ) -> EntsoeFrame:
        """Get withdrawn unavailability of generation (synchronous)."""
        if not self._loop:
            raise RuntimeError("Client not initialized. Use with context manager.")
        return self._loop.run_until_complete(
            self._async_client.get_withdrawn_unavailability_generation(
                area, start, end, fill_missing
            )
        )
