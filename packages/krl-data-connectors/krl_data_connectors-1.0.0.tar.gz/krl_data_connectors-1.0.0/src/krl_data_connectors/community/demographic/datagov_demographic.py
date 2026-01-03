# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Data.gov Demographic Domain Connector - Community Tier

Pre-configured access to demographic datasets from Data.gov, filtered to
Census Bureau, Social Security Administration, and population-related agencies.
Provides datasets on population, age, race, ethnicity, migration, and more.

Domain Organizations:
- Census Bureau (census-gov): ACS, decennial census, population estimates
- SSA (ssa-gov): Social Security, actuarial data
- DHS (dhs-gov): Immigration, citizenship statistics

Key Dataset Categories:
- Population: Estimates, projections, density
- Age/Gender: Age distribution, gender demographics
- Race/Ethnicity: Racial and ethnic composition
- Migration: Geographic mobility, immigration
- Households: Family structure, housing characteristics

Usage:
    from krl_data_connectors.community.demographic import DataGovDemographicConnector
    
    demo = DataGovDemographicConnector()
    
    # Search demographic datasets (auto-filtered to Census/SSA)
    results = demo.search_datasets("population estimates")
    
    # Use agency-specific convenience methods
    census_data = demo.search_census_datasets("age distribution")
    migration = demo.search_migration_data("state to state")
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from krl_data_connectors.community.civic.datagov_catalog import DataGovCatalogConnector


class DataGovDemographicConnector(DataGovCatalogConnector):
    """
    Data.gov Demographic Domain Connector - Community Tier

    Pre-configured for Census Bureau, SSA, and demographic agency datasets.
    All searches are automatically filtered to demographic organizations
    unless overridden with a specific organization parameter.

    Limitations (Community Tier):
    - Maximum 50 results per search query
    - No bulk export functionality
    - Upgrade to DataGovDemographicFullConnector for unlimited access
    """

    _connector_name = "DataGov_Demographic"

    # Domain configuration - auto-filter searches to these organizations
    DOMAIN_ORGANIZATIONS: List[str] = [
        "census-gov",   # Census Bureau
        "ssa-gov",      # Social Security Administration
        "dhs-gov",      # Department of Homeland Security
    ]
    
    DOMAIN_TAGS: List[str] = [
        "demographics",
        "population",
        "census",
        "age",
        "race",
        "ethnicity",
        "migration",
    ]
    
    DOMAIN_NAME: str = "Demographic"

    # Override popular datasets with demographic focus
    POPULAR_DATASETS: Dict[str, List[str]] = {
        "population": [
            "american-community-survey",
            "population-estimates-program",
            "decennial-census",
            "population-projections",
            "county-population-totals",
        ],
        "age_gender": [
            "age-and-sex-composition",
            "population-by-age",
            "gender-demographics",
            "median-age-by-county",
            "senior-population",
        ],
        "race_ethnicity": [
            "race-and-ethnicity",
            "hispanic-origin",
            "diversity-index",
            "ancestry-data",
            "race-by-county",
        ],
        "migration": [
            "geographic-mobility",
            "state-to-state-migration",
            "county-to-county-flow",
            "foreign-born-population",
            "immigration-statistics",
        ],
        "households": [
            "household-composition",
            "family-type",
            "living-arrangements",
            "group-quarters",
            "household-size",
        ],
    }

    # Demographic organizations with descriptions
    WHITELISTED_ORGANIZATIONS: Dict[str, str] = {
        "census-gov": "U.S. Census Bureau",
        "ssa-gov": "Social Security Administration",
        "dhs-gov": "Department of Homeland Security",
        "cdc-gov": "Centers for Disease Control and Prevention",
        "hhs-gov": "Department of Health and Human Services",
    }

    def search_census_datasets(
        self,
        query: str,
        formats: Optional[List[str]] = None,
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search Census Bureau datasets specifically.

        Args:
            query: Search query string
            formats: Filter by resource format (e.g., ['CSV', 'JSON'])
            rows: Number of results (max 50 for Community tier)

        Returns:
            DataFrame with Census dataset metadata

        Example:
            >>> demo = DataGovDemographicConnector()
            >>> acs = demo.search_census_datasets("american community survey")
        """
        return self.search_datasets(
            query=query,
            organization="census-gov",
            formats=formats,
            rows=rows,
        )

    def search_population_data(
        self,
        query: str = "*:*",
        state: Optional[str] = None,
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search for population datasets.

        Args:
            query: Search query (default: all population datasets)
            state: Optional state filter
            rows: Number of results

        Returns:
            DataFrame with population dataset metadata
        """
        search_query = f"population {query}" if query != "*:*" else "population estimates"
        if state:
            search_query = f"{search_query} {state}"
        
        return self.search_datasets(
            query=search_query,
            rows=rows,
        )

    def search_migration_data(
        self,
        query: str = "*:*",
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search for migration and mobility datasets.

        Args:
            query: Search query (default: all migration datasets)
            rows: Number of results

        Returns:
            DataFrame with migration dataset metadata
        """
        search_query = f"migration mobility {query}" if query != "*:*" else "migration geographic mobility"
        
        return self.search_datasets(
            query=search_query,
            rows=rows,
        )

    def search_race_ethnicity_data(
        self,
        query: str = "*:*",
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search for race and ethnicity datasets.

        Args:
            query: Search query (default: all race/ethnicity datasets)
            rows: Number of results

        Returns:
            DataFrame with race/ethnicity dataset metadata
        """
        search_query = f"race ethnicity {query}" if query != "*:*" else "race ethnicity demographics"
        
        return self.search_datasets(
            query=search_query,
            rows=rows,
        )

    def search_age_distribution_data(
        self,
        query: str = "*:*",
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search for age distribution datasets.

        Args:
            query: Search query (default: all age datasets)
            rows: Number of results

        Returns:
            DataFrame with age distribution dataset metadata
        """
        search_query = f"age distribution {query}" if query != "*:*" else "age distribution population"
        
        return self.search_datasets(
            query=search_query,
            rows=rows,
        )

    def search_household_data(
        self,
        query: str = "*:*",
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search for household and family datasets.

        Args:
            query: Search query (default: all household datasets)
            rows: Number of results

        Returns:
            DataFrame with household dataset metadata
        """
        search_query = f"household family {query}" if query != "*:*" else "household family composition"
        
        return self.search_datasets(
            query=search_query,
            rows=rows,
        )

    def get_demographic_categories(self) -> List[str]:
        """Get available demographic dataset categories."""
        return list(self.POPULAR_DATASETS.keys())

    def __repr__(self) -> str:
        return (
            f"DataGovDemographicConnector("
            f"domain='{self.DOMAIN_NAME}', "
            f"organizations={self.DOMAIN_ORGANIZATIONS}, "
            f"max_results={self.MAX_RESULTS})"
        )
