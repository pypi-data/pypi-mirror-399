# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Data.gov Financial Domain Connector - Professional Tier

Full access to financial datasets with unlimited search, bulk export.
Pre-configured for Treasury, SEC, FDIC, FFIEC, CFPB.
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from krl_data_connectors.professional.civic.datagov_full import DataGovFullConnector
from krl_data_connectors.licensed_connector_mixin import requires_license


class DataGovFinancialFullConnector(DataGovFullConnector):
    """
    Data.gov Financial Domain Connector - Professional Tier
    """

    _connector_name = "DataGov_Financial_Full"
    DEFAULT_DOWNLOAD_DIR = "~/.krl/data/datagov_financial"

    DOMAIN_ORGANIZATIONS: List[str] = [
        "treasury-gov",     # Department of Treasury
        "sec-gov",          # Securities and Exchange Commission
        "fdic-gov",         # FDIC
        "ffiec-gov",        # FFIEC
        "cfpb-gov",         # Consumer Financial Protection Bureau
    ]
    
    DOMAIN_TAGS: List[str] = [
        "finance",
        "banking",
        "securities",
        "debt",
        "budget",
        "fiscal",
    ]
    
    DOMAIN_NAME: str = "Financial"

    POPULAR_DATASETS: Dict[str, List[str]] = {
        "treasury": [
            "daily-treasury-statement",
            "public-debt",
            "treasury-securities",
        ],
        "banking": [
            "fdic-bank-data",
            "failed-banks",
            "call-reports",
        ],
        "securities": [
            "sec-filings",
            "edgar",
            "market-data",
        ],
        "consumer": [
            "consumer-complaints",
            "mortgage-data",
            "credit-data",
        ],
    }

    @requires_license
    def search_treasury_data(
        self,
        query: str,
        formats: Optional[List[str]] = None,
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search Treasury datasets specifically."""
        return self.search_datasets(
            query=query,
            organization="treasury-gov",
            formats=formats,
            rows=rows,
        )

    @requires_license
    def search_sec_data(
        self,
        query: str,
        formats: Optional[List[str]] = None,
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search SEC datasets specifically."""
        return self.search_datasets(
            query=query,
            organization="sec-gov",
            formats=formats,
            rows=rows,
        )

    @requires_license
    def search_banking_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for banking datasets."""
        search_query = f"bank {query}" if query != "*:*" else "bank banking FDIC"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_public_debt_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for public debt datasets."""
        search_query = f"public debt {query}" if query != "*:*" else "public debt treasury"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_securities_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for securities datasets."""
        search_query = f"securities {query}" if query != "*:*" else "securities filings"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_mortgage_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for mortgage datasets."""
        search_query = f"mortgage {query}" if query != "*:*" else "mortgage HMDA lending"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def bulk_export_treasury_data(
        self,
        query: str = "*:*",
        max_datasets: int = 1000,
    ) -> pd.DataFrame:
        """Bulk export Treasury datasets."""
        return self.bulk_export(
            query=query,
            organization="treasury-gov",
            max_datasets=max_datasets,
        )

    def __repr__(self) -> str:
        return (
            f"DataGovFinancialFullConnector("
            f"domain='{self.DOMAIN_NAME}', "
            f"organizations={self.DOMAIN_ORGANIZATIONS})"
        )
