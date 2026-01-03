# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Data.gov Catalog Connector - Community Tier

Free access to the US Government's open data catalog via the CKAN API.
Provides search and metadata retrieval for 300,000+ datasets across
federal agencies including EPA, NOAA, Census, and more.

The Community tier provides:
- Catalog search (up to 50 results per query)
- Dataset metadata retrieval
- Popular dataset whitelisting by category
- Basic resource listing

For full catalog access, bulk export, and resource streaming,
upgrade to Professional tier: https://krlabs.dev/pricing

API Documentation:
- CKAN API: https://docs.ckan.org/en/2.9/api/
- Data.gov: https://data.gov/developers/apis/
- API Key Signup: https://api.data.gov/signup/

Usage:
    from krl_data_connectors.community.civic import DataGovCatalogConnector
    
    datagov = DataGovCatalogConnector()
    
    # Search datasets
    results = datagov.search_datasets("climate change", organization="epa")
    
    # Get dataset metadata
    metadata = datagov.get_dataset("some-dataset-id")
    
    # List popular datasets by category
    popular = datagov.list_popular_datasets(category="environment")
"""

import os
import time
from collections import deque
from datetime import datetime, UTC
from threading import Lock
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from krl_data_connectors.base_connector import BaseConnector
from krl_data_connectors.core import DataTier


class DataGovCatalogConnector(BaseConnector):
    """
    Data.gov Catalog Connector - Community Tier

    Free access to the US Government open data catalog (300,000+ datasets)
    via the CKAN API. No license validation required for Community tier.

    Key Features:
    - Search across all federal agency datasets
    - Filter by organization, tag, and format
    - Retrieve detailed dataset metadata
    - Access to curated popular datasets

    Limitations (Community Tier):
    - Maximum 50 results per search query
    - No bulk export functionality
    - No direct resource file streaming
    - Rate limited to ensure fair access

    API Access:
    - Base URL: https://catalog.data.gov/api/3/
    - API Key: Optional (recommended for higher rate limits)
    - Registration: https://api.data.gov/signup/
    """

    _connector_name = "DataGov_Catalog"
    _required_tier = DataTier.COMMUNITY

    BASE_URL = "https://catalog.data.gov/api/3"
    
    # Maximum results for Community tier
    MAX_RESULTS = 50
    
    # Rate limiting: Data.gov recommends max 1 request/second without API key,
    # 3 requests/second with API key. We use conservative limits to avoid 500 errors.
    RATE_LIMIT_NO_KEY = 1.0  # requests per second without API key
    RATE_LIMIT_WITH_KEY = 2.0  # requests per second with API key (conservative)
    RATE_LIMIT_WINDOW = 1.0  # sliding window in seconds

    # Domain configuration - subclasses can override these to create domain-specific connectors
    # When set, searches are automatically filtered to these organizations/tags
    DOMAIN_ORGANIZATIONS: List[str] = []  # e.g., ["epa-gov", "noaa-gov"] for environmental
    DOMAIN_TAGS: List[str] = []  # e.g., ["climate", "air-quality"] for environmental
    DOMAIN_NAME: str = ""  # Human-readable domain name, e.g., "Environmental"

    # Popular datasets curated by category for Community tier quick access
    POPULAR_DATASETS: Dict[str, List[str]] = {
        "environment": [
            "air-quality-annual-summary",
            "climate-data-online",
            "epa-air-quality-system-aqs",
            "superfund-sites",
            "water-quality-portal",
        ],
        "climate": [
            "global-historical-climatology-network",
            "noaa-climate-normals",
            "sea-level-trends",
            "drought-monitor",
            "carbon-dioxide-emissions",
        ],
        "demographics": [
            "american-community-survey",
            "census-bureau-population-estimates",
            "county-population-totals",
            "decennial-census",
            "geographic-mobility",
        ],
        "economy": [
            "bureau-of-labor-statistics",
            "county-business-patterns",
            "economic-census",
            "quarterly-census-employment-wages",
            "small-area-income-poverty-estimates",
        ],
        "health": [
            "cdc-wonder",
            "healthdata-gov-datasets",
            "medicare-provider-utilization",
            "food-and-drug-administration",
            "substance-abuse-mental-health",
        ],
        "education": [
            "college-scorecard",
            "civil-rights-data-collection",
            "elementary-secondary-information",
            "integrated-postsecondary-education",
            "national-assessment-educational-progress",
        ],
        "transportation": [
            "national-bridge-inventory",
            "fatality-analysis-reporting-system",
            "highway-performance-monitoring-system",
            "national-transit-database",
            "airline-on-time-performance",
        ],
        "agriculture": [
            "usda-national-agricultural-statistics",
            "food-access-research-atlas",
            "crop-production",
            "livestock-slaughter",
            "farm-income-wealth-statistics",
        ],
    }

    # Whitelisted organizations for filtering
    WHITELISTED_ORGANIZATIONS = {
        "epa-gov": "Environmental Protection Agency",
        "noaa-gov": "National Oceanic and Atmospheric Administration",
        "census-gov": "U.S. Census Bureau",
        "hhs-gov": "Department of Health and Human Services",
        "usda-gov": "U.S. Department of Agriculture",
        "ed-gov": "Department of Education",
        "dot-gov": "Department of Transportation",
        "dol-gov": "Department of Labor",
        "energy-gov": "Department of Energy",
        "nasa-gov": "National Aeronautics and Space Administration",
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_dir: Optional[str] = None,
        cache_ttl: int = 3600,  # 1 hour - dataset metadata changes infrequently
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        Initialize Data.gov Catalog connector.

        Args:
            api_key: Optional Data.gov API key (recommended for higher rate limits)
                     Register at: https://api.data.gov/signup/
            cache_dir: Directory for caching responses
            cache_ttl: Cache time-to-live in seconds (default: 1 hour)
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
        self.base_url = self.BASE_URL
        self.cache_ttl = cache_ttl  # Store for download_resource caching
        
        # Initialize rate limiter
        self._rate_limit = (
            self.RATE_LIMIT_WITH_KEY if self.api_key else self.RATE_LIMIT_NO_KEY
        )
        self._request_times: deque = deque(maxlen=10)
        self._rate_lock = Lock()
        
        self.logger.info(
            "Initialized Data.gov Catalog connector (Community tier)",
            extra={
                "max_results": self.MAX_RESULTS,
                "organizations": len(self.WHITELISTED_ORGANIZATIONS),
                "has_api_key": bool(self.api_key),
                "rate_limit": f"{self._rate_limit} req/s",
            },
        )

    def _get_api_key(self) -> Optional[str]:
        """
        Get API key for Data.gov API.

        For Community tier, looks for DATA_GOV_API_KEY environment variable.
        API key is optional but recommended for higher rate limits.

        Returns:
            Data.gov API key or None
        """
        return os.getenv("DATA_GOV_API_KEY")

    def _init_session(self) -> "requests.Session":
        """
        Initialize HTTP session without urllib3 retry on 5xx errors.
        
        We override the base implementation to disable automatic retries
        for server errors - our custom _make_request handles retries with
        rate limiting awareness.
        
        Returns:
            Configured requests.Session object
        """
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        if self.session is None:
            self.session = requests.Session()
            
            # Only retry on connection errors and 429 (rate limit)
            # NOT on 5xx errors - our _make_request handles those with rate limiting
            retry_strategy = Retry(
                total=self.max_retries,
                backoff_factor=1,
                status_forcelist=[429],  # Only retry on rate limit, not 5xx
                allowed_methods=["HEAD", "GET", "OPTIONS"],
            )
            
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)
            
            self.logger.debug("HTTP session initialized (Data.gov custom)")
        
        return self.session

    def _wait_for_rate_limit(self) -> None:
        """
        Implement rate limiting using a sliding window approach.
        
        Ensures requests don't exceed the configured rate limit to avoid
        API throttling and 500 errors from Data.gov.
        """
        with self._rate_lock:
            now = time.time()
            
            # Remove timestamps outside the sliding window
            while self._request_times and now - self._request_times[0] > self.RATE_LIMIT_WINDOW:
                self._request_times.popleft()
            
            # If we've hit the rate limit, wait
            if len(self._request_times) >= self._rate_limit:
                oldest_request = self._request_times[0]
                wait_time = self.RATE_LIMIT_WINDOW - (now - oldest_request)
                if wait_time > 0:
                    self.logger.debug(
                        f"Rate limiting: waiting {wait_time:.2f}s",
                        extra={"rate_limit": self._rate_limit},
                    )
                    time.sleep(wait_time)
            
            # Record this request
            self._request_times.append(time.time())

    def _make_request(
        self,
        action: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make a request to the CKAN API with rate limiting and retry logic.

        Args:
            action: CKAN action endpoint (e.g., 'package_search')
            params: Query parameters

        Returns:
            Parsed JSON response

        Raises:
            requests.HTTPError: If request fails after retries
            ValueError: If API returns error
        """
        import requests
        
        self._init_session()
        
        url = f"{self.base_url}/action/{action}"
        request_params = params or {}

        # Add API key to headers if available (CKAN uses X-CKAN-API-Key header)
        # Also include User-Agent to identify ourselves (some APIs block requests without it)
        headers = {
            "User-Agent": "KRL-Data-Connectors/1.0 (https://github.com/KR-Labs/krl-data-connectors)"
        }
        if self.api_key:
            headers["X-CKAN-API-Key"] = self.api_key

        last_error = None
        
        for attempt in range(self.max_retries + 1):
            # Apply rate limiting before each request
            self._wait_for_rate_limit()
            
            self.logger.debug(
                f"Making CKAN API request: {action}",
                extra={
                    "params": self._mask_sensitive_params(request_params),
                    "attempt": attempt + 1,
                },
            )

            try:
                response = self.session.get(
                    url,
                    params=request_params,
                    headers=headers,
                    timeout=self.timeout,
                )
                
                # Check for server errors (5xx) - retry with backoff
                if response.status_code >= 500:
                    wait_time = (2 ** attempt) * 0.5  # 0.5s, 1s, 2s, 4s
                    self.logger.warning(
                        f"Server error {response.status_code}, retrying in {wait_time:.1f}s",
                        extra={"attempt": attempt + 1, "max_retries": self.max_retries},
                    )
                    time.sleep(wait_time)
                    last_error = requests.HTTPError(
                        f"{response.status_code} Server Error for url: {url}"
                    )
                    continue
                
                response.raise_for_status()

                data = response.json()

                # Check CKAN success field
                if not data.get("success", False):
                    error = data.get("error", {})
                    raise ValueError(
                        f"CKAN API error: {error.get('message', 'Unknown error')}"
                    )

                return data.get("result", {})
            
            except requests.exceptions.RetryError as e:
                # urllib3/requests exhausted retries (e.g., persistent 429 or connection issues)
                self.logger.error(
                    f"Data.gov API unavailable after retries: {action}",
                    extra={"url": url, "error": str(e)},
                )
                raise ConnectionError(
                    f"Data.gov API is experiencing issues. The '{action}' endpoint "
                    f"is returning errors. Please try again later. "
                    f"Check https://status.data.gov for service status."
                ) from e
                
            except requests.exceptions.Timeout as e:
                wait_time = (2 ** attempt) * 0.5
                self.logger.warning(
                    f"Request timeout, retrying in {wait_time:.1f}s",
                    extra={"attempt": attempt + 1},
                )
                time.sleep(wait_time)
                last_error = e
                continue
        
        # All retries exhausted
        raise last_error or requests.HTTPError(
            f"Max retries ({self.max_retries}) exceeded for {action}"
        )

    def connect(self) -> bool:
        """
        Test connection to Data.gov CKAN API.

        Returns:
            True if connection successful
        """
        try:
            self._init_session()

            # Test with a simple status/info request
            response = self.session.get(
                f"{self.base_url}/action/status_show",
                params={"api_key": self.api_key} if self.api_key else None,
                timeout=self.timeout,
            )
            response.raise_for_status()

            data = response.json()
            if data.get("success"):
                self.logger.info("Successfully connected to Data.gov CKAN API")
                return True

            self.logger.warning("Data.gov API returned unsuccessful status")
            return False

        except Exception as e:
            self.logger.error(f"Failed to connect to Data.gov API: {str(e)}")
            return False

    def fetch(self, **kwargs) -> Any:
        """
        Generic fetch method for CKAN API.

        Supports multiple query types via the 'action' parameter:
        - 'package_search': Search datasets
        - 'package_show': Get dataset details
        - 'organization_list': List organizations
        - 'tag_list': List tags

        Args:
            action: CKAN action to execute
            **kwargs: Additional parameters for the action

        Returns:
            API response data
        """
        action = kwargs.pop("action", "package_search")
        return self._make_request(action, kwargs)

    def search_datasets(
        self,
        query: str,
        organization: Optional[str] = None,
        tags: Optional[List[str]] = None,
        formats: Optional[List[str]] = None,
        rows: int = 10,
        start: int = 0,
        sort: str = "score desc",
    ) -> pd.DataFrame:
        """
        Search the Data.gov catalog for datasets.

        Args:
            query: Search query string (searches title, description, tags)
            organization: Filter by organization ID (e.g., 'epa-gov', 'noaa-gov')
            tags: Filter by tags (list of tag names)
            formats: Filter by resource format (e.g., ['CSV', 'JSON'])
            rows: Number of results to return (max 50 for Community tier)
            start: Starting offset for pagination
            sort: Sort order (default: relevance then recency)

        Returns:
            DataFrame with dataset metadata including:
            - id: Dataset unique identifier
            - name: Dataset slug/name
            - title: Human-readable title
            - organization: Publishing organization
            - notes: Description/notes
            - tags: List of tags
            - resources: Number of resources
            - formats: Available formats
            - modified: Last modified date
            - url: Data.gov URL

        Raises:
            ValueError: If rows exceeds Community tier limit (50)

        Example:
            >>> datagov = DataGovCatalogConnector()
            >>> results = datagov.search_datasets(
            ...     "air quality",
            ...     organization="epa-gov",
            ...     formats=["CSV"]
            ... )
            >>> print(results[['title', 'organization', 'modified']].head())
        """
        # Enforce Community tier limit
        if rows > self.MAX_RESULTS:
            self.logger.warning(
                f"Requested {rows} results, limiting to {self.MAX_RESULTS} (Community tier). "
                "Upgrade to Professional for unlimited results: https://krlabs.dev/pricing"
            )
            rows = self.MAX_RESULTS

        # Build query parameters
        params: Dict[str, Any] = {
            "q": query,
            "rows": rows,
            "start": start,
            "sort": sort,
        }

        # Build filter query (fq) string
        fq_parts = []
        
        # Apply domain organization filter if set and no specific organization requested
        if not organization and self.DOMAIN_ORGANIZATIONS:
            # Use OR for multiple domain organizations
            org_filter = " OR ".join(f"organization:{org}" for org in self.DOMAIN_ORGANIZATIONS)
            fq_parts.append(f"({org_filter})")
        elif organization:
            fq_parts.append(f"organization:{organization}")
        
        # Apply domain tags filter if set
        if self.DOMAIN_TAGS and not tags:
            # Domain tags are additive hints, not strict filters
            pass  # Don't auto-filter by tags to avoid being too restrictive
            
        if tags:
            for tag in tags:
                fq_parts.append(f"tags:{tag}")
        if formats:
            for fmt in formats:
                fq_parts.append(f"res_format:{fmt}")

        if fq_parts:
            params["fq"] = " AND ".join(fq_parts)

        self.logger.info(
            f"Searching Data.gov catalog: '{query}'",
            extra={
                "organization": organization,
                "tags": tags,
                "formats": formats,
                "rows": rows,
            },
        )

        result = self._make_request("package_search", params)

        # Parse results into DataFrame
        datasets = result.get("results", [])
        count = result.get("count", 0)

        self.logger.info(
            f"Found {count} datasets, returning {len(datasets)}",
            extra={"total": count, "returned": len(datasets)},
        )

        if not datasets:
            return pd.DataFrame()

        # Extract relevant fields
        records = []
        for ds in datasets:
            resources = ds.get("resources", [])
            formats_found = list(set(r.get("format", "").upper() for r in resources if r.get("format")))

            records.append({
                "id": ds.get("id"),
                "name": ds.get("name"),
                "title": ds.get("title"),
                "organization": ds.get("organization", {}).get("title", "Unknown"),
                "organization_id": ds.get("organization", {}).get("name", ""),
                "notes": ds.get("notes", "")[:500] if ds.get("notes") else "",
                "tags": [t.get("name") for t in ds.get("tags", [])],
                "num_resources": len(resources),
                "formats": formats_found,
                "license_title": ds.get("license_title", ""),
                "modified": ds.get("metadata_modified"),
                "created": ds.get("metadata_created"),
                "url": f"https://catalog.data.gov/dataset/{ds.get('name')}",
            })

        df = pd.DataFrame(records)

        # Convert date columns
        for col in ["modified", "created"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

        return df

    def get_dataset(self, dataset_id: str) -> Dict[str, Any]:
        """
        Get detailed metadata for a specific dataset.

        Args:
            dataset_id: Dataset ID or name/slug

        Returns:
            Dictionary with full dataset metadata including:
            - id, name, title, notes (description)
            - organization details
            - tags and groups
            - resources (with download URLs)
            - license and author info
            - temporal and spatial coverage
            - update frequency

        Example:
            >>> datagov = DataGovCatalogConnector()
            >>> dataset = datagov.get_dataset("air-quality-annual-summary")
            >>> print(dataset['title'])
            >>> print([r['format'] for r in dataset['resources']])
        """
        self.logger.info(f"Fetching dataset metadata: {dataset_id}")

        result = self._make_request("package_show", {"id": dataset_id})

        # Enrich with convenience fields
        resources = result.get("resources", [])
        result["_summary"] = {
            "num_resources": len(resources),
            "formats": list(set(r.get("format", "").upper() for r in resources if r.get("format"))),
            "total_size_bytes": sum(r.get("size", 0) or 0 for r in resources),
            "download_urls": [r.get("url") for r in resources if r.get("url")],
        }

        return result

    def get_dataset_resources(self, dataset_id: str) -> pd.DataFrame:
        """
        Get resources (downloadable files) for a dataset.

        Args:
            dataset_id: Dataset ID or name/slug

        Returns:
            DataFrame with resource details:
            - id: Resource ID
            - name: Resource name
            - format: File format (CSV, JSON, XML, etc.)
            - url: Download URL
            - size: File size in bytes
            - description: Resource description
            - created/modified: Timestamps

        Note:
            Community tier provides resource URLs only.
            For streaming downloads and caching, upgrade to Professional tier.
        """
        dataset = self.get_dataset(dataset_id)
        resources = dataset.get("resources", [])

        if not resources:
            return pd.DataFrame()

        records = []
        for r in resources:
            records.append({
                "id": r.get("id"),
                "name": r.get("name"),
                "description": r.get("description", ""),
                "format": r.get("format", "").upper(),
                "mimetype": r.get("mimetype", ""),
                "url": r.get("url"),
                "size": r.get("size"),
                "created": r.get("created"),
                "modified": r.get("last_modified"),
            })

        df = pd.DataFrame(records)

        # Convert size to human-readable format
        if "size" in df.columns:
            df["size_mb"] = df["size"].apply(
                lambda x: round(x / (1024 * 1024), 2) if pd.notna(x) and x else None
            )

        return df

    def list_organizations(self, all_fields: bool = False) -> Union[List[str], pd.DataFrame]:
        """
        List organizations publishing data on Data.gov.

        Args:
            all_fields: If True, return DataFrame with full org details

        Returns:
            List of organization IDs, or DataFrame with full details
        """
        # Only include all_fields if True (CKAN has issues with all_fields=false)
        params = {"all_fields": "true"} if all_fields else {}
        result = self._make_request("organization_list", params)

        if not all_fields:
            return result

        # Return as DataFrame if all_fields requested
        records = []
        for org in result:
            records.append({
                "id": org.get("id"),
                "name": org.get("name"),
                "title": org.get("title"),
                "description": org.get("description", "")[:200],
                "image_url": org.get("image_url"),
                "package_count": org.get("package_count", 0),
                "created": org.get("created"),
            })

        return pd.DataFrame(records)

    def list_tags(self, query: Optional[str] = None) -> List[str]:
        """
        List available tags in the catalog.

        Args:
            query: Optional search query to filter tags

        Returns:
            List of tag names
        """
        params = {}
        if query:
            params["query"] = query

        result = self._make_request("tag_list", params)
        return result

    def list_popular_datasets(self, category: str) -> pd.DataFrame:
        """
        Get curated popular datasets for a category.

        This provides quick access to commonly-used datasets without
        needing to search. Categories are curated by KR-Labs.

        Args:
            category: Category name (environment, climate, demographics,
                     economy, health, education, transportation, agriculture)

        Returns:
            DataFrame with dataset metadata for popular datasets

        Raises:
            ValueError: If category is not recognized

        Example:
            >>> datagov = DataGovCatalogConnector()
            >>> climate_data = datagov.list_popular_datasets("climate")
            >>> print(climate_data[['title', 'organization']].head())
        """
        category_lower = category.lower()

        if category_lower not in self.POPULAR_DATASETS:
            available = ", ".join(self.POPULAR_DATASETS.keys())
            raise ValueError(
                f"Unknown category: '{category}'. "
                f"Available categories: {available}"
            )

        dataset_names = self.POPULAR_DATASETS[category_lower]

        self.logger.info(
            f"Fetching popular datasets for category: {category}",
            extra={"num_datasets": len(dataset_names)},
        )

        # Fetch metadata for each popular dataset
        records = []
        for name in dataset_names:
            try:
                dataset = self.get_dataset(name)
                resources = dataset.get("resources", [])

                records.append({
                    "id": dataset.get("id"),
                    "name": dataset.get("name"),
                    "title": dataset.get("title"),
                    "organization": dataset.get("organization", {}).get("title", "Unknown"),
                    "notes": dataset.get("notes", "")[:300] if dataset.get("notes") else "",
                    "num_resources": len(resources),
                    "formats": list(set(r.get("format", "").upper() for r in resources if r.get("format"))),
                    "url": f"https://catalog.data.gov/dataset/{name}",
                })
            except Exception as e:
                self.logger.warning(f"Could not fetch dataset '{name}': {str(e)}")
                continue

        return pd.DataFrame(records)

    def get_organization_datasets(
        self,
        organization: str,
        rows: int = 20,
    ) -> pd.DataFrame:
        """
        Get datasets from a specific organization.

        Args:
            organization: Organization ID (e.g., 'epa-gov', 'noaa-gov')
            rows: Number of results (max 50 for Community tier)

        Returns:
            DataFrame with dataset metadata

        Example:
            >>> datagov = DataGovCatalogConnector()
            >>> epa_data = datagov.get_organization_datasets("epa-gov", rows=20)
        """
        return self.search_datasets(
            query="*:*",  # Match all
            organization=organization,
            rows=min(rows, self.MAX_RESULTS),
        )

    def get_whitelisted_organizations(self) -> Dict[str, str]:
        """
        Get the list of curated organizations.

        Returns:
            Dictionary mapping organization ID to display name
        """
        return self.WHITELISTED_ORGANIZATIONS.copy()

    def get_categories(self) -> List[str]:
        """
        Get available curated categories for popular datasets.

        Returns:
            List of category names
        """
        return list(self.POPULAR_DATASETS.keys())

    def get_domain_organizations(self) -> List[str]:
        """
        Get the list of organizations this connector is filtered to.

        Returns:
            List of organization IDs, or empty list if not domain-filtered
        """
        return list(self.DOMAIN_ORGANIZATIONS)

    def get_domain_name(self) -> str:
        """
        Get the human-readable domain name for this connector.

        Returns:
            Domain name (e.g., "Environmental", "Health") or empty string
        """
        return self.DOMAIN_NAME

    def search_all_domains(
        self,
        query: str,
        formats: Optional[List[str]] = None,
        rows: int = 10,
        start: int = 0,
    ) -> pd.DataFrame:
        """
        Search across ALL Data.gov datasets, ignoring domain filters.

        This method bypasses any DOMAIN_ORGANIZATIONS or DOMAIN_TAGS filters,
        allowing cross-domain discovery. Useful for finding datasets that
        span multiple domains (e.g., environmental health).

        Args:
            query: Search query string
            formats: Filter by resource format (e.g., ['CSV', 'JSON'])
            rows: Number of results to return (max 50 for Community tier)
            start: Starting offset for pagination

        Returns:
            DataFrame with dataset metadata from all organizations

        Example:
            >>> # Even from an environmental connector, search all domains
            >>> env = DataGovEnvironmentalConnector()
            >>> all_results = env.search_all_domains("environmental health", rows=20)
        """
        # Temporarily disable domain filtering
        saved_orgs = self.DOMAIN_ORGANIZATIONS
        saved_tags = self.DOMAIN_TAGS
        
        try:
            self.DOMAIN_ORGANIZATIONS = []
            self.DOMAIN_TAGS = []
            return self.search_datasets(
                query=query,
                organization=None,  # Explicitly no organization filter
                tags=None,
                formats=formats,
                rows=rows,
                start=start,
            )
        finally:
            # Restore domain filtering
            self.DOMAIN_ORGANIZATIONS = saved_orgs
            self.DOMAIN_TAGS = saved_tags

    def download_resource(
        self,
        resource_url: str,
        use_cache: bool = True,
        cache_ttl: Optional[int] = None,
    ) -> bytes:
        """
        Download a resource file from Data.gov.

        Downloads the resource content with optional caching to avoid
        repeated downloads. Cached files use MD5 hash of the URL as key.

        Args:
            resource_url: URL of the resource to download
            use_cache: Whether to use local file caching (default: True)
            cache_ttl: Cache time-to-live in seconds (default: uses connector's cache_ttl)

        Returns:
            Raw bytes content of the resource

        Raises:
            requests.HTTPError: If download fails
            ValueError: If URL is invalid

        Example:
            >>> datagov = DataGovCatalogConnector(cache_dir="/tmp/krl_cache")
            >>> content = datagov.download_resource("https://data.gov/resource.csv")
            >>> # Subsequent calls use cached version
        """
        import hashlib
        import os
        import requests

        if not resource_url:
            raise ValueError("Resource URL is required")

        # Generate cache key from URL
        url_hash = hashlib.md5(resource_url.encode()).hexdigest()
        cache_ttl_used = cache_ttl if cache_ttl is not None else self.cache_ttl

        # Check cache first
        if use_cache and self.cache_dir:
            cache_path = os.path.join(self.cache_dir, f"resource_{url_hash}.bin")
            
            if os.path.exists(cache_path):
                # Check if cache is still valid
                cache_age = time.time() - os.path.getmtime(cache_path)
                if cache_age < cache_ttl_used:
                    self.logger.debug(
                        f"Using cached resource: {cache_path}",
                        extra={"age_seconds": cache_age, "ttl": cache_ttl_used},
                    )
                    with open(cache_path, "rb") as f:
                        return f.read()
                else:
                    self.logger.debug(f"Cache expired for: {cache_path}")

        # Apply rate limiting
        self._wait_for_rate_limit()

        self.logger.info(
            f"Downloading resource: {resource_url[:100]}...",
            extra={"use_cache": use_cache},
        )

        # Make download request
        self._init_session()
        headers = {
            "User-Agent": "KRL-Data-Connectors/1.0 (https://github.com/KR-Labs/krl-data-connectors)"
        }
        
        response = self.session.get(
            resource_url,
            headers=headers,
            timeout=self.timeout * 3,  # Longer timeout for downloads
            stream=True,
        )
        response.raise_for_status()

        # Read content
        content = response.content

        # Save to cache if enabled
        if use_cache and self.cache_dir:
            os.makedirs(self.cache_dir, exist_ok=True)
            cache_path = os.path.join(self.cache_dir, f"resource_{url_hash}.bin")
            with open(cache_path, "wb") as f:
                f.write(content)
            self.logger.debug(f"Cached resource: {cache_path}")

        return content

    def fetch_as_dataframe(
        self,
        dataset_id: str,
        resource_index: int = 0,
        format_hint: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Fetch a dataset resource and load it as a DataFrame.

        Downloads the specified resource from a dataset and automatically
        detects the format to parse it into a pandas DataFrame.

        Args:
            dataset_id: Dataset ID or name
            resource_index: Index of the resource to download (default: 0, first resource)
            format_hint: Optional format hint ('csv', 'json', 'geojson', 'excel', 'xml')
                        If not provided, format is auto-detected from URL/content-type

        Returns:
            DataFrame containing the resource data

        Raises:
            ValueError: If dataset has no resources or format is unsupported
            requests.HTTPError: If download fails

        Example:
            >>> datagov = DataGovCatalogConnector()
            >>> df = datagov.fetch_as_dataframe("air-quality-annual-summary")
            >>> print(df.head())
        """
        from krl_data_connectors.utils.formats import (
            detect_format,
            load_resource_to_dataframe,
        )

        # Get dataset metadata
        dataset = self.get_dataset(dataset_id)
        resources = dataset.get("resources", [])

        if not resources:
            raise ValueError(f"Dataset '{dataset_id}' has no downloadable resources")

        if resource_index >= len(resources):
            raise ValueError(
                f"Resource index {resource_index} out of range. "
                f"Dataset has {len(resources)} resources (0-{len(resources)-1})"
            )

        resource = resources[resource_index]
        resource_url = resource.get("url")
        resource_format = resource.get("format", "").lower()
        resource_name = resource.get("name", "")

        if not resource_url:
            raise ValueError(f"Resource at index {resource_index} has no URL")

        self.logger.info(
            f"Fetching resource as DataFrame: {resource_name or resource_url[:50]}",
            extra={
                "dataset": dataset_id,
                "format": resource_format,
                "resource_index": resource_index,
            },
        )

        # Detect format
        detected_format = format_hint or detect_format(
            url=resource_url,
            filename=resource_name,
            format_hint=resource_format,
        )

        if not detected_format:
            raise ValueError(
                f"Could not detect format for resource. "
                f"Available info: url={resource_url}, format={resource_format}. "
                f"Try specifying format_hint='csv', 'json', 'geojson', 'excel', or 'xml'"
            )

        # Download and parse
        content = self.download_resource(resource_url)
        
        return load_resource_to_dataframe(
            source=content,
            format=detected_format,
            url=resource_url,
        )

    def __repr__(self) -> str:
        return (
            f"DataGovCatalogConnector("
            f"tier={self._required_tier.value}, "
            f"max_results={self.MAX_RESULTS}, "
            f"has_api_key={bool(self.api_key)})"
        )
