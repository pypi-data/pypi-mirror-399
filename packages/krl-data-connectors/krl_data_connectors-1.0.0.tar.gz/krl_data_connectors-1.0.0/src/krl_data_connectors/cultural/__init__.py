# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Cultural and arts data connectors.

This module provides connectors for accessing cultural participation,
arts funding, and creative economy data.

Available Connectors:
- NEACulturalDataConnector: National Endowment for the Arts data
"""

__all__: list[str] = []

# Re-export from professional tier
try:
    from krl_data_connectors.professional.cultural.nea import NEACulturalDataConnector
    __all__.append("NEACulturalDataConnector")
except ImportError:
    pass
