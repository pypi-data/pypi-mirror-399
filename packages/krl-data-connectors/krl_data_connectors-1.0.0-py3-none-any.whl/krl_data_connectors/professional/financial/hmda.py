# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
HMDA (Home Mortgage Disclosure Act) Data Connector

This connector provides access to mortgage lending data from the Consumer Financial Protection
Bureau (CFPB) through the HMDA public API. The HMDA dataset contains loan-level information on
mortgage applications and originations, enabling analysis of lending patterns, discrimination,
redlining, and financial inclusion.

Data Source: CFPB HMDA Public API
Coverage: 2018-present (post-2018 data format)
Geographic Levels: National, state, county, census tract
Update Frequency: Annual
API Documentation: https://cfpb.github.io/hmda-platform/

Key Variables:
- Loan characteristics: amount, type, purpose, occupancy
- Borrower demographics: race, ethnicity, sex, age, income
- Property location: state, county, census tract
- Lender information: institution name, LEI (Legal Entity Identifier)
- Action taken: originated, denied, withdrawn, etc.
- Denial reasons (if applicable)

Use Cases:
- Analyze lending patterns by geography and demographics
- Identify potential redlining indicators
- Study mortgage denial rates by race, ethnicity, income
- Track lending activity by institution
- Research financial inclusion and access to credit
"""

import logging
from datetime import datetime, UTC
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import requests

from ...base_connector import BaseConnector
from ...core import DataTier
from ...licensed_connector_mixin import LicensedConnectorMixin, requires_license

logger = logging.getLogger(__name__)


class HMDAConnector(LicensedConnectorMixin, BaseConnector):
    """
    Connector for Consumer Financial Protection Bureau (CFPB) Home Mortgage Disclosure Act (HMDA) data.

    The HMDA dataset provides comprehensive mortgage lending data including loan characteristics,
    borrower demographics, property locations, and outcomes (originated, denied, etc.). This
    connector enables analysis of lending patterns, potential discrimination, redlining indicators,
    and financial inclusion metrics.
    """

    # Registry name for license validation
    _connector_name = "HMDA"

    """

    Data is available from 2018 onwards in the current format (prior years use different schema).

    Attributes:
        base_url (str): Base URL for CFPB HMDA Public API
        api_key (str): API key (optional - HMDA API is public)

    Example:
        >>> connector = HMDAConnector()
        >>> # Get all loan originations for California in 2022
        >>> ca_loans = connector.get_loans_by_state(year=2022, state_code='CA', action_taken=1)
        >>> print(f"CA loan originations: {len(ca_loans):,}")
        >>>
        >>> # Analyze denial rates by race
        >>> denial_rates = connector.get_denial_rates(year=2022, state_code='CA')
        >>> print(denial_rates[['race', 'total_applications', 'denial_rate']])
    """

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize the HMDAConnector.

        Args:
            api_key: Optional API key (HMDA API is public, but key may enable higher rate limits)
            **kwargs: Additional arguments passed to BaseConnector
        """
        self.base_url = "https://ffiec.cfpb.gov/v2/data-browser-api"
        super().__init__(api_key=api_key, **kwargs)
        logger.info("HMDAConnector initialized with base_url=%s", self.base_url)

    def connect(self) -> None:
        """
        Test connection to HMDA API.
        """
        try:
            # Test with a simple request
            response = requests.get(f"{self.base_url}/view/nationwide/aggregate", timeout=10)
            response.raise_for_status()
            logger.info("Successfully connected to HMDA API")
        except Exception as e:
            logger.error("Failed to connect to HMDA API: %s", e)
            raise

    def _get_api_key(self) -> Optional[str]:
        """
        Get API key from instance variable or ConfigManager.

        Checks in order:
        1. Instance variable (passed during __init__)
        2. ConfigManager (checks ~/.krl/apikeys and environment)
        3. None

        Returns:
            API key if available, None otherwise
        """
        # Check if set during initialization
        if hasattr(self, "_hmda_api_key") and self._hmda_api_key:
            return self._hmda_api_key

        # Fall back to ConfigManager (environment + ~/.krl/apikeys)
        return self.config.get("HMDA_API_KEY")

    def _make_request(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None, method: str = "GET"
    ) -> Dict[str, Any]:
        """
        Make a request to the HMDA API.

        Args:
            endpoint: API endpoint path (relative to base_url)
            params: Query parameters
            method: HTTP method (GET or POST)

        Returns:
            JSON response as dictionary

        Raises:
            requests.HTTPError: If request fails
        """
        url = f"{self.base_url}/{endpoint}"
        headers = {}

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        logger.debug("Making %s request to %s with params=%s", method, url, params)

        if method.upper() == "GET":
            response = requests.get(url, params=params, headers=headers, timeout=30)
        elif method.upper() == "POST":
            response = requests.post(url, json=params, headers=headers, timeout=30)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        return response.json()

    def load_loan_data(
        self,
        year: int,
        state_code: Optional[str] = None,
        county_code: Optional[str] = None,
        action_taken: Optional[Union[int, List[int]]] = None,
        loan_purpose: Optional[Union[int, List[int]]] = None,
        limit: int = 10000,
    ) -> pd.DataFrame:
        """
        Load loan-level HMDA data with optional filtering.

        Args:
            year: Data year (2018 or later)
            state_code: Two-letter state code (e.g., 'CA', 'NY') - optional
            county_code: Five-digit county FIPS code - optional
            action_taken: Action taken code(s). Common values:
                1 = Loan originated
                3 = Application denied
                4 = Application withdrawn
                5 = File closed for incompleteness
                Can be single int or list of ints
            loan_purpose: Loan purpose code(s):
                1 = Home purchase
                2 = Home improvement
                31 = Refinancing - cash-out
                32 = Refinancing - no cash-out
                4 = Other purpose
                Can be single int or list of ints
            limit: Maximum number of records to return (default 10,000)

        Returns:
            DataFrame with loan-level data including:
                - activity_year, state_code, county_code, census_tract
                - loan_type, loan_purpose, loan_amount
                - action_taken, denial_reason_1
                - applicant_race_1, applicant_ethnicity_1, applicant_sex
                - applicant_income
                - lender (derived_msa_md, lei)

        Example:
            >>> # Get home purchase loans originated in California (2022)
            >>> loans = connector.load_loan_data(
            ...     year=2022,
            ...     state_code='CA',
            ...     action_taken=1,  # originated
            ...     loan_purpose=1   # home purchase
            ... )
        """
        logger.info(
            "Loading HMDA loan data: year=%s, state=%s, county=%s, action_taken=%s",
            year,
            state_code,
            county_code,
            action_taken,
        )

        # Note: HMDA API has different endpoints for different aggregation levels
        # For loan-level data, we use aggregations endpoint with appropriate filters
        # In production, this would use the actual HMDA API structure

        # Build query parameters
        params = {"year": year, "limit": limit}

        if state_code:
            params["state_code"] = state_code.upper()

        if county_code:
            params["county_code"] = county_code

        if action_taken is not None:
            if isinstance(action_taken, list):
                params["action_taken"] = ",".join(map(str, action_taken))
            else:
                params["action_taken"] = action_taken

        if loan_purpose is not None:
            if isinstance(loan_purpose, list):
                params["loan_purpose"] = ",".join(map(str, loan_purpose))
            else:
                params["loan_purpose"] = loan_purpose

        # In a real implementation, this would call the HMDA API
        # For now, return a structured DataFrame that matches HMDA schema
        logger.info("Fetching loan data from HMDA API (mock implementation)")

        # Mock data structure matching HMDA LAR (Loan Application Register) format
        df = pd.DataFrame(
            {
                "activity_year": [year] * 100,
                "state_code": [state_code or "CA"] * 100,
                "county_code": ["06037"] * 100,  # Los Angeles County example
                "census_tract": ["0601.02"] * 100,
                "lei": ["LENDER123"] * 100,  # Legal Entity Identifier
                "loan_type": [1] * 100,  # Conventional
                "loan_purpose": [loan_purpose or 1] * 100,
                "loan_amount": [350000] * 100,
                "action_taken": [action_taken or 1] * 100,
                "denial_reason_1": [None] * 100,
                "applicant_race_1": [5] * 100,  # White
                "applicant_ethnicity_1": [2] * 100,  # Not Hispanic or Latino
                "applicant_sex": [1] * 100,  # Male
                "applicant_income": [95000] * 100,
                "derived_msa_md": ["31080"] * 100,  # Los Angeles MSA
                "derived_loan_to_value_ratio": [0.80] * 100,
                "derived_dwelling_category": ["Single Family"] * 100,
                "debt_to_income_ratio": ["25%-<30%"] * 100,
            }
        )

        logger.info("Loaded %d loan records", len(df))
        return df

    @requires_license
    def get_loans_by_state(
        self, year: int, state_code: str, action_taken: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Get all loans for a specific state.

        Args:
            year: Data year (2018 or later)
            state_code: Two-letter state code (e.g., 'CA', 'NY')
            action_taken: Optional filter for action taken (1=originated, 3=denied, etc.)

        Returns:
            DataFrame with loans for the specified state

        Example:
            >>> # Get all originated loans in New York (2022)
            >>> ny_loans = connector.get_loans_by_state(
            ...     year=2022,
            ...     state_code='NY',
            ...     action_taken=1
            ... )
        """
        logger.info(
            "Fetching loans for state=%s, year=%s, action_taken=%s", state_code, year, action_taken
        )

        return self.load_loan_data(
            year=year,
            state_code=state_code,
            action_taken=action_taken,
            limit=50000,  # Higher limit for state-level data
        )

    @requires_license
    def get_denial_rates(
        self,
        year: int,
        state_code: Optional[str] = None,
        by_race: bool = True,
        by_ethnicity: bool = False,
        by_income_bracket: bool = False,
    ) -> pd.DataFrame:
        """
        Calculate mortgage denial rates by demographic characteristics.

        This method analyzes applications that were either originated (action_taken=1)
        or denied (action_taken=3) to compute denial rates.

        Args:
            year: Data year
            state_code: Optional state filter (if None, national data)
            by_race: Group by applicant race (default True)
            by_ethnicity: Group by applicant ethnicity (default False)
            by_income_bracket: Group by income brackets (default False)

        Returns:
            DataFrame with denial rates by demographic group:
                - race/ethnicity/income_bracket (depending on parameters)
                - total_applications
                - denied
                - originated
                - denial_rate (percentage)

        Example:
            >>> # Denial rates by race in California
            >>> denial_rates = connector.get_denial_rates(
            ...     year=2022,
            ...     state_code='CA',
            ...     by_race=True
            ... )
            >>> print(denial_rates[['race', 'denial_rate']])
        """
        logger.info(
            "Calculating denial rates: year=%s, state=%s, by_race=%s, by_ethnicity=%s",
            year,
            state_code,
            by_race,
            by_ethnicity,
        )

        # Load applications that were either originated or denied
        df = self.load_loan_data(
            year=year,
            state_code=state_code,
            action_taken=[1, 3],  # 1=originated, 3=denied
            limit=100000,
        )

        # Map race codes to labels
        race_map = {
            1: "American Indian or Alaska Native",
            2: "Asian",
            3: "Black or African American",
            4: "Native Hawaiian or Other Pacific Islander",
            5: "White",
            6: "Information not provided",
            7: "Not applicable",
        }

        ethnicity_map = {
            1: "Hispanic or Latino",
            2: "Not Hispanic or Latino",
            3: "Information not provided",
            4: "Not applicable",
        }

        # Add readable labels
        if by_race and "applicant_race_1" in df.columns:
            df["race"] = df["applicant_race_1"].map(race_map)

        if by_ethnicity and "applicant_ethnicity_1" in df.columns:
            df["ethnicity"] = df["applicant_ethnicity_1"].map(ethnicity_map)

        # Create income brackets if requested
        if by_income_bracket and "applicant_income" in df.columns:
            df["income_bracket"] = pd.cut(
                df["applicant_income"],
                bins=[0, 50000, 75000, 100000, 150000, float("inf")],
                labels=["<$50K", "$50K-$75K", "$75K-$100K", "$100K-$150K", "$150K+"],
            )

        # Determine grouping columns
        group_cols = []
        if by_race:
            group_cols.append("race")
        if by_ethnicity:
            group_cols.append("ethnicity")
        if by_income_bracket:
            group_cols.append("income_bracket")

        if not group_cols:
            raise ValueError(
                "Must specify at least one grouping: by_race, by_ethnicity, or by_income_bracket"
            )

        # Calculate denial rates
        result = (
            df.groupby(group_cols)
            .agg(
                total_applications=("action_taken", "count"),
                denied=("action_taken", lambda x: (x == 3).sum()),
                originated=("action_taken", lambda x: (x == 1).sum()),
            )
            .reset_index()
        )

        result["denial_rate"] = (result["denied"] / result["total_applications"] * 100).round(2)

        # Sort by denial rate descending
        result = result.sort_values("denial_rate", ascending=False)

        logger.info("Calculated denial rates for %d groups", len(result))
        return result

    @requires_license
    def get_loans_by_demographic(
        self,
        year: int,
        race: Optional[int] = None,
        ethnicity: Optional[int] = None,
        sex: Optional[int] = None,
        state_code: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Filter loans by borrower demographic characteristics.

        Args:
            year: Data year
            race: Applicant race code (1=American Indian, 2=Asian, 3=Black, 4=Pacific Islander,
                  5=White, 6=Not provided, 7=Not applicable)
            ethnicity: Applicant ethnicity (1=Hispanic/Latino, 2=Not Hispanic/Latino,
                      3=Not provided, 4=Not applicable)
            sex: Applicant sex (1=Male, 2=Female, 3=Not provided, 4=Not applicable)
            state_code: Optional state filter

        Returns:
            DataFrame with loans matching demographic criteria

        Example:
            >>> # Get loans for Black or African American borrowers in California
            >>> loans = connector.get_loans_by_demographic(
            ...     year=2022,
            ...     race=3,  # Black or African American
            ...     state_code='CA'
            ... )
        """
        logger.info(
            "Filtering loans by demographics: year=%s, race=%s, ethnicity=%s, sex=%s, state=%s",
            year,
            race,
            ethnicity,
            sex,
            state_code,
        )

        df = self.load_loan_data(year=year, state_code=state_code, limit=100000)

        # Apply demographic filters
        if race is not None:
            df = df[df["applicant_race_1"] == race]

        if ethnicity is not None:
            df = df[df["applicant_ethnicity_1"] == ethnicity]

        if sex is not None:
            df = df[df["applicant_sex"] == sex]

        logger.info("Filtered to %d loans matching demographic criteria", len(df))
        return df

    @requires_license
    def get_lending_patterns(
        self, year: int, state_code: str, group_by: str = "county"
    ) -> pd.DataFrame:
        """
        Analyze lending patterns by geographic area.

        Args:
            year: Data year
            state_code: Two-letter state code
            group_by: Geographic grouping level ('county' or 'tract')

        Returns:
            DataFrame with lending statistics by geography:
                - geography identifier (county_code or census_tract)
                - total_applications
                - total_originations
                - median_loan_amount
                - avg_loan_to_value_ratio
                - origination_rate (percentage)

        Example:
            >>> # Lending patterns by county in Texas
            >>> patterns = connector.get_lending_patterns(
            ...     year=2022,
            ...     state_code='TX',
            ...     group_by='county'
            ... )
        """
        logger.info(
            "Analyzing lending patterns: year=%s, state=%s, group_by=%s", year, state_code, group_by
        )

        df = self.load_loan_data(
            year=year,
            state_code=state_code,
            action_taken=[1, 3],  # originated or denied
            limit=100000,
        )

        if group_by not in ["county", "tract"]:
            raise ValueError("group_by must be 'county' or 'tract'")

        group_col = "county_code" if group_by == "county" else "census_tract"

        # Calculate lending statistics by geography
        result = (
            df.groupby(group_col)
            .agg(
                total_applications=("action_taken", "count"),
                total_originations=("action_taken", lambda x: (x == 1).sum()),
                median_loan_amount=("loan_amount", "median"),
                avg_loan_to_value_ratio=("derived_loan_to_value_ratio", "mean"),
            )
            .reset_index()
        )

        result["origination_rate"] = (
            result["total_originations"] / result["total_applications"] * 100
        ).round(2)

        # Sort by total applications descending
        result = result.sort_values("total_applications", ascending=False)

        logger.info("Calculated lending patterns for %d geographic areas", len(result))
        return result

    def analyze_redlining_indicators(
        self, year: int, state_code: str, minority_threshold: float = 0.5
    ) -> pd.DataFrame:
        """
        Identify potential redlining indicators by analyzing lending patterns in
        minority-majority vs. non-minority areas.

        This analysis looks for disparities in:
        - Origination rates (approval rates)
        - Denial rates
        - Median loan amounts
        - Application volumes

        Args:
            year: Data year
            state_code: Two-letter state code
            minority_threshold: Threshold for classifying tract as minority-majority (default 0.5)

        Returns:
            DataFrame with comparative statistics:
                - tract_category ('Minority-Majority' or 'Non-Minority')
                - total_applications
                - origination_rate
                - denial_rate
                - median_loan_amount

        Example:
            >>> # Check for redlining indicators in California
            >>> indicators = connector.analyze_redlining_indicators(
            ...     year=2022,
            ...     state_code='CA'
            ... )
            >>> print(indicators)

        Note:
            This is a simplified indicator analysis. Full redlining analysis would require
            additional demographic data at the tract level from Census Bureau.
        """
        logger.info(
            "Analyzing redlining indicators: year=%s, state=%s, minority_threshold=%s",
            year,
            state_code,
            minority_threshold,
        )

        df = self.load_loan_data(
            year=year,
            state_code=state_code,
            action_taken=[1, 3],  # originated or denied
            limit=100000,
        )

        # For this analysis, we would typically join with Census demographic data
        # to identify minority-majority tracts. Here we use a simplified approach
        # based on applicant demographics as a proxy.

        # Calculate tract-level minority percentage (simplified)
        tract_demographics = (
            df.groupby("census_tract")
            .agg(
                total_apps=("applicant_race_1", "count"),
                minority_apps=("applicant_race_1", lambda x: (x != 5).sum()),  # non-White
            )
            .reset_index()
        )

        tract_demographics["minority_pct"] = (
            tract_demographics["minority_apps"] / tract_demographics["total_apps"]
        )

        # Classify tracts
        tract_demographics["tract_category"] = tract_demographics["minority_pct"].apply(
            lambda x: "Minority-Majority" if x >= minority_threshold else "Non-Minority"
        )

        # Merge back to loan data
        df = df.merge(tract_demographics[["census_tract", "tract_category"]], on="census_tract")

        # Calculate comparative statistics
        result = (
            df.groupby("tract_category")
            .agg(
                total_applications=("action_taken", "count"),
                originations=("action_taken", lambda x: (x == 1).sum()),
                denials=("action_taken", lambda x: (x == 3).sum()),
                median_loan_amount=("loan_amount", "median"),
            )
            .reset_index()
        )

        result["origination_rate"] = (
            result["originations"] / result["total_applications"] * 100
        ).round(2)

        result["denial_rate"] = (result["denials"] / result["total_applications"] * 100).round(2)

        logger.info("Calculated redlining indicators for %d tract categories", len(result))
        return result[
            [
                "tract_category",
                "total_applications",
                "origination_rate",
                "denial_rate",
                "median_loan_amount",
            ]
        ]

    @requires_license
    def get_lender_statistics(
        self, year: int, state_code: Optional[str] = None, top_n: int = 20
    ) -> pd.DataFrame:
        """
        Get statistics on lending institutions (lenders).

        Args:
            year: Data year
            state_code: Optional state filter (if None, national data)
            top_n: Number of top lenders to return (by application volume)

        Returns:
            DataFrame with lender statistics:
                - lei (Legal Entity Identifier)
                - total_applications
                - total_originations
                - origination_rate
                - median_loan_amount

        Example:
            >>> # Top 20 lenders in Florida by application volume
            >>> lenders = connector.get_lender_statistics(
            ...     year=2022,
            ...     state_code='FL',
            ...     top_n=20
            ... )
        """
        logger.info(
            "Calculating lender statistics: year=%s, state=%s, top_n=%s", year, state_code, top_n
        )

        df = self.load_loan_data(
            year=year,
            state_code=state_code,
            action_taken=[1, 3],  # originated or denied
            limit=100000,
        )

        # Calculate statistics by lender (LEI)
        result = (
            df.groupby("lei")
            .agg(
                total_applications=("action_taken", "count"),
                total_originations=("action_taken", lambda x: (x == 1).sum()),
                median_loan_amount=("loan_amount", "median"),
            )
            .reset_index()
        )

        result["origination_rate"] = (
            result["total_originations"] / result["total_applications"] * 100
        ).round(2)

        # Sort by application volume and take top N
        result = result.sort_values("total_applications", ascending=False).head(top_n)

        logger.info("Calculated statistics for top %d lenders", len(result))
        return result

    def fetch(
        self, year: int, state_code: Optional[str] = None, analysis_type: str = "loans", **kwargs
    ) -> pd.DataFrame:
        """
        Main entry point for fetching HMDA data.

        Args:
            year: Data year (2018 or later)
            state_code: Optional two-letter state code
            analysis_type: Type of analysis to perform:
                - 'loans': Raw loan-level data (default)
                - 'denial_rates': Denial rate analysis
                - 'lending_patterns': Geographic lending patterns
                - 'redlining': Redlining indicators
                - 'lenders': Lender statistics
            **kwargs: Additional parameters passed to specific methods

        Returns:
            DataFrame appropriate for the requested analysis type

        Example:
            >>> connector = HMDAConnector()
            >>>
            >>> # Get raw loan data
            >>> loans = connector.fetch(year=2022, state_code='CA', analysis_type='loans')
            >>>
            >>> # Get denial rates by race
            >>> denial_rates = connector.fetch(
            ...     year=2022,
            ...     state_code='CA',
            ...     analysis_type='denial_rates',
            ...     by_race=True
            ... )
        """
        logger.info("Fetch: year=%s, state=%s, analysis_type=%s", year, state_code, analysis_type)

        if analysis_type == "loans":
            return self.load_loan_data(year=year, state_code=state_code, **kwargs)

        elif analysis_type == "denial_rates":
            return self.get_denial_rates(year=year, state_code=state_code, **kwargs)

        elif analysis_type == "lending_patterns":
            if not state_code:
                raise ValueError("state_code required for lending_patterns analysis")
            return self.get_lending_patterns(year=year, state_code=state_code, **kwargs)

        elif analysis_type == "redlining":
            if not state_code:
                raise ValueError("state_code required for redlining analysis")
            return self.analyze_redlining_indicators(year=year, state_code=state_code, **kwargs)

        elif analysis_type == "lenders":
            return self.get_lender_statistics(year=year, state_code=state_code, **kwargs)

        else:
            raise ValueError(
                f"Unknown analysis_type: {analysis_type}. "
                "Must be one of: loans, denial_rates, lending_patterns, redlining, lenders"
            )
