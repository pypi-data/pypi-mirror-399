# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ and KRL Data Connectors™ are trademarks of Deloatch, Williams, Faison, & Parker, LLLP.
# Deloatch, Williams, Faison, & Parker, LLLP
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
LocalBusiness Data Connector

Provides access to local business registry data including business permits,
licenses, registrations, and operational information. Integrates with various
local government business data sources.

Data Sources:
- Business licenses and permits
- Business registrations
- Industry classifications (NAICS codes)
- Business locations and contact information
- Operational status and compliance

Author: KR-Labs
License: Apache 2.0
"""

import logging
from datetime import datetime, UTC
from typing import Any, Dict, List, Optional

import pandas as pd
import requests

from ...base_connector import BaseConnector
from ...core import DataTier
from ...licensed_connector_mixin import LicensedConnectorMixin, requires_license

logger = logging.getLogger(__name__)


class LocalBusinessConnector(LicensedConnectorMixin, BaseConnector):
    """
    Connector for local business registry data.

    Provides access to business licenses, permits, registrations, and operational
    information from local government sources. Supports searching by location,
    industry, business type, and operational status.

    Attributes:
        BASE_NAME: Connector identifier
        BASE_URL: Base API URL for business data
        ENDPOINTS: Dictionary of available API endpoints
        BUSINESS_TYPES: Common business type classifications
        NAICS_CATEGORIES: Top-level NAICS code categories
    """

    # Registry name for license validation
    _connector_name = "Local_Business"

    BASE_NAME = "LocalBusiness"
    BASE_URL = "https://api.businessdata.gov"  # Mock URL for demonstration

    ENDPOINTS = {
        "search": "/v1/businesses/search",
        "details": "/v1/businesses/{business_id}",
        "licenses": "/v1/businesses/{business_id}/licenses",
        "permits": "/v1/businesses/{business_id}/permits",
        "inspections": "/v1/businesses/{business_id}/inspections",
        "compliance": "/v1/businesses/{business_id}/compliance",
        "locations": "/v1/locations/search",
    }

    BUSINESS_TYPES = [
        "Corporation",
        "LLC",
        "Sole Proprietorship",
        "Partnership",
        "Nonprofit",
        "Cooperative",
        "Franchise",
    ]

    NAICS_CATEGORIES = {
        "11": "Agriculture, Forestry, Fishing and Hunting",
        "21": "Mining, Quarrying, and Oil and Gas Extraction",
        "22": "Utilities",
        "23": "Construction",
        "31-33": "Manufacturing",
        "42": "Wholesale Trade",
        "44-45": "Retail Trade",
        "48-49": "Transportation and Warehousing",
        "51": "Information",
        "52": "Finance and Insurance",
        "53": "Real Estate and Rental and Leasing",
        "54": "Professional, Scientific, and Technical Services",
        "55": "Management of Companies and Enterprises",
        "56": "Administrative and Support Services",
        "61": "Educational Services",
        "62": "Health Care and Social Assistance",
        "71": "Arts, Entertainment, and Recreation",
        "72": "Accommodation and Food Services",
        "81": "Other Services",
        "92": "Public Administration",
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_dir: Optional[str] = None,
        cache_ttl: int = 86400,  # 24 hours default
        timeout: int = 30,
        max_retries: int = 3,
        **kwargs,
    ):
        """
        Initialize LocalBusiness connector.

        Args:
            api_key: API key for business data service
            cache_dir: Directory for caching responses
            cache_ttl: Cache time-to-live in seconds (default: 24 hours)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            **kwargs: Additional configuration options
        """
        super().__init__(
            api_key=api_key,
            cache_dir=cache_dir,
            cache_ttl=cache_ttl,
            timeout=timeout,
            max_retries=max_retries,
            **kwargs,
        )
        self.logger = logging.getLogger(__name__)

    def _get_api_key(self) -> Optional[str]:
        """
        Get API key for business data service.

        Returns:
            API key string or None
        """
        return self.api_key

    def connect(self) -> None:
        """
        Test connection to business data API.

        Validates API key and connectivity by performing a minimal search query.

        Raises:
            ConnectionError: If connection fails
            ValueError: If API key is invalid
        """
        if not self.api_key:
            raise ValueError("API key is required for LocalBusiness connector")

        test_url = f"{self.BASE_URL}{self.ENDPOINTS['search']}"

        try:
            response = requests.get(
                test_url,
                params={"apikey": self.api_key, "city": "Seattle", "limit": 1},
                timeout=self.timeout,
            )

            if response.status_code == 401:
                raise ValueError("Invalid API key for LocalBusiness service")
            elif response.status_code == 403:
                raise ValueError("API key does not have required permissions")

            response.raise_for_status()
            self.logger.info("Successfully connected to LocalBusiness API")

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to LocalBusiness API: {e}")

    def _make_request(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make authenticated request to business API.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            JSON response as dictionary

        Raises:
            requests.exceptions.RequestException: If request fails
        """
        url = f"{self.BASE_URL}{endpoint}"

        if params is None:
            params = {}

        params["apikey"] = self.api_key

        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()

        return response.json()

    def search_businesses(
        self,
        city: Optional[str] = None,
        state: Optional[str] = None,
        zip_code: Optional[str] = None,
        business_name: Optional[str] = None,
        naics_code: Optional[str] = None,
        business_type: Optional[str] = None,
        status: str = "active",
        limit: int = 100,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """
        Search for businesses by location and criteria.

        Args:
            city: City name
            state: State code (2-letter)
            zip_code: ZIP code
            business_name: Business name (partial match supported)
            naics_code: NAICS industry code
            business_type: Business entity type
            status: Business status (active, inactive, all)
            limit: Maximum number of results
            **kwargs: Additional search parameters

        Returns:
            List of business records
        """
        params = {"limit": min(limit, 500), "status": status}

        if city:
            params["city"] = city
        if state:
            params["state"] = state.upper()
        if zip_code:
            params["zip_code"] = zip_code
        if business_name:
            params["business_name"] = business_name
        if naics_code:
            params["naics_code"] = naics_code
        if business_type:
            params["business_type"] = business_type

        params.update(kwargs)

        data = self._make_request(self.ENDPOINTS["search"], params)
        return data.get("businesses", [])

    @requires_license
    def get_business_details(self, business_id: str) -> Dict[str, Any]:
        """
        Get detailed information for a specific business.

        Args:
            business_id: Unique business identifier

        Returns:
            Business details dictionary
        """
        endpoint = self.ENDPOINTS["details"].format(business_id=business_id)
        return self._make_request(endpoint)

    @requires_license
    def get_business_licenses(self, business_id: str) -> List[Dict[str, Any]]:
        """
        Get licenses for a specific business.

        Args:
            business_id: Unique business identifier

        Returns:
            List of license records
        """
        endpoint = self.ENDPOINTS["licenses"].format(business_id=business_id)
        data = self._make_request(endpoint)
        return data.get("licenses", [])

    @requires_license
    def get_business_permits(self, business_id: str) -> List[Dict[str, Any]]:
        """
        Get permits for a specific business.

        Args:
            business_id: Unique business identifier

        Returns:
            List of permit records
        """
        endpoint = self.ENDPOINTS["permits"].format(business_id=business_id)
        data = self._make_request(endpoint)
        return data.get("permits", [])

    @requires_license
    def get_business_inspections(self, business_id: str) -> List[Dict[str, Any]]:
        """
        Get inspection records for a specific business.

        Args:
            business_id: Unique business identifier

        Returns:
            List of inspection records
        """
        endpoint = self.ENDPOINTS["inspections"].format(business_id=business_id)
        data = self._make_request(endpoint)
        return data.get("inspections", [])

    def extract_business_info(self, business: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract standardized information from business record.

        Args:
            business: Raw business data dictionary

        Returns:
            Standardized business information
        """
        info = {
            "business_id": business.get("id"),
            "business_name": business.get("name"),
            "dba_name": business.get("dba_name"),
            "business_type": business.get("business_type"),
            "status": business.get("status"),
            "registration_date": business.get("registration_date"),
            "naics_code": business.get("naics_code"),
            "naics_description": business.get("naics_description"),
        }

        # Location information
        location = business.get("location", {})
        info["address"] = location.get("address")
        info["city"] = location.get("city")
        info["state"] = location.get("state")
        info["zip_code"] = location.get("zip_code")
        info["latitude"] = location.get("latitude")
        info["longitude"] = location.get("longitude")

        # Contact information
        contact = business.get("contact", {})
        info["phone"] = contact.get("phone")
        info["email"] = contact.get("email")
        info["website"] = contact.get("website")

        # Business metrics
        info["employee_count"] = business.get("employee_count")
        info["annual_revenue"] = business.get("annual_revenue")

        # Compliance status
        info["licenses_current"] = business.get("licenses_current", False)
        info["permits_current"] = business.get("permits_current", False)
        info["last_inspection_date"] = business.get("last_inspection_date")
        info["inspection_score"] = business.get("inspection_score")

        return info

    def fetch(
        self,
        city: Optional[str] = None,
        state: Optional[str] = None,
        naics_code: Optional[str] = None,
        business_type: Optional[str] = None,
        max_results: int = 500,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Fetch business data and return as DataFrame.

        Args:
            city: City name
            state: State code (2-letter)
            naics_code: NAICS industry code
            business_type: Business entity type
            max_results: Maximum number of results
            **kwargs: Additional search parameters

        Returns:
            DataFrame with business information
        """
        all_businesses = []

        businesses = self.search_businesses(
            city=city,
            state=state,
            naics_code=naics_code,
            business_type=business_type,
            limit=max_results,
            **kwargs,
        )

        for business in businesses:
            if len(all_businesses) >= max_results:
                break

            business_info = self.extract_business_info(business)
            business_info["fetched_at"] = datetime.now(UTC).isoformat()
            all_businesses.append(business_info)

        return pd.DataFrame(all_businesses)
