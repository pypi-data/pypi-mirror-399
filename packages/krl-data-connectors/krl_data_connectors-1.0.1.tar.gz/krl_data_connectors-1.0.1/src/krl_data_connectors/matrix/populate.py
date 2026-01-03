# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Matrix Population Tools

Utilities for populating and maintaining the data source matrix.
Seeds the matrix from existing configuration and infrastructure.
"""

import asyncio
import logging
from typing import Any, Optional

from krl_core import get_logger


logger = get_logger(__name__)


class MatrixPopulator:
    """
    Automated population of the data source matrix.

    Populates the matrix by:
    1. Seeding from existing domain_connector_map
    2. Inferring framework-domain compatibility
    3. Computing quality scores for all connectors
    4. Generating model-domain affinities
    """

    def __init__(self, db_session: Any):
        """
        Initialize populator.

        Args:
            db_session: SQLAlchemy async session
        """
        self.db = db_session
        self.entries_created = 0
        self.profiles_created = 0

    async def populate_from_domain_map(self):
        """
        Seed matrix from existing domain_connector_map.

        Creates baseline entries for all domain → connector mappings,
        then infers framework and model compatibility.

        This is Phase 1 of matrix population, targeting ~2,000 entries.
        """
        logger.info("Starting matrix population from domain_connector_map")

        try:
            import sys
            sys.path.append("/Users/bcdelo/Documents/GitHub/KRL/Private IP/krl-premium-backend")
            from app.config.domain_connector_map import (
                DOMAIN_CONNECTOR_MAP,
                FRAMEWORK_DOMAIN_REQUIREMENTS,
            )

            # Import models
            from app.db_models.data_source_matrix import DataSourceMatrix as MatrixModel
            from sqlalchemy import select

            # Iterate over all domains
            for domain, config in DOMAIN_CONNECTOR_MAP.items():
                primary = config.get("primary_connector")
                fallbacks = config.get("fallback_connectors", [])
                tier_required = config.get("tier_required", "community")

                logger.info(f"Processing domain: {domain}")

                # Infer compatible frameworks
                frameworks = self._infer_frameworks_for_domain(domain, FRAMEWORK_DOMAIN_REQUIREMENTS)

                # Infer compatible models
                models = self._infer_models_for_domain(domain)

                # Create matrix entries for each framework × model × domain combination
                for framework in frameworks:
                    for model in models:
                        # Check if entry already exists
                        stmt = select(MatrixModel).where(
                            MatrixModel.framework_slug == framework,
                            MatrixModel.model_id == model,
                            MatrixModel.domain == domain
                        )
                        result = await self.db.execute(stmt)
                        existing = result.scalar_one_or_none()

                        if existing:
                            logger.debug(f"Entry already exists for {framework} × {model} × {domain}")
                            continue

                        # Compute quality scores
                        quality_scores = await self._compute_quality_scores(primary, domain)

                        # Create entry
                        entry = MatrixModel(
                            framework_slug=framework,
                            model_id=model,
                            domain=domain,
                            primary_connector=primary,
                            fallback_connectors=fallbacks,
                            quality_scores=quality_scores,
                            overall_quality_score=self._compute_overall_quality(quality_scores),
                            min_tier_required=tier_required,
                            confidence_level="medium",
                            connector_config={},
                            notes=f"Auto-populated from domain_connector_map"
                        )

                        self.db.add(entry)
                        self.entries_created += 1

                        if self.entries_created % 100 == 0:
                            logger.info(f"Created {self.entries_created} matrix entries...")

            # Commit all entries
            await self.db.commit()

            logger.info(
                f"Matrix population complete: {self.entries_created} entries created"
            )

            return {
                "success": True,
                "entries_created": self.entries_created,
                "message": f"Successfully populated matrix with {self.entries_created} entries"
            }

        except Exception as e:
            logger.error(f"Matrix population failed: {e}", exc_info=True)
            await self.db.rollback()
            return {
                "success": False,
                "error": str(e)
            }

    def _infer_frameworks_for_domain(
        self,
        domain: str,
        framework_requirements: dict
    ) -> list[str]:
        """
        Infer which frameworks need this domain.

        Args:
            domain: Domain name
            framework_requirements: Dict mapping frameworks to required domains

        Returns:
            List of framework slugs that require this domain
        """
        frameworks = []

        for fw, domains in framework_requirements.items():
            if domain in domains:
                frameworks.append(fw)

        # If no specific frameworks found, add to general frameworks
        if not frameworks:
            frameworks = ["general"]

        logger.debug(f"Domain {domain} → frameworks: {frameworks}")
        return frameworks

    def _infer_models_for_domain(self, domain: str) -> list[str]:
        """
        Infer which models are compatible with this domain.

        Maps domains to model categories based on typical use cases.

        Args:
            domain: Domain name

        Returns:
            List of model IDs compatible with this domain
        """
        # Map domains to model categories
        domain_to_models = {
            "labor": ["ols", "panel_fixed_effects", "arima", "var", "logistic"],
            "economic": ["ols", "arima", "var", "vecm", "garch", "prophet"],
            "health": ["logistic", "poisson", "survival", "panel_fixed_effects"],
            "education": ["ols", "logistic", "panel_fixed_effects", "hierarchical"],
            "housing": ["ols", "arima", "hedonic", "spatial_lag"],
            "demographic": ["ols", "logistic", "cohort_component", "microsimulation"],
            "financial": ["garch", "var", "copula", "credit_risk"],
            "transportation": ["ols", "gravity_model", "logit_choice"],
            "environment": ["arima", "spatial_autocorrelation", "panel_fixed_effects"],
            "governance": ["ols", "panel_fixed_effects", "event_study"],
            "climate": ["arima", "garch", "extreme_value"],
            "energy": ["arima", "var", "structural_breaks"],
            "sam": ["input_output", "cge", "sam_multiplier"],
            "sectors": ["shift_share", "location_quotient", "panel_fixed_effects"],
            "spatial": ["spatial_lag", "spatial_error", "geographically_weighted"],
            "causal": ["did", "rdd", "synthetic_control", "propensity_score", "iv"],
        }

        models = domain_to_models.get(domain, ["ols", "logistic", "arima"])

        logger.debug(f"Domain {domain} → models: {models}")
        return models

    async def _compute_quality_scores(
        self,
        connector_name: str,
        domain: str
    ) -> dict[str, float]:
        """
        Compute quality scores for a connector-domain pair.

        Args:
            connector_name: Connector identifier
            domain: Domain name

        Returns:
            Dict with 6-dimensional quality scores
        """
        try:
            from krl_data_connectors.matrix.quality_scorer import QualityScorer

            scorer = QualityScorer()
            quality_score = scorer.score_connector(connector_name, domain)

            return quality_score.to_dict()

        except Exception as e:
            logger.warning(f"Failed to compute quality scores for {connector_name} × {domain}: {e}")
            # Return default scores
            return {
                "temporal_coverage": 0.7,
                "geographic_granularity": 0.7,
                "update_frequency": 0.7,
                "completeness": 0.7,
                "reliability": 0.7,
                "tier_accessibility": 0.7,
            }

    def _compute_overall_quality(self, quality_scores: dict[str, float]) -> float:
        """
        Compute overall quality score from individual dimensions.

        Uses default weights if not specified.

        Args:
            quality_scores: Dict with 6-dimensional scores

        Returns:
            Weighted overall quality score
        """
        weights = {
            "temporal_coverage": 0.20,
            "geographic_granularity": 0.15,
            "update_frequency": 0.15,
            "completeness": 0.25,
            "reliability": 0.15,
            "tier_accessibility": 0.10,
        }

        total = sum(
            quality_scores.get(dim, 0.0) * weight
            for dim, weight in weights.items()
        )

        return round(total, 2)

    async def populate_quality_profiles(self):
        """
        Populate connector_quality_profiles table.

        Computes and stores quality profiles for all connector-domain pairs.
        """
        logger.info("Starting quality profile population")

        try:
            import sys
            sys.path.append("/Users/bcdelo/Documents/GitHub/KRL/Private IP/krl-premium-backend")
            from app.config.domain_connector_map import DOMAIN_CONNECTOR_MAP
            from app.db_models.data_source_matrix import ConnectorQualityProfile
            from krl_data_connectors.matrix.quality_scorer import QualityScorer

            scorer = QualityScorer()

            # Get all unique connector-domain pairs
            connector_domain_pairs = set()

            for domain, config in DOMAIN_CONNECTOR_MAP.items():
                primary = config.get("primary_connector")
                fallbacks = config.get("fallback_connectors", [])

                connector_domain_pairs.add((primary, domain))
                for fallback in fallbacks:
                    connector_domain_pairs.add((fallback, domain))

            logger.info(f"Found {len(connector_domain_pairs)} connector-domain pairs")

            # Create quality profiles
            for connector_name, domain in connector_domain_pairs:
                # Check if profile exists
                from sqlalchemy import select
                stmt = select(ConnectorQualityProfile).where(
                    ConnectorQualityProfile.connector_name == connector_name,
                    ConnectorQualityProfile.domain == domain
                )
                result = await self.db.execute(stmt)
                existing = result.scalar_one_or_none()

                if existing:
                    logger.debug(f"Profile already exists for {connector_name} × {domain}")
                    continue

                # Compute quality score
                quality_score = scorer.score_connector(connector_name, domain)

                # Get metadata from scorer
                metadata = scorer.CONNECTOR_METADATA.get(
                    connector_name.lower(),
                    scorer.CONNECTOR_METADATA["default"]
                )

                # Create profile
                profile = ConnectorQualityProfile(
                    connector_name=connector_name,
                    domain=domain,
                    temporal_coverage=quality_score.temporal_coverage,
                    temporal_start_year=2024 - metadata.get("temporal_years", 10),
                    temporal_frequency=metadata.get("update_cadence", "annual"),
                    geographic_granularity=quality_score.geographic_granularity,
                    geographic_levels=metadata.get("geographic_levels", ["national"]),
                    update_frequency=quality_score.update_frequency,
                    update_cadence=metadata.get("update_cadence", "annual"),
                    completeness=quality_score.completeness,
                    reliability=quality_score.reliability,
                    official_source=metadata.get("official_source", False),
                    tier_accessibility=quality_score.tier_accessibility,
                    assessment_version="1.0.0"
                )

                self.db.add(profile)
                self.profiles_created += 1

                if self.profiles_created % 20 == 0:
                    logger.info(f"Created {self.profiles_created} quality profiles...")

            # Commit all profiles
            await self.db.commit()

            logger.info(
                f"Quality profile population complete: {self.profiles_created} profiles created"
            )

            return {
                "success": True,
                "profiles_created": self.profiles_created,
                "message": f"Successfully populated {self.profiles_created} quality profiles"
            }

        except Exception as e:
            logger.error(f"Quality profile population failed: {e}", exc_info=True)
            await self.db.rollback()
            return {
                "success": False,
                "error": str(e)
            }


# =============================================================================
# CLI INTERFACE
# =============================================================================

async def main():
    """CLI interface for matrix population."""
    import argparse

    parser = argparse.ArgumentParser(description="Populate Data Source Matrix")
    parser.add_argument(
        "--database-url",
        default="postgresql+asyncpg://postgres:p4ssw0rd@localhost:5432/krl_premium",
        help="Database URL"
    )
    parser.add_argument(
        "--mode",
        choices=["matrix", "profiles", "both"],
        default="both",
        help="What to populate"
    )

    args = parser.parse_args()

    # Initialize database session
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker

    engine = create_async_engine(args.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        populator = MatrixPopulator(session)

        if args.mode in ["matrix", "both"]:
            result = await populator.populate_from_domain_map()
            print(f"\nMatrix Population: {result}")

        if args.mode in ["profiles", "both"]:
            result = await populator.populate_quality_profiles()
            print(f"\nQuality Profiles: {result}")


if __name__ == "__main__":
    asyncio.run(main())
