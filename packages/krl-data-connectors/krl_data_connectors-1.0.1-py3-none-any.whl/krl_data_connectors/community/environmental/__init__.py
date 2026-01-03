# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Community Tier Environmental Connectors

This module provides free access to environmental data sources:
- NOAA Climate Data Online (CDO) - weather and climate observations
- Data.gov Environmental - EPA, NOAA datasets from Data.gov catalog

Usage:
    from krl_data_connectors.community.environmental import (
        NOAAClimateConnector,
        DataGovEnvironmentalConnector,
    )
"""

from krl_data_connectors.community.environmental.noaa_climate_current import (
    NOAAClimateConnector,
)
from krl_data_connectors.community.environmental.datagov_environmental import (
    DataGovEnvironmentalConnector,
)

__all__ = [
    "NOAAClimateConnector",
    "DataGovEnvironmentalConnector",
]
