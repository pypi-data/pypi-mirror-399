# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Data.gov Financial Domain Connector - Community Tier

Pre-configured access to financial datasets from Data.gov, filtered to
Treasury, SEC, FDIC, FFIEC, and CFPB agencies. Provides datasets on
public debt, banking, securities, fiscal policy, and consumer finance.

Domain Organizations:
- Treasury (treasury-gov): Public debt, fiscal data, revenue
- SEC (sec-gov): Securities filings, market data
- FDIC (fdic-gov): Bank statistics, failures
- FFIEC (ffiec-gov): Financial institutions data
- CFPB (cfpb-gov): Consumer complaints, mortgage data

Key Dataset Categories:
- Treasury: Public debt, fiscal operations, revenue
- Banking: Bank statistics, FDIC data, failures
- Securities: SEC filings, market data
- Mortgages: HMDA, lending patterns
- Consumer: Complaints, protection data

Usage:
    from krl_data_connectors.community.financial import DataGovFinancialConnector
    
    fin = DataGovFinancialConnector()
    
    # Search financial datasets (auto-filtered to Treasury/SEC)
    results = fin.search_datasets("public debt")
    
    # Use agency-specific convenience methods
    treasury = fin.search_treasury_data("fiscal year")
    banking = fin.search_banking_data("bank failures")
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from krl_data_connectors.community.civic.datagov_catalog import DataGovCatalogConnector


class DataGovFinancialConnector(DataGovCatalogConnector):
    """
    Data.gov Financial Domain Connector - Community Tier

    Pre-configured for Treasury, SEC, FDIC, and financial agency datasets.
    All searches are automatically filtered to financial organizations
    unless overridden with a specific organization parameter.

    Limitations (Community Tier):
    - Maximum 50 results per search query
    - No bulk export functionality
    - Upgrade to DataGovFinancialFullConnector for unlimited access
    """

    _connector_name = "DataGov_Financial"

    # Domain configuration - auto-filter searches to these organizations
    DOMAIN_ORGANIZATIONS: List[str] = [
        "treasury-gov",     # Department of Treasury
        "sec-gov",          # Securities and Exchange Commission
        "fdic-gov",         # Federal Deposit Insurance Corporation
        "ffiec-gov",        # Federal Financial Institutions Examination Council
        "cfpb-gov",         # Consumer Financial Protection Bureau
    ]
    
    DOMAIN_TAGS: List[str] = [
        "finance",
        "banking",
        "securities",
        "debt",
        "budget",
        "fiscal",
        "mortgage",
    ]
    
    DOMAIN_NAME: str = "Financial"

    # Override popular datasets with financial focus
    POPULAR_DATASETS: Dict[str, List[str]] = {
        "treasury": [
            "daily-treasury-statement",
            "monthly-treasury-statement",
            "public-debt-outstanding",
            "treasury-securities",
            "federal-revenue-collections",
        ],
        "banking": [
            "fdic-bank-data",
            "failed-bank-list",
            "summary-of-deposits",
            "call-reports",
            "bank-holding-companies",
        ],
        "securities": [
            "sec-filings",
            "edgar-company-filings",
            "investment-company-data",
            "municipal-securities",
            "market-structure-data",
        ],
        "mortgages": [
            "hmda-mortgage-data",
            "mortgage-performance",
            "foreclosure-data",
            "home-lending-data",
            "fair-lending",
        ],
        "consumer": [
            "consumer-complaints",
            "credit-card-complaints",
            "debt-collection-complaints",
            "financial-literacy",
            "consumer-credit",
        ],
    }

    # Financial organizations with descriptions
    WHITELISTED_ORGANIZATIONS: Dict[str, str] = {
        "treasury-gov": "U.S. Department of the Treasury",
        "sec-gov": "Securities and Exchange Commission",
        "fdic-gov": "Federal Deposit Insurance Corporation",
        "ffiec-gov": "Federal Financial Institutions Examination Council",
        "cfpb-gov": "Consumer Financial Protection Bureau",
        "fhfa-gov": "Federal Housing Finance Agency",
    }

    def search_treasury_data(
        self,
        query: str,
        formats: Optional[List[str]] = None,
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search Treasury Department datasets specifically.

        Args:
            query: Search query string
            formats: Filter by resource format
            rows: Number of results (max 50 for Community tier)

        Returns:
            DataFrame with Treasury dataset metadata
        """
        return self.search_datasets(
            query=query,
            organization="treasury-gov",
            formats=formats,
            rows=rows,
        )

    def search_sec_data(
        self,
        query: str,
        formats: Optional[List[str]] = None,
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search SEC datasets specifically.

        Args:
            query: Search query string
            formats: Filter by resource format
            rows: Number of results (max 50 for Community tier)

        Returns:
            DataFrame with SEC dataset metadata
        """
        return self.search_datasets(
            query=query,
            organization="sec-gov",
            formats=formats,
            rows=rows,
        )

    def search_banking_data(
        self,
        query: str = "*:*",
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search for banking datasets.

        Args:
            query: Search query (default: all banking datasets)
            rows: Number of results

        Returns:
            DataFrame with banking dataset metadata
        """
        search_query = f"bank {query}" if query != "*:*" else "bank banking FDIC"
        
        return self.search_datasets(
            query=search_query,
            organization="fdic-gov",
            rows=rows,
        )

    def search_public_debt_data(
        self,
        query: str = "*:*",
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search for public debt datasets.

        Args:
            query: Search query (default: all debt datasets)
            rows: Number of results

        Returns:
            DataFrame with public debt dataset metadata
        """
        search_query = f"public debt {query}" if query != "*:*" else "public debt treasury securities"
        
        return self.search_datasets(
            query=search_query,
            organization="treasury-gov",
            rows=rows,
        )

    def search_securities_data(
        self,
        query: str = "*:*",
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search for securities and market datasets.

        Args:
            query: Search query (default: all securities datasets)
            rows: Number of results

        Returns:
            DataFrame with securities dataset metadata
        """
        search_query = f"securities {query}" if query != "*:*" else "securities filings market"
        
        return self.search_datasets(
            query=search_query,
            organization="sec-gov",
            rows=rows,
        )

    def search_mortgage_data(
        self,
        query: str = "*:*",
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search for mortgage and lending datasets.

        Args:
            query: Search query (default: all mortgage datasets)
            rows: Number of results

        Returns:
            DataFrame with mortgage dataset metadata
        """
        search_query = f"mortgage {query}" if query != "*:*" else "mortgage HMDA lending"
        
        return self.search_datasets(
            query=search_query,
            rows=rows,
        )

    def search_consumer_finance_data(
        self,
        query: str = "*:*",
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search for consumer finance datasets.

        Args:
            query: Search query (default: all consumer finance datasets)
            rows: Number of results

        Returns:
            DataFrame with consumer finance dataset metadata
        """
        search_query = f"consumer {query}" if query != "*:*" else "consumer complaints credit"
        
        return self.search_datasets(
            query=search_query,
            organization="cfpb-gov",
            rows=rows,
        )

    def get_financial_categories(self) -> List[str]:
        """Get available financial dataset categories."""
        return list(self.POPULAR_DATASETS.keys())

    def __repr__(self) -> str:
        return (
            f"DataGovFinancialConnector("
            f"domain='{self.DOMAIN_NAME}', "
            f"organizations={self.DOMAIN_ORGANIZATIONS}, "
            f"max_results={self.MAX_RESULTS})"
        )
