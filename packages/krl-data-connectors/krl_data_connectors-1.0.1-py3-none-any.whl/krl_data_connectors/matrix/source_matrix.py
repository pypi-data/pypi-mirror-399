# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Multi-Dimensional Data Source Matrix

Framework × Model × Domain → Optimal Connector Selection

This module provides intelligent data source routing based on analytical context.
It combines framework requirements, model characteristics, and domain-specific
needs to select optimal data connectors with quality-scored fallback chains.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from krl_core import get_logger


logger = get_logger(__name__)


# =============================================================================
# ENUMS AND DATA CLASSES
# =============================================================================

class QualityDimension(str, Enum):
    """Six quality dimensions for data source scoring."""
    TEMPORAL_COVERAGE = "temporal_coverage"
    GEOGRAPHIC_GRANULARITY = "geographic_granularity"
    UPDATE_FREQUENCY = "update_frequency"
    COMPLETENESS = "completeness"
    RELIABILITY = "reliability"
    TIER_ACCESSIBILITY = "tier_accessibility"


@dataclass
class QualityScore:
    """
    Multi-dimensional quality score for a data source.

    All scores are on a 0-1 scale where:
    - 1.0 = Excellent
    - 0.7-0.9 = Good
    - 0.5-0.7 = Adequate
    - Below 0.5 = Poor
    """
    temporal_coverage: float = 0.0       # Historical depth and frequency
    geographic_granularity: float = 0.0  # Spatial resolution (tract > county > state > national)
    update_frequency: float = 0.0        # Data freshness (realtime > daily > monthly > annual)
    completeness: float = 0.0            # Data completeness (low null rates, high coverage)
    reliability: float = 0.0             # Source trustworthiness (official sources > research > derived)
    tier_accessibility: float = 0.0      # Access openness (community=1.0, professional=0.5, enterprise=0.0)

    def weighted_score(self, weights: dict[str, float]) -> float:
        """
        Compute weighted aggregate quality score.

        Args:
            weights: Dictionary mapping dimension names to weights (must sum to 1.0)

        Returns:
            Weighted overall quality score (0-1 scale)

        Example:
            >>> score = QualityScore(temporal_coverage=0.8, completeness=0.9, ...)
            >>> weights = {"temporal_coverage": 0.2, "completeness": 0.3, ...}
            >>> score.weighted_score(weights)
            0.85
        """
        return (
            self.temporal_coverage * weights.get('temporal_coverage', 0.20) +
            self.geographic_granularity * weights.get('geographic_granularity', 0.15) +
            self.update_frequency * weights.get('update_frequency', 0.15) +
            self.completeness * weights.get('completeness', 0.25) +
            self.reliability * weights.get('reliability', 0.15) +
            self.tier_accessibility * weights.get('tier_accessibility', 0.10)
        )

    def to_dict(self) -> dict[str, float]:
        """Convert to dictionary."""
        return {
            "temporal_coverage": self.temporal_coverage,
            "geographic_granularity": self.geographic_granularity,
            "update_frequency": self.update_frequency,
            "completeness": self.completeness,
            "reliability": self.reliability,
            "tier_accessibility": self.tier_accessibility,
        }

    @classmethod
    def from_dict(cls, data: dict[str, float]) -> "QualityScore":
        """Create from dictionary."""
        return cls(
            temporal_coverage=data.get("temporal_coverage", 0.0),
            geographic_granularity=data.get("geographic_granularity", 0.0),
            update_frequency=data.get("update_frequency", 0.0),
            completeness=data.get("completeness", 0.0),
            reliability=data.get("reliability", 0.0),
            tier_accessibility=data.get("tier_accessibility", 0.0),
        )


@dataclass
class ConnectorRecommendation:
    """
    Recommended connector with quality scoring.

    Represents a single data source recommendation with all
    metadata needed for intelligent source selection.
    """
    connector_name: str                    # Connector identifier (e.g., "census", "fred")
    quality_scores: QualityScore           # 6-dimensional quality assessment
    overall_quality: float                 # Weighted aggregate score (0-1)
    tier_required: str                     # "community", "professional", or "enterprise"
    confidence: str                        # "high", "medium", or "low"
    query_config: dict[str, Any] = field(default_factory=dict)  # Connector-specific config
    fallback_rank: int = 0                 # 0 = primary, 1+ = fallback

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "connector_name": self.connector_name,
            "quality_scores": self.quality_scores.to_dict(),
            "overall_quality": self.overall_quality,
            "tier_required": self.tier_required,
            "confidence": self.confidence,
            "query_config": self.query_config,
            "fallback_rank": self.fallback_rank,
        }


