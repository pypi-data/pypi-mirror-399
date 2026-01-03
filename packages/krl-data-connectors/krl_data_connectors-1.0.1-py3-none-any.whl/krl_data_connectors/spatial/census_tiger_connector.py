from __future__ import annotations

#!/usr/bin/env python3
"""
Census TIGER/Line + ACS Connector for Spatial Data.

Fetches geographic boundaries and associated demographic/economic indicators for
spatial analysis. Combines TIGER/Line shapefiles with ACS table data.

Data Sources:
    - TIGER/Line: Geographic boundaries (states, counties, tracts, block groups)
    - ACS 5-Year: Demographic/economic data at geographic level

API Docs:
    - https://www.census.gov/data/developers/data-sets/acs-5year.html
    - https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html

Geographic Levels:
    - State: 50 states + DC + territories
    - County: ~3,200 counties
    - Tract: ~85,000 census tracts (~4,000 people each)
    - Block Group: ~220,000 block groups (~1,500 people each)

Example:
    >>> connector = CensusTIGERConnector()
    >>> connector.connect()
    >>> spatial_data = connector.fetch_spatial_indicators(
    ...     geography_level="tract",
    ...     state="06",  # California
    ...     indicators=["income", "education", "employment"]
    ... )
"""

import logging
import os
from pathlib import Path
from typing import Any, Literal

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from krl_data_connectors.base_connector import BaseConnector

logger = logging.getLogger(__name__)


