# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Data.gov Science Domain Connector - Professional Tier

Full access to science and research datasets.
Pre-configured for NSF, NASA, DOE, NIH.
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from krl_data_connectors.professional.civic.datagov_full import DataGovFullConnector
from krl_data_connectors.licensed_connector_mixin import requires_license


class DataGovScienceFullConnector(DataGovFullConnector):
    """
    Data.gov Science Domain Connector - Professional Tier
    """

    _connector_name = "DataGov_Science_Full"
    DEFAULT_DOWNLOAD_DIR = "~/.krl/data/datagov_science"

    DOMAIN_ORGANIZATIONS: List[str] = [
        "nsf-gov",            # National Science Foundation
        "nasa-gov",           # NASA
        "osti-energy-gov",    # DOE Office of Scientific and Technical Information
        "nih-gov",            # National Institutes of Health
        "noaa-gov",           # NOAA
        "nist-gov",           # National Institute of Standards and Technology
    ]
    
    DOMAIN_TAGS: List[str] = [
        "science",
        "research",
        "grants",
        "publications",
        "innovation",
    ]
    
    DOMAIN_NAME: str = "Science"

    POPULAR_DATASETS: Dict[str, List[str]] = {
        "grants": [
            "nsf-awards",
            "nih-grants",
            "research-funding",
        ],
        "research": [
            "publications",
            "patents",
            "research-data",
        ],
        "space": [
            "nasa-missions",
            "satellite-data",
            "earth-science",
        ],
    }

    @requires_license
    def search_nsf_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for NSF datasets."""
        search_query = f"NSF {query}" if query != "*:*" else "NSF grants research"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_nasa_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for NASA datasets."""
        search_query = f"NASA {query}" if query != "*:*" else "NASA space science"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_nih_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for NIH datasets."""
        search_query = f"NIH {query}" if query != "*:*" else "NIH health research grants"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_research_grants(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for research grant datasets."""
        search_query = f"research grants {query}" if query != "*:*" else "research grants funding awards"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_patents_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for patents and innovation datasets."""
        search_query = f"patents {query}" if query != "*:*" else "patents innovation research"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def bulk_export_science_data(
        self,
        topic: str = "grants",
        limit: int = 1000,
        output_format: str = "parquet",
    ) -> str:
        """Bulk export science datasets."""
        return self.bulk_export_domain_data(
            topic=topic,
            limit=limit,
            output_format=output_format,
        )

    def __repr__(self) -> str:
        return (
            f"DataGovScienceFullConnector("
            f"domain='{self.DOMAIN_NAME}', "
            f"organizations={self.DOMAIN_ORGANIZATIONS})"
        )
