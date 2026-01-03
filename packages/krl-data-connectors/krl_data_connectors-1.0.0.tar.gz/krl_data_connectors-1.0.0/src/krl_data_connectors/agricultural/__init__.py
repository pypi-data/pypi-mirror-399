# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Agricultural data connectors.

This module provides connectors for agricultural and food-related data sources.

Copyright (c) 2025 Sudiata Giddasira, Inc. d/b/a Quipu Research Labs, LLC d/b/a KR-Labs™
SPDX-License-Identifier: Apache-2.0
"""

__all__: list[str] = []

# Re-export from professional tier
try:
    from krl_data_connectors.professional.agricultural.usda_food_atlas import (
        USDAFoodAtlasConnector,
    )
    __all__.append("USDAFoodAtlasConnector")
except ImportError:
    pass

try:
    from krl_data_connectors.professional.agricultural.usda_nass import (
        USDANASSConnector,
    )
    __all__.append("USDANASSConnector")
except ImportError:
    pass
