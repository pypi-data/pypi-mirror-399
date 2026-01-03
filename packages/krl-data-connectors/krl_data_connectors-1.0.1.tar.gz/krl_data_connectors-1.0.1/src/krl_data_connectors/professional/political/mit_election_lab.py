# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

# Copyright (c) 2024 Sudiata Giddasira, Inc. d/b/a Quipu Research Labs, LLC d/b/a KR-Labs™
# SPDX-License-Identifier: Apache-2.0
#
# Khipu Research Analytics Suite - KR-Labs™
# Licensed under the Apache License, Version 2.0

"""
MIT Election Lab Connector

Provides access to MIT Election Data and Science Lab datasets for political research.

Data Sources:
- U.S. President Election Returns (1976-2020)
- U.S. House Election Returns (1976-2022)
- U.S. Senate Election Returns (1976-2020)
- County Presidential Election Returns (2000-2020)
- Voter Turnout Data
- State Legislative Election Returns

Key Use Cases:
- Electoral trend analysis
- Voter turnout research
- Partisan voting patterns
- Swing state identification
- Geographic political shifts
- Competitive race analysis

Data Coverage:
- Geographic: State, county, congressional district levels
- Temporal: 1976-2022 (varies by dataset)
- Elections: Presidential, House, Senate, state legislative
- Metrics: Vote counts, vote shares, turnout rates, margins

Documentation: https://electionlab.mit.edu/
Data Portal: https://dataverse.harvard.edu/dataverse/medsl
Research: https://electionlab.mit.edu/research
"""

from pathlib import Path
from typing import Dict, List, Optional, Union

import pandas as pd

from krl_data_connectors.base_connector import BaseConnector

from ...core import DataTier
from ...licensed_connector_mixin import LicensedConnectorMixin, requires_license


