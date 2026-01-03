# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Quality Scoring Engine

Computes 6-dimensional quality scores for data connectors:
1. Temporal Coverage - Historical depth and frequency
2. Geographic Granularity - Spatial resolution
3. Update Frequency - Data freshness
4. Completeness - Null rates and coverage
5. Reliability - Source trustworthiness
6. Tier Accessibility - Access openness
"""

from typing import Any, Optional

from krl_core import get_logger
from krl_data_connectors.matrix.source_matrix import QualityScore


logger = get_logger(__name__)


class QualityScorer:
    """
    Scores data connectors on 6 quality dimensions.

    Uses heuristics based on known connector characteristics to
    compute quality scores when no database profile exists.
    """

    # Connector metadata for quality scoring
    CONNECTOR_METADATA = {
        # Federal Reserve Economic Data
        "fred": {
            "temporal_years": 70,
            "geographic_levels": ["national", "state"],
            "update_cadence": "daily",
            "official_source": True,
            "tier": "community"
        },
        "fred_full": {
            "temporal_years": 100,
            "geographic_levels": ["national", "state", "metro"],
            "update_cadence": "daily",
            "official_source": True,
            "tier": "professional"
        },

        # Bureau of Labor Statistics
        "bls": {
            "temporal_years": 25,
            "geographic_levels": ["national", "state", "metro"],
            "update_cadence": "monthly",
            "official_source": True,
            "tier": "community"
        },
        "bls_enhanced": {
            "temporal_years": 30,
            "geographic_levels": ["national", "state", "county", "metro"],
            "update_cadence": "monthly",
            "official_source": True,
            "tier": "professional"
        },

        # US Census Bureau
        "census": {
            "temporal_years": 10,
            "geographic_levels": ["national", "state", "county"],
            "update_cadence": "annual",
            "official_source": True,
            "tier": "community"
        },
        "census_acs_detailed": {
            "temporal_years": 10,
            "geographic_levels": ["national", "state", "county", "tract", "block_group"],
            "update_cadence": "annual",
            "official_source": True,
            "tier": "professional"
        },

        # Bureau of Economic Analysis
        "bea": {
            "temporal_years": 50,
            "geographic_levels": ["national", "state", "county", "metro"],
            "update_cadence": "quarterly",
            "official_source": True,
            "tier": "community"
        },

        # World Bank
        "world_bank": {
            "temporal_years": 60,
            "geographic_levels": ["national"],
            "update_cadence": "annual",
            "official_source": True,
            "tier": "community"
        },

        # OECD
        "oecd": {
            "temporal_years": 60,
            "geographic_levels": ["national"],
            "update_cadence": "annual",
            "official_source": True,
            "tier": "community"
        },

        # CDC
        "cdc": {
            "temporal_years": 20,
            "geographic_levels": ["national", "state", "county"],
            "update_cadence": "monthly",
            "official_source": True,
            "tier": "professional"
        },

        # HUD
        "hud": {
            "temporal_years": 20,
            "geographic_levels": ["national", "state", "county", "zip"],
            "update_cadence": "annual",
            "official_source": True,
            "tier": "professional"
        },

        # Zillow (market-based, not official)
        "zillow": {
            "temporal_years": 15,
            "geographic_levels": ["national", "state", "metro", "zip"],
            "update_cadence": "monthly",
            "official_source": False,
            "tier": "professional"
        },

        # Default fallback
        "default": {
            "temporal_years": 10,
            "geographic_levels": ["national"],
            "update_cadence": "annual",
            "official_source": False,
            "tier": "community"
        }
    }

    def score_connector(
        self,
        connector_name: str,
        domain: str,
        db_session: Optional[Any] = None
    ) -> QualityScore:
        """
        Compute comprehensive quality score for a connector-domain pair.

        Args:
            connector_name: Name of the connector
            domain: Data domain
            db_session: Optional database session for profile lookup

        Returns:
            QualityScore with all 6 dimensions scored

        Example:
            >>> scorer = QualityScorer()
            >>> score = scorer.score_connector("fred", "economic")
            >>> print(score.temporal_coverage)
            0.95
        """
        # Try database lookup first
        if db_session:
            profile = self._lookup_quality_profile(db_session, connector_name, domain)
            if profile:
                return self._profile_to_score(profile)

        # Fall back to heuristic scoring
        logger.debug(f"Computing heuristic quality score for {connector_name} × {domain}")
        return self._compute_heuristic_score(connector_name, domain)

    def _compute_heuristic_score(self, connector_name: str, domain: str) -> QualityScore:
        """
        Compute score using heuristics based on connector metadata.

        Args:
            connector_name: Connector identifier
            domain: Data domain

        Returns:
            QualityScore computed from heuristics
        """
        # Normalize connector name (handle variations)
        normalized_name = connector_name.lower().replace("_connector", "").replace("-", "_")

        # Get metadata (with fallback to default)
        metadata = self.CONNECTOR_METADATA.get(
            normalized_name,
            self.CONNECTOR_METADATA["default"]
        )

        # Score each dimension
        temporal = self._score_temporal_coverage(metadata)
        geographic = self._score_geographic_granularity(metadata, domain)
        freshness = self._score_update_frequency(metadata, domain)
        completeness = self._score_completeness(metadata, connector_name)
        reliability = self._score_reliability(metadata)
        accessibility = self._score_tier_accessibility(metadata)

        score = QualityScore(
            temporal_coverage=temporal,
            geographic_granularity=geographic,
            update_frequency=freshness,
            completeness=completeness,
            reliability=reliability,
            tier_accessibility=accessibility
        )

        logger.debug(
            f"Quality score for {connector_name} × {domain}: {score.weighted_score({}):.2f}",
            extra={"connector": connector_name, "domain": domain, "scores": score.to_dict()}
        )

        return score

    def _score_temporal_coverage(self, metadata: dict) -> float:
        """
        Score temporal coverage based on historical depth.

        Scoring:
        - 50+ years → 1.0 (excellent historical depth)
        - 25-50 years → 0.8-0.95
        - 10-25 years → 0.6-0.8
        - 5-10 years → 0.4-0.6
        - < 5 years → 0.2-0.4

        Args:
            metadata: Connector metadata

        Returns:
            Score from 0-1
        """
        years = metadata.get("temporal_years", 10)

        # Formula: score = min(1.0, (years / 50) * 0.5 + 0.5)
        # This gives: 5 years → 0.55, 25 years → 0.75, 50+ years → 1.0
        score = min(1.0, (years / 50) * 0.5 + 0.5)

        return round(score, 2)

    def _score_geographic_granularity(self, metadata: dict, domain: str) -> float:
        """
        Score geographic granularity based on finest level available.

        Scoring:
        - Block group level → 1.0
        - Tract level → 0.95
        - ZIP code level → 0.9
        - County level → 0.8
        - Metro area level → 0.7
        - State level → 0.6
        - National only → 0.3

        Args:
            metadata: Connector metadata
            domain: Data domain (some domains don't need fine granularity)

        Returns:
            Score from 0-1
        """
        levels = metadata.get("geographic_levels", ["national"])

        # Granularity hierarchy
        granularity_scores = {
            "block_group": 1.0,
            "tract": 0.95,
            "zip": 0.9,
            "county": 0.8,
            "metro": 0.7,
            "state": 0.6,
            "national": 0.3
        }

        # Get finest level available
        finest_score = 0.3  # Default to national
        for level in levels:
            level_lower = level.lower()
            if level_lower in granularity_scores:
                finest_score = max(finest_score, granularity_scores[level_lower])

        # Some domains (like climate, energy) don't need fine granularity
        if domain in ["climate", "energy", "governance", "sam"]:
            finest_score = max(finest_score, 0.7)  # Boost score for national-level domains

        return round(finest_score, 2)

    def _score_update_frequency(self, metadata: dict, domain: str) -> float:
        """
        Score update frequency based on how fresh the data is.

        Scoring:
        - Realtime/Daily → 1.0
        - Weekly → 0.9
        - Monthly → 0.8
        - Quarterly → 0.6
        - Annual → 0.4
        - Less frequent → 0.2

        Args:
            metadata: Connector metadata
            domain: Data domain (some domains have slower natural update cycles)

        Returns:
            Score from 0-1
        """
        cadence = metadata.get("update_cadence", "annual").lower()

        frequency_scores = {
            "realtime": 1.0,
            "daily": 1.0,
            "weekly": 0.9,
            "monthly": 0.8,
            "quarterly": 0.6,
            "annual": 0.4,
            "biennial": 0.2
        }

        score = frequency_scores.get(cadence, 0.4)

        # Some domains (demographic, housing) update slowly by nature
        # Boost their scores to avoid penalizing natural cadence
        slow_update_domains = ["demographic", "housing", "education", "sam"]
        if domain in slow_update_domains and cadence == "annual":
            score = max(score, 0.7)  # Boost annual data for slow-update domains

        return round(score, 2)

    def _score_completeness(self, metadata: dict, connector_name: str) -> float:
        """
        Score data completeness based on typical null rates and coverage.

        This is an estimate based on known connector quality.

        Scoring:
        - Census/BLS (high quality) → 0.90-0.95
        - FRED/BEA (very good) → 0.85-0.90
        - International (OECD/World Bank) → 0.80-0.85
        - Research/Derived → 0.70-0.80
        - Experimental → 0.60-0.70

        Args:
            metadata: Connector metadata
            connector_name: Connector identifier

        Returns:
            Score from 0-1
        """
        # High-quality official sources
        if connector_name.lower() in ["census", "census_acs_detailed", "bls", "bls_enhanced"]:
            return 0.95

        # Very good federal sources
        if connector_name.lower() in ["fred", "fred_full", "bea", "cdc", "hud"]:
            return 0.90

        # Good international sources
        if connector_name.lower() in ["world_bank", "oecd", "imf"]:
            return 0.82

        # Research/derived sources
        if connector_name.lower() in ["zillow", "opportunity_insights"]:
            return 0.75

        # Default for unknown sources
        return 0.70

    def _score_reliability(self, metadata: dict) -> float:
        """
        Score source reliability/trustworthiness.

        Scoring:
        - Official government sources → 0.95
        - International organizations → 0.85
        - Academic/research → 0.75
        - Commercial/derived → 0.65

        Args:
            metadata: Connector metadata

        Returns:
            Score from 0-1
        """
        is_official = metadata.get("official_source", False)

        if is_official:
            return 0.95
        else:
            # Non-official sources (commercial, derived, etc.)
            return 0.70

    def _score_tier_accessibility(self, metadata: dict) -> float:
        """
        Score tier accessibility.

        Scoring:
        - Community (free) → 1.0
        - Professional → 0.5
        - Enterprise → 0.0

        This encourages use of accessible sources when quality is similar.

        Args:
            metadata: Connector metadata

        Returns:
            Score from 0-1
        """
        tier = metadata.get("tier", "community").lower()

        tier_scores = {
            "community": 1.0,
            "professional": 0.5,
            "enterprise": 0.0
        }

        return tier_scores.get(tier, 1.0)

    def _lookup_quality_profile(self, db_session, connector_name: str, domain: str):
        """
        Lookup quality profile from database.

        Args:
            db_session: Database session
            connector_name: Connector name
            domain: Domain name

        Returns:
            Quality profile or None
        """
        try:
            from sqlalchemy import select
            from app.db_models.data_source_matrix import ConnectorQualityProfile

            stmt = select(ConnectorQualityProfile).where(
                ConnectorQualityProfile.connector_name == connector_name,
                ConnectorQualityProfile.domain == domain
            )

            result = db_session.execute(stmt)
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Database profile lookup failed: {e}")
            return None

    def _profile_to_score(self, profile) -> QualityScore:
        """
        Convert database profile to QualityScore.

        Args:
            profile: ConnectorQualityProfile instance

        Returns:
            QualityScore
        """
        return QualityScore(
            temporal_coverage=float(profile.temporal_coverage or 0.0),
            geographic_granularity=float(profile.geographic_granularity or 0.0),
            update_frequency=float(profile.update_frequency or 0.0),
            completeness=float(profile.completeness or 0.0),
            reliability=float(profile.reliability or 0.0),
            tier_accessibility=float(profile.tier_accessibility or 0.0),
        )
