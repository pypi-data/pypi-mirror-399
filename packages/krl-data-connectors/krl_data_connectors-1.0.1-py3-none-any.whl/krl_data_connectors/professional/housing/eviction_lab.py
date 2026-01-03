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
Eviction Lab Connector

Provides access to the Eviction Lab database for housing instability research.

Data Sources:
- Eviction Lab (Princeton University) - National eviction database
- Census tract-level eviction rates (2000-2018)
- County-level aggregated data
- State-level summary statistics

Key Use Cases:
- Housing instability and displacement research
- Eviction rate trends over time
- Geographic disparities in eviction patterns
- Demographic correlates of eviction risk
- Policy impact evaluation

Data Coverage:
- Geographic: All 50 states, DC, and Puerto Rico
- Temporal: 2000-2018 (annual data)
- Granularity: Census tract, county, state levels
- Metrics: Eviction filings, evictions, rates, filing rates

API Documentation: https://evictionlab.org/
Data Downloads: https://evictionlab.org/get-the-data/
Research: https://evictionlab.org/national-estimates/
"""

from pathlib import Path
from typing import Dict, List, Optional, Union

import pandas as pd
import requests

from krl_data_connectors.base_connector import BaseConnector

from ...core import DataTier
from ...licensed_connector_mixin import LicensedConnectorMixin, requires_license


class EvictionLabConnector(LicensedConnectorMixin, BaseConnector):
    """
    Connector for Eviction Lab data on housing instability and evictions.

    The Eviction Lab at Princeton University maintains the most comprehensive
    database of evictions in America, providing census tract-level data on
    eviction filings and completed evictions from 2000-2018.

    This connector enables analysis of housing instability, displacement
    patterns, and the geography of eviction across the United States.
    """

    # Registry name for license validation
    _connector_name = "Eviction_Lab"

    """
    Data Structure:
    - Eviction filings: Legal actions initiated by landlords
    - Evictions: Court-ordered evictions that were carried out
    - Eviction rate: Evictions per 100 renter-occupied households
    - Filing rate: Filings per 100 renter-occupied households

    Geographic Levels:
    - Census tract (GEOID format: 11-digit)
    - County (FIPS code: 5-digit)
    - City
    - State (2-letter abbreviation or FIPS)

    Time Period: 2000-2018 (annual observations)

    Examples:
        >>> # Initialize connector
        >>> eviction = EvictionLabConnector()
        >>> eviction.connect()

        >>> # Load tract-level data
        >>> tract_data = eviction.load_tract_data('data/tracts.csv')
        >>>
        >>> # Get county-level eviction rates
        >>> county_rates = eviction.get_county_evictions(state='CA')
        >>>
        >>> # Time series analysis
        >>> trends = eviction.get_eviction_trends(geoid='06037', level='county')
        >>>
        >>> # High eviction areas
        >>> hotspots = eviction.get_high_eviction_areas(threshold=5.0)
    """

    def __init__(
        self,
        data_dir: Optional[Union[str, Path]] = None,
        cache_dir: Optional[str] = None,
        cache_ttl: int = 86400,
    ):
        """
        Initialize Eviction Lab connector.

        Args:
            data_dir: Directory containing downloaded Eviction Lab CSV files
            cache_dir: Directory for caching responses
            cache_ttl: Cache time-to-live in seconds (default: 24 hours)
        """
        super().__init__(
            cache_dir=cache_dir,
            cache_ttl=cache_ttl,
        )
        self.connector_name = "EvictionLab"
        self.data_dir = Path(data_dir) if data_dir else None
        self._tract_data = None
        self._county_data = None
        self._state_data = None

    def _get_api_key(self) -> Optional[str]:
        """
        Get API key from environment or config.

        Eviction Lab data is public and does not require API authentication.
        Implemented for BaseConnector interface compliance.

        Returns:
            None (no API key required)
        """
        return None

    def fetch(self, **kwargs) -> Dict:
        """
        Fetch data from Eviction Lab (if API becomes available).

        Note: Eviction Lab currently provides bulk CSV downloads.
        This method is implemented for future API compatibility.

        Args:
            **kwargs: Connector-specific parameters

        Returns:
            JSON response as dictionary

        Raises:
            NotImplementedError: API access not yet available
        """
        raise NotImplementedError(
            "Eviction Lab uses bulk CSV downloads. "
            "Use load_tract_data(), load_county_data(), or load_state_data() "
            "to load Eviction Lab data files. "
            "Download data from: https://evictionlab.org/get-the-data/"
        )

    def connect(self) -> None:
        """
        Establish connection to Eviction Lab data sources.

        For file-based access, validates data directory exists.

        Raises:
            ConnectionError: If data directory doesn't exist
        """
        self._init_session()

        # Validate data directory if provided
        if self.data_dir and not self.data_dir.exists():
            raise ConnectionError(
                f"Eviction Lab data directory not found: {self.data_dir}. "
                "Download data from https://evictionlab.org/get-the-data/"
            )

        self.logger.info("Eviction Lab connector initialized successfully")

    def load_tract_data(
        self, file_path: Union[str, Path], state_filter: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Load census tract-level eviction data from CSV file.

        Eviction Lab provides tract-level data with eviction filings,
        evictions, rates, and demographic context.

        Args:
            file_path: Path to tract-level CSV file
            state_filter: Optional 2-letter state code to filter results

        Returns:
            DataFrame with tract-level eviction data

        Columns include:
        - GEOID: 11-digit census tract identifier
        - year: Year of observation (2000-2018)
        - name: Tract name
        - parent-location: County name
        - eviction-filings: Number of eviction filings
        - evictions: Number of completed evictions
        - eviction-rate: Evictions per 100 renter households
        - eviction-filing-rate: Filings per 100 renter households
        - renter-occupied-households: Number of renter households
        - pct-renter-occupied: Percentage of households that rent
        - median-gross-rent: Median rent ($)
        - median-household-income: Median income ($)
        - median-property-value: Median property value ($)
        - rent-burden: Percentage rent-burdened (>30% income on rent)
        - pct-white: Percentage white residents
        - pct-african-american: Percentage Black residents
        - pct-hispanic: Percentage Hispanic/Latino residents
        - pct-am-ind: Percentage American Indian/Alaska Native
        - pct-asian: Percentage Asian residents
        - pct-nh-pi: Percentage Native Hawaiian/Pacific Islander
        - pct-multiple: Percentage multiple race residents
        - pct-other: Percentage other race residents
        - poverty-rate: Poverty rate

        Examples:
            >>> # Load national tract data
            >>> tracts = eviction.load_tract_data('eviction_lab_tracts.csv')
            >>>
            >>> # Filter to California only
            >>> ca_tracts = eviction.load_tract_data(
            ...     'eviction_lab_tracts.csv',
            ...     state_filter='CA'
            ... )
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Tract data file not found: {file_path}")

        self.logger.info(f"Loading Eviction Lab tract data from {file_path.name}")

        # Load data
        # Preserve GEOID as string to maintain leading zeros
        df = pd.read_csv(file_path, low_memory=False, dtype={"GEOID": "str"})

        # Filter by state if provided (GEOID starts with state FIPS)
        if state_filter:
            state_filter = state_filter.upper()
            # Map state abbreviation to FIPS code if needed
            # For now, assume GEOID filtering by first 2 digits
            if len(state_filter) == 2:
                # Would need state FIPS mapping here
                self.logger.warning(
                    "State filtering by abbreviation requires FIPS mapping. "
                    "Filter by GEOID prefix instead."
                )

        self._tract_data = df
        self.logger.info(f"Loaded {len(df):,} tract-year observations")
        return df

    def load_county_data(
        self, file_path: Union[str, Path], state_filter: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Load county-level eviction data from CSV file.

        Args:
            file_path: Path to county-level CSV file
            state_filter: Optional 2-letter state code

        Returns:
            DataFrame with county-level eviction data

        Columns similar to tract data but aggregated to county level.
        GEOID format: 5-digit county FIPS code

        Examples:
            >>> # Load county data
            >>> counties = eviction.load_county_data('eviction_lab_counties.csv')
            >>>
            >>> # Texas counties only
            >>> tx_counties = eviction.load_county_data(
            ...     'eviction_lab_counties.csv',
            ...     state_filter='TX'
            ... )
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"County data file not found: {file_path}")

        self.logger.info(f"Loading Eviction Lab county data from {file_path.name}")

        # Load data with GEOID preservation
        df = pd.read_csv(file_path, low_memory=False, dtype={"GEOID": "str"})

        # Filter by state if provided (first 2 digits of 5-digit FIPS)
        if state_filter:
            state_filter = state_filter.upper()
            # Would need state FIPS mapping
            self.logger.warning(
                "State filtering by abbreviation requires FIPS mapping. "
                "Filter by GEOID prefix instead."
            )

        self._county_data = df
        self.logger.info(f"Loaded {len(df):,} county-year observations")
        return df

    @requires_license
    def get_eviction_by_geography(
        self, geoid: str, level: str = "tract", year: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Get eviction data for specific geography.

        Args:
            geoid: Geographic identifier (11-digit tract or 5-digit county)
            level: Geographic level ('tract' or 'county')
            year: Optional year filter (2000-2018)

        Returns:
            DataFrame with eviction data for specified geography

        Examples:
            >>> # Los Angeles County evictions over time
            >>> la_county = eviction.get_eviction_by_geography(
            ...     geoid='06037',
            ...     level='county'
            ... )
            >>>
            >>> # Specific tract in 2018
            >>> tract_2018 = eviction.get_eviction_by_geography(
            ...     geoid='06037206100',
            ...     level='tract',
            ...     year=2018
            ... )
        """
        # Determine which dataset to use
        if level == "tract":
            if self._tract_data is None:
                raise ValueError("No tract data loaded. Call load_tract_data() first.")
            df = self._tract_data[self._tract_data["GEOID"] == geoid]
        elif level == "county":
            if self._county_data is None:
                raise ValueError("No county data loaded. Call load_county_data() first.")
            df = self._county_data[self._county_data["GEOID"] == geoid]
        else:
            raise ValueError(f"Invalid level: {level}. Use 'tract' or 'county'.")

        # Filter by year if specified
        if year:
            df = df[df["year"] == year]

        return df

    @requires_license
    def get_eviction_trends(self, geoid: str, level: str = "tract") -> pd.DataFrame:
        """
        Get time series of eviction rates for a geography.

        Args:
            geoid: Geographic identifier
            level: Geographic level ('tract' or 'county')

        Returns:
            DataFrame with year and eviction metrics over time

        Examples:
            >>> # County eviction trends
            >>> trends = eviction.get_eviction_trends('06037', level='county')
            >>> trends.plot(x='year', y='eviction-rate')
        """
        df = self.get_eviction_by_geography(geoid, level=level)

        # Sort by year
        df = df.sort_values("year")

        return df[
            ["year", "evictions", "eviction-filings", "eviction-rate", "eviction-filing-rate"]
        ]

    @requires_license
    def get_high_eviction_areas(
        self, threshold: float = 5.0, year: Optional[int] = None, level: str = "tract"
    ) -> pd.DataFrame:
        """
        Identify areas with high eviction rates.

        Args:
            threshold: Minimum eviction rate (evictions per 100 renter households)
            year: Optional year filter (default: most recent available)
            level: Geographic level ('tract' or 'county')

        Returns:
            DataFrame of high-eviction areas

        Examples:
            >>> # Tracts with eviction rates above 5%
            >>> hotspots = eviction.get_high_eviction_areas(threshold=5.0)
            >>>
            >>> # Counties with extreme eviction rates (>10%) in 2018
            >>> extreme = eviction.get_high_eviction_areas(
            ...     threshold=10.0,
            ...     year=2018,
            ...     level='county'
            ... )
        """
        # Determine dataset
        if level == "tract":
            if self._tract_data is None:
                raise ValueError("No tract data loaded. Call load_tract_data() first.")
            df = self._tract_data.copy()
        elif level == "county":
            if self._county_data is None:
                raise ValueError("No county data loaded. Call load_county_data() first.")
            df = self._county_data.copy()
        else:
            raise ValueError(f"Invalid level: {level}")

        # Filter by year
        if year:
            df = df[df["year"] == year]
        else:
            # Use most recent year per geography
            df = df.sort_values("year").groupby("GEOID").tail(1)

        # Filter by threshold
        high_eviction = df[df["eviction-rate"] >= threshold]

        return high_eviction.sort_values("eviction-rate", ascending=False)

    @requires_license
    def get_eviction_statistics(
        self, level: str = "tract", year: Optional[int] = None
    ) -> Dict[str, float]:
        """
        Get summary statistics for eviction rates.

        Args:
            level: Geographic level ('tract' or 'county')
            year: Optional year filter

        Returns:
            Dictionary with summary statistics:
            - mean_eviction_rate: Average eviction rate
            - median_eviction_rate: Median eviction rate
            - std_eviction_rate: Standard deviation
            - total_evictions: Total evictions nationwide
            - total_filings: Total eviction filings

        Examples:
            >>> # National statistics for 2018
            >>> stats = eviction.get_eviction_statistics(year=2018)
            >>> print(f"Average eviction rate: {stats['mean_eviction_rate']:.2f}%")
        """
        # Determine dataset
        if level == "tract":
            if self._tract_data is None:
                raise ValueError("No tract data loaded.")
            df = self._tract_data.copy()
        elif level == "county":
            if self._county_data is None:
                raise ValueError("No county data loaded.")
            df = self._county_data.copy()
        else:
            raise ValueError(f"Invalid level: {level}")

        # Filter by year
        if year:
            df = df[df["year"] == year]

        # Calculate statistics
        stats = {
            "mean_eviction_rate": df["eviction-rate"].mean(),
            "median_eviction_rate": df["eviction-rate"].median(),
            "std_eviction_rate": df["eviction-rate"].std(),
            "total_evictions": df["evictions"].sum(),
            "total_filings": df["eviction-filings"].sum(),
            "observations": len(df),
        }

        return stats

    def compare_geographies(
        self, geoids: List[str], level: str = "tract", metric: str = "eviction-rate"
    ) -> pd.DataFrame:
        """
        Compare eviction metrics across multiple geographies.

        Args:
            geoids: List of geographic identifiers
            level: Geographic level ('tract' or 'county')
            metric: Metric to compare (default: 'eviction-rate')

        Returns:
            DataFrame with time series comparison

        Examples:
            >>> # Compare three counties
            >>> comparison = eviction.compare_geographies(
            ...     geoids=['06037', '17031', '36061'],  # LA, Cook, NYC
            ...     level='county',
            ...     metric='eviction-rate'
            ... )
        """
        # Determine dataset
        if level == "tract":
            if self._tract_data is None:
                raise ValueError("No tract data loaded.")
            df = self._tract_data.copy()
        elif level == "county":
            if self._county_data is None:
                raise ValueError("No county data loaded.")
            df = self._county_data.copy()
        else:
            raise ValueError(f"Invalid level: {level}")

        # Filter to specified geographies
        df = df[df["GEOID"].isin(geoids)]

        # Pivot for comparison
        comparison = df.pivot(index="year", columns="GEOID", values=metric)

        return comparison
