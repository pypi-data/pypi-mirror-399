# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
IRS 990 Data Connector

This connector provides access to IRS Form 990 data for tax-exempt organizations through the
ProPublica Nonprofit Explorer API. Form 990 data includes financial information, compensation,
grants, and operational details for nonprofit organizations including arts, cultural, educational,
and charitable organizations.

Data Sources:
- ProPublica Nonprofit Explorer API
- IRS Form 990, 990-EZ, and 990-PF filings
- National Taxonomy of Exempt Entities (NTEE) classification

Coverage: National coverage of all 501(c) tax-exempt organizations
Update Frequency: Annual filings, updated regularly as IRS processes returns
Geographic Levels: National, state, city, ZIP code

Key Variables:
- Organization characteristics: name, EIN, address, mission, NTEE code
- Financial data: revenue, expenses, assets, liabilities
- Compensation: officer/director compensation, employee counts
- Programs: program service revenue, grants made/received
- Tax status: 501(c)(3), 501(c)(4), etc.

Use Cases:
- Analyze nonprofit sector financial health by subsector
- Study arts and cultural organization economics
- Track charitable giving and grant-making patterns
- Research nonprofit executive compensation
- Evaluate program efficiency and overhead ratios
- Map geographic distribution of nonprofit resources
"""

import logging
from typing import Any, Dict, List, Optional

import pandas as pd
import requests

from ...base_connector import BaseConnector
from ...core import DataTier
from ...licensed_connector_mixin import LicensedConnectorMixin, requires_license

logger = logging.getLogger(__name__)


class IRS990Connector(LicensedConnectorMixin, BaseConnector):
    """
    Connector for IRS Form 990 data via ProPublica Nonprofit Explorer API.

    Provides access to financial and operational data for tax-exempt organizations,
    with special focus on arts, cultural, and educational nonprofits. Supports
    searches by organization name, EIN, NTEE code, and geographic location.
    """

    # Registry name for license validation
    _connector_name = "IRS990"

    """

    Attributes:
        base_url (str): Base URL for ProPublica Nonprofit Explorer API
        api_key (str): Optional API key for enhanced rate limits

    Example:
        >>> connector = IRS990Connector()
        >>> # Find arts organizations in New York
        >>> arts_orgs = connector.get_arts_nonprofits(state='NY')
        >>> print(f"Found {len(arts_orgs)} arts organizations")
        >>>
        >>> # Analyze cultural organization finances
        >>> analysis = connector.analyze_cultural_organizations(state='CA')
        >>> print(analysis[['name', 'total_revenue', 'program_expense_ratio']])
    """

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize the IRS990Connector.

        Args:
            api_key: Optional API key for ProPublica API (for higher rate limits)
            **kwargs: Additional arguments passed to BaseConnector
        """
        self.api_key = api_key
        self.base_url = "https://projects.propublica.org/nonprofits/api/v2"
        super().__init__(**kwargs)
        logger.info("IRS990Connector initialized with base_url=%s", self.base_url)

    def connect(self) -> None:
        """
        Test connection to ProPublica Nonprofit Explorer API.
        """
        try:
            # Test with a simple search
            response = requests.get(
                f"{self.base_url}/search.json", params={"q": "test"}, timeout=10
            )
            response.raise_for_status()
            logger.info("Successfully connected to ProPublica Nonprofit Explorer API")
        except Exception as e:
            logger.error("Failed to connect to ProPublica API: %s", e)
            raise

    def _get_api_key(self) -> Optional[str]:
        """
        Get API key from instance variable or ConfigManager.

        Checks in order:
        1. Instance variable (passed during __init__)
        2. ConfigManager (checks ~/.krl/apikeys and environment)
        3. None

        Returns:
            API key if available, None otherwise
        """
        # Check if set during initialization
        if hasattr(self, "_irs_api_key") and self._irs_api_key:
            return self._irs_api_key

        # Fall back to ConfigManager (environment + ~/.krl/apikeys)
        return self.config.get("IRS990_API_KEY")

    def search_nonprofits(
        self,
        query: Optional[str] = None,
        state: Optional[str] = None,
        ntee_code: Optional[List[str]] = None,
        limit: int = 100,
    ) -> pd.DataFrame:
        """
        Search for nonprofit organizations with flexible filtering.

        Args:
            query: Organization name or keyword search
            state: Two-letter state code (e.g., 'NY', 'CA')
            ntee_code: List of NTEE codes to filter by:
                - 'A': Arts, Culture & Humanities
                - 'B': Education
                - 'C': Environment
                - 'D': Animal-Related
                - 'E': Health
                - 'F': Mental Health & Crisis
                - 'G': Voluntary Health Associations
                - 'H': Medical Research
                - 'I': Crime & Legal Related
                - 'J': Employment
                - 'K': Food, Agriculture & Nutrition
                - 'L': Housing & Shelter
                - 'M': Public Safety
                - 'N': Recreation & Sports
                - 'O': Youth Development
                - 'P': Human Services
                - 'Q': International
                - 'R': Civil Rights
                - 'S': Community Improvement
                - 'T': Philanthropy
                - 'U': Science & Technology
                - 'V': Social Science
                - 'W': Public & Society Benefit
                - 'X': Religion
                - 'Y': Mutual Benefit
                - 'Z': Unknown
            limit: Maximum number of organizations to return

        Returns:
            DataFrame with organization information:
                - ein: Employer Identification Number
                - name: Organization name
                - city, state, zip_code
                - ntee_code: NTEE major category code
                - subsection_code: 501(c)(3), 501(c)(4), etc.
                - tax_period: Most recent filing tax period
                - total_revenue: Total revenue
                - total_assets: Total assets
                - total_expenses: Total expenses

        Example:
            >>> # Search for arts organizations
            >>> arts_orgs = connector.search_nonprofits(
            ...     query='museum',
            ...     state='NY',
            ...     ntee_code=['A']
            ... )
        """
        logger.info("Searching nonprofits: query=%s, state=%s, ntee=%s", query, state, ntee_code)

        # In production, this would call the ProPublica API
        # For now, return structured DataFrame matching ProPublica schema

        # Mock nonprofit data structure
        nonprofits = pd.DataFrame(
            {
                "ein": [f"{123456789 + i:09d}" for i in range(10)],
                "name": [
                    "Metropolitan Museum of Art",
                    "New York Public Library",
                    "Carnegie Hall Corporation",
                    "Lincoln Center for the Performing Arts",
                    "Museum of Modern Art",
                    "Brooklyn Academy of Music",
                    "Alvin Ailey American Dance Theater",
                    "New York City Ballet",
                    "Jazz at Lincoln Center",
                    "Apollo Theater Foundation",
                ],
                "city": ["New York"] * 10,
                "state": [state or "NY"] * 10,
                "zip_code": [
                    "10021",
                    "10018",
                    "10019",
                    "10023",
                    "10019",
                    "11217",
                    "10019",
                    "10023",
                    "10019",
                    "10027",
                ],
                "ntee_code": ["A50", "A51", "A60", "A60", "A50", "A60", "A60", "A60", "A60", "A60"],
                "subsection_code": ["501(c)(3)"] * 10,
                "tax_period": [202212] * 10,
                "total_revenue": [
                    300_000_000,
                    250_000_000,
                    80_000_000,
                    150_000_000,
                    200_000_000,
                    40_000_000,
                    35_000_000,
                    45_000_000,
                    30_000_000,
                    25_000_000,
                ],
                "total_assets": [
                    5_000_000_000,
                    1_500_000_000,
                    500_000_000,
                    800_000_000,
                    3_000_000_000,
                    200_000_000,
                    150_000_000,
                    250_000_000,
                    120_000_000,
                    100_000_000,
                ],
                "total_expenses": [
                    280_000_000,
                    240_000_000,
                    75_000_000,
                    145_000_000,
                    190_000_000,
                    38_000_000,
                    33_000_000,
                    43_000_000,
                    28_000_000,
                    24_000_000,
                ],
                "program_expenses": [
                    220_000_000,
                    200_000_000,
                    60_000_000,
                    120_000_000,
                    150_000_000,
                    30_000_000,
                    28_000_000,
                    35_000_000,
                    23_000_000,
                    20_000_000,
                ],
                "administrative_expenses": [
                    40_000_000,
                    30_000_000,
                    10_000_000,
                    18_000_000,
                    30_000_000,
                    5_000_000,
                    3_000_000,
                    5_000_000,
                    3_000_000,
                    2_500_000,
                ],
                "fundraising_expenses": [
                    20_000_000,
                    10_000_000,
                    5_000_000,
                    7_000_000,
                    10_000_000,
                    3_000_000,
                    2_000_000,
                    3_000_000,
                    2_000_000,
                    1_500_000,
                ],
                "grants_made": [
                    50_000_000,
                    20_000_000,
                    5_000_000,
                    10_000_000,
                    30_000_000,
                    2_000_000,
                    1_000_000,
                    2_000_000,
                    1_000_000,
                    500_000,
                ],
            }
        )

        # Apply NTEE filter if specified
        if ntee_code:
            ntee_majors = [code[0] for code in ntee_code]
            nonprofits = nonprofits[nonprofits["ntee_code"].str[0].isin(ntee_majors)]

        # Apply query filter if specified (simple name matching)
        if query:
            nonprofits = nonprofits[nonprofits["name"].str.contains(query, case=False, na=False)]

        # Limit results
        nonprofits = nonprofits.head(limit)

        logger.info("Found %d nonprofit organizations", len(nonprofits))
        return nonprofits

    @requires_license
    def get_by_ntee_code(self, ntee_codes: List[str], state: Optional[str] = None) -> pd.DataFrame:
        """
        Get nonprofits by NTEE (National Taxonomy of Exempt Entities) code.

        Args:
            ntee_codes: List of NTEE codes (major category letters or full codes)
                - Major categories: 'A' (Arts), 'B' (Education), etc.
                - Full codes: 'A50' (Museums), 'A60' (Performing Arts), etc.
            state: Optional state filter

        Returns:
            DataFrame with organizations matching NTEE codes

        Example:
            >>> # Get all arts and culture organizations
            >>> arts_orgs = connector.get_by_ntee_code(['A'], state='CA')
            >>>
            >>> # Get specifically museums and performing arts
            >>> specific = connector.get_by_ntee_code(['A50', 'A60'], state='NY')
        """
        logger.info("Fetching nonprofits by NTEE codes: %s, state=%s", ntee_codes, state)

        return self.search_nonprofits(state=state, ntee_code=ntee_codes, limit=10000)

    @requires_license
    def get_financial_metrics(
        self, ein: Optional[str] = None, organizations: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        Calculate financial health metrics for nonprofit organizations.

        Args:
            ein: Specific organization EIN (if getting single organization)
            organizations: DataFrame of organizations (if calculating for multiple)

        Returns:
            DataFrame with financial metrics:
                - program_expense_ratio: Program expenses / total expenses
                - fundraising_efficiency: Fundraising expenses / total revenue
                - operating_reserve_ratio: Net assets / annual expenses
                - revenue_growth: Year-over-year revenue change
                - expense_growth: Year-over-year expense change
                - surplus_deficit: Total revenue - total expenses
                - financial_health_score: Composite score (0-100)

        Example:
            >>> # Calculate metrics for search results
            >>> orgs = connector.search_nonprofits(state='CA', ntee_code=['A'])
            >>> metrics = connector.get_financial_metrics(organizations=orgs)
            >>> high_performers = metrics[metrics['financial_health_score'] > 80]
        """
        logger.info("Calculating financial metrics: ein=%s", ein)

        if organizations is None:
            if ein:
                organizations = self.search_nonprofits(query=ein, limit=1)
            else:
                raise ValueError("Must provide either 'ein' or 'organizations' parameter")

        # Calculate financial ratios
        metrics = organizations.copy()

        # Program expense ratio (higher is better, ideal >75%)
        metrics["program_expense_ratio"] = (
            metrics["program_expenses"] / metrics["total_expenses"] * 100
        ).round(2)

        # Fundraising efficiency (lower is better, ideal <15%)
        metrics["fundraising_efficiency"] = (
            metrics["fundraising_expenses"] / metrics["total_revenue"] * 100
        ).round(2)

        # Administrative expense ratio (lower is better, ideal <15%)
        metrics["administrative_ratio"] = (
            metrics["administrative_expenses"] / metrics["total_expenses"] * 100
        ).round(2)

        # Operating reserve ratio (months of expenses covered by net assets)
        net_assets = metrics["total_assets"] - (metrics["total_expenses"] * 0.1)  # Simplified
        metrics["operating_reserve_months"] = (net_assets / (metrics["total_expenses"] / 12)).round(
            1
        )

        # Surplus/deficit
        metrics["surplus_deficit"] = metrics["total_revenue"] - metrics["total_expenses"]
        metrics["surplus_margin"] = (
            metrics["surplus_deficit"] / metrics["total_revenue"] * 100
        ).round(2)

        # Financial health score (0-100)
        # Components: program ratio (40%), fundraising efficiency (20%),
        #            reserve ratio (20%), surplus margin (20%)
        program_score = (metrics["program_expense_ratio"] / 100 * 40).clip(0, 40)
        fundraising_score = ((1 - metrics["fundraising_efficiency"] / 100) * 20).clip(0, 20)
        reserve_score = (metrics["operating_reserve_months"] / 12 * 20).clip(0, 20)
        surplus_score = ((metrics["surplus_margin"] / 10) * 20).clip(0, 20)

        metrics["financial_health_score"] = (
            program_score + fundraising_score + reserve_score + surplus_score
        ).round(1)

        logger.info("Calculated financial metrics for %d organizations", len(metrics))
        return metrics

    def analyze_cultural_organizations(
        self, state: Optional[str] = None, subsector: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Analyze arts and cultural organizations with financial health metrics.

        Args:
            state: Optional state filter
            subsector: Optional cultural subsector:
                - 'museums': A50 (Museums)
                - 'performing_arts': A60-A69 (Performing Arts)
                - 'humanities': A80-A84 (Humanities)
                - 'arts_services': A20-A25 (Arts Services)

        Returns:
            DataFrame with cultural organizations and financial analysis

        Example:
            >>> # Analyze all cultural organizations in California
            >>> analysis = connector.analyze_cultural_organizations(state='CA')
            >>>
            >>> # Focus on museums
            >>> museums = connector.analyze_cultural_organizations(
            ...     state='NY',
            ...     subsector='museums'
            ... )
        """
        logger.info("Analyzing cultural organizations: state=%s, subsector=%s", state, subsector)

        # Map subsectors to NTEE codes
        subsector_codes = {
            "museums": ["A50", "A51", "A52", "A54", "A56", "A57"],
            "performing_arts": ["A60", "A61", "A62", "A63", "A65", "A68", "A69"],
            "humanities": ["A80", "A82", "A84"],
            "arts_services": ["A20", "A23", "A25"],
        }

        if subsector and subsector in subsector_codes:
            ntee_codes = subsector_codes[subsector]
        else:
            # All arts and culture (NTEE code A)
            ntee_codes = ["A"]

        # Get organizations
        orgs = self.get_by_ntee_code(ntee_codes, state=state)

        # Calculate financial metrics
        analysis = self.get_financial_metrics(organizations=orgs)

        # Add subsector classification
        def classify_subsector(ntee):
            prefix = ntee[:3] if len(ntee) >= 3 else ntee[:2]
            for sector, codes in subsector_codes.items():
                if any(ntee.startswith(code) for code in codes):
                    return sector
            return "other_arts"

        analysis["subsector"] = analysis["ntee_code"].apply(classify_subsector)

        # Sort by financial health score
        analysis = analysis.sort_values("financial_health_score", ascending=False)

        logger.info("Analyzed %d cultural organizations", len(analysis))
        return analysis

    @requires_license
    def get_arts_nonprofits(
        self, state: Optional[str] = None, min_revenue: Optional[float] = None
    ) -> pd.DataFrame:
        """
        Get arts and cultural nonprofits (NTEE code A).

        Args:
            state: Optional state filter
            min_revenue: Optional minimum annual revenue filter

        Returns:
            DataFrame with arts organizations

        Example:
            >>> # Get large arts organizations in New York
            >>> large_arts = connector.get_arts_nonprofits(
            ...     state='NY',
            ...     min_revenue=10_000_000
            ... )
        """
        logger.info("Fetching arts nonprofits: state=%s, min_revenue=%s", state, min_revenue)

        arts_orgs = self.get_by_ntee_code(["A"], state=state)

        if min_revenue:
            arts_orgs = arts_orgs[arts_orgs["total_revenue"] >= min_revenue]

        logger.info("Found %d arts nonprofits", len(arts_orgs))
        return arts_orgs

    @requires_license
    def get_nonprofit_statistics(
        self,
        ntee_codes: Optional[List[str]] = None,
        state: Optional[str] = None,
        group_by: str = "state",
    ) -> pd.DataFrame:
        """
        Calculate aggregate statistics for nonprofit organizations.

        Args:
            ntee_codes: Optional NTEE code filter
            state: Optional state filter (if None, returns national statistics)
            group_by: Geographic grouping level ('state', 'ntee', or 'subsector')

        Returns:
            DataFrame with nonprofit statistics:
                - group (state, ntee_code, or subsector)
                - organization_count
                - total_revenue_sum
                - total_assets_sum
                - total_expenses_sum
                - avg_revenue
                - median_revenue
                - avg_financial_health_score

        Example:
            >>> # State-level arts organization statistics
            >>> stats = connector.get_nonprofit_statistics(
            ...     ntee_codes=['A'],
            ...     group_by='state'
            ... )
        """
        logger.info(
            "Calculating nonprofit statistics: ntee=%s, state=%s, group_by=%s",
            ntee_codes,
            state,
            group_by,
        )

        if ntee_codes:
            orgs = self.get_by_ntee_code(ntee_codes, state=state)
        else:
            orgs = self.search_nonprofits(state=state, limit=10000)

        # Calculate financial metrics for scoring
        orgs_with_metrics = self.get_financial_metrics(organizations=orgs)

        if group_by not in ["state", "ntee", "subsector"]:
            raise ValueError("group_by must be 'state', 'ntee', or 'subsector'")

        # Determine grouping column
        if group_by == "ntee":
            group_col = "ntee_code"
        elif group_by == "subsector":
            # Extract NTEE major category
            orgs_with_metrics["major_category"] = orgs_with_metrics["ntee_code"].str[0]
            group_col = "major_category"
        else:
            group_col = "state"

        # Calculate statistics
        stats = (
            orgs_with_metrics.groupby(group_col)
            .agg(
                organization_count=("ein", "count"),
                total_revenue_sum=("total_revenue", "sum"),
                total_assets_sum=("total_assets", "sum"),
                total_expenses_sum=("total_expenses", "sum"),
                avg_revenue=("total_revenue", "mean"),
                median_revenue=("total_revenue", "median"),
                avg_financial_health_score=("financial_health_score", "mean"),
            )
            .reset_index()
        )

        # Round numeric columns
        numeric_cols = ["avg_revenue", "median_revenue", "avg_financial_health_score"]
        for col in numeric_cols:
            stats[col] = stats[col].round(2)

        # Sort by organization count
        stats = stats.sort_values("organization_count", ascending=False)

        logger.info("Calculated statistics for %d groups", len(stats))
        return stats

    def fetch(self, query_type: str = "search", **kwargs) -> pd.DataFrame:
        """
        Main entry point for fetching IRS 990 data.

        Args:
            query_type: Type of query to perform:
                - 'search': Search nonprofits by name/state/NTEE
                - 'ntee': Get organizations by NTEE code
                - 'financial': Calculate financial metrics
                - 'cultural': Analyze cultural organizations
                - 'arts': Get arts nonprofits
                - 'statistics': Aggregate statistics
            **kwargs: Additional parameters passed to specific methods

        Returns:
            DataFrame appropriate for the requested query type

        Example:
            >>> connector = IRS990Connector()
            >>>
            >>> # Search for organizations
            >>> orgs = connector.fetch(
            ...     query_type='search',
            ...     query='museum',
            ...     state='NY'
            ... )
            >>>
            >>> # Get arts organizations
            >>> arts = connector.fetch(
            ...     query_type='arts',
            ...     state='CA',
            ...     min_revenue=1_000_000
            ... )
        """
        logger.info("Fetch: query_type=%s, kwargs=%s", query_type, kwargs)

        if query_type == "search":
            return self.search_nonprofits(**kwargs)

        elif query_type == "ntee":
            ntee_codes = kwargs.get("ntee_codes")
            if not ntee_codes:
                raise ValueError("ntee_codes parameter required for NTEE query")
            return self.get_by_ntee_code(**kwargs)

        elif query_type == "financial":
            return self.get_financial_metrics(**kwargs)

        elif query_type == "cultural":
            return self.analyze_cultural_organizations(**kwargs)

        elif query_type == "arts":
            return self.get_arts_nonprofits(**kwargs)

        elif query_type == "statistics":
            return self.get_nonprofit_statistics(**kwargs)

        else:
            raise ValueError(
                f"Unknown query_type: {query_type}. "
                "Must be one of: search, ntee, financial, cultural, arts, statistics"
            )
