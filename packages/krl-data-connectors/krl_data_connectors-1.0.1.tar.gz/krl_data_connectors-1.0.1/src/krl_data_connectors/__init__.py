# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

# Copyright (c) 2025 KR-Labs Foundation. All rights reserved.
# Licensed under Apache License 2.0 (see LICENSE file for details)

"""
KRL Data Connectors - Enterprise-grade data connectors for 67 data sources across 3 tiers.

This package provides unified, type-safe interfaces for accessing data from government,
research, and public data providers. Built with 2,098+ automated tests maintaining >78%
coverage, ensuring production reliability.

**3-Tier Architecture:**
- **Community (12 connectors)**: FREE tier for learning and POCs
- **Professional (47 connectors)**: Paid tier ($149-599/mo) for production analytics
- **Enterprise (8 connectors)**: Premium tier ($999-5,000/mo) for regulated data

**Import Structure:**
```python
# Community tier (free)
from krl_data_connectors.community import FREDBasicConnector, BLSBasicConnector

# Professional tier (requires license)
from krl_data_connectors.professional import FREDFullConnector, SECConnector

# Enterprise tier (requires license + device binding)
from krl_data_connectors.enterprise import FBIUCRConnector, SAMHSAConnector
```

For full connector listings, see:
- `krl_data_connectors.community.__all__`
- `krl_data_connectors.professional.__all__`  
- `krl_data_connectors.enterprise.__all__`
"""

from .__version__ import __author__, __license__, __version__
from .base_connector import BaseConnector
from .base_dispatcher_connector import BaseDispatcherConnector
from .core import ConnectorLicenseValidator, ConnectorRegistry, DataTier
from .licensed_connector_mixin import LicensedConnectorMixin, requires_license, skip_license_check
from .utils.config import find_config_file, load_api_key_from_config


def get_available_connectors(tier: DataTier = DataTier.COMMUNITY) -> dict:
    """
    Get available connectors organized by tier.

    This is a convenience function for querying the connector registry.
    Returns a dict with connector information for the specified tier and below.

    Args:
        tier: Maximum tier level to include (default: COMMUNITY for free connectors)

    Returns:
        Dict with keys 'connectors' (set of names), 'tier' (current), 'count' (int)

    Example:
        >>> info = get_available_connectors()
        >>> print(info['count'])
        15
        >>> print(info['tier'])
        'community'

        >>> pro = get_available_connectors(DataTier.PROFESSIONAL)
        >>> print(pro['count'])
        59
    """
    connectors = ConnectorRegistry.get_connectors_for_tier(tier)
    return {
        "connectors": sorted(connectors),
        "tier": tier.value,
        "count": len(connectors),
        "tier_counts": ConnectorRegistry.get_tier_counts(),
    }


# Expose tier-specific connectors through submodules
# Users should import from: krl_data_connectors.{tier}.{connector}
# Example: from krl_data_connectors.community import FREDBasicConnector

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__license__",
    # Base Classes
    "BaseConnector",
    "BaseDispatcherConnector",
    # License Management
    "LicensedConnectorMixin",
    "requires_license",
    "skip_license_check",
    # Core Registry & Validation
    "ConnectorRegistry",
    "DataTier",
    "ConnectorLicenseValidator",
    # Utilities
    "find_config_file",
    "load_api_key_from_config",
    # Convenience Functions
    "get_available_connectors",
]
