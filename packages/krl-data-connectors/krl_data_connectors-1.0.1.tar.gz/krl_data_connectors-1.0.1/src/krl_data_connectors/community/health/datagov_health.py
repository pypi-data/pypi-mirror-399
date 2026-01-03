# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Data.gov Health Domain Connector - Community Tier

Pre-configured access to health and healthcare datasets from Data.gov,
filtered to HHS, CDC, FDA, CMS, and other health agencies. Provides
50,000+ datasets on public health, healthcare quality, epidemiology,
Medicare/Medicaid, drug safety, and more.

Domain Organizations:
- HHS (hhs-gov): Department of Health and Human Services umbrella
- CDC: Disease surveillance, mortality, BRFSS
- FDA (fda-gov): Drug approvals, adverse events, recalls
- CMS (cms-gov): Medicare, Medicaid, hospital data
- NIH (nih-gov): Research grants, clinical trials

Key Dataset Categories:
- Public Health: Disease surveillance, mortality, behavioral risk factors
- Healthcare Quality: Hospital compare, physician compare, nursing homes
- Medicare/Medicaid: Claims, enrollment, provider utilization
- Drug Safety: Adverse events, recalls, approvals
- Epidemiology: COVID-19, flu surveillance, chronic disease

Usage:
    from krl_data_connectors.community.health import DataGovHealthConnector
    
    health = DataGovHealthConnector()
    
    # Search health datasets (auto-filtered to HHS agencies)
    results = health.search_datasets("diabetes prevalence")
    
    # Use agency-specific convenience methods
    cdc_data = health.search_cdc_datasets("COVID-19 surveillance")
    medicare = health.search_medicare_data("hospital readmissions")
    
    # Cross-domain search (bypass health filter)
    env_health = health.search_all_domains("environmental health disparities")
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from krl_data_connectors.community.civic.datagov_catalog import DataGovCatalogConnector


