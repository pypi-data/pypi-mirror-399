# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Data.gov Health Domain Connector - Professional Tier

Full access to health and healthcare datasets from Data.gov with unlimited
search, bulk export, and resource streaming. Pre-configured for HHS, CDC,
FDA, CMS, and other health agencies.

Professional tier includes:
- Unlimited search results (vs 50 for Community)
- Bulk export up to 10,000 datasets
- Resource file streaming with local caching
- Parallel downloads for efficiency
- Full API access with higher rate limits

Domain Organizations:
- HHS (hhs-gov): Department of Health and Human Services
- CDC (cdc-gov): Disease surveillance, mortality, BRFSS
- FDA (fda-gov): Drug approvals, adverse events, recalls
- CMS (cms-gov): Medicare, Medicaid, hospital data
- NIH (nih-gov): Research grants, clinical trials

Usage:
    from krl_data_connectors.professional.health import DataGovHealthFullConnector
    
    health = DataGovHealthFullConnector()
    
    # Search health datasets (unlimited results)
    results = health.search_datasets("diabetes prevalence", rows=500)
    
    # Bulk export CDC disease data
    disease_data = health.bulk_export_cdc_data(query="surveillance", max_datasets=1000)
    
    # Download and cache resource files
    path = health.download_resource("dataset-id", "resource-id")
    
    # Load directly as DataFrame
    df = health.fetch_as_dataframe("mortality-data")
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from krl_data_connectors.professional.civic.datagov_full import DataGovFullConnector
from krl_data_connectors.licensed_connector_mixin import requires_license


