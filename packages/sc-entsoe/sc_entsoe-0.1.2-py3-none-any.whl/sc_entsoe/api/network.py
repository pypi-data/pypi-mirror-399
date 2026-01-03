"""Network and market position API methods."""

from datetime import datetime
from typing import Any

from sc_entsoe.models import (
    BusinessType,
    DocumentType,
    MarketAgreementType,
    ProcessType,
)
from sc_entsoe.parsers.converters import get_area_code, normalize_timestamp


def build_net_position_params(
    area: str,
    start: datetime | str,
    end: datetime | str,
    dayahead: bool = True,
) -> dict[str, Any]:
    """Build parameters for net position query.

    Args:
        area: Area code or country code
        start: Start datetime
        end: End datetime
        dayahead: True for day-ahead, False for intraday

    Returns:
        Query parameters dictionary
    """
    start_dt = normalize_timestamp(start) if isinstance(start, str) else start
    end_dt = normalize_timestamp(end) if isinstance(end, str) else end

    contract_type = MarketAgreementType.DAILY if dayahead else MarketAgreementType.INTRADAY

    return {
        "documentType": DocumentType.ALLOCATION_RESULT.value,
        "businessType": BusinessType.NET_POSITION.value,
        "Contract_MarketAgreement.Type": contract_type.value,
        "in_Domain": get_area_code(area),
        "out_Domain": get_area_code(area),
        "periodStart": start_dt.strftime("%Y%m%d%H%M"),
        "periodEnd": end_dt.strftime("%Y%m%d%H%M"),
    }


def build_aggregated_bids_params(
    area: str,
    start: datetime | str,
    end: datetime | str,
    process_type: ProcessType | str = ProcessType.DAY_AHEAD,
) -> dict[str, Any]:
    """Build parameters for aggregated bids query.

    Args:
        area: Area code or country code
        start: Start datetime
        end: End datetime
        process_type: Process type (day-ahead, intraday)

    Returns:
        Query parameters dictionary
    """
    start_dt = normalize_timestamp(start) if isinstance(start, str) else start
    end_dt = normalize_timestamp(end) if isinstance(end, str) else end

    process_value = process_type.value if isinstance(process_type, ProcessType) else process_type

    return {
        "documentType": DocumentType.BID_DOCUMENT.value,
        "processType": process_value,
        "area_Domain": get_area_code(area),
        "periodStart": start_dt.strftime("%Y%m%d%H%M"),
        "periodEnd": end_dt.strftime("%Y%m%d%H%M"),
    }
