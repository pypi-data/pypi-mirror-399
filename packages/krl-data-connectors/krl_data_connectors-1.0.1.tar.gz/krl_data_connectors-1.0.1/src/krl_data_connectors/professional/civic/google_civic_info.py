# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

# Copyright (c) 2025 KR-Labs Foundation. All rights reserved.
# Licensed under Apache License 2.0 (see LICENSE file for details)

"""
Google Civic Information API Connector.

Provides access to:
- Polling place locations and hours
- Elected representatives (federal, state, local)
- Election information and ballot data
- Voter registration requirements
- Early voting locations
- Voter information by address

The Google Civic Information API helps voters access accurate voting information,
empowering civic engagement and increasing voter participation across the United States.

Documentation: https://developers.google.com/civic-information/
API Console: https://console.cloud.google.com/apis/library/civicinfo.googleapis.com
"""

from datetime import datetime, UTC
from typing import Any, Dict, List, Optional

from ...base_connector import BaseConnector
from ...core import DataTier
from ...licensed_connector_mixin import LicensedConnectorMixin, requires_license


class GoogleCivicInfoConnector(LicensedConnectorMixin, BaseConnector):
    """
    Connector for Google Civic Information API.

    Provides comprehensive civic engagement data including voting locations,
    elected representatives, election information, and voter registration details.

    Key Features:
    - Find polling places by address
    - Look up elected representatives (federal, state, local)
    - Get upcoming election information
    - Access voter registration requirements
    - Find early voting and drop-off locations
    - Get ballot information and measures

    API Access:
    - Free tier: 25,000 queries per day
    - Requires Google Cloud API key (free to obtain)
    - No authentication beyond API key

    Rate Limits:
    - 25,000 requests per day (free tier)
    - 1,000 requests per 100 seconds per user
    - Can request quota increase for high-volume applications

    Example Usage:
        >>> connector = GoogleCivicInfoConnector(api_key="YOUR_API_KEY")
        >>>
        >>> # Find polling places
        >>> polling = connector.get_polling_places(
        ...     address="1600 Pennsylvania Ave NW, Washington, DC 20500"
        ... )
        >>>
        >>> # Look up representatives
        >>> reps = connector.get_representatives(
        ...     address="1600 Pennsylvania Ave NW, Washington, DC 20500"
        ... )
        >>>
        >>> # Get election information
        >>> elections = connector.get_elections()
        >>>
        >>> # Get voter info for upcoming election
        >>> voter_info = connector.get_voter_info(
        ...     address="123 Main St, Springfield, IL 62701",
        ...     election_id=2000
        ... )
    """

    # Registry name for license validation
    _connector_name = "Google_Civic_Info"

    BASE_URL = "https://www.googleapis.com/civicinfo/v2"

    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_dir: Optional[str] = None,
        cache_ttl: int = 86400,  # 24 hours (civic data changes infrequently)
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        Initialize Google Civic Information connector.

        Args:
            api_key: Google Cloud API key (required)
            cache_dir: Directory for cache files
            cache_ttl: Cache time-to-live in seconds (default: 24 hours)
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        super().__init__(
            api_key=api_key,
            cache_dir=cache_dir,
            cache_ttl=cache_ttl,
            timeout=timeout,
            max_retries=max_retries,
        )

        if not self.api_key:
            self.logger.warning(
                "No API key provided. Get one at: "
                "https://console.cloud.google.com/apis/credentials"
            )

    def _get_api_key(self) -> Optional[str]:
        """
        Get API key from configuration.

        Returns:
            API key or None
        """
        return self.config.get("GOOGLE_CIVIC_INFO_API_KEY") or self.config.get("GOOGLE_API_KEY")

    def connect(self) -> None:
        """
        Establish connection to Google Civic Information API.

        Tests connection by fetching the list of available elections.
        """
        try:
            # Test connection with elections endpoint
            self.get_elections()
            self.logger.info("Successfully connected to Google Civic Information API")

        except Exception as e:
            self.logger.error(f"Failed to connect to Google Civic Information API: {e}")
            raise

    @requires_license
    def get_polling_places(
        self,
        address: str,
        election_id: Optional[int] = None,
        official_only: bool = False,
    ) -> Dict[str, Any]:
        """
        Find polling places for a given address.

        Returns polling location details including address, hours, and
        accessibility information for Election Day voting.

        Args:
            address: Full address (e.g., "123 Main St, Springfield, IL 62701")
            election_id: Specific election ID (default: next election)
            official_only: Only return official data (exclude crowdsourced)

        Returns:
            Dictionary containing:
            - pollingLocations: List of polling places
            - earlyVoteSites: Early voting locations
            - dropOffLocations: Ballot drop-off sites
            - normalizedAddress: Standardized address used

        Example:
            >>> places = connector.get_polling_places(
            ...     address="1600 Pennsylvania Ave NW, Washington, DC 20500"
            ... )
            >>> for location in places.get("pollingLocations", []):
            ...     print(location["address"]["locationName"])
            ...     print(location["pollingHours"])
        """
        endpoint = f"{self.BASE_URL}/voterinfo"

        params = {
            "key": self.api_key,
            "address": address,
        }

        if election_id:
            params["electionId"] = str(election_id)

        if official_only:
            params["officialOnly"] = "true"

        self.logger.info(
            f"Fetching polling places",
            extra={"address": address, "election_id": election_id},
        )

        response = self._make_request(url=endpoint, params=params, use_cache=True)

        return response

    @requires_license
    def get_representatives(
        self,
        address: Optional[str] = None,
        include_offices: bool = True,
        levels: Optional[List[str]] = None,
        roles: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Look up elected representatives for an address.

        Returns information about all elected officials representing the given
        address at federal, state, and local levels.

        Args:
            address: Full address (if None, returns all current federal officials)
            include_offices: Include office names and divisions
            levels: Filter by government level
                   (country, administrativeArea1, administrativeArea2, locality, etc.)
            roles: Filter by role (legislatorUpperBody, legislatorLowerBody, etc.)

        Returns:
            Dictionary containing:
            - officials: List of elected representatives with contact info
            - offices: Government offices and divisions
            - normalizedInput: Standardized address

        Example:
            >>> reps = connector.get_representatives(
            ...     address="1600 Pennsylvania Ave NW, Washington, DC 20500",
            ...     levels=["country", "administrativeArea1"]
            ... )
            >>> for official in reps["officials"]:
            ...     print(f"{official['name']} - {official['party']}")
            ...     if 'phones' in official:
            ...         print(f"Phone: {official['phones'][0]}")
        """
        endpoint = f"{self.BASE_URL}/representatives"

        params = {"key": self.api_key}

        if address:
            params["address"] = address

        if include_offices:
            params["includeOffices"] = "true"

        if levels:
            params["levels"] = ",".join(levels)

        if roles:
            params["roles"] = ",".join(roles)

        self.logger.info(
            f"Fetching representatives",
            extra={"address": address, "levels": levels, "roles": roles},
        )

        response = self._make_request(url=endpoint, params=params, use_cache=True)

        return response

    @requires_license
    def get_elections(self) -> List[Dict[str, Any]]:
        """
        Get list of available elections.

        Returns information about current and upcoming elections that can be
        queried for voter information.

        Returns:
            List of election dictionaries containing:
            - id: Election ID
            - name: Election name
            - electionDay: Election date (YYYY-MM-DD)
            - ocdDivisionId: Geographic division identifier

        Example:
            >>> elections = connector.get_elections()
            >>> for election in elections:
            ...     print(f"{election['name']} - {election['electionDay']}")
            ...     print(f"ID: {election['id']}")
        """
        endpoint = f"{self.BASE_URL}/elections"

        params = {"key": self.api_key}

        self.logger.info("Fetching available elections")

        response = self._make_request(url=endpoint, params=params, use_cache=True)

        # Extract elections array from response
        elections = response.get("elections", [])

        self.logger.info(f"Retrieved {len(elections)} elections")

        return elections

    @requires_license
    def get_voter_info(
        self,
        address: str,
        election_id: Optional[int] = None,
        official_only: bool = False,
        return_all_available_data: bool = False,
    ) -> Dict[str, Any]:
        """
        Get comprehensive voter information for an address.

        Returns complete voter information including polling places, candidates,
        ballot measures, and registration requirements.

        Args:
            address: Full address
            election_id: Specific election ID (default: next election)
            official_only: Only return official data
            return_all_available_data: Include all available fields

        Returns:
            Dictionary containing:
            - election: Election details
            - pollingLocations: Polling places
            - earlyVoteSites: Early voting locations
            - dropOffLocations: Ballot drop boxes
            - contests: Ballot contests and candidates
            - state: State-level election info
            - normalizedAddress: Standardized address

        Example:
            >>> info = connector.get_voter_info(
            ...     address="123 Main St, Springfield, IL 62701",
            ...     return_all_available_data=True
            ... )
            >>> print(f"Election: {info['election']['name']}")
            >>> print(f"Polling place: {info['pollingLocations'][0]['address']}")
            >>> for contest in info.get("contests", []):
            ...     print(f"Contest: {contest['office']}")
            ...     for candidate in contest.get("candidates", []):
            ...         print(f"  - {candidate['name']} ({candidate['party']})")
        """
        endpoint = f"{self.BASE_URL}/voterinfo"

        params = {
            "key": self.api_key,
            "address": address,
        }

        if election_id:
            params["electionId"] = str(election_id)

        if official_only:
            params["officialOnly"] = "true"

        if return_all_available_data:
            params["returnAllAvailableData"] = "true"

        self.logger.info(
            f"Fetching voter info",
            extra={"address": address, "election_id": election_id},
        )

        response = self._make_request(url=endpoint, params=params, use_cache=True)

        return response

    @requires_license
    def get_representatives_by_division(
        self,
        ocd_id: str,
        recursive: bool = False,
        levels: Optional[List[str]] = None,
        roles: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Look up representatives by Open Civic Data division identifier.

        More precise than address-based lookup when you know the exact
        political division (state, district, county, etc.).

        Args:
            ocd_id: Open Civic Data division ID
                   (e.g., "ocd-division/country:us/state:ca/cd:12")
            recursive: Include representatives from parent divisions
            levels: Filter by government level
            roles: Filter by role

        Returns:
            Dictionary with officials and offices for the division

        Example:
            >>> # Get representatives for California's 12th Congressional District
            >>> reps = connector.get_representatives_by_division(
            ...     ocd_id="ocd-division/country:us/state:ca/cd:12"
            ... )
        """
        endpoint = f"{self.BASE_URL}/representatives/{ocd_id}"

        params = {"key": self.api_key}

        if recursive:
            params["recursive"] = "true"

        if levels:
            params["levels"] = ",".join(levels)

        if roles:
            params["roles"] = ",".join(roles)

        self.logger.info(
            f"Fetching representatives by division",
            extra={"ocd_id": ocd_id, "recursive": recursive},
        )

        response = self._make_request(url=endpoint, params=params, use_cache=True)

        return response

    def search_by_coordinates(
        self,
        latitude: float,
        longitude: float,
        include_offices: bool = True,
    ) -> Dict[str, Any]:
        """
        Find representatives by geographic coordinates.

        Useful for mobile applications or when precise address is unknown.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            include_offices: Include office information

        Returns:
            Dictionary with officials for the location

        Example:
            >>> # White House coordinates
            >>> reps = connector.search_by_coordinates(
            ...     latitude=38.8977,
            ...     longitude=-77.0365
            ... )
        """
        # Convert coordinates to address-like string
        address = f"{latitude},{longitude}"

        return self.get_representatives(
            address=address,
            include_offices=include_offices,
        )

    def fetch(self, **kwargs) -> Dict[str, Any]:
        """
        Generic fetch method for compatibility with BaseConnector.

        Routes to appropriate method based on parameters.

        Args:
            **kwargs: Method-specific parameters

        Returns:
            API response data
        """
        address = kwargs.get("address")
        method = kwargs.get("method", "voter_info")

        if not address and method != "elections":
            raise ValueError("address parameter is required (except for get_elections)")

        # Ensure address is a string for methods that require it
        address_str = str(address) if address is not None else ""

        if method == "polling_places":
            return self.get_polling_places(
                address=address_str,
                election_id=kwargs.get("election_id"),
                official_only=kwargs.get("official_only", False),
            )
        elif method == "representatives":
            return self.get_representatives(
                address=address,
                include_offices=kwargs.get("include_offices", True),
                levels=kwargs.get("levels"),
                roles=kwargs.get("roles"),
            )
        elif method == "elections":
            return {"elections": self.get_elections()}
        else:  # Default to voter_info
            return self.get_voter_info(
                address=address_str,
                election_id=kwargs.get("election_id"),
                official_only=kwargs.get("official_only", False),
                return_all_available_data=kwargs.get("return_all_available_data", False),
            )
