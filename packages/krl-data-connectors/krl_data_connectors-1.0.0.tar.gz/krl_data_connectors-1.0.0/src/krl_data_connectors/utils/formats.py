# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

# Copyright (c) 2025 KR-Labs Foundation. All rights reserved.
# Licensed under Apache License 2.0 (see LICENSE file for details)

"""
Format detection and conversion utilities for data resources.

Provides unified DataFrame loading from various data formats commonly
found in government open data catalogs (CSV, JSON, GeoJSON, Excel, XML).
"""

import io
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union
from urllib.parse import urlparse

import pandas as pd
import requests

logger = logging.getLogger(__name__)

# Supported formats with their MIME types and file extensions
SUPPORTED_FORMATS = {
    "csv": {
        "extensions": [".csv", ".txt"],
        "mime_types": ["text/csv", "text/plain", "application/csv"],
    },
    "json": {
        "extensions": [".json"],
        "mime_types": ["application/json", "text/json"],
    },
    "geojson": {
        "extensions": [".geojson", ".json"],
        "mime_types": ["application/geo+json", "application/vnd.geo+json"],
    },
    "excel": {
        "extensions": [".xlsx", ".xls"],
        "mime_types": [
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel",
        ],
    },
    "xml": {
        "extensions": [".xml"],
        "mime_types": ["application/xml", "text/xml"],
    },
}


def detect_format(
    url: Optional[str] = None,
    filename: Optional[str] = None,
    content_type: Optional[str] = None,
    format_hint: Optional[str] = None,
) -> Optional[str]:
    """
    Detect the data format from URL, filename, content-type, or explicit hint.

    Args:
        url: Resource URL (checks file extension)
        filename: Filename (checks extension)
        content_type: HTTP Content-Type header
        format_hint: Explicit format hint (e.g., from CKAN resource metadata)

    Returns:
        Detected format string ('csv', 'json', 'geojson', 'excel', 'xml') or None
    """
    # Priority 1: Explicit format hint
    if format_hint:
        hint_lower = format_hint.lower().strip()
        if hint_lower in SUPPORTED_FORMATS:
            return hint_lower
        # Handle common variations
        if hint_lower in ["geojson", "geo+json"]:
            return "geojson"
        if hint_lower in ["xlsx", "xls"]:
            return "excel"

    # Priority 2: Content-Type header
    if content_type:
        content_lower = content_type.lower().split(";")[0].strip()
        for fmt, info in SUPPORTED_FORMATS.items():
            if content_lower in info["mime_types"]:
                return fmt

    # Priority 3: File extension from filename or URL
    source = filename or (urlparse(url).path if url else None)
    if source:
        ext = Path(source).suffix.lower()
        for fmt, info in SUPPORTED_FORMATS.items():
            if ext in info["extensions"]:
                return fmt

    return None


def load_csv(content: Union[str, bytes, io.IOBase], **kwargs) -> pd.DataFrame:
    """Load CSV content into DataFrame."""
    if isinstance(content, bytes):
        content = content.decode("utf-8", errors="replace")
    if isinstance(content, str):
        content = io.StringIO(content)
    
    # Sensible defaults for government data
    defaults = {
        "encoding": "utf-8",
        "on_bad_lines": "warn",
    }
    defaults.update(kwargs)
    
    return pd.read_csv(content, **defaults)


def load_json(content: Union[str, bytes, io.IOBase], **kwargs) -> pd.DataFrame:
    """Load JSON content into DataFrame."""
    if isinstance(content, bytes):
        content = content.decode("utf-8", errors="replace")
    if isinstance(content, io.IOBase):
        content = content.read()
    
    import json
    data = json.loads(content)
    
    # Handle common JSON structures
    if isinstance(data, list):
        return pd.DataFrame(data)
    elif isinstance(data, dict):
        # Check for common wrapper patterns
        if "data" in data and isinstance(data["data"], list):
            return pd.DataFrame(data["data"])
        if "results" in data and isinstance(data["results"], list):
            return pd.DataFrame(data["results"])
        if "features" in data:  # GeoJSON
            return load_geojson_features(data["features"])
        # Single record or nested dict
        return pd.json_normalize(data)
    
    raise ValueError(f"Cannot convert JSON to DataFrame: unexpected type {type(data)}")


def load_geojson_features(features: list) -> pd.DataFrame:
    """Extract properties from GeoJSON features into DataFrame."""
    records = []
    for feature in features:
        record = feature.get("properties", {}).copy()
        # Optionally include geometry as WKT or keep reference
        if "geometry" in feature:
            geom = feature["geometry"]
            record["_geometry_type"] = geom.get("type") if geom else None
            # Store coordinates as string for simple cases
            if geom and geom.get("type") == "Point":
                coords = geom.get("coordinates", [])
                record["_longitude"] = coords[0] if len(coords) > 0 else None
                record["_latitude"] = coords[1] if len(coords) > 1 else None
        records.append(record)
    return pd.DataFrame(records)


