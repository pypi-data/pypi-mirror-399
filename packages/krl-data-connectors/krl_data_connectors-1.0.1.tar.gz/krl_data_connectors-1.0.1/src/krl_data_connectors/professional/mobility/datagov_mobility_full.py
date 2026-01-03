# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Data.gov Mobility Domain Connector - Professional Tier

Full access to mobility and migration datasets.
Pre-configured for Census, DOT, BTS.
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from krl_data_connectors.professional.civic.datagov_full import DataGovFullConnector
from krl_data_connectors.licensed_connector_mixin import requires_license


class DataGovMobilityFullConnector(DataGovFullConnector):
    """
    Data.gov Mobility Domain Connector - Professional Tier
    """

    _connector_name = "DataGov_Mobility_Full"
    DEFAULT_DOWNLOAD_DIR = "~/.krl/data/datagov_mobility"

    DOMAIN_ORGANIZATIONS: List[str] = [
        "census-gov",       # Census Bureau
        "dot-gov",          # Department of Transportation
        "bts-gov",          # Bureau of Transportation Statistics
    ]
    
    DOMAIN_TAGS: List[str] = [
        "mobility",
        "migration",
        "commuting",
        "travel",
    ]
    
    DOMAIN_NAME: str = "Mobility"

    POPULAR_DATASETS: Dict[str, List[str]] = {
        "migration": [
            "migration-flows",
            "state-to-state-migration",
            "county-migration",
        ],
        "commuting": [
            "commuting-patterns",
            "lehd-origin-destination",
            "commute-times",
        ],
        "travel": [
            "travel-survey",
            "vehicle-miles-traveled",
            "trip-data",
        ],
    }

    @requires_license
    def search_migration_flows(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for migration flow datasets."""
        search_query = f"migration {query}" if query != "*:*" else "migration flow state county"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_commuting_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for commuting datasets."""
        search_query = f"commuting {query}" if query != "*:*" else "commuting patterns origin destination"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_travel_patterns(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for travel pattern datasets."""
        search_query = f"travel {query}" if query != "*:*" else "travel survey vehicle miles"
        return self.search_datasets(query=search_query, rows=rows)

    def __repr__(self) -> str:
        return (
            f"DataGovMobilityFullConnector("
            f"domain='{self.DOMAIN_NAME}', "
            f"organizations={self.DOMAIN_ORGANIZATIONS})"
        )
