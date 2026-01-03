"""Efficient XML parser for ENTSOE responses using lxml streaming."""

from datetime import datetime, timedelta
from typing import Any

import polars as pl
from lxml import etree

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


def _get_namespace(root: etree._Element) -> dict[str, str]:
    """Extract namespace from root element.

    ENTSOE uses different namespaces for different document types.
    This detects and returns the appropriate namespace mapping.

    Args:
        root: XML root element

    Returns:
        Namespace dictionary for XPath queries
    """
    # Get the default namespace from the root element
    ns = root.nsmap.get(None, "")

    # If no default namespace, try to match against known namespaces
    if not ns:
        for known_ns in ENTSOE_NAMESPACES.values():
            if known_ns in str(root.tag):
                ns = known_ns
                break

    return {"ns": ns} if ns else {}


def parse_entsoe_xml(
    xml_content: str | bytes,
    fill_missing: bool = True,
    strict_schema: bool = False,
) -> EntsoeFrame:
    """Parse ENTSOE XML response to Polars DataFrame.

    This uses streaming XML parsing with lxml for memory efficiency.
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
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")

        root = etree.fromstring(xml_content)

        # Detect namespace from the document
        namespaces = _get_namespace(root)

        # Extract metadata from document
        metadata = _extract_metadata(root, namespaces)

        # Parse time series data - try with namespace first, then without
        time_series_list = root.findall(".//ns:TimeSeries", namespaces) if namespaces else []

        # Fallback: try without namespace if not found
        if not time_series_list:
            time_series_list = root.findall(".//{*}TimeSeries")

        if not time_series_list:
            # Empty response - no data available
            return EntsoeFrame(
                df=pl.DataFrame(),
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
                df=pl.DataFrame(),
                metadata={**metadata, "empty": True},
            )

        # Convert to Polars DataFrame
        df = pl.DataFrame(all_data)

        # Ensure timestamp column is datetime type and UTC
        if "timestamp" in df.columns:
            df = df.with_columns(pl.col("timestamp").str.to_datetime(time_zone="UTC"))
            # Sort by timestamp
            df = df.sort("timestamp")

        return EntsoeFrame(df=df, metadata=metadata)

    except etree.XMLSyntaxError as e:
        raise ParseError(f"Invalid XML: {e}", response_text=str(xml_content[:500])) from e
    except Exception as e:
        if strict_schema:
            raise ParseError(
                f"Failed to parse XML: {e}", response_text=str(xml_content[:500])
            ) from e
        # Best effort: return empty frame
        return EntsoeFrame(
            df=pl.DataFrame(),
            metadata={"error": str(e), "empty": True},
        )


def _find_element(
    parent: etree._Element, xpath: str, namespaces: dict[str, str]
) -> etree._Element | None:
    """Find element with namespace fallback.

    Args:
        parent: Parent element
        xpath: XPath expression (with ns: prefix)
        namespaces: Namespace mapping

    Returns:
        Found element or None
    """
    # Try with namespace
    if namespaces:
        elem = parent.find(xpath, namespaces)
        if elem is not None:
            return elem

    # Fallback: try with wildcard namespace
    wildcard_xpath = xpath.replace("ns:", "{*}")
    return parent.find(wildcard_xpath)


def _extract_metadata(root: etree._Element, namespaces: dict[str, str]) -> dict[str, Any]:
    """Extract metadata from XML root element.

    Args:
        root: XML root element
        namespaces: Namespace mapping

    Returns:
        Dictionary of metadata
    """
    metadata: dict[str, Any] = {}

    # Document type
    doc_type = _find_element(root, ".//ns:type", namespaces)
    if doc_type is not None and doc_type.text:
        metadata["document_type"] = doc_type.text

    # Time interval
    time_interval = _find_element(root, ".//ns:time_Period.timeInterval", namespaces)
    if time_interval is not None:
        start = _find_element(time_interval, ".//ns:start", namespaces)
        end = _find_element(time_interval, ".//ns:end", namespaces)
        if start is not None and start.text:
            metadata["start_time"] = normalize_timestamp(start.text)
        if end is not None and end.text:
            metadata["end_time"] = normalize_timestamp(end.text)

    # Process type
    process_type = _find_element(root, ".//ns:process.processType", namespaces)
    if process_type is not None and process_type.text:
        metadata["process_type"] = process_type.text

    # Sender/receiver
    sender = _find_element(root, ".//ns:sender_MarketParticipant.mRID", namespaces)
    if sender is not None and sender.text:
        metadata["sender"] = sender.text

    return metadata


def _find_all_elements(
    parent: etree._Element, xpath: str, namespaces: dict[str, str]
) -> list[etree._Element]:
    """Find all elements with namespace fallback.

    Args:
        parent: Parent element
        xpath: XPath expression (with ns: prefix)
        namespaces: Namespace mapping

    Returns:
        List of found elements
    """
    # Try with namespace
    if namespaces:
        elems = parent.findall(xpath, namespaces)
        if elems:
            return elems

    # Fallback: try with wildcard namespace
    wildcard_xpath = xpath.replace("ns:", "{*}")
    return parent.findall(wildcard_xpath)


def _parse_time_series(
    time_series: etree._Element,
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
    resolution_elem = _find_element(time_series, ".//ns:resolution", namespaces)
    resolution_str = (
        resolution_elem.text if resolution_elem is not None and resolution_elem.text else "PT60M"
    )
    resolution = parse_resolution(resolution_str)

    # Get area/zone - try multiple possible element names
    area = None
    for domain_path in [
        ".//ns:inBiddingZone_Domain.mRID",
        ".//ns:outBiddingZone_Domain.mRID",
        ".//ns:in_Domain.mRID",
        ".//ns:out_Domain.mRID",
    ]:
        domain_elem = _find_element(time_series, domain_path, namespaces)
        if domain_elem is not None and domain_elem.text:
            area = domain_elem.text
            break

    # Get PSR type (generation type)
    psr_type_elem = _find_element(time_series, ".//ns:MktPSRType/ns:psrType", namespaces)
    if psr_type_elem is None:
        psr_type_elem = _find_element(time_series, ".//{*}MktPSRType/{*}psrType", {})
    psr_type = psr_type_elem.text if psr_type_elem is not None else None

    # Get business type
    business_type_elem = _find_element(time_series, ".//ns:businessType", namespaces)
    business_type = business_type_elem.text if business_type_elem is not None else None

    # Parse periods
    periods = _find_all_elements(time_series, ".//ns:Period", namespaces)

    for period in periods:
        # Get period start time
        start_elem = _find_element(period, ".//ns:timeInterval/ns:start", namespaces)
        if start_elem is None:
            start_elem = _find_element(period, ".//{*}timeInterval/{*}start", {})
        if start_elem is None or not start_elem.text:
            continue

        period_start = normalize_timestamp(start_elem.text)

        # Parse points
        points = _find_all_elements(period, ".//ns:Point", namespaces)

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
                position_elem = _find_element(point, ".//ns:position", namespaces)
                quantity_elem = _find_element(point, ".//ns:quantity", namespaces)
                price_elem = _find_element(point, ".//ns:price.amount", namespaces)

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
    points: list[etree._Element],
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
        position_elem = _find_element(point, ".//ns:position", namespaces)
        quantity_elem = _find_element(point, ".//ns:quantity", namespaces)
        price_elem = _find_element(point, ".//ns:price.amount", namespaces)

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
