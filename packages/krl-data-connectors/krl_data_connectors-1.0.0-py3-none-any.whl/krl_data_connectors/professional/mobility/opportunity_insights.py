# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

# Copyright (c) 2025 KR-Labs Foundation. All rights reserved.
# Licensed under Apache License 2.0 (see LICENSE file for details)

"""
Opportunity Insights Connector

Provides access to three major Opportunity Insights data products:
1. Opportunity Atlas - Intergenerational mobility by neighborhood
2. Social Capital Atlas - Economic connectedness and social capital
3. Economic Connectedness - Cross-class friendships

Data Sources:
- Opportunity Atlas: https://opportunityinsights.org/data/
- Social Capital Atlas: https://socialcapital.org/
- Economic Connectedness: Chetty et al. (2022), Nature

Geographic Coverage:
- Census tracts (~74,000 tracts)
- ZIP codes
- Counties
- Commuting zones
- States

Key Domains:
- D10: Social Mobility
- D21: Social Capital
"""

import hashlib
import os
from pathlib import Path
from typing import Dict, List, Optional, Union
from urllib.parse import urljoin

import pandas as pd
import requests

from krl_data_connectors.base_dispatcher_connector import BaseDispatcherConnector
from krl_data_connectors.core import DataTier
from krl_data_connectors.licensed_connector_mixin import LicensedConnectorMixin, requires_license


