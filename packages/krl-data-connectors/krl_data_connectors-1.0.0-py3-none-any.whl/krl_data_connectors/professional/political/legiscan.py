# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
LegiScan API Connector.

Provides access to the LegiScan API for tracking state and federal legislation,
votes, bill text, amendments, and legislative data.

API Documentation: https://legiscan.com/legiscan
"""

from datetime import datetime, UTC
from typing import Any, Dict, List, Optional

import pandas as pd

from ...base_connector import BaseConnector
from ...core import DataTier
from ...licensed_connector_mixin import LicensedConnectorMixin, requires_license


class LegiScanConnector(LicensedConnectorMixin, BaseConnector):
    """
    Connector for LegiScan API.

    LegiScan provides comprehensive legislative data including:
    - Bills (state and federal)
    - Votes and roll calls
    - Bill text and amendments
    - Sponsors and co-sponsors
    - Committee assignments
    - Legislative sessions

    API Documentation: https://legiscan.com/legiscan
    API Registration: https://legiscan.com/legiscan#register

    Example:
        >>> connector = LegiScanConnector()
        >>>
        >>> # Search for bills
        >>> bills = connector.search_bills(
        ...     state='CA',
        ...     query='climate change',
        ...     year=2024
        ... )
        >>>
        >>> # Get bill details
        >>> bill = connector.get_bill(bill_id=12345)
        >>>
        >>> # Get votes
        >>> votes = connector.get_votes(bill_id=12345)
        >>>
        >>> connector.close()
    """

    # Registry name for license validation
    _connector_name = "LegiScan"

    def __init__(self, api_key: Optional[str] = None, timeout: int = 30, **kwargs):
        """
        Initialize LegiScan connector.

        Args:
            api_key: LegiScan API key (required)
            timeout: Request timeout in seconds (default: 30)
            **kwargs: Additional arguments passed to BaseConnector
        """
        # Store LegiScan-specific API key before parent initialization
        self._legiscan_api_key = api_key

        super().__init__(api_key=api_key, timeout=timeout, **kwargs)
        self.base_url = "https://api.legiscan.com"

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
        if hasattr(self, "_legiscan_api_key") and self._legiscan_api_key:
            return self._legiscan_api_key

        # Fall back to ConfigManager (environment + ~/.krl/apikeys)
        return self.config.get("LEGISCAN_API_KEY")

    def connect(self) -> None:
        """
        Establish connection to LegiScan API.

        Raises:
            ConnectionError: If unable to connect
            ValueError: If API key is missing
        """
        if not self.api_key:
            raise ValueError(
                "LegiScan API key is required. "
                "Register at https://legiscan.com/legiscan#register"
            )

        if self.session is not None:
            return

        try:
            self.session = self._init_session()

            # Test connection with a simple request
            response = self.session.get(
                f"{self.base_url}/",
                params={"key": self.api_key, "op": "getSessionList", "state": "ALL"},
                timeout=self.timeout,
            )
            response.raise_for_status()

            self.logger.info("Successfully connected to LegiScan API")
        except Exception as e:
            self.logger.error(f"Failed to connect to LegiScan API: {e}")
            raise ConnectionError(f"Failed to connect to LegiScan API: {e}") from e

    def fetch(self, **kwargs: Any) -> Any:
        """
        Generic fetch method for LegiScan API queries.

        Args:
            **kwargs: Query parameters

        Returns:
            API response data

        Raises:
            ValueError: If operation not specified
        """
        if "op" not in kwargs:
            raise ValueError("Operation 'op' must be specified")

        return self._make_api_request(**kwargs)

    def _make_api_request(self, **params: Any) -> Dict[str, Any]:
        """
        Make request to LegiScan API.

        Args:
            **params: API parameters

        Returns:
            API response data

        Raises:
            ValueError: If API key not configured
        """
        if not self.api_key:
            raise ValueError("API key is required")

        # Add API key to params
        params["key"] = self.api_key

        # Make request
        url = f"{self.base_url}/"
        response_data = self._make_request(url, params=params)

        # Check for API errors
        if response_data.get("status") == "ERROR":
            error_msg = response_data.get("alert", {}).get("message", "Unknown error")
            raise ValueError(f"LegiScan API error: {error_msg}")

        return response_data

    @requires_license
    def get_session_list(self, state: str = "ALL") -> List[Dict[str, Any]]:
        """
        Get list of legislative sessions.

        Args:
            state: State abbreviation (e.g., 'CA', 'TX') or 'ALL' for all states

        Returns:
            List of legislative sessions

        Example:
            >>> sessions = connector.get_session_list(state='CA')
        """
        response = self._make_api_request(op="getSessionList", state=state)
        return response.get("sessions", [])

    def search_bills(
        self,
        query: Optional[str] = None,
        state: Optional[str] = None,
        year: Optional[int] = None,
        page: int = 1,
    ) -> Dict[str, Any]:
        """
        Search for bills.

        Args:
            query: Search query string
            state: State abbreviation (e.g., 'CA', 'TX')
            year: Year of legislative session
            page: Page number for paginated results

        Returns:
            Search results with bills

        Example:
            >>> bills = connector.search_bills(
            ...     state='CA',
            ...     query='climate change',
            ...     year=2024
            ... )
        """
        params = {"op": "getSearch", "page": page}

        if query:
            params["query"] = query
        if state:
            params["state"] = state
        if year:
            params["year"] = year

        return self._make_api_request(**params)

    @requires_license
    def get_bill(self, bill_id: int) -> Dict[str, Any]:
        """
        Get detailed information about a bill.

        Args:
            bill_id: LegiScan bill ID

        Returns:
            Bill details

        Example:
            >>> bill = connector.get_bill(bill_id=12345)
        """
        response = self._make_api_request(op="getBill", id=bill_id)
        return response.get("bill", {})

    @requires_license
    def get_bill_text(self, doc_id: int) -> Dict[str, Any]:
        """
        Get bill text document.

        Args:
            doc_id: LegiScan document ID

        Returns:
            Bill text document

        Example:
            >>> text = connector.get_bill_text(doc_id=67890)
        """
        response = self._make_api_request(op="getBillText", id=doc_id)
        return response.get("text", {})

    @requires_license
    def get_votes(self, roll_call_id: int) -> Dict[str, Any]:
        """
        Get roll call vote information.

        Args:
            roll_call_id: LegiScan roll call ID

        Returns:
            Vote information

        Example:
            >>> votes = connector.get_votes(roll_call_id=54321)
        """
        response = self._make_api_request(op="getRollCall", id=roll_call_id)
        return response.get("roll_call", {})

    @requires_license
    def get_sponsor(self, people_id: int) -> Dict[str, Any]:
        """
            Get information about a legislator/sponsor.

            Args:
                people_id: LegiScan people ID

            Returns:
                Legislator information

            Example:
                >>> sponsor = connector.get_sponsor(people_id=1
        1111)
        """
        response = self._make_api_request(op="getPerson", id=people_id)
        return response.get("person", {})

    @requires_license
    def get_session_people(self, session_id: int) -> List[Dict[str, Any]]:
        """
        Get all legislators for a session.

        Args:
            session_id: LegiScan session ID

        Returns:
            List of legislators

        Example:
            >>> people = connector.get_session_people(session_id=1234)

        """
        response = self._make_api_request(op="getSessionPeople", id=session_id)
        return response.get("sessionpeople", {}).get("people", [])

    @requires_license
    def get_master_list(self, session_id: int) -> List[Dict[str, Any]]:
        """
        Get master list of all bills in a session.

        Args:
            session_id: LegiScan session ID

        Returns:
            List of bills

        Example:
            >>> bills = connector.get_master_list(session_id=1234)
        """
        response = self._make_api_request(op="getMasterList", id=session_id)
        return response.get("masterlist", [])

    def monitor_list(self, record: str = "current") -> List[Dict[str, Any]]:
        """
            Get monitored bills list.

            Args:
                record: 'current' or 'archive'

            Returns:
                List of monitored bills

            Example:
                >>
        > monitored = connector.monitor_list()
        """
        response = self._make_api_request(op="getMonitorList", record=record)
        return response.get("monitorlist", [])

    @requires_license
    def get_dataset_list(
        self, state: Optional[str] = None, year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get available datasets for download.

        Args:
            state: State abbreviation
            year: Year

        Returns:
            List of available datasets

        Example:
            >>> datasets = connector.get_dataset_list(state='CA', year=2024)
        """
        params = {"op": "getDatasetList"}

        if state:
            params["state"] = state
        if year:
            params["year"] = year

        response = self._make_api_request(**params)
        return response.get("datasetlist", [])

    @requires_license
    def get_dataset(self, session_id: int, access_key: str) -> Dict[str, Any]:
        """
        Download a dataset.

        Args:
            session_id: LegiScan session ID
            access_key: Dataset access key

        Returns:
            Dataset download information

        Example:
            >>> dataset = connector.get_dataset(
            ...     session_id=1234,
            ...     access_key='abc123'
            ... )
        """
        response = self._make_api_request(op="getDataset", id=session_id, access_key=access_key)
        return response.get("dataset", {})

    def to_dataframe(self, bills: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Convert bills list to pandas DataFrame.

        Args:
            bills: List of bills from API

        Returns:
            DataFrame with bill information

        Example:
            >>> search_results = connector.search_bills(state='CA')
            >>> df = connector.to_dataframe(search_results.get('searchresult', []))
        """
        if not bills:
            return pd.DataFrame()

        # Flatten nested structures
        flattened = []
        for bill in bills:
            flat = {
                "bill_id": bill.get("bill_id"),
                "bill_number": bill.get("bill_number"),
                "title": bill.get("title"),
                "description": bill.get("description"),
                "state": bill.get("state"),
                "session": bill.get("session", {}).get("session_name"),
                "status": bill.get("status"),
                "status_date": bill.get("status_date"),
                "url": bill.get("url"),
            }
            flattened.append(flat)

        return pd.DataFrame(flattened)
