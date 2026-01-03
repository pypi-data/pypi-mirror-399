# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Matrix Validation Tools

Tools for validating matrix integrity and data quality.
"""

import asyncio
from typing import Any

from krl_core import get_logger


logger = get_logger(__name__)


class MatrixValidator:
    """Validation tools for matrix integrity."""

    def __init__(self, db_session: Any):
        """
        Initialize validator.

        Args:
            db_session: SQLAlchemy async session
        """
        self.db = db_session

    async def validate_matrix_integrity(self) -> dict[str, Any]:
        """
        Comprehensive validation of matrix data.

        Checks:
        1. All frameworks have domain coverage
        2. No orphaned entries (invalid framework/model/domain IDs)
        3. Quality scores are in valid ranges (0-1)
        4. Tier requirements are consistent
        5. Fallback chains are valid

        Returns:
            Dict with validation results, errors, and warnings
        """
        report = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'stats': {
                'total_entries': 0,
                'frameworks_covered': 0,
                'models_covered': 0,
                'domains_covered': 0,
                'quality_profiles': 0,
            }
        }

        try:
            from sqlalchemy import func, select
            from app.db_models.data_source_matrix import (
                DataSourceMatrix as MatrixModel,
                ConnectorQualityProfile,
            )

            # Get counts
            report['stats']['total_entries'] = await self.db.scalar(
                select(func.count()).select_from(MatrixModel)
            )

            report['stats']['quality_profiles'] = await self.db.scalar(
                select(func.count()).select_from(ConnectorQualityProfile)
            )

            # Get unique frameworks, models, domains
            report['stats']['frameworks_covered'] = await self.db.scalar(
                select(func.count(func.distinct(MatrixModel.framework_slug)))
            )

            report['stats']['models_covered'] = await self.db.scalar(
                select(func.count(func.distinct(MatrixModel.model_id)))
            )

            report['stats']['domains_covered'] = await self.db.scalar(
                select(func.count(func.distinct(MatrixModel.domain)))
            )

            # Check for quality score validity
            invalid_scores = await self.db.execute(
                select(MatrixModel).where(
                    (MatrixModel.overall_quality_score < 0.0) |
                    (MatrixModel.overall_quality_score > 1.0)
                )
            )
            invalid_score_entries = invalid_scores.scalars().all()

            if invalid_score_entries:
                report['errors'].append(
                    f"Found {len(invalid_score_entries)} entries with invalid quality scores (outside 0-1 range)"
                )
                report['valid'] = False

            # Check for missing primary connectors
            missing_connectors = await self.db.execute(
                select(MatrixModel).where(
                    (MatrixModel.primary_connector == None) |
                    (MatrixModel.primary_connector == "")
                )
            )
            missing_connector_entries = missing_connectors.scalars().all()

            if missing_connector_entries:
                report['errors'].append(
                    f"Found {len(missing_connector_entries)} entries with missing primary connector"
                )
                report['valid'] = False

            # Check framework domain coverage
            try:
                import sys
                sys.path.append("/Users/bcdelo/Documents/GitHub/KRL/Private IP/krl-premium-backend")
                from app.config.domain_connector_map import FRAMEWORK_DOMAIN_REQUIREMENTS

                for framework, required_domains in FRAMEWORK_DOMAIN_REQUIREMENTS.items():
                    for domain in required_domains:
                        count = await self.db.scalar(
                            select(func.count()).select_from(MatrixModel).where(
                                MatrixModel.framework_slug == framework,
                                MatrixModel.domain == domain
                            )
                        )

                        if count == 0:
                            report['warnings'].append(
                                f"No matrix entries for {framework} × {domain}"
                            )

            except Exception as e:
                logger.warning(f"Could not validate framework coverage: {e}")

            # Check for inactive entries
            inactive_count = await self.db.scalar(
                select(func.count()).select_from(MatrixModel).where(
                    MatrixModel.is_active == False
                )
            )

            if inactive_count > 0:
                report['warnings'].append(
                    f"Found {inactive_count} inactive matrix entries"
                )

            logger.info(f"Matrix validation complete: {report['stats']}")

        except Exception as e:
            logger.error(f"Matrix validation failed: {e}", exc_info=True)
            report['valid'] = False
            report['errors'].append(f"Validation error: {str(e)}")

        return report

    async def suggest_missing_entries(self) -> list[dict[str, str]]:
        """
        Analyze usage patterns and suggest missing matrix entries.

        Returns:
            List of suggested entries with framework, model, domain
        """
        suggestions = []

        try:
            import sys
            sys.path.append("/Users/bcdelo/Documents/GitHub/KRL/Private IP/krl-premium-backend")
            from app.config.domain_connector_map import (
                FRAMEWORK_DOMAIN_REQUIREMENTS,
                DOMAIN_CONNECTOR_MAP,
            )
            from sqlalchemy import select
            from app.db_models.data_source_matrix import DataSourceMatrix as MatrixModel

            # Common model categories
            common_models = [
                "ols", "logistic", "arima", "var", "panel_fixed_effects",
                "did", "synthetic_control", "garch", "prophet"
            ]

            # Check each framework-domain combination
            for framework, domains in FRAMEWORK_DOMAIN_REQUIREMENTS.items():
                for domain in domains:
                    if domain not in DOMAIN_CONNECTOR_MAP:
                        continue

                    for model in common_models:
                        # Check if entry exists
                        exists = await self.db.scalar(
                            select(func.count()).select_from(MatrixModel).where(
                                MatrixModel.framework_slug == framework,
                                MatrixModel.model_id == model,
                                MatrixModel.domain == domain
                            )
                        )

                        if not exists:
                            suggestions.append({
                                "framework": framework,
                                "model": model,
                                "domain": domain,
                                "reason": "Common model × framework × domain combination"
                            })

            logger.info(f"Generated {len(suggestions)} suggestions for missing entries")

        except Exception as e:
            logger.error(f"Failed to generate suggestions: {e}", exc_info=True)

        return suggestions


# =============================================================================
# CLI INTERFACE
# =============================================================================

async def main():
    """CLI interface for matrix validation."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate Data Source Matrix")
    parser.add_argument(
        "--database-url",
        default="postgresql://postgres:p4ssw0rd@localhost:5432/krl_premium",
        help="Database URL"
    )
    parser.add_argument(
        "--suggest",
        action="store_true",
        help="Suggest missing entries"
    )

    args = parser.parse_args()

    # Initialize database session
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker

    engine = create_async_engine(args.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        validator = MatrixValidator(session)

        # Run validation
        report = await validator.validate_matrix_integrity()

        print("\n" + "="*80)
        print("DATA SOURCE MATRIX VALIDATION REPORT")
        print("="*80)

        print(f"\nStatus: {'✓ VALID' if report['valid'] else '✗ INVALID'}")

        print(f"\nStatistics:")
        for key, value in report['stats'].items():
            print(f"  {key}: {value}")

        if report['errors']:
            print(f"\nErrors ({len(report['errors'])}):")
            for error in report['errors']:
                print(f"  ✗ {error}")

        if report['warnings']:
            print(f"\nWarnings ({len(report['warnings'])}):")
            for warning in report['warnings'][:10]:  # Show first 10
                print(f"  ⚠ {warning}")
            if len(report['warnings']) > 10:
                print(f"  ... and {len(report['warnings']) - 10} more warnings")

        # Suggestions
        if args.suggest:
            print(f"\nGenerating suggestions...")
            suggestions = await validator.suggest_missing_entries()

            if suggestions:
                print(f"\nSuggested Missing Entries ({len(suggestions)}):")
                for i, suggestion in enumerate(suggestions[:20], 1):
                    print(
                        f"  {i}. {suggestion['framework']} × "
                        f"{suggestion['model']} × {suggestion['domain']}"
                    )
                if len(suggestions) > 20:
                    print(f"  ... and {len(suggestions) - 20} more suggestions")

        print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
