# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
NOAA Climate Data Connector.

Provides access to:
- Climate Data Online (CDO) API
- Historical weather observations
- Climate normals
- Storm events database

API Reference: https://www.ncdc.noaa.gov/cdo-web/webservices/v2
"""

from __future__ import annotations

from datetime import datetime, date, UTC
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


# NOAA CDO API
CDO_API_BASE = "https://www.ncdc.noaa.gov/cdo-web/api/v2"


class NOAAClimateConnector:
    """
    Connector for NOAA Climate Data Online.
    
    Access historical weather data, climate normals, and
    storm events information.
    
    Example:
        >>> noaa = NOAAClimateConnector(api_token="your_token")
        >>> data = noaa.get_daily_data(
        ...     station="GHCND:USW00013874",
        ...     start_date="2024-01-01",
        ...     end_date="2024-01-31"
        ... )
    """
    
    def __init__(
        self,
        api_token: Optional[str] = None,
        cache_dir: Optional[str] = None,
        cache_ttl: int = 86400,
    ):
        """
        Initialize NOAA Climate connector.
        
        Args:
            api_token: NOAA CDO API token (get from https://www.ncdc.noaa.gov/cdo-web/token)
            cache_dir: Directory for cached data
            cache_ttl: Cache time-to-live in seconds
        """
        import os
        
        self.api_token = api_token or os.environ.get("NOAA_CDO_TOKEN")
        
        if not self.api_token:
            logger.warning("NOAA API token not provided. Get token at: "
                         "https://www.ncdc.noaa.gov/cdo-web/token")
        
        self.cache_ttl = cache_ttl
        self.cache_dir = Path(cache_dir or Path.home() / ".krl_cache" / "noaa")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
            "token": self.api_token or "",
            "User-Agent": "KRL-DataConnectors/1.0",
        })
    
    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make authenticated request to NOAA CDO API."""
        url = f"{CDO_API_BASE}/{endpoint}"
        
        response = self.session.get(url, params=params, timeout=60)
        response.raise_for_status()
        
        return response.json()
    
    def get_stations(
        self,
        state: Optional[str] = None,
        dataset: str = "GHCND",
        limit: int = 100,
    ) -> pd.DataFrame:
        """
        Get weather stations.
        
        Args:
            state: 2-letter state code
            dataset: Dataset ID (default: GHCND for daily summaries)
            limit: Maximum results
        
        Returns:
            DataFrame with station information
        """
        params = {
            "datasetid": dataset,
            "limit": limit,
        }
        if state:
            params["locationid"] = f"FIPS:{state}"
        
        data = self._make_request("stations", params)
        return pd.DataFrame(data.get("results", []))
    
    def get_daily_data(
        self,
        station: str,
        start_date: str,
        end_date: str,
        data_types: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Get daily weather observations.
        
        Args:
            station: Station ID (e.g., "GHCND:USW00013874")
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            data_types: List of data type IDs (TMAX, TMIN, PRCP, etc.)
        
        Returns:
            DataFrame with daily observations
        """
        params = {
            "datasetid": "GHCND",
            "stationid": station,
            "startdate": start_date,
            "enddate": end_date,
            "limit": 1000,
            "units": "metric",
        }
        
        if data_types:
            params["datatypeid"] = ",".join(data_types)
        
        data = self._make_request("data", params)
        return pd.DataFrame(data.get("results", []))
    
    def get_data_types(
        self,
        dataset: str = "GHCND",
    ) -> pd.DataFrame:
        """
        Get available data types for a dataset.
        
        Args:
            dataset: Dataset ID
        
        Returns:
            DataFrame with data type information
        """
        data = self._make_request("datatypes", {"datasetid": dataset, "limit": 100})
        return pd.DataFrame(data.get("results", []))
    
    def __repr__(self) -> str:
        return f"NOAAClimateConnector(authenticated={bool(self.api_token)})"
