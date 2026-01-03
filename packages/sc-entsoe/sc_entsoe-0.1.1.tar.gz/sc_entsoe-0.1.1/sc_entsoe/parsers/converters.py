"""Converters and utilities for ENTSOE data."""

from datetime import UTC, datetime, timedelta
from typing import Any

from sc_entsoe.models import Area, Resolution

# Area code mappings (country codes to EIC codes)
AREA_MAPPINGS = {
    "DE": Area.DE_LU,
    "FR": Area.FR,
    "NL": Area.NL,
    "BE": Area.BE,
    "AT": Area.AT,
    "CH": Area.CH,
    "ES": Area.ES,
    "PT": Area.PT,
    "FI": Area.FI,
    "PL": Area.PL,
    "CZ": Area.CZ,
    "GB": Area.GB,
    "SE1": Area.SE_1,
    "SE2": Area.SE_2,
    "SE3": Area.SE_3,
    "SE4": Area.SE_4,
    "NO1": Area.NO_1,
    "NO2": Area.NO_2,
    "NO3": Area.NO_3,
    "NO4": Area.NO_4,
    "DK1": Area.DK_1,
    "DK2": Area.DK_2,
}


def parse_resolution(resolution_code: str) -> timedelta:
    """Parse ENTSOE resolution code to timedelta.

    Args:
        resolution_code: Resolution code (e.g., "PT15M", "PT60M", "P1D")

    Returns:
        timedelta representing the resolution

    Examples:
        >>> parse_resolution("PT15M")
        timedelta(minutes=15)
        >>> parse_resolution("PT60M")
        timedelta(hours=1)
        >>> parse_resolution("P1D")
        timedelta(days=1)
    """
    resolution_map = {
        Resolution.PT15M: timedelta(minutes=15),
        Resolution.PT30M: timedelta(minutes=30),
        Resolution.PT60M: timedelta(hours=1),
        Resolution.P1D: timedelta(days=1),
    }

    try:
        return resolution_map[Resolution(resolution_code)]
    except (ValueError, KeyError):
        # Fallback: try to parse manually
        if resolution_code.startswith("PT") and resolution_code.endswith("M"):
            minutes = int(resolution_code[2:-1])
            return timedelta(minutes=minutes)
        elif resolution_code.startswith("PT") and resolution_code.endswith("H"):
            hours = int(resolution_code[2:-1])
            return timedelta(hours=hours)
        elif resolution_code.startswith("P") and resolution_code.endswith("D"):
            days = int(resolution_code[1:-1])
            return timedelta(days=days)
        else:
            raise ValueError(f"Unknown resolution code: {resolution_code}") from None


def normalize_timestamp(dt: datetime | str) -> datetime:
    """Normalize timestamp to UTC timezone-aware datetime.

    Args:
        dt: datetime object or ISO string

    Returns:
        UTC timezone-aware datetime
    """
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))

    # Ensure timezone-aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    else:
        # Convert to UTC
        dt = dt.astimezone(UTC)

    return dt


def get_area_code(area: str | Area) -> str:
    """Get EIC area code from country code or Area enum.

    Args:
        area: Country code (e.g., "DE") or Area enum

    Returns:
        EIC area code

    Examples:
        >>> get_area_code("DE")
        '10Y1001A1001A82H'
        >>> get_area_code(Area.DE_LU)
        '10Y1001A1001A82H'
    """
    if isinstance(area, Area):
        return area.value

    # Try direct mapping
    if area in AREA_MAPPINGS:
        return AREA_MAPPINGS[area].value

    # Assume it's already an EIC code
    return area


def canonicalize_params(params: dict[str, Any]) -> dict[str, Any]:
    """Canonicalize query parameters for cache key generation.

    Args:
        params: Query parameters

    Returns:
        Canonicalized parameters (sorted, normalized timestamps)
    """
    canonical: dict[str, Any] = {}

    for key, value in sorted(params.items()):
        if isinstance(value, datetime):
            # Normalize to UTC ISO format
            canonical[key] = normalize_timestamp(value).isoformat()
        elif isinstance(value, (list, tuple)):
            # Sort lists for consistency
            canonical[key] = tuple(sorted(str(v) for v in value))
        else:
            canonical[key] = value

    return canonical
