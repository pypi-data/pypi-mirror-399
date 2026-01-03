"""
Syndication Handler - National vs Regional Content Separation
============================================================

Key Innovation: Treats syndicated wire content as "national narrative baseline"
separate from regional clustering analysis.

Problem Solved:
    - Syndicated articles with λ=0.0 were creating mega-clusters
    - "Fact Check Team" stories scattered across 10+ clusters
    - 40-50% of articles are syndicated, polluting regional analysis

Solution:
    - Separate syndicated (λ=0.0) from local (λ>0.0) content
    - Analyze syndicated as national baseline
    - Cluster only local/regional content for geographic insights

Business Value:
    - Policy analysts: Predict regional opposition
    - PR teams: Tailor messaging by region
    - Campaigns: Identify swing regions

© 2025 KR-Labs. All rights reserved.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class NationalBaseline:
    """National narrative baseline from syndicated content analysis."""

    total_articles: int
    unique_stories: int
    duplication_rate: float
    geographic_spread: int
    avg_sentiment: Optional[float]
    top_stories: Dict[str, int] = field(default_factory=dict)
    top_sources: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "total_articles": self.total_articles,
            "unique_stories": self.unique_stories,
            "duplication_rate": self.duplication_rate,
            "geographic_spread": self.geographic_spread,
            "avg_sentiment": self.avg_sentiment,
            "top_stories": self.top_stories,
            "top_sources": self.top_sources,
        }


class SyndicationHandler:
    """
    Separate syndicated (national) from local (regional) content.

    This class provides methods to partition media content into national
    syndicated baseline and regional original reporting, enabling more
    meaningful geographic analysis of news coverage patterns.

    The separation is based on the adaptive λ weight calculated for each
    article, where λ=0.0 indicates syndicated content and λ>0.0 indicates
    local/regional content.

    Example:
        >>> handler = SyndicationHandler()
        >>> df_syndicated, df_local = handler.separate_content(df_enriched)
        >>> baseline = handler.analyze_national_baseline(df_syndicated)
        >>> print(f"Duplication rate: {baseline.duplication_rate:.1%}")
    """

    def separate_content(
        self,
        df_enriched: pd.DataFrame,
        lambda_column: str = "lambda_spatial",
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Split DataFrame into syndicated and local content.

        Args:
            df_enriched: DataFrame with adaptive λ weights
            lambda_column: Column containing λ values

        Returns:
            Tuple of (df_syndicated, df_local) DataFrames

        Raises:
            ValueError: If lambda_column is not present in DataFrame
        """
        if lambda_column not in df_enriched.columns:
            raise ValueError(
                f"DataFrame must have '{lambda_column}' column. "
                "Run adaptive weighting first."
            )

        # Separate by lambda value
        df_syndicated = df_enriched[df_enriched[lambda_column] == 0.0].copy()
        df_local = df_enriched[df_enriched[lambda_column] > 0.0].copy()

        total = len(df_enriched)
        syndicated_count = len(df_syndicated)
        local_count = len(df_local)

        logger.info(
            f"Content separation complete | "
            f"total={total} | "
            f"syndicated={syndicated_count} ({syndicated_count/total*100:.1f}%) | "
            f"local={local_count} ({local_count/total*100:.1f}%)"
        )

        return df_syndicated, df_local

    def analyze_national_baseline(
        self,
        df_syndicated: pd.DataFrame,
        title_column: str = "title",
        source_column: str = "source",
        location_column: str = "location",
        sentiment_column: str = "sentiment_deep_score",
    ) -> Optional[NationalBaseline]:
        """
        Analyze syndicated content as national narrative baseline.

        This analysis reveals:
            - Most common national stories
            - Geographic spread of syndicated content
            - Average sentiment of national coverage

        Args:
            df_syndicated: DataFrame of syndicated articles
            title_column: Column containing article titles
            source_column: Column containing source names
            location_column: Column containing location names
            sentiment_column: Column containing sentiment scores

        Returns:
            NationalBaseline object or None if no syndicated content
        """
        if len(df_syndicated) == 0:
            logger.warning("No syndicated content found for baseline analysis")
            return None

        # Most common syndicated stories (by exact title match)
        top_stories = (
            df_syndicated.groupby(title_column)
            .size()
            .sort_values(ascending=False)
            .head(10)
            .to_dict()
        )

        # Geographic spread
        geographic_spread = (
            df_syndicated[location_column].nunique()
            if location_column in df_syndicated.columns
            else 0
        )

        # Sentiment baseline (if available)
        avg_sentiment: Optional[float] = None
        if sentiment_column in df_syndicated.columns:
            avg_sentiment = float(df_syndicated[sentiment_column].mean())

        # Top sources
        top_sources: Dict[str, int] = {}
        if source_column in df_syndicated.columns:
            top_sources = (
                df_syndicated[source_column]
                .value_counts()
                .head(5)
                .to_dict()
            )

        # Duplication analysis
        unique_stories = df_syndicated[title_column].nunique()
        total_instances = len(df_syndicated)
        duplication_rate = (
            1 - (unique_stories / total_instances) if total_instances > 0 else 0
        )

        baseline = NationalBaseline(
            total_articles=total_instances,
            unique_stories=unique_stories,
            duplication_rate=duplication_rate,
            geographic_spread=geographic_spread,
            avg_sentiment=avg_sentiment,
            top_stories=top_stories,
            top_sources=top_sources,
        )

        logger.info(
            f"National baseline analysis | "
            f"articles={baseline.total_articles} | "
            f"unique={baseline.unique_stories} | "
            f"duplication={baseline.duplication_rate:.1%}"
        )

        return baseline

    def get_local_only_for_clustering(
        self,
        df_enriched: pd.DataFrame,
        lambda_column: str = "lambda_spatial",
    ) -> pd.DataFrame:
        """
        Convenience method: Get local content ready for clustering.

        Use this instead of the full df_enriched when running spatial clustering
        to exclude syndicated content that would create artificial mega-clusters.

        Args:
            df_enriched: Full enriched DataFrame
            lambda_column: Column containing λ values

        Returns:
            DataFrame with only local/regional content (λ > 0.0)
        """
        _, df_local = self.separate_content(df_enriched, lambda_column)

        logger.info(
            f"Ready for regional clustering | "
            f"articles={len(df_local)} | "
            f"syndicated_excluded=True"
        )

        return df_local

    @staticmethod
    def print_baseline_summary(baseline: NationalBaseline) -> None:
        """Print formatted summary of national baseline analysis."""
        print("\n" + "=" * 80)
        print("📰 NATIONAL NARRATIVE BASELINE (Syndicated Content)")
        print("=" * 80)

        print(f"\n🔢 Volume:")
        print(f"   Total articles: {baseline.total_articles}")
        print(f"   Unique stories: {baseline.unique_stories}")
        print(f"   Duplication rate: {baseline.duplication_rate:.1%}")

        print(f"\n🌍 Geographic Reach:")
        print(f"   Locations covered: {baseline.geographic_spread}")

        if baseline.avg_sentiment is not None:
            print(f"\n😊 Sentiment:")
            print(f"   Average: {baseline.avg_sentiment:.3f}")
            if baseline.avg_sentiment > 0.1:
                tone = "POSITIVE"
            elif baseline.avg_sentiment < -0.1:
                tone = "NEGATIVE"
            else:
                tone = "NEUTRAL"
            print(f"   Overall tone: {tone}")

        print(f"\n🔝 Top Syndicated Stories:")
        for i, (title, count) in enumerate(
            list(baseline.top_stories.items())[:5], 1
        ):
            pct = count / baseline.total_articles * 100
            print(f"   {i}. {title[:70]}...")
            print(f"      Instances: {count} ({pct:.1f}%)")

        if baseline.top_sources:
            print(f"\n📡 Top Sources:")
            for source, count in list(baseline.top_sources.items())[:5]:
                print(f"   • {source}: {count} articles")

        print("\n" + "=" * 80)

    @staticmethod
    def print_comparison_guide() -> None:
        """Print guide for interpreting national vs regional analysis."""
        print("\n" + "=" * 80)
        print("📖 NATIONAL vs REGIONAL ANALYSIS GUIDE")
        print("=" * 80)

        print("\n🌐 National Baseline (Syndicated):")
        print("   • Wire services (AP, Reuters, Bloomberg)")
        print("   • Network news (CNN, Fox, NBC)")
        print("   • Fact-check services")
        print("   • Corporate press releases")
        print("   → Represents what MOST Americans see")
        print("   → Geography is IRRELEVANT (same story everywhere)")

        print("\n🏘️  Regional Coverage (Local):")
        print("   • Local newspapers")
        print("   • Regional TV stations")
        print("   • Original reporting")
        print("   → Represents REGIONAL PERSPECTIVES")
        print("   → Geography MATTERS (different angles by location)")

        print("\n🔍 How to Use:")
        print("   1. National Baseline = What everyone sees")
        print("   2. Regional Clusters = Where coverage diverges")
        print("   3. Compare regional sentiment to national baseline")
        print("   4. Identify regional resistance/support patterns")

        print("\n💼 Business Value:")
        print("   • Policy analysts: Predict regional opposition")
        print("   • PR teams: Tailor messaging by region")
        print("   • Campaigns: Identify swing regions")

        print("=" * 80)
