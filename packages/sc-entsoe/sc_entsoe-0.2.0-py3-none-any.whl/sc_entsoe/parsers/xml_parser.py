"""Efficient XML parser for ENTSOE responses using standard library xml.etree."""

import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Any

from sc_entsoe.exceptions import ParseError
from sc_entsoe.models import EntsoeFrame
from sc_entsoe.parsers.converters import normalize_timestamp, parse_resolution

# XML namespaces used by ENTSOE - different document types use different namespaces
ENTSOE_NAMESPACES = {
    # Publication document (prices)
    "publication": "urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:3",
    # Generation/Load document
    "gl": "urn:iec62325.351:tc57wg16:451-6:generationloaddocument:3:0",
    # Transmission network document
    "transmission": "urn:iec62325.351:tc57wg16:451-5:transmissionnetworkdocument:3:0",
    # Unavailability document
    "unavailability": "urn:iec62325.351:tc57wg16:451-7:unavailabilitydocument:2:0",
    # Balancing document
    "balancing": "urn:iec62325.351:tc57wg16:451-8:balancingdocument:5:1",
    # Critical network element document
    "cne": "urn:iec62325.351:tc57wg16:451-9:cnedocument:3:0",
}


def _get_namespace(root: ET.Element) -> dict[str, str]:
    """Extract namespace from root element.

    ENTSOE uses different namespaces for different document types.
    This detects and returns the appropriate namespace mapping.

    Args:
        root: XML root element

    Returns:
        Namespace dictionary for element queries
    """
    # Extract namespace from root tag (format: {namespace}tag)
    if root.tag.startswith("{") and "}" in root.tag:
        ns = root.tag.split("}")[0][1:]
        return {"ns": ns}

    # Try to match against known namespaces
    for known_ns in ENTSOE_NAMESPACES.values():
        if known_ns in str(root.tag):
            return {"ns": known_ns}

    return {}


def parse_entsoe_xml(
    xml_content: str | bytes,
    fill_missing: bool = True,
    strict_schema: bool = False,
) -> EntsoeFrame:
    """Parse ENTSOE XML response to list of dictionaries.

    This uses standard library xml.etree for parsing.
    Handles ENTSOE's quirk of omitting duplicate consecutive values.

    Args:
        xml_content: XML content as string or bytes
        fill_missing: Fill missing intervals with last known value
        strict_schema: Raise on unexpected XML format

    Returns:
        EntsoeFrame with data and metadata

    Raises:
        ParseError: If XML parsing fails
    """
    try:
        if isinstance(xml_content, bytes):
            xml_content = xml_content.decode("utf-8")

        root = ET.fromstring(xml_content)

        # Detect namespace from the document
        namespaces = _get_namespace(root)

        # Extract metadata from document
        metadata = _extract_metadata(root, namespaces)

        # Parse time series data - search with namespace
        ns_prefix = namespaces.get("ns", "")
        if ns_prefix:
            ns_tag = f"{{{ns_prefix}}}TimeSeries"
            time_series_list = list(root.iter(ns_tag))
        else:
            # Fallback: search for any TimeSeries element
            time_series_list = list(root.iter("TimeSeries"))

        if not time_series_list:
            # Empty response - no data available
            return EntsoeFrame(
                data=[],
                metadata={**metadata, "empty": True},
            )

        # Parse all time series
        all_data = []
        for ts in time_series_list:
            data = _parse_time_series(ts, namespaces, fill_missing=fill_missing)
            if data:
                all_data.extend(data)

        if not all_data:
            return EntsoeFrame(
                data=[],
                metadata={**metadata, "empty": True},
            )

        # Sort by timestamp
        all_data.sort(key=lambda x: x.get("timestamp", ""))

        return EntsoeFrame(data=all_data, metadata=metadata)

    except ET.ParseError as e:
        raise ParseError(f"Invalid XML: {e}", response_text=str(xml_content[:500])) from e
    except Exception as e:
        if strict_schema:
            raise ParseError(
                f"Failed to parse XML: {e}", response_text=str(xml_content[:500])
            ) from e
        # Best effort: return empty frame
        return EntsoeFrame(
            data=[],
            metadata={"error": str(e), "empty": True},
        )


