# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Data.gov Education Domain Connector - Community Tier

Pre-configured access to education datasets from Data.gov, filtered to
Department of Education, NCES, and NSF agencies. Provides datasets on
schools, colleges, students, teachers, and education funding.

Domain Organizations:
- ED (ed-gov): Department of Education programs, policy data
- NCES (nces-gov): Education statistics, surveys
- NSF (nsf-gov): STEM education, research funding

Key Dataset Categories:
- K-12: Elementary, secondary school data
- Higher Education: College, university data
- Students: Enrollment, achievement, outcomes
- Teachers: Staffing, qualifications, salaries
- Finance: School funding, expenditures

Usage:
    from krl_data_connectors.community.education import DataGovEducationConnector
    
    edu = DataGovEducationConnector()
    
    # Search education datasets (auto-filtered to ED/NCES)
    results = edu.search_datasets("student enrollment")
    
    # Use convenience methods
    k12 = edu.search_k12_data("graduation rates")
    colleges = edu.search_higher_education_data("tuition costs")
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from krl_data_connectors.community.civic.datagov_catalog import DataGovCatalogConnector


class DataGovEducationConnector(DataGovCatalogConnector):
    """
    Data.gov Education Domain Connector - Community Tier

    Pre-configured for Department of Education, NCES, and NSF datasets.
    All searches are automatically filtered to education organizations
    unless overridden with a specific organization parameter.

    Limitations (Community Tier):
    - Maximum 50 results per search query
    - No bulk export functionality
    - Upgrade to DataGovEducationFullConnector for unlimited access
    """

    _connector_name = "DataGov_Education"

    # Domain configuration - auto-filter searches to these organizations
    DOMAIN_ORGANIZATIONS: List[str] = [
        "ed-gov",       # Department of Education
        "nces-gov",     # National Center for Education Statistics
        "nsf-gov",      # National Science Foundation
    ]
    
    DOMAIN_TAGS: List[str] = [
        "education",
        "schools",
        "college",
        "students",
        "teachers",
        "enrollment",
        "graduation",
    ]
    
    DOMAIN_NAME: str = "Education"

    # Override popular datasets with education focus
    POPULAR_DATASETS: Dict[str, List[str]] = {
        "k12": [
            "common-core-of-data",
            "elementary-secondary-information",
            "public-school-characteristics",
            "private-school-survey",
            "school-district-finance",
        ],
        "higher_education": [
            "college-scorecard",
            "ipeds-completion-data",
            "postsecondary-enrollment",
            "college-tuition-costs",
            "student-financial-aid",
        ],
        "students": [
            "student-enrollment",
            "graduation-rates",
            "assessment-scores",
            "student-demographics",
            "english-learners",
        ],
        "teachers": [
            "teacher-staffing",
            "teacher-qualifications",
            "teacher-salaries",
            "pupil-teacher-ratio",
            "educator-workforce",
        ],
        "finance": [
            "school-finance-data",
            "education-expenditures",
            "federal-education-funding",
            "title-i-allocations",
            "pell-grant-data",
        ],
    }

    # Education organizations with descriptions
    WHITELISTED_ORGANIZATIONS: Dict[str, str] = {
        "ed-gov": "U.S. Department of Education",
        "nces-gov": "National Center for Education Statistics",
        "nsf-gov": "National Science Foundation",
        "census-gov": "U.S. Census Bureau",
    }

    def search_ed_datasets(
        self,
        query: str,
        formats: Optional[List[str]] = None,
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search Department of Education datasets specifically.

        Args:
            query: Search query string
            formats: Filter by resource format
            rows: Number of results (max 50 for Community tier)

        Returns:
            DataFrame with ED dataset metadata
        """
        return self.search_datasets(
            query=query,
            organization="ed-gov",
            formats=formats,
            rows=rows,
        )

    def search_nces_datasets(
        self,
        query: str,
        formats: Optional[List[str]] = None,
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search NCES datasets specifically.

        Args:
            query: Search query string
            formats: Filter by resource format
            rows: Number of results (max 50 for Community tier)

        Returns:
            DataFrame with NCES dataset metadata
        """
        return self.search_datasets(
            query=query,
            organization="nces-gov",
            formats=formats,
            rows=rows,
        )

    def search_k12_data(
        self,
        query: str = "*:*",
        state: Optional[str] = None,
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search for K-12 education datasets.

        Args:
            query: Search query (default: all K-12 datasets)
            state: Optional state filter
            rows: Number of results

        Returns:
            DataFrame with K-12 dataset metadata
        """
        search_query = f"elementary secondary school {query}" if query != "*:*" else "K-12 elementary secondary"
        if state:
            search_query = f"{search_query} {state}"
        
        return self.search_datasets(
            query=search_query,
            rows=rows,
        )

    def search_higher_education_data(
        self,
        query: str = "*:*",
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search for college and university datasets.

        Args:
            query: Search query (default: all higher ed datasets)
            rows: Number of results

        Returns:
            DataFrame with higher education dataset metadata
        """
        search_query = f"college university {query}" if query != "*:*" else "college university postsecondary"
        
        return self.search_datasets(
            query=search_query,
            rows=rows,
        )

    def search_enrollment_data(
        self,
        query: str = "*:*",
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search for student enrollment datasets.

        Args:
            query: Search query (default: all enrollment datasets)
            rows: Number of results

        Returns:
            DataFrame with enrollment dataset metadata
        """
        search_query = f"enrollment {query}" if query != "*:*" else "student enrollment school"
        
        return self.search_datasets(
            query=search_query,
            rows=rows,
        )

    def search_graduation_data(
        self,
        query: str = "*:*",
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search for graduation rate datasets.

        Args:
            query: Search query (default: all graduation datasets)
            rows: Number of results

        Returns:
            DataFrame with graduation dataset metadata
        """
        search_query = f"graduation rates {query}" if query != "*:*" else "graduation rates completion"
        
        return self.search_datasets(
            query=search_query,
            rows=rows,
        )

    def search_education_finance(
        self,
        query: str = "*:*",
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search for education funding datasets.

        Args:
            query: Search query (default: all finance datasets)
            rows: Number of results

        Returns:
            DataFrame with education finance dataset metadata
        """
        search_query = f"education funding {query}" if query != "*:*" else "school funding expenditures finance"
        
        return self.search_datasets(
            query=search_query,
            rows=rows,
        )

    def get_education_categories(self) -> List[str]:
        """Get available education dataset categories."""
        return list(self.POPULAR_DATASETS.keys())

    def __repr__(self) -> str:
        return (
            f"DataGovEducationConnector("
            f"domain='{self.DOMAIN_NAME}', "
            f"organizations={self.DOMAIN_ORGANIZATIONS}, "
            f"max_results={self.MAX_RESULTS})"
        )
