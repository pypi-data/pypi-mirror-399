# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Data.gov Business Domain Connector - Professional Tier

Full access to business datasets from Data.gov with unlimited search,
bulk export, and resource streaming. Pre-configured for SBA, Census, Commerce.
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from krl_data_connectors.professional.civic.datagov_full import DataGovFullConnector
from krl_data_connectors.licensed_connector_mixin import requires_license


class DataGovBusinessFullConnector(DataGovFullConnector):
    """
    Data.gov Business Domain Connector - Professional Tier

    Full access to SBA, Census, and Commerce business datasets.
    """

    _connector_name = "DataGov_Business_Full"
    DEFAULT_DOWNLOAD_DIR = "~/.krl/data/datagov_business"

    DOMAIN_ORGANIZATIONS: List[str] = [
        "sba-gov",          # Small Business Administration
        "census-gov",       # Census Bureau
        "commerce-gov",     # Department of Commerce
        "ita-gov",          # International Trade Administration
        "gsa-gov",          # General Services Administration
    ]
    
    DOMAIN_TAGS: List[str] = [
        "business",
        "enterprise",
        "commerce",
        "contracts",
        "trade",
    ]
    
    DOMAIN_NAME: str = "Business"

    POPULAR_DATASETS: Dict[str, List[str]] = {
        "patterns": [
            "county-business-patterns",
            "zip-code-business-patterns",
            "business-dynamics",
            "nonemployer-statistics",
        ],
        "contracts": [
            "federal-procurement",
            "contract-opportunities",
            "sam-entity-data",
            "government-contracts",
        ],
        "small_business": [
            "sba-loan-data",
            "small-business-lending",
            "eidl-loans",
            "ppp-loans",
        ],
        "trade": [
            "export-data",
            "import-data",
            "trade-statistics",
            "international-trade",
        ],
    }

    @requires_license
    def search_sba_datasets(
        self,
        query: str,
        formats: Optional[List[str]] = None,
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search SBA datasets specifically."""
        return self.search_datasets(
            query=query,
            organization="sba-gov",
            formats=formats,
            rows=rows,
        )

    @requires_license
    def search_business_patterns(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for business patterns datasets."""
        search_query = f"business patterns {query}" if query != "*:*" else "county business patterns establishments"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_government_contracts(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for government contract datasets."""
        search_query = f"contracts {query}" if query != "*:*" else "federal procurement contracts"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_sba_loans(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for SBA loan datasets."""
        search_query = f"SBA loans {query}" if query != "*:*" else "SBA loans lending small business"
        return self.search_datasets(query=search_query, organization="sba-gov", rows=rows)

    @requires_license
    def search_trade_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for trade statistics datasets."""
        search_query = f"trade {query}" if query != "*:*" else "export import trade statistics"
        return self.search_datasets(query=search_query, rows=rows)

    def __repr__(self) -> str:
        return (
            f"DataGovBusinessFullConnector("
            f"domain='{self.DOMAIN_NAME}', "
            f"organizations={self.DOMAIN_ORGANIZATIONS})"
        )
