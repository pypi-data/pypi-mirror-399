"""Balancing data API methods."""

from datetime import datetime
from typing import Any

from sc_entsoe.models import (
    BusinessType,
    DocumentType,
    MarketAgreementType,
    ProcessType,
)
from sc_entsoe.parsers.converters import get_area_code, normalize_timestamp


def build_procured_balancing_capacity_params(
    area: str,
    start: datetime | str,
    end: datetime | str,
    process_type: ProcessType | str = ProcessType.DAY_AHEAD,
    type_marketagreement_type: MarketAgreementType | str = MarketAgreementType.DAILY,
) -> dict[str, Any]:
    """Build parameters for procured balancing capacity query.

    Args:
        area: Area code or country code
        start: Start datetime
        end: End datetime
        process_type: Process type (day-ahead, week-ahead, etc.)
        type_marketagreement_type: Type of market agreement

    Returns:
        Query parameters dictionary
    """
    start_dt = normalize_timestamp(start) if isinstance(start, str) else start
    end_dt = normalize_timestamp(end) if isinstance(end, str) else end

    process_value = process_type.value if isinstance(process_type, ProcessType) else process_type
    market_value = (
        type_marketagreement_type.value
        if isinstance(type_marketagreement_type, MarketAgreementType)
        else type_marketagreement_type
    )

    return {
        "documentType": DocumentType.ACQUIRING_SYSTEM_OPERATOR_RESERVE.value,
        "processType": process_value,
        "type_MarketAgreement.Type": market_value,
        "area_Domain": get_area_code(area),
        "periodStart": start_dt.strftime("%Y%m%d%H%M"),
        "periodEnd": end_dt.strftime("%Y%m%d%H%M"),
    }


def build_activated_balancing_energy_params(
    area: str,
    start: datetime | str,
    end: datetime | str,
    business_type: BusinessType | str = BusinessType.FREQUENCY_CONTAINMENT_RESERVE,
) -> dict[str, Any]:
    """Build parameters for activated balancing energy query.

    Args:
        area: Area code or country code
        start: Start datetime
        end: End datetime
        business_type: Business type (A95=FCR, A96=aFRR, A97=mFRR, A98=RR)

    Returns:
        Query parameters dictionary
    """
    start_dt = normalize_timestamp(start) if isinstance(start, str) else start
    end_dt = normalize_timestamp(end) if isinstance(end, str) else end

    business_value = (
        business_type.value if isinstance(business_type, BusinessType) else business_type
    )

    return {
        "documentType": DocumentType.ACTIVATED_BALANCING_QUANTITIES.value,
        "businessType": business_value,
        "controlArea_Domain": get_area_code(area),
        "periodStart": start_dt.strftime("%Y%m%d%H%M"),
        "periodEnd": end_dt.strftime("%Y%m%d%H%M"),
    }


def build_imbalance_volumes_params(
    area: str,
    start: datetime | str,
    end: datetime | str,
) -> dict[str, Any]:
    """Build parameters for system imbalance volumes query.

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
        "documentType": DocumentType.IMBALANCE_VOLUME.value,
        "controlArea_Domain": get_area_code(area),
        "periodStart": start_dt.strftime("%Y%m%d%H%M"),
        "periodEnd": end_dt.strftime("%Y%m%d%H%M"),
    }


def build_balancing_energy_prices_params(
    area: str,
    start: datetime | str,
    end: datetime | str,
) -> dict[str, Any]:
    """Build parameters for balancing energy prices query.

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
        "documentType": DocumentType.ACTIVATED_BALANCING_PRICES.value,
        "controlArea_Domain": get_area_code(area),
        "periodStart": start_dt.strftime("%Y%m%d%H%M"),
        "periodEnd": end_dt.strftime("%Y%m%d%H%M"),
    }


def build_contracted_reserve_prices_params(
    area: str,
    start: datetime | str,
    end: datetime | str,
    type_marketagreement_type: MarketAgreementType | str,
    psr_type: str | None = None,
) -> dict[str, Any]:
    """Build parameters for contracted reserve prices query.

    Args:
        area: Area code or country code
        start: Start datetime
        end: End datetime
        type_marketagreement_type: Type of reserves
        psr_type: Power system resource type (optional)

    Returns:
        Query parameters dictionary
    """
    start_dt = normalize_timestamp(start) if isinstance(start, str) else start
    end_dt = normalize_timestamp(end) if isinstance(end, str) else end

    market_value = (
        type_marketagreement_type.value
        if isinstance(type_marketagreement_type, MarketAgreementType)
        else type_marketagreement_type
    )

    params = {
        "documentType": DocumentType.CONTRACTED_RESERVE_PRICES.value,
        "type_MarketAgreement.Type": market_value,
        "controlArea_Domain": get_area_code(area),
        "periodStart": start_dt.strftime("%Y%m%d%H%M"),
        "periodEnd": end_dt.strftime("%Y%m%d%H%M"),
    }

    if psr_type:
        params["psrType"] = psr_type

    return params


def build_contracted_reserve_amount_params(
    area: str,
    start: datetime | str,
    end: datetime | str,
    type_marketagreement_type: MarketAgreementType | str,
    psr_type: str | None = None,
) -> dict[str, Any]:
    """Build parameters for contracted reserve amount query.

    Args:
        area: Area code or country code
        start: Start datetime
        end: End datetime
        type_marketagreement_type: Type of reserves
        psr_type: Power system resource type (optional)

    Returns:
        Query parameters dictionary
    """
    start_dt = normalize_timestamp(start) if isinstance(start, str) else start
    end_dt = normalize_timestamp(end) if isinstance(end, str) else end

    market_value = (
        type_marketagreement_type.value
        if isinstance(type_marketagreement_type, MarketAgreementType)
        else type_marketagreement_type
    )

    params = {
        "documentType": DocumentType.CONTRACTED_RESERVES.value,
        "type_MarketAgreement.Type": market_value,
        "controlArea_Domain": get_area_code(area),
        "periodStart": start_dt.strftime("%Y%m%d%H%M"),
        "periodEnd": end_dt.strftime("%Y%m%d%H%M"),
    }

    if psr_type:
        params["psrType"] = psr_type

    return params


def build_activated_balancing_energy_prices_params(
    area: str,
    start: datetime | str,
    end: datetime | str,
    process_type: ProcessType | str = ProcessType.REALISED,
    psr_type: str | None = None,
    business_type: BusinessType | str | None = None,
) -> dict[str, Any]:
    """Build parameters for activated balancing energy prices query.

    Args:
        area: Area code or country code
        start: Start datetime
        end: End datetime
        process_type: Process type (default A16=Realised)
        psr_type: Power system resource type (optional)
        business_type: Business type (optional)

    Returns:
        Query parameters dictionary
    """
    start_dt = normalize_timestamp(start) if isinstance(start, str) else start
    end_dt = normalize_timestamp(end) if isinstance(end, str) else end

    process_value = process_type.value if isinstance(process_type, ProcessType) else process_type

    params = {
        "documentType": DocumentType.ACTIVATED_BALANCING_PRICES.value,
        "processType": process_value,
        "controlArea_Domain": get_area_code(area),
        "periodStart": start_dt.strftime("%Y%m%d%H%M"),
        "periodEnd": end_dt.strftime("%Y%m%d%H%M"),
    }

    if psr_type:
        params["psrType"] = psr_type
    if business_type:
        business_value = (
            business_type.value if isinstance(business_type, BusinessType) else business_type
        )
        params["businessType"] = business_value

    return params
