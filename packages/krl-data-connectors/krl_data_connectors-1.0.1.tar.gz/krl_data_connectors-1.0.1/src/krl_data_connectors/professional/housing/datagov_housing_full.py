# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Data.gov Housing Domain Connector - Professional Tier

Full access to housing datasets with unlimited search, bulk export.
Pre-configured for HUD, FHFA, Census, CFPB.
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from krl_data_connectors.professional.civic.datagov_full import DataGovFullConnector
from krl_data_connectors.licensed_connector_mixin import requires_license


class DataGovHousingFullConnector(DataGovFullConnector):
    """
    Data.gov Housing Domain Connector - Professional Tier
    """

    _connector_name = "DataGov_Housing_Full"
    DEFAULT_DOWNLOAD_DIR = "~/.krl/data/datagov_housing"

    DOMAIN_ORGANIZATIONS: List[str] = [
        "hud-gov",          # HUD
        "fhfa-gov",         # Federal Housing Finance Agency
        "census-gov",       # Census Bureau
        "cfpb-gov",         # Consumer Financial Protection Bureau
    ]
    
    DOMAIN_TAGS: List[str] = [
        "housing",
        "homes",
        "rental",
        "mortgage",
        "real-estate",
        "homelessness",
    ]
    
    DOMAIN_NAME: str = "Housing"

    POPULAR_DATASETS: Dict[str, List[str]] = {
        "hud": [
            "fair-market-rents",
            "section-8",
            "public-housing",
            "hud-programs",
        ],
        "finance": [
            "hmda-mortgage",
            "house-price-index",
            "foreclosure-data",
        ],
        "homelessness": [
            "pit-counts",
            "continuum-of-care",
            "homeless-data",
        ],
        "rental": [
            "rental-data",
            "housing-affordability",
            "vacancy-rates",
        ],
    }

    @requires_license
    def search_hud_datasets(
        self,
        query: str,
        formats: Optional[List[str]] = None,
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search HUD datasets specifically."""
        return self.search_datasets(
            query=query,
            organization="hud-gov",
            formats=formats,
            rows=rows,
        )

    @requires_license
    def search_fair_market_rents(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for fair market rent datasets."""
        search_query = f"fair market rent {query}" if query != "*:*" else "fair market rent FMR"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_housing_finance(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for housing finance datasets."""
        search_query = f"mortgage housing {query}" if query != "*:*" else "mortgage housing finance HMDA"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_public_housing(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for public housing datasets."""
        search_query = f"public housing {query}" if query != "*:*" else "public housing section 8"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_homelessness_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for homelessness datasets."""
        search_query = f"homeless {query}" if query != "*:*" else "homeless PIT count CoC"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def bulk_export_hud_data(
        self,
        query: str = "*:*",
        max_datasets: int = 1000,
    ) -> pd.DataFrame:
        """Bulk export HUD datasets."""
        return self.bulk_export(
            query=query,
            organization="hud-gov",
            max_datasets=max_datasets,
        )

    def __repr__(self) -> str:
        return (
            f"DataGovHousingFullConnector("
            f"domain='{self.DOMAIN_NAME}', "
            f"organizations={self.DOMAIN_ORGANIZATIONS})"
        )
