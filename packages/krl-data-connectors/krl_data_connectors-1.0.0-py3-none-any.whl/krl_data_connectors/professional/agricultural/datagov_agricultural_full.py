# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Data.gov Agricultural Domain Connector - Professional Tier

Full access to agricultural datasets from Data.gov with unlimited search,
bulk export, and resource streaming. Pre-configured for USDA agencies.

Professional tier includes:
- Unlimited search results (vs 50 for Community)
- Bulk export up to 10,000 datasets
- Resource file streaming with local caching

Domain Organizations:
- USDA (usda-gov): Primary agriculture data
- FSA (fsa-usda-gov): Farm Service Agency
- NASS (nass-usda-gov): National Agricultural Statistics Service
- ERS (ers-usda-gov): Economic Research Service
- AMS (ams-usda-gov): Agricultural Marketing Service
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from krl_data_connectors.professional.civic.datagov_full import DataGovFullConnector
from krl_data_connectors.licensed_connector_mixin import requires_license


class DataGovAgriculturalFullConnector(DataGovFullConnector):
    """
    Data.gov Agricultural Domain Connector - Professional Tier

    Full access to USDA and agricultural agency datasets with
    unlimited search, bulk export, and resource streaming.
    """

    _connector_name = "DataGov_Agricultural_Full"
    DEFAULT_DOWNLOAD_DIR = "~/.krl/data/datagov_agricultural"

    DOMAIN_ORGANIZATIONS: List[str] = [
        "usda-gov",         # US Department of Agriculture
        "fsa-usda-gov",     # Farm Service Agency
        "nass-usda-gov",    # National Agricultural Statistics Service
        "ers-usda-gov",     # Economic Research Service
        "ams-usda-gov",     # Agricultural Marketing Service
    ]
    
    DOMAIN_TAGS: List[str] = [
        "agriculture",
        "farming",
        "crops",
        "livestock",
        "food",
        "rural",
    ]
    
    DOMAIN_NAME: str = "Agricultural"

    POPULAR_DATASETS: Dict[str, List[str]] = {
        "crops": [
            "crop-production",
            "crop-progress",
            "crop-acreage",
            "crop-values",
            "field-crops",
        ],
        "livestock": [
            "cattle-inventory",
            "hogs-pigs",
            "poultry-production",
            "dairy-products",
            "livestock-slaughter",
        ],
        "food_access": [
            "food-access-research-atlas",
            "snap-participation",
            "food-insecurity",
            "food-environment-atlas",
            "food-desert",
        ],
        "farm_economics": [
            "farm-income",
            "agricultural-prices",
            "farm-production-expenses",
            "agricultural-exports",
            "farm-labor",
        ],
    }

    @requires_license
    def search_usda_datasets(
        self,
        query: str,
        formats: Optional[List[str]] = None,
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search USDA datasets specifically."""
        return self.search_datasets(
            query=query,
            organization="usda-gov",
            formats=formats,
            rows=rows,
        )

    @requires_license
    def search_crop_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for crop production datasets."""
        search_query = f"crop {query}" if query != "*:*" else "crop production agriculture"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_livestock_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for livestock datasets."""
        search_query = f"livestock {query}" if query != "*:*" else "livestock cattle poultry"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_food_access_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for food access and nutrition datasets."""
        search_query = f"food access {query}" if query != "*:*" else "food access SNAP nutrition"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_farm_economics_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for farm economics datasets."""
        search_query = f"farm economics {query}" if query != "*:*" else "farm income agricultural prices"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def bulk_export_usda_data(
        self,
        query: str = "*:*",
        max_datasets: int = 1000,
    ) -> pd.DataFrame:
        """Bulk export USDA datasets."""
        return self.bulk_export(
            query=query,
            organization="usda-gov",
            max_datasets=max_datasets,
        )

    def __repr__(self) -> str:
        return (
            f"DataGovAgriculturalFullConnector("
            f"domain='{self.DOMAIN_NAME}', "
            f"organizations={self.DOMAIN_ORGANIZATIONS})"
        )
