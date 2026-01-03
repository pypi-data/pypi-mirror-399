# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Data.gov Technology Domain Connector - Professional Tier

Full access to technology and telecommunications datasets.
Pre-configured for FCC, NTIA, NIST.
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from krl_data_connectors.professional.civic.datagov_full import DataGovFullConnector
from krl_data_connectors.licensed_connector_mixin import requires_license


class DataGovTechnologyFullConnector(DataGovFullConnector):
    """
    Data.gov Technology Domain Connector - Professional Tier
    """

    _connector_name = "DataGov_Technology_Full"
    DEFAULT_DOWNLOAD_DIR = "~/.krl/data/datagov_technology"

    DOMAIN_ORGANIZATIONS: List[str] = [
        "fcc-gov",            # Federal Communications Commission
        "ntia-commerce-gov",  # NTIA
        "nist-gov",           # National Institute of Standards and Technology
        "gsa-gov",            # General Services Administration
    ]
    
    DOMAIN_TAGS: List[str] = [
        "technology",
        "broadband",
        "telecommunications",
        "spectrum",
        "cybersecurity",
    ]
    
    DOMAIN_NAME: str = "Technology"

    POPULAR_DATASETS: Dict[str, List[str]] = {
        "broadband": [
            "broadband-availability",
            "internet-access",
            "fixed-broadband",
        ],
        "spectrum": [
            "spectrum-allocation",
            "wireless-licenses",
            "radio-frequency",
        ],
        "standards": [
            "cybersecurity-framework",
            "standards-data",
            "measurements",
        ],
    }

    @requires_license
    def search_broadband_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for broadband datasets."""
        search_query = f"broadband {query}" if query != "*:*" else "broadband internet access"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_spectrum_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for spectrum datasets."""
        search_query = f"spectrum {query}" if query != "*:*" else "spectrum wireless radio"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_cybersecurity_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for cybersecurity datasets."""
        search_query = f"cybersecurity {query}" if query != "*:*" else "cybersecurity security NIST"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_telecom_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for telecommunications datasets."""
        search_query = f"telecommunications {query}" if query != "*:*" else "telecommunications FCC"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_it_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for IT infrastructure datasets."""
        search_query = f"IT infrastructure {query}" if query != "*:*" else "IT infrastructure technology"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def bulk_export_technology_data(
        self,
        topic: str = "broadband",
        limit: int = 1000,
        output_format: str = "parquet",
    ) -> str:
        """Bulk export technology datasets."""
        return self.bulk_export_domain_data(
            topic=topic,
            limit=limit,
            output_format=output_format,
        )

    def __repr__(self) -> str:
        return (
            f"DataGovTechnologyFullConnector("
            f"domain='{self.DOMAIN_NAME}', "
            f"organizations={self.DOMAIN_ORGANIZATIONS})"
        )
