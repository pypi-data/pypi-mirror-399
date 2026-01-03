# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Data.gov Economic Domain Connector - Community Tier

Pre-configured access to economic datasets from Data.gov, filtered to
BEA, BLS, Commerce, Treasury, and SBA agencies. Provides datasets on
GDP, employment, trade, income, and business statistics.

Domain Organizations:
- BEA (bea-gov): GDP, personal income, economic accounts
- BLS (bls-gov): Employment, wages, CPI, productivity
- Commerce (commerce-gov): Trade, business statistics
- Treasury (treasury-gov): Fiscal data, debt, revenue
- SBA (sba-gov): Small business, lending data

Key Dataset Categories:
- GDP: National, state, metro GDP data
- Employment: Jobs, unemployment, labor force
- Trade: Import/export, balance of trade
- Income: Personal income, wages, compensation
- Business: Small business, enterprise statistics

Usage:
    from krl_data_connectors.community.economic import DataGovEconomicConnector
    
    econ = DataGovEconomicConnector()
    
    # Search economic datasets (auto-filtered to BEA/BLS)
    results = econ.search_datasets("GDP growth")
    
    # Use agency-specific convenience methods
    bls_data = econ.search_bls_datasets("unemployment rates")
    gdp = econ.search_gdp_data("quarterly")
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from krl_data_connectors.community.civic.datagov_catalog import DataGovCatalogConnector


class DataGovEconomicConnector(DataGovCatalogConnector):
    """
    Data.gov Economic Domain Connector - Community Tier

    Pre-configured for BEA, BLS, Commerce, Treasury, and SBA datasets.
    All searches are automatically filtered to economic organizations
    unless overridden with a specific organization parameter.

    Limitations (Community Tier):
    - Maximum 50 results per search query
    - No bulk export functionality
    - Upgrade to DataGovEconomicFullConnector for unlimited access
    """

    _connector_name = "DataGov_Economic"

    # Domain configuration - auto-filter searches to these organizations
    DOMAIN_ORGANIZATIONS: List[str] = [
        "bea-gov",          # Bureau of Economic Analysis
        "bls-gov",          # Bureau of Labor Statistics
        "commerce-gov",     # Department of Commerce
        "treasury-gov",     # Department of Treasury
        "sba-gov",          # Small Business Administration
    ]
    
    DOMAIN_TAGS: List[str] = [
        "economy",
        "gdp",
        "employment",
        "trade",
        "business",
        "income",
        "wages",
    ]
    
    DOMAIN_NAME: str = "Economic"

    # Override popular datasets with economic focus
    POPULAR_DATASETS: Dict[str, List[str]] = {
        "gdp": [
            "gross-domestic-product",
            "real-gdp-by-state",
            "gdp-by-metro-area",
            "quarterly-gdp",
            "gdp-by-industry",
        ],
        "employment": [
            "current-employment-statistics",
            "local-area-unemployment",
            "quarterly-census-employment-wages",
            "job-openings-labor-turnover",
            "occupational-employment-statistics",
        ],
        "trade": [
            "international-trade",
            "trade-in-goods-services",
            "export-statistics",
            "import-statistics",
            "trade-balance",
        ],
        "income": [
            "personal-income-by-state",
            "median-household-income",
            "per-capita-income",
            "wage-statistics",
            "compensation-costs",
        ],
        "business": [
            "business-dynamics-statistics",
            "small-business-lending",
            "business-formation-statistics",
            "county-business-patterns",
            "nonemployer-statistics",
        ],
    }

    # Economic organizations with descriptions
    WHITELISTED_ORGANIZATIONS: Dict[str, str] = {
        "bea-gov": "Bureau of Economic Analysis",
        "bls-gov": "Bureau of Labor Statistics",
        "commerce-gov": "Department of Commerce",
        "treasury-gov": "Department of the Treasury",
        "sba-gov": "Small Business Administration",
        "census-gov": "U.S. Census Bureau",
    }

    def search_bea_datasets(
        self,
        query: str,
        formats: Optional[List[str]] = None,
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search BEA datasets specifically.

        Args:
            query: Search query string
            formats: Filter by resource format
            rows: Number of results (max 50 for Community tier)

        Returns:
            DataFrame with BEA dataset metadata
        """
        return self.search_datasets(
            query=query,
            organization="bea-gov",
            formats=formats,
            rows=rows,
        )

    def search_bls_datasets(
        self,
        query: str,
        formats: Optional[List[str]] = None,
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search BLS datasets specifically.

        Args:
            query: Search query string
            formats: Filter by resource format
            rows: Number of results (max 50 for Community tier)

        Returns:
            DataFrame with BLS dataset metadata
        """
        return self.search_datasets(
            query=query,
            organization="bls-gov",
            formats=formats,
            rows=rows,
        )

    def search_gdp_data(
        self,
        query: str = "*:*",
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search for GDP and economic output datasets.

        Args:
            query: Search query (default: all GDP datasets)
            rows: Number of results

        Returns:
            DataFrame with GDP dataset metadata
        """
        search_query = f"GDP {query}" if query != "*:*" else "gross domestic product GDP"
        
        return self.search_datasets(
            query=search_query,
            rows=rows,
        )

    def search_employment_data(
        self,
        query: str = "*:*",
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search for employment and labor datasets.

        Args:
            query: Search query (default: all employment datasets)
            rows: Number of results

        Returns:
            DataFrame with employment dataset metadata
        """
        search_query = f"employment jobs {query}" if query != "*:*" else "employment unemployment labor"
        
        return self.search_datasets(
            query=search_query,
            rows=rows,
        )

    def search_trade_data(
        self,
        query: str = "*:*",
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search for international trade datasets.

        Args:
            query: Search query (default: all trade datasets)
            rows: Number of results

        Returns:
            DataFrame with trade dataset metadata
        """
        search_query = f"trade {query}" if query != "*:*" else "international trade import export"
        
        return self.search_datasets(
            query=search_query,
            rows=rows,
        )

    def search_small_business_data(
        self,
        query: str = "*:*",
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search for small business datasets.

        Args:
            query: Search query (default: all small business datasets)
            rows: Number of results

        Returns:
            DataFrame with small business dataset metadata
        """
        search_query = f"small business {query}" if query != "*:*" else "small business SBA lending"
        
        return self.search_datasets(
            query=search_query,
            organization="sba-gov",
            rows=rows,
        )

    def search_income_data(
        self,
        query: str = "*:*",
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search for income and wage datasets.

        Args:
            query: Search query (default: all income datasets)
            rows: Number of results

        Returns:
            DataFrame with income dataset metadata
        """
        search_query = f"income wages {query}" if query != "*:*" else "personal income wages compensation"
        
        return self.search_datasets(
            query=search_query,
            rows=rows,
        )

    def get_economic_categories(self) -> List[str]:
        """Get available economic dataset categories."""
        return list(self.POPULAR_DATASETS.keys())

    def __repr__(self) -> str:
        return (
            f"DataGovEconomicConnector("
            f"domain='{self.DOMAIN_NAME}', "
            f"organizations={self.DOMAIN_ORGANIZATIONS}, "
            f"max_results={self.MAX_RESULTS})"
        )
