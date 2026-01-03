# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
EPA Air Quality System (AQS) Data Connector.

Provides access to EPA's Air Quality System data including:
- Criteria pollutant measurements (PM2.5, PM10, O3, NO2, SO2, CO)
- Air Quality Index (AQI) data
- Monitoring station information
- Historical air quality data

API Reference: https://aqs.epa.gov/aqsweb/documents/data_api.html
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, UTC
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


# AQS API Base URL
AQS_API_BASE = "https://aqs.epa.gov/data/api"


class EPAAirQualityConnector:
    """
    Connector for EPA Air Quality System (AQS) data.
    
    Provides access to criteria pollutant data, AQI values, and
    monitoring station information.
    
    Example:
        >>> aq = EPAAirQualityConnector(email="your@email.com", api_key="your_key")
        >>> data = aq.get_daily_aqi(state="13", county="121", start_date="2024-01-01")
    """
    
    def __init__(
        self,
        email: Optional[str] = None,
        api_key: Optional[str] = None,
        cache_dir: Optional[str] = None,
        cache_ttl: int = 86400,
    ):
        """
        Initialize Air Quality connector.
        
        Args:
            email: Email registered with EPA AQS API
            api_key: API key from EPA AQS registration
            cache_dir: Directory for cached data
            cache_ttl: Cache time-to-live in seconds
        """
        import os
        
        self.email = email or os.environ.get("EPA_AQS_EMAIL")
        self.api_key = api_key or os.environ.get("EPA_AQS_API_KEY")
        
        if not self.email or not self.api_key:
            logger.warning("EPA AQS credentials not provided. Get credentials at: "
                         "https://aqs.epa.gov/aqsweb/documents/data_api.html")
        
        self.cache_ttl = cache_ttl
        self.cache_dir = Path(cache_dir or Path.home() / ".krl_cache" / "epa_aqs")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "KRL-DataConnectors/1.0",
        })
    
    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make authenticated request to AQS API."""
        params = params or {}
        params["email"] = self.email
        params["key"] = self.api_key
        
        url = f"{AQS_API_BASE}/{endpoint}"
        
        response = self.session.get(url, params=params, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        
        # Check for API errors
        if isinstance(data, dict) and "Header" in data:
            header = data["Header"]
            if isinstance(header, list) and header:
                status = header[0].get("status")
                if status == "Failed":
                    raise ValueError(f"AQS API error: {header[0].get('request_time', 'Unknown error')}")
        
        return data
    
    def get_daily_aqi(
        self,
        state: str,
        county: str,
        start_date: str,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Get daily AQI values for a county.
        
        Args:
            state: 2-digit state FIPS code
            county: 3-digit county FIPS code
            start_date: Start date (YYYYMMDD or YYYY-MM-DD)
            end_date: End date (default: same as start_date)
        
        Returns:
            DataFrame with daily AQI values
        """
        start_date = start_date.replace("-", "")
        end_date = (end_date or start_date).replace("-", "")
        
        data = self._make_request(
            "dailyData/byCounty",
            {
                "param": "88101",  # PM2.5
                "bdate": start_date,
                "edate": end_date,
                "state": state,
                "county": county,
            }
        )
        
        records = data.get("Data", [])
        return pd.DataFrame(records)
    
    def get_monitors(
        self,
        state: str,
        county: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Get air quality monitoring stations.
        
        Args:
            state: 2-digit state FIPS code
            county: Optional 3-digit county FIPS code
        
        Returns:
            DataFrame with monitor information
        """
        params = {"state": state}
        if county:
            params["county"] = county
        
        data = self._make_request("monitors/byState", params)
        records = data.get("Data", [])
        return pd.DataFrame(records)
    
    def __repr__(self) -> str:
        return f"EPAAirQualityConnector(authenticated={bool(self.api_key)})"
