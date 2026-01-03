# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""Housing data connectors for KRL Data Connectors."""

__all__: list[str] = []

# Re-export from professional tier
try:
    from krl_data_connectors.professional.housing.zillow_research import ZillowConnector
    __all__.append("ZillowConnector")
except ImportError:
    pass

try:
    from krl_data_connectors.professional.housing.hud_fair_market_rents import HUDFMRConnector
    __all__.append("HUDFMRConnector")
except ImportError:
    pass

try:
    from krl_data_connectors.professional.housing.eviction_lab import EvictionLabConnector
    __all__.append("EvictionLabConnector")
except ImportError:
    pass
