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

from krl_data_connectors.matrix.source_matrix import (
    ConnectorRecommendation,
    DataSourceMatrix,
    QualityDimension,
    QualityScore,
)

__all__ = [
    "DataSourceMatrix",
    "ConnectorRecommendation",
    "QualityScore",
    "QualityDimension",
]