def load_geojson(content: Union[str, bytes, io.IOBase], **kwargs) -> pd.DataFrame:
    """Load GeoJSON content into DataFrame (extracts feature properties)."""
    if isinstance(content, bytes):
        content = content.decode("utf-8", errors="replace")
    if isinstance(content, io.IOBase):
        content = content.read()
    
    import json
    data = json.loads(content)
    
    if "features" in data:
        return load_geojson_features(data["features"])
    
    raise ValueError("Invalid GeoJSON: no 'features' array found")


def load_excel(content: Union[bytes, io.IOBase], **kwargs) -> pd.DataFrame:
    """Load Excel content into DataFrame."""
    if isinstance(content, bytes):
        content = io.BytesIO(content)
    
    # Default to first sheet
    defaults = {"sheet_name": 0}
    defaults.update(kwargs)
    
    return pd.read_excel(content, **defaults)


def load_xml(content: Union[str, bytes, io.IOBase], **kwargs) -> pd.DataFrame:
    """Load XML content into DataFrame."""
    if isinstance(content, bytes):
        content = content.decode("utf-8", errors="replace")
    if isinstance(content, io.IOBase):
        content = content.read()
    
    # Use pandas XML parser (requires lxml)
    try:
        return pd.read_xml(io.StringIO(content), **kwargs)
    except Exception as e:
        logger.warning(f"pandas.read_xml failed: {e}, trying alternative parsing")
        # Fallback: try to extract records from common XML patterns
        import xml.etree.ElementTree as ET
        root = ET.fromstring(content)
        
        # Find repeating elements (likely data rows)
        children = list(root)
        if not children:
            raise ValueError("Cannot parse XML: no child elements found")
        
        # Use first child's tag as row indicator
        row_tag = children[0].tag
        records = []
        for child in root.findall(f".//{row_tag}"):
            record = {}
            for elem in child:
                record[elem.tag] = elem.text
            if record:
                records.append(record)
        
        if records:
            return pd.DataFrame(records)
        raise ValueError("Cannot extract tabular data from XML")


# Format loader registry
FORMAT_LOADERS = {
    "csv": load_csv,
    "json": load_json,
    "geojson": load_geojson,
    "excel": load_excel,
    "xml": load_xml,
}


def load_resource_to_dataframe(
    source: Union[str, bytes, io.IOBase],
    format: Optional[str] = None,
    url: Optional[str] = None,
    timeout: int = 60,
    **kwargs,
) -> pd.DataFrame:
    """
    Load a data resource into a pandas DataFrame.

    Automatically detects format from URL, content-type, or explicit hint.
    Supports CSV, JSON, GeoJSON, Excel (.xlsx/.xls), and XML.

    Args:
        source: Data source - can be:
            - URL string (will be downloaded)
            - Raw bytes content
            - File-like object
        format: Explicit format hint ('csv', 'json', 'geojson', 'excel', 'xml')
        url: Original URL (for format detection if source is bytes)
        timeout: Download timeout in seconds (if source is URL)
        **kwargs: Additional arguments passed to format-specific loader

    Returns:
        pandas DataFrame with loaded data

    Raises:
        ValueError: If format cannot be detected or is unsupported
        requests.HTTPError: If URL download fails

    Example:
        >>> df = load_resource_to_dataframe(
        ...     "https://data.gov/resource.csv",
        ...     format="csv"
        ... )
        >>> df = load_resource_to_dataframe(
        ...     raw_bytes,
        ...     format="json",
        ...     url="https://api.data.gov/data.json"
        ... )
    """
    content = source
    content_type = None
    source_url = url

    # If source is a URL, download it
    if isinstance(source, str) and source.startswith(("http://", "https://")):
        source_url = source
        logger.debug(f"Downloading resource: {source_url}")
        
        response = requests.get(
            source_url,
            timeout=timeout,
            headers={
                "User-Agent": "KRL-Data-Connectors/1.0 (https://github.com/KR-Labs/krl-data-connectors)"
            },
        )
        response.raise_for_status()
        
        content = response.content
        content_type = response.headers.get("Content-Type")

    # Detect format
    detected_format = detect_format(
        url=source_url,
        content_type=content_type,
        format_hint=format,
    )

    if not detected_format:
        raise ValueError(
            f"Cannot detect format for resource. "
            f"Please specify format='csv'|'json'|'geojson'|'excel'|'xml'. "
            f"URL: {source_url}, Content-Type: {content_type}"
        )

    if detected_format not in FORMAT_LOADERS:
        raise ValueError(
            f"Unsupported format: {detected_format}. "
            f"Supported: {list(FORMAT_LOADERS.keys())}"
        )

    logger.debug(f"Loading resource as {detected_format}")
    loader = FORMAT_LOADERS[detected_format]
    
    try:
        df = loader(content, **kwargs)
        logger.info(
            f"Loaded resource: {len(df)} rows, {len(df.columns)} columns",
            extra={"format": detected_format, "shape": df.shape},
        )
        return df
    except Exception as e:
        raise ValueError(
            f"Failed to parse {detected_format} content: {e}"
        ) from e


def get_supported_formats() -> Dict[str, Any]:
    """
    Get information about supported data formats.

    Returns:
        Dictionary with format names, extensions, and MIME types
    """
    return {
        fmt: {
            "extensions": info["extensions"],
            "mime_types": info["mime_types"],
        }
        for fmt, info in SUPPORTED_FORMATS.items()
    }
