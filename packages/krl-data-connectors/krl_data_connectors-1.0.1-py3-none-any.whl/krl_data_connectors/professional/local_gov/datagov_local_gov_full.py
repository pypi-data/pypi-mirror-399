# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Data.gov Local Government Domain Connector - Professional Tier

Full access to local government datasets with unlimited search.
Pre-configured for Census, GSA, Treasury.
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from krl_data_connectors.professional.civic.datagov_full import DataGovFullConnector
from krl_data_connectors.licensed_connector_mixin import requires_license


class DataGovLocalGovFullConnector(DataGovFullConnector):
    """
    Data.gov Local Government Domain Connector - Professional Tier
    """

    _connector_name = "DataGov_LocalGov_Full"
    DEFAULT_DOWNLOAD_DIR = "~/.krl/data/datagov_local_gov"

    DOMAIN_ORGANIZATIONS: List[str] = [
        "census-gov",       # Census Bureau
        "gsa-gov",          # General Services Administration
        "treasury-gov",     # Department of Treasury
    ]
    
    DOMAIN_TAGS: List[str] = [
        "local-government",
        "municipal",
        "county",
        "state-government",
    ]
    
    DOMAIN_NAME: str = "Local Government"

    POPULAR_DATASETS: Dict[str, List[str]] = {
        "finance": [
            "state-local-finance",
            "government-expenditures",
            "tax-revenue",
        ],
        "services": [
            "public-services",
            "municipal-data",
        ],
        "employment": [
            "government-employment",
            "public-sector-wages",
        ],
    }

    @requires_license
    def search_government_finance(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for government finance datasets."""
        search_query = f"government finance {query}" if query != "*:*" else "state local government finance"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_municipal_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for municipal datasets."""
        search_query = f"municipal city {query}" if query != "*:*" else "municipal city local government"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_county_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for county-level datasets."""
        search_query = f"county {query}" if query != "*:*" else "county government data"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_tax_revenue_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for tax revenue datasets."""
        search_query = f"tax revenue {query}" if query != "*:*" else "tax revenue state local"
        return self.search_datasets(query=search_query, rows=rows)

    def __repr__(self) -> str:
        return (
            f"DataGovLocalGovFullConnector("
            f"domain='{self.DOMAIN_NAME}', "
            f"organizations={self.DOMAIN_ORGANIZATIONS})"
        )
