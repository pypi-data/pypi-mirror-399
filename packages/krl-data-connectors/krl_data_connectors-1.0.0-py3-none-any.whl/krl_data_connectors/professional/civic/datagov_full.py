# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Data.gov Full Connector - Professional Tier

Full access to the US Government's open data catalog via the CKAN API.
Provides comprehensive search, bulk export, and resource streaming
for 300,000+ datasets across federal agencies.

The Professional tier provides:
- Unlimited search results (no 50-result cap)
- Bulk dataset export functionality
- Resource file streaming and local caching
- Advanced filtering by organization, tag, license, format
- Parallel download support
- Full organization and group metadata

API Documentation:
- CKAN API: https://docs.ckan.org/en/2.9/api/
- Data.gov: https://data.gov/developers/apis/
- API Key Signup: https://api.data.gov/signup/ (REQUIRED for Professional tier)

Usage:
    from krl_data_connectors.professional.civic import DataGovFullConnector
    
    datagov = DataGovFullConnector(api_key="your_data_gov_api_key")
    
    # Search with no result limit
    results = datagov.search_datasets("climate", rows=500)
    
    # Bulk export datasets
    bulk_data = datagov.bulk_export(organization="epa-gov", max_datasets=1000)
    
    # Download and cache resource files
    filepath = datagov.download_resource(resource_id, cache=True)
