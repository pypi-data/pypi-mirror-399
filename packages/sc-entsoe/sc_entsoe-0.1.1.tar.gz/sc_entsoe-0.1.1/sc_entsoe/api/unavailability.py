"""Unavailability and outage API methods (return ZIP files)."""

from datetime import datetime
from typing import Any

from sc_entsoe.models import DocStatus, DocumentType
from sc_entsoe.parsers.converters import get_area_code, normalize_timestamp


def build_unavailability_generation_params(
    area: str,
    start: datetime | str,
    end: datetime | str,
    docstatus: DocStatus | str | None = None,
    periodstartupdate: datetime | str | None = None,
    periodendupdate: datetime | str | None = None,
) -> dict[str, Any]:
    """Build parameters for unavailability of generation units query.

    Args:
        area: Area code or country code
        start: Start datetime
        end: End datetime
        docstatus: Document status (optional, e.g., DocStatus.ACTIVE)
        periodstartupdate: Period start update (optional)
        periodendupdate: Period end update (optional)

    Returns:
        Query parameters dictionary
    """
    start_dt = normalize_timestamp(start) if isinstance(start, str) else start
    end_dt = normalize_timestamp(end) if isinstance(end, str) else end

    params = {
        "documentType": DocumentType.GENERATION_UNAVAILABILITY.value,
        "biddingZone_Domain": get_area_code(area),
        "periodStart": start_dt.strftime("%Y%m%d%H%M"),
        "periodEnd": end_dt.strftime("%Y%m%d%H%M"),
    }

    if docstatus:
        status_value = docstatus.value if isinstance(docstatus, DocStatus) else docstatus
        params["docStatus"] = status_value
    if periodstartupdate:
        update_dt = (
            normalize_timestamp(periodstartupdate)
            if isinstance(periodstartupdate, str)
            else periodstartupdate
        )
        params["periodStartUpdate"] = update_dt.strftime("%Y%m%d%H%M")
    if periodendupdate:
        update_dt = (
            normalize_timestamp(periodendupdate)
            if isinstance(periodendupdate, str)
            else periodendupdate
        )
        params["periodEndUpdate"] = update_dt.strftime("%Y%m%d%H%M")

    return params


def build_unavailability_production_params(
    area: str,
    start: datetime | str,
    end: datetime | str,
    docstatus: DocStatus | str | None = None,
    periodstartupdate: datetime | str | None = None,
    periodendupdate: datetime | str | None = None,
) -> dict[str, Any]:
    """Build parameters for unavailability of production units query.

    Args:
        area: Area code or country code
        start: Start datetime
        end: End datetime
        docstatus: Document status (optional)
        periodstartupdate: Period start update (optional)
        periodendupdate: Period end update (optional)

    Returns:
        Query parameters dictionary
    """
    start_dt = normalize_timestamp(start) if isinstance(start, str) else start
    end_dt = normalize_timestamp(end) if isinstance(end, str) else end

    params = {
        "documentType": DocumentType.PRODUCTION_UNAVAILABILITY.value,
        "biddingZone_Domain": get_area_code(area),
        "periodStart": start_dt.strftime("%Y%m%d%H%M"),
        "periodEnd": end_dt.strftime("%Y%m%d%H%M"),
    }

    if docstatus:
        status_value = docstatus.value if isinstance(docstatus, DocStatus) else docstatus
        params["docStatus"] = status_value
    if periodstartupdate:
        update_dt = (
            normalize_timestamp(periodstartupdate)
            if isinstance(periodstartupdate, str)
            else periodstartupdate
        )
        params["periodStartUpdate"] = update_dt.strftime("%Y%m%d%H%M")
    if periodendupdate:
        update_dt = (
            normalize_timestamp(periodendupdate)
            if isinstance(periodendupdate, str)
            else periodendupdate
        )
        params["periodEndUpdate"] = update_dt.strftime("%Y%m%d%H%M")

    return params


def build_unavailability_transmission_params(
    from_area: str,
    to_area: str,
    start: datetime | str,
    end: datetime | str,
    docstatus: DocStatus | str | None = None,
    periodstartupdate: datetime | str | None = None,
    periodendupdate: datetime | str | None = None,
) -> dict[str, Any]:
    """Build parameters for unavailability of transmission infrastructure query.

    Args:
        from_area: Source area code or country code
        to_area: Destination area code or country code
        start: Start datetime
        end: End datetime
        docstatus: Document status (optional)
        periodstartupdate: Period start update (optional)
        periodendupdate: Period end update (optional)

    Returns:
        Query parameters dictionary
    """
    start_dt = normalize_timestamp(start) if isinstance(start, str) else start
    end_dt = normalize_timestamp(end) if isinstance(end, str) else end

    params = {
        "documentType": DocumentType.TRANSMISSION_UNAVAILABILITY.value,
        "in_Domain": get_area_code(to_area),
        "out_Domain": get_area_code(from_area),
        "periodStart": start_dt.strftime("%Y%m%d%H%M"),
        "periodEnd": end_dt.strftime("%Y%m%d%H%M"),
    }

    if docstatus:
        status_value = docstatus.value if isinstance(docstatus, DocStatus) else docstatus
        params["docStatus"] = status_value
    if periodstartupdate:
        update_dt = (
            normalize_timestamp(periodstartupdate)
            if isinstance(periodstartupdate, str)
            else periodstartupdate
        )
        params["periodStartUpdate"] = update_dt.strftime("%Y%m%d%H%M")
    if periodendupdate:
        update_dt = (
            normalize_timestamp(periodendupdate)
            if isinstance(periodendupdate, str)
            else periodendupdate
        )
        params["periodEndUpdate"] = update_dt.strftime("%Y%m%d%H%M")

    return params


def build_unavailability_offshore_grid_params(
    area: str,
    start: datetime | str,
    end: datetime | str,
) -> dict[str, Any]:
    """Build parameters for unavailability of offshore grid infrastructure query.

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
        "documentType": DocumentType.OFFSHORE_GRID_UNAVAILABILITY.value,
        "biddingZone_Domain": get_area_code(area),
        "periodStart": start_dt.strftime("%Y%m%d%H%M"),
        "periodEnd": end_dt.strftime("%Y%m%d%H%M"),
    }


def build_withdrawn_unavailability_generation_params(
    area: str,
    start: datetime | str,
    end: datetime | str,
) -> dict[str, Any]:
    """Build parameters for withdrawn unavailability of generation units query.

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
        "documentType": DocumentType.GENERATION_UNAVAILABILITY.value,
        "docStatus": DocStatus.WITHDRAWN.value,
        "biddingZone_Domain": get_area_code(area),
        "periodStart": start_dt.strftime("%Y%m%d%H%M"),
        "periodEnd": end_dt.strftime("%Y%m%d%H%M"),
    }
