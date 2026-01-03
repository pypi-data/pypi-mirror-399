# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Data.gov Transit Domain Connector - Professional Tier

Full access to public transit datasets.
Pre-configured for FTA, DOT, BTS.
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from krl_data_connectors.professional.civic.datagov_full import DataGovFullConnector
from krl_data_connectors.licensed_connector_mixin import requires_license


class DataGovTransitFullConnector(DataGovFullConnector):
    """
    Data.gov Transit Domain Connector - Professional Tier
    """

    _connector_name = "DataGov_Transit_Full"
    DEFAULT_DOWNLOAD_DIR = "~/.krl/data/datagov_transit"

    DOMAIN_ORGANIZATIONS: List[str] = [
        "fta-dot-gov",        # Federal Transit Administration
        "dot-gov",            # Department of Transportation
        "bts-dot-gov",        # Bureau of Transportation Statistics
    ]
    
    DOMAIN_TAGS: List[str] = [
        "transit",
        "public-transit",
        "bus",
        "rail",
        "ridership",
    ]
    
    DOMAIN_NAME: str = "Transit"

    POPULAR_DATASETS: Dict[str, List[str]] = {
        "ntd": [
            "national-transit-database",
            "transit-statistics",
            "ridership-data",
        ],
        "agencies": [
            "transit-agencies",
            "service-data",
            "routes",
        ],
        "infrastructure": [
            "stations",
            "fleet-data",
            "capital-projects",
        ],
    }

    @requires_license
    def search_ntd_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for National Transit Database datasets."""
        search_query = f"NTD {query}" if query != "*:*" else "national transit database NTD"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_ridership_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for ridership datasets."""
        search_query = f"ridership {query}" if query != "*:*" else "transit ridership passengers"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_bus_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for bus transit datasets."""
        search_query = f"bus {query}" if query != "*:*" else "bus transit public"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_rail_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for rail transit datasets."""
        search_query = f"rail {query}" if query != "*:*" else "rail transit subway metro"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_transit_agencies(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for transit agency datasets."""
        search_query = f"transit agency {query}" if query != "*:*" else "transit agency service"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def bulk_export_transit_data(
        self,
        topic: str = "ntd",
        limit: int = 1000,
        output_format: str = "parquet",
    ) -> str:
        """Bulk export transit datasets."""
        return self.bulk_export_domain_data(
            topic=topic,
            limit=limit,
            output_format=output_format,
        )

    def __repr__(self) -> str:
        return (
            f"DataGovTransitFullConnector("
            f"domain='{self.DOMAIN_NAME}', "
            f"organizations={self.DOMAIN_ORGANIZATIONS})"
        )