def _find_element(
    parent: ET.Element, tag: str, namespaces: dict[str, str]
) -> ET.Element | None:
    """Find element with namespace fallback.

    Args:
        parent: Parent element
        tag: Element tag name (e.g., "type", "start")
        namespaces: Namespace mapping

    Returns:
        Found element or None
    """
    ns_prefix = namespaces.get("ns", "")

    # Try with namespace
    if ns_prefix:
        ns_tag = f"{{{ns_prefix}}}{tag}"
        elem = parent.find(ns_tag)
        if elem is not None:
            return elem

    # Fallback: try without namespace
    elem = parent.find(tag)
    if elem is not None:
        return elem

    # Fallback: search recursively
    for child in parent.iter():
        if child.tag.endswith("}" + tag) or child.tag == tag:
            return child

    return None


def _extract_metadata(root: ET.Element, namespaces: dict[str, str]) -> dict[str, Any]:
    """Extract metadata from XML root element.

    Args:
        root: XML root element
        namespaces: Namespace mapping

    Returns:
        Dictionary of metadata
    """
    metadata: dict[str, Any] = {}

    # Document type - search recursively
    for elem in root.iter():
        if elem.tag.endswith("}type") or elem.tag == "type":
            if elem.text:
                metadata["document_type"] = elem.text
            break

    # Time interval
    for elem in root.iter():
        if "timeInterval" in elem.tag or "time_Period" in elem.tag:
            for child in elem.iter():
                if child.tag.endswith("}start") or child.tag == "start":
                    if child.text:
                        metadata["start_time"] = normalize_timestamp(child.text)
                elif child.tag.endswith("}end") or child.tag == "end":
                    if child.text:
                        metadata["end_time"] = normalize_timestamp(child.text)

    # Process type
    for elem in root.iter():
        if "processType" in elem.tag or "process.processType" in elem.tag:
            if elem.text:
                metadata["process_type"] = elem.text
            break

    # Sender/receiver
    for elem in root.iter():
        if "sender_MarketParticipant" in elem.tag or "mRID" in elem.tag:
            if elem.text and "sender" not in metadata:
                metadata["sender"] = elem.text
            break

    return metadata


def _find_all_elements(
    parent: ET.Element, tag: str, namespaces: dict[str, str]
) -> list[ET.Element]:
    """Find all elements with namespace fallback.

    Args:
        parent: Parent element
        tag: Element tag name
        namespaces: Namespace mapping

    Returns:
        List of found elements
    """
    ns_prefix = namespaces.get("ns", "")
    results = []

    # Try with namespace
    if ns_prefix:
        ns_tag = f"{{{ns_prefix}}}{tag}"
        results.extend(parent.findall(f".//{ns_tag}"))

    # Fallback: try without namespace
    results.extend(parent.findall(f".//{tag}"))

    # Remove duplicates while preserving order
    seen = set()
    unique_results = []
    for elem in results:
        if id(elem) not in seen:
            seen.add(id(elem))
            unique_results.append(elem)

    return unique_results


