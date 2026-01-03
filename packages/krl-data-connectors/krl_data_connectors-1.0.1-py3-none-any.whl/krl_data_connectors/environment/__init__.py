"""
Environment and environmental justice data connectors.

© 2025 KR-Labs. All rights reserved.
KR-Labs™ is a trademark of Quipu Research Labs, LLC, a subsidiary of Sudiata Giddasira, Inc.

SPDX-License-Identifier: Apache-2.0
"""

from .air_quality_connector import EPAAirQualityConnector
from .ejscreen_connector import EJScreenConnector
from .noaa_climate_connector import NOAAClimateConnector
from .superfund_connector import EPASuperfundConnector
from .water_quality_connector import EPAWaterQualityConnector

# Backwards compatible aliases
WaterQualityConnector = EPAWaterQualityConnector
SuperfundConnector = EPASuperfundConnector
AirQualityConnector = EPAAirQualityConnector

__all__ = [
    "EJScreenConnector",
    "EPAAirQualityConnector",
    "EPASuperfundConnector",
    "EPAWaterQualityConnector",
    "NOAAClimateConnector",
    # Legacy aliases
    "WaterQualityConnector",
    "SuperfundConnector",
    "AirQualityConnector",
]
