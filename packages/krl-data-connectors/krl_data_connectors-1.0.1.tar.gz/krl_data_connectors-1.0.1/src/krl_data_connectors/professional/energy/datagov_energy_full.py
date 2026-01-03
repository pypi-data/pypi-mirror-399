# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Data.gov Energy Domain Connector - Professional Tier

Full access to energy datasets with unlimited search, bulk export.
Pre-configured for DOE, EIA, NRC, FERC.
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from krl_data_connectors.professional.civic.datagov_full import DataGovFullConnector
from krl_data_connectors.licensed_connector_mixin import requires_license


class DataGovEnergyFullConnector(DataGovFullConnector):
    """
    Data.gov Energy Domain Connector - Professional Tier
    """

    _connector_name = "DataGov_Energy_Full"
    DEFAULT_DOWNLOAD_DIR = "~/.krl/data/datagov_energy"

    DOMAIN_ORGANIZATIONS: List[str] = [
        "energy-gov",       # Department of Energy
        "eia-gov",          # Energy Information Administration
        "nrc-gov",          # Nuclear Regulatory Commission
        "ferc-gov",         # Federal Energy Regulatory Commission
    ]
    
    DOMAIN_TAGS: List[str] = [
        "energy",
        "electricity",
        "oil",
        "gas",
        "renewable",
        "nuclear",
        "solar",
    ]
    
    DOMAIN_NAME: str = "Energy"

    POPULAR_DATASETS: Dict[str, List[str]] = {
        "electricity": [
            "electricity-generation",
            "power-plants",
            "electric-grid",
            "utility-data",
        ],
        "petroleum": [
            "crude-oil",
            "petroleum-products",
            "natural-gas",
            "fuel-prices",
        ],
        "renewable": [
            "solar-energy",
            "wind-energy",
            "hydroelectric",
            "biofuels",
        ],
        "nuclear": [
            "nuclear-reactors",
            "uranium",
            "nuclear-waste",
        ],
        "consumption": [
            "energy-consumption",
            "sector-consumption",
            "energy-efficiency",
        ],
    }

    @requires_license
    def search_eia_datasets(
        self,
        query: str,
        formats: Optional[List[str]] = None,
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search EIA datasets specifically."""
        return self.search_datasets(
            query=query,
            organization="eia-gov",
            formats=formats,
            rows=rows,
        )

    @requires_license
    def search_electricity_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for electricity datasets."""
        search_query = f"electricity {query}" if query != "*:*" else "electricity generation power"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_petroleum_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for petroleum datasets."""
        search_query = f"petroleum oil {query}" if query != "*:*" else "petroleum oil natural gas"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_renewable_energy(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for renewable energy datasets."""
        search_query = f"renewable {query}" if query != "*:*" else "renewable solar wind energy"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_energy_consumption(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for energy consumption datasets."""
        search_query = f"consumption {query}" if query != "*:*" else "energy consumption sector"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def bulk_export_eia_data(
        self,
        query: str = "*:*",
        max_datasets: int = 1000,
    ) -> pd.DataFrame:
        """Bulk export EIA datasets."""
        return self.bulk_export(
            query=query,
            organization="eia-gov",
            max_datasets=max_datasets,
        )

    def __repr__(self) -> str:
        return (
            f"DataGovEnergyFullConnector("
            f"domain='{self.DOMAIN_NAME}', "
            f"organizations={self.DOMAIN_ORGANIZATIONS})"
        )
