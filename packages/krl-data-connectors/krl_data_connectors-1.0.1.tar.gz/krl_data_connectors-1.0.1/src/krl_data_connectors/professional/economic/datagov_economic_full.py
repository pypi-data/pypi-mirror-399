# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Data.gov Economic Domain Connector - Professional Tier

Full access to economic datasets with unlimited search, bulk export.
Pre-configured for BEA, BLS, Commerce, Treasury, SBA.
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from krl_data_connectors.professional.civic.datagov_full import DataGovFullConnector
from krl_data_connectors.licensed_connector_mixin import requires_license


class DataGovEconomicFullConnector(DataGovFullConnector):
    """
    Data.gov Economic Domain Connector - Professional Tier
    """

    _connector_name = "DataGov_Economic_Full"
    DEFAULT_DOWNLOAD_DIR = "~/.krl/data/datagov_economic"

    DOMAIN_ORGANIZATIONS: List[str] = [
        "bea-gov",          # Bureau of Economic Analysis
        "bls-gov",          # Bureau of Labor Statistics
        "commerce-gov",     # Department of Commerce
        "treasury-gov",     # Department of Treasury
        "sba-gov",          # Small Business Administration
    ]
    
    DOMAIN_TAGS: List[str] = [
        "economy",
        "gdp",
        "employment",
        "trade",
        "business",
        "income",
    ]
    
    DOMAIN_NAME: str = "Economic"

    POPULAR_DATASETS: Dict[str, List[str]] = {
        "gdp": [
            "gross-domestic-product",
            "gdp-by-state",
            "gdp-by-industry",
        ],
        "employment": [
            "current-employment-statistics",
            "unemployment",
            "job-openings",
        ],
        "trade": [
            "international-trade",
            "exports",
            "imports",
        ],
        "income": [
            "personal-income",
            "median-household-income",
            "wages",
        ],
    }

    @requires_license
    def search_bea_datasets(
        self,
        query: str,
        formats: Optional[List[str]] = None,
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search BEA datasets specifically."""
        return self.search_datasets(
            query=query,
            organization="bea-gov",
            formats=formats,
            rows=rows,
        )

    @requires_license
    def search_bls_datasets(
        self,
        query: str,
        formats: Optional[List[str]] = None,
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search BLS datasets specifically."""
        return self.search_datasets(
            query=query,
            organization="bls-gov",
            formats=formats,
            rows=rows,
        )

    @requires_license
    def search_gdp_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for GDP datasets."""
        search_query = f"GDP {query}" if query != "*:*" else "gross domestic product GDP"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_employment_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for employment datasets."""
        search_query = f"employment {query}" if query != "*:*" else "employment unemployment labor"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_trade_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for trade datasets."""
        search_query = f"trade {query}" if query != "*:*" else "international trade import export"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def bulk_export_bls_data(
        self,
        query: str = "*:*",
        max_datasets: int = 1000,
    ) -> pd.DataFrame:
        """Bulk export BLS datasets."""
        return self.bulk_export(
            query=query,
            organization="bls-gov",
            max_datasets=max_datasets,
        )

    def __repr__(self) -> str:
        return (
            f"DataGovEconomicFullConnector("
            f"domain='{self.DOMAIN_NAME}', "
            f"organizations={self.DOMAIN_ORGANIZATIONS})"
        )
