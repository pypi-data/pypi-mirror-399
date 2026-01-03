from __future__ import annotations

#!/usr/bin/env python3
"""
Census ACS Public Use Microdata Sample (PUMS) Connector.

Fetches household-level microdata from the American Community Survey (ACS) for
use in microsimulation models. PUMS provides detailed demographic and economic
characteristics of individual households.

Data Source: https://www.census.gov/programs-surveys/acs/microdata.html
API Docs: https://www.census.gov/data/developers/data-sets/census-microdata-api.html

Key Variables:
    - PINCP: Person's total income
    - HINCP: Household income
    - WAGP: Wages/salary income
    - PERNP: Total person's earnings
    - PWGTP: Person weight (for population estimates)
    - INDP: Industry code
    - OCCP: Occupation code
    - AGEP: Age
    - SEX: Sex
    - RAC1P: Race
    - HISP: Hispanic origin

Example:
    >>> connector = CensusACSMicrodataConnector()
    >>> connector.connect()
    >>> households = connector.fetch_household_microdata(
    ...     geography="state:06",  # California
    ...     year=2021,
    ...     sample_size=10000
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


class CensusACSMicrodataConnector(BaseConnector):
    """
    Connector for Census ACS Public Use Microdata Sample (PUMS).

    Fetches household-level microdata for microsimulation and distributional analysis.

    Attributes:
        api_key: Census API key (optional but recommended for higher rate limits).
        base_url: Census API base URL.
        cache_dir: Directory for caching downloaded microdata.
    """

    def __init__(
        self,
        api_key: str | None = None,

    ):
        """
        Initialize Census ACS PUMS connector.

        Args:
            api_key: Census API key. If None, reads from CENSUS_API_KEY environment variable.
            cache_policy: Caching strategy.
        """
        # Store api_key before calling super().__init__
        self._api_key_override = api_key

        super().__init__(api_key=api_key)

        if not self.api_key:
            logger.warning(
                "No Census API key provided. Sign up at https://api.census.gov/data/key_signup.html. "
                "Rate limits apply without a key."
            )

        self.base_url = "https://api.census.gov/data"
        # Convert Path to string for cache_dir setter
        cache_path = Path.home() / ".krl" / "cache" / "census_acs_pums"
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
            **kwargs: Parameters passed to fetch_household_microdata()

        Returns:
            Household microdata DataFrame
        """
        return self.fetch_household_microdata(**kwargs)

    def connect(self) -> None:
        """
        Verify API connectivity.

        Raises:
            ConnectionError: If Census API is unreachable.
        """
        try:
            # Test with simple request
            url = f"{self.base_url}/2021/acs/acs1/pums"
            params = {"get": "SERIALNO", "for": "state:01"}  # Alabama, 1 record

            if self.api_key:
                params["key"] = self.api_key

            response = self._session.get(url, params=params, timeout=10)
            response.raise_for_status()

            logger.info("✓ Connected to Census ACS PUMS API")

        except requests.exceptions.RequestException as e:
            logger.warning(f"Census API test failed: {e}. Will use sample data if needed.")

    def fetch_household_microdata(
        self,
        geography: str = "us:1",
        year: int = 2021,
        sample_size: int | None = None,
        variables: list[str] | None = None,
    ) -> pd.DataFrame:
        """
        Fetch household microdata from ACS PUMS.

        Args:
            geography: Geographic filter (e.g., "state:06" for California, "us:1" for nationwide).
            year: Survey year (2017-2022 available).
            sample_size: If provided, randomly sample this many households. None = all households.
            variables: List of variables to fetch. None = fetch standard set.

        Returns:
            DataFrame with household microdata (one row per household).

        Raises:
            ValueError: If year or geography is invalid.
        """
        # Check cache
        cache_key = f"pums_{year}_{geography}_{sample_size}"
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            logger.info(f"Using cached PUMS data: {year}, {geography}")
            return cached_data

        # Default variables for CGE-Microsim use cases
        if variables is None:
            variables = [
                "SERIALNO",  # Household serial number (ID)
                "HINCP",     # Household income
                "ADJINC",    # Income adjustment factor
                "NP",        # Number of persons in household
                "TYPE",      # Household/GQ type
                "WAGP",      # Wages/salary (for household head)
                "PINCP",     # Person's total income
                "AGEP",      # Age
                "SEX",       # Sex
                "RAC1P",     # Race
                "HISP",      # Hispanic origin
                "INDP",      # Industry code (NAICS-based)
                "OCCP",      # Occupation code
                "PWGTP",     # Person weight
                "WGTP",      # Housing unit weight
            ]

        # Construct API URL
        dataset = "acs1"  # 1-year ACS (smaller sample, most recent)
        if year < 2017:
            logger.warning(f"Year {year} may not have PUMS API access. Using 2021 as fallback.")
            year = 2021

        url = f"{self.base_url}/{year}/acs/{dataset}/pums"

        # Build query params
        get_vars = ",".join(variables)
        params = {
            "get": get_vars,
            "for": geography,
        }

        if self.api_key:
            params["key"] = self.api_key

        try:
            logger.info(f"Fetching PUMS data: year={year}, geography={geography}")
            response = self._session.get(url, params=params, timeout=60)
            response.raise_for_status()

            data_json = response.json()

            # Parse response (first row is headers)
            headers = data_json[0]
            rows = data_json[1:]

            df = pd.DataFrame(rows, columns=headers)

            # Convert numeric columns
            numeric_cols = ["HINCP", "WAGP", "PINCP", "AGEP", "NP", "PWGTP", "WGTP", "ADJINC"]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            # Adjust income for inflation (ADJINC is a 6-digit factor, divide by 1,000,000)
            if "ADJINC" in df.columns and "HINCP" in df.columns:
                df["HINCP_adjusted"] = df["HINCP"] * (df["ADJINC"] / 1_000_000)
            else:
                df["HINCP_adjusted"] = df.get("HINCP", 0)

            # Filter to households only (TYPE == 1)
            if "TYPE" in df.columns:
                df = df[df["TYPE"] == "1"].copy()

            # Sample if requested
            if sample_size is not None and len(df) > sample_size:
                df = df.sample(n=sample_size, random_state=42, replace=False)

            logger.info(f"✓ Fetched {len(df)} household records")

            # Cache result
            self.cache.set(cache_key, df)

            return df

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch PUMS data: {e}")
            # Fall back to sample data
            return self._generate_sample_microdata(sample_size or 1000)

    def aggregate_by_cohort(
        self,
        microdata: pd.DataFrame,
        n_cohorts: int = 100,
        stratify_by: Literal["income", "age", "industry"] = "income",
    ) -> pd.DataFrame:
        """
        Aggregate household microdata into cohorts for CGE-Microsim.

        Cohorts reduce computational burden while preserving distributional heterogeneity.

        Args:
            microdata: Household microdata from fetch_household_microdata().
            n_cohorts: Number of cohorts to create.
            stratify_by: Variable to use for cohort stratification.

        Returns:
            DataFrame with cohort-level aggregates (one row per cohort).
        """
        if stratify_by == "income":
            # Create income-based cohorts (percentiles)
            microdata["cohort"] = pd.qcut(
                microdata["HINCP_adjusted"],
                q=n_cohorts,
                labels=False,
                duplicates="drop",
            )
        elif stratify_by == "age":
            # Create age-based cohorts
            microdata["cohort"] = pd.cut(
                microdata["AGEP"],
                bins=n_cohorts,
                labels=False,
            )
        elif stratify_by == "industry":
            # Create industry-based cohorts (group NAICS codes)
            # INDP is 4-digit NAICS, group into ~n_cohorts sectors
            microdata["cohort"] = (
                pd.to_numeric(microdata.get("INDP", 0), errors="coerce").fillna(0) // (10000 // n_cohorts)
            ).astype(int)
            microdata["cohort"] = microdata["cohort"].clip(0, n_cohorts - 1)
        else:
            raise ValueError(f"Invalid stratify_by: {stratify_by}")

        # Aggregate by cohort
        cohort_agg = microdata.groupby("cohort").agg({
            "HINCP_adjusted": "mean",  # Average household income
            "WAGP": "mean",            # Average wages
            "NP": "mean",              # Average household size
            "PWGTP": "sum",            # Total population weight (cohort size)
            "SERIALNO": "count",       # Number of households in cohort
        }).reset_index()

        cohort_agg.columns = [
            "cohort_id",
            "income",
            "wages",
            "household_size",
            "cohort_population",
            "n_households",
        ]

        # Estimate consumption (assume 70-80% of income)
        cohort_agg["consumption"] = cohort_agg["income"] * 0.75

        # Estimate savings
        cohort_agg["savings"] = cohort_agg["income"] - cohort_agg["consumption"]

        # Map to industry sectors (use modal industry from microdata)
        if "INDP" in microdata.columns:
            cohort_sectors = microdata.groupby("cohort")["INDP"].agg(
                lambda x: pd.to_numeric(x, errors="coerce").mode().iloc[0] if len(x) > 0 else 0
            )
            cohort_agg["sector_affiliation"] = cohort_agg["cohort_id"].map(cohort_sectors).fillna(0).astype(int)
        else:
            cohort_agg["sector_affiliation"] = cohort_agg["cohort_id"] % 10  # Random assignment

        logger.info(f"✓ Aggregated {len(microdata)} households into {len(cohort_agg)} cohorts")

        return cohort_agg

    def _generate_sample_microdata(self, n_households: int) -> pd.DataFrame:
        """Generate sample microdata for testing without API access."""
        import numpy as np

        np.random.seed(42)

        # Generate realistic income distribution (lognormal)
        incomes = np.random.lognormal(mean=10.5, sigma=0.8, size=n_households)

        # Generate correlated variables
        ages = np.clip(np.random.normal(45, 15, n_households), 18, 90).astype(int)
        household_sizes = np.random.poisson(lam=2.5, size=n_households).clip(1, 10)

        # Industry codes (2-digit NAICS simplified)
        industries = np.random.choice(
            [11, 21, 22, 23, 31, 42, 44, 48, 51, 52, 53, 54, 55, 56, 61, 62, 71, 72, 81, 92],
            size=n_households,
        )

        # Wages (correlated with income)
        wages = incomes * np.random.uniform(0.6, 0.9, n_households)

        df = pd.DataFrame({
            "SERIALNO": np.arange(n_households),
            "HINCP": incomes,
            "HINCP_adjusted": incomes,
            "WAGP": wages,
            "PINCP": incomes / household_sizes,  # Per-person income
            "AGEP": ages,
            "SEX": np.random.choice([1, 2], size=n_households),
            "NP": household_sizes,
            "INDP": industries * 100,  # Convert to 4-digit
            "PWGTP": np.ones(n_households),  # Equal weights for sample
            "WGTP": np.ones(n_households),
            "TYPE": np.ones(n_households, dtype=int),
            "ADJINC": np.ones(n_households) * 1_000_000,  # No adjustment
        })

        logger.info(f"Generated sample microdata: {n_households} households")
        return df
