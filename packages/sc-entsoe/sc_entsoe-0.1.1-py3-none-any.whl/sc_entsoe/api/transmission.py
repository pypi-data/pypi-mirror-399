"""Transmission data API methods."""

from datetime import datetime
from typing import Any

from sc_entsoe.models import AuctionType, DocumentType, MarketAgreementType
from sc_entsoe.parsers.converters import get_area_code, normalize_timestamp


def build_crossborder_flows_params(
    from_area: str,
    to_area: str,
    start: datetime | str,
    end: datetime | str,
) -> dict[str, Any]:
    """Build parameters for cross-border physical flows query.

    Args:
        from_area: Source area code or country code
        to_area: Destination area code or country code
        start: Start datetime
        end: End datetime

    Returns:
        Query parameters dictionary
    """
    start_dt = normalize_timestamp(start) if isinstance(start, str) else start
    end_dt = normalize_timestamp(end) if isinstance(end, str) else end

    return {
        "documentType": DocumentType.PHYSICAL_FLOWS.value,
        "in_Domain": get_area_code(to_area),
        "out_Domain": get_area_code(from_area),
        "periodStart": start_dt.strftime("%Y%m%d%H%M"),
        "periodEnd": end_dt.strftime("%Y%m%d%H%M"),
    }


def build_scheduled_exchanges_params(
    from_area: str,
    to_area: str,
    start: datetime | str,
    end: datetime | str,
) -> dict[str, Any]:
    """Build parameters for scheduled commercial exchanges query.

    Args:
        from_area: Source area code or country code
        to_area: Destination area code or country code
        start: Start datetime
        end: End datetime

    Returns:
        Query parameters dictionary
    """
    start_dt = normalize_timestamp(start) if isinstance(start, str) else start
    end_dt = normalize_timestamp(end) if isinstance(end, str) else end

    return {
        "documentType": DocumentType.FINALISED_SCHEDULE.value,
        "in_Domain": get_area_code(to_area),
        "out_Domain": get_area_code(from_area),
        "periodStart": start_dt.strftime("%Y%m%d%H%M"),
        "periodEnd": end_dt.strftime("%Y%m%d%H%M"),
    }


def build_transmission_capacity_params(
    from_area: str,
    to_area: str,
    start: datetime | str,
    end: datetime | str,
    contract_type: MarketAgreementType | str = MarketAgreementType.DAILY,
) -> dict[str, Any]:
    """Build parameters for available transfer capacity query.

    Args:
        from_area: Source area code or country code
        to_area: Destination area code or country code
        start: Start datetime
        end: End datetime
        contract_type: Contract market agreement type

    Returns:
        Query parameters dictionary
    """
    start_dt = normalize_timestamp(start) if isinstance(start, str) else start
    end_dt = normalize_timestamp(end) if isinstance(end, str) else end

    contract_value = (
        contract_type.value if isinstance(contract_type, MarketAgreementType) else contract_type
    )

    return {
        "documentType": DocumentType.ESTIMATED_NET_TRANSFER_CAPACITY.value,
        "contract_MarketAgreement.Type": contract_value,
        "in_Domain": get_area_code(to_area),
        "out_Domain": get_area_code(from_area),
        "periodStart": start_dt.strftime("%Y%m%d%H%M"),
        "periodEnd": end_dt.strftime("%Y%m%d%H%M"),
    }


def build_net_transfer_capacity_dayahead_params(
    from_area: str,
    to_area: str,
    start: datetime | str,
    end: datetime | str,
) -> dict[str, Any]:
    """Build parameters for day-ahead net transfer capacity query.

    Args:
        from_area: Source area code or country code
        to_area: Destination area code or country code
        start: Start datetime
        end: End datetime

    Returns:
        Query parameters dictionary
    """
    start_dt = normalize_timestamp(start) if isinstance(start, str) else start
    end_dt = normalize_timestamp(end) if isinstance(end, str) else end

    return {
        "documentType": DocumentType.ESTIMATED_NET_TRANSFER_CAPACITY.value,
        "contract_MarketAgreement.Type": MarketAgreementType.DAILY.value,
        "in_Domain": get_area_code(to_area),
        "out_Domain": get_area_code(from_area),
        "periodStart": start_dt.strftime("%Y%m%d%H%M"),
        "periodEnd": end_dt.strftime("%Y%m%d%H%M"),
    }


def build_net_transfer_capacity_weekahead_params(
    from_area: str,
    to_area: str,
    start: datetime | str,
    end: datetime | str,
) -> dict[str, Any]:
    """Build parameters for week-ahead net transfer capacity query.

    Args:
        from_area: Source area code or country code
        to_area: Destination area code or country code
        start: Start datetime
        end: End datetime

    Returns:
        Query parameters dictionary
    """
    start_dt = normalize_timestamp(start) if isinstance(start, str) else start
    end_dt = normalize_timestamp(end) if isinstance(end, str) else end

    return {
        "documentType": DocumentType.ESTIMATED_NET_TRANSFER_CAPACITY.value,
        "contract_MarketAgreement.Type": MarketAgreementType.WEEKLY.value,
        "in_Domain": get_area_code(to_area),
        "out_Domain": get_area_code(from_area),
        "periodStart": start_dt.strftime("%Y%m%d%H%M"),
        "periodEnd": end_dt.strftime("%Y%m%d%H%M"),
    }


