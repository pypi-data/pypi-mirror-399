# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
FRED Basic Connector - Community Tier

Free access to essential Federal Reserve Economic Data series.
No API key required.

Available Series:
- UNRATE: Unemployment Rate
- GDP: Gross Domestic Product
- CPIAUCSL: Consumer Price Index
- FEDFUNDS: Federal Funds Rate
- DGS10: 10-Year Treasury Rate
- MORTGAGE30US: 30-Year Mortgage Rate
- PAYEMS: Total Nonfarm Payrolls
- And other essential indicators

Usage:
    from krl_data_connectors.community import FREDBasicConnector
    
    fred = FREDBasicConnector()
    unemployment = fred.get_series("UNRATE")
    gdp = fred.get_series("GDP")
"""

from datetime import datetime, timedelta, UTC
from typing import Any, Dict, List, Optional

import pandas as pd

from krl_data_connectors import BaseConnector
from krl_data_connectors.core import DataTier


class FREDBasicConnector(BaseConnector):
    """
    FRED Basic Connector - Community Tier

    Free access to essential Federal Reserve Economic Data.
    No license validation required for Community tier.
    """

    _connector_name = "FRED_Basic"
    _required_tier = DataTier.COMMUNITY

    # Whitelist of available series for Community tier
    AVAILABLE_SERIES = {
        "UNRATE": "Unemployment Rate",
        "GDP": "Gross Domestic Product",
        "CPIAUCSL": "Consumer Price Index for All Urban Consumers",
        "FEDFUNDS": "Federal Funds Effective Rate",
        "DGS10": "10-Year Treasury Constant Maturity Rate",
        "MORTGAGE30US": "30-Year Fixed Rate Mortgage Average",
        "PAYEMS": "All Employees, Total Nonfarm",
        "INDPRO": "Industrial Production Index",
        "HOUST": "Housing Starts",
        "RETAILSALES": "Advance Retail Sales",
        "M2": "M2 Money Stock",
        "DEXUSEU": "US / Euro Foreign Exchange Rate",
        "VIXCLS": "CBOE Volatility Index",
        "SP500": "S&P 500",
        "WILLTAXREC": "Federal Tax Receipts",
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_dir: Optional[str] = None,
        cache_ttl: int = 3600,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        Initialize FRED Basic connector.

        Args:
            api_key: Optional API key (not required for Community tier)
            cache_dir: Directory for caching responses
            cache_ttl: Cache time-to-live in seconds
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        super().__init__(
            api_key=api_key,
            cache_dir=cache_dir,
            cache_ttl=cache_ttl,
            timeout=timeout,
            max_retries=max_retries,
        )
        self.base_url = "https://api.stlouisfed.org/fred"
        self.logger.info(
            "Initialized FRED Basic connector (Community tier)",
            extra={"available_series": len(self.AVAILABLE_SERIES)},
        )

    def _get_api_key(self) -> Optional[str]:
        """
        Get API key for FRED API.

        For Community tier, looks for FRED_API_KEY environment variable.

        Returns:
            FRED API key or None
        """
        import os
        return os.getenv("FRED_API_KEY")

    def connect(self) -> bool:
        """
        Test connection to FRED API.

        Returns:
            True if connection successful
        """
        try:
            # Initialize session if needed
            self._init_session()
            
            # Test with a simple series request
            response = self.session.get(
                f"{self.base_url}/series",
                params={"series_id": "GDP", "api_key": self._get_api_key(), "file_type": "json"},
                timeout=self.timeout,
            )
            response.raise_for_status()
            self.logger.info("Successfully connected to FRED API")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to FRED API: {str(e)}")
            return False

    def get_series(
        self, series_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get economic data series.

        Args:
            series_id: FRED series ID (must be in AVAILABLE_SERIES)
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            DataFrame with date index and value column

        Raises:
            ValueError: If series_id not available in Community tier
        """
        # Initialize session if needed
        self._init_session()
        
        # Validate series is available in Community tier
        if series_id not in self.AVAILABLE_SERIES:
            available = ", ".join(list(self.AVAILABLE_SERIES.keys())[:5])
            raise ValueError(
                f"Series '{series_id}' is not available in Community tier. "
                f"Available series include: {available}... "
                f"Upgrade to Professional tier for full FRED access: "
                "https://krlabs.dev/pricing"
            )

        self.logger.info(
            f"Fetching FRED series: {series_id}",
            extra={"series_id": series_id, "start_date": start_date, "end_date": end_date},
        )

        # Build request parameters
        params = {"series_id": series_id, "api_key": self._get_api_key(), "file_type": "json"}

        if start_date:
            params["observation_start"] = start_date
        if end_date:
            params["observation_end"] = end_date

        # Make request
        response = self.session.get(
            f"{self.base_url}/series/observations", params=params, timeout=self.timeout
        )
        response.raise_for_status()

        # Parse response
        data = response.json()
        observations = data.get("observations", [])

        # Convert to DataFrame
        df = pd.DataFrame(observations)
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
            df["value"] = pd.to_numeric(df["value"], errors="coerce")
            df = df[["date", "value"]].set_index("date")

        self.logger.info(
            f"Retrieved {len(df)} observations for {series_id}",
            extra={"series_id": series_id, "rows": len(df)},
        )

        return df

    def get_series_info(self, series_id: str) -> Dict[str, Any]:
        """
        Get metadata about a series.

        Args:
            series_id: FRED series ID

        Returns:
            Dictionary with series metadata
        """
        if series_id not in self.AVAILABLE_SERIES:
            raise ValueError(
                f"Series '{series_id}' not available in Community tier. "
                "Upgrade to Professional for full access."
            )

        # Initialize session if needed
        self._init_session()

        response = self.session.get(
            f"{self.base_url}/series",
            params={"series_id": series_id, "api_key": self._get_api_key(), "file_type": "json"},
            timeout=self.timeout,
        )
        response.raise_for_status()

        data = response.json()
        return data.get("seriess", [{}])[0]

    def list_available_series(self) -> List[Dict[str, str]]:
        """
        List all series available in Community tier.

        Returns:
            List of dictionaries with series_id and title
        """
        return [{"series_id": sid, "title": title} for sid, title in self.AVAILABLE_SERIES.items()]

    def fetch(self, series_id: str, **kwargs) -> pd.DataFrame:
        """
        Generic fetch method (alias for get_series).

        Args:
            series_id: FRED series ID
            **kwargs: Additional arguments passed to get_series

        Returns:
            DataFrame with series data
        """
        return self.get_series(series_id, **kwargs)
