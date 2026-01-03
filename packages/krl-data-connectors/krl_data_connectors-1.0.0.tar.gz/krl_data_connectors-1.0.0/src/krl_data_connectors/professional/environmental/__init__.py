# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Professional Environmental Data Connectors

This module provides full access to environmental data sources:
- EPA Air Quality - AQS air monitoring data
- EJScreen - Environmental justice screening
- Water Quality - Water quality monitoring
- Data.gov Environmental - EPA, NOAA datasets (unlimited search, bulk export)

Usage:
    from krl_data_connectors.professional.environmental import (
        EPAAirQualityConnector,
        EJScreenConnector,
        WaterQualityConnector,
        DataGovEnvironmentalFullConnector,
    )
"""

from krl_data_connectors.professional.environmental.epa_air_quality_full import (
    EPAAirQualityConnector,
)
from krl_data_connectors.professional.environmental.epa_ejscreen import (
    EJScreenConnector,
)
from krl_data_connectors.professional.environmental.epa_water_quality import (
    WaterQualityConnector,
)
from krl_data_connectors.professional.environmental.datagov_environmental_full import (
    DataGovEnvironmentalFullConnector,
)

__all__ = [
    "EPAAirQualityConnector",
    "EJScreenConnector",
    "WaterQualityConnector",
    "DataGovEnvironmentalFullConnector",
]