class OpportunityInsightsConnector(LicensedConnectorMixin, BaseDispatcherConnector):
    """
        Connector for Opportunity Insights data products using dispatcher pattern.

        Unlike most connectors, this does not require an API key.
        Instead, it downloads and caches CSV files from public URLs.

        The connector provides access to:
        - Opportunity Atlas: Intergenerational mobility outcomes
        - Social Capital Atlas: Economic connectedness metrics
        - Economic Connectedness: Cross-class friendship data
    """

    # Registry name for license validation
    _connector_name = "Opportunity_Insights"

    """
        **Dispatcher Configuration:**
        This connector uses the dispatcher pattern:
        - DISPATCH_PARAM: 'data_product'
        - Valid values: 'atlas', 'social_capital', 'ec'
        - Routes to: fetch_opportunity_atlas(), fetch_social_capital(), fetch_economic_connectedness()

        Args:
            cache_dir: Directory for cache files (default: ~/.krl_cache/mobility)
            cache_ttl: Cache time-to-live in seconds (default: 30 days)
            timeout: Request timeout in seconds (default: 60 for large files)
            max_retries: Maximum number of retry attempts (default: 3)
            data_version: Data version to use (default: "latest")

        Example:
            >>> from krl_data_connectors import OpportunityInsightsConnector
    from ...licensed_connector_mixin import LicensedConnectorMixin, requires_license
    from ...core import DataTier
            >>> oi = OpportunityInsightsConnector()
            >>>
            >>> # Fetch mobility data for California
            >>> ca_mobility = oi.fetch_opportunity_atlas(
            ...     geography="tract",
            ...     state="06",
            ...     metrics=["kfr_pooled_p25", "kfr_pooled_p50"]
            ... )
            >>>
            >>> # Fetch social capital data
            >>> social_capital = oi.fetch_social_capital(
            ...     geography="county",
            ...     metrics=["ec_county", "clustering_county"]
            ... )
            >>>
            >>> # Aggregate to county level
            >>> county_data = oi.aggregate_to_county(ca_mobility)
    """

    # Data source URLs - STATA format (.dta files)
    # Opportunity Atlas data from "The Opportunity Atlas" paper
    BASE_URL = "https://opportunityinsights.org/wp-content/uploads/"

    # All Outcomes by Geography - STATA files with simplified outcomes
    ATLAS_TRACT_URL = f"{BASE_URL}2018/10/tract_outcomes_simple.dta"
    ATLAS_COUNTY_URL = f"{BASE_URL}2018/10/county_outcomes_simple.dta"
    ATLAS_CZ_URL = f"{BASE_URL}2018/10/cz_outcomes_simple.dta"
    ATLAS_NATIONAL_URL = f"{BASE_URL}2018/10/national_percentile_outcomes.dta"

    # Tract covariates (neighborhood characteristics)
    TRACT_COVARIATES_URL = f"{BASE_URL}2018/10/tract_covariates.dta"
    COUNTY_COVARIATES_URL = f"{BASE_URL}2018/12/cty_covariates.dta"
    CZ_COVARIATES_URL = f"{BASE_URL}2018/12/cz_covariates.dta"

    # Late cohort data (1984-1989 birth cohorts)
    ATLAS_TRACT_LATE_URL = f"{BASE_URL}2024/08/tract_outcomes_late_simple.dta"

    # Crosswalk files
    TRACT_2010_2020_CROSSWALK = f"{BASE_URL}2021/05/us_tract_2010_2020_crosswalk.dta"

    # Social Capital Atlas (Nature 2022 paper)
    # Data hosted on Humanitarian Data Exchange (HDX)
    # Using correct dataset ID and resource URLs from HDX metadata
    HDX_DATASET_ID = "85ee8e10-0c66-4635-b997-79b6fad44c71"

    # HDX Download URLs (from official metadata)
    SOCIAL_CAPITAL_COUNTY = "https://data.humdata.org/dataset/85ee8e10-0c66-4635-b997-79b6fad44c71/resource/ec896b64-c922-4737-b759-e4bd7f73b8cc/download/social_capital_county.csv"
    SOCIAL_CAPITAL_ZIP = "https://data.humdata.org/dataset/85ee8e10-0c66-4635-b997-79b6fad44c71/resource/ab878625-279b-4bef-a2b3-c132168d536e/download/social_capital_zip.csv"
    SOCIAL_CAPITAL_COLLEGE = "https://data.humdata.org/dataset/85ee8e10-0c66-4635-b997-79b6fad44c71/resource/7bd697cf-c572-47a6-b15b-8450cc5c7ef8/download/social_capital_college.csv"
    SOCIAL_CAPITAL_HS = "https://data.humdata.org/dataset/85ee8e10-0c66-4635-b997-79b6fad44c71/resource/0de85271-031d-4849-bda8-c8582a67e11b/download/social_capital_high_school.csv"

    # Dispatcher configuration
    DISPATCH_PARAM = "data_product"
    DISPATCH_MAP = {
        "atlas": "fetch_opportunity_atlas",
        "social_capital": "fetch_social_capital",
        "ec": "fetch_economic_connectedness",
    }

    def __init__(
        self,
        cache_dir: Optional[str] = None,
        cache_ttl: int = 2592000,  # 30 days for large datasets
        timeout: int = 60,
        max_retries: int = 3,
        data_version: str = "latest",
    ):
        """Initialize Opportunity Insights connector."""
        # Validate parameter types
        if not isinstance(cache_ttl, int):
            raise TypeError(f"cache_ttl must be int, got {type(cache_ttl).__name__}")
        if not isinstance(timeout, int):
            raise TypeError(f"timeout must be int, got {type(timeout).__name__}")
        if not isinstance(max_retries, int):
            raise TypeError(f"max_retries must be int, got {type(max_retries).__name__}")
        if not isinstance(data_version, str):
            raise TypeError(f"data_version must be str, got {type(data_version).__name__}")
        if cache_dir is not None and not isinstance(cache_dir, str):
            raise TypeError(f"cache_dir must be str or None, got {type(cache_dir).__name__}")

        # Set default cache directory for mobility data
        if cache_dir is None:
            cache_dir = str(Path.home() / ".krl_cache" / "mobility")

        super().__init__(
            api_key=None,  # No API key required
            cache_dir=cache_dir,
            cache_ttl=cache_ttl,
            timeout=timeout,
            max_retries=max_retries,
        )

        self.data_version = data_version
        self._atlas_data: Optional[dict[str, pd.DataFrame]] = None  # Lazy-loaded cache
        self._social_capital_data: Optional[pd.DataFrame] = None

        self.logger.info(
            "OpportunityInsightsConnector initialized",
            extra={
                "data_version": data_version,
                "cache_dir": cache_dir,
                "cache_ttl_days": cache_ttl / 86400,
            },
        )

    def _get_api_key(self) -> Optional[str]:
        """
        Get API key from configuration.

        Opportunity Insights data is publicly available and does not
        require an API key.

        Returns:
            None (no API key required)
        """
        return None

    def connect(self) -> None:
        """
        Establish connection to Opportunity Insights data sources.

        Since this connector uses public CSV files, "connecting"
        means initializing the HTTP session for file downloads.

        Example:
            >>> oi = OpportunityInsightsConnector()
            >>> oi.connect()
            >>> print("Connected successfully")
            Connected successfully
        """
        try:
            self.session = self._init_session()
            self.logger.info("Connection established to Opportunity Insights data sources")
        except Exception as e:
            self.logger.error(f"Failed to connect: {str(e)}")
            raise

    def _normalize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize column names from STATA files.

        The STATA files use a naming convention with extra '_pooled'
        (e.g., 'kfr_pooled_pooled_p25' instead of 'kfr_pooled_p25').
        This method creates simplified aliases for easier use.

        Args:
            df: DataFrame with original STATA column names

        Returns:
            DataFrame with additional simplified column names
        """
        # Create column name mappings for common metrics
        # Pattern: kfr_RACE_GENDER_PERCENTILE -> simplified version
        rename_map = {}

        for col in df.columns:
            # Handle double-pooled patterns: kfr_pooled_pooled_p25 -> kfr_pooled_p25
            if "_pooled_pooled_" in col:
                simplified = col.replace("_pooled_pooled_", "_pooled_")
                rename_map[col] = simplified
            # Handle race-pooled patterns: kfr_white_pooled_p25 -> kfr_white_p25
            elif "_pooled_p" in col and any(
                race in col for race in ["black", "white", "hisp", "asian", "natam"]
            ):
                simplified = col.replace("_pooled_", "_")
                rename_map[col] = simplified
            # Handle jail patterns similarly
            elif "jail_" in col and "_pooled_p" in col:
                if "_pooled_pooled_" in col:
                    simplified = col.replace("_pooled_pooled_", "_pooled_")
                    rename_map[col] = simplified
                elif any(race in col for race in ["black", "white", "hisp", "asian", "natam"]):
                    simplified = col.replace("_pooled_", "_")
                    rename_map[col] = simplified

        # Apply renaming
        if rename_map:
            df = df.rename(columns=rename_map)
            self.logger.debug(f"Normalized {len(rename_map)} column names")

        return df

    def _get_hdx_download_url(self, resource_id: str) -> str:
        """
        Get download URL for HDX resource.

        HDX resources use signed S3 URLs that expire. This method constructs
        the HDX download endpoint that provides a fresh signed URL.

        Args:
            resource_id: HDX resource identifier

        Returns:
            Download URL (redirects to signed S3 URL)
        """
        return (
            f"https://data.humdata.org/dataset/{self.HDX_DATASET_ID}/"
            f"resource/{resource_id}/download"
        )

    def _get_expected_size(self, geography: str) -> str:
        """Get expected file size for geography (from HDX metadata)."""
        sizes = {"county": "701KB", "zip": "3.9MB", "high_school": "2.8MB", "college": "504KB"}
        return sizes.get(geography, "unknown")

    # fetch() method inherited from BaseDispatcherConnector
    # Routes based on data_product parameter to methods in DISPATCH_MAP

    def _download_file(
        self,
        url: str,
        filename: str,
        force_download: bool = False,
    ) -> Path:
        """
        Download a file from URL and cache it locally.

        Args:
            url: URL to download from
            filename: Local filename to save as
            force_download: Force re-download even if cached

        Returns:
            Path to the downloaded/cached file

        Raises:
            requests.RequestException: If download fails
            ValueError: If path traversal or invalid URL detected
        """
        # Security: Validate filename to prevent path traversal
        # Remove any path separators and resolve to just the filename
        clean_filename = Path(filename).name
        if not clean_filename or clean_filename in (".", ".."):
            raise ValueError(f"Invalid filename: {filename}")

        # Validate URL scheme (only HTTPS allowed for security)
        if not url.startswith(("http://", "https://")):
            raise ValueError(f"Invalid URL scheme: {url}. Only HTTP/HTTPS allowed.")

        # Build cache path and ensure it's within cache directory
        cache_dir = Path(self.cache.cache_dir).resolve()
        cache_path = (cache_dir / clean_filename).resolve()

        # Security: Ensure resolved path is within cache directory
        try:
            cache_path.relative_to(cache_dir)
        except ValueError:
            raise ValueError(
                f"Security violation: Path '{filename}' attempts to escape cache directory"
            )

        # Check if file exists and is not expired
        if cache_path.exists() and not force_download:
            file_age = (
                pd.Timestamp.now() - pd.Timestamp(cache_path.stat().st_mtime, unit="s")
            ).total_seconds()
            cache_ttl = 2592000  # Default 30 days for large datasets
            if self.cache.default_ttl is not None:
                cache_ttl = self.cache.default_ttl
            if file_age < cache_ttl:
                self.logger.info(
                    f"Using cached file: {filename}", extra={"age_days": file_age / 86400}
                )
                return cache_path

        # Download file
        self.logger.info(f"Downloading {filename} from {url}")

        # Ensure session is initialized
        if self.session is None:
            self.connect()

        # Download file (session is guaranteed to be initialized here)
        session = self.session
        if session is None:
            raise RuntimeError("Failed to initialize session")

        response = session.get(url, stream=True, timeout=self.timeout)
        response.raise_for_status()

        # Create cache directory if it doesn't exist
        cache_path.parent.mkdir(parents=True, exist_ok=True)

        # Download with progress indication for large files
        total_size = int(response.headers.get("content-length", 0))
        block_size = 1024 * 1024  # 1MB chunks

        with open(cache_path, "wb") as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=block_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        if downloaded % (block_size * 10) == 0:  # Log every 10MB
                            self.logger.debug(f"Download progress: {progress:.1f}%")

        self.logger.info(
            f"Downloaded {filename}", extra={"size_mb": cache_path.stat().st_size / (1024 * 1024)}
        )

        return cache_path

    def fetch_opportunity_atlas(
        self,
        geography: str = "tract",
        metrics: Optional[List[str]] = None,
        state: Optional[str] = None,
        county: Optional[str] = None,
        force_download: bool = False,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Fetch Opportunity Atlas intergenerational mobility data.

        The Opportunity Atlas provides data on economic outcomes for children
        who grew up in different neighborhoods across the United States.

        Args:
            geography: Geographic level ("tract", "county", "cz", "state")
            metrics: List of metrics to include (None = all metrics)
            state: State FIPS code for filtering (e.g., "06" for California)
            county: County FIPS code for filtering (e.g., "06037" for Los Angeles)
            force_download: Force re-download of data file

        Returns:
            DataFrame with Opportunity Atlas data

        Raises:
            ValueError: If invalid geography level specified
            requests.RequestException: If download fails

        Available Metrics:
            - kfr_pooled_p25: Mean kid rank (pooled) for parents at p25
            - kfr_pooled_p50: Mean kid rank (pooled) for parents at p50
            - kfr_pooled_p75: Mean kid rank (pooled) for parents at p75
            - emp_rate_pooled: Employment rate (pooled)
            - jail_pooled: Incarceration rate (pooled)
            - frac_coll_plus_pooled: College attendance rate (pooled)
            - married_pooled: Marriage rate (pooled)

        Example:
            >>> oi = OpportunityInsightsConnector()
            >>> # Get mobility data for California
            >>> ca_data = oi.fetch_opportunity_atlas(
            ...     geography="tract",
            ...     state="06",
            ...     metrics=["kfr_pooled_p25", "kfr_pooled_p50"]
            ... )
            >>> print(ca_data.shape)
            (8057, 4)  # 8,057 tracts in CA, 4 columns (tract, state, kfr_p25, kfr_p50)
        """
        valid_geographies = ["tract", "county", "cz", "state"]
        if geography not in valid_geographies:
            raise ValueError(
                f"Invalid geography: {geography}. " f"Must be one of {valid_geographies}"
            )

        # Download Opportunity Atlas data if not cached for this geography level
        # Ensure _atlas_data is initialized (defensive check for backwards compatibility)
        if not hasattr(self, "_atlas_data") or self._atlas_data is None:
            self._atlas_data = {}

        if geography not in self._atlas_data or force_download:
            # Select the appropriate geography file (STATA format)
            # For state-level, use county data and aggregate up (CZ data doesn't have state column)
            url_map = {
                "tract": (self.ATLAS_TRACT_URL, "tract_outcomes_simple.dta"),
                "county": (self.ATLAS_COUNTY_URL, "county_outcomes_simple.dta"),
                "cz": (self.ATLAS_CZ_URL, "cz_outcomes_simple.dta"),
                "state": (
                    self.ATLAS_COUNTY_URL,
                    "county_outcomes_simple.dta",
                ),  # Use county file, will aggregate to state
            }

            url, filename = url_map[geography]
            atlas_path = self._download_file(url, filename, force_download=force_download)

            self.logger.info(f"Loading Opportunity Atlas {geography}-level data from STATA file")
            # Read STATA file - pandas handles .dta format natively
            atlas_df = pd.read_stata(atlas_path, convert_categoricals=True, preserve_dtypes=False)

            # Normalize column names (STATA files use different naming convention)
            atlas_df = self._normalize_column_names(atlas_df)

            # Convert geographic identifiers to strings for filtering
            # STATA files store these as floats, need to convert to int first, then string
            if "state" in atlas_df.columns:
                # State is 2 digits
                atlas_df["state"] = atlas_df["state"].fillna(0).astype(int).astype(str).str.zfill(2)

            if "county" in atlas_df.columns and "state" in atlas_df.columns:
                # County in STATA file is only 3 digits (county suffix)
                # Need to combine with state to get 5-digit FIPS code
                county_suffix = atlas_df["county"].fillna(0).astype(int).astype(str).str.zfill(3)
                atlas_df["county"] = atlas_df["state"] + county_suffix

            if geography == "tract" and "tract" in atlas_df.columns:
                # Tract in STATA file is only 6 digits (tract suffix)
                # Need to combine with county to get full 11-digit code
                tract_suffix = atlas_df["tract"].fillna(0).astype(int).astype(str).str.zfill(6)
                atlas_df["tract"] = atlas_df["county"] + tract_suffix

            # Cache the data keyed by geography level
            self._atlas_data[geography] = atlas_df

        df = self._atlas_data[geography].copy()

        # For state-level geography, aggregation creates the state column
        # So we need to aggregate first, then filter
        if geography == "state":
            df = self._aggregate_atlas(df, geography)

            # Now filter by state if specified
            if state is not None:
                df = df[df["state"] == str(state).zfill(2)]
        else:
            # For other geographies, filter before aggregation for efficiency
            # Filter by state if specified
            if state is not None and "state" in df.columns:
                df = df[df["state"] == str(state).zfill(2)]

            # Filter by county if specified
            if county is not None and "county" in df.columns:
                df = df[df["county"] == str(county).zfill(5)]

            # Aggregate to requested geography if not tract
            if geography != "tract":
                df = self._aggregate_atlas(df, geography)

        # Select metrics if specified (after aggregation to avoid losing group columns)
        if metrics is not None:
            # Always include geographic identifiers
            geo_cols = ["tract", "county", "state", "cz", "czname"]
            cols_to_keep = [col for col in geo_cols if col in df.columns] + metrics
            df = df[cols_to_keep]

        self.logger.info(
            "Fetched Opportunity Atlas data",
            extra={
                "geography": geography,
                "rows": len(df),
                "columns": len(df.columns),
                "state_filter": state,
                "county_filter": county,
            },
        )

        return df

    def fetch_social_capital(
        self,
        geography: str = "county",
        metrics: Optional[List[str]] = None,
        force_download: bool = False,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Fetch Social Capital Atlas data.

        The Social Capital Atlas provides data on economic connectedness
        and social capital based on Facebook friendship networks.

        Args:
            geography: Geographic level ("zip", "county", "college")
            metrics: List of metrics to include (None = all metrics)
            force_download: Force re-download of data file

        Returns:
            DataFrame with Social Capital data

        Raises:
            ValueError: If invalid geography level specified
            NotImplementedError: If geography not yet supported

        Available Metrics:
            - ec_{geo}: Economic connectedness
            - ec_se: Standard error of economic connectedness
            - clustering_{geo}: Local clustering coefficient
            - support_ratio_{geo}: Support ratio
            - volunteering_rate_{geo}: Volunteering rate

        Example:
            >>> oi = OpportunityInsightsConnector()
            >>> # Get social capital data at county level
            >>> county_sc = oi.fetch_social_capital(
            ...     geography="county",
            ...     metrics=["ec_county", "clustering_county"]
            ... )
            >>> print(county_sc.head())
        """
        valid_geographies = ["zip", "county", "college", "high_school"]
        if geography not in valid_geographies:
            raise ValueError(
                f"Invalid geography: {geography}. " f"Must be one of {valid_geographies}"
            )

        # Initialize cache if needed
        if not hasattr(self, "_social_capital_cache"):
            self._social_capital_cache = {}

        # Download Social Capital data if not cached for this geography
        if geography not in self._social_capital_cache or force_download:
            # Map geography to signed S3 URL and filename
            url_map = {
                "county": (self.SOCIAL_CAPITAL_COUNTY, "social_capital_county.csv"),
                "zip": (self.SOCIAL_CAPITAL_ZIP, "social_capital_zip.csv"),
                "college": (self.SOCIAL_CAPITAL_COLLEGE, "social_capital_college.csv"),
                "high_school": (self.SOCIAL_CAPITAL_HS, "social_capital_high_school.csv"),
            }

            if geography == "college":
                raise NotImplementedError(
                    "College-level social capital data not yet implemented. "
                    "This will be added in Week 3."
                )

            if geography == "high_school":
                raise NotImplementedError(
                    "High school-level social capital data not yet implemented. "
                    "This will be added in Week 3."
                )

            url, filename = url_map[geography]

            self.logger.info(
                f"Downloading Social Capital {geography} data from HDX S3",
                extra={"geography": geography},
            )

            # Download from signed S3 URL
            sc_path = self._download_file(url, filename, force_download=force_download)

            self.logger.info(f"Loading Social Capital {geography}-level data from CSV")
            # Read CSV file - Social Capital data is in CSV format
            try:
                data = pd.read_csv(sc_path, low_memory=False)
            except pd.errors.EmptyDataError:
                # HDX has bot protection - provide manual download instructions
                manual_msg = f"""
HDX bot protection blocks automated downloads. Please download manually:

1. Visit: https://data.humdata.org/dataset/85ee8e10-0c66-4635-b997-79b6fad44c71
2. Click download for: Social Capital Atlas - US {geography.title()}s.csv
3. Save to: {Path(sc_path).parent}/
4. Re-run your code

File should be named: {Path(sc_path).name}
Expected size: ~{self._get_expected_size(geography)}

See docs/SOCIAL_CAPITAL_DATA_ACQUISITION.md for details.
"""
                self.logger.error(
                    "HDX download blocked - manual download required",
                    extra={"geography": geography, "file": Path(sc_path).name},
                )
                raise FileNotFoundError(manual_msg)

            # Convert geographic identifiers to strings if needed
            if "county" in data.columns:
                # County FIPS codes
                data["county"] = data["county"].astype(str).str.zfill(5)

            if "zip" in data.columns:
                # ZIP codes
                data["zip"] = data["zip"].astype(str).str.zfill(5)

            # Cache the data for this geography
            self._social_capital_cache[geography] = data

        df = self._social_capital_cache[geography].copy()

        # Select metrics if specified
        if metrics is not None:
            # Always include geographic identifier
            geo_cols = ["county", "zip", "college"]
            cols_to_keep = [col for col in geo_cols if col in df.columns] + metrics
            df = df[cols_to_keep]

        self.logger.info(
            "Fetched Social Capital data",
            extra={
                "geography": geography,
                "rows": len(df),
                "columns": len(df.columns),
            },
        )

        return df

    def fetch_economic_connectedness(
        self,
        geography: str = "county",
        force_download: bool = False,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Fetch Economic Connectedness data.

        Economic connectedness measures the extent of social interaction
        between people of different socioeconomic status. This is actually
        a specific metric from the Social Capital Atlas data.

        Args:
            geography: Geographic level ("zip", "county")
            force_download: Force re-download of data file

        Returns:
            DataFrame with Economic Connectedness data (subset of Social Capital)

        Raises:
            ValueError: If invalid geography specified

        Example:
            >>> oi = OpportunityInsightsConnector()
            >>> ec_data = oi.fetch_economic_connectedness(geography="county")
            >>> print(ec_data[['county', 'ec_county']].head())
        """
        # Economic connectedness is part of Social Capital data
        # Just fetch Social Capital and filter to EC metrics
        sc_data = self.fetch_social_capital(geography=geography, force_download=force_download)

        # Filter to economic connectedness metrics
        ec_cols = [col for col in sc_data.columns if col.startswith("ec_")]
        geo_cols = ["county", "zip"]
        cols_to_keep = [col for col in geo_cols if col in sc_data.columns] + ec_cols

        df = sc_data[cols_to_keep]

        self.logger.info(
            "Fetched Economic Connectedness data",
            extra={
                "geography": geography,
                "rows": len(df),
                "ec_metrics": len(ec_cols),
            },
        )

        return df

    def _aggregate_atlas(
        self,
        df: pd.DataFrame,
        target_geography: str,
    ) -> pd.DataFrame:
        """
        Aggregate Opportunity Atlas data to different geographic levels.

        Args:
            df: DataFrame with tract-level data
            target_geography: Target geography ("county", "cz", "state")

        Returns:
            Aggregated DataFrame

        Note:
            Uses simple mean aggregation. Should be enhanced with
            population-weighted aggregation in production.
        """
        if target_geography == "tract":
            return df

        group_col = {
            "county": "county",
            "cz": "cz",
            "state": "state",
        }[target_geography]

        # If grouping by state but no state column, derive from county or tract
        if group_col == "state" and "state" not in df.columns:
            if "county" in df.columns:
                # State is first 2 digits of 5-digit county FIPS
                df = df.copy()
                df["state"] = df["county"].astype(str).str[:2]
            elif "tract" in df.columns:
                # State is first 2 digits of 11-digit tract FIPS
                df = df.copy()
                df["state"] = df["tract"].astype(str).str[:2]
            else:
                raise ValueError("Cannot derive state: no county or tract column found")

        # Identify numeric columns for aggregation (exclude the group column)
        numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns.tolist()
        # Remove group column from aggregation to avoid duplication
        if group_col in numeric_cols:
            numeric_cols.remove(group_col)

        # Separate count columns (should be summed) from metric columns (should be averaged)
        count_cols = [
            col for col in numeric_cols if "count" in col.lower() or "pooled_pooled_count" in col
        ]
        metric_cols = [col for col in numeric_cols if col not in count_cols]

        # Build aggregation dict
        agg_dict = {}
        for col in metric_cols:
            agg_dict[col] = "mean"
        for col in count_cols:
            agg_dict[col] = "sum"

        # Group and aggregate
        agg_df = df.groupby(group_col).agg(agg_dict).reset_index()

        self.logger.info(f"Aggregated to {target_geography} level", extra={"rows": len(agg_df)})

        return agg_df

    def aggregate_to_county(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate tract-level data to county level.

        Args:
            df: DataFrame with tract-level data

        Returns:
            County-level DataFrame

        Example:
            >>> oi = OpportunityInsightsConnector()
            >>> tract_data = oi.fetch_opportunity_atlas(geography="tract", state="06")
            >>> county_data = oi.aggregate_to_county(tract_data)
            >>> print(county_data.shape)
            (58, N)  # 58 counties in California
        """
        return self._aggregate_atlas(df, "county")

    def aggregate_to_cz(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate tract-level data to commuting zone (CZ) level.

        Args:
            df: DataFrame with tract-level data

        Returns:
            Commuting zone-level DataFrame

        Example:
            >>> oi = OpportunityInsightsConnector()
            >>> tract_data = oi.fetch_opportunity_atlas(geography="tract")
            >>> cz_data = oi.aggregate_to_cz(tract_data)
        """
        return self._aggregate_atlas(df, "cz")

    def aggregate_to_state(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate tract-level data to state level.

        Args:
            df: DataFrame with tract-level data

        Returns:
            State-level DataFrame

        Example:
            >>> oi = OpportunityInsightsConnector()
            >>> tract_data = oi.fetch_opportunity_atlas(geography="tract")
            >>> state_data = oi.aggregate_to_state(tract_data)
            >>> print(state_data.shape)
            (51, N)  # 50 states + DC
        """
        return self._aggregate_atlas(df, "state")

    @requires_license
    def get_available_metrics(self, data_product: str = "atlas") -> List[str]:
        """
        Get list of available metrics for a data product.

        Args:
            data_product: Data product name ("atlas", "social_capital", "ec")

        Returns:
            List of available metric names

        Example:
            >>> oi = OpportunityInsightsConnector()
            >>> metrics = oi.get_available_metrics("atlas")
            >>> print(metrics[:3])
            ['kfr_pooled_p25', 'kfr_pooled_p50', 'kfr_pooled_p75']
            >>>
            >>> # Week 4 Enhancement: Get social capital analysis methods
            >>> methods = oi.get_available_methods("social_capital")
            >>> print(methods[:3])
            ['get_high_ec_areas', 'get_low_ec_areas', 'compare_ec_by_state']
        """
        if data_product == "atlas":
            # Common Opportunity Atlas metrics
            return [
                "kfr_pooled_p25",
                "kfr_pooled_p50",
                "kfr_pooled_p75",
                "emp_rate_pooled",
                "jail_pooled",
                "frac_coll_plus_pooled",
                "married_pooled",
                "teenbrth_pooled",
            ]
        elif data_product == "social_capital":
            return [
                "ec_county",
                "ec_zip",
                "clustering_county",
                "clustering_zip",
                "support_ratio_county",
                "volunteering_rate_county",
            ]
        elif data_product == "ec":
            return [
                "ec",
                "ec_se",
                "ec_high",
                "ec_low",
            ]
        else:
            raise ValueError(f"Unknown data product: {data_product}")

    @requires_license
    def get_available_methods(self, category: str = "all") -> List[str]:
        """
        Get list of available analysis methods (Week 4 Enhancement).

        Args:
            category: Method category ("all", "social_capital", "mobility", "analysis")

        Returns:
            List of available method names

        Example:
            >>> oi = OpportunityInsightsConnector()
            >>> sc_methods = oi.get_available_methods("social_capital")
            >>> print(len(sc_methods))
            7
        """
        social_capital_methods = [
            "get_high_ec_areas",
            "get_low_ec_areas",
            "compare_ec_by_state",
            "get_ec_clustering_correlation",
            "get_social_capital_summary",
            "rank_areas_by_ec",
            "compare_mobility_and_social_capital",
        ]

        mobility_methods = [
            "fetch_opportunity_atlas",
            "aggregate_to_county",
            "aggregate_to_cz",
            "aggregate_to_state",
        ]

        data_methods = [
            "fetch",
            "fetch_social_capital",
            "fetch_economic_connectedness",
        ]

        if category == "social_capital":
            return social_capital_methods
        elif category == "mobility":
            return mobility_methods
        elif category == "data":
            return data_methods
        elif category == "all":
            return social_capital_methods + mobility_methods + data_methods
        else:
            raise ValueError(
                f"Unknown category: {category}. "
                f"Must be one of: all, social_capital, mobility, data"
            )

    def __repr__(self) -> str:
        """String representation of the connector."""
        return (
            f"OpportunityInsightsConnector("
            f"cache_dir='{self.cache.cache_dir}', "
            f"data_version='{self.data_version}', "
            f"connected={self.session is not None})"
        )

    # ============================================================
    # SOCIAL CAPITAL ANALYSIS METHODS (Week 4 Enhancement)
    # ============================================================

    @requires_license
    def get_high_ec_areas(
        self,
        geography: str = "county",
        threshold_percentile: float = 90.0,
        force_download: bool = False,
    ) -> pd.DataFrame:
        """
        Identify areas with high economic connectedness.

        Economic connectedness measures cross-class social interactions.
        Areas with high EC tend to have better mobility outcomes.

        Args:
            geography: Geographic level ("zip", "county")
            threshold_percentile: Percentile threshold for "high" EC (default: 90)
            force_download: Force re-download of data

        Returns:
            DataFrame with high-EC areas above threshold percentile

        Example:
            >>> oi = OpportunityInsightsConnector()
            >>> high_ec = oi.get_high_ec_areas(geography="county", threshold_percentile=90)
            >>> print(f"Found {len(high_ec)} counties with high EC")
            Found 314 counties with high EC (top 10%)
        """
        # Fetch social capital data
        sc_data = self.fetch_social_capital(geography=geography, force_download=force_download)

        # Identify EC column for this geography
        ec_col = f"ec_{geography}"
        if ec_col not in sc_data.columns:
            raise ValueError(f"Economic connectedness column '{ec_col}' not found")

        # Calculate threshold
        threshold = sc_data[ec_col].quantile(threshold_percentile / 100.0)

        # Filter to high-EC areas
        high_ec = sc_data[sc_data[ec_col] >= threshold].copy()

        # Sort by EC descending
        high_ec = high_ec.sort_values(ec_col, ascending=False)

        self.logger.info(
            f"Identified {len(high_ec)} high-EC areas",
            extra={
                "geography": geography,
                "threshold_percentile": threshold_percentile,
                "threshold_value": threshold,
                "max_ec": high_ec[ec_col].max(),
            },
        )

        return high_ec

    @requires_license
    def get_low_ec_areas(
        self,
        geography: str = "county",
        threshold_percentile: float = 10.0,
        force_download: bool = False,
    ) -> pd.DataFrame:
        """
        Identify areas with low economic connectedness.

        Low EC areas have limited cross-class interactions, which may
        indicate segregation and reduced mobility prospects.

        Args:
            geography: Geographic level ("zip", "county")
            threshold_percentile: Percentile threshold for "low" EC (default: 10)
            force_download: Force re-download of data

        Returns:
            DataFrame with low-EC areas below threshold percentile

        Example:
            >>> oi = OpportunityInsightsConnector()
            >>> low_ec = oi.get_low_ec_areas(geography="county", threshold_percentile=10)
            >>> print(f"Found {len(low_ec)} counties with low EC")
            Found 314 counties with low EC (bottom 10%)
        """
        # Fetch social capital data
        sc_data = self.fetch_social_capital(geography=geography, force_download=force_download)

        # Identify EC column for this geography
        ec_col = f"ec_{geography}"
        if ec_col not in sc_data.columns:
            raise ValueError(f"Economic connectedness column '{ec_col}' not found")

        # Calculate threshold
        threshold = sc_data[ec_col].quantile(threshold_percentile / 100.0)

        # Filter to low-EC areas
        low_ec = sc_data[sc_data[ec_col] <= threshold].copy()

        # Sort by EC ascending
        low_ec = low_ec.sort_values(ec_col, ascending=True)

        self.logger.info(
            f"Identified {len(low_ec)} low-EC areas",
            extra={
                "geography": geography,
                "threshold_percentile": threshold_percentile,
                "threshold_value": threshold,
                "min_ec": low_ec[ec_col].min(),
            },
        )

        return low_ec

    def compare_ec_by_state(
        self,
        states: Optional[List[str]] = None,
        force_download: bool = False,
    ) -> pd.DataFrame:
        """
        Compare economic connectedness across states.

        Aggregates county-level EC data to state level for comparison.

        Args:
            states: List of state FIPS codes (None = all states)
            force_download: Force re-download of data

        Returns:
            DataFrame with state-level EC statistics (mean, median, min, max)

        Example:
            >>> oi = OpportunityInsightsConnector()
            >>> state_ec = oi.compare_ec_by_state(states=["06", "36", "48"])
            >>> print(state_ec[['state', 'ec_mean', 'ec_median']])
               state  ec_mean  ec_median
            0     06    0.825      0.820
            1     36    0.892      0.885
            2     48    0.798      0.795
        """
        # Fetch county-level data
        county_data = self.fetch_social_capital(geography="county", force_download=force_download)

        # Extract state from county FIPS (first 2 digits)
        county_data = county_data.copy()
        county_data["state"] = county_data["county"].str[:2]

        # Filter to requested states
        if states is not None:
            states_formatted = [str(s).zfill(2) for s in states]
            county_data = county_data[county_data["state"].isin(states_formatted)]

        # Aggregate to state level
        ec_col = "ec_county"
        state_stats = (
            county_data.groupby("state")[ec_col]
            .agg(
                [
                    ("ec_mean", "mean"),
                    ("ec_median", "median"),
                    ("ec_min", "min"),
                    ("ec_max", "max"),
                    ("ec_std", "std"),
                    ("county_count", "count"),
                ]
            )
            .reset_index()
        )

        # Sort by mean EC descending
        state_stats = state_stats.sort_values("ec_mean", ascending=False)

        self.logger.info(
            f"Compared EC across {len(state_stats)} states",
            extra={
                "states_analyzed": len(state_stats),
                "highest_ec_state": state_stats.iloc[0]["state"],
                "highest_ec_mean": state_stats.iloc[0]["ec_mean"],
            },
        )

        return state_stats

    @requires_license
    def get_ec_clustering_correlation(
        self,
        geography: str = "county",
        force_download: bool = False,
    ) -> Dict[str, float]:
        """
        Calculate correlation between economic connectedness and clustering.

        EC measures cross-class friendships; clustering measures within-group
        density. Understanding their relationship helps identify network patterns.

        Args:
            geography: Geographic level ("zip", "county")
            force_download: Force re-download of data

        Returns:
            Dict with correlation statistics (pearson_r, sample_size)
            Note: Spearman correlation omitted to avoid scipy dependency

        Example:
            >>> oi = OpportunityInsightsConnector()
            >>> corr = oi.get_ec_clustering_correlation(geography="county")
            >>> print(f"Pearson r: {corr['pearson_r']:.3f}")
            Pearson r: 0.245
        """
        # Fetch social capital data
        sc_data = self.fetch_social_capital(geography=geography, force_download=force_download)

        # Identify relevant columns
        ec_col = f"ec_{geography}"
        clustering_col = f"clustering_{geography}"

        if ec_col not in sc_data.columns:
            raise ValueError(f"Economic connectedness column '{ec_col}' not found")
        if clustering_col not in sc_data.columns:
            raise ValueError(f"Clustering column '{clustering_col}' not found")

        # Remove missing values
        valid_data = sc_data[[ec_col, clustering_col]].dropna()

        # Calculate Pearson correlation (no scipy dependency)
        pearson_r = valid_data[ec_col].corr(valid_data[clustering_col], method="pearson")

        result = {
            "pearson_r": pearson_r,
            "sample_size": len(valid_data),
            "geography": geography,
        }

        self.logger.info(
            "Calculated EC-clustering correlation",
            extra=result,
        )

        return result

    @requires_license
    def get_social_capital_summary(
        self,
        geography: str = "county",
        geo_id: Optional[str] = None,
        force_download: bool = False,
    ) -> Dict[str, Union[str, float, int]]:
        """
        Get comprehensive social capital summary for a specific area.

        Provides all available social capital metrics for one geographic unit.

        Args:
            geography: Geographic level ("zip", "county")
            geo_id: Geographic identifier (county FIPS or ZIP code)
            force_download: Force re-download of data

        Returns:
            Dict with all available social capital metrics for the area

        Raises:
            ValueError: If geo_id not found in data

        Example:
            >>> oi = OpportunityInsightsConnector()
            >>> # Los Angeles County
            >>> la_social_capital = oi.get_social_capital_summary(
            ...     geography="county",
            ...     geo_id="06037"
            ... )
            >>> print(f"LA EC: {la_social_capital['ec_county']:.3f}")
            LA EC: 0.892
        """
        # Fetch social capital data
        sc_data = self.fetch_social_capital(geography=geography, force_download=force_download)

        # Identify geographic identifier column
        geo_col = geography  # 'county' or 'zip'
        if geo_col not in sc_data.columns:
            raise ValueError(f"Geographic column '{geo_col}' not found")

        # Format geo_id appropriately
        if geography == "county":
            geo_id_formatted = str(geo_id).zfill(5)
        elif geography == "zip":
            geo_id_formatted = str(geo_id).zfill(5)
        else:
            geo_id_formatted = str(geo_id)

        # Find the area
        area_data = sc_data[sc_data[geo_col] == geo_id_formatted]

        if len(area_data) == 0:
            raise ValueError(f"Geographic ID '{geo_id}' not found in {geography}-level data")

        # Convert to dict (first row if multiple matches)
        summary = area_data.iloc[0].to_dict()

        self.logger.info(
            f"Retrieved social capital summary for {geography} {geo_id}",
            extra={
                "geography": geography,
                "geo_id": geo_id,
                "metrics_count": len(summary),
            },
        )

        return summary

    def rank_areas_by_ec(
        self,
        geography: str = "county",
        top_n: Optional[int] = None,
        ascending: bool = False,
        force_download: bool = False,
    ) -> pd.DataFrame:
        """
        Rank geographic areas by economic connectedness.

        Args:
            geography: Geographic level ("zip", "county")
            top_n: Number of top areas to return (None = all areas)
            ascending: If True, rank from lowest to highest EC
            force_download: Force re-download of data

        Returns:
            DataFrame with areas ranked by EC, including rank column

        Example:
            >>> oi = OpportunityInsightsConnector()
            >>> top_counties = oi.rank_areas_by_ec(geography="county", top_n=10)
            >>> print(top_counties[['county', 'ec_county', 'ec_rank']])
        """
        # Fetch social capital data
        sc_data = self.fetch_social_capital(geography=geography, force_download=force_download)

        # Identify EC column
        ec_col = f"ec_{geography}"
        if ec_col not in sc_data.columns:
            raise ValueError(f"Economic connectedness column '{ec_col}' not found")

        # Sort by EC
        ranked = sc_data.sort_values(ec_col, ascending=ascending).copy()

        # Add rank column
        ranked["ec_rank"] = range(1, len(ranked) + 1)

        # Limit to top N if specified
        if top_n is not None:
            ranked = ranked.head(top_n)

        direction = "lowest" if ascending else "highest"
        self.logger.info(
            f"Ranked areas by EC ({direction})",
            extra={
                "geography": geography,
                "total_areas": len(sc_data),
                "returned_areas": len(ranked),
                "top_ec": ranked.iloc[0][ec_col],
            },
        )

        return ranked

    def compare_mobility_and_social_capital(
        self,
        geography: str = "county",
        states: Optional[List[str]] = None,
        force_download: bool = False,
    ) -> pd.DataFrame:
        """
        Compare intergenerational mobility with social capital metrics.

        Joins Opportunity Atlas mobility data with Social Capital Atlas data
        to enable analysis of their relationship.

        Args:
            geography: Geographic level ("county" only for now)
            states: List of state FIPS codes to filter (None = all)
            force_download: Force re-download of data

        Returns:
            DataFrame with both mobility and social capital metrics

        Raises:
            ValueError: If geography not supported

        Example:
            >>> oi = OpportunityInsightsConnector()
            >>> combined = oi.compare_mobility_and_social_capital(
            ...     geography="county",
            ...     states=["06", "36"]
            ... )
            >>> # Correlation between mobility and EC
            >>> corr = combined['kfr_pooled_p25'].corr(combined['ec_county'])
            >>> print(f"Mobility-EC correlation: {corr:.3f}")
            Mobility-EC correlation: 0.385
        """
        if geography != "county":
            raise ValueError(
                "Currently only county-level comparison supported. "
                "Tract-level joining coming in future enhancement."
            )

        # Fetch Opportunity Atlas data
        atlas_data = self.fetch_opportunity_atlas(geography="county", force_download=force_download)

        # Fetch Social Capital data
        sc_data = self.fetch_social_capital(geography="county", force_download=force_download)

        # Merge on county FIPS
        combined = pd.merge(
            atlas_data, sc_data, on="county", how="inner", suffixes=("_atlas", "_sc")
        )

        # Filter by state if specified
        if states is not None:
            states_formatted = [str(s).zfill(2) for s in states]
            combined = combined[combined["state"].isin(states_formatted)]

        self.logger.info(
            "Merged mobility and social capital data",
            extra={
                "geography": geography,
                "total_counties": len(combined),
                "atlas_metrics": len([c for c in atlas_data.columns if c != "county"]),
                "sc_metrics": len([c for c in sc_data.columns if c != "county"]),
            },
        )

        return combined