class MITElectionLabConnector(LicensedConnectorMixin, BaseConnector):
    """
    Connector for MIT Election Data and Science Lab datasets.
    """

    # Registry name for license validation
    _connector_name = "MIT_Election_Lab"

    """

    The MIT Election Lab (formerly MIT Election Data and Science Lab)
    maintains comprehensive election returns and voter turnout data
    for U.S. elections at multiple geographic levels.

    This connector enables political science research, electoral trend
    analysis, and civic engagement studies using authoritative election
    data curated by MIT researchers.

    Data Structure:
    - Election returns: Vote counts by candidate, party, office
    - Voter turnout: Votes cast, eligible voters, turnout rates
    - Geographic levels: State, county, congressional district
    - Temporal coverage: 1976-2022 (varies by dataset)

    Key Datasets:
    - U.S. President (1976-2020): County and state returns
    - U.S. House (1976-2022): District-level returns
    - U.S. Senate (1976-2020): State-level returns
    - County Presidential (2000-2020): County-level detail
    - Voter Turnout (1980-2020): State-level turnout

    Examples:
        >>> # Initialize connector
        >>> mit = MITElectionLabConnector()
        >>> mit.connect()

        >>> # Load presidential returns
        >>> pres = mit.load_presidential_data('president_1976_2020.csv')
        >>>
        >>> # Get state results for 2020
        >>> results_2020 = mit.get_election_results(year=2020, office='president')
        >>>
        >>> # Analyze swing states
        >>> swing = mit.get_swing_states(threshold=5.0)
        >>>
        >>> # Voter turnout trends
        >>> turnout = mit.get_turnout_trends(state='PA')
    """

    def __init__(
        self,
        data_dir: Optional[Union[str, Path]] = None,
        cache_dir: Optional[str] = None,
        cache_ttl: int = 86400,
    ):
        """
        Initialize MIT Election Lab connector.

        Args:
            data_dir: Directory containing MIT Election Lab CSV files
            cache_dir: Directory for caching responses
            cache_ttl: Cache time-to-live in seconds (default: 24 hours)
        """
        super().__init__(
            cache_dir=cache_dir,
            cache_ttl=cache_ttl,
        )
        self.connector_name = "MITElectionLab"
        self.data_dir = Path(data_dir) if data_dir else None
        self._presidential_data = None
        self._house_data = None
        self._senate_data = None
        self._county_data = None
        self._turnout_data = None

    def _get_api_key(self) -> Optional[str]:
        """
        Get API key from environment or config.

        MIT Election Lab data is public and does not require authentication.
        Implemented for BaseConnector interface compliance.

        Returns:
            None (no API key required)
        """
        return None

    def fetch(self, **kwargs) -> Dict:
        """
        Fetch data from MIT Election Lab (if API becomes available).

        Note: MIT Election Lab currently provides bulk CSV downloads via
        Harvard Dataverse. This method is implemented for future API compatibility.

        Args:
            **kwargs: Connector-specific parameters

        Returns:
            JSON response as dictionary

        Raises:
            NotImplementedError: API access not yet available
        """
        raise NotImplementedError(
            "MIT Election Lab uses bulk CSV downloads via Harvard Dataverse. "
            "Use load_*_data() methods to load MIT Election Lab data files. "
            "Download data from: https://dataverse.harvard.edu/dataverse/medsl"
        )

    def connect(self) -> None:
        """
        Establish connection to MIT Election Lab data sources.

        For file-based access, validates data directory exists.

        Raises:
            ConnectionError: If data directory doesn't exist
        """
        self._init_session()

        # Validate data directory if provided
        if self.data_dir and not self.data_dir.exists():
            raise ConnectionError(
                f"MIT Election Lab data directory not found: {self.data_dir}. "
                "Download data from https://dataverse.harvard.edu/dataverse/medsl"
            )

        self.logger.info("MIT Election Lab connector initialized successfully")

    def load_presidential_data(
        self, file_path: Union[str, Path], year_filter: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Load U.S. presidential election returns from CSV file.

        MIT Election Lab presidential dataset includes state-level returns
        for presidential elections from 1976-2020.

        Args:
            file_path: Path to presidential election CSV file
            year_filter: Optional year to filter results

        Returns:
            DataFrame with presidential election returns

        Columns include:
        - year: Election year
        - state: State name
        - state_po: State postal abbreviation (2-letter)
        - state_fips: State FIPS code
        - state_cen: State Census code
        - state_ic: State ICPSR code
        - office: Office sought (PRESIDENT)
        - candidate: Candidate name
        - party_detailed: Detailed party affiliation
        - party_simplified: Simplified party (DEMOCRAT, REPUBLICAN, OTHER)
        - mode: Vote mode (total, absentee, etc.)
        - candidatevotes: Votes received by candidate
        - totalvotes: Total votes cast in state
        - writein: Boolean for write-in candidate
        - version: Dataset version

        Examples:
            >>> # Load all presidential data
            >>> pres = mit.load_presidential_data('president_1976_2020.csv')
            >>>
            >>> # Filter to 2020 only
            >>> pres_2020 = mit.load_presidential_data(
            ...     'president_1976_2020.csv',
            ...     year_filter=2020
            ... )
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Presidential data file not found: {file_path}")

        self.logger.info(f"Loading MIT Election Lab presidential data from {file_path.name}")

        # Load data
        df = pd.read_csv(file_path, low_memory=False)

        # Filter by year if provided
        if year_filter:
            df = df[df["year"] == year_filter]
            self.logger.info(f"Filtered to {len(df):,} records for {year_filter}")

        self._presidential_data = df
        self.logger.info(f"Loaded {len(df):,} presidential election records")
        return df

    def load_county_presidential_data(
        self,
        file_path: Union[str, Path],
        year_filter: Optional[int] = None,
        state_filter: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Load county-level presidential election returns from CSV file.

        County presidential dataset provides fine-grained geographic detail
        for presidential elections from 2000-2020.

        Args:
            file_path: Path to county presidential CSV file
            year_filter: Optional year filter
            state_filter: Optional state postal abbreviation

        Returns:
            DataFrame with county-level presidential returns

        Columns include:
        - year: Election year
        - state: State name
        - state_po: State postal code
        - county_name: County name
        - county_fips: 5-digit county FIPS code
        - office: Office (PRESIDENT)
        - candidate: Candidate name
        - party: Party affiliation
        - candidatevotes: Votes for candidate in county
        - totalvotes: Total votes cast in county
        - mode: Vote mode

        Examples:
            >>> # Load all county data
            >>> counties = mit.load_county_presidential_data('countypres_2000_2020.csv')
            >>>
            >>> # Pennsylvania 2020
            >>> pa_2020 = mit.load_county_presidential_data(
            ...     'countypres_2000_2020.csv',
            ...     year_filter=2020,
            ...     state_filter='PA'
            ... )
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"County presidential data file not found: {file_path}")

        self.logger.info(f"Loading county presidential data from {file_path.name}")

        # Load data with FIPS preservation
        df = pd.read_csv(file_path, low_memory=False, dtype={"county_fips": "str"})

        # Apply filters
        if year_filter:
            df = df[df["year"] == year_filter]
        if state_filter:
            df = df[df["state_po"] == state_filter.upper()]

        if year_filter or state_filter:
            filters = []
            if year_filter:
                filters.append(str(year_filter))
            if state_filter:
                filters.append(state_filter.upper())
            self.logger.info(f"Filtered to {len(df):,} records ({', '.join(filters)})")

        self._county_data = df
        return df

    @requires_license
    def get_election_results(
        self, year: int, office: str = "president", state: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get election results for specific year and office.

        Args:
            year: Election year
            office: Office type ('president', 'house', 'senate')
            state: Optional state filter (postal abbreviation)

        Returns:
            DataFrame with election results

        Examples:
            >>> # 2020 presidential results
            >>> results = mit.get_election_results(year=2020, office='president')
            >>>
            >>> # Georgia 2020 results
            >>> ga_results = mit.get_election_results(year=2020, office='president', state='GA')
        """
        # Determine which dataset to use
        if office.lower() == "president":
            if self._presidential_data is None:
                raise ValueError(
                    "No presidential data loaded. Call load_presidential_data() first."
                )
            df = self._presidential_data[self._presidential_data["year"] == year]
        else:
            raise ValueError(f"Office '{office}' not yet supported. Use 'president'.")

        # Filter by state if provided
        if state:
            df = df[df["state_po"] == state.upper()]

        return df

    @requires_license
    def get_state_winner(
        self, year: int, state: str, office: str = "president"
    ) -> Dict[str, Union[str, int, float]]:
        """
        Get winning candidate and margin for a state election.

        Args:
            year: Election year
            state: State postal abbreviation
            office: Office type (default: 'president')

        Returns:
            Dictionary with winner info:
            - winner: Winning candidate name
            - party: Winning party
            - votes: Votes received
            - total_votes: Total votes cast
            - vote_share: Percentage of vote
            - margin: Victory margin (percentage points)

        Examples:
            >>> # Pennsylvania 2020 winner
            >>> pa_winner = mit.get_state_winner(year=2020, state='PA')
            >>> print(f"{pa_winner['winner']} won with {pa_winner['vote_share']:.1f}%")
        """
        results = self.get_election_results(year=year, office=office, state=state)

        # Get top 2 candidates by votes
        top_candidates = results.nlargest(2, "candidatevotes")

        if len(top_candidates) < 2:
            raise ValueError(f"Insufficient data for {state} {year}")

        winner = top_candidates.iloc[0]
        runner_up = top_candidates.iloc[1]

        total_votes = results["totalvotes"].iloc[0]
        winner_votes = winner["candidatevotes"]
        runner_up_votes = runner_up["candidatevotes"]

        winner_share = (winner_votes / total_votes) * 100
        runner_up_share = (runner_up_votes / total_votes) * 100
        margin = winner_share - runner_up_share

        return {
            "winner": winner["candidate"],
            "party": winner["party_simplified"],
            "votes": int(winner_votes),
            "total_votes": int(total_votes),
            "vote_share": float(winner_share),
            "margin": float(margin),
        }

    @requires_license
    def get_swing_states(self, year: int, threshold: float = 5.0) -> pd.DataFrame:
        """
        Identify swing states based on victory margin threshold.

        Args:
            year: Election year
            threshold: Maximum margin to be considered swing state (default: 5%)

        Returns:
            DataFrame of swing states with margins

        Examples:
            >>> # 2020 swing states (margin < 5%)
            >>> swing = mit.get_swing_states(year=2020, threshold=5.0)
            >>> print(swing[['state_po', 'winner', 'margin']].sort_values('margin'))
        """
        if self._presidential_data is None:
            raise ValueError("No presidential data loaded.")

        results = self._presidential_data[self._presidential_data["year"] == year]

        # Get state winners
        swing_states = []
        for state in results["state_po"].unique():
            try:
                winner_info = self.get_state_winner(year, state)
                if winner_info["margin"] <= threshold:
                    swing_states.append(
                        {
                            "state_po": state,
                            "winner": winner_info["winner"],
                            "party": winner_info["party"],
                            "margin": winner_info["margin"],
                            "vote_share": winner_info["vote_share"],
                        }
                    )
            except (ValueError, IndexError):
                # Skip states with data issues
                continue

        return pd.DataFrame(swing_states).sort_values("margin")

    @requires_license
    def get_state_trends(self, state: str, office: str = "president") -> pd.DataFrame:
        """
        Get electoral trends for a state over time.

        Args:
            state: State postal abbreviation
            office: Office type (default: 'president')

        Returns:
            DataFrame with winners and margins by year

        Examples:
            >>> # Pennsylvania presidential trends
            >>> pa_trends = mit.get_state_trends(state='PA')
            >>> pa_trends.plot(x='year', y='dem_share', title='PA Democratic Vote Share')
        """
        if self._presidential_data is None:
            raise ValueError("No presidential data loaded.")

        results = self._presidential_data[self._presidential_data["state_po"] == state.upper()]

        # Calculate party vote shares by year
        trends = []
        for year in sorted(results["year"].unique()):
            year_data = results[results["year"] == year]

            dem = year_data[year_data["party_simplified"] == "DEMOCRAT"]
            rep = year_data[year_data["party_simplified"] == "REPUBLICAN"]

            if len(dem) > 0 and len(rep) > 0:
                total = year_data["totalvotes"].iloc[0]
                dem_votes = dem["candidatevotes"].sum()
                rep_votes = rep["candidatevotes"].sum()

                trends.append(
                    {
                        "year": year,
                        "dem_votes": int(dem_votes),
                        "rep_votes": int(rep_votes),
                        "total_votes": int(total),
                        "dem_share": (dem_votes / total) * 100,
                        "rep_share": (rep_votes / total) * 100,
                        "margin": abs((dem_votes - rep_votes) / total) * 100,
                    }
                )

        return pd.DataFrame(trends)

    def compare_states(
        self, states: List[str], year: int, metric: str = "dem_share"
    ) -> pd.DataFrame:
        """
        Compare electoral metrics across multiple states.

        Args:
            states: List of state postal abbreviations
            year: Election year
            metric: Metric to compare ('dem_share', 'rep_share', 'margin')

        Returns:
            DataFrame with comparison

        Examples:
            >>> # Compare swing states 2020
            >>> comparison = mit.compare_states(
            ...     states=['PA', 'WI', 'MI', 'AZ', 'GA'],
            ...     year=2020,
            ...     metric='dem_share'
            ... )
        """
        comparison = []
        for state in states:
            try:
                trends = self.get_state_trends(state)
                year_data = trends[trends["year"] == year]
                if len(year_data) > 0:
                    comparison.append({"state": state, metric: year_data.iloc[0][metric]})
            except (ValueError, KeyError):
                continue

        return pd.DataFrame(comparison).sort_values(metric, ascending=False)
