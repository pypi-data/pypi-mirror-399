"""Price data API methods."""

from datetime import datetime
from typing import Any

from sc_entsoe.models import DocumentType, MarketAgreementType
from sc_entsoe.parsers.converters import get_area_code, normalize_timestamp


def build_day_ahead_prices_params(
    area: str,
    start: datetime | str,
    end: datetime | str,
) -> dict[str, Any]:
    """Build parameters for day-ahead prices query.

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
        "documentType": DocumentType.DAY_AHEAD_PRICES.value,
        "in_Domain": get_area_code(area),
        "out_Domain": get_area_code(area),
        "contract_MarketAgreement.type": MarketAgreementType.DAILY.value,
        "periodStart": start_dt.strftime("%Y%m%d%H%M"),
        "periodEnd": end_dt.strftime("%Y%m%d%H%M"),
    }


def build_imbalance_prices_params(
    area: str,
    start: datetime | str,
    end: datetime | str,
) -> dict[str, Any]:
    """Build parameters for imbalance prices query.

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
        "documentType": DocumentType.IMBALANCE_PRICES.value,
        "controlArea_Domain": get_area_code(area),
        "periodStart": start_dt.strftime("%Y%m%d%H%M"),
        "periodEnd": end_dt.strftime("%Y%m%d%H%M"),
    }
