"""Load data API methods."""

from datetime import datetime
from typing import Any

from sc_entsoe.models import DocumentType, ProcessType
from sc_entsoe.parsers.converters import get_area_code, normalize_timestamp


def build_load_actual_params(
    area: str,
    start: datetime | str,
    end: datetime | str,
) -> dict[str, Any]:
    """Build parameters for actual total load query.

    Args:
        area: Area code or country code
        start: Start datetime
        end: End datetime

    Returns:
        Query parameters dictionary
    """
    start_dt = normalize_timestamp(start) if isinstance(start, str) else start
    end_dt = normalize_timestamp(end) if isinstance(end, str) else end

    return {
        "documentType": DocumentType.ACTUAL_TOTAL_LOAD.value,
        "processType": ProcessType.REALISED.value,
        "outBiddingZone_Domain": get_area_code(area),
        "periodStart": start_dt.strftime("%Y%m%d%H%M"),
        "periodEnd": end_dt.strftime("%Y%m%d%H%M"),
    }


def build_load_forecast_params(
    area: str,
    start: datetime | str,
    end: datetime | str,
    process_type: ProcessType | str = ProcessType.DAY_AHEAD,
) -> dict[str, Any]:
    """Build parameters for load forecast query.

    Args:
        area: Area code or country code
        start: Start datetime
        end: End datetime
        process_type: Forecast type (day-ahead, week-ahead, month-ahead, year-ahead)

    Returns:
        Query parameters dictionary
    """
    start_dt = normalize_timestamp(start) if isinstance(start, str) else start
    end_dt = normalize_timestamp(end) if isinstance(end, str) else end

    process_value = process_type.value if isinstance(process_type, ProcessType) else process_type

    return {
        "documentType": DocumentType.DAY_AHEAD_TOTAL_LOAD_FORECAST.value,
        "processType": process_value,
        "outBiddingZone_Domain": get_area_code(area),
        "periodStart": start_dt.strftime("%Y%m%d%H%M"),
        "periodEnd": end_dt.strftime("%Y%m%d%H%M"),
    }
