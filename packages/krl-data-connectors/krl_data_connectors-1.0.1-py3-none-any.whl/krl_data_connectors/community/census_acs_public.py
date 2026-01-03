# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Census ACS Public Connector - Community Tier

Free access to state-level American Community Survey (ACS) data.
No API key required (uses public access).

Available Data:
- State-level demographics (population, age, race/ethnicity)
- State-level economic indicators (income, poverty, employment)
- State-level housing characteristics
- 5-year ACS estimates only (most reliable for state-level)

Usage:
    from krl_data_connectors.community import CensusACSPublicConnector
    
    census = CensusACSPublicConnector()
    population = census.get_population_by_state(year=2022)
    income = census.get_median_income_by_state(year=2022)
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from krl_data_connectors import BaseConnector
from krl_data_connectors.core import DataTier


class CensusACSPublicConnector(BaseConnector):
    """
    Census ACS Public Connector - Community Tier

    Free access to state-level American Community Survey data.
    No license validation required for Community tier.
    Limited to state-level geography and 5-year estimates.
    """

    _connector_name = "Census_ACS_Public"
    _required_tier = DataTier.COMMUNITY

    BASE_URL = "https://api.census.gov/data"

    # Common ACS variables for Community tier
    COMMON_VARIABLES = {
        # Population
        "B01001_001E": "Total Population",
        "B01002_001E": "Median Age",
        "B01001_002E": "Male Population",
        "B01001_026E": "Female Population",
        # Race/Ethnicity
        "B02001_002E": "White Alone",
        "B02001_003E": "Black or African American Alone",
        "B02001_005E": "Asian Alone",
        "B03003_003E": "Hispanic or Latino",
        # Economic
        "B19013_001E": "Median Household Income",
        "B17001_002E": "Population Below Poverty Level",
        "B23025_005E": "Unemployed",
        # Housing
        "B25001_001E": "Total Housing Units",
        "B25003_002E": "Owner Occupied Housing Units",
        "B25003_003E": "Renter Occupied Housing Units",
        "B25077_001E": "Median Home Value",
        # Education
        "B15003_022E": "Bachelor's Degree",
        "B15003_023E": "Master's Degree",
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
        Initialize Census ACS Public connector.

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
        self.base_url = self.BASE_URL
        self.logger.info(
            "Initialized Census ACS Public connector (Community tier)",
            extra={"geography": "state-level only"},
        )

    def _get_api_key(self) -> Optional[str]:
        """
        Get API key from environment or config.
        
        Census API doesn't require an API key for basic access,
        but having one increases rate limits.
        
        Returns:
            API key or None
        """
        import os
        return os.environ.get("CENSUS_API_KEY")

    def connect(self) -> bool:
        """
        Test connection to Census API.

        Returns:
            True if connection successful
        """
        try:
            # Initialize session if needed
            self._init_session()
            
            # Test with a simple request
            url = f"{self.base_url}/2022/acs/acs5"
            params = {"get": "NAME,B01001_001E", "for": "state:*"}

            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()

            self.logger.info("Successfully connected to Census API")
            return True

        except Exception as e:
            self.logger.error(f"Failed to connect to Census API: {str(e)}")
            return False

    def get_data(self, year: int, variables: List[str], **kwargs: Any) -> pd.DataFrame:
        """
        Get ACS data for all states.

        Community tier: State-level only, 5-year estimates.

        Args:
            year: Data year (e.g., 2022)
            variables: List of variable codes

        Returns:
            DataFrame with state-level data

        Raises:
            ValueError: If year not available or variables invalid
        """
        # Initialize session if needed
        self._init_session()
        
        # Community tier: 5-year estimates only, state-level only
        dataset = "acs/acs5"
        geography = "state:*"

        url = f"{self.base_url}/{year}/{dataset}"

        # Add NAME to get state names
        if "NAME" not in variables:
            variables = ["NAME"] + variables

        params = {"get": ",".join(variables), "for": geography}

        self.logger.info(
            f"Fetching Census ACS data for {year}",
            extra={"year": year, "variables": len(variables), "geography": "state"},
        )

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            # First row is headers
            headers = data[0]
            rows = data[1:]

            df = pd.DataFrame(rows, columns=headers)

            # Convert numeric columns
            for col in df.columns:
                if col not in ["NAME", "state"]:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            self.logger.info(
                f"Retrieved data for {len(df)} states", extra={"year": year, "rows": len(df)}
            )

            return df

        except Exception as e:
            self.logger.error(f"Failed to fetch Census data: {e}")
            raise

    def get_population_by_state(self, year: int = 2022) -> pd.DataFrame:
        """
        Get total population by state.

        Args:
            year: Data year

        Returns:
            DataFrame with state populations
        """
        return self.get_data(year=year, variables=["B01001_001E"])  # Total population

    def get_median_income_by_state(self, year: int = 2022) -> pd.DataFrame:
        """
        Get median household income by state.

        Args:
            year: Data year

        Returns:
            DataFrame with state median incomes
        """
        return self.get_data(year=year, variables=["B19013_001E"])  # Median household income

    def get_demographics_by_state(self, year: int = 2022) -> pd.DataFrame:
        """
        Get comprehensive demographics by state.

        Includes: population, median age, race/ethnicity, income, poverty.

        Args:
            year: Data year

        Returns:
            DataFrame with state demographics
        """
        variables = [
            "B01001_001E",  # Total population
            "B01002_001E",  # Median age
            "B02001_002E",  # White alone
            "B02001_003E",  # Black alone
            "B02001_005E",  # Asian alone
            "B03003_003E",  # Hispanic/Latino
            "B19013_001E",  # Median income
            "B17001_002E",  # Below poverty
        ]

        return self.get_data(year=year, variables=variables)

    def list_available_variables(self) -> Dict[str, str]:
        """
        List common variables available in Community tier.

        Returns:
            Dictionary mapping variable code to description
        """
        return self.COMMON_VARIABLES.copy()

    def fetch(self, year: int, variables: Optional[List[str]] = None, **kwargs) -> pd.DataFrame:
        """
        Generic fetch method.

        Args:
            year: Data year
            variables: List of variable codes (default: population)
            **kwargs: Additional arguments

        Returns:
            DataFrame with census data
        """
        if variables is None:
            variables = ["B01001_001E"]  # Default to total population

        return self.get_data(year=year, variables=variables, **kwargs)
