# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Data.gov Transportation Domain Connector - Professional Tier

Full access to transportation datasets.
Pre-configured for DOT, FAA, FHWA, NHTSA.
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from krl_data_connectors.professional.civic.datagov_full import DataGovFullConnector
from krl_data_connectors.licensed_connector_mixin import requires_license


class DataGovTransportationFullConnector(DataGovFullConnector):
    """
    Data.gov Transportation Domain Connector - Professional Tier
    """

    _connector_name = "DataGov_Transportation_Full"
    DEFAULT_DOWNLOAD_DIR = "~/.krl/data/datagov_transportation"

    DOMAIN_ORGANIZATIONS: List[str] = [
        "dot-gov",            # Department of Transportation
        "faa-gov",            # Federal Aviation Administration
        "fhwa-dot-gov",       # Federal Highway Administration
        "nhtsa-dot-gov",      # National Highway Traffic Safety Administration
        "fra-dot-gov",        # Federal Railroad Administration
        "bts-dot-gov",        # Bureau of Transportation Statistics
    ]
    
    DOMAIN_TAGS: List[str] = [
        "transportation",
        "aviation",
        "highway",
        "safety",
        "infrastructure",
    ]
    
    DOMAIN_NAME: str = "Transportation"

    POPULAR_DATASETS: Dict[str, List[str]] = {
        "aviation": [
            "aviation-data",
            "airports",
            "flight-data",
        ],
        "highway": [
            "highway-statistics",
            "traffic-data",
            "road-conditions",
        ],
        "safety": [
            "fatality-data",
            "crash-data",
            "recalls",
        ],
        "freight": [
            "freight-data",
            "commodity-flow",
            "trucking",
        ],
    }

    @requires_license
    def search_faa_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for FAA aviation datasets."""
        search_query = f"FAA {query}" if query != "*:*" else "FAA aviation airports"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_highway_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for highway datasets."""
        search_query = f"highway {query}" if query != "*:*" else "highway traffic roads"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_safety_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for transportation safety datasets."""
        search_query = f"safety {query}" if query != "*:*" else "transportation safety NHTSA"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_crash_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for crash and fatality datasets."""
        search_query = f"crash {query}" if query != "*:*" else "crash fatality accidents"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_freight_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for freight datasets."""
        search_query = f"freight {query}" if query != "*:*" else "freight trucking commodity"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_railroad_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for railroad datasets."""
        search_query = f"railroad {query}" if query != "*:*" else "railroad rail freight"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def bulk_export_transportation_data(
        self,
        topic: str = "highway",
        limit: int = 1000,
        output_format: str = "parquet",
    ) -> str:
        """Bulk export transportation datasets."""
        return self.bulk_export_domain_data(
            topic=topic,
            limit=limit,
            output_format=output_format,
        )

    def __repr__(self) -> str:
        return (
            f"DataGovTransportationFullConnector("
            f"domain='{self.DOMAIN_NAME}', "
            f"organizations={self.DOMAIN_ORGANIZATIONS})"
        )