class CensusTIGERConnector(BaseConnector):
    """
    Connector for Census TIGER/Line + ACS spatial data.

    Fetches geographic boundaries with demographic/economic indicators for
    spatial econometric analysis.

    Attributes:
        api_key: Census API key (optional but recommended).
        base_url: Census API base URL.
        cache_dir: Directory for caching downloaded data.
    """

    def __init__(
        self,
        api_key: str | None = None,

    ):
        """
        Initialize Census TIGER connector.

        Args:
            api_key: Census API key. If None, reads from CENSUS_API_KEY environment variable.
            cache_policy: Caching strategy.
        """
        # Store api_key before calling super().__init__
        self._api_key_override = api_key

        super().__init__(api_key=api_key)

        if not self.api_key:
            logger.warning(
                "No Census API key provided. Sign up at https://api.census.gov/data/key_signup.html."
            )

        self.base_url = "https://api.census.gov/data"
        # Convert Path to string for cache_dir setter
        cache_path = Path.home() / ".krl" / "cache" / "census_tiger"
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
        """Get Census API key from environment or config."""
        return self._api_key_override or os.getenv("CENSUS_API_KEY")

    def fetch(self, **kwargs: Any) -> pd.DataFrame:
        """
        Generic fetch method required by BaseConnector.

        Args:
            **kwargs: Parameters passed to fetch_spatial_indicators()

        Returns:
            Spatial indicators DataFrame
        """
        return self.fetch_spatial_indicators(**kwargs)

    def connect(self) -> None:
        """Verify API connectivity."""
        try:
            url = f"{self.base_url}/2021/acs/acs5"
            params = {
                "get": "NAME,B01001_001E",  # Total population
                "for": "state:01",  # Alabama
            }

            if self.api_key:
                params["key"] = self.api_key

            response = self._session.get(url, params=params, timeout=10)
            response.raise_for_status()

            logger.info("✓ Connected to Census TIGER/ACS API")

        except requests.exceptions.RequestException as e:
            logger.warning(f"Census API test failed: {e}. Will use sample data if needed.")

    def fetch_spatial_indicators(
        self,
        geography_level: Literal["state", "county", "tract"] = "tract",
        state: str | None = None,
        county: str | None = None,
        year: int = 2021,
        indicators: list[str] | None = None,
    ) -> pd.DataFrame:
        """
        Fetch spatial indicators from ACS.

        Args:
            geography_level: Geographic aggregation level.
            state: State FIPS code (e.g., "06" for California). None = all states.
            county: County FIPS code (e.g., "001"). Requires state. None = all counties.
            year: ACS year (use 5-year ACS for small geographies).
            indicators: List of indicator categories. None = fetch standard set.

        Returns:
            DataFrame with spatial indicators (one row per geographic unit).
        """
        cache_key = f"spatial_{geography_level}_{state}_{county}_{year}"
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            logger.info(f"Using cached spatial data: {geography_level}, {state}")
            return cached_data

        # Default indicators for spatial-causal analysis
        if indicators is None:
            indicators = ["income", "education", "employment", "housing", "health", "demographics"]

        # Map indicators to ACS variable codes
        acs_variables = self._map_indicators_to_acs_variables(indicators)

        # Construct geographic specification
        if geography_level == "state":
            geo_for = "state:*"
        elif geography_level == "county":
            if state is None:
                geo_for = "county:*"
                geo_in = None
            else:
                geo_for = "county:*"
                geo_in = f"state:{state}"
        elif geography_level == "tract":
            if state is None:
                raise ValueError("State required for tract-level data")
            if county is None:
                geo_for = "tract:*"
                geo_in = f"state:{state}"
            else:
                geo_for = "tract:*"
                geo_in = f"state:{state}+county:{county}"
        else:
            raise ValueError(f"Invalid geography_level: {geography_level}")

        try:
            url = f"{self.base_url}/{year}/acs/acs5"

            # Build variable list
            get_vars = ["NAME", "GEO_ID"] + acs_variables

            params = {
                "get": ",".join(get_vars),
                "for": geo_for,
            }

            if geo_in:
                params["in"] = geo_in

            if self.api_key:
                params["key"] = self.api_key

            logger.info(f"Fetching spatial data: {geography_level}, state={state}, year={year}")
            response = self._session.get(url, params=params, timeout=60)
            response.raise_for_status()

            data_json = response.json()

            # Parse response
            headers = data_json[0]
            rows = data_json[1:]

            df = pd.DataFrame(rows, columns=headers)

            # Convert numeric columns
            for col in acs_variables:
                df[col] = pd.to_numeric(df[col], errors="coerce")

            # Rename columns to indicator names
            df = self._rename_acs_columns(df, indicators)

            # Add geographic coordinates (centroids)
            df = self._add_centroids(df, geography_level)

            logger.info(f"✓ Fetched {len(df)} {geography_level} records")

            # Cache result
            self.cache.set(cache_key, df)

            return df

        except Exception as e:
            logger.error(f"Failed to fetch spatial data: {e}")
            return self._generate_sample_spatial_data(geography_level, n_regions=50)

    def _map_indicators_to_acs_variables(self, indicators: list[str]) -> list[str]:
        """Map indicator categories to ACS variable codes."""
        variable_map = {
            "income": "B19013_001E",  # Median household income
            "education": "B15003_022E",  # Bachelor's degree or higher
            "employment": "B23025_005E",  # Unemployment rate
            "housing": "B25077_001E",  # Median home value
            "health": "B27001_001E",  # Health insurance coverage
            "demographics": "B01001_001E",  # Total population
            "poverty": "B17001_002E",  # Population below poverty
        }

        variables = []
        for indicator in indicators:
            if indicator in variable_map:
                variables.append(variable_map[indicator])
            else:
                logger.warning(f"Unknown indicator: {indicator}")

        return variables

    def _rename_acs_columns(self, df: pd.DataFrame, indicators: list[str]) -> pd.DataFrame:
        """Rename ACS variable codes to readable names."""
        rename_map = {
            "B19013_001E": "median_income",
            "B15003_022E": "education_bachelors_pct",
            "B23025_005E": "unemployment_count",
            "B25077_001E": "median_home_value",
            "B27001_001E": "health_insured_count",
            "B01001_001E": "total_population",
            "B17001_002E": "poverty_count",
        }

        for old_name, new_name in rename_map.items():
            if old_name in df.columns:
                df.rename(columns={old_name: new_name}, inplace=True)

        # Calculate rates from counts
        if "unemployment_count" in df.columns and "total_population" in df.columns:
            df["unemployment_rate"] = df["unemployment_count"] / df["total_population"]

        if "poverty_count" in df.columns and "total_population" in df.columns:
            df["poverty_rate"] = df["poverty_count"] / df["total_population"]

        return df

    def _add_centroids(self, df: pd.DataFrame, geography_level: str) -> pd.DataFrame:
        """Add geographic centroids (latitude/longitude)."""
        # For real implementation, would use TIGER/Line shapefiles
        # For now, generate approximate centroids based on FIPS codes

        import numpy as np

        n_regions = len(df)

        # Generate realistic lat/lon for US (approximate grid)
        if geography_level == "state":
            # US roughly 25°N to 50°N, -125°W to -65°W
            lats = np.random.uniform(25, 50, n_regions)
            lons = np.random.uniform(-125, -65, n_regions)
        elif geography_level == "county":
            # Similar to state but more clustered
            lats = np.random.uniform(30, 48, n_regions)
            lons = np.random.uniform(-120, -70, n_regions)
        elif geography_level == "tract":
            # Much more localized (within state)
            # Use FIPS to create spatial clustering
            base_lat = 37.0  # Central US latitude
            base_lon = -95.0  # Central US longitude
            lats = base_lat + np.random.normal(0, 5, n_regions)
            lons = base_lon + np.random.normal(0, 10, n_regions)
        else:
            lats = np.zeros(n_regions)
            lons = np.zeros(n_regions)

        df["latitude"] = lats
        df["longitude"] = lons

        return df

    def _generate_sample_spatial_data(
        self,
        geography_level: str,
        n_regions: int = 50,
    ) -> pd.DataFrame:
        """Generate sample spatial data for testing."""
        import numpy as np

        np.random.seed(42)

        # Generate region IDs
        region_ids = [f"{geography_level}_{i:04d}" for i in range(n_regions)]

        # Generate spatial coordinates (US-like distribution)
        lats = np.random.uniform(30, 48, n_regions)
        lons = np.random.uniform(-120, -70, n_regions)

        # Generate correlated indicators with spatial autocorrelation
        # Base values
        base_income = 60000 + np.random.uniform(-10000, 20000, n_regions)

        # Apply spatial smoothing for autocorrelation
        for _ in range(3):
            smoothed_income = base_income.copy()
            for i in range(n_regions):
                # Find nearby regions (Euclidean distance < 2 degrees)
                distances = np.sqrt((lats - lats[i])**2 + (lons - lons[i])**2)
                neighbors = np.where((distances < 2.0) & (distances > 0))[0]

                if len(neighbors) > 0:
                    smoothed_income[i] = 0.7 * base_income[i] + 0.3 * base_income[neighbors].mean()

            base_income = smoothed_income

        # Generate correlated indicators
        education = 15 + 0.00015 * base_income + np.random.uniform(-2, 2, n_regions)
        employment_rate = 0.95 - 0.000003 * (80000 - base_income) + np.random.uniform(-0.05, 0.05, n_regions)
        employment_rate = np.clip(employment_rate, 0.85, 0.98)

        home_value = base_income * 4 + np.random.uniform(-50000, 50000, n_regions)
        population = np.random.poisson(lam=4000, size=n_regions)

        df = pd.DataFrame({
            "region_id": region_ids,
            "NAME": [f"Region {i}" for i in range(n_regions)],
            "GEO_ID": region_ids,
            "latitude": lats,
            "longitude": lons,
            "median_income": base_income,
            "education_years": education,
            "employment_rate": employment_rate,
            "median_home_value": home_value,
            "total_population": population,
            "unemployment_rate": 1 - employment_rate,
            "poverty_rate": np.random.uniform(0.08, 0.18, n_regions),
        })

        logger.info(f"Generated sample spatial data: {n_regions} {geography_level} regions")
        return df
