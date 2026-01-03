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
LEHD (Longitudinal Employer-Household Dynamics) Data Connector.

This connector provides access to the Census Bureau's LEHD Origin-Destination
Employment Statistics (LODES) data, which describes worker flows between
home and work locations.

Data Source: https://lehd.ces.census.gov/data/
API Documentation: https://lehd.ces.census.gov/data/lodes/LODES7/
"""

from typing import Any, List, Optional

import pandas as pd

from ...base_dispatcher_connector import BaseDispatcherConnector
from ...core import DataTier
from ...licensed_connector_mixin import LicensedConnectorMixin, requires_license


class LEHDConnector(LicensedConnectorMixin, BaseDispatcherConnector):
    """
    Connector for LEHD Origin-Destination Employment Statistics (LODES).

    The LODES data provides detailed information on:
    - Worker flows between home and work locations
    - Job characteristics by origin/destination
    - Worker characteristics (age, earnings, industry)
    - Temporal employment patterns

    Data is available at the Census block level, aggregated to various geographies.

    Uses dispatcher pattern - routes based on 'data_type' parameter:
    - 'od': Origin-Destination employment data
    - 'rac': Residence Area Characteristics
    - 'wac': Workplace Area Characteristics

    Example:
        >>> lehd = LEHDConnector()
        >>> # Get main OD data for California in 2020
        >>> od_data = lehd.fetch(data_type='od', state='ca', year=2020, part='main')
        >>> # Get residential area characteristics
        >>> rac_data = lehd.fetch(data_type='rac', state='ca', year=2020)
    """

    # Registry name for license validation
    _connector_name = "Census_LEHD_Full"

    BASE_URL = "https://lehd.ces.census.gov/data/lodes/LODES7"

    # Dispatcher configuration
    DISPATCH_PARAM = "data_type"
    DISPATCH_MAP = {
        "od": "get_od_data",
        "rac": "get_rac_data",
        "wac": "get_wac_data",
    }

    # Job type codes
    JOB_TYPES = {
        "JT00": "All jobs",
        "JT01": "Primary jobs",
        "JT02": "All private jobs",
        "JT03": "Private primary jobs",
        "JT04": "All federal jobs",
        "JT05": "Federal primary jobs",
    }

    # Segment codes (worker characteristics)
    SEGMENTS = {
        "S000": "All workers",
        "SA01": "Age 29 or younger",
        "SA02": "Age 30 to 54",
        "SA03": "Age 55 or older",
        "SE01": "Earnings $1250/month or less",
        "SE02": "Earnings $1251-$3333/month",
        "SE03": "Earnings greater than $3333/month",
        "SI01": "Goods producing industry",
        "SI02": "Trade, transportation, and utilities",
        "SI03": "All other services",
    }

    # Part codes for OD data
    PARTS = {
        "main": "Main (all jobs)",
        "aux": "Auxiliary (federal jobs)",
    }

    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize LEHD connector.

        Args:
            cache_dir: Optional directory for caching responses
        """
        super().__init__(cache_dir=cache_dir)
        self.logger.info("Initialized LEHD connector")

    def _get_api_key(self) -> Optional[str]:
        """LEHD data doesn't require an API key."""
        return None

    def connect(self) -> None:
        """Establish connection to LEHD data source (no-op for public data)."""
        self.logger.debug("LEHD connector ready (no authentication required)")

    # fetch() method inherited from BaseDispatcherConnector
    # Routes based on 'data_type' parameter to methods in DISPATCH_MAP

    def _build_lodes_url(
        self,
        state: str,
        data_type: str,
        year: int,
        part: str = "main",
        job_type: str = "JT00",
        segment: str = "S000",
    ) -> str:
        """
        Build LODES data file URL.

        Args:
            state: Two-letter state abbreviation (lowercase)
            data_type: Type of data ('od', 'rac', 'wac')
            year: Year of data (2002-2020)
            part: 'main' or 'aux' (for OD data only)
            job_type: Job type code (e.g., 'JT00')
            segment: Worker segment code (e.g., 'S000')

        Returns:
            Complete URL to CSV file
        """
        state = state.lower()

        if data_type == "od":
            # Origin-Destination: state_od_part_jobtype_year.csv.gz
            filename = f"{state}_od_{part}_{job_type}_{year}.csv.gz"
        else:
            # RAC/WAC: state_datatype_segment_jobtype_year.csv.gz
            filename = f"{state}_{data_type}_{segment}_{job_type}_{year}.csv.gz"

        url = f"{self.BASE_URL}/{state}/{data_type}/{filename}"
        return url

    @requires_license
    def get_od_data(
        self,
        state: str,
        year: int,
        part: str = "main",
        job_type: str = "JT00",
        segment: str = "S000",
    ) -> pd.DataFrame:
        """
        Get Origin-Destination employment data.

        This shows worker flows from residence (origin) to workplace (destination).

        Args:
            state: Two-letter state abbreviation (e.g., 'ca', 'ny')
            year: Year of data (2002-2020)
            part: 'main' for all jobs, 'aux' for federal jobs
            job_type: Job type code (default: 'JT00' = all jobs)
            segment: Worker segment code (default: 'S000' = all workers)

        Returns:
            DataFrame with columns:
                - w_geocode: Workplace Census block code
                - h_geocode: Residence Census block code
                - S000: Total number of jobs
                - SA01, SA02, SA03: Jobs by age group
                - SE01, SE02, SE03: Jobs by earnings
                - SI01, SI02, SI03: Jobs by industry
                - createdate: Date file was created

        Example:
            >>> lehd = LEHDConnector()
            >>> od = lehd.get_od_data('ca', 2020)
            >>> # Find top commute flows
            >>> od.nlargest(10, 'S000')
        """
        self.logger.info(
            f"Fetching LEHD OD data: state={state}, year={year}, "
            f"part={part}, job_type={job_type}, segment={segment}"
        )

        # Validate inputs before making HTTP request
        # State code validation
        if not state or not isinstance(state, str):
            raise ValueError(f"Invalid state code: '{state}'. Must be non-empty string.")

        state = state.strip().lower()
        if not state or len(state) != 2:
            raise ValueError(f"Invalid state code: '{state}'. Must be 2-letter state abbreviation.")

        # Year validation
        if not isinstance(year, int):
            raise TypeError(f"Invalid year type: {type(year).__name__}. Year must be an integer.")

        # LEHD LODES data is available from 2002-2021 (as of 2025)
        if year < 2002 or year > 2021:
            raise ValueError(f"Invalid year: {year}. LEHD data is available from 2002-2021.")

        url = self._build_lodes_url(state, "od", year, part, job_type, segment)

        # Read CSV (it's gzipped)
        try:
            df = pd.read_csv(
                url,
                compression="gzip",
                dtype={
                    "w_geocode": str,
                    "h_geocode": str,
                },
            )

            self.logger.info(f"Retrieved {len(df):,} OD records")
            return df

        except Exception as e:
            self.logger.error(
                f"Failed to fetch OD data: {e
    }"
            )
            raise

    @requires_license
    def get_rac_data(
        self,
        state: str,
        year: int,
        segment: str = "S000",
        job_type: str = "JT00",
    ) -> pd.DataFrame:
        """
        Get Residence Area Characteristics (RAC) data.

        This shows characteristics of workers who live in each Census block.

        Args:
            state: Two-letter state abbreviation
            year: Year of data (2002-2020)
            segment: Worker segment code (default: 'S000' = all workers)
            job_type: Job type code (default: 'JT00' = all jobs)

        Returns:
            DataFrame with residence location employment characteristics

        Example:
            >>> lehd = LEHDConnector()
            >>> rac = lehd.get_rac_data('ny', 2020)
            >>> # Aggregate to county level (first 5 digits of geocode)
            >>> rac['county'] = rac['h_geocode'].str[:5]
            >>> county_workers = rac.groupby('county')['C000'].sum()
        """
        self.logger.info(
            f"Fetching LEHD RAC data: state={state}, year={year}, "
            f"segment={segment}, job_type={job_type}"
        )

        # Validate inputs before making HTTP request
        if not state or not isinstance(state, str):
            raise ValueError(f"Invalid state code: '{state}'. Must be non-empty string.")

        state = state.strip().lower()
        if not state or len(state) != 2:
            raise ValueError(f"Invalid state code: '{state}'. Must be 2-letter state abbreviation.")

        if not isinstance(year, int):
            raise TypeError(f"Invalid year type: {type(year).__name__}. Year must be an integer.")

        if year < 2002 or year > 2021:
            raise ValueError(f"Invalid year: {year}. LEHD data is available from 2002-2021.")

        url = self._build_lodes_url(state, "rac", year, segment=segment, job_type=job_type)

        try:
            df = pd.read_csv(url, compression="gzip", dtype={"h_geocode": str})
            self.logger.info(f"Retrieved {len(df):,} RAC records")
            return df
        except Exception as e:
            self.logger.error(f"Failed to fetch RAC data: {e}")
            raise

    @requires_license
    def get_wac_data(
        self,
        state: str,
        year: int,
        segment: str = "S000",
        job_type: str = "JT00",
    ) -> pd.DataFrame:
        """
        Get Workplace Area Characteristics (WAC) data.

        This shows characteristics of jobs located in each Census block.

        Args:
            state: Two-letter state abbreviation
            year: Year of data (2002-2020)
            segment: Worker segment code (default: 'S000' = all workers)
            job_type: Job type code (default: 'JT00' = all jobs)

        Returns:
            DataFrame with workplace location employment characteristics

        Example:
            >>> lehd = LEHDConnector()
            >>> wac = lehd.get_wac_data('tx', 2020)
            >>> # Find employment centers
            >>> wac.nlargest(20, 'C000')[['w_geocode', 'C000']]
        """
        self.logger.info(
            f"Fetching LEHD WAC data: state={state}, year={year}, "
            f"segment={segment}, job_type={job_type}"
        )

        # Validate inputs before making HTTP request
        if not state or not isinstance(state, str):
            raise ValueError(f"Invalid state code: '{state}'. Must be non-empty string.")

        state = state.strip().lower()
        if not state or len(state) != 2:
            raise ValueError(f"Invalid state code: '{state}'. Must be 2-letter state abbreviation.")

        if not isinstance(year, int):
            raise TypeError(f"Invalid year type: {type(year).__name__}. Year must be an integer.")

        if year < 2002 or year > 2021:
            raise ValueError(f"Invalid year: {year}. LEHD data is available from 2002-2021.")

        url = self._build_lodes_url(state, "wac", year, segment=segment, job_type=job_type)

        try:
            df = pd.read_csv(url, compression="gzip", dtype={"w_geocode": str})
            self.logger.info(f"Retrieved {len(df):,} WAC records")
            return df
        except Exception as e:
            self.logger.error(f"Failed to fetch WAC data: {e}")
            raise

    @requires_license
    def get_available_years(self, state: str) -> List[int]:
        """
        Get list of available years for a state.

        Note: This is a best-effort approach since LEHD doesn't provide
        a direct API for metadata. Years 2002-2020 are generally available
        for most states.

        Args:
            state: Two-letter state abbreviation

        Returns:
            List of available years
        """
        # Most states have data from 2002-2020
        # This is a simplified implementation
        return list(range(2002, 2021))

    def aggregate_to_tract(
        self,
        df: pd.DataFrame,
        geocode_col: str = "h_geocode",
    ) -> pd.DataFrame:
        """
        Aggregate block-level data to Census tract level.

        Args:
            df: DataFrame with block-level data
            geocode_col: Name of geocode column ('h_geocode' or 'w_geocode')

        Returns:
            DataFrame aggregated to tract level

        Example:
            >>> rac = lehd.get_rac_data('ca', 2020)
            >>> rac_tracts = lehd.aggregate_to_tract(rac, 'h_geocode')
        """
        # Census tract is first 11 digits of block code
        tract_col = geocode_col.replace("geocode", "tract")
        df = df.copy()
        df[tract_col] = df[geocode_col].str[:11]

        # Sum numeric columns
        numeric_cols = df.select_dtypes(include=["number"]).columns
        agg_df = df.groupby(tract_col)[numeric_cols].sum().reset_index()

        return agg_df

    def aggregate_to_county(
        self,
        df: pd.DataFrame,
        geocode_col: str = "h_geocode",
    ) -> pd.DataFrame:
        """
        Aggregate block-level data to county level.

        Args:
            df: DataFrame with block-level data
            geocode_col: Name of geocode column ('h_geocode' or 'w_geocode')

        Returns:
            DataFrame aggregated to county level

        Example:
            >>> wac = lehd.get_wac_data('ny', 2020)
            >>> wac_counties = lehd.aggregate_to_county(wac, 'w_geocode')
        """
        # Handle empty DataFrame
        if df.empty:
            return df

        # County FIPS is first 5 digits of block code
        county_col = geocode_col.replace("geocode", "county")
        df = df.copy()
        df[county_col] = df[geocode_col].str[:5]

        # Sum numeric columns
        numeric_cols = df.select_dtypes(include=["number"]).columns
        agg_df = df.groupby(county_col)[numeric_cols].sum().reset_index()

        return agg_df

    @staticmethod
    @requires_license
    def get_job_type_description(job_type: str) -> str:
        """Get human-readable description of job type code."""
        return LEHDConnector.JOB_TYPES.get(job_type, f"Unknown job type: {job_type}")

    @staticmethod
    @requires_license
    def get_segment_description(segment: str) -> str:
        """Get human-readable description of segment code."""
        return LEHDConnector.SEGMENTS.get(segment, f"Unknown segment: {segment}")