# =============================================================================
# DATA SOURCE MATRIX
# =============================================================================

class DataSourceMatrix:
    """
    Multi-dimensional matrix for Framework × Model × Domain → Connector selection.

    Provides intelligent routing to optimal data sources based on:
    - Framework requirements (e.g., MPI needs poverty indicators)
    - Model characteristics (e.g., ARIMA needs high-frequency time series)
    - Domain specifics (e.g., labor data from BLS vs Census)
    - User tier constraints (community/professional/enterprise)

    The matrix uses 6-dimensional quality scoring to rank sources and
    automatically provide fallback chains for resilience.

    Example Usage:
        >>> matrix = DataSourceMatrix(db_session)
        >>> sources = await matrix.get_optimal_sources(
        ...     framework='mpi',
        ...     model='logistic',
        ...     domain='health',
        ...     user_tier='professional'
        ... )
        >>> print(sources[0].connector_name)
        'census'
        >>> print(sources[0].overall_quality)
        0.87
    """

    # Default quality weights (can be overridden per context)
    DEFAULT_WEIGHTS = {
        'temporal_coverage': 0.20,
        'geographic_granularity': 0.15,
        'update_frequency': 0.15,
        'completeness': 0.25,      # Highest weight - data quality is critical
        'reliability': 0.15,
        'tier_accessibility': 0.10,
    }

    def __init__(
        self,
        db_session: Optional[Any] = None,
        config_overrides: Optional[dict] = None,
        enable_cache: bool = True
    ):
        """
        Initialize the Data Source Matrix.

        Args:
            db_session: SQLAlchemy async session for database lookups (optional)
            config_overrides: Optional configuration overrides
            enable_cache: Whether to enable in-memory caching (default: True)
        """
        self.db = db_session
        self.config_overrides = config_overrides or {}
        self.enable_cache = enable_cache
        self._cache = {} if enable_cache else None

        logger.info(
            "DataSourceMatrix initialized",
            extra={
                "has_db": bool(db_session),
                "cache_enabled": enable_cache
            }
        )

    async def get_optimal_sources(
        self,
        framework: str,
        model: str,
        domain: str,
        user_tier: str = 'community',
        include_fallbacks: bool = True,
        max_fallbacks: int = 3
    ) -> list[ConnectorRecommendation]:
        """
        Get optimal data source(s) for a Framework × Model × Domain combination.

        This is the primary API for intelligent connector selection. It returns
        an ordered list of connectors, with the best option first followed by
        quality-ranked fallbacks.

        Args:
            framework: Framework slug (e.g., 'mpi', 'hdi', 'remsom')
            model: Model ID (e.g., 'ols_robust', 'arima', 'logistic')
            domain: Data domain (e.g., 'labor', 'health', 'economic')
            user_tier: User's subscription tier for filtering
            include_fallbacks: Whether to include fallback options
            max_fallbacks: Maximum number of fallbacks to return

        Returns:
            Ordered list of ConnectorRecommendation (primary first, then fallbacks)

        Example:
            >>> matrix = DataSourceMatrix(db_session)
            >>> sources = await matrix.get_optimal_sources(
            ...     framework='mpi',
            ...     model='logistic',
            ...     domain='health',
            ...     user_tier='professional'
            ... )
            >>> print(sources[0].connector_name)
            'census'
            >>> print(sources[0].overall_quality)
            0.87
        """
        logger.debug(
            f"Getting optimal sources for {framework} × {model} × {domain}",
            extra={
                "framework": framework,
                "model": model,
                "domain": domain,
                "user_tier": user_tier
            }
        )

        # Check cache first
        if self.enable_cache:
            cache_key = f"{framework}:{model}:{domain}:{user_tier}"
            if cache_key in self._cache:
                logger.debug(f"Cache hit for {cache_key}")
                return self._cache[cache_key]

        # Try database lookup first
        if self.db:
            db_result = await self._lookup_database(
                framework, model, domain, user_tier, include_fallbacks, max_fallbacks
            )
            if db_result:
                if self.enable_cache:
                    self._cache[cache_key] = db_result
                return db_result

        # Fall back to programmatic defaults
        logger.debug(f"No database entry found for {framework} × {model} × {domain}, using defaults")
        default_result = await self._compute_default_routing(
            framework, model, domain, user_tier, include_fallbacks, max_fallbacks
        )

        if self.enable_cache and default_result:
            self._cache[cache_key] = default_result

        return default_result

    async def _lookup_database(
        self,
        framework: str,
        model: str,
        domain: str,
        user_tier: str,
        include_fallbacks: bool,
        max_fallbacks: int
    ) -> Optional[list[ConnectorRecommendation]]:
        """
        Lookup matrix entry in database.

        Args:
            framework: Framework slug
            model: Model ID
            domain: Domain name
            user_tier: User tier for filtering
            include_fallbacks: Whether to include fallbacks
            max_fallbacks: Max number of fallbacks

        Returns:
            List of recommendations or None if not found
        """
        if not self.db:
            return None

        try:
            # Import here to avoid circular dependencies
            from sqlalchemy import select
            from app.db_models.data_source_matrix import DataSourceMatrix as MatrixModel

            # Query for exact match
            stmt = select(MatrixModel).where(
                MatrixModel.framework_slug == framework.lower(),
                MatrixModel.model_id == model.lower(),
                MatrixModel.domain == domain.lower(),
                MatrixModel.is_active == True
            )

            result = await self.db.execute(stmt)
            entry = result.scalar_one_or_none()

            if not entry:
                return None

            logger.debug(f"Found database entry for {framework} × {model} × {domain}")

            # Build primary recommendation
            quality_scores = QualityScore.from_dict(entry.quality_scores or {})
            recommendations = [
                ConnectorRecommendation(
                    connector_name=entry.primary_connector,
                    quality_scores=quality_scores,
                    overall_quality=float(entry.overall_quality_score or 0.0),
                    tier_required=entry.min_tier_required or "community",
                    confidence=entry.confidence_level,
                    query_config=entry.connector_config or {},
                    fallback_rank=0
                )
            ]

            # Add fallbacks if requested
            if include_fallbacks and entry.fallback_connectors:
                for i, connector in enumerate(entry.fallback_connectors[:max_fallbacks]):
                    # For fallbacks, we'd need to look up their quality scores
                    # For now, use slightly degraded primary scores
                    fallback_scores = QualityScore(
                        temporal_coverage=quality_scores.temporal_coverage * 0.9,
                        geographic_granularity=quality_scores.geographic_granularity * 0.9,
                        update_frequency=quality_scores.update_frequency * 0.9,
                        completeness=quality_scores.completeness * 0.9,
                        reliability=quality_scores.reliability * 0.9,
                        tier_accessibility=quality_scores.tier_accessibility * 0.9,
                    )
                    recommendations.append(
                        ConnectorRecommendation(
                            connector_name=connector,
                            quality_scores=fallback_scores,
                            overall_quality=fallback_scores.weighted_score(self.DEFAULT_WEIGHTS),
                            tier_required=entry.min_tier_required or "community",
                            confidence="medium",
                            query_config={},
                            fallback_rank=i + 1
                        )
                    )

            return recommendations

        except Exception as e:
            logger.error(f"Database lookup failed: {e}", exc_info=True)
            return None

    async def _compute_default_routing(
        self,
        framework: str,
        model: str,
        domain: str,
        user_tier: str,
        include_fallbacks: bool,
        max_fallbacks: int
    ) -> list[ConnectorRecommendation]:
        """
        Compute optimal routing using heuristics when no DB entry exists.

        This implements the "smart defaults" logic:
        1. Match domain to primary connectors from domain_connector_map
        2. Apply quality scoring heuristics
        3. Filter by user tier
        4. Rank and return top options

        Args:
            framework: Framework slug
            model: Model ID
            domain: Domain name
            user_tier: User tier
            include_fallbacks: Whether to include fallbacks
            max_fallbacks: Max fallbacks

        Returns:
            List of connector recommendations
        """
        # Import domain connector map
        try:
            import sys
            sys.path.append("/Users/bcdelo/Documents/GitHub/KRL/Private IP/krl-premium-backend")
            from app.config.domain_connector_map import (
                get_domain_config,
                get_primary_connector,
                get_fallback_connectors
            )

            # Get domain config
            domain_config = get_domain_config(domain)
            if not domain_config:
                logger.warning(f"No domain config found for {domain}")
                return []

            # Get primary and fallback connectors
            primary = get_primary_connector(domain)
            fallbacks = get_fallback_connectors(domain) if include_fallbacks else []

            logger.debug(
                f"Using default routing for {domain}: primary={primary}, fallbacks={fallbacks}"
            )

            # Build recommendations with quality scoring
            from krl_data_connectors.matrix.quality_scorer import QualityScorer

            scorer = QualityScorer()
            recommendations = []

            # Get queries for this domain
            queries = domain_config.get("queries", [])
            
            # Find primary query (matching primary connector, not a fallback)
            primary_query = None
            for query in queries:
                if query.get("connector") == primary and not query.get("fallback_for"):
                    primary_query = query
                    break
            if not primary_query and queries:
                primary_query = queries[0]

            # Score primary connector
            if primary:
                quality_scores = scorer.score_connector(primary, domain)
                overall_quality = quality_scores.weighted_score(self.DEFAULT_WEIGHTS)

                # Include full query config: series_ids, params, field_mapping, query_type
                query_config = {}
                if primary_query:
                    query_config = {
                        "series_ids": primary_query.get("series_ids", []),
                        "params": primary_query.get("params", {}),
                        "field_mapping": primary_query.get("field_mapping", {}),
                        "query_type": str(primary_query.get("query_type", "series")),
                        "dataset": primary_query.get("dataset"),
                        "table_name": primary_query.get("table_name"),
                    }
                    # Remove None values
                    query_config = {k: v for k, v in query_config.items() if v is not None}

                recommendations.append(
                    ConnectorRecommendation(
                        connector_name=primary,
                        quality_scores=quality_scores,
                        overall_quality=overall_quality,
                        tier_required=domain_config.get("tier_required", "community"),
                        confidence="medium",
                        query_config=query_config,
                        fallback_rank=0
                    )
                )

            # Score fallback connectors
            for i, connector in enumerate(fallbacks[:max_fallbacks]):
                quality_scores = scorer.score_connector(connector, domain)
                overall_quality = quality_scores.weighted_score(self.DEFAULT_WEIGHTS)

                # Find fallback query for this connector
                fallback_query = None
                for query in queries:
                    if query.get("connector") == connector:
                        fallback_query = query
                        break
                
                fallback_query_config = {}
                if fallback_query:
                    fallback_query_config = {
                        "series_ids": fallback_query.get("series_ids", []),
                        "params": fallback_query.get("params", {}),
                        "field_mapping": fallback_query.get("field_mapping", {}),
                        "query_type": str(fallback_query.get("query_type", "series")),
                    }
                    fallback_query_config = {k: v for k, v in fallback_query_config.items() if v}

                recommendations.append(
                    ConnectorRecommendation(
                        connector_name=connector,
                        quality_scores=quality_scores,
                        overall_quality=overall_quality,
                        tier_required=domain_config.get("tier_required", "community"),
                        confidence="low",
                        query_config=fallback_query_config,
                        fallback_rank=i + 1
                    )
                )

            # Filter by tier and sort by quality
            tier_hierarchy = {"community": 0, "professional": 1, "enterprise": 2}
            user_tier_level = tier_hierarchy.get(user_tier, 0)

            filtered = [
                rec for rec in recommendations
                if tier_hierarchy.get(rec.tier_required, 0) <= user_tier_level
            ]

            # Sort by quality score (descending)
            filtered.sort(key=lambda r: r.overall_quality, reverse=True)

            return filtered

        except ImportError as e:
            logger.error(f"Failed to import domain_connector_map: {e}")
            return []
        except Exception as e:
            logger.error(f"Default routing computation failed: {e}", exc_info=True)
            return []

    async def get_optimal_sources_bulk(
        self,
        framework: str,
        model: str,
        domains: list[str],
        user_tier: str = 'community'
    ) -> dict[str, list[ConnectorRecommendation]]:
        """
        Get optimal sources for multiple domains at once.

        Efficient bulk query for when a framework needs data from
        multiple domains simultaneously.

        Args:
            framework: Framework slug
            model: Model ID
            domains: List of domain names
            user_tier: User tier

        Returns:
            Dictionary mapping domain names to recommendation lists

        Example:
            >>> sources = await matrix.get_optimal_sources_bulk(
            ...     framework='mpi',
            ...     model='logistic',
            ...     domains=['health', 'education', 'housing'],
            ...     user_tier='professional'
            ... )
            >>> print(sources['health'][0].connector_name)
            'census'
        """
        results = {}
        for domain in domains:
            results[domain] = await self.get_optimal_sources(
                framework=framework,
                model=model,
                domain=domain,
                user_tier=user_tier
            )
        return results

    def clear_cache(self):
        """Clear the in-memory cache."""
        if self._cache is not None:
            self._cache.clear()
            logger.info("Matrix cache cleared")