def _parse_time_series(
    time_series: ET.Element,
    namespaces: dict[str, str],
    fill_missing: bool = True,
) -> list[dict[str, Any]]:
    """Parse a single TimeSeries element.

    Args:
        time_series: TimeSeries XML element
        namespaces: Namespace mapping
        fill_missing: Fill missing intervals

    Returns:
        List of data dictionaries
    """
    data_points = []

    # Get resolution
    resolution_elem = _find_element(time_series, "resolution", namespaces)
    resolution_str = (
        resolution_elem.text if resolution_elem is not None and resolution_elem.text else "PT60M"
    )
    resolution = parse_resolution(resolution_str)

    # Get area/zone - try multiple possible element names
    area = None
    for tag_name in ["inBiddingZone_Domain", "outBiddingZone_Domain", "in_Domain", "out_Domain"]:
        domain_elem = _find_element(time_series, tag_name, namespaces)
        if domain_elem is not None:
            mrid_elem = _find_element(domain_elem, "mRID", namespaces)
            if mrid_elem is not None and mrid_elem.text:
                area = mrid_elem.text
                break

    # Get PSR type (generation type)
    psr_type_elem = _find_element(time_series, "MktPSRType", namespaces)
    psr_type = None
    if psr_type_elem is not None:
        psr_type_child = _find_element(psr_type_elem, "psrType", namespaces)
        if psr_type_child is not None and psr_type_child.text:
            psr_type = psr_type_child.text

    # Get business type
    business_type_elem = _find_element(time_series, "businessType", namespaces)
    business_type = business_type_elem.text if business_type_elem is not None else None

    # Parse periods
    periods = _find_all_elements(time_series, "Period", namespaces)

    for period in periods:
        # Get period start time
        time_interval_elem = _find_element(period, "timeInterval", namespaces)
        if time_interval_elem is None:
            continue
        start_elem = _find_element(time_interval_elem, "start", namespaces)
        if start_elem is None or not start_elem.text:
            continue

        period_start = normalize_timestamp(start_elem.text)

        # Parse points
        points = _find_all_elements(period, "Point", namespaces)

        if fill_missing:
            # Handle ENTSOE duplicate omission: fill missing intervals
            data_points.extend(
                _parse_points_with_fill(
                    points, period_start, resolution, area, psr_type, business_type, namespaces
                )
            )
        else:
            # Parse points as-is
            for point in points:
                position_elem = _find_element(point, "position", namespaces)
                quantity_elem = _find_element(point, "quantity", namespaces)
                # Try price.amount or price/amount
                price_elem = _find_element(point, "price.amount", namespaces)
                if price_elem is None:
                    price_elem = _find_element(point, "price", namespaces)
                    if price_elem is not None:
                        amount_elem = _find_element(price_elem, "amount", namespaces)
                        if amount_elem is not None:
                            price_elem = amount_elem

                if position_elem is None or not position_elem.text:
                    continue

                position = int(position_elem.text)
                timestamp = period_start + resolution * (position - 1)

                point_data: dict[str, Any] = {
                    "timestamp": timestamp.isoformat(),
                    "area": area,
                }

                if quantity_elem is not None and quantity_elem.text:
                    point_data["value"] = float(quantity_elem.text)
                if price_elem is not None and price_elem.text:
                    point_data["price"] = float(price_elem.text)
                if psr_type:
                    point_data["psr_type"] = psr_type
                if business_type:
                    point_data["business_type"] = business_type

                data_points.append(point_data)

    return data_points


def _parse_points_with_fill(
    points: list[ET.Element],
    period_start: datetime,
    resolution: timedelta,
    area: str | None,
    psr_type: str | None,
    business_type: str | None,
    namespaces: dict[str, str],
) -> list[dict[str, Any]]:
    """Parse points and fill missing intervals (ENTSOE duplicate handling).

    ENTSOE omits consecutive duplicate values. This fills them in.

    Args:
        points: List of Point XML elements
        period_start: Period start time
        resolution: Time resolution
        area: Area code
        psr_type: PSR type
        business_type: Business type
        namespaces: Namespace mapping

    Returns:
        List of data dictionaries with filled intervals
    """
    if not points:
        return []

    # Parse all points first
    parsed_points = []
    for point in points:
        position_elem = _find_element(point, "position", namespaces)
        quantity_elem = _find_element(point, "quantity", namespaces)
        # Try price.amount or price/amount
        price_elem = _find_element(point, "price.amount", namespaces)
        if price_elem is None:
            price_elem = _find_element(point, "price", namespaces)
            if price_elem is not None:
                amount_elem = _find_element(price_elem, "amount", namespaces)
                if amount_elem is not None:
                    price_elem = amount_elem

        if position_elem is None or not position_elem.text:
            continue

        position = int(position_elem.text)
        value = (
            float(quantity_elem.text) if quantity_elem is not None and quantity_elem.text else None
        )
        price = float(price_elem.text) if price_elem is not None and price_elem.text else None

        parsed_points.append((position, value, price))

    if not parsed_points:
        return []

    # Fill missing positions
    max_position = max(p[0] for p in parsed_points)
    filled_data = []

    # Create lookup for existing points
    point_lookup = {p[0]: (p[1], p[2]) for p in parsed_points}

    # Fill all positions from 1 to max
    last_value = None
    last_price = None

    for position in range(1, max_position + 1):
        timestamp = period_start + resolution * (position - 1)

        if position in point_lookup:
            # Point exists
            value, price = point_lookup[position]
            last_value = value
            last_price = price
        else:
            # Point missing - use last known value (ENTSOE duplicate omission)
            value = last_value
            price = last_price

        point_data: dict[str, Any] = {
            "timestamp": timestamp.isoformat(),
            "area": area,
        }

        if value is not None:
            point_data["value"] = value
        if price is not None:
            point_data["price"] = price
        if psr_type:
            point_data["psr_type"] = psr_type
        if business_type:
            point_data["business_type"] = business_type

        filled_data.append(point_data)

    return filled_data
