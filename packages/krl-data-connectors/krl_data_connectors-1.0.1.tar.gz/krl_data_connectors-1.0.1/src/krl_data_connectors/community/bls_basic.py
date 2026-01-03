# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
BLS Basic Connector - Community Tier

Free access to essential Bureau of Labor Statistics series.
No API key required.

Available Series:
- National unemployment rate
- National employment level
- National labor force
- Consumer Price Index (all items)
- Monthly employment trends

Usage:
    from krl_data_connectors.community import BLSBasicConnector
    
    bls = BLSBasicConnector()
    unemployment = bls.get_unemployment_rate()
    cpi = bls.get_cpi()
"""

from datetime import datetime, UTC
from typing import Any, Dict, Optional

import pandas as pd

from krl_data_connectors import BaseConnector
from krl_data_connectors.core import DataTier


class BLSBasicConnector(BaseConnector):
    """
    BLS Basic Connector - Community Tier

    Free access to essential Bureau of Labor Statistics data.
    No license validation required for Community tier.
    Limited to national-level series only.
    """

    _connector_name = "BLS_Basic"
    _required_tier = DataTier.COMMUNITY

    BASE_URL_V1 = "https://api.bls.gov/publicAPI/v1/timeseries/data/"

    # Community tier: National-level series only
    AVAILABLE_SERIES = {
        "LNS14000000": "Unemployment Rate (National)",
        "LNS12000000": "Employment Level (National)",
        "LNS11000000": "Civilian Labor Force (National)",
        "CUUR0000SA0": "CPI-U All Items (National)",
        "CUUR0000SAF": "CPI-U Food (National)",
        "CUUR0000SA0E": "CPI-U Energy (National)",
        "CES0000000001": "Total Nonfarm Employment (National)",
        "CES0500000003": "Average Hourly Earnings (National)",
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
        Initialize BLS Basic connector.

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
        self.base_url = self.BASE_URL_V1
        self.logger.info(
            "Initialized BLS Basic connector (Community tier)",
            extra={"available_series": len(self.AVAILABLE_SERIES)},
        )

    def _get_api_key(self) -> Optional[str]:
        """
        Get API key for BLS API.

        For Community tier, BLS v1 API doesn't require a key.

        Returns:
            BLS API key or None
        """
        return None

    def connect(self) -> bool:
        """
        Test connection to BLS API.

        Returns:
            True if connection successful
        """
        try:
            # Initialize session if needed
            self._init_session()
            
            # Test with unemployment rate series
            payload = {
                "seriesid": ["LNS14000000"],
                "startyear": str(datetime.now().year),
                "endyear": str(datetime.now().year),
            }

            response = self.session.post(self.base_url, json=payload, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            if data.get("status") == "REQUEST_SUCCEEDED":
                self.logger.info("Successfully connected to BLS API")
                return True
            else:
                self.logger.warning(f"BLS API returned status: {data.get('status')}")
                return False

        except Exception as e:
            self.logger.error(f"Failed to connect to BLS API: {str(e)}")
            return False

    def _validate_series(self, series_id: str) -> None:
        """
        Validate that series is available in Community tier.

        Args:
            series_id: BLS series ID

        Raises:
            ValueError: If series not available in Community tier
        """
        if series_id not in self.AVAILABLE_SERIES:
            available = ", ".join(list(self.AVAILABLE_SERIES.keys())[:3])
            raise ValueError(
                f"Series '{series_id}' is not available in Community tier. "
                f"Community tier includes: {available}... (national series only). "
                f"For state/metro/county data, upgrade to Professional tier: "
                "https://krlabs.dev/pricing"
            )

    def get_series(
        self,
        series_id: str,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """
        Get time series data for a BLS series.

        Args:
            series_id: BLS series ID (must be in AVAILABLE_SERIES)
            start_year: Start year (default: current year - 9, max 10 years)
            end_year: End year (default: current year)

        Returns:
            DataFrame with columns: year, period, periodName, value, date

        Raises:
            ValueError: If series_id not available in Community tier
        """
        # Validate series
        self._validate_series(series_id)

        # Default to last 10 years (v1 API limit)
        if end_year is None:
            end_year = datetime.now().year
        if start_year is None:
            start_year = end_year - 9

        # Community tier: max 10 years
        if end_year - start_year + 1 > 10:
            raise ValueError(
                "Community tier limited to 10 years of data. "
                "For 20-year history, upgrade to Professional tier."
            )

        payload = {"seriesid": [series_id], "startyear": str(start_year), "endyear": str(end_year)}

        self.logger.info(
            f"Fetching BLS series: {series_id}",
            extra={"series_id": series_id, "start_year": start_year, "end_year": end_year},
        )

        # Initialize session if needed
        self._init_session()

        try:
            response = self.session.post(self.base_url, json=payload, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            # Check status
            if data.get("status") != "REQUEST_SUCCEEDED":
                error_msg = data.get("message", ["Unknown error"])[0]
                raise ValueError(f"BLS API error: {error_msg}")

            # Extract data
            series_data = data.get("Results", {}).get("series", [])
            if not series_data:
                self.logger.warning(f"No data returned for series {series_id}")
                return pd.DataFrame()

            # Parse observations
            observations = series_data[0].get("data", [])
            df = pd.DataFrame(observations)

            # Convert value to numeric
            if "value" in df.columns:
                df["value"] = pd.to_numeric(df["value"], errors="coerce")

            # Create date column
            if "year" in df.columns and "period" in df.columns:
                df["date"] = pd.to_datetime(
                    df["year"] + "-" + df["period"].str.replace("M", "").str.zfill(2),
                    format="%Y-%m",
                    errors="coerce",
                )

            # Sort by date
            if "date" in df.columns:
                df = df.sort_values("date").reset_index(drop=True)
                df = df.set_index("date")

            self.logger.info(
                f"Retrieved {len(df)} observations for {series_id}",
                extra={"series_id": series_id, "rows": len(df)},
            )

            return df

        except Exception as e:
            self.logger.error(f"Failed to fetch BLS series {series_id}: {e}")
            raise

    def get_unemployment_rate(
        self, start_year: Optional[int] = None, end_year: Optional[int] = None, **kwargs: Any
    ) -> pd.DataFrame:
        """
        Get national unemployment rate.

        Community tier: National level only.

        Args:
            start_year: Start year
            end_year: End year

        Returns:
            DataFrame with unemployment rate data
        """
        return self.get_series("LNS14000000", start_year, end_year)

    def get_cpi(
        self,
        item: str = "SA0",
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """
        Get Consumer Price Index data.

        Community tier: National CPI only.

        Args:
            item: Item code (SA0=all items, SAF=food, SA0E=energy)
            start_year: Start year
            end_year: End year

        Returns:
            DataFrame with CPI data
        """
        series_id = f"CUUR0000{item}"

        # Validate item is in Community tier
        if series_id not in self.AVAILABLE_SERIES:
            raise ValueError(
                f"CPI series '{item}' not available in Community tier. "
                f"Available: all items (SA0), food (SAF), energy (SA0E). "
                "For regional/metro CPI, upgrade to Professional tier."
            )

        return self.get_series(series_id, start_year, end_year)

    def list_available_series(self) -> Dict[str, str]:
        """
        List all series available in Community tier.

        Returns:
            Dictionary mapping series_id to description
        """
        return self.AVAILABLE_SERIES.copy()

    def fetch(self, series_id: str, **kwargs) -> pd.DataFrame:
        """
        Generic fetch method (alias for get_series).

        Args:
            series_id: BLS series ID
            **kwargs: Additional arguments passed to get_series

        Returns:
            DataFrame with series data
        """
        return self.get_series(series_id, **kwargs)
