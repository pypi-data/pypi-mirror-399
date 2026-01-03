# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Data.gov Social Domain Connector - Professional Tier

Full access to social programs and services datasets.
Pre-configured for ACF, SSA, VA, USDA.
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from krl_data_connectors.professional.civic.datagov_full import DataGovFullConnector
from krl_data_connectors.licensed_connector_mixin import requires_license


class DataGovSocialFullConnector(DataGovFullConnector):
    """
    Data.gov Social Domain Connector - Professional Tier
    """

    _connector_name = "DataGov_Social_Full"
    DEFAULT_DOWNLOAD_DIR = "~/.krl/data/datagov_social"

    DOMAIN_ORGANIZATIONS: List[str] = [
        "acf-hhs-gov",        # Administration for Children and Families
        "ssa-gov",            # Social Security Administration
        "va-gov",             # Veterans Administration
        "fns-usda-gov",       # Food and Nutrition Service
        "hhs-gov",            # Health and Human Services
    ]
    
    DOMAIN_TAGS: List[str] = [
        "social-services",
        "welfare",
        "veterans",
        "snap",
        "assistance",
    ]
    
    DOMAIN_NAME: str = "Social"

    POPULAR_DATASETS: Dict[str, List[str]] = {
        "food_assistance": [
            "snap-data",
            "wic-data",
            "food-assistance",
        ],
        "child_welfare": [
            "tanf-data",
            "foster-care",
            "child-care",
        ],
        "veterans": [
            "va-benefits",
            "veteran-services",
            "disability-compensation",
        ],
        "social_security": [
            "ssi-data",
            "ssdi-data",
            "retirement-benefits",
        ],
    }

    @requires_license
    def search_snap_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for SNAP (food assistance) datasets."""
        search_query = f"SNAP {query}" if query != "*:*" else "SNAP food stamps assistance"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_tanf_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for TANF (welfare) datasets."""
        search_query = f"TANF {query}" if query != "*:*" else "TANF welfare assistance"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_veterans_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for veterans datasets."""
        search_query = f"veterans {query}" if query != "*:*" else "veterans benefits VA"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_social_security_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for Social Security datasets."""
        search_query = f"social security {query}" if query != "*:*" else "social security SSI SSDI"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_child_welfare_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for child welfare datasets."""
        search_query = f"child welfare {query}" if query != "*:*" else "child welfare foster care"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def bulk_export_social_data(
        self,
        topic: str = "snap",
        limit: int = 1000,
        output_format: str = "parquet",
    ) -> str:
        """Bulk export social program datasets."""
        return self.bulk_export_domain_data(
            topic=topic,
            limit=limit,
            output_format=output_format,
        )

    def __repr__(self) -> str:
        return (
            f"DataGovSocialFullConnector("
            f"domain='{self.DOMAIN_NAME}', "
            f"organizations={self.DOMAIN_ORGANIZATIONS})"
        )
