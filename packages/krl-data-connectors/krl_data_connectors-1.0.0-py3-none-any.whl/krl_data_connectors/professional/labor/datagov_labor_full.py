# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Data.gov Labor Domain Connector - Professional Tier

Full access to labor datasets with unlimited search, bulk export.
Pre-configured for DOL, BLS, OSHA, EEOC.
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from krl_data_connectors.professional.civic.datagov_full import DataGovFullConnector
from krl_data_connectors.licensed_connector_mixin import requires_license


class DataGovLaborFullConnector(DataGovFullConnector):
    """
    Data.gov Labor Domain Connector - Professional Tier
    """

    _connector_name = "DataGov_Labor_Full"
    DEFAULT_DOWNLOAD_DIR = "~/.krl/data/datagov_labor"

    DOMAIN_ORGANIZATIONS: List[str] = [
        "dol-gov",          # Department of Labor
        "bls-gov",          # Bureau of Labor Statistics
        "osha-gov",         # OSHA
        "eeoc-gov",         # EEOC
        "nlrb-gov",         # National Labor Relations Board
    ]
    
    DOMAIN_TAGS: List[str] = [
        "labor",
        "employment",
        "workforce",
        "wages",
        "unions",
        "workplace",
    ]
    
    DOMAIN_NAME: str = "Labor"

    POPULAR_DATASETS: Dict[str, List[str]] = {
        "employment": [
            "employment-statistics",
            "unemployment",
            "labor-force",
            "job-openings",
        ],
        "wages": [
            "wage-data",
            "compensation",
            "earnings",
            "minimum-wage",
        ],
        "safety": [
            "osha-inspections",
            "workplace-injuries",
            "safety-violations",
        ],
        "discrimination": [
            "eeoc-charges",
            "employment-discrimination",
        ],
    }

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
    def search_osha_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for OSHA safety datasets."""
        search_query = f"OSHA {query}" if query != "*:*" else "OSHA workplace safety"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_wage_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for wage datasets."""
        search_query = f"wages {query}" if query != "*:*" else "wages compensation earnings"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_unemployment_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for unemployment datasets."""
        search_query = f"unemployment {query}" if query != "*:*" else "unemployment claims jobless"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_workplace_safety(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for workplace safety datasets."""
        search_query = f"workplace safety {query}" if query != "*:*" else "workplace safety injuries"
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
            f"DataGovLaborFullConnector("
            f"domain='{self.DOMAIN_NAME}', "
            f"organizations={self.DOMAIN_ORGANIZATIONS})"
        )
