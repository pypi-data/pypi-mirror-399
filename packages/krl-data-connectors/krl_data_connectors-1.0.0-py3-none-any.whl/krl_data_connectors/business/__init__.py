# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ and KRL Data Connectors™ are trademarks of Deloatch, Williams, Faison, & Parker, LLLP.
# Deloatch, Williams, Faison, & Parker, LLLP
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""Business data connectors module."""

__all__: list[str] = []

# Re-export from professional tier
try:
    from krl_data_connectors.professional.business.local_business import LocalBusinessConnector
    __all__.append("LocalBusinessConnector")
except ImportError:
    pass
