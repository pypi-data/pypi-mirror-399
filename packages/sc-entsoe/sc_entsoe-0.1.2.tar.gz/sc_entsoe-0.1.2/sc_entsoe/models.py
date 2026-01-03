"""Data models and enums for ENTSOE API."""

from datetime import datetime
from enum import Enum
from typing import Any

import polars as pl
from pydantic import BaseModel, Field


class Area(str, Enum):
    """ENTSOE bidding zones and control areas (EIC codes)."""

    # Major European areas
    DE_LU = "10Y1001A1001A82H"  # Germany-Luxembourg
    FR = "10YFR-RTE------C"  # France
    NL = "10YNL----------L"  # Netherlands
    BE = "10YBE----------2"  # Belgium
    AT = "10YAT-APG------L"  # Austria
    CH = "10YCH-SWISSGRIDZ"  # Switzerland
    IT_NORTH = "10Y1001A1001A73I"  # Italy North
    ES = "10YES-REE------0"  # Spain
    PT = "10YPT-REN------W"  # Portugal
    DK_1 = "10YDK-1--------W"  # Denmark 1 (West)
    DK_2 = "10YDK-2--------M"  # Denmark 2 (East)
    NO_1 = "10YNO-1--------2"  # Norway 1
    NO_2 = "10YNO-2--------T"  # Norway 2
    NO_3 = "10YNO-3--------J"  # Norway 3
    NO_4 = "10YNO-4--------9"  # Norway 4
    SE_1 = "10Y1001A1001A44P"  # Sweden 1
    SE_2 = "10Y1001A1001A45N"  # Sweden 2
    SE_3 = "10Y1001A1001A46L"  # Sweden 3
    SE_4 = "10Y1001A1001A47J"  # Sweden 4
    FI = "10YFI-1--------U"  # Finland
    PL = "10YPL-AREA-----S"  # Poland
    CZ = "10YCZ-CEPS-----N"  # Czech Republic
    GB = "10YGB----------A"  # Great Britain


class DocumentType(str, Enum):
    """ENTSOE document types."""

    # Prices
    DAY_AHEAD_PRICES = "A44"
    IMBALANCE_PRICES = "A85"

    # Allocation & Positions
    ALLOCATION_RESULT = "A25"  # Net positions
    IMPLICIT_AUCTION_NET_POSITIONS = "A25"
    IMPLICIT_AUCTION_CONGESTION_INCOME = "A93"

    # Load
    SYSTEM_TOTAL_LOAD = "A65"
    ACTUAL_TOTAL_LOAD = "A65"
    DAY_AHEAD_TOTAL_LOAD_FORECAST = "A65"
    WEEK_AHEAD_TOTAL_LOAD_FORECAST = "A65"
    MONTH_AHEAD_TOTAL_LOAD_FORECAST = "A65"
    YEAR_AHEAD_TOTAL_LOAD_FORECAST = "A65"

    # Generation
    ACTUAL_GENERATION_PER_TYPE = "A75"
    AGGREGATED_GENERATION_PER_TYPE = "A75"
    ACTUAL_GENERATION = "A73"  # Actual generation per unit
    GENERATION_FORECAST = "A71"  # Generation forecast
    WIND_SOLAR_FORECAST = "A69"  # Wind and solar forecast
    INSTALLED_GENERATION_CAPACITY_PER_TYPE = "A68"
    RESERVOIR_FILLING = "A72"  # Water reservoirs / hydro storage

    # Transmission
    PHYSICAL_FLOWS = "A11"  # Aggregated energy data report
    FINALISED_SCHEDULE = "A09"  # Scheduled exchanges
    ESTIMATED_NET_TRANSFER_CAPACITY = "A61"  # NTC
    AGREED_CAPACITY = "A31"  # Offered capacity
    CAPACITY_ALLOCATED = "A29"

    # Balancing
    ACQUIRING_SYSTEM_OPERATOR_RESERVE = "A15"  # Procured balancing capacity
    CONTRACTED_RESERVES = "A81"
    ACTIVATED_BALANCING_QUANTITIES = "A83"
    ACTIVATED_BALANCING_PRICES = "A84"
    IMBALANCE_VOLUME = "A86"
    CONTRACTED_RESERVE_PRICES = "A89"

    # Unavailability
    GENERATION_UNAVAILABILITY = "A80"
    PRODUCTION_UNAVAILABILITY = "A77"
    TRANSMISSION_UNAVAILABILITY = "A78"
    OFFSHORE_GRID_UNAVAILABILITY = "A79"

    # Bids
    BID_DOCUMENT = "A24"


class ProcessType(str, Enum):
    """ENTSOE process types."""

    DAY_AHEAD = "A01"
    INTRADAY_INCREMENTAL = "A02"  # Intra day incremental
    REALISED = "A16"
    INTRADAY_TOTAL = "A18"  # Intraday total
    WEEK_AHEAD = "A31"
    MONTH_AHEAD = "A32"
    YEAR_AHEAD = "A33"
    SYNCHRONISATION = "A39"
    INTRADAY_PROCESS = "A40"  # For intraday wind/solar forecasts
    REPLACEMENT_RESERVE = "A46"
    MANUAL_FREQUENCY_RESTORATION_RESERVE = "A47"
    AUTOMATIC_FREQUENCY_RESTORATION_RESERVE = "A51"
    FREQUENCY_CONTAINMENT_RESERVE = "A52"
    FREQUENCY_RESTORATION_RESERVE = "A56"