class DataGovHealthFullConnector(DataGovFullConnector):
    """
    Data.gov Health Domain Connector - Professional Tier

    Full access to HHS, CDC, FDA, CMS, and health agency datasets with
    unlimited search, bulk export, and resource streaming.

    Inherits from DataGovFullConnector with:
    - DOMAIN_ORGANIZATIONS: ["hhs-gov", "cdc-gov", "fda-gov", "cms-gov"]
    - Domain-specific popular datasets
    - Convenience methods for CDC, Medicare, FDA data
    - All Professional tier features (bulk export, streaming, caching)
    """

    _connector_name = "DataGov_Health_Full"
    DEFAULT_DOWNLOAD_DIR = "~/.krl/data/datagov_health"

    # Domain configuration - auto-filter searches to these organizations
    DOMAIN_ORGANIZATIONS: List[str] = [
        "hhs-gov",      # Department of Health and Human Services
        "cdc-gov",      # Centers for Disease Control and Prevention
        "fda-gov",      # Food and Drug Administration
        "cms-gov",      # Centers for Medicare & Medicaid Services
        "nih-gov",      # National Institutes of Health
        "samhsa-gov",   # Substance Abuse and Mental Health Services
    ]
    
    DOMAIN_TAGS: List[str] = [
        "health",
        "healthcare",
        "public-health",
        "medicare",
        "medicaid",
        "epidemiology",
        "disease",
    ]
    
    DOMAIN_NAME: str = "Health"

    @requires_license
    def search_cdc_datasets(
        self,
        query: str,
        formats: Optional[List[str]] = None,
        rows: int = 100,
    ) -> pd.DataFrame:
        """
        Search CDC datasets specifically.

        Convenience method for disease surveillance, mortality,
        and behavioral health data.

        Args:
            query: Search query string
            formats: Filter by resource format (e.g., ['CSV', 'JSON'])
            rows: Number of results (unlimited for Professional tier)

        Returns:
            DataFrame with CDC dataset metadata

        Example:
            >>> health = DataGovHealthFullConnector()
            >>> flu = health.search_cdc_datasets("influenza surveillance", rows=200)
        """
        return self.search_datasets(
            query=query,
            organization="cdc-gov",
            formats=formats,
            rows=rows,
        )

    @requires_license
    def search_fda_datasets(
        self,
        query: str,
        formats: Optional[List[str]] = None,
        rows: int = 100,
    ) -> pd.DataFrame:
        """
        Search FDA datasets specifically.

        Convenience method for drug approvals, adverse events,
        food safety, and medical device data.

        Args:
            query: Search query string
            formats: Filter by resource format (e.g., ['CSV', 'JSON'])
            rows: Number of results (unlimited for Professional tier)

        Returns:
            DataFrame with FDA dataset metadata

        Example:
            >>> health = DataGovHealthFullConnector()
            >>> recalls = health.search_fda_datasets("drug recalls", rows=500)
        """
        return self.search_datasets(
            query=query,
            organization="fda-gov",
            formats=formats,
            rows=rows,
        )

    @requires_license
    def search_medicare_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """
        Search for Medicare and CMS datasets.

        Includes provider utilization, hospital data, claims,
        and quality metrics.

        Args:
            query: Search query (default: all Medicare datasets)
            rows: Number of results

        Returns:
            DataFrame with Medicare/CMS dataset metadata

        Example:
            >>> health = DataGovHealthFullConnector()
            >>> hospitals = health.search_medicare_data("hospital readmissions", rows=200)
        """
        search_query = f"medicare {query}" if query != "*:*" else "medicare"
        
        return self.search_datasets(
            query=search_query,
            organization="cms-gov",
            rows=rows,
        )

    @requires_license
    def search_disease_surveillance(
        self,
        disease: Optional[str] = None,
        rows: int = 100,
    ) -> pd.DataFrame:
        """
        Search for disease surveillance datasets.

        Args:
            disease: Optional disease name filter (e.g., "COVID-19", "flu")
            rows: Number of results

        Returns:
            DataFrame with surveillance dataset metadata
        """
        search_query = f"{disease} surveillance" if disease else "disease surveillance"
        
        return self.search_datasets(
            query=search_query,
            organization="cdc-gov",
            rows=rows,
        )

    @requires_license
    def search_mortality_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """
        Search for mortality and death statistics datasets.

        Includes CDC WONDER, vital statistics, and cause of death data.

        Args:
            query: Search query (default: all mortality datasets)
            rows: Number of results

        Returns:
            DataFrame with mortality dataset metadata
        """
        search_query = f"mortality death {query}" if query != "*:*" else "mortality death statistics"
        
        return self.search_datasets(
            query=search_query,
            organization="cdc-gov",
            rows=rows,
        )

    @requires_license
    def search_healthcare_quality(
        self,
        facility_type: Optional[str] = None,
        rows: int = 100,
    ) -> pd.DataFrame:
        """
        Search for healthcare quality and compare datasets.

        Args:
            facility_type: Optional type filter (e.g., "hospital", "nursing home")
            rows: Number of results

        Returns:
            DataFrame with quality metrics dataset metadata
        """
        search_query = f"{facility_type} compare quality" if facility_type else "healthcare quality compare"
        
        return self.search_datasets(
            query=search_query,
            organization="cms-gov",
            rows=rows,
        )

    @requires_license
    def bulk_export_cdc_data(
        self,
        query: str = "*:*",
        max_datasets: int = 1000,
    ) -> pd.DataFrame:
        """
        Bulk export CDC datasets.

        Args:
            query: Search query
            max_datasets: Maximum datasets to export (up to 10,000)

        Returns:
            DataFrame with all matching CDC datasets
        """
        return self.bulk_export(
            query=query,
            organization="cdc-gov",
            max_datasets=min(max_datasets, self.MAX_BULK_EXPORT),
        )

    @requires_license
    def bulk_export_medicare_data(
        self,
        query: str = "*:*",
        max_datasets: int = 1000,
    ) -> pd.DataFrame:
        """
        Bulk export CMS/Medicare datasets.

        Args:
            query: Search query
            max_datasets: Maximum datasets to export (up to 10,000)

        Returns:
            DataFrame with all matching Medicare datasets
        """
        return self.bulk_export(
            query=query,
            organization="cms-gov",
            max_datasets=min(max_datasets, self.MAX_BULK_EXPORT),
        )

    def __repr__(self) -> str:
        return (
            f"DataGovHealthFullConnector("
            f"domain='{self.DOMAIN_NAME}', "
            f"organizations={self.DOMAIN_ORGANIZATIONS}, "
            f"download_dir='{self.download_dir}')"
        )
