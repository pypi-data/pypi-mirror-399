# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

# Copyright (c) 2024 Sudiata Giddasira, Inc. d/b/a Quipu Research Labs, LLC d/b/a KR-Labs™
# SPDX-License-Identifier: Apache-2.0
#
# Khipu Research Analytics Suite - KR-Labs™
# Licensed under the Apache License, Version 2.0

"""
FCC Broadband Map Connector

Provides access to FCC Broadband Map data for digital divide analytics.

Data Sources:
- FCC Broadband Data Collection (BDC) - Provider coverage
- FCC Fixed Broadband Deployment - Block-level availability
- FCC Mobile Broadband Coverage - Mobile service availability

Key Use Cases:
- Digital divide analysis (broadband deserts)
- Service provider competition metrics
- Speed tier availability by geography
- Infrastructure gap identification

API Documentation: https://www.fcc.gov/BroadbandData
Data Portal: https://broadbandmap.fcc.gov/
"""

from pathlib import Path
from typing import Dict, List, Optional, Union

import pandas as pd
import requests

from krl_data_connectors.base_connector import BaseConnector

from ...core import DataTier
from ...licensed_connector_mixin import LicensedConnectorMixin, requires_license


class FCCBroadbandConnector(LicensedConnectorMixin, BaseConnector):
    """
    Connector for FCC Broadband Data Collection and Coverage Maps.

    The FCC Broadband Map provides comprehensive data on internet service
    availability, speeds, and technology types across the United States at
    the census block level. This connector enables digital divide research,
    infrastructure gap analysis, and broadband policy evaluation.

    Data Availability:
    - Fixed Broadband: Cable, fiber, DSL, satellite coverage by block
    - Mobile Broadband: 4G LTE, 5G coverage by block
    - Speed Tiers: Download/upload speeds by technology type
    - Provider Data: ISP availability and competition metrics
    """

    # Registry name for license validation
    _connector_name = "FCC_Broadband"

    """

    Geographic Granularity: Census block (highest resolution)
    Update Frequency: Biannual (June and December)
    Historical Data: June 2019 - present

    Note: FCC data is available via bulk CSV downloads. This connector
    supports local file loading and basic API access for availability data.

    Examples:
        >>> # Initialize connector
        >>> fcc = FCCBroadbandConnector()
        >>> fcc.connect()

        >>> # Load broadband availability data
        >>> coverage = fcc.get_coverage_by_state('CA', technology='fiber')
        >>>
        >>> # Analyze digital divide
        >>> underserved = fcc.get_underserved_areas(min_download_mbps=25)
        >>>
        >>> # Provider competition analysis
        >>> competition = fcc.get_provider_competition(state='NY')
    """

    def __init__(
        self,
        base_url: str = "https://broadbandmap.fcc.gov/api",
        data_dir: Optional[Union[str, Path]] = None,
        cache_dir: Optional[str] = None,
        cache_ttl: int = 86400,
    ):
        """
        Initialize FCC Broadband Map connector.

        Args:
            base_url: Base URL for FCC API (if available)
            data_dir: Directory containing downloaded FCC CSV files
            cache_dir: Directory for caching responses
            cache_ttl: Cache time-to-live in seconds (default: 24 hours)
        """
        super().__init__(
            cache_dir=cache_dir,
            cache_ttl=cache_ttl,
        )
        self.base_url = base_url
        self.connector_name = "FCCBroadband"
        self.data_dir = Path(data_dir) if data_dir else None
        self._coverage_data = None
        self._provider_data = None

    def _get_api_key(self) -> Optional[str]:
        """
        Get API key from environment or config.

        FCC Broadband Map currently uses bulk downloads, no API key needed.
        Implemented for BaseConnector interface compliance.

        Returns:
            None (no API key required for current data access method)
        """
        return None

    def fetch(self, **kwargs) -> Dict:
        """
        Fetch data from FCC API endpoint (if available).

        Note: Currently FCC provides bulk data downloads. This method is
        implemented for future API compatibility if FCC launches real-time API.

        Args:
            **kwargs: Connector-specific parameters

        Returns:
            JSON response as dictionary

        Raises:
            NotImplementedError: API access not yet available
        """
        raise NotImplementedError(
            "FCC Broadband Map uses bulk CSV downloads. "
            "Use load_coverage_data() to load FCC data files. "
            "Download data from: https://broadbandmap.fcc.gov/data-download"
        )

    def connect(self) -> None:
        """
        Establish connection to FCC data sources.

        For file-based access, validates data directory exists.
        For API access, tests connectivity (if API becomes available).

        Raises:
            ConnectionError: If data directory doesn't exist or API unreachable
        """
        self._init_session()

        # Validate data directory if provided
        if self.data_dir and not self.data_dir.exists():
            raise ConnectionError(
                f"FCC data directory not found: {self.data_dir}. "
                "Download FCC broadband data from https://broadbandmap.fcc.gov/data-download"
            )

        self.logger.info("FCC Broadband connector initialized successfully")

    def load_coverage_data(
        self, file_path: Union[str, Path], state_filter: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Load FCC broadband coverage data from CSV file.

        FCC provides bulk data downloads with broadband availability by census block.
        Files are typically named like 'BDC_YYYYMM_v1_fixed_broadband.csv'.

        Args:
            file_path: Path to FCC coverage CSV file
            state_filter: Optional 2-letter state code to filter results

        Returns:
            DataFrame with coverage data

        Columns include:
        - state_abbr: State abbreviation
        - county_geoid: County FIPS code
        - block_geoid: Census block ID (15-digit)
        - provider_id: FCC provider identifier
        - technology: Technology code (10=DSL, 40=Cable, 50=Fiber, 70=Satellite)
        - max_down: Maximum download speed (Mbps)
        - max_up: Maximum upload speed (Mbps)
        - low_latency: Boolean for low-latency service (<100ms)

        Examples:
            >>> # Load June 2024 fixed broadband data
            >>> coverage = fcc.load_coverage_data('BDC_202406_fixed_broadband.csv')
            >>>
            >>> # Filter to California only
            >>> ca_coverage = fcc.load_coverage_data(
            ...     'BDC_202406_fixed_broadband.csv',
            ...     state_filter='CA'
            ... )
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Coverage file not found: {file_path}")

        self.logger.info(f"Loading FCC coverage data from {file_path.name}")

        # Load data with chunking for large files
        # Preserve block_geoid as string to maintain leading zeros
        df = pd.read_csv(file_path, low_memory=False, dtype={"block_geoid": "str"})

        # Filter by state if provided
        if state_filter:
            state_filter = state_filter.upper()
            if "state_abbr" in df.columns:
                df = df[df["state_abbr"] == state_filter]
                self.logger.info(f"Filtered to {len(df):,} records for {state_filter}")

        self._coverage_data = df
        return df

    @requires_license
    def get_coverage_by_state(
        self, state: str, technology: Optional[str] = None, min_download_mbps: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Get broadband coverage summary by state.

        Args:
            state: 2-letter state abbreviation (e.g., 'CA', 'NY')
            technology: Optional filter ('fiber', 'cable', 'dsl', 'satellite', '5g')
            min_download_mbps: Minimum download speed threshold

        Returns:
            DataFrame with state-level coverage statistics

        Examples:
            >>> # Fiber coverage in California
            >>> ca_fiber = fcc.get_coverage_by_state('CA', technology='fiber')
            >>>
            >>> # Broadband 25/3 Mbps availability in Texas
            >>> tx_broadband = fcc.get_coverage_by_state('TX', min_download_mbps=25)
        """
        if self._coverage_data is None:
            raise ValueError("No coverage data loaded. Call load_coverage_data() first.")

        # Filter data
        df = self._coverage_data[self._coverage_data["state_abbr"] == state.upper()]

        # Technology mapping (FCC codes to names)
        tech_codes = {"dsl": 10, "cable": 40, "fiber": 50, "satellite": 70, "5g": 71, "lte": 70}

        if technology and technology.lower() in tech_codes:
            tech_code = tech_codes[technology.lower()]
            df = df[df["technology"] == tech_code]

        if min_download_mbps:
            df = df[df["max_down"] >= min_download_mbps]

        return df

    @requires_license
    def get_underserved_areas(
        self, min_download_mbps: int = 25, min_upload_mbps: int = 3, state: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Identify underserved areas (lacking minimum broadband speeds).

        FCC defines broadband as 25/3 Mbps (download/upload) minimum.
        This method identifies census blocks not meeting this threshold.

        Args:
            min_download_mbps: Minimum download speed (default: 25 Mbps)
            min_upload_mbps: Minimum upload speed (default: 3 Mbps)
            state: Optional state filter

        Returns:
            DataFrame of census blocks lacking adequate broadband

        Examples:
            >>> # FCC broadband standard (25/3 Mbps)
            >>> underserved = fcc.get_underserved_areas()
            >>>
            >>> # High-speed standard (100/20 Mbps)
            >>> digital_divide = fcc.get_underserved_areas(
            ...     min_download_mbps=100,
            ...     min_upload_mbps=20
            ... )
        """
        if self._coverage_data is None:
            raise ValueError("No coverage data loaded. Call load_coverage_data() first.")

        df = self._coverage_data.copy()

        if state:
            df = df[df["state_abbr"] == state.upper()]

        # Find blocks NOT meeting threshold
        underserved = df[(df["max_down"] < min_download_mbps) | (df["max_up"] < min_upload_mbps)]

        return underserved.drop_duplicates(subset=["block_geoid"])

    @requires_license
    def get_provider_competition(
        self, state: Optional[str] = None, technology: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Analyze ISP competition (number of providers per area).

        Args:
            state: Optional 2-letter state code
            technology: Optional technology filter

        Returns:
            DataFrame with provider counts by census block

        Columns:
        - block_geoid: Census block identifier
        - provider_count: Number of ISPs offering service
        - monopoly: Boolean (True if only 1 provider)
        - duopoly: Boolean (True if only 2 providers)
        - competitive: Boolean (True if 3+ providers)

        Examples:
            >>> # Provider competition in rural areas
            >>> competition = fcc.get_provider_competition(state='MT')
            >>>
            >>> # Fiber provider competition nationwide
            >>> fiber_comp = fcc.get_provider_competition(technology='fiber')
        """
        if self._coverage_data is None:
            raise ValueError("No coverage data loaded. Call load_coverage_data() first.")

        df = self._coverage_data.copy()

        if state:
            df = df[df["state_abbr"] == state.upper()]

        # Count unique providers per block
        competition = df.groupby("block_geoid")["provider_id"].nunique().reset_index()
        competition.columns = ["block_geoid", "provider_count"]

        # Add competition categories
        competition["monopoly"] = competition["provider_count"] == 1
        competition["duopoly"] = competition["provider_count"] == 2
        competition["competitive"] = competition["provider_count"] >= 3

        return competition

    @requires_license
    def get_speed_tier_distribution(self, state: Optional[str] = None) -> Dict[str, int]:
        """
        Get distribution of speeds available across coverage area.

        Args:
            state: Optional 2-letter state code

        Returns:
            Dictionary with speed tier counts:
            - 'under_25mbps': Below broadband threshold
            - '25_100mbps': Basic broadband
            - '100_1000mbps': High-speed broadband
            - 'gigabit_plus': Gigabit and above

        Examples:
            >>> # Speed distribution nationwide
            >>> speeds = fcc.get_speed_tier_distribution()
            >>> print(f"Gigabit availability: {speeds['gigabit_plus']:,} blocks")
        """
        if self._coverage_data is None:
            raise ValueError("No coverage data loaded. Call load_coverage_data() first.")

        df = self._coverage_data.copy()

        if state:
            df = df[df["state_abbr"] == state.upper()]

        # Categorize by speed tiers
        distribution = {
            "under_25mbps": len(df[df["max_down"] < 25]),
            "25_100mbps": len(df[(df["max_down"] >= 25) & (df["max_down"] < 100)]),
            "100_1000mbps": len(df[(df["max_down"] >= 100) & (df["max_down"] < 1000)]),
            "gigabit_plus": len(df[df["max_down"] >= 1000]),
        }

        return distribution

    @requires_license
    def get_technology_availability(self, state: Optional[str] = None) -> pd.DataFrame:
        """
        Get availability of different broadband technologies.

        Args:
            state: Optional 2-letter state code

        Returns:
            DataFrame with technology availability statistics

        Examples:
            >>> # Technology mix in rural state
            >>> tech_avail = fcc.get_technology_availability(state='WY')
            >>> print(tech_avail[['technology_name', 'block_count', 'percent']])
        """
        if self._coverage_data is None:
            raise ValueError("No coverage data loaded. Call load_coverage_data() first.")

        df = self._coverage_data.copy()

        if state:
            df = df[df["state_abbr"] == state.upper()]

        # Technology name mapping
        tech_names = {10: "DSL", 40: "Cable", 50: "Fiber", 70: "Satellite", 71: "5G/Fixed Wireless"}

        # Count blocks by technology
        tech_counts = df.groupby("technology")["block_geoid"].nunique().reset_index()
        tech_counts.columns = ["technology_code", "block_count"]
        tech_counts["technology_name"] = tech_counts["technology_code"].map(tech_names)

        # Calculate percentages
        total_blocks = tech_counts["block_count"].sum()
        tech_counts["percent"] = (tech_counts["block_count"] / total_blocks * 100).round(2)

        return tech_counts[["technology_name", "block_count", "percent"]]
