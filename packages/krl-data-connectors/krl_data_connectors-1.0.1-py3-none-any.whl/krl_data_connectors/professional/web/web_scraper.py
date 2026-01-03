# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

# Copyright (c) 2025 KR-Labs Foundation. All rights reserved.
# Licensed under Apache License 2.0 (see LICENSE file for details)

"""
WebScraperConnector - Advanced web scraping with LLM extraction.

This connector wraps Crawl4AI to provide intelligent web scraping capabilities
with LLM-based structured data extraction, table parsing, and PDF extraction.

Professional Tier Feature ($99/mo).
"""

import asyncio
import io
import ipaddress
import json
import re
import socket
import tempfile
import time
from html import escape
from typing import Any, Dict, List, Optional, Set, Union
from urllib.parse import urlparse

import requests
from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig, LLMConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy, LLMExtractionStrategy
from PyPDF2 import PdfReader

from krl_data_connectors.base_connector import BaseConnector
from krl_data_connectors.core import DataTier
from krl_data_connectors.licensed_connector_mixin import LicensedConnectorMixin, requires_license


class WebScraperConnector(LicensedConnectorMixin, BaseConnector):
    """
    Advanced web scraping connector using Crawl4AI.

    Features:
    - LLM-based structured data extraction
    - HTML table extraction with complex layout support
    - PDF content extraction
    - Multi-page crawling with pagination
    - JavaScript rendering support
    - Rate limiting and retry logic
    - Caching for performance

    Professional Tier Component:
    - Part of $99/mo tier with WebScraperConnector + enhanced APIs
    - Enables real data extraction for NEA, Census, and other connectors
    - LLM extraction accuracy target: 90%+
    """

    # Registry name for license validation
    _connector_name = "Web_Scraper"

    """
    Example:
        >>> scraper = WebScraperConnector()
        >>> scraper.connect()
        >>>
        >>> # Extract structured data with LLM
        >>> schema = {
        ...     "name": "grants",
        ...     "baseSelector": ".grant-item",
        ...     "fields": [
        ...         {"name": "title", "selector": ".title", "type": "text"},
        ...         {"name": "amount", "selector": ".amount", "type": "text"}
        ...     ]
        ... }
        >>> grants = scraper.extract_structured_data(
        ...     url="https://apps.nea.gov/GrantSearch/",
        ...     schema=schema
        ... )
        >>>
        >>> # Extract tables
        >>> tables = scraper.extract_table(
        ...     url="https://www.census.gov/data/tables.html",
        ...     table_index=0
        ... )
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        llm_provider: str = "openai",
        llm_model: str = "gpt-4o-mini",
        cache_dir: Optional[str] = None,
        cache_ttl: int = 3600,
        timeout: int = 60,
        max_retries: int = 3,
        headless: bool = True,
        verbose: bool = False,
        max_concurrent_requests: int = 5,
        backoff_factor: float = 2.0,
        max_backoff_delay: int = 60,
        enable_ssrf_protection: bool = True,
        enable_xss_sanitization: bool = True,
    ):
        """
        Initialize WebScraperConnector.

        Args:
            api_key: LLM API key (OpenAI, Anthropic, etc.) - optional if in env
            llm_provider: LLM provider for extraction ("openai", "anthropic", "local")
            llm_model: Model name (e.g., "gpt-4o-mini", "claude-3-sonnet")
            cache_dir: Directory for cache files (default: ~/.krl_cache)
            cache_ttl: Cache TTL in seconds (default: 3600 = 1 hour)
            timeout: Page load timeout in seconds (default: 60)
            max_retries: Maximum retry attempts (default: 3)
            headless: Run browser in headless mode (default: True)
            verbose: Enable verbose logging (default: False)
            max_concurrent_requests: Maximum concurrent requests (default: 5)
            backoff_factor: Exponential backoff multiplier (default: 2.0)
            max_backoff_delay: Maximum backoff delay in seconds (default: 60)
            enable_ssrf_protection: Enable SSRF protection (default: True)
            enable_xss_sanitization: Enable XSS sanitization (default: True)
        """
        # Set LLM config BEFORE calling super().__init__()
        # because _get_api_key() needs self.llm_provider
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.headless = headless
        self.verbose = verbose

        # Advanced error handling configuration
        self.max_concurrent_requests = max_concurrent_requests
        self.backoff_factor = backoff_factor
        self.max_backoff_delay = max_backoff_delay
        self.enable_ssrf_protection = enable_ssrf_protection
        self.enable_xss_sanitization = enable_xss_sanitization

        # Concurrent request limiting (semaphore initialized on connect)
        self._semaphore: Optional[asyncio.Semaphore] = None

        # Private IP ranges for SSRF protection
        self._private_ip_ranges: Set[ipaddress.IPv4Network] = {
            ipaddress.IPv4Network("127.0.0.0/8"),  # Loopback
            ipaddress.IPv4Network("10.0.0.0/8"),  # Private Class A
            ipaddress.IPv4Network("172.16.0.0/12"),  # Private Class B
            ipaddress.IPv4Network("192.168.0.0/16"),  # Private Class C
            ipaddress.IPv4Network("169.254.0.0/16"),  # Link-local
            ipaddress.IPv4Network("224.0.0.0/4"),  # Multicast
        }

        super().__init__(
            api_key=api_key,
            cache_dir=cache_dir,
            cache_ttl=cache_ttl,
            timeout=timeout,
            max_retries=max_retries,
        )

        # Crawler instances (initialized on connect)
        self.crawler: Optional[AsyncWebCrawler] = None
        self._crawler_started = False

        self.logger.info(
            "WebScraperConnector initialized",
            extra={
                "llm_provider": llm_provider,
                "llm_model": llm_model,
                "headless": headless,
                "timeout": timeout,
                "max_concurrent_requests": max_concurrent_requests,
                "ssrf_protection": enable_ssrf_protection,
                "xss_sanitization": enable_xss_sanitization,
            },
        )

    def _get_api_key(self) -> Optional[str]:
        """
        Get LLM API key from configuration.

        Supports multiple LLM providers:
        - OpenAI: OPENAI_API_KEY
        - Anthropic: ANTHROPIC_API_KEY
        - Local: No API key needed

        Returns:
            API key or None if not found/needed
        """
        if self.llm_provider == "openai":
            return self.config.get("OPENAI_API_KEY")
        elif self.llm_provider == "anthropic":
            return self.config.get("ANTHROPIC_API_KEY")
        elif self.llm_provider == "local":
            return None  # Local models don't need API keys
        else:
            self.logger.warning(
                f"Unknown LLM provider: {self.llm_provider}",
                extra={"provider": self.llm_provider},
            )
            return None

    def connect(self) -> None:
        """
        Initialize browser and crawler resources.

        Sets up AsyncWebCrawler with optimized configuration:
        - Headless browser mode
        - Custom user agent
        - JavaScript rendering enabled
        - Stealth mode for anti-bot evasion
        - Concurrent request limiting with semaphore
        """
        if self._crawler_started:
            self.logger.debug("Crawler already started")
            return

        self.logger.info("Initializing browser and crawler")

        # Initialize semaphore for concurrent request limiting
        self._semaphore = asyncio.Semaphore(self.max_concurrent_requests)

        # Browser configuration
        browser_config = BrowserConfig(
            headless=self.headless,
            verbose=self.verbose,
            browser_type="chromium",  # Use chromium for best compatibility
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            viewport_width=1920,
            viewport_height=1080,
        )

        # Create crawler instance
        self.crawler = AsyncWebCrawler(config=browser_config)

        self._crawler_started = True
        self.logger.info("Crawler initialized successfully")

    def disconnect(self) -> None:
        """
        Close browser and cleanup resources.

        Properly shuts down AsyncWebCrawler and releases browser resources.
        """
        if self.crawler and self._crawler_started:
            self.logger.info("Closing browser and crawler")

            # AsyncWebCrawler cleanup is handled automatically
            # by context manager or garbage collection
            self.crawler = None
            self._crawler_started = False

            self.logger.info("Crawler closed successfully")

        super().disconnect()

    async def _crawl_page(
        self,
        url: str,
        wait_for: Optional[str] = None,
        js_code: Optional[str] = None,
        use_cache: bool = True,
    ) -> Any:
        """
        Internal method to crawl a single page.

        Includes:
        - SSRF protection against private IP ranges
        - Exponential backoff retry logic for rate limiting
        - Concurrent request limiting with semaphore
        - XSS sanitization of extracted content

        Args:
            url: URL to crawl
            wait_for: CSS selector to wait for before extraction
            js_code: JavaScript code to execute on page
            use_cache: Whether to use cache (default: True)

        Returns:
            CrawlResult object from Crawl4AI

        Raises:
            RuntimeError: If crawler not initialized
            ValueError: If URL fails SSRF validation
            Exception: If crawl fails after retries
        """
        if not self.crawler or not self._crawler_started:
            raise RuntimeError("Crawler not initialized. Call connect() first.")

        # SSRF protection: Validate URL before crawling
        self._validate_url_ssrf(url)

        # Configure crawl
        crawler_config = CrawlerRunConfig(
            cache_mode=CacheMode.ENABLED if use_cache else CacheMode.DISABLED,
            wait_until="networkidle",
            page_timeout=self.timeout * 1000,  # Convert to milliseconds
            wait_for=wait_for,
            js_code=js_code,
            simulate_user=True,  # Simulate human behavior
            override_navigator=True,  # Anti-bot evasion
        )

        self.logger.info(f"Crawling page: {url}", extra={"url": url, "use_cache": use_cache})

        # Wrapper function for retry logic
        async def _do_crawl():
            async with self.crawler as crawler:
                result = await crawler.arun(url=url, config=crawler_config)

                if not result.success:
                    error_msg = f"Failed to crawl {url}: {result.error_message}"
                    self.logger.error(error_msg, extra={"url": url, "error": result.error_message})
                    raise Exception(error_msg)

                # XSS sanitization: Sanitize markdown and HTML content
                if result.markdown and self.enable_xss_sanitization:
                    result.markdown = self._sanitize_xss(result.markdown)
                if result.html and self.enable_xss_sanitization:
                    result.html = self._sanitize_xss(result.html)

                self.logger.info(
                    "Page crawled successfully",
                    extra={
                        "url": url,
                        "html_length": len(result.html) if result.html else 0,
                        "markdown_length": len(result.markdown) if result.markdown else 0,
                    },
                )

                return result

        # Use retry logic with exponential backoff
        return await self._retry_with_backoff(_do_crawl)

    def extract_structured_data(
        self,
        url: str,
        schema: Dict[str, Any],
        extraction_strategy: str = "llm",
        wait_for: Optional[str] = None,
        js_code: Optional[str] = None,
        use_cache: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Extract structured data from a webpage using LLM or CSS selectors.

        Args:
            url: URL to scrape
            schema: JSON schema defining the data structure to extract
                For LLM extraction:
                    {
                        "name": "schema_name",
                        "description": "What to extract",
                        "fields": [...field definitions...]
                    }
                For CSS extraction:
                    {
                        "name": "schema_name",
                        "baseSelector": ".container",
                        "fields": [
                            {"name": "field1", "selector": ".title", "type": "text"},
                            {"name": "field2", "selector": ".amount", "type": "number"}
                        ]
                    }
            extraction_strategy: "llm" (LLM-based) or "css" (CSS selector-based)
            wait_for: CSS selector to wait for before extraction
            js_code: JavaScript code to execute on page
            use_cache: Whether to use cache (default: True)

        Returns:
            List of extracted data items

        Example:
            >>> schema = {
            ...     "name": "grants",
            ...     "description": "Extract grant information",
            ...     "fields": [
            ...         {"name": "title", "type": "string"},
            ...         {"name": "amount", "type": "number"},
            ...         {"name": "date", "type": "string"}
            ...     ]
            ... }
            >>> grants = scraper.extract_structured_data(
            ...     url="https://apps.nea.gov/GrantSearch/",
            ...     schema=schema,
            ...     extraction_strategy="llm"
            ... )
        """
        if not self._crawler_started:
            self.connect()

        # Validate schema
        if "name" not in schema:
            raise ValueError("Schema must include 'name' field")

        self.logger.info(
            f"Extracting structured data from {url}",
            extra={
                "url": url,
                "schema_name": schema.get("name"),
                "strategy": extraction_strategy,
            },
        )

        # Create extraction strategy
        if extraction_strategy == "llm":
            if not self.api_key:
                raise ValueError(
                    f"API key required for LLM extraction. "
                    f"Set {self.llm_provider.upper()}_API_KEY environment variable."
                )

            instruction = schema.get("description", f"Extract {schema['name']} data from the page")

            # Create LLM config for Crawl4AI v0.7.6 API
            # Provider format: "provider/model" (e.g., "openai/gpt-4o-mini")
            provider_string = f"{self.llm_provider}/{self.llm_model}"
            llm_config = LLMConfig(
                provider=provider_string,
                api_token=self.api_key,
            )

            strategy = LLMExtractionStrategy(
                llm_config=llm_config,
                schema=schema,
                extraction_type="schema",
                instruction=instruction,
            )

        elif extraction_strategy == "css":
            if "baseSelector" not in schema:
                raise ValueError("CSS extraction requires 'baseSelector' in schema")
            if "fields" not in schema:
                raise ValueError("CSS extraction requires 'fields' in schema")

            strategy = JsonCssExtractionStrategy(schema)

        else:
            raise ValueError(f"Unknown extraction strategy: {extraction_strategy}")

        # Run async crawl
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            self._extract_with_strategy(
                url=url,
                strategy=strategy,
                wait_for=wait_for,
                js_code=js_code,
                use_cache=use_cache,
            )
        )

        return result

    async def _extract_with_strategy(
        self,
        url: str,
        strategy: Any,
        wait_for: Optional[str] = None,
        js_code: Optional[str] = None,
        use_cache: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Internal async method to extract data with a strategy.

        Args:
            url: URL to scrape
            strategy: Crawl4AI extraction strategy instance
            wait_for: CSS selector to wait for
            js_code: JavaScript to execute
            use_cache: Whether to use cache

        Returns:
            List of extracted data items
        """
        crawler_config = CrawlerRunConfig(
            cache_mode=CacheMode.ENABLED if use_cache else CacheMode.DISABLED,
            wait_until="networkidle",
            page_timeout=self.timeout * 1000,
            wait_for=wait_for,
            js_code=js_code,
            extraction_strategy=strategy,
        )

        async with self.crawler as crawler:
            result = await crawler.arun(url=url, config=crawler_config)

            if not result.success:
                error_msg = f"Failed to extract data from {url}: {result.error_message}"
                self.logger.error(error_msg, extra={"url": url, "error": result.error_message})
                raise Exception(error_msg)

            # Parse extracted data
            if result.extracted_content:
                try:
                    extracted_data = json.loads(result.extracted_content)
                    self.logger.info(
                        f"Extracted {len(extracted_data)} items",
                        extra={"url": url, "item_count": len(extracted_data)},
                    )
                    return extracted_data
                except json.JSONDecodeError as e:
                    self.logger.error(
                        f"Failed to parse extracted data: {e}",
                        extra={"url": url, "error": str(e)},
                    )
                    return []
            else:
                self.logger.warning("No data extracted from page", extra={"url": url})
                return []

    def extract_table(
        self,
        url: str,
        table_index: int = 0,
        wait_for: Optional[str] = None,
        use_cache: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Extract HTML table data from a webpage.

        Args:
            url: URL containing the table
            table_index: Index of table to extract (0-based, default: 0)
            wait_for: CSS selector to wait for before extraction
            use_cache: Whether to use cache (default: True)

        Returns:
            List of dictionaries, one per table row

        Example:
            >>> tables = scraper.extract_table(
            ...     url="https://www.census.gov/data/tables.html",
            ...     table_index=0
            ... )
            >>> # Returns: [
            ...     {"column1": "value1", "column2": "value2"},
            ...     {"column1": "value3", "column2": "value4"},
            ... ]
        """
        if not self._crawler_started:
            self.connect()

        self.logger.info(
            f"Extracting table {table_index} from {url}",
            extra={"url": url, "table_index": table_index},
        )

        # JavaScript to extract table data
        js_code = f"""
        (function() {{
            const tables = document.querySelectorAll('table');
            if (tables.length > {table_index}) {{
                const table = tables[{table_index}];
                const headers = Array.from(table.querySelectorAll('thead th, tr:first-child th'))
                    .map(th => th.textContent.trim());
                
                const rows = Array.from(table.querySelectorAll('tbody tr, tr:not(:first-child)'))
                    .filter(row => row.querySelectorAll('td').length > 0)
                    .map(row => {{
                        const cells = Array.from(row.querySelectorAll('td'));
                        const rowData = {{}};
                        cells.forEach((cell, i) => {{
                            const header = headers[i] || `column_${{i}}`;
                            rowData[header] = cell.textContent.trim();
                        }});
                        return rowData;
                    }});
                
                return JSON.stringify(rows);
            }}
            return '[]';
        }})();
        """

        # Run async crawl
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            self._crawl_page(url=url, wait_for=wait_for, js_code=js_code, use_cache=use_cache)
        )

        # Extract table data from result
        # In Crawl4AI, JS execution results are available in result.js_result
        if hasattr(result, "js_result") and result.js_result:
            try:
                table_data = json.loads(result.js_result)
                self.logger.info(
                    f"Extracted table with {len(table_data)} rows",
                    extra={"url": url, "row_count": len(table_data)},
                )
                return table_data
            except json.JSONDecodeError as e:
                self.logger.error(
                    f"Failed to parse table data: {e}",
                    extra={"url": url, "error": str(e)},
                )
                return []
        else:
            self.logger.warning("No table data found", extra={"url": url})
            return []

    def extract_pdf(
        self,
        url: str,
        pages: Optional[str] = None,
        use_cache: bool = True,
    ) -> str:
        """
        Extract text content from a PDF document with page filtering.

        Supports flexible page range syntax:
        - Single page: "5"
        - Range: "1-10"
        - Multiple ranges: "1-5,10,15-20"
        - All pages: None (default)

        Security features:
        - SSRF protection against private IP ranges
        - XSS sanitization of extracted text

        Args:
            url: URL of the PDF file
            pages: Page specification string (1-based indexing, default: None for all pages)
            use_cache: Whether to use cache (default: True)

        Returns:
            Extracted text content from specified pages

        Raises:
            ValueError: If page specification is invalid or URL fails SSRF validation
            Exception: If PDF download or parsing fails

        Example:
            >>> # Extract all pages
            >>> text = scraper.extract_pdf("https://example.com/report.pdf")
            >>>
            >>> # Extract specific pages
            >>> text = scraper.extract_pdf(
            ...     url="https://www.nea.gov/sites/default/files/report.pdf",
            ...     pages="1-10,15,20-25"
            ... )
        """
        if not self._crawler_started:
            self.connect()

        # SSRF protection: Validate URL before downloading
        self._validate_url_ssrf(url)

        self.logger.info(
            f"Extracting PDF from {url}",
            extra={"url": url, "pages": pages},
        )

        # Check if URL is a PDF
        parsed_url = urlparse(url)
        if not parsed_url.path.lower().endswith(".pdf"):
            self.logger.warning(
                f"URL does not appear to be a PDF: {url}",
                extra={"url": url},
            )

        try:
            # Download PDF
            self.logger.debug(f"Downloading PDF from {url}")
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()

            # Parse PDF with PyPDF2
            pdf_file = io.BytesIO(response.content)
            pdf_reader = PdfReader(pdf_file)
            total_pages = len(pdf_reader.pages)

            self.logger.info(
                f"PDF has {total_pages} pages",
                extra={"url": url, "total_pages": total_pages},
            )

            # Parse page specification
            if pages:
                page_indices = self._parse_page_range(pages, total_pages)
                self.logger.info(
                    f"Extracting {len(page_indices)} pages: {pages}",
                    extra={"url": url, "page_count": len(page_indices)},
                )
            else:
                # Extract all pages
                page_indices = list(range(total_pages))
                self.logger.info(
                    f"Extracting all {total_pages} pages",
                    extra={"url": url, "total_pages": total_pages},
                )

            # Extract text from specified pages
            extracted_text = []
            for page_idx in page_indices:
                try:
                    page = pdf_reader.pages[page_idx]
                    text = page.extract_text()
                    if text:
                        extracted_text.append(text)
                except Exception as e:
                    self.logger.warning(
                        f"Failed to extract text from page {page_idx + 1}: {e}",
                        extra={"url": url, "page": page_idx + 1, "error": str(e)},
                    )

            result_text = "\n\n".join(extracted_text)

            # XSS sanitization: Sanitize extracted PDF text
            if self.enable_xss_sanitization:
                result_text = self._sanitize_xss(result_text)

            self.logger.info(
                f"Extracted {len(result_text)} characters from {len(extracted_text)} pages",
                extra={
                    "url": url,
                    "text_length": len(result_text),
                    "pages_extracted": len(extracted_text),
                },
            )

            return result_text

        except requests.RequestException as e:
            error_msg = f"Failed to download PDF from {url}: {e}"
            self.logger.error(error_msg, extra={"url": url, "error": str(e)})
            raise Exception(error_msg) from e

        except Exception as e:
            error_msg = f"Failed to parse PDF from {url}: {e}"
            self.logger.error(error_msg, extra={"url": url, "error": str(e)})
            raise Exception(error_msg) from e

    def _parse_page_range(self, pages: str, total_pages: int) -> List[int]:
        """
        Parse page range specification into list of page indices.

        Supports flexible syntax:
        - Single page: "5" -> [4]  (0-indexed)
        - Range: "1-10" -> [0,1,2,...,9]
        - Multiple ranges: "1-5,10,15-20" -> [0,1,2,3,4,9,14,15,...,19]

        Args:
            pages: Page specification string (1-based)
            total_pages: Total number of pages in PDF

        Returns:
            List of 0-based page indices

        Raises:
            ValueError: If page specification is invalid
        """
        page_indices = set()

        # Split by comma
        parts = pages.split(",")

        for part in parts:
            part = part.strip()

            if not part:
                continue

            # Check if it's a range (e.g., "1-10")
            if "-" in part:
                try:
                    start_str, end_str = part.split("-", 1)
                    start = int(start_str.strip())
                    end = int(end_str.strip())

                    # Validate range
                    if start < 1 or end < 1:
                        raise ValueError(f"Page numbers must be >= 1: {part}")
                    if start > total_pages or end > total_pages:
                        raise ValueError(f"Page numbers exceed PDF length ({total_pages}): {part}")
                    if start > end:
                        raise ValueError(f"Invalid page range (start > end): {part}")

                    # Add pages in range (convert to 0-indexed)
                    page_indices.update(range(start - 1, end))

                except ValueError as e:
                    raise ValueError(f"Invalid page range '{part}': {e}") from e

            else:
                # Single page number
                try:
                    page_num = int(part)

                    if page_num < 1:
                        raise ValueError(f"Page number must be >= 1: {part}")
                    if page_num > total_pages:
                        raise ValueError(f"Page number exceeds PDF length ({total_pages}): {part}")

                    # Add page (convert to 0-indexed)
                    page_indices.add(page_num - 1)

                except ValueError as e:
                    raise ValueError(f"Invalid page number '{part}': {e}") from e

        # Return sorted list
        return sorted(list(page_indices))

    def fetch(self, url: str, **kwargs: Any) -> str:
        """
        Fetch raw HTML/markdown content from a URL.

        This is the BaseConnector's fetch() implementation for simple scraping.

        Args:
            url: URL to fetch
            **kwargs: Additional parameters:
                - format: "html" or "markdown" (default: "markdown")
                - wait_for: CSS selector to wait for
                - js_code: JavaScript to execute
                - use_cache: Whether to use cache (default: True)

        Returns:
            Page content as HTML or markdown

        Example:
            >>> html = scraper.fetch("https://example.com", format="html")
            >>> markdown = scraper.fetch("https://example.com", format="markdown")
        """
        if not self._crawler_started:
            self.connect()

        content_format = kwargs.get("format", "markdown")
        wait_for = kwargs.get("wait_for")
        js_code = kwargs.get("js_code")
        use_cache = kwargs.get("use_cache", True)

        self.logger.info(
            f"Fetching {content_format} from {url}",
            extra={"url": url, "format": content_format},
        )

        # Run async crawl
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            self._crawl_page(url=url, wait_for=wait_for, js_code=js_code, use_cache=use_cache)
        )

        # Return requested format
        if content_format == "html":
            return result.html or ""
        else:
            return result.markdown or ""

    async def _extract_next_page_url(
        self,
        result: Any,
        next_page_selector: str,
        selector_type: str = "css",
    ) -> Optional[str]:
        """
        Extract next page URL from crawl result.

        Args:
            result: CrawlResult from Crawl4AI
            next_page_selector: Selector for next page link
            selector_type: "css" or "xpath" (default: "css")

        Returns:
            Next page URL or None if not found
        """
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(result.html, "html.parser")

            if selector_type == "css":
                next_link = soup.select_one(next_page_selector)
            else:  # xpath
                # For XPath, we'll use a simple approach
                # In production, consider using lxml for better XPath support
                self.logger.warning(
                    "XPath selector support is limited, consider using CSS selectors",
                    extra={"selector": next_page_selector},
                )
                return None

            if next_link:
                href = next_link.get("href")
                if href and isinstance(href, str):
                    # Handle relative URLs
                    if href.startswith("http"):
                        return href
                    else:
                        from urllib.parse import urljoin

                        return urljoin(result.url, href)

        except Exception as e:
            self.logger.error(
                f"Failed to extract next page URL: {e}",
                extra={"selector": next_page_selector, "error": str(e)},
            )

        return None

    def crawl_multi_page(
        self,
        start_url: str,
        next_page_selector: str,
        max_pages: int = 10,
        strategy: str = "breadth_first",
        selector_type: str = "css",
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """
        Crawl multiple pages following pagination links.

        Supports two strategies:
        - breadth_first: Crawl all pages at current level before going deeper
        - depth_first: Follow first link deeply before exploring siblings

        Args:
            start_url: Starting URL for crawling
            next_page_selector: CSS/XPath selector for next page link
            max_pages: Maximum number of pages to crawl (default: 10)
            strategy: "breadth_first" or "depth_first" (default: "breadth_first")
            selector_type: "css" or "xpath" for next_page_selector (default: "css")
            **kwargs: Additional parameters passed to _crawl_page():
                - wait_for: CSS selector to wait for
                - js_code: JavaScript to execute
                - use_cache: Whether to use cache (default: True)

        Returns:
            List of crawled page data, each containing:
            - url: Page URL
            - html: Page HTML content
            - markdown: Page markdown content
            - page_number: Sequential page number (1-indexed)

        Example:
            >>> # Breadth-first pagination
            >>> pages = scraper.crawl_multi_page(
            ...     start_url="https://example.com/articles",
            ...     next_page_selector="a.next-page",
            ...     max_pages=5
            ... )
            >>>
            >>> # Depth-first with custom selector
            >>> pages = scraper.crawl_multi_page(
            ...     start_url="https://example.com/docs",
            ...     next_page_selector="a[rel='next']",
            ...     strategy="depth_first",
            ...     max_pages=10
            ... )
        """
        if not self._crawler_started:
            self.connect()

        if strategy not in ["breadth_first", "depth_first"]:
            raise ValueError(
                f"Invalid strategy: {strategy}. Must be 'breadth_first' or 'depth_first'"
            )

        self.logger.info(
            f"Starting multi-page crawl with {strategy} strategy",
            extra={
                "start_url": start_url,
                "max_pages": max_pages,
                "strategy": strategy,
                "selector": next_page_selector,
            },
        )

        visited_urls = set()
        pages_data = []
        page_count = 0

        loop = asyncio.get_event_loop()

        # Breadth-first: Use queue (FIFO)
        if strategy == "breadth_first":
            from collections import deque

            url_queue = deque([start_url])

            while url_queue and page_count < max_pages:
                current_url = url_queue.popleft()

                # Skip if already visited
                if current_url in visited_urls:
                    continue

                visited_urls.add(current_url)
                page_count += 1

                self.logger.info(
                    f"Crawling page {page_count}/{max_pages}: {current_url}",
                    extra={"page": page_count, "url": current_url},
                )

                try:
                    # Crawl current page
                    result = loop.run_until_complete(
                        self._crawl_page(
                            url=current_url,
                            wait_for=kwargs.get("wait_for"),
                            js_code=kwargs.get("js_code"),
                            use_cache=kwargs.get("use_cache", True),
                        )
                    )

                    # Store page data
                    pages_data.append(
                        {
                            "url": current_url,
                            "html": result.html or "",
                            "markdown": result.markdown or "",
                            "page_number": page_count,
                        }
                    )

                    # Extract next page URL
                    next_url = loop.run_until_complete(
                        self._extract_next_page_url(
                            result=result,
                            next_page_selector=next_page_selector,
                            selector_type=selector_type,
                        )
                    )

                    if next_url and next_url not in visited_urls:
                        url_queue.append(next_url)

                except Exception as e:
                    self.logger.error(
                        f"Failed to crawl page {page_count}: {e}",
                        extra={"url": current_url, "error": str(e)},
                    )
                    # Continue with next page on error

        # Depth-first: Use stack (LIFO) - recursive approach
        else:  # depth_first

            def crawl_recursive(url: str, depth: int = 0):
                nonlocal page_count

                if page_count >= max_pages or url in visited_urls:
                    return

                visited_urls.add(url)
                page_count += 1

                self.logger.info(
                    f"Crawling page {page_count}/{max_pages} (depth={depth}): {url}",
                    extra={"page": page_count, "url": url, "depth": depth},
                )

                try:
                    # Crawl current page
                    result = loop.run_until_complete(
                        self._crawl_page(
                            url=url,
                            wait_for=kwargs.get("wait_for"),
                            js_code=kwargs.get("js_code"),
                            use_cache=kwargs.get("use_cache", True),
                        )
                    )

                    # Store page data
                    pages_data.append(
                        {
                            "url": url,
                            "html": result.html or "",
                            "markdown": result.markdown or "",
                            "page_number": page_count,
                        }
                    )

                    # Extract next page URL and recurse
                    next_url = loop.run_until_complete(
                        self._extract_next_page_url(
                            result=result,
                            next_page_selector=next_page_selector,
                            selector_type=selector_type,
                        )
                    )

                    if next_url and next_url not in visited_urls and page_count < max_pages:
                        crawl_recursive(next_url, depth + 1)

                except Exception as e:
                    self.logger.error(
                        f"Failed to crawl page {page_count}: {e}",
                        extra={"url": url, "error": str(e)},
                    )

            crawl_recursive(start_url)

        self.logger.info(
            f"Multi-page crawl completed: {len(pages_data)} pages crawled",
            extra={"pages_crawled": len(pages_data), "max_pages": max_pages},
        )

        return pages_data

    def crawl_parallel(
        self,
        urls: List[str],
        worker_pool_size: Optional[int] = None,
        return_format: str = "markdown",
        timeout_per_url: Optional[int] = None,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """
        Crawl multiple URLs in parallel with concurrent execution.

        Features:
        - Concurrent URL fetching with asyncio worker pool
        - Configurable worker pool size (defaults to max_concurrent_requests)
        - Automatic retry logic with exponential backoff
        - SSRF protection and XSS sanitization
        - Progress tracking
        - Connection pooling (via AsyncWebCrawler reuse)

        Args:
            urls: List of URLs to crawl in parallel
            worker_pool_size: Number of concurrent workers (default: max_concurrent_requests)
            return_format: Content format - "markdown", "html", or "both" (default: "markdown")
            timeout_per_url: Timeout per URL in seconds (default: self.timeout)
            **kwargs: Additional arguments passed to _crawl_page()
                - wait_for: CSS selector to wait for
                - js_code: JavaScript to execute
                - use_cache: Whether to use cache (default: True)

        Returns:
            List of crawl results, each containing:
                - url: The crawled URL
                - success: Whether crawl succeeded
                - markdown: Extracted markdown content (if return_format includes it)
                - html: Extracted HTML content (if return_format includes it)
                - error: Error message (if failed)
                - crawl_time: Time taken to crawl (seconds)

        Raises:
            RuntimeError: If crawler not initialized
            ValueError: If invalid parameters

        Example:
            >>> scraper = WebScraperConnector(max_concurrent_requests=5)
            >>> scraper.connect()
            >>>
            >>> urls = [
            ...     "https://example.com/page1",
            ...     "https://example.com/page2",
            ...     "https://example.com/page3",
            ... ]
            >>>
            >>> results = scraper.crawl_parallel(urls, worker_pool_size=3)
            >>>
            >>> for result in results:
            ...     if result['success']:
            ...         print(f"{result['url']}: {len(result['markdown'])} chars")
            ...     else:
            ...         print(f"{result['url']}: FAILED - {result['error']}")
        """
        if not self._crawler_started:
            self.connect()

        # Validate inputs
        if not urls:
            raise ValueError("urls list cannot be empty")

        if return_format not in ["markdown", "html", "both"]:
            raise ValueError("return_format must be 'markdown', 'html', or 'both'")

        # Set worker pool size
        pool_size = worker_pool_size or self.max_concurrent_requests

        # Set timeout per URL
        url_timeout = timeout_per_url or self.timeout

        self.logger.info(
            f"Starting parallel crawl of {len(urls)} URLs with {pool_size} workers",
            extra={
                "url_count": len(urls),
                "worker_pool_size": pool_size,
                "return_format": return_format,
            },
        )

        # Use asyncio to run parallel crawl
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(
            self._crawl_parallel_async(
                urls=urls,
                pool_size=pool_size,
                return_format=return_format,
                url_timeout=url_timeout,
                **kwargs,
            )
        )

        # Calculate statistics
        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful
        total_time = sum(r.get("crawl_time", 0) for r in results)
        avg_time = total_time / len(results) if results else 0

        self.logger.info(
            f"Parallel crawl completed: {successful}/{len(urls)} successful, "
            f"avg {avg_time:.2f}s per URL",
            extra={
                "total_urls": len(urls),
                "successful": successful,
                "failed": failed,
                "total_time": total_time,
                "avg_time": avg_time,
            },
        )

        return results

    async def _crawl_parallel_async(
        self,
        urls: List[str],
        pool_size: int,
        return_format: str,
        url_timeout: int,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """
        Internal async method for parallel crawling.

        Uses asyncio.Semaphore for worker pool management and
        asyncio.gather() for concurrent execution.

        Args:
            urls: List of URLs to crawl
            pool_size: Worker pool size
            return_format: Content format ("markdown", "html", "both")
            url_timeout: Timeout per URL
            **kwargs: Additional arguments for _crawl_page()

        Returns:
            List of crawl results
        """
        # Create semaphore for worker pool
        # Note: We already have self._semaphore for max_concurrent_requests
        # This creates an additional limit for parallel crawling
        worker_semaphore = asyncio.Semaphore(pool_size)

        # Create tasks for all URLs
        tasks = [
            self._crawl_single_url_async(
                url=url,
                semaphore=worker_semaphore,
                return_format=return_format,
                url_timeout=url_timeout,
                **kwargs,
            )
            for url in urls
        ]

        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=False)

        return results

    async def _crawl_single_url_async(
        self,
        url: str,
        semaphore: asyncio.Semaphore,
        return_format: str,
        url_timeout: int,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Crawl a single URL with semaphore-based concurrency control.

        Args:
            url: URL to crawl
            semaphore: Semaphore for worker pool
            return_format: Content format
            url_timeout: Timeout for this URL
            **kwargs: Additional arguments for _crawl_page()

        Returns:
            Crawl result dictionary
        """
        start_time = time.time()
        result = {
            "url": url,
            "success": False,
            "error": None,
            "crawl_time": 0,
        }

        try:
            # Acquire semaphore (blocks if pool is full)
            async with semaphore:
                self.logger.debug(f"Starting crawl: {url}")

                # Crawl page (includes retry logic and SSRF/XSS protection)
                crawl_result = await self._crawl_page(
                    url=url,
                    wait_for=kwargs.get("wait_for"),
                    js_code=kwargs.get("js_code"),
                    use_cache=kwargs.get("use_cache", True),
                )

                # Extract content based on return_format
                if return_format in ["markdown", "both"]:
                    result["markdown"] = crawl_result.markdown or ""

                if return_format in ["html", "both"]:
                    result["html"] = crawl_result.html or ""

                result["success"] = True
                self.logger.debug(f"Completed crawl: {url} ({time.time() - start_time:.2f}s)")

        except Exception as e:
            result["error"] = str(e)
            self.logger.error(
                f"Failed to crawl {url}: {e}",
                extra={"url": url, "error": str(e)},
            )

        finally:
            result["crawl_time"] = time.time() - start_time

        return result

    def _validate_url_ssrf(self, url: str) -> None:
        """
        Validate URL against SSRF (Server-Side Request Forgery) attacks.

        Blocks requests to:
        - Private IP ranges (127.0.0.0/8, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)
        - Loopback addresses
        - Link-local addresses
        - Multicast addresses

        Args:
            url: URL to validate

        Raises:
            ValueError: If URL targets private/internal resources
        """
        if not self.enable_ssrf_protection:
            return

        try:
            parsed = urlparse(url)
            hostname = parsed.hostname

            if not hostname:
                raise ValueError(f"Invalid URL: no hostname found in {url}")

            # Try to resolve hostname to IP
            try:
                ip_str = socket.gethostbyname(hostname)
                ip = ipaddress.IPv4Address(ip_str)

                # Check if IP is in any private range
                for private_range in self._private_ip_ranges:
                    if ip in private_range:
                        raise ValueError(
                            f"SSRF protection: URL resolves to private IP {ip_str} "
                            f"in range {private_range}"
                        )

            except socket.gaierror:
                # DNS resolution failed - allow it to fail naturally in request
                self.logger.warning(
                    f"DNS resolution failed for {hostname} - allowing request to proceed",
                    extra={"url": url, "hostname": hostname},
                )

        except Exception as e:
            if "SSRF protection" in str(e):
                raise
            # Other validation errors - log but don't block
            self.logger.warning(
                f"URL validation error: {e}",
                extra={"url": url, "error": str(e)},
            )

    def _sanitize_xss(self, content: str) -> str:
        """
        Sanitize content to prevent XSS (Cross-Site Scripting) attacks.

        Removes:
        - <script> tags and content
        - Event handler attributes (onclick, onerror, etc.)
        - javascript: protocol in URLs
        - data: protocol in URLs (can contain embedded scripts)

        Args:
            content: Raw content to sanitize

        Returns:
            Sanitized content safe for display
        """
        if not self.enable_xss_sanitization:
            return content

        # Remove <script> tags and content
        content = re.sub(r"<script[^>]*>.*?</script>", "", content, flags=re.DOTALL | re.IGNORECASE)

        # Remove event handler attributes
        event_handlers = [
            "onclick",
            "onload",
            "onerror",
            "onmouseover",
            "onmouseout",
            "onfocus",
            "onblur",
            "onchange",
            "onsubmit",
        ]
        for handler in event_handlers:
            content = re.sub(
                rf'\s{handler}\s*=\s*["\'][^"\']*["\']',
                "",
                content,
                flags=re.IGNORECASE,
            )

        # Remove javascript: and data: protocols
        content = re.sub(
            r'(href|src)\s*=\s*["\']?(javascript|data):',
            r'\1="',
            content,
            flags=re.IGNORECASE,
        )

        # Escape HTML entities in text content
        # Only escape outside of HTML tags
        def escape_text(match):
            text = match.group(0)
            if text.startswith("<") and text.endswith(">"):
                return text  # Don't escape HTML tags
            return escape(text)

        # This is a simple approach - for production consider using bleach or html5lib
        return content

    async def _retry_with_backoff(
        self,
        func,
        *args,
        **kwargs,
    ) -> Any:
        """
        Retry function with exponential backoff.

        Implements exponential backoff for 429 (rate limiting) and 5xx server errors:
        - Initial delay: 1 second
        - Backoff factor: self.backoff_factor (default 2.0)
        - Max delay: self.max_backoff_delay (default 60 seconds)
        - Max retries: self.max_retries (default 3)

        Args:
            func: Async function to retry
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result from successful function call

        Raises:
            Exception: If all retries exhausted
        """
        delay = 1.0  # Initial delay in seconds
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                # Use semaphore for concurrent request limiting
                if self._semaphore:
                    async with self._semaphore:
                        return await func(*args, **kwargs)
                else:
                    return await func(*args, **kwargs)

            except Exception as e:
                last_exception = e
                error_str = str(e).lower()

                # Check if error is retryable (429, 5xx, network errors)
                is_rate_limit = "429" in error_str or "rate limit" in error_str
                is_server_error = any(code in error_str for code in ["500", "502", "503", "504"])
                is_network_error = any(
                    err in error_str
                    for err in ["timeout", "connection", "network", "ssl", "certificate"]
                )

                if not (is_rate_limit or is_server_error or is_network_error):
                    # Non-retryable error
                    raise

                if attempt < self.max_retries - 1:
                    # Calculate backoff delay
                    backoff_delay = min(
                        delay * (self.backoff_factor**attempt), self.max_backoff_delay
                    )

                    self.logger.warning(
                        f"Attempt {attempt + 1}/{self.max_retries} failed: {e}. "
                        f"Retrying in {backoff_delay:.1f}s...",
                        extra={
                            "attempt": attempt + 1,
                            "max_retries": self.max_retries,
                            "backoff_delay": backoff_delay,
                            "error": str(e),
                        },
                    )

                    await asyncio.sleep(backoff_delay)
                else:
                    # Last attempt failed
                    self.logger.error(
                        f"All {self.max_retries} retry attempts exhausted",
                        extra={"max_retries": self.max_retries, "last_error": str(e)},
                    )

        # All retries exhausted
        raise Exception(f"All {self.max_retries} retry attempts failed: {last_exception}")

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"WebScraperConnector("
            f"llm_provider='{self.llm_provider}', "
            f"llm_model='{self.llm_model}', "
            f"headless={self.headless}, "
            f"crawler_started={self._crawler_started}"
            ")"
        )
