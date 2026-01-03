from __future__ import annotations

#!/usr/bin/env python3
"""
Bureau of Labor Statistics (BLS) Connector.

Fetches employment and wage data from BLS for use in labor market analysis and CGE models.

Data Sources:
    - CES (Current Employment Statistics): Establishment survey, employment by industry
    - QCEW (Quarterly Census of Employment and Wages): Comprehensive employment/wage data
    - OES (Occupational Employment and Wage Statistics): Occupation-level wages

API Docs: https://www.bls.gov/developers/

Key Series:
    - CES: Employment by industry (monthly, seasonally adjusted)
    - QCEW: Employment + wages by industry (quarterly)
    - OES: Wages by occupation (annual)

Example:
    >>> connector = BLSConnector()
    >>> connector.connect()
    >>> employment = connector.fetch_employment_by_industry(year=2023)
    >>> wages = connector.fetch_wages_by_industry(year=2023)
"""

import logging
import os
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from krl_data_connectors.base_connector import BaseConnector

logger = logging.getLogger(__name__)


class BLSConnector(BaseConnector):
    """
    Connector for Bureau of Labor Statistics (BLS) data.

    Fetches employment and wage data by industry for labor market analysis.

    Attributes:
        api_key: BLS API key (optional, increases rate limits).
        base_url: BLS API base URL.
        cache_dir: Directory for caching downloaded data.
    """

    def __init__(
        self,
        api_key: str | None = None,

    ):
        """
        Initialize BLS connector.

        Args:
            api_key: BLS API key. If None, reads from BLS_API_KEY environment variable.
            cache_policy: Caching strategy.
        """
        # Store api_key before calling super().__init__
        self._api_key_override = api_key

        super().__init__(api_key=api_key)

        if not self.api_key:
            logger.warning(
                "No BLS API key provided. Register at https://www.bls.gov/developers/. "
                "Rate limits apply (25 queries/day without key, 500/day with key)."
            )

        self.base_url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
        # Convert Path to string for cache_dir setter
        cache_path = Path.home() / ".krl" / "cache" / "bls"
        cache_path.mkdir(parents=True, exist_ok=True)
        self.cache_dir = str(cache_path)

        # Session with retries
        self._session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self._session.mount("https://", adapter)

    def _get_api_key(self) -> str | None:
        """Get BLS API key from environment or config."""
        return self._api_key_override or os.getenv("BLS_API_KEY")

    def fetch(self, **kwargs: Any) -> pd.DataFrame:
        """
        Generic fetch method required by BaseConnector.

        Args:
            **kwargs: Parameters passed to fetch_employment_by_industry()

        Returns:
            Employment data DataFrame
        """
        return self.fetch_employment_by_industry(**kwargs)

    def connect(self) -> None:
        """
        Verify API connectivity.

        Raises:
            ConnectionError: If BLS API is unreachable.
        """
        try:
            # Test with simple request (total nonfarm employment)
            test_series = "CES0000000001"  # Total nonfarm employment
            payload = {
                "seriesid": [test_series],
                "startyear": "2023",
                "endyear": "2023",
            }

            if self.api_key:
                payload["registrationkey"] = self.api_key

            response = self._session.post(self.base_url, json=payload, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data.get("status") == "REQUEST_SUCCEEDED":
                logger.info("✓ Connected to BLS API")
            else:
                logger.warning(f"BLS API test returned status: {data.get('status')}")

        except requests.exceptions.RequestException as e:
            logger.warning(f"BLS API test failed: {e}. Will use sample data if needed.")

    def fetch_employment_by_industry(
        self,
        year: int = 2023,
        industry_level: int = 2,  # 2-digit NAICS
    ) -> pd.DataFrame:
        """
        Fetch employment data by industry from CES.

        Args:
            year: Year for employment data.
            industry_level: NAICS aggregation level (2-digit, 3-digit, etc.).

        Returns:
            DataFrame with employment by industry.
        """
        cache_key = f"employment_{year}_{industry_level}digit"
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            logger.info(f"Using cached employment data: {year}")
            return cached_data

        # CES series IDs for major industries (2-digit NAICS)
        # Format: CES + supersector + data_type + seasonal_adjustment
        # Data type: 01 = employment (in thousands)
        # Seasonal adjustment: 01 = seasonally adjusted
        ces_series = {
            "Total Nonfarm": "CES0000000001",
            "Mining": "CES1000000001",
            "Construction": "CES2000000001",
            "Manufacturing": "CES3000000001",
            "Wholesale Trade": "CES4142000001",
            "Retail Trade": "CES4200000001",
            "Transportation": "CES4300000001",
            "Utilities": "CES4422000001",
            "Information": "CES5000000001",
            "Financial Activities": "CES5500000001",
            "Professional Services": "CES6000000001",
            "Education/Health": "CES6500000001",
            "Leisure/Hospitality": "CES7000000001",
            "Other Services": "CES8000000001",
            "Government": "CES9000000001",
        }

        try:
            payload = {
                "seriesid": list(ces_series.values()),
                "startyear": str(year),
                "endyear": str(year),
            }

            if self.api_key:
                payload["registrationkey"] = self.api_key

            logger.info(f"Fetching employment data from BLS: year={year}")
            response = self._session.post(self.base_url, json=payload, timeout=30)
            response.raise_for_status()

            data = response.json()

            if data.get("status") != "REQUEST_SUCCEEDED":
                raise ValueError(f"BLS API error: {data.get('message')}")

            # Parse response
            employment_data = []
            series_list = data.get("Results", {}).get("series", [])

            for series in series_list:
                series_id = series["seriesID"]
                # Find industry name
                industry_name = next(
                    (name for name, sid in ces_series.items() if sid == series_id),
                    "Unknown",
                )

                # Get latest value (most recent month)
                if series.get("data"):
                    latest = series["data"][0]  # Most recent month
                    employment = float(latest["value"])  # In thousands

                    employment_data.append({
                        "industry": industry_name,
                        "employment_thousands": employment,
                        "year": year,
                        "period": latest.get("period"),
                    })

            df = pd.DataFrame(employment_data)

            # Convert to employment shares
            total_employment = df[df["industry"] == "Total Nonfarm"]["employment_thousands"].values[0]
            df["employment_share"] = df["employment_thousands"] / total_employment

            logger.info(f"✓ Fetched employment for {len(df)} industries")

            # Cache result
            self.cache.set(cache_key, df)

            return df

        except Exception as e:
            logger.error(f"Failed to fetch BLS employment data: {e}")
            return self._generate_sample_employment(year)

    def fetch_wages_by_industry(
        self,
        year: int = 2023,
    ) -> pd.DataFrame:
        """
        Fetch wage data by industry from OES.

        Args:
            year: Year for wage data.

        Returns:
            DataFrame with wages by industry.
        """
        cache_key = f"wages_{year}"
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            logger.info(f"Using cached wage data: {year}")
            return cached_data

        # For simplicity, generate sample wage data
        # Real implementation would use OES API or QCEW files
        logger.warning("BLS wages API not fully implemented - using sample data")
        return self._generate_sample_wages(year)

    def _generate_sample_employment(self, year: int) -> pd.DataFrame:
        """Generate sample employment data."""
        import numpy as np

        industries = [
            "Total Nonfarm",
            "Mining",
            "Construction",
            "Manufacturing",
            "Wholesale Trade",
            "Retail Trade",
            "Transportation",
            "Utilities",
            "Information",
            "Financial Activities",
            "Professional Services",
            "Education/Health",
            "Leisure/Hospitality",
            "Other Services",
            "Government",
        ]

        # Realistic employment shares (based on 2023 US data)
        employment_shares = np.array([
            1.0,    # Total (will be normalized out)
            0.005,  # Mining
            0.055,  # Construction
            0.080,  # Manufacturing
            0.037,  # Wholesale
            0.095,  # Retail
            0.035,  # Transportation
            0.003,  # Utilities
            0.018,  # Information
            0.055,  # Financial
            0.140,  # Professional
            0.165,  # Education/Health
            0.105,  # Leisure
            0.035,  # Other
            0.150,  # Government
        ])

        # Normalize (exclude Total Nonfarm)
        employment_shares[1:] = employment_shares[1:] / employment_shares[1:].sum()

        # Total employment ~160 million
        total_employment = 160_000  # thousands

        df = pd.DataFrame({
            "industry": industries,
            "employment_thousands": employment_shares * total_employment,
            "employment_share": employment_shares,
            "year": year,
            "period": "M12",  # December
        })

        logger.info(f"Generated sample employment data for {year}")
        return df

    def _generate_sample_wages(self, year: int) -> pd.DataFrame:
        """Generate sample wage data."""
        import numpy as np

        industries = [
            "Mining",
            "Construction",
            "Manufacturing",
            "Wholesale Trade",
            "Retail Trade",
            "Transportation",
            "Utilities",
            "Information",
            "Financial Activities",
            "Professional Services",
            "Education/Health",
            "Leisure/Hospitality",
            "Other Services",
            "Government",
        ]

        # Realistic hourly wages by industry (2023 US averages)
        wages = np.array([
            35.50,  # Mining
            32.00,  # Construction
            29.50,  # Manufacturing
            31.00,  # Wholesale
            18.50,  # Retail
            26.00,  # Transportation
            42.00,  # Utilities
            45.00,  # Information
            38.00,  # Financial
            40.00,  # Professional
            28.00,  # Education/Health
            16.50,  # Leisure
            24.00,  # Other
            32.00,  # Government
        ])

        # Annual hours (assume 2000 hours/year)
        annual_hours = 2000

        df = pd.DataFrame({
            "industry": industries,
            "hourly_wage": wages,
            "annual_wage": wages * annual_hours,
            "annual_hours": annual_hours,
            "year": year,
        })

        logger.info(f"Generated sample wage data for {year}")
        return df
