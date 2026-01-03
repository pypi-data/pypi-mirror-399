# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Health data connectors for KRL Data Connectors.

Copyright (c) 2024-2025 KR-Labs Foundation
Licensed under the Apache License, Version 2.0
"""

__all__: list[str] = []

# Local connectors
try:
    from .cdc_connector import CDCWonderConnector
    __all__.append("CDCWonderConnector")
except ImportError:
    pass

# Re-export from professional tier
try:
    from krl_data_connectors.professional.health.brfss import BRFSSConnector
    __all__.append("BRFSSConnector")
except ImportError:
    pass

try:
    from krl_data_connectors.professional.health.county_health_rankings import CountyHealthRankingsConnector
    __all__.append("CountyHealthRankingsConnector")
except ImportError:
    pass

try:
    from krl_data_connectors.professional.health.hrsa import HRSAConnector
    __all__.append("HRSAConnector")
except ImportError:
    pass

try:
    from krl_data_connectors.professional.health.nih_reporter import NIHConnector
    __all__.append("NIHConnector")
except ImportError:
    pass

# Re-export from enterprise tier
try:
    from krl_data_connectors.enterprise.health.samhsa import SAMHSAConnector
    __all__.append("SAMHSAConnector")
except ImportError:
    pass
