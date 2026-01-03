"""Hydro and water reservoir API methods."""

from datetime import datetime
from typing import Any

from sc_entsoe.models import DocumentType, ProcessType
from sc_entsoe.parsers.converters import get_area_code, normalize_timestamp


def build_aggregate_water_reservoirs_params(
    area: str,
    start: datetime | str,
    end: datetime | str,
) -> dict[str, Any]:
    """Build parameters for aggregate water reservoirs and hydro storage query.

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
        "documentType": DocumentType.RESERVOIR_FILLING.value,
        "processType": ProcessType.REALISED.value,
        "in_Domain": get_area_code(area),
        "periodStart": start_dt.strftime("%Y%m%d%H%M"),
        "periodEnd": end_dt.strftime("%Y%m%d%H%M"),
    }