def build_net_transfer_capacity_monthahead_params(
    from_area: str,
    to_area: str,
    start: datetime | str,
    end: datetime | str,
) -> dict[str, Any]:
    """Build parameters for month-ahead net transfer capacity query.

    Args:
        from_area: Source area code or country code
        to_area: Destination area code or country code
        start: Start datetime
        end: End datetime

    Returns:
        Query parameters dictionary
    """
    start_dt = normalize_timestamp(start) if isinstance(start, str) else start
    end_dt = normalize_timestamp(end) if isinstance(end, str) else end

    return {
        "documentType": DocumentType.ESTIMATED_NET_TRANSFER_CAPACITY.value,
        "contract_MarketAgreement.Type": MarketAgreementType.MONTHLY.value,
        "in_Domain": get_area_code(to_area),
        "out_Domain": get_area_code(from_area),
        "periodStart": start_dt.strftime("%Y%m%d%H%M"),
        "periodEnd": end_dt.strftime("%Y%m%d%H%M"),
    }


def build_net_transfer_capacity_yearahead_params(
    from_area: str,
    to_area: str,
    start: datetime | str,
    end: datetime | str,
) -> dict[str, Any]:
    """Build parameters for year-ahead net transfer capacity query.

    Args:
        from_area: Source area code or country code
        to_area: Destination area code or country code
        start: Start datetime
        end: End datetime

    Returns:
        Query parameters dictionary
    """
    start_dt = normalize_timestamp(start) if isinstance(start, str) else start
    end_dt = normalize_timestamp(end) if isinstance(end, str) else end

    return {
        "documentType": DocumentType.ESTIMATED_NET_TRANSFER_CAPACITY.value,
        "contract_MarketAgreement.Type": MarketAgreementType.YEARLY.value,
        "in_Domain": get_area_code(to_area),
        "out_Domain": get_area_code(from_area),
        "periodStart": start_dt.strftime("%Y%m%d%H%M"),
        "periodEnd": end_dt.strftime("%Y%m%d%H%M"),
    }


def build_intraday_offered_capacity_params(
    from_area: str,
    to_area: str,
    start: datetime | str,
    end: datetime | str,
    implicit: bool = True,
) -> dict[str, Any]:
    """Build parameters for intraday offered capacity query.

    Args:
        from_area: Source area code or country code
        to_area: Destination area code or country code
        start: Start datetime
        end: End datetime
        implicit: True for implicit auction, False for explicit

    Returns:
        Query parameters dictionary
    """
    start_dt = normalize_timestamp(start) if isinstance(start, str) else start
    end_dt = normalize_timestamp(end) if isinstance(end, str) else end

    auction = AuctionType.IMPLICIT if implicit else AuctionType.EXPLICIT

    return {
        "documentType": DocumentType.AGREED_CAPACITY.value,
        "Auction.Type": auction.value,
        "contract_MarketAgreement.Type": MarketAgreementType.INTRADAY.value,
        "in_Domain": get_area_code(to_area),
        "out_Domain": get_area_code(from_area),
        "periodStart": start_dt.strftime("%Y%m%d%H%M"),
        "periodEnd": end_dt.strftime("%Y%m%d%H%M"),
    }


def build_offered_capacity_params(
    from_area: str,
    to_area: str,
    start: datetime | str,
    end: datetime | str,
    contract_type: MarketAgreementType | str = MarketAgreementType.DAILY,
    implicit: bool = True,
) -> dict[str, Any]:
    """Build parameters for offered capacity query.

    Args:
        from_area: Source area code or country code
        to_area: Destination area code or country code
        start: Start datetime
        end: End datetime
        contract_type: Contract market agreement type
        implicit: True for implicit auction, False for explicit

    Returns:
        Query parameters dictionary
    """
    start_dt = normalize_timestamp(start) if isinstance(start, str) else start
    end_dt = normalize_timestamp(end) if isinstance(end, str) else end

    auction = AuctionType.IMPLICIT if implicit else AuctionType.EXPLICIT
    contract_value = (
        contract_type.value if isinstance(contract_type, MarketAgreementType) else contract_type
    )

    return {
        "documentType": DocumentType.AGREED_CAPACITY.value,
        "Auction.Type": auction.value,
        "contract_MarketAgreement.Type": contract_value,
        "in_Domain": get_area_code(to_area),
        "out_Domain": get_area_code(from_area),
        "periodStart": start_dt.strftime("%Y%m%d%H%M"),
        "periodEnd": end_dt.strftime("%Y%m%d%H%M"),
    }
