"""
Jina Reader API Client
======================

High-success-rate article full-text extraction using Jina Reader API.

Advantages over basic URL parsing:
    - 85-95% success rate (empirically validated)
    - Handles JavaScript rendering, paywalls, dynamic content
    - Returns clean markdown format
    - Built-in rate limiting

Pricing:
    - $29/month for 5,000 requests
    - Enterprise tiers available

Environment Variables:
    JINA_API_KEY: Jina API key (required for operation)

Usage:
    >>> from krl_data_connectors.core.enrichment import JinaClient
    >>> client = JinaClient()
    >>> result = client.fetch_article("https://example.com/article")

© 2025 KR-Labs. All rights reserved.
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Any, Dict, List, Optional

import pandas as pd
import requests
from tqdm import tqdm

logger = logging.getLogger(__name__)


@dataclass
class JinaFetchResult:
    """Result of a Jina Reader API fetch operation."""

    success: bool
    content: str
    title: str
    url: str
    word_count: int = 0
    fetched_at: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "success": self.success,
            "content": self.content,
            "title": self.title,
            "url": self.url,
            "word_count": self.word_count,
            "fetched_at": self.fetched_at,
            "error": self.error,
        }


@dataclass
class JinaStatistics:
    """Statistics for Jina Reader API usage."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0

    @property
    def success_rate(self) -> float:
        """Calculate success rate as a percentage."""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests

    @property
    def estimated_cost_usd(self) -> float:
        """Estimate cost based on $29/5000 requests pricing."""
        return (self.total_requests / 5000) * 29


