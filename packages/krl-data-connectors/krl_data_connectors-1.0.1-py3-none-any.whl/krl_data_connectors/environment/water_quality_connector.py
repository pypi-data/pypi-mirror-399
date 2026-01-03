# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
EPA Water Quality Data Connector.

Provides access to:
- Water Quality Portal (WQP) data
- STORET/WQX monitoring data
- Safe Drinking Water Information System (SDWIS)
- Beach monitoring data

API Reference: https://www.waterqualitydata.us/webservices_documentation/
"""

from __future__ import annotations

from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import requests

try:
    from krl_core import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


# Water Quality Portal API
WQP_API_BASE = "https://www.waterqualitydata.us"


class EPAWaterQualityConnector:
    """
    Connector for EPA Water Quality Portal data.
    
    Access water quality measurements, monitoring stations,
    and various water-related environmental data.
    
    Example:
        >>> wq = EPAWaterQualityConnector()
        >>> stations = wq.get_stations(state="GA", county="Fulton")
        >>> results = wq.get_results(site_id="USGS-02336300")
    """
    
    def __init__(
        self,
        cache_dir: Optional[str] = None,
        cache_ttl: int = 86400,
    ):
        """
        Initialize Water Quality connector.
        
        Args:
            cache_dir: Directory for cached data
            cache_ttl: Cache time-to-live in seconds
        """
        self.cache_ttl = cache_ttl
        self.cache_dir = Path(cache_dir or Path.home() / ".krl_cache" / "wqp")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "KRL-DataConnectors/1.0",
            "Accept": "application/json",
        })
    
    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        accept_csv: bool = False,
    ) -> Union[Dict[str, Any], pd.DataFrame]:
        """Make request to WQP API."""
        params = params or {}
        params["mimeType"] = "csv" if accept_csv else "geojson"
        
        url = f"{WQP_API_BASE}/{endpoint}"
        
        response = self.session.get(url, params=params, timeout=120)
        response.raise_for_status()
        
        if accept_csv:
            from io import StringIO
            return pd.read_csv(StringIO(response.text))
        return response.json()
    
    def get_stations(
        self,
        state: Optional[str] = None,
        county: Optional[str] = None,
        huc: Optional[str] = None,
        bbox: Optional[tuple] = None,
    ) -> pd.DataFrame:
        """
        Get water quality monitoring stations.
        
        Args:
            state: State name or code
            county: County name
            huc: Hydrologic Unit Code
            bbox: Bounding box (west, south, east, north)
        
        Returns:
            DataFrame with station information
        """
        params = {}
        if state:
            params["statecode"] = f"US:{state}"
        if county:
            params["countycode"] = county
        if huc:
            params["huc"] = huc
        if bbox:
            params["bBox"] = ",".join(map(str, bbox))
        
        return self._make_request("data/Station/search", params, accept_csv=True)
    
    def get_results(
        self,
        site_id: Optional[str] = None,
        state: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        characteristic: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Get water quality measurement results.
        
        Args:
            site_id: Monitoring site identifier
            state: State name or code
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            characteristic: Characteristic name (e.g., "Nitrogen")
        
        Returns:
            DataFrame with water quality results
        """
        params = {}
        if site_id:
            params["siteid"] = site_id
        if state:
            params["statecode"] = f"US:{state}"
        if start_date:
            params["startDateLo"] = start_date
        if end_date:
            params["startDateHi"] = end_date
        if characteristic:
            params["characteristicName"] = characteristic
        
        return self._make_request("data/Result/search", params, accept_csv=True)
    
    def __repr__(self) -> str:
        return "EPAWaterQualityConnector()"


# Backwards compatible alias
WaterQualityConnector = EPAWaterQualityConnector
