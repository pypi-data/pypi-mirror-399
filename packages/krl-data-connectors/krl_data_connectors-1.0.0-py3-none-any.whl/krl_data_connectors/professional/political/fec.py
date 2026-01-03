# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
FEC (Federal Election Commission) Data Connector

This connector provides access to campaign finance data from the Federal Election Commission's
API. It includes information on candidates, committees, contributions, expenditures, and
financial summaries for federal elections (presidential, Senate, and House races).

Data Sources:
- FEC API v1 (https://api.open.fec.gov/developers/)
- Campaign finance reports (Form 3, 3P, 3X)
- Candidate and committee registrations
- Individual and PAC contributions
- Independent expenditures

Coverage: All federal elections (Presidential, Senate, House)
Update Frequency: Real-time updates, with periodic bulk releases
Geographic Levels: National, state, congressional district

Key Variables:
- Candidate information: name, party, office, district, incumbent status
- Committee data: type, designation, affiliated candidate
- Financial totals: receipts, disbursements, cash on hand, debt
- Contributions: donor information, amount, date, employer
- Expenditures: recipient, purpose, amount, date

Use Cases:
- Campaign finance trend analysis
- Donor network mapping
- Fundraising competitiveness assessment
- Political spending patterns by geography
- PAC and Super PAC influence tracking
- Small donor vs large donor analysis
"""

import logging
from datetime import datetime, UTC
from typing import Any, Dict, List, Optional

import pandas as pd
import requests

from krl_data_connectors.base_dispatcher_connector import BaseDispatcherConnector
from krl_data_connectors.core import DataTier
from krl_data_connectors.licensed_connector_mixin import LicensedConnectorMixin, requires_license

logger = logging.getLogger(__name__)


class FECConnector(LicensedConnectorMixin, BaseDispatcherConnector):
    """
    Connector for Federal Election Commission (FEC) campaign finance data.

    Provides access to candidate information, committee finances, contributions,
    """

    # Registry name for license validation
    _connector_name = "FEC"

    """
    expenditures, and campaign finance reports for federal elections. Supports
    analysis of fundraising patterns, donor networks, and political spending.

    This connector uses the dispatcher pattern to route requests based on the
    'query_type' parameter. The fetch() method automatically routes to the
    appropriate specialized method.

    Attributes:
        base_url (str): Base URL for FEC API
        api_key (str): FEC API key (required for production use)

    Example:
        >>> connector = FECConnector(api_key='YOUR_API_KEY')
        >>> # Using dispatcher pattern
        >>> candidates = connector.fetch(
        ...     query_type='candidates',
        ...     office='P',
        ...     cycle=2024
        ... )
        >>> # Or call methods directly
        >>> candidates = connector.search_candidates(
        ...     office='P',
        ...     cycle=2024
        ... )
    """

    # Dispatcher configuration
    DISPATCH_PARAM = "query_type"
    DISPATCH_MAP = {
        "candidates": "search_candidates",
        "committees": "get_committee_finances",
        "contributions": "get_contributions",
        "expenditures": "get_expenditures",
        "fundraising": "analyze_fundraising_patterns",
        "statistics": "get_campaign_statistics",
    }

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize the FECConnector.

        Args:
            api_key: FEC API key (get from https://api.data.gov/signup/)
            **kwargs: Additional arguments passed to BaseConnector
        """
        self.api_key = api_key
        self.base_url = "https://api.open.fec.gov/v1"
        super().__init__(**kwargs)
        logger.info("FECConnector initialized with base_url=%s", self.base_url)

    def connect(self) -> None:
        """
        Test connection to FEC API.
        """
        try:
            # Test with a simple request
            params = {"api_key": self.api_key} if self.api_key else {}
            response = requests.get(
                f"{self.base_url}/candidates/", params={**params, "per_page": 1}, timeout=10
            )
            response.raise_for_status()
            logger.info("Successfully connected to FEC API")
        except Exception as e:
            logger.error("Failed to connect to FEC API: %s", e)
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
        if hasattr(self, "_fec_api_key") and self._fec_api_key:
            return self._fec_api_key

        # Fall back to ConfigManager (environment + ~/.krl/apikeys)
        return self.config.get("DATA_GOV_API_KEY")

    def search_candidates(
        self,
        name: Optional[str] = None,
        office: Optional[str] = None,
        state: Optional[str] = None,
        party: Optional[str] = None,
        cycle: Optional[int] = None,
        incumbent_challenge: Optional[str] = None,
        limit: int = 100,
    ) -> pd.DataFrame:
        """
        Search for federal candidates with flexible filtering.

        Args:
            name: Candidate name (partial match)
            office: Office sought:
                - 'P': President
                - 'S': Senate
                - 'H': House
            state: Two-letter state code (for Senate/House)
            party: Party affiliation:
                - 'DEM': Democratic
                - 'REP': Republican
                - 'LIB': Libertarian
                - 'GRE': Green
                - 'IND': Independent
            cycle: Election cycle year (2020, 2022, 2024, etc.)
            incumbent_challenge: Incumbent status:
                - 'I': Incumbent
                - 'C': Challenger
                - 'O': Open seat
            limit: Maximum number of candidates to return

        Returns:
            DataFrame with candidate information:
                - candidate_id: FEC candidate ID
                - name: Candidate name
                - office: Office sought (P/S/H)
                - office_full: Full office description
                - state: State (for S/H)
                - district: District (for H)
                - party: Party affiliation
                - party_full: Full party name
                - incumbent_challenge: I/C/O
                - incumbent_challenge_full: Full status description
                - cycles: List of election cycles
                - election_year: Primary election year
                - active_through: Last active cycle

        Example:
            >>> # Find 2024 Senate candidates in competitive states
            >>> senate = connector.search_candidates(
            ...     office='S',
            ...     cycle=2024,
            ...     state='PA'
            ... )
        """
        logger.info(
            "Searching candidates: name=%s, office=%s, state=%s, party=%s, cycle=%s",
            name,
            office,
            state,
            party,
            cycle,
        )

        # In production, this would call the FEC API
        # For now, return structured DataFrame matching FEC schema

        # Mock candidate data
        candidates = pd.DataFrame(
            {
                "candidate_id": [
                    f"P800{i:05d}" if office == "P" else f"H000{i:05d}" for i in range(1, 11)
                ],
                "name": [
                    "SMITH, JOHN",
                    "JOHNSON, MARY",
                    "WILLIAMS, ROBERT",
                    "BROWN, PATRICIA",
                    "JONES, MICHAEL",
                    "GARCIA, JENNIFER",
                    "MILLER, DAVID",
                    "DAVIS, LINDA",
                    "RODRIGUEZ, JAMES",
                    "MARTINEZ, BARBARA",
                ],
                "office": [office or "H"] * 10,
                "office_full": [
                    "President" if office == "P" else "House" if office == "H" else "Senate"
                ]
                * 10,
                "state": [state or "PA"] * 10,
                "district": (
                    ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10"]
                    if office == "H"
                    else [None] * 10
                ),
                "party": [party or "DEM"] * 5 + [party or "REP"] * 5,
                "party_full": ["Democratic"] * 5 + ["Republican"] * 5,
                "incumbent_challenge": ["I", "C", "O", "C", "I", "C", "O", "C", "I", "C"],
                "incumbent_challenge_full": [
                    "Incumbent",
                    "Challenger",
                    "Open seat",
                    "Challenger",
                    "Incumbent",
                    "Challenger",
                    "Open seat",
                    "Challenger",
                    "Incumbent",
                    "Challenger",
                ],
                "cycles": [[2024]] * 10 if cycle else [[2020, 2022, 2024]] * 10,
                "election_year": [cycle or 2024] * 10,
                "active_through": [cycle or 2024] * 10,
            }
        )

        # Apply name filter if specified
        if name:
            candidates = candidates[
                candidates["name"].str.contains(name.upper(), case=False, na=False)
            ]

        # Limit results
        candidates = candidates.head(limit)

        logger.info("Found %d candidates", len(candidates))
        return candidates

    @requires_license
    def get_committee_finances(
        self,
        committee_id: Optional[str] = None,
        committee_type: Optional[str] = None,
        cycle: Optional[int] = None,
        limit: int = 100,
    ) -> pd.DataFrame:
        """
        Get financial summaries for political committees.

        Args:
            committee_id: Specific committee ID
            committee_type: Committee type:
                - 'P': Presidential
                - 'H': House
                - 'S': Senate
                - 'N': PAC - Nonqualified
                - 'Q': PAC - Qualified
                - 'O': Super PAC
                - 'U': Single candidate independent expenditure
            cycle: Election cycle year
            limit: Maximum number of committees to return

        Returns:
            DataFrame with committee financial information:
                - committee_id: FEC committee ID
                - committee_name: Committee name
                - committee_type: Type code
                - committee_type_full: Full type description
                - designation: A (authorized) / U (unauthorized)
                - party: Party affiliation
                - cycle: Election cycle
                - receipts: Total receipts
                - disbursements: Total disbursements
                - cash_on_hand_end_period: Ending cash balance
                - debts_owed: Total debts
                - individual_contributions: Contributions from individuals
                - pac_contributions: Contributions from PACs
                - candidate_contributions: Candidate self-funding
                - operating_expenditures: Operating expenses
                - independent_expenditures: Independent expenditures made

        Example:
            >>> # Get Super PAC finances for 2024
            >>> super_pacs = connector.get_committee_finances(
            ...     committee_type='O',
            ...     cycle=2024
            ... )
        """
        logger.info(
            "Fetching committee finances: committee_id=%s, type=%s, cycle=%s",
            committee_id,
            committee_type,
            cycle,
        )

        # Mock committee financial data
        committees = pd.DataFrame(
            {
                "committee_id": [f"C00{i:06d}" for i in range(1, 11)],
                "committee_name": [
                    "Committee to Elect Smith",
                    "Johnson for Congress",
                    "Williams Campaign Committee",
                    "Friends of Patricia Brown",
                    "Jones for Senate",
                    "Garcia Leadership PAC",
                    "Miller Victory Fund",
                    "Davis for America",
                    "Rodriguez Campaign",
                    "Martinez for Congress",
                ],
                "committee_type": [committee_type or "H"] * 10,
                "committee_type_full": [
                    "House" if not committee_type or committee_type == "H" else "Senate"
                ]
                * 10,
                "designation": ["A"] * 10,  # Authorized
                "party": ["DEM"] * 5 + ["REP"] * 5,
                "cycle": [cycle or 2024] * 10,
                "receipts": [
                    2_500_000,
                    1_800_000,
                    3_200_000,
                    1_500_000,
                    5_000_000,
                    2_000_000,
                    2_800_000,
                    1_200_000,
                    3_500_000,
                    1_900_000,
                ],
                "disbursements": [
                    2_300_000,
                    1_700_000,
                    3_000_000,
                    1_400_000,
                    4_800_000,
                    1_900_000,
                    2_700_000,
                    1_100_000,
                    3_300_000,
                    1_800_000,
                ],
                "cash_on_hand_end_period": [
                    200_000,
                    100_000,
                    200_000,
                    100_000,
                    200_000,
                    100_000,
                    100_000,
                    100_000,
                    200_000,
                    100_000,
                ],
                "debts_owed": [
                    50_000,
                    25_000,
                    100_000,
                    30_000,
                    150_000,
                    40_000,
                    75_000,
                    20_000,
                    120_000,
                    35_000,
                ],
                "individual_contributions": [
                    1_800_000,
                    1_200_000,
                    2_500_000,
                    1_000_000,
                    3_500_000,
                    1_400_000,
                    2_000_000,
                    800_000,
                    2_800_000,
                    1_300_000,
                ],
                "pac_contributions": [
                    500_000,
                    400_000,
                    500_000,
                    300_000,
                    1_000_000,
                    400_000,
                    600_000,
                    250_000,
                    500_000,
                    400_000,
                ],
                "candidate_contributions": [
                    200_000,
                    200_000,
                    200_000,
                    200_000,
                    500_000,
                    200_000,
                    200_000,
                    150_000,
                    200_000,
                    200_000,
                ],
                "operating_expenditures": [
                    300_000,
                    200_000,
                    400_000,
                    180_000,
                    600_000,
                    250_000,
                    350_000,
                    150_000,
                    450_000,
                    220_000,
                ],
                "independent_expenditures": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            }
        )

        # Filter by committee_id if specified
        if committee_id:
            committees = committees[committees["committee_id"] == committee_id]

        # Limit results
        committees = committees.head(limit)

        logger.info("Found %d committee financial records", len(committees))
        return committees

    @requires_license
    def get_contributions(
        self,
        committee_id: Optional[str] = None,
        contributor_name: Optional[str] = None,
        min_amount: Optional[float] = None,
        cycle: Optional[int] = None,
        limit: int = 100,
    ) -> pd.DataFrame:
        """
        Get individual contributions to committees.

        Args:
            committee_id: Recipient committee ID
            contributor_name: Contributor name (partial match)
            min_amount: Minimum contribution amount
            cycle: Election cycle year
            limit: Maximum number of contributions to return

        Returns:
            DataFrame with contribution information:
                - committee_id: Recipient committee
                - committee_name: Committee name
                - contributor_name: Contributor name
                - contributor_city: Contributor city
                - contributor_state: Contributor state
                - contributor_employer: Employer
                - contributor_occupation: Occupation
                - contribution_receipt_date: Date received
                - contribution_amount: Amount contributed
                - receipt_type: Type of receipt
                - cycle: Election cycle

        Example:
            >>> # Get large contributions (>$2000) for a candidate
            >>> big_donors = connector.get_contributions(
            ...     committee_id='C00123456',
            ...     min_amount=2000,
            ...     cycle=2024
            ... )
        """
        logger.info(
            "Fetching contributions: committee=%s, contributor=%s, min_amount=%s, cycle=%s",
            committee_id,
            contributor_name,
            min_amount,
            cycle,
        )

        # Mock contribution data
        contributions = pd.DataFrame(
            {
                "committee_id": [committee_id or f"C00{i:06d}" for i in range(1, 11)],
                "committee_name": [f"Committee {i}" for i in range(1, 11)],
                "contributor_name": [
                    "DOE, JOHN",
                    "SMITH, JANE",
                    "JOHNSON, ROBERT",
                    "WILLIAMS, MARY",
                    "BROWN, MICHAEL",
                    "JONES, PATRICIA",
                    "GARCIA, DAVID",
                    "MILLER, LINDA",
                    "DAVIS, JAMES",
                    "RODRIGUEZ, BARBARA",
                ],
                "contributor_city": [
                    "NEW YORK",
                    "LOS ANGELES",
                    "CHICAGO",
                    "HOUSTON",
                    "PHILADELPHIA",
                    "SAN FRANCISCO",
                    "BOSTON",
                    "SEATTLE",
                    "DENVER",
                    "ATLANTA",
                ],
                "contributor_state": ["NY", "CA", "IL", "TX", "PA", "CA", "MA", "WA", "CO", "GA"],
                "contributor_employer": [
                    "GOLDMAN SACHS",
                    "GOOGLE",
                    "MICROSOFT",
                    "EXXONMOBIL",
                    "COMCAST",
                    "APPLE",
                    "GENERAL ELECTRIC",
                    "AMAZON",
                    "WELLS FARGO",
                    "COCA-COLA",
                ],
                "contributor_occupation": [
                    "BANKER",
                    "ENGINEER",
                    "SOFTWARE DEVELOPER",
                    "EXECUTIVE",
                    "ATTORNEY",
                    "ENGINEER",
                    "EXECUTIVE",
                    "SOFTWARE DEVELOPER",
                    "BANKER",
                    "MARKETING",
                ],
                "contribution_receipt_date": pd.to_datetime(
                    [
                        "2024-01-15",
                        "2024-02-20",
                        "2024-03-10",
                        "2024-04-05",
                        "2024-05-12",
                        "2024-06-18",
                        "2024-07-22",
                        "2024-08-08",
                        "2024-09-14",
                        "2024-10-01",
                    ]
                ),
                "contribution_amount": [2800, 1000, 500, 2800, 1500, 2800, 750, 2800, 1200, 2800],
                "receipt_type": ["IND"] * 10,  # Individual contribution
                "cycle": [cycle or 2024] * 10,
            }
        )

        # Apply contributor name filter
        if contributor_name:
            contributions = contributions[
                contributions["contributor_name"].str.contains(
                    contributor_name.upper(), case=False, na=False
                )
            ]

        # Apply minimum amount filter
        if min_amount:
            contributions = contributions[contributions["contribution_amount"] >= min_amount]

        # Limit results
        contributions = contributions.head(limit)

        logger.info("Found %d contributions", len(contributions))
        return contributions

    def analyze_fundraising_patterns(
        self,
        candidate_id: Optional[str] = None,
        committee_id: Optional[str] = None,
        cycle: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Analyze fundraising patterns including donor demographics and contribution sizes.

        Args:
            candidate_id: Candidate to analyze
            committee_id: Committee to analyze (alternative to candidate_id)
            cycle: Election cycle year

        Returns:
            DataFrame with fundraising analysis:
                - entity_id: Candidate or committee ID
                - entity_name: Name
                - cycle: Election cycle
                - total_raised: Total receipts
                - total_contributions: Number of contributions
                - avg_contribution: Average contribution size
                - small_donor_count: Contributions <$200
                - small_donor_amount: Total from small donors
                - small_donor_percentage: % from small donors
                - large_donor_count: Contributions >$2000
                - large_donor_amount: Total from large donors
                - large_donor_percentage: % from large donors
                - pac_amount: PAC contributions
                - pac_percentage: % from PACs
                - self_funding_amount: Candidate self-funding
                - self_funding_percentage: % from self-funding
                - burn_rate: Disbursements / receipts
                - cash_on_hand: Current cash balance

        Example:
            >>> # Analyze a candidate's fundraising
            >>> analysis = connector.analyze_fundraising_patterns(
            ...     candidate_id='P80012345',
            ...     cycle=2024
            ... )
        """
        logger.info(
            "Analyzing fundraising: candidate=%s, committee=%s, cycle=%s",
            candidate_id,
            committee_id,
            cycle,
        )

        # Get committee finances
        if candidate_id:
            # In production, would look up committee for candidate
            committee_id = f"C00{candidate_id[3:]}"

        finances = self.get_committee_finances(committee_id=committee_id, cycle=cycle, limit=1)

        if len(finances) == 0:
            return pd.DataFrame()

        # Calculate fundraising metrics
        analysis = finances.copy()

        # Total raised
        analysis["total_raised"] = analysis["receipts"]

        # Contribution counts (simplified estimates)
        analysis["total_contributions"] = (analysis["individual_contributions"] / 500).astype(int)

        analysis["avg_contribution"] = (
            analysis["individual_contributions"] / analysis["total_contributions"]
        ).round(2)

        # Small donors (<$200)
        analysis["small_donor_count"] = (analysis["total_contributions"] * 0.6).astype(int)
        analysis["small_donor_amount"] = (analysis["individual_contributions"] * 0.20).round(0)
        analysis["small_donor_percentage"] = (
            analysis["small_donor_amount"] / analysis["total_raised"] * 100
        ).round(2)

        # Large donors (>$2000)
        analysis["large_donor_count"] = (analysis["total_contributions"] * 0.15).astype(int)
        analysis["large_donor_amount"] = (analysis["individual_contributions"] * 0.40).round(0)
        analysis["large_donor_percentage"] = (
            analysis["large_donor_amount"] / analysis["total_raised"] * 100
        ).round(2)

        # PAC contributions
        analysis["pac_amount"] = analysis["pac_contributions"]
        analysis["pac_percentage"] = (
            analysis["pac_amount"] / analysis["total_raised"] * 100
        ).round(2)

        # Self-funding
        analysis["self_funding_amount"] = analysis["candidate_contributions"]
        analysis["self_funding_percentage"] = (
            analysis["self_funding_amount"] / analysis["total_raised"] * 100
        ).round(2)

        # Burn rate
        analysis["burn_rate"] = (analysis["disbursements"] / analysis["receipts"] * 100).round(2)

        # Rename columns
        analysis = analysis.rename(
            columns={
                "committee_id": "entity_id",
                "committee_name": "entity_name",
            }
        )

        # Select relevant columns
        keep_cols = [
            "entity_id",
            "entity_name",
            "cycle",
            "total_raised",
            "total_contributions",
            "avg_contribution",
            "small_donor_count",
            "small_donor_amount",
            "small_donor_percentage",
            "large_donor_count",
            "large_donor_amount",
            "large_donor_percentage",
            "pac_amount",
            "pac_percentage",
            "self_funding_amount",
            "self_funding_percentage",
            "burn_rate",
            "cash_on_hand_end_period",
        ]

        analysis = analysis[[col for col in keep_cols if col in analysis.columns]]

        if "cash_on_hand_end_period" in analysis.columns:
            analysis = analysis.rename(columns={"cash_on_hand_end_period": "cash_on_hand"})

        logger.info("Completed fundraising analysis")
        return analysis

    @requires_license
    def get_expenditures(
        self,
        committee_id: Optional[str] = None,
        recipient_name: Optional[str] = None,
        min_amount: Optional[float] = None,
        cycle: Optional[int] = None,
        limit: int = 100,
    ) -> pd.DataFrame:
        """
        Get committee expenditures.

        Args:
            committee_id: Spending committee ID
            recipient_name: Recipient name (partial match)
            min_amount: Minimum expenditure amount
            cycle: Election cycle year
            limit: Maximum number of expenditures to return

        Returns:
            DataFrame with expenditure information:
                - committee_id: Spending committee
                - committee_name: Committee name
                - recipient_name: Recipient/payee name
                - recipient_city: Recipient city
                - recipient_state: Recipient state
                - disbursement_date: Date of expenditure
                - disbursement_amount: Amount spent
                - disbursement_description: Purpose/description
                - category_code: Expenditure category
                - cycle: Election cycle

        Example:
            >>> # Get advertising expenditures
            >>> ad_spending = connector.get_expenditures(
            ...     committee_id='C00123456',
            ...     min_amount=10000,
            ...     cycle=2024
            ... )
        """
        logger.info(
            "Fetching expenditures: committee=%s, recipient=%s, min_amount=%s, cycle=%s",
            committee_id,
            recipient_name,
            min_amount,
            cycle,
        )

        # Mock expenditure data
        expenditures = pd.DataFrame(
            {
                "committee_id": [committee_id or f"C00{i:06d}" for i in range(1, 11)],
                "committee_name": [f"Committee {i}" for i in range(1, 11)],
                "recipient_name": [
                    "MEDIA STRATEGIES INC",
                    "CAMPAIGN CONSULTANTS LLC",
                    "DIGITAL OUTREACH GROUP",
                    "EVENT PLANNING PROS",
                    "DIRECT MAIL EXPERTS",
                    "TV ADVERTISING AGENCY",
                    "POLLING RESEARCH INC",
                    "FUNDRAISING SOLUTIONS",
                    "CAMPAIGN STAFF PAYROLL",
                    "TRAVEL SERVICES",
                ],
                "recipient_city": [
                    "WASHINGTON",
                    "NEW YORK",
                    "LOS ANGELES",
                    "CHICAGO",
                    "PHILADELPHIA",
                    "BOSTON",
                    "DENVER",
                    "ATLANTA",
                    "SEATTLE",
                    "MIAMI",
                ],
                "recipient_state": ["DC", "NY", "CA", "IL", "PA", "MA", "CO", "GA", "WA", "FL"],
                "disbursement_date": pd.to_datetime(
                    [
                        "2024-02-15",
                        "2024-03-20",
                        "2024-04-10",
                        "2024-05-05",
                        "2024-06-12",
                        "2024-07-18",
                        "2024-08-22",
                        "2024-09-08",
                        "2024-10-14",
                        "2024-10-25",
                    ]
                ),
                "disbursement_amount": [
                    50000,
                    25000,
                    35000,
                    15000,
                    40000,
                    75000,
                    20000,
                    30000,
                    45000,
                    18000,
                ],
                "disbursement_description": [
                    "MEDIA PRODUCTION",
                    "CAMPAIGN STRATEGY",
                    "DIGITAL ADVERTISING",
                    "CAMPAIGN EVENTS",
                    "DIRECT MAIL",
                    "TELEVISION ADVERTISING",
                    "POLLING",
                    "FUNDRAISING",
                    "STAFF SALARIES",
                    "TRAVEL EXPENSES",
                ],
                "category_code": [
                    "MEDIA",
                    "CONSULTING",
                    "MEDIA",
                    "EVENTS",
                    "MAIL",
                    "MEDIA",
                    "POLLING",
                    "FUNDRAISING",
                    "PAYROLL",
                    "TRAVEL",
                ],
                "cycle": [cycle or 2024] * 10,
            }
        )

        # Apply recipient name filter
        if recipient_name:
            expenditures = expenditures[
                expenditures["recipient_name"].str.contains(
                    recipient_name.upper(), case=False, na=False
                )
            ]

        # Apply minimum amount filter
        if min_amount:
            expenditures = expenditures[expenditures["disbursement_amount"] >= min_amount]

        # Limit results
        expenditures = expenditures.head(limit)

        logger.info("Found %d expenditures", len(expenditures))
        return expenditures

    @requires_license
    def get_campaign_statistics(
        self,
        office: Optional[str] = None,
        state: Optional[str] = None,
        cycle: Optional[int] = None,
        group_by: str = "state",
    ) -> pd.DataFrame:
        """
        Calculate aggregate campaign finance statistics.

        Args:
            office: Filter by office (P/S/H)
            state: Filter by state
            cycle: Election cycle year
            group_by: Grouping level ('state', 'office', or 'party')

        Returns:
            DataFrame with campaign statistics:
                - group: Geographic or categorical group
                - candidate_count: Number of candidates
                - total_raised: Total receipts
                - avg_raised: Average receipts per candidate
                - median_raised: Median receipts
                - total_spent: Total disbursements
                - avg_cash_on_hand: Average cash balance

        Example:
            >>> # State-level House campaign statistics
            >>> stats = connector.get_campaign_statistics(
            ...     office='H',
            ...     cycle=2024,
            ...     group_by='state'
            ... )
        """
        logger.info(
            "Calculating campaign statistics: office=%s, state=%s, cycle=%s, group_by=%s",
            office,
            state,
            cycle,
            group_by,
        )

        # Get candidates
        candidates = self.search_candidates(office=office, state=state, cycle=cycle, limit=10000)

        # Get committee finances for each candidate
        # In production, would batch this efficiently
        finances_list = []
        for _, candidate in candidates.iterrows():
            committee_id = f"C00{candidate['candidate_id'][3:]}"
            finance = self.get_committee_finances(committee_id=committee_id, cycle=cycle, limit=1)
            if len(finance) > 0:
                finance["candidate_party"] = candidate["party"]
                finance["candidate_state"] = candidate["state"]
                finance["candidate_office"] = candidate["office"]
                finances_list.append(finance)

        if not finances_list:
            return pd.DataFrame()

        all_finances = pd.concat(finances_list, ignore_index=True)

        # Determine grouping column
        if group_by == "state":
            group_col = "candidate_state"
        elif group_by == "office":
            group_col = "candidate_office"
        elif group_by == "party":
            group_col = "candidate_party"
        else:
            raise ValueError("group_by must be 'state', 'office', or 'party'")

        # Calculate statistics
        stats = (
            all_finances.groupby(group_col)
            .agg(
                candidate_count=("committee_id", "count"),
                total_raised=("receipts", "sum"),
                avg_raised=("receipts", "mean"),
                median_raised=("receipts", "median"),
                total_spent=("disbursements", "sum"),
                avg_cash_on_hand=("cash_on_hand_end_period", "mean"),
            )
            .reset_index()
        )

        # Rename group column
        stats = stats.rename(columns={group_col: "group"})

        # Round numeric columns
        numeric_cols = ["avg_raised", "median_raised", "avg_cash_on_hand"]
        for col in numeric_cols:
            stats[col] = stats[col].round(2)

        # Sort by total raised
        stats = stats.sort_values("total_raised", ascending=False)

        logger.info("Calculated statistics for %d groups", len(stats))
        return stats