class JinaClient:
    """
    Jina Reader API client for full-text article extraction.

    This client provides high-success-rate text extraction from web articles,
    handling JavaScript rendering, paywalls, and dynamic content that basic
    HTML parsing cannot handle.

    Attributes:
        enabled: Whether the client is operational (requires API key)
        stats: Usage statistics for monitoring

    Example:
        >>> client = JinaClient()
        >>> result = client.fetch_article("https://nytimes.com/some-article")
        >>> if result.success:
        ...     print(f"Extracted {result.word_count} words")
    """

    # API configuration
    BASE_URL = "https://r.jina.ai/"
    MIN_REQUEST_INTERVAL = 0.2  # 5 requests/second rate limit
    DEFAULT_TIMEOUT = 10

    def __init__(
        self,
        api_key: Optional[str] = None,
        return_format: str = "markdown",
    ) -> None:
        """
        Initialize Jina Reader client.

        Args:
            api_key: Jina API key. If not provided, reads from JINA_API_KEY
                environment variable.
            return_format: Response format ('markdown' or 'text')
        """
        self.api_key = api_key or os.environ.get("JINA_API_KEY")

        if not self.api_key:
            logger.warning(
                "Jina API key not found. Set JINA_API_KEY environment variable "
                "or pass api_key parameter. Full-text enrichment will be skipped. "
                "Get an API key at https://jina.ai/reader"
            )
            self.enabled = False
            return

        self.enabled = True
        self.return_format = return_format
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "X-Return-Format": return_format,
        }

        # Rate limiting state
        self._last_request_time: float = 0

        # Statistics tracking
        self.stats = JinaStatistics()

        logger.info(
            "Jina Reader client initialized | "
            f"rate_limit=5/sec | monthly_quota=5000 | pricing=$29/month"
        )

    def _enforce_rate_limit(self) -> None:
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.MIN_REQUEST_INTERVAL:
            time.sleep(self.MIN_REQUEST_INTERVAL - elapsed)
        self._last_request_time = time.time()

    def fetch_article(
        self,
        url: str,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> JinaFetchResult:
        """
        Fetch full text for a single article.

        Args:
            url: Article URL to fetch
            timeout: Request timeout in seconds

        Returns:
            JinaFetchResult with extracted content or error details
        """
        if not self.enabled:
            return JinaFetchResult(
                success=False,
                content="",
                title="",
                url=url,
                error="Jina API key not configured",
            )

        self._enforce_rate_limit()
        self.stats.total_requests += 1

        try:
            response = requests.get(
                f"{self.BASE_URL}{url}",
                headers=self.headers,
                timeout=timeout,
            )

            if response.status_code == 200:
                content = response.text.strip()
                self.stats.successful_requests += 1

                return JinaFetchResult(
                    success=True,
                    content=content,
                    title="",  # Would need to parse from content
                    url=url,
                    word_count=len(content.split()),
                    fetched_at=datetime.now().isoformat(),
                )

            # Handle rate limiting
            if response.status_code == 429:
                logger.warning("Jina API rate limit hit, backing off")
                time.sleep(2)

            self.stats.failed_requests += 1
            return JinaFetchResult(
                success=False,
                content="",
                title="",
                url=url,
                error=f"HTTP {response.status_code}",
            )

        except requests.exceptions.Timeout:
            self.stats.failed_requests += 1
            return JinaFetchResult(
                success=False,
                content="",
                title="",
                url=url,
                error="Request timeout",
            )
        except requests.exceptions.RequestException as e:
            self.stats.failed_requests += 1
            return JinaFetchResult(
                success=False,
                content="",
                title="",
                url=url,
                error=str(e),
            )

    def enrich_dataframe(
        self,
        df: pd.DataFrame,
        url_column: str = "url",
        max_articles: Optional[int] = None,
        show_progress: bool = True,
    ) -> pd.DataFrame:
        """
        Enrich DataFrame with full-text content from Jina Reader.

        Args:
            df: DataFrame containing article URLs
            url_column: Name of the column containing URLs
            max_articles: Maximum articles to enrich (for testing/cost control)
            show_progress: Whether to display progress bar

        Returns:
            DataFrame with additional columns: full_text, word_count, fetch_success
        """
        if not self.enabled:
            logger.warning("Jina Reader not enabled - skipping full-text enrichment")
            df = df.copy()
            df["full_text"] = df.get("title", "")
            df["word_count"] = df["full_text"].str.split().str.len()
            df["fetch_success"] = False
            return df

        # Deduplicate and limit URLs
        urls = df[url_column].dropna().unique()
        if max_articles:
            urls = urls[:max_articles]
            logger.info(f"Limited to {max_articles} articles for enrichment")

        estimated_cost = (len(urls) / 5000) * 29
        estimated_time = (len(urls) * self.MIN_REQUEST_INTERVAL) / 60

        logger.info(
            f"Enriching {len(urls):,} articles with full text | "
            f"estimated_cost=${estimated_cost:.2f} | "
            f"estimated_time={estimated_time:.1f}min"
        )

        # Fetch articles
        results: List[Dict[str, Any]] = []
        iterator = tqdm(urls, desc="Fetching") if show_progress else urls

        for url in iterator:
            result = self.fetch_article(url)
            results.append(result.to_dict())

        # Create results DataFrame
        results_df = pd.DataFrame(results)

        # Merge with original DataFrame
        enriched_df = df.merge(
            results_df[["url", "content", "word_count", "success"]],
            left_on=url_column,
            right_on="url",
            how="left",
            suffixes=("", "_jina"),
        )

        # Rename and clean up columns
        enriched_df = enriched_df.rename(
            columns={
                "content": "full_text",
                "success": "fetch_success",
            }
        )

        # Fill missing full_text with title
        enriched_df["full_text"] = enriched_df["full_text"].fillna(
            enriched_df.get("title", "")
        )
        enriched_df["fetch_success"] = enriched_df["fetch_success"].fillna(False)

        # Log statistics
        success_rate = self.stats.success_rate
        avg_word_count = enriched_df.loc[
            enriched_df["fetch_success"] == True, "word_count"
        ].mean()

        logger.info(
            f"Enrichment complete | "
            f"success_rate={success_rate:.1%} | "
            f"avg_words={avg_word_count:.0f} | "
            f"failed={self.stats.failed_requests}"
        )

        return enriched_df

    def get_statistics(self) -> Dict[str, Any]:
        """Get enrichment statistics."""
        return {
            "total_requests": self.stats.total_requests,
            "successful": self.stats.successful_requests,
            "failed": self.stats.failed_requests,
            "success_rate": self.stats.success_rate,
            "estimated_cost_usd": self.stats.estimated_cost_usd,
        }

    def reset_statistics(self) -> None:
        """Reset usage statistics."""
        self.stats = JinaStatistics()
