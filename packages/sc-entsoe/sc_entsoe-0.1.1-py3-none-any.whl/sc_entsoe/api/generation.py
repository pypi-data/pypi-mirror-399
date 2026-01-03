"""Generation data API methods."""

from datetime import datetime
from typing import Any

from sc_entsoe.models import DocumentType, ProcessType, PSRType
from sc_entsoe.parsers.converters import get_area_code, normalize_timestamp


def build_generation_actual_params(
    area: str,
    start: datetime | str,
    end: datetime | str,
    psr_type: PSRType | str | None = None,
) -> dict[str, Any]:
    """Build parameters for actual generation query.

    Args:
        area: Area code or country code
        start: Start datetime
        end: End datetime
        psr_type: Power system resource type (optional, for specific generation type)

    Returns:
        Query parameters dictionary
    """
    start_dt = normalize_timestamp(start) if isinstance(start, str) else start
    end_dt = normalize_timestamp(end) if isinstance(end, str) else end

    params = {
        "documentType": DocumentType.ACTUAL_GENERATION_PER_TYPE.value,
        "processType": ProcessType.REALISED.value,
        "in_Domain": get_area_code(area),
        "periodStart": start_dt.strftime("%Y%m%d%H%M"),
        "periodEnd": end_dt.strftime("%Y%m%d%H%M"),
    }

    if psr_type:
        psr_value = psr_type.value if isinstance(psr_type, PSRType) else psr_type
        params["psrType"] = psr_value

    return params


def build_generation_forecast_params(
    area: str,
    start: datetime | str,
    end: datetime | str,
    psr_type: PSRType | str | None = None,
) -> dict[str, Any]:
    """Build parameters for generation forecast query.

    Args:
        area: Area code or country code
        start: Start datetime
        end: End datetime
        psr_type: Power system resource type (optional)

    Returns:
        Query parameters dictionary
    """
    start_dt = normalize_timestamp(start) if isinstance(start, str) else start
    end_dt = normalize_timestamp(end) if isinstance(end, str) else end

    params = {
        "documentType": DocumentType.GENERATION_FORECAST.value,
        "processType": ProcessType.DAY_AHEAD.value,
        "in_Domain": get_area_code(area),
        "periodStart": start_dt.strftime("%Y%m%d%H%M"),
        "periodEnd": end_dt.strftime("%Y%m%d%H%M"),
    }

    if psr_type:
        psr_value = psr_type.value if isinstance(psr_type, PSRType) else psr_type
        params["psrType"] = psr_value

    return params


def build_installed_capacity_params(
    area: str,
    start: datetime | str,
    end: datetime | str,
    psr_type: PSRType | str | None = None,
) -> dict[str, Any]:
    """Build parameters for installed generation capacity query.

    Args:
        area: Area code or country code
        start: Start datetime
        end: End datetime
        psr_type: Power system resource type (optional)

    Returns:
        Query parameters dictionary
    """
    start_dt = normalize_timestamp(start) if isinstance(start, str) else start
    end_dt = normalize_timestamp(end) if isinstance(end, str) else end

    params = {
        "documentType": DocumentType.INSTALLED_GENERATION_CAPACITY_PER_TYPE.value,
        "processType": ProcessType.YEAR_AHEAD.value,
        "in_Domain": get_area_code(area),
        "periodStart": start_dt.strftime("%Y%m%d%H%M"),
        "periodEnd": end_dt.strftime("%Y%m%d%H%M"),
    }

    if psr_type:
        psr_value = psr_type.value if isinstance(psr_type, PSRType) else psr_type
        params["psrType"] = psr_value

    return params


