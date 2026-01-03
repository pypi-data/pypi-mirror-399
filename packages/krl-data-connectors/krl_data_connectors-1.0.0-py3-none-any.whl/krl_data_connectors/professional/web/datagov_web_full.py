# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Data.gov Web Domain Connector - Professional Tier

Full access to web and digital resource datasets from Data.gov,
integrated with Crawl4AI and Jina for enhanced content extraction.

Pre-configured for GSA, FCC, NTIA web data sources.
Combines Data.gov catalog discovery with web scraping capabilities.
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from krl_data_connectors.professional.civic.datagov_full import DataGovFullConnector
from krl_data_connectors.licensed_connector_mixin import requires_license


class DataGovWebFullConnector(DataGovFullConnector):
    """
    Data.gov Web Domain Connector - Professional Tier
    
    Combines Data.gov catalog search with Crawl4AI and Jina
    for web content extraction and enrichment.
    
    Features:
        - Search Data.gov for web-related datasets
        - Discover URLs and web resources from federal agencies
        - Integrate with WebScraperConnector for content extraction
        - Use JinaClient for high-accuracy article parsing
        
    Example:
        >>> connector = DataGovWebFullConnector()
        >>> connector.connect()
        >>>
        >>> # Find web datasets
        >>> datasets = connector.search_web_resources("open data portals")
        >>>
        >>> # Get URLs for scraping
        >>> urls = connector.get_scrapeable_urls(datasets)
        >>>
        >>> # Enrich with Crawl4AI
        >>> from krl_data_connectors.professional.web import WebScraperConnector
        >>> scraper = WebScraperConnector()
        >>> content = scraper.scrape_page(urls[0])
    """

    _connector_name = "DataGov_Web_Full"
    DEFAULT_DOWNLOAD_DIR = "~/.krl/data/datagov_web"

    DOMAIN_ORGANIZATIONS: List[str] = [
        "gsa-gov",            # General Services Administration
        "fcc-gov",            # Federal Communications Commission
        "ntia-commerce-gov",  # NTIA
        "data-gov",           # Data.gov itself
    ]
    
    DOMAIN_TAGS: List[str] = [
        "web",
        "api",
        "data-portal",
        "open-data",
        "digital-services",
    ]
    
    DOMAIN_NAME: str = "Web"

    POPULAR_DATASETS: Dict[str, List[str]] = {
        "apis": [
            "api-catalog",
            "data-apis",
            "web-services",
        ],
        "portals": [
            "data-portals",
            "open-data-sites",
            "catalog-data",
        ],
        "digital": [
            "digital-services",
            "website-data",
            "online-resources",
        ],
    }

    def __init__(self, *args, **kwargs):
        """Initialize the Web connector with optional Crawl4AI/Jina integration."""
        super().__init__(*args, **kwargs)
        self._scraper = None
        self._jina_client = None

    def _get_scraper(self):
        """Lazy-load the WebScraperConnector."""
        if self._scraper is None:
            try:
                from krl_data_connectors.professional.web.web_scraper import WebScraperConnector
                self._scraper = WebScraperConnector()
            except ImportError:
                self._scraper = None
        return self._scraper

    def _get_jina_client(self):
        """Lazy-load the JinaClient."""
        if self._jina_client is None:
            try:
                from krl_data_connectors.core.enrichment.jina_client import JinaClient
                self._jina_client = JinaClient()
            except ImportError:
                self._jina_client = None
        return self._jina_client

    @requires_license
    def search_web_resources(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """
        Search for web-related datasets on Data.gov.
        
        Args:
            query: Search query for web resources
            rows: Number of results to return
            
        Returns:
            DataFrame with web dataset metadata
        """
        search_query = f"web {query}" if query != "*:*" else "web api data portal"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_api_catalogs(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for API catalog datasets."""
        search_query = f"API {query}" if query != "*:*" else "API catalog web services"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_data_portals(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for open data portal datasets."""
        search_query = f"data portal {query}" if query != "*:*" else "open data portal catalog"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_digital_services(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for digital services datasets."""
        search_query = f"digital services {query}" if query != "*:*" else "digital services government"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def get_scrapeable_urls(
        self,
        datasets: pd.DataFrame,
        resource_format: Optional[str] = None,
    ) -> List[str]:
        """
        Extract scrapeable URLs from dataset resources.
        
        Args:
            datasets: DataFrame from search_datasets
            resource_format: Optional filter for resource format (html, json, etc.)
            
        Returns:
            List of URLs that can be scraped
        """
        urls = []
        
        if 'resources' not in datasets.columns:
            return urls
            
        for _, row in datasets.iterrows():
            resources = row.get('resources', [])
            if isinstance(resources, list):
                for resource in resources:
                    if isinstance(resource, dict):
                        url = resource.get('url', '')
                        fmt = resource.get('format', '').lower()
                        
                        if url:
                            if resource_format is None:
                                urls.append(url)
                            elif fmt == resource_format.lower():
                                urls.append(url)
        
        return urls

    @requires_license
    def scrape_url_with_crawl4ai(
        self,
        url: str,
        extract_tables: bool = False,
    ) -> Dict[str, Any]:
        """
        Scrape a URL using the integrated Crawl4AI WebScraperConnector.
        
        Args:
            url: URL to scrape
            extract_tables: Whether to extract HTML tables
            
        Returns:
            Dictionary with scraped content
        """
        scraper = self._get_scraper()
        if scraper is None:
            return {
                "success": False,
                "error": "WebScraperConnector not available. Install crawl4ai.",
                "url": url,
            }
        
        try:
            result = scraper.scrape_page(url)
            
            if extract_tables:
                tables = scraper.extract_table(url)
                result["tables"] = tables
                
            return {
                "success": True,
                "url": url,
                "content": result.get("content", ""),
                "title": result.get("title", ""),
                "tables": result.get("tables", []),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": url,
            }

    @requires_license
    def fetch_article_with_jina(
        self,
        url: str,
    ) -> Dict[str, Any]:
        """
        Fetch article content using the integrated Jina Reader API.
        
        Args:
            url: Article URL to fetch
            
        Returns:
            Dictionary with article content
        """
        jina = self._get_jina_client()
        if jina is None:
            return {
                "success": False,
                "error": "JinaClient not available. Set JINA_API_KEY.",
                "url": url,
            }
        
        try:
            result = jina.fetch_article(url)
            return result.to_dict()
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": url,
            }

    @requires_license
    def discover_and_scrape(
        self,
        query: str,
        max_urls: int = 10,
        use_jina: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Discover datasets from Data.gov and scrape their web resources.
        
        Args:
            query: Search query for discovering datasets
            max_urls: Maximum number of URLs to scrape
            use_jina: Whether to use Jina (True) or Crawl4AI (False)
            
        Returns:
            List of scraped content dictionaries
        """
        # Search for datasets
        datasets = self.search_web_resources(query=query, rows=max_urls * 2)
        
        # Extract URLs
        urls = self.get_scrapeable_urls(datasets)[:max_urls]
        
        # Scrape each URL
        results = []
        for url in urls:
            if use_jina:
                result = self.fetch_article_with_jina(url)
            else:
                result = self.scrape_url_with_crawl4ai(url)
            results.append(result)
        
        return results

    @requires_license
    def bulk_export_web_data(
        self,
        topic: str = "apis",
        limit: int = 1000,
        output_format: str = "parquet",
    ) -> str:
        """Bulk export web datasets."""
        return self.bulk_export_domain_data(
            topic=topic,
            limit=limit,
            output_format=output_format,
        )

    def __repr__(self) -> str:
        scraper_status = "loaded" if self._scraper else "not loaded"
        jina_status = "loaded" if self._jina_client else "not loaded"
        return (
            f"DataGovWebFullConnector("
            f"domain='{self.DOMAIN_NAME}', "
            f"organizations={self.DOMAIN_ORGANIZATIONS}, "
            f"crawl4ai={scraper_status}, "
            f"jina={jina_status})"
        )