"""

import hashlib
import os
import shutil
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, UTC
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Generator, Iterator, List, Optional, Tuple, Union

import pandas as pd

from krl_data_connectors.base_connector import BaseConnector
from krl_data_connectors.core import DataTier
from krl_data_connectors.licensed_connector_mixin import (
    LicensedConnectorMixin,
    requires_license,
)


class DataGovFullConnector(LicensedConnectorMixin, BaseConnector):
    """
    Data.gov Full Connector - Professional Tier

    Full access to the US Government open data catalog (300,000+ datasets)
    via the CKAN API. Requires Professional license for access.

    Key Features:
    - Unlimited search results
    - Bulk dataset export
    - Resource file streaming with local caching
    - Advanced multi-filter queries
    - Organization and group management
    - Parallel downloads for efficiency

    Professional tier includes:
    - No result limits
    - Resource streaming (CSV, JSON, XML, etc.)
    - Local file caching
    - Bulk export up to 10,000 datasets
    - Full API access with higher rate limits

    API Access:
    - Base URL: https://catalog.data.gov/api/3/
    - API Key: Required (register at https://api.data.gov/signup/)
    - License: Professional tier required
    """

    _connector_name = "DataGov_Full"
    _required_tier = DataTier.PROFESSIONAL

    BASE_URL = "https://catalog.data.gov/api/3"

    # Professional tier limits (higher than Community)
    MAX_BULK_EXPORT = 10000
    DEFAULT_DOWNLOAD_DIR = "~/.krl/data/datagov"
    MAX_PARALLEL_DOWNLOADS = 5
    STREAM_CHUNK_SIZE = 8192  # 8KB chunks for streaming
    
    # Rate limiting: Professional tier gets higher limits with API key
    # Data.gov recommends max 3 requests/second with API key
    RATE_LIMIT_NO_KEY = 1.0  # requests per second without API key
    RATE_LIMIT_WITH_KEY = 3.0  # requests per second with API key
    RATE_LIMIT_WINDOW = 1.0  # sliding window in seconds

    # Domain configuration - subclasses can override these to create domain-specific connectors
    # When set, searches are automatically filtered to these organizations/tags
    DOMAIN_ORGANIZATIONS: List[str] = []  # e.g., ["epa-gov", "noaa-gov"] for environmental
    DOMAIN_TAGS: List[str] = []  # e.g., ["climate", "air-quality"] for environmental
    DOMAIN_NAME: str = ""  # Human-readable domain name, e.g., "Environmental"

    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_dir: Optional[str] = None,
        download_dir: Optional[str] = None,
        cache_ttl: int = 3600,
        timeout: int = 60,
        max_retries: int = 3,
    ):
        """
        Initialize Data.gov Full connector.

        Args:
            api_key: Data.gov API key (required for Professional tier)
                     Register at: https://api.data.gov/signup/
            cache_dir: Directory for API response caching
            download_dir: Directory for downloaded resource files
            cache_ttl: Cache time-to-live in seconds
            timeout: Request timeout in seconds (higher for large downloads)
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

        # Set up download directory
        self.download_dir = Path(
            os.path.expanduser(download_dir or self.DEFAULT_DOWNLOAD_DIR)
        )
        self.download_dir.mkdir(parents=True, exist_ok=True)

        if not self.api_key:
            self.logger.warning(
                "No API key provided. Data.gov API requires registration. "
                "Register at: https://api.data.gov/signup/"
            )
        
        # Initialize rate limiter
        self._rate_limit = (
            self.RATE_LIMIT_WITH_KEY if self.api_key else self.RATE_LIMIT_NO_KEY
        )
        self._request_times: deque = deque(maxlen=10)
        self._rate_lock = Lock()

        self.logger.info(
            "Initialized Data.gov Full connector (Professional tier)",
            extra={
                "download_dir": str(self.download_dir),
                "has_api_key": bool(self.api_key),
                "rate_limit": f"{self._rate_limit} req/s",
            },
        )

    def _get_api_key(self) -> Optional[str]:
        """
        Get API key for Data.gov API.

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
            action: CKAN action endpoint
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

        # Add API key to headers (CKAN uses X-CKAN-API-Key header)
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

            return False

        except Exception as e:
            self.logger.error(f"Failed to connect to Data.gov API: {str(e)}")
            return False

    @requires_license
    def fetch(self, **kwargs) -> Any:
        """
        Generic fetch method for CKAN API.

        Supports all CKAN actions without restrictions.

        Args:
            action: CKAN action to execute
            **kwargs: Additional parameters

        Returns:
            API response data
        """
        action = kwargs.pop("action", "package_search")
        return self._make_request(action, kwargs)

    @requires_license
    def search_datasets(
        self,
        query: str = "*:*",
        organization: Optional[str] = None,
        groups: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        formats: Optional[List[str]] = None,
        license_id: Optional[str] = None,
        rows: int = 100,
        start: int = 0,
        sort: str = "score desc",
        include_private: bool = False,
        include_drafts: bool = False,
    ) -> pd.DataFrame:
        """
        Search the Data.gov catalog with full Professional tier access.

        Args:
            query: Search query string (default: all datasets)
            organization: Filter by organization ID
            groups: Filter by group IDs
            tags: Filter by tags
            formats: Filter by resource format
            license_id: Filter by license ID
            rows: Number of results to return (no limit)
            start: Starting offset for pagination
            sort: Sort order
            include_private: Include private datasets
            include_drafts: Include draft datasets

        Returns:
            DataFrame with comprehensive dataset metadata
        """
        params: Dict[str, Any] = {
            "q": query,
            "rows": rows,
            "start": start,
            "sort": sort,
        }

        # Build filter query
        fq_parts = []
        
        # Apply domain organization filter if set and no specific organization requested
        if not organization and self.DOMAIN_ORGANIZATIONS:
            # Use OR for multiple domain organizations
            org_filter = " OR ".join(f"organization:{org}" for org in self.DOMAIN_ORGANIZATIONS)
            fq_parts.append(f"({org_filter})")
        elif organization:
            fq_parts.append(f"organization:{organization}")
            
        if groups:
            for group in groups:
                fq_parts.append(f"groups:{group}")
        if tags:
            for tag in tags:
                fq_parts.append(f"tags:{tag}")
        if formats:
            for fmt in formats:
                fq_parts.append(f"res_format:{fmt}")
        if license_id:
            fq_parts.append(f"license_id:{license_id}")
        if not include_private:
            fq_parts.append("private:false")
        if not include_drafts:
            fq_parts.append("state:active")

        if fq_parts:
            params["fq"] = " AND ".join(fq_parts)

        self.logger.info(
            f"Searching Data.gov catalog (Professional): '{query}'",
            extra={"rows": rows, "start": start, "filters": len(fq_parts)},
        )

        result = self._make_request("package_search", params)

        datasets = result.get("results", [])
        count = result.get("count", 0)

        self.logger.info(
            f"Found {count} datasets, returning {len(datasets)}",
            extra={"total": count, "returned": len(datasets)},
        )

        if not datasets:
            return pd.DataFrame()

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
                "notes": ds.get("notes", ""),
                "tags": [t.get("name") for t in ds.get("tags", [])],
                "groups": [g.get("name") for g in ds.get("groups", [])],
                "num_resources": len(resources),
                "formats": formats_found,
                "license_id": ds.get("license_id", ""),
                "license_title": ds.get("license_title", ""),
                "author": ds.get("author", ""),
                "maintainer": ds.get("maintainer", ""),
                "modified": ds.get("metadata_modified"),
                "created": ds.get("metadata_created"),
                "state": ds.get("state", ""),
                "type": ds.get("type", ""),
                "url": f"https://catalog.data.gov/dataset/{ds.get('name')}",
            })

        df = pd.DataFrame(records)

        for col in ["modified", "created"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

        return df

    @requires_license
    def get_dataset(self, dataset_id: str) -> Dict[str, Any]:
        """
        Get detailed metadata for a specific dataset.

        Args:
            dataset_id: Dataset ID or name/slug

        Returns:
            Dictionary with full dataset metadata
        """
        self.logger.info(f"Fetching dataset metadata: {dataset_id}")

        result = self._make_request("package_show", {"id": dataset_id})

        resources = result.get("resources", [])
        result["_summary"] = {
            "num_resources": len(resources),
            "formats": list(set(r.get("format", "").upper() for r in resources if r.get("format"))),
            "total_size_bytes": sum(r.get("size", 0) or 0 for r in resources),
            "download_urls": [r.get("url") for r in resources if r.get("url")],
        }

        return result

    @requires_license
    def get_dataset_resources(self, dataset_id: str) -> pd.DataFrame:
        """
        Get resources (downloadable files) for a dataset.

        Args:
            dataset_id: Dataset ID or name/slug

        Returns:
            DataFrame with resource details
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
                "hash": r.get("hash"),
                "created": r.get("created"),
                "modified": r.get("last_modified"),
            })

        df = pd.DataFrame(records)

        if "size" in df.columns:
            df["size_mb"] = df["size"].apply(
                lambda x: round(x / (1024 * 1024), 2) if pd.notna(x) and x else None
            )

        return df

    @requires_license
    def download_resource(
        self,
        resource_id: str,
        destination: Optional[str] = None,
        cache: bool = True,
        overwrite: bool = False,
    ) -> Path:
        """
        Download a resource file with streaming and caching.

        Args:
            resource_id: Resource ID
            destination: Custom destination path (uses cache dir if not provided)
            cache: Whether to cache the file locally
            overwrite: Overwrite existing cached file

        Returns:
            Path to the downloaded file

        Raises:
            ValueError: If resource not found
            IOError: If download fails
        """
        self._init_session()

        # Get resource metadata
        resource = self._make_request("resource_show", {"id": resource_id})
        url = resource.get("url")
        format_ext = resource.get("format", "").lower() or "dat"
        resource_name = resource.get("name", resource_id)

        if not url:
            raise ValueError(f"No download URL for resource: {resource_id}")

        # Determine destination path
        if destination:
            dest_path = Path(destination)
        else:
            # Use hash-based filename for caching
            url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
            filename = f"{resource_name}_{url_hash}.{format_ext}"
            filename = "".join(c if c.isalnum() or c in "._-" else "_" for c in filename)
            dest_path = self.download_dir / filename

        # Check cache
        if cache and dest_path.exists() and not overwrite:
            self.logger.info(f"Using cached resource: {dest_path}")
            return dest_path

        self.logger.info(
            f"Downloading resource: {resource_id}",
            extra={"url": url, "destination": str(dest_path)},
        )

        # Stream download
        try:
            response = self.session.get(url, stream=True, timeout=self.timeout)
            response.raise_for_status()

            # Create parent directories
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Write to temp file then rename (atomic)
            temp_path = dest_path.with_suffix(".tmp")
            total_size = 0

            with open(temp_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=self.STREAM_CHUNK_SIZE):
                    if chunk:
                        f.write(chunk)
                        total_size += len(chunk)

            # Rename temp to final
            shutil.move(str(temp_path), str(dest_path))

            self.logger.info(
                f"Downloaded resource: {dest_path}",
                extra={"size_bytes": total_size, "size_mb": round(total_size / (1024 * 1024), 2)},
            )

            return dest_path

        except Exception as e:
            # Clean up temp file on failure
            temp_path = dest_path.with_suffix(".tmp")
            if temp_path.exists():
                temp_path.unlink()
            raise IOError(f"Failed to download resource: {str(e)}") from e

    @requires_license
    def download_dataset_resources(
        self,
        dataset_id: str,
        formats: Optional[List[str]] = None,
        max_resources: int = 10,
        parallel: bool = True,
    ) -> List[Tuple[str, Path]]:
        """
        Download multiple resources from a dataset.

        Args:
            dataset_id: Dataset ID or name
            formats: Filter by format (e.g., ['CSV', 'JSON'])
            max_resources: Maximum resources to download
            parallel: Use parallel downloads

        Returns:
            List of tuples (resource_id, file_path)
        """
        resources_df = self.get_dataset_resources(dataset_id)

        if resources_df.empty:
            return []

        # Filter by format if specified
        if formats:
            formats_upper = [f.upper() for f in formats]
            resources_df = resources_df[resources_df["format"].isin(formats_upper)]

        resources_df = resources_df.head(max_resources)

        resource_ids = resources_df["id"].tolist()

        if not resource_ids:
            return []

        self.logger.info(
            f"Downloading {len(resource_ids)} resources from {dataset_id}",
            extra={"parallel": parallel},
        )

        results = []

        if parallel and len(resource_ids) > 1:
            with ThreadPoolExecutor(max_workers=self.MAX_PARALLEL_DOWNLOADS) as executor:
                futures = {
                    executor.submit(self.download_resource, rid): rid
                    for rid in resource_ids
                }

                for future in as_completed(futures):
                    rid = futures[future]
                    try:
                        path = future.result()
                        results.append((rid, path))
                    except Exception as e:
                        self.logger.error(f"Failed to download {rid}: {str(e)}")
        else:
            for rid in resource_ids:
                try:
                    path = self.download_resource(rid)
                    results.append((rid, path))
                except Exception as e:
                    self.logger.error(f"Failed to download {rid}: {str(e)}")

        return results

    @requires_license
    def bulk_export(
        self,
        organization: Optional[str] = None,
        tags: Optional[List[str]] = None,
        formats: Optional[List[str]] = None,
        max_datasets: int = 1000,
        include_resources: bool = False,
    ) -> pd.DataFrame:
        """
        Bulk export dataset metadata from the catalog.

        Args:
            organization: Filter by organization ID
            tags: Filter by tags
            formats: Filter by resource format
            max_datasets: Maximum datasets to export (max 10,000)
            include_resources: Include resource details (slower)

        Returns:
            DataFrame with all matching dataset metadata
        """
        if max_datasets > self.MAX_BULK_EXPORT:
            self.logger.warning(
                f"Limiting bulk export to {self.MAX_BULK_EXPORT} datasets"
            )
            max_datasets = self.MAX_BULK_EXPORT

        self.logger.info(
            f"Starting bulk export (max {max_datasets} datasets)",
            extra={"organization": organization, "tags": tags, "formats": formats},
        )

        all_records = []
        rows_per_request = 500
        start = 0

        while len(all_records) < max_datasets:
            remaining = max_datasets - len(all_records)
            rows = min(rows_per_request, remaining)

            df = self.search_datasets(
                query="*:*",
                organization=organization,
                tags=tags,
                formats=formats,
                rows=rows,
                start=start,
            )

            if df.empty:
                break

            all_records.extend(df.to_dict("records"))
            start += len(df)

            self.logger.debug(
                f"Bulk export progress: {len(all_records)}/{max_datasets}"
            )

            if len(df) < rows:
                break

        result_df = pd.DataFrame(all_records)

        self.logger.info(
            f"Bulk export complete: {len(result_df)} datasets",
            extra={"total": len(result_df)},
        )

        return result_df

    @requires_license
    def stream_search_results(
        self,
        query: str = "*:*",
        organization: Optional[str] = None,
        batch_size: int = 100,
        max_results: Optional[int] = None,
    ) -> Generator[pd.DataFrame, None, None]:
        """
        Stream search results in batches (memory-efficient).

        Args:
            query: Search query
            organization: Filter by organization
            batch_size: Results per batch
            max_results: Maximum total results (None for all)

        Yields:
            DataFrame batches of search results
        """
        start = 0
        total_yielded = 0

        while True:
            if max_results:
                remaining = max_results - total_yielded
                if remaining <= 0:
                    break
                batch_size = min(batch_size, remaining)

            df = self.search_datasets(
                query=query,
                organization=organization,
                rows=batch_size,
                start=start,
            )

            if df.empty:
                break

            yield df

            total_yielded += len(df)
            start += len(df)

            if len(df) < batch_size:
                break

    @requires_license
    def list_organizations(self, all_fields: bool = True) -> Union[List[str], pd.DataFrame]:
        """
        List all organizations with full details.

        Args:
            all_fields: If True, return DataFrame with full details

        Returns:
            List or DataFrame of organizations
        """
        # Only include all_fields if True (CKAN has issues with all_fields=false)
        params = {"all_fields": "true"} if all_fields else {}
        result = self._make_request("organization_list", params)

        if not all_fields:
            return result

        records = []
        for org in result:
            records.append({
                "id": org.get("id"),
                "name": org.get("name"),
                "title": org.get("title"),
                "description": org.get("description", ""),
                "image_url": org.get("image_url"),
                "package_count": org.get("package_count", 0),
                "created": org.get("created"),
                "state": org.get("state"),
                "approval_status": org.get("approval_status"),
            })

        return pd.DataFrame(records)

    @requires_license
    def list_groups(self, all_fields: bool = True) -> Union[List[str], pd.DataFrame]:
        """
        List all groups (topic categories).

        Args:
            all_fields: If True, return DataFrame with full details

        Returns:
            List or DataFrame of groups
        """
        result = self._make_request("group_list", {"all_fields": all_fields})

        if not all_fields:
            return result

        records = []
        for grp in result:
            records.append({
                "id": grp.get("id"),
                "name": grp.get("name"),
                "title": grp.get("title"),
                "description": grp.get("description", ""),
                "image_url": grp.get("image_url"),
                "package_count": grp.get("package_count", 0),
                "created": grp.get("created"),
            })

        return pd.DataFrame(records)

    @requires_license
    def list_licenses(self) -> List[Dict[str, Any]]:
        """
        List available license types.

        Returns:
            List of license dictionaries
        """
        return self._make_request("license_list")

    @requires_license
    def get_catalog_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the Data.gov catalog.

        Uses parallel requests for improved performance while respecting
        the shared rate limit.

        Returns:
            Dictionary with catalog statistics
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed

        # Define API calls to make in parallel
        api_calls = {
            "datasets": ("package_search", {"rows": 0}),
            "organizations": ("organization_list", {}),
            "groups": ("group_list", {}),
            "tags": ("tag_list", {}),
        }

        results = {}
        errors = []

        # Execute API calls in parallel (rate limiter is thread-safe)
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(self._make_request, action, params): name
                for name, (action, params) in api_calls.items()
            }

            for future in as_completed(futures):
                name = futures[future]
                try:
                    results[name] = future.result()
                except Exception as e:
                    self.logger.warning(f"Failed to get {name}: {e}")
                    errors.append(name)
                    results[name] = None

        return {
            "total_datasets": results.get("datasets", {}).get("count", 0) if results.get("datasets") else 0,
            "total_organizations": len(results.get("organizations") or []),
            "total_groups": len(results.get("groups") or []),
            "total_tags": len(results.get("tags") or []),
            "retrieved_at": datetime.now(UTC).isoformat(),
            "errors": errors if errors else None,
        }

    def clear_download_cache(self) -> int:
        """
        Clear the local download cache.

        Returns:
            Number of files removed
        """
        if not self.download_dir.exists():
            return 0

        files_removed = 0
        for file in self.download_dir.iterdir():
            if file.is_file():
                file.unlink()
                files_removed += 1

        self.logger.info(f"Cleared download cache: {files_removed} files removed")
        return files_removed

    def get_cache_size(self) -> Dict[str, Any]:
        """
        Get the size of the download cache.

        Returns:
            Dictionary with cache statistics
        """
        if not self.download_dir.exists():
            return {"total_files": 0, "total_size_bytes": 0, "total_size_mb": 0}

        files = list(self.download_dir.iterdir())
        total_size = sum(f.stat().st_size for f in files if f.is_file())

        return {
            "total_files": len(files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "cache_dir": str(self.download_dir),
        }

    @requires_license
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

        Professional tier includes:
        - No file size limits
        - Streaming download for large files
        - Full caching support

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
            >>> datagov = DataGovFullConnector()
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
        resource_id = resource.get("id", f"resource_{resource_index}")

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

        # Use download_resource for caching (Professional tier already has this)
        downloaded_path = self.download_resource(dataset_id, resource_id)
        
        # Load from file path
        with open(downloaded_path, "rb") as f:
            content = f.read()
        
        return load_resource_to_dataframe(
            source=content,
            format=detected_format,
            url=resource_url,
        )

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

    @requires_license
    def search_all_domains(
        self,
        query: str,
        formats: Optional[List[str]] = None,
        rows: int = 100,
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
            rows: Number of results to return (unlimited for Professional)
            start: Starting offset for pagination

        Returns:
            DataFrame with dataset metadata from all organizations

        Example:
            >>> # Even from an environmental connector, search all domains
            >>> env = DataGovEnvironmentalFullConnector()
            >>> all_results = env.search_all_domains("environmental health", rows=200)
        """
        # Temporarily disable domain filtering
        saved_orgs = self.DOMAIN_ORGANIZATIONS
        saved_tags = self.DOMAIN_TAGS
        
        try:
            self.DOMAIN_ORGANIZATIONS = []
            self.DOMAIN_TAGS = []
            return self.search_datasets(
                query=query,
                organization=None,
                tags=None,
                formats=formats,
                rows=rows,
                start=start,
            )
        finally:
            # Restore domain filtering
            self.DOMAIN_ORGANIZATIONS = saved_orgs
            self.DOMAIN_TAGS = saved_tags

    def __repr__(self) -> str:
        return (
            f"DataGovFullConnector("
            f"tier={self._required_tier.value}, "
            f"download_dir='{self.download_dir}', "
            f"has_api_key={bool(self.api_key)})"
        )
