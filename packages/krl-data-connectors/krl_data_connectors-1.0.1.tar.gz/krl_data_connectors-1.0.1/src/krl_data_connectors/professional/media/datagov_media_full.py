# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Data.gov Media Domain Connector - Professional Tier

Full access to media and telecommunications datasets.
Pre-configured for FCC, NTIA.
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from krl_data_connectors.professional.civic.datagov_full import DataGovFullConnector
from krl_data_connectors.licensed_connector_mixin import requires_license


class DataGovMediaFullConnector(DataGovFullConnector):
    """
    Data.gov Media Domain Connector - Professional Tier
    """

    _connector_name = "DataGov_Media_Full"
    DEFAULT_DOWNLOAD_DIR = "~/.krl/data/datagov_media"

    DOMAIN_ORGANIZATIONS: List[str] = [
        "fcc-gov",          # Federal Communications Commission
        "ntia-gov",         # National Telecommunications and Information Admin
    ]
    
    DOMAIN_TAGS: List[str] = [
        "media",
        "broadcasting",
        "telecommunications",
        "press",
    ]
    
    DOMAIN_NAME: str = "Media"

    POPULAR_DATASETS: Dict[str, List[str]] = {
        "broadcasting": [
            "broadcast-licenses",
            "radio-stations",
            "television-stations",
        ],
        "ownership": [
            "media-ownership",
            "station-ownership",
        ],
    }

    @requires_license
    def search_fcc_media(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for FCC media datasets."""
        search_query = f"media broadcasting {query}" if query != "*:*" else "broadcast license television radio"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_media_ownership(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for media ownership datasets."""
        search_query = f"media ownership {query}" if query != "*:*" else "media ownership broadcast"
        return self.search_datasets(query=search_query, rows=rows)

    def __repr__(self) -> str:
        return (
            f"DataGovMediaFullConnector("
            f"domain='{self.DOMAIN_NAME}', "
            f"organizations={self.DOMAIN_ORGANIZATIONS})"
        )
