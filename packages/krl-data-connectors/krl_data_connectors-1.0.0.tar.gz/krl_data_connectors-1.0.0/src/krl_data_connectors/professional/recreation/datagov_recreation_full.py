# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Data.gov Recreation Domain Connector - Professional Tier

Full access to recreation and parks datasets.
Pre-configured for NPS, Forest Service, BLM.
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from krl_data_connectors.professional.civic.datagov_full import DataGovFullConnector
from krl_data_connectors.licensed_connector_mixin import requires_license


class DataGovRecreationFullConnector(DataGovFullConnector):
    """
    Data.gov Recreation Domain Connector - Professional Tier
    """

    _connector_name = "DataGov_Recreation_Full"
    DEFAULT_DOWNLOAD_DIR = "~/.krl/data/datagov_recreation"

    DOMAIN_ORGANIZATIONS: List[str] = [
        "nps-gov",            # National Park Service
        "fs-usda-gov",        # Forest Service
        "blm-gov",            # Bureau of Land Management
        "fws-gov",            # Fish and Wildlife Service
        "doi-gov",            # Department of the Interior
    ]
    
    DOMAIN_TAGS: List[str] = [
        "recreation",
        "parks",
        "forests",
        "outdoors",
        "camping",
        "trails",
    ]
    
    DOMAIN_NAME: str = "Recreation"

    POPULAR_DATASETS: Dict[str, List[str]] = {
        "national_parks": [
            "park-visitation",
            "park-boundaries",
            "park-facilities",
        ],
        "forests": [
            "national-forest-boundaries",
            "recreation-sites",
            "trails",
        ],
        "public_lands": [
            "blm-recreation",
            "wilderness-areas",
            "campgrounds",
        ],
    }

    @requires_license
    def search_nps_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for National Park Service datasets."""
        search_query = f"national park {query}" if query != "*:*" else "national park visitation"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_forest_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for national forest datasets."""
        search_query = f"national forest {query}" if query != "*:*" else "national forest recreation"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_trails_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for trails and hiking datasets."""
        search_query = f"trails {query}" if query != "*:*" else "hiking trails recreation"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_camping_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for camping and campground datasets."""
        search_query = f"camping {query}" if query != "*:*" else "campgrounds recreation sites"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_public_lands_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for public lands datasets."""
        search_query = f"public lands {query}" if query != "*:*" else "public lands BLM recreation"
        return self.search_datasets(query=search_query, rows=rows)

    def __repr__(self) -> str:
        return (
            f"DataGovRecreationFullConnector("
            f"domain='{self.DOMAIN_NAME}', "
            f"organizations={self.DOMAIN_ORGANIZATIONS})"
        )
