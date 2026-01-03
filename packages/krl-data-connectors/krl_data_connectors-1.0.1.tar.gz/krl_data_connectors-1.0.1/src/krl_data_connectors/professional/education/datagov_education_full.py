# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Data.gov Education Domain Connector - Professional Tier

Full access to education datasets with unlimited search, bulk export.
Pre-configured for ED, NCES, NSF.
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from krl_data_connectors.professional.civic.datagov_full import DataGovFullConnector
from krl_data_connectors.licensed_connector_mixin import requires_license


class DataGovEducationFullConnector(DataGovFullConnector):
    """
    Data.gov Education Domain Connector - Professional Tier
    """

    _connector_name = "DataGov_Education_Full"
    DEFAULT_DOWNLOAD_DIR = "~/.krl/data/datagov_education"

    DOMAIN_ORGANIZATIONS: List[str] = [
        "ed-gov",           # Department of Education
        "nces-gov",         # National Center for Education Statistics
        "nsf-gov",          # National Science Foundation
    ]
    
    DOMAIN_TAGS: List[str] = [
        "education",
        "schools",
        "college",
        "students",
        "teachers",
    ]
    
    DOMAIN_NAME: str = "Education"

    POPULAR_DATASETS: Dict[str, List[str]] = {
        "k12": [
            "common-core-of-data",
            "public-school-data",
            "private-school-survey",
        ],
        "higher_education": [
            "college-scorecard",
            "ipeds",
            "postsecondary-enrollment",
        ],
        "students": [
            "enrollment",
            "graduation-rates",
            "assessment",
        ],
        "finance": [
            "school-finance",
            "education-expenditures",
            "federal-funding",
        ],
    }

    @requires_license
    def search_ed_datasets(
        self,
        query: str,
        formats: Optional[List[str]] = None,
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search Department of Education datasets."""
        return self.search_datasets(
            query=query,
            organization="ed-gov",
            formats=formats,
            rows=rows,
        )

    @requires_license
    def search_k12_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for K-12 education datasets."""
        search_query = f"K-12 school {query}" if query != "*:*" else "elementary secondary school"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_higher_education_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for higher education datasets."""
        search_query = f"college university {query}" if query != "*:*" else "college university postsecondary"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_enrollment_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for enrollment datasets."""
        search_query = f"enrollment {query}" if query != "*:*" else "student enrollment"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def bulk_export_education_data(
        self,
        query: str = "*:*",
        max_datasets: int = 1000,
    ) -> pd.DataFrame:
        """Bulk export education datasets."""
        return self.bulk_export(
            query=query,
            organization="ed-gov",
            max_datasets=max_datasets,
        )

    def __repr__(self) -> str:
        return (
            f"DataGovEducationFullConnector("
            f"domain='{self.DOMAIN_NAME}', "
            f"organizations={self.DOMAIN_ORGANIZATIONS})"
        )