class DataGovHealthConnector(DataGovCatalogConnector):
    """
    Data.gov Health Domain Connector - Community Tier

    Pre-configured for HHS, CDC, FDA, CMS, and health agency datasets.
    All searches are automatically filtered to health organizations
    unless overridden with a specific organization parameter.

    Inherits from DataGovCatalogConnector with:
    - DOMAIN_ORGANIZATIONS: ["hhs-gov", "cdc-gov", "fda-gov", "cms-gov"]
    - Domain-specific popular datasets
    - Convenience methods for CDC, Medicare, FDA data

    Limitations (Community Tier):
    - Maximum 50 results per search query
    - No bulk export functionality
    - Upgrade to DataGovHealthFullConnector for unlimited access
    """

    _connector_name = "DataGov_Health"

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

    # Override popular datasets with health focus
    POPULAR_DATASETS: Dict[str, List[str]] = {
        "public_health": [
            "cdc-wonder",
            "behavioral-risk-factor-surveillance",
            "national-health-and-nutrition-examination",
            "national-health-interview-survey",
            "youth-risk-behavior-surveillance",
        ],
        "epidemiology": [
            "covid-19-case-surveillance",
            "influenza-surveillance",
            "foodborne-disease-outbreaks",
            "hiv-aids-surveillance",
            "sexually-transmitted-disease-surveillance",
        ],
        "healthcare_quality": [
            "hospital-compare",
            "physician-compare",
            "nursing-home-compare",
            "dialysis-facility-compare",
            "home-health-compare",
        ],
        "medicare_medicaid": [
            "medicare-provider-utilization",
            "medicare-inpatient-hospitals",
            "medicaid-enrollment",
            "medicare-part-d-prescribers",
            "durable-medical-equipment",
        ],
        "drug_safety": [
            "fda-adverse-event-reporting",
            "drug-recalls-enforcement",
            "orange-book-products",
            "national-drug-code-directory",
            "medication-guides",
        ],
        "mortality": [
            "multiple-cause-of-death",
            "infant-mortality-rates",
            "life-expectancy",
            "mortality-underlying-cause",
            "maternal-mortality",
        ],
    }

    # Health organizations with descriptions
    WHITELISTED_ORGANIZATIONS: Dict[str, str] = {
        "hhs-gov": "Department of Health and Human Services",
        "cdc-gov": "Centers for Disease Control and Prevention",
        "fda-gov": "Food and Drug Administration",
        "cms-gov": "Centers for Medicare & Medicaid Services",
        "nih-gov": "National Institutes of Health",
        "samhsa-gov": "Substance Abuse and Mental Health Services",
        "hrsa-gov": "Health Resources and Services Administration",
        "ahrq-gov": "Agency for Healthcare Research and Quality",
    }

    def search_cdc_datasets(
        self,
        query: str,
        formats: Optional[List[str]] = None,
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search CDC datasets specifically.

        Convenience method for disease surveillance, mortality,
        and behavioral health data.

        Args:
            query: Search query string
            formats: Filter by resource format (e.g., ['CSV', 'JSON'])
            rows: Number of results (max 50 for Community tier)

        Returns:
            DataFrame with CDC dataset metadata

        Example:
            >>> health = DataGovHealthConnector()
            >>> flu = health.search_cdc_datasets("influenza surveillance")
        """
        return self.search_datasets(
            query=query,
            organization="cdc-gov",
            formats=formats,
            rows=rows,
        )

    def search_fda_datasets(
        self,
        query: str,
        formats: Optional[List[str]] = None,
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search FDA datasets specifically.

        Convenience method for drug approvals, adverse events,
        food safety, and medical device data.

        Args:
            query: Search query string
            formats: Filter by resource format (e.g., ['CSV', 'JSON'])
            rows: Number of results (max 50 for Community tier)

        Returns:
            DataFrame with FDA dataset metadata

        Example:
            >>> health = DataGovHealthConnector()
            >>> recalls = health.search_fda_datasets("drug recalls")
        """
        return self.search_datasets(
            query=query,
            organization="fda-gov",
            formats=formats,
            rows=rows,
        )

    def search_medicare_data(
        self,
        query: str = "*:*",
        rows: int = 10,
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
            >>> health = DataGovHealthConnector()
            >>> hospitals = health.search_medicare_data("hospital readmissions")
        """
        search_query = f"medicare {query}" if query != "*:*" else "medicare"
        
        return self.search_datasets(
            query=search_query,
            organization="cms-gov",
            rows=rows,
        )

    def search_disease_surveillance(
        self,
        disease: Optional[str] = None,
        rows: int = 10,
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

    def search_mortality_data(
        self,
        query: str = "*:*",
        rows: int = 10,
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

    def search_healthcare_quality(
        self,
        facility_type: Optional[str] = None,
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search for healthcare quality and compare datasets.

        Args:
            facility_type: Optional type filter (e.g., "hospital", "nursing home")
            rows: Number of results

        Returns:
            DataFrame with quality metrics dataset metadata

        Example:
            >>> health = DataGovHealthConnector()
            >>> hospitals = health.search_healthcare_quality("hospital")
        """
        search_query = f"{facility_type} compare quality" if facility_type else "healthcare quality compare"
        
        return self.search_datasets(
            query=search_query,
            organization="cms-gov",
            rows=rows,
        )

    def search_drug_data(
        self,
        query: str = "*:*",
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search for drug and pharmaceutical datasets.

        Includes FDA drug approvals, adverse events, and NDC directory.

        Args:
            query: Search query (default: all drug datasets)
            rows: Number of results

        Returns:
            DataFrame with drug dataset metadata
        """
        search_query = f"drug {query}" if query != "*:*" else "drug pharmaceutical"
        
        return self.search_datasets(
            query=search_query,
            organization="fda-gov",
            rows=rows,
        )

    def get_health_categories(self) -> List[str]:
        """
        Get available health dataset categories.

        Returns:
            List of category names specific to health data
        """
        return list(self.POPULAR_DATASETS.keys())

    def __repr__(self) -> str:
        return (
            f"DataGovHealthConnector("
            f"domain='{self.DOMAIN_NAME}', "
            f"organizations={self.DOMAIN_ORGANIZATIONS}, "
            f"max_results={self.MAX_RESULTS})"
        )
