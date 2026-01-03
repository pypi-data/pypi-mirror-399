# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Data.gov Demographic Domain Connector - Professional Tier

Full access to demographic datasets with unlimited search, bulk export.
Pre-configured for Census, SSA, DHS agencies.
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from krl_data_connectors.professional.civic.datagov_full import DataGovFullConnector
from krl_data_connectors.licensed_connector_mixin import requires_license


class DataGovDemographicFullConnector(DataGovFullConnector):
    """
    Data.gov Demographic Domain Connector - Professional Tier
    """

    _connector_name = "DataGov_Demographic_Full"
    DEFAULT_DOWNLOAD_DIR = "~/.krl/data/datagov_demographic"

    DOMAIN_ORGANIZATIONS: List[str] = [
        "census-gov",       # Census Bureau
        "ssa-gov",          # Social Security Administration
        "dhs-gov",          # Department of Homeland Security
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

    POPULAR_DATASETS: Dict[str, List[str]] = {
        "population": [
            "american-community-survey",
            "population-estimates",
            "decennial-census",
            "population-projections",
        ],
        "age_gender": [
            "age-sex-composition",
            "population-by-age",
            "median-age",
        ],
        "race_ethnicity": [
            "race-ethnicity",
            "hispanic-origin",
            "diversity-index",
        ],
        "migration": [
            "geographic-mobility",
            "state-to-state-migration",
            "immigration-statistics",
        ],
    }

    @requires_license
    def search_census_datasets(
        self,
        query: str,
        formats: Optional[List[str]] = None,
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search Census Bureau datasets specifically."""
        return self.search_datasets(
            query=query,
            organization="census-gov",
            formats=formats,
            rows=rows,
        )

    @requires_license
    def search_population_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for population datasets."""
        search_query = f"population {query}" if query != "*:*" else "population estimates census"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_migration_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for migration datasets."""
        search_query = f"migration {query}" if query != "*:*" else "migration mobility flow"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_race_ethnicity_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for race/ethnicity datasets."""
        search_query = f"race ethnicity {query}" if query != "*:*" else "race ethnicity demographics"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def bulk_export_census_data(
        self,
        query: str = "*:*",
        max_datasets: int = 1000,
    ) -> pd.DataFrame:
        """Bulk export Census datasets."""
        return self.bulk_export(
            query=query,
            organization="census-gov",
            max_datasets=max_datasets,
        )

    def __repr__(self) -> str:
        return (
            f"DataGovDemographicFullConnector("
            f"domain='{self.DOMAIN_NAME}', "
            f"organizations={self.DOMAIN_ORGANIZATIONS})"
        )