class BusinessType(str, Enum):
    """ENTSOE business types."""

    PRODUCTION = "A01"
    CONSUMPTION = "A04"
    AGGREGATED_ENERGY_DATA = "A14"
    BALANCE_ENERGY_DEVIATION = "A19"
    GENERAL_CAPACITY_INFORMATION = "A25"
    ALREADY_ALLOCATED_CAPACITY = "A29"
    REQUESTED_CAPACITY = "A43"
    SYSTEM_OPERATOR_REDISPATCHING = "A46"
    PLANNED_MAINTENANCE = "A53"
    UNPLANNED_OUTAGE = "A54"
    MINIMUM_POSSIBLE = "A60"
    MAXIMUM_POSSIBLE = "A61"
    INTERNAL_REDISPATCH = "A85"
    POSITIVE_FORECAST_MARGIN = "A91"
    NEGATIVE_FORECAST_MARGIN = "A92"
    WIND_GENERATION = "A93"
    SOLAR_GENERATION = "A94"
    FREQUENCY_CONTAINMENT_RESERVE = "A95"
    AUTOMATIC_FREQUENCY_RESTORATION_RESERVE = "A96"
    MANUAL_FREQUENCY_RESTORATION_RESERVE = "A97"
    REPLACEMENT_RESERVE = "A98"
    COUNTER_TRADE = "B03"
    CONGESTION_COSTS = "B04"
    CAPACITY_ALLOCATED = "B05"
    AUCTION_REVENUE = "B07"
    TOTAL_NOMINATED_CAPACITY = "B08"
    NET_POSITION = "B09"
    CONGESTION_INCOME = "B10"
    PRODUCTION_UNIT = "B11"
    AREA_CONTROL_ERROR = "B33"
    OFFER = "B74"
    NEED = "B75"
    PROCURED_CAPACITY = "B95"


class MarketAgreementType(str, Enum):
    """ENTSOE contract/market agreement types."""

    DAILY = "A01"  # Day-ahead
    WEEKLY = "A02"
    MONTHLY = "A03"
    YEARLY = "A04"
    TOTAL = "A05"
    LONG_TERM = "A06"
    INTRADAY = "A07"
    HOURLY = "A13"


class AuctionType(str, Enum):
    """ENTSOE auction types."""

    IMPLICIT = "A01"
    EXPLICIT = "A02"


class DocStatus(str, Enum):
    """ENTSOE document status codes."""

    INTERMEDIATE = "A01"
    FINAL = "A02"
    ACTIVE = "A05"
    CANCELLED = "A09"
    WITHDRAWN = "A13"
    ESTIMATED = "X01"


class PSRType(str, Enum):
    """Power System Resource types (generation types)."""

    BIOMASS = "B01"
    FOSSIL_BROWN_COAL = "B02"
    FOSSIL_COAL_DERIVED_GAS = "B03"
    FOSSIL_GAS = "B04"
    FOSSIL_HARD_COAL = "B05"
    FOSSIL_OIL = "B06"
    FOSSIL_OIL_SHALE = "B07"
    FOSSIL_PEAT = "B08"
    GEOTHERMAL = "B09"
    HYDRO_PUMPED_STORAGE = "B10"
    HYDRO_RUN_OF_RIVER = "B11"
    HYDRO_WATER_RESERVOIR = "B12"
    MARINE = "B13"
    NUCLEAR = "B14"
    OTHER_RENEWABLE = "B15"
    SOLAR = "B16"
    WASTE = "B17"
    WIND_OFFSHORE = "B18"
    WIND_ONSHORE = "B19"
    OTHER = "B20"


class Resolution(str, Enum):
    """Time series resolution codes."""

    PT15M = "PT15M"  # 15 minutes
    PT30M = "PT30M"  # 30 minutes
    PT60M = "PT60M"  # 60 minutes (1 hour)
    P1D = "P1D"  # 1 day


class EntsoeFrame(BaseModel):
    """Wrapper around Polars DataFrame with metadata.

    This provides schema guarantees and rich metadata about the query.
    """

    model_config = {"arbitrary_types_allowed": True}

    df: pl.DataFrame = Field(..., description="The actual data as Polars DataFrame")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata about the query and response",
    )

    @property
    def document_type(self) -> str | None:
        """Get document type from metadata."""
        return self.metadata.get("document_type")

    @property
    def resolution(self) -> str | None:
        """Get resolution from metadata."""
        return self.metadata.get("resolution")

    @property
    def area(self) -> str | None:
        """Get area from metadata."""
        return self.metadata.get("area")

    @property
    def start_time(self) -> datetime | None:
        """Get start time from metadata."""
        return self.metadata.get("start_time")

    @property
    def end_time(self) -> datetime | None:
        """Get end time from metadata."""
        return self.metadata.get("end_time")

    def to_pandas(self):
        """Convert to pandas DataFrame for compatibility.

        Returns:
            pandas.DataFrame
        """
        return self.df.to_pandas()

    def __repr__(self) -> str:
        """String representation."""
        meta_str = ", ".join(f"{k}={v}" for k, v in self.metadata.items())
        return f"EntsoeFrame(shape={self.df.shape}, {meta_str})"