def build_wind_solar_forecast_params(
    area: str,
    start: datetime | str,
    end: datetime | str,
    psr_type: PSRType | str | None = None,
) -> dict[str, Any]:
    """Build parameters for wind and solar forecast query.

    Args:
        area: Area code or country code
        start: Start datetime
        end: End datetime
        psr_type: Power system resource type (B16=Solar, B18=Wind Offshore, B19=Wind Onshore)

    Returns:
        Query parameters dictionary
    """
    start_dt = normalize_timestamp(start) if isinstance(start, str) else start
    end_dt = normalize_timestamp(end) if isinstance(end, str) else end

    params = {
        "documentType": DocumentType.WIND_SOLAR_FORECAST.value,
        "processType": ProcessType.DAY_AHEAD.value,
        "in_Domain": get_area_code(area),
        "periodStart": start_dt.strftime("%Y%m%d%H%M"),
        "periodEnd": end_dt.strftime("%Y%m%d%H%M"),
    }

    if psr_type:
        psr_value = psr_type.value if isinstance(psr_type, PSRType) else psr_type
        params["psrType"] = psr_value

    return params


def build_intraday_wind_solar_forecast_params(
    area: str,
    start: datetime | str,
    end: datetime | str,
    psr_type: PSRType | str | None = None,
) -> dict[str, Any]:
    """Build parameters for intraday wind and solar forecast query.

    Args:
        area: Area code or country code
        start: Start datetime
        end: End datetime
        psr_type: Power system resource type (B16=Solar, B18=Wind Offshore, B19=Wind Onshore)

    Returns:
        Query parameters dictionary
    """
    start_dt = normalize_timestamp(start) if isinstance(start, str) else start
    end_dt = normalize_timestamp(end) if isinstance(end, str) else end

    params = {
        "documentType": DocumentType.WIND_SOLAR_FORECAST.value,
        "processType": ProcessType.INTRADAY_PROCESS.value,
        "in_Domain": get_area_code(area),
        "periodStart": start_dt.strftime("%Y%m%d%H%M"),
        "periodEnd": end_dt.strftime("%Y%m%d%H%M"),
    }

    if psr_type:
        psr_value = psr_type.value if isinstance(psr_type, PSRType) else psr_type
        params["psrType"] = psr_value

    return params


def build_generation_per_plant_params(
    area: str,
    start: datetime | str,
    end: datetime | str,
    psr_type: PSRType | str | None = None,
) -> dict[str, Any]:
    """Build parameters for generation per plant query.

    Args:
        area: Area code or country code
        start: Start datetime
        end: End datetime
        psr_type: Power system resource type (optional)

    Returns:
        Query parameters dictionary
    """
    start_dt = normalize_timestamp(start) if isinstance(start, str) else start
    end_dt = normalize_timestamp(end) if isinstance(end, str) else end

    params = {
        "documentType": DocumentType.ACTUAL_GENERATION.value,
        "processType": ProcessType.REALISED.value,
        "in_Domain": get_area_code(area),
        "periodStart": start_dt.strftime("%Y%m%d%H%M"),
        "periodEnd": end_dt.strftime("%Y%m%d%H%M"),
    }

    if psr_type:
        psr_value = psr_type.value if isinstance(psr_type, PSRType) else psr_type
        params["psrType"] = psr_value

    return params


def build_installed_capacity_per_unit_params(
    area: str,
    start: datetime | str,
    end: datetime | str,
    psr_type: PSRType | str | None = None,
) -> dict[str, Any]:
    """Build parameters for installed capacity per unit query.

    Args:
        area: Area code or country code
        start: Start datetime
        end: End datetime
        psr_type: Power system resource type (optional)

    Returns:
        Query parameters dictionary
    """
    start_dt = normalize_timestamp(start) if isinstance(start, str) else start
    end_dt = normalize_timestamp(end) if isinstance(end, str) else end

    params = {
        "documentType": DocumentType.GENERATION_FORECAST.value,
        "processType": ProcessType.YEAR_AHEAD.value,
        "in_Domain": get_area_code(area),
        "periodStart": start_dt.strftime("%Y%m%d%H%M"),
        "periodEnd": end_dt.strftime("%Y%m%d%H%M"),
    }

    if psr_type:
        psr_value = psr_type.value if isinstance(psr_type, PSRType) else psr_type
        params["psrType"] = psr_value

    return params
