# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Data.gov Cultural Domain Connector - Professional Tier

Full access to cultural datasets from Data.gov with unlimited search.
Pre-configured for NEA, NEH, IMLS, Smithsonian.
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from krl_data_connectors.professional.civic.datagov_full import DataGovFullConnector
from krl_data_connectors.licensed_connector_mixin import requires_license


class DataGovCulturalFullConnector(DataGovFullConnector):
    """
    Data.gov Cultural Domain Connector - Professional Tier
    """

    _connector_name = "DataGov_Cultural_Full"
    DEFAULT_DOWNLOAD_DIR = "~/.krl/data/datagov_cultural"

    DOMAIN_ORGANIZATIONS: List[str] = [
        "nea-gov",          # National Endowment for the Arts
        "neh-gov",          # National Endowment for the Humanities
        "imls-gov",         # Institute of Museum and Library Services
        "si-edu",           # Smithsonian Institution
        "loc-gov",          # Library of Congress
    ]
    
    DOMAIN_TAGS: List[str] = [
        "culture",
        "arts",
        "museums",
        "libraries",
        "heritage",
        "humanities",
    ]
    
    DOMAIN_NAME: str = "Cultural"

    POPULAR_DATASETS: Dict[str, List[str]] = {
        "arts": [
            "nea-grants",
            "arts-participation",
            "arts-education",
            "public-art",
        ],
        "museums": [
            "museum-data",
            "smithsonian-collections",
            "museum-statistics",
        ],
        "libraries": [
            "public-library-survey",
            "library-statistics",
            "imls-grants",
        ],
        "heritage": [
            "historic-preservation",
            "cultural-heritage",
            "national-register",
        ],
    }

    @requires_license
    def search_arts_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for arts datasets."""
        search_query = f"arts {query}" if query != "*:*" else "arts grants NEA"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_museum_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for museum datasets."""
        search_query = f"museum {query}" if query != "*:*" else "museum collections statistics"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_library_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for library datasets."""
        search_query = f"library {query}" if query != "*:*" else "public library statistics"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_heritage_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for heritage preservation datasets."""
        search_query = f"heritage {query}" if query != "*:*" else "historic preservation heritage"
        return self.search_datasets(query=search_query, rows=rows)

    def __repr__(self) -> str:
        return (
            f"DataGovCulturalFullConnector("
            f"domain='{self.DOMAIN_NAME}', "
            f"organizations={self.DOMAIN_ORGANIZATIONS})"
        )
