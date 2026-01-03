# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Connector Registry - Central mapping of connectors to required tiers.

This module defines the tier allocation for all 68 data connectors across
Community (free), Professional, and Enterprise tiers.
"""

from enum import Enum
from typing import Dict, Set


class DataTier(Enum):
    """
    Enumeration of available data access tiers.

    COMMUNITY: Free tier with 12 basic connectors
    PROFESSIONAL: Paid tier ($149-599/mo) with 60 total connectors (12 + 48)
    ENTERPRISE: Premium tier ($999-5,000/mo) with all 68 connectors (12 + 48 + 8)
    """

    COMMUNITY = "community"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class ConnectorRegistry:
    """
    Central registry mapping connectors to required access tiers.

    This registry enforces tier-based access control for all data connectors,
    ensuring that users can only access connectors appropriate for their
    subscription level.

    Attributes:
        TIER_MAP: Dictionary mapping connector names to minimum required tiers

    Example:
        >>> registry = ConnectorRegistry()
        >>> tier = registry.get_required_tier("FRED_Full")
        >>> print(tier)
        DataTier.PROFESSIONAL

        >>> connectors = registry.get_connectors_for_tier(DataTier.COMMUNITY)
        >>> print(len(connectors))
        15
    """

    # Tier allocation map: connector_name -> required minimum tier
    TIER_MAP: Dict[str, DataTier] = {
        # ====================================================================
        # COMMUNITY TIER (12 connectors implemented, 3 planned) - FREE
        # ====================================================================
        # Economic Data (5 connectors)
        "FRED_Basic": DataTier.COMMUNITY,
        "BLS_Basic": DataTier.COMMUNITY,
        "Census_ACS_Public": DataTier.COMMUNITY,
        "BEA_National": DataTier.COMMUNITY,
        "Treasury_Public_Debt": DataTier.COMMUNITY,
        # Demographic & Social (3 connectors)
        "Census_CBP_Summary": DataTier.COMMUNITY,
        "NCES_School_Directory": DataTier.COMMUNITY,
        "SSA_Actuarial": DataTier.COMMUNITY,
        # Environmental (1 connector, 2 planned)
        # TODO: "EPA_Air_Quality_Basic": DataTier.COMMUNITY,
        "NOAA_Climate_Current": DataTier.COMMUNITY,
        # Geographic (1 connector, 1 planned)
        "USGS_Earthquakes": DataTier.COMMUNITY,
        # TODO: "Census_TIGER_Basic": DataTier.COMMUNITY,
        # Civic (1 connector)
        "DataGov_Catalog": DataTier.COMMUNITY,
        # Health (2 connectors, 1 planned)
        # TODO: "CDC_WONDER_Mortality": DataTier.COMMUNITY,
        "FDA_Drug_Approvals": DataTier.COMMUNITY,
        # Specialty (1 connector)
        "OECD_Indicators": DataTier.COMMUNITY,
        # ====================================================================
        # PROFESSIONAL TIER (48 additional = 60 total) - $149-599/mo
        # ====================================================================
        # Economic Data (4 connectors)
        "FRED_Full": DataTier.PROFESSIONAL,
        "BLS_Enhanced": DataTier.PROFESSIONAL,
        "World_Bank_Full": DataTier.PROFESSIONAL,
        "Census_BDS": DataTier.PROFESSIONAL,
        # Demographic (1 connector)
        "Census_ACS_Detailed": DataTier.PROFESSIONAL,
        # Labor (2 connectors)
        "Census_LEHD_Full": DataTier.PROFESSIONAL,
        "OSHA": DataTier.PROFESSIONAL,
        # Health (5 connectors)
        "HRSA": DataTier.PROFESSIONAL,
        "County_Health_Rankings": DataTier.PROFESSIONAL,
        "NIH_Reporter": DataTier.PROFESSIONAL,
        "BRFSS": DataTier.PROFESSIONAL,
        "Places": DataTier.PROFESSIONAL,  # CDC PLACES - county/tract health estimates
        # Environmental (3 connectors)
        "EPA_EJScreen": DataTier.PROFESSIONAL,
        "EPA_Air_Quality_Full": DataTier.PROFESSIONAL,
        "EPA_Water_Quality": DataTier.PROFESSIONAL,
        # Education (3 connectors)
        "NCES_CCD": DataTier.PROFESSIONAL,
        "College_Scorecard": DataTier.PROFESSIONAL,
        "IPEDS": DataTier.PROFESSIONAL,
        # Housing (3 connectors)
        "HUD_Fair_Market_Rents": DataTier.PROFESSIONAL,
        "Zillow_Research": DataTier.PROFESSIONAL,
        "Eviction_Lab": DataTier.PROFESSIONAL,
        # Energy (1 connector)
        "EIA_Full": DataTier.PROFESSIONAL,
        # Agricultural (2 connectors)
        "USDA_NASS": DataTier.PROFESSIONAL,
        "USDA_Food_Atlas": DataTier.PROFESSIONAL,
        # Science (2 connectors)
        "NSF": DataTier.PROFESSIONAL,
        "USPTO": DataTier.PROFESSIONAL,
        # Financial (4 connectors)
        "SEC_Filings": DataTier.PROFESSIONAL,
        "FDIC_Bank_Data": DataTier.PROFESSIONAL,
        "HMDA": DataTier.PROFESSIONAL,
        "IRS990": DataTier.PROFESSIONAL,
        # Transportation (2 connectors)
        "FAA": DataTier.PROFESSIONAL,
        "NHTS": DataTier.PROFESSIONAL,
        # Political (3 connectors)
        "FEC": DataTier.PROFESSIONAL,
        "LegiScan": DataTier.PROFESSIONAL,
        "MIT_Election_Lab": DataTier.PROFESSIONAL,
        # Social (1 connector)
        "Social_Media_Harvester": DataTier.PROFESSIONAL,
        # Cultural (2 connectors)
        "NEA": DataTier.PROFESSIONAL,
        "Cultural_Sentiment": DataTier.PROFESSIONAL,
        # Business (1 connector)
        "Local_Business": DataTier.PROFESSIONAL,
        # Civic (2 connectors)
        "Google_Civic_Info": DataTier.PROFESSIONAL,
        "DataGov_Full": DataTier.PROFESSIONAL,
        # Events (1 connector)
        "Events_Venues": DataTier.PROFESSIONAL,
        # Recreation (1 connector)
        "Parks_Recreation": DataTier.PROFESSIONAL,
        # Web (1 connector)
        "Web_Scraper": DataTier.PROFESSIONAL,
        # Transit (1 connector)
        "Transit": DataTier.PROFESSIONAL,
        # Technology (1 connector)
        "FCC_Broadband": DataTier.PROFESSIONAL,
        # Media (1 connector)
        "GDELT": DataTier.PROFESSIONAL,
        # Mobility (1 connector)
        "Opportunity_Insights": DataTier.PROFESSIONAL,
        # Local Government (1 connector)
        "Local_Gov_Finance": DataTier.PROFESSIONAL,
        # ====================================================================
        # ENTERPRISE TIER (8 additional = 68 total) - $999-5,000/mo
        # ====================================================================
        # Premium Crime & Justice (3 connectors)
        "FBI_UCR_Detailed": DataTier.ENTERPRISE,
        "Bureau_Of_Justice": DataTier.ENTERPRISE,
        "Victims_Of_Crime": DataTier.ENTERPRISE,
        # Premium Health Data (2 connectors)
        "SAMHSA": DataTier.ENTERPRISE,
        "CDC_Full_API": DataTier.ENTERPRISE,
        # Premium Environmental (1 connector)
        "EPA_Superfund_Full": DataTier.ENTERPRISE,
        # Premium Social Services (2 connectors)
        "Veterans_Affairs": DataTier.ENTERPRISE,
        "ACF_Full": DataTier.ENTERPRISE,
    }

    @classmethod
    def get_required_tier(cls, connector_name: str) -> DataTier:
        """
        Get the minimum tier required to access a connector.

        Args:
            connector_name: Name of the connector (e.g., "FRED_Full")

        Returns:
            DataTier enum value indicating minimum required tier

        Raises:
            KeyError: If connector_name is not found in registry

        Example:
            >>> ConnectorRegistry.get_required_tier("FRED_Basic")
            DataTier.COMMUNITY

            >>> ConnectorRegistry.get_required_tier("CMS_Medicare")
            DataTier.ENTERPRISE
        """
        if connector_name not in cls.TIER_MAP:
            raise KeyError(
                f"Unknown connector: {connector_name}. "
                f"Available connectors: {', '.join(sorted(cls.TIER_MAP.keys()))}"
            )
        return cls.TIER_MAP[connector_name]

    @classmethod
    def get_connectors_for_tier(cls, tier: DataTier) -> Set[str]:
        """
        Get all connectors available at a given tier (includes lower tiers).

        Tier hierarchy:
        - COMMUNITY: 12 connectors
        - PROFESSIONAL: 59 connectors (Community + 47 additional)
        - ENTERPRISE: 67 connectors (Professional + 8 additional)

        Args:
            tier: DataTier enum value

        Returns:
            Set of connector names available at this tier

        Example:
            >>> community = ConnectorRegistry.get_connectors_for_tier(DataTier.COMMUNITY)
            >>> len(community)
            12

            >>> professional = ConnectorRegistry.get_connectors_for_tier(DataTier.PROFESSIONAL)
            >>> len(professional)
            59

            >>> enterprise = ConnectorRegistry.get_connectors_for_tier(DataTier.ENTERPRISE)
            >>> len(enterprise)
            67
        """
        tier_hierarchy = {
            DataTier.COMMUNITY: [DataTier.COMMUNITY],
            DataTier.PROFESSIONAL: [DataTier.COMMUNITY, DataTier.PROFESSIONAL],
            DataTier.ENTERPRISE: [DataTier.COMMUNITY, DataTier.PROFESSIONAL, DataTier.ENTERPRISE],
        }

        allowed_tiers = tier_hierarchy[tier]
        return {
            connector_name
            for connector_name, required_tier in cls.TIER_MAP.items()
            if required_tier in allowed_tiers
        }

    @classmethod
    def get_tier_counts(cls) -> Dict[DataTier, int]:
        """
        Get count of connectors in each tier (exclusive, not cumulative).

        Returns:
            Dictionary mapping tiers to exclusive connector counts

        Example:
            >>> counts = ConnectorRegistry.get_tier_counts()
            >>> print(counts)
            {
                DataTier.COMMUNITY: 12,
                DataTier.PROFESSIONAL: 47,
                DataTier.ENTERPRISE: 8
            }
        """
        from collections import Counter

        tier_counts = Counter(cls.TIER_MAP.values())
        return {tier: tier_counts[tier] for tier in DataTier}

    @classmethod
    def validate_registry_integrity(cls) -> Dict[str, any]:
        """
        Validate the integrity of the connector registry.

        Checks:
        1. Total connector count matches expected (68)
        2. Tier distribution matches expected (12/48/8)
        3. No duplicate connector names
        4. All connector names follow naming convention

        Returns:
            Dictionary with validation results and any errors found

        Example:
            >>> result = ConnectorRegistry.validate_registry_integrity()
            >>> print(result['valid'])
            True
            >>> print(result['total_connectors'])
            68
        """
        errors = []
        warnings = []

        # Check total count
        total_count = len(cls.TIER_MAP)
        expected_total = 70  # Updated: DataGov_Catalog and DataGov_Full added
        if total_count != expected_total:
            errors.append(
                f"Total connector count mismatch: expected {expected_total}, got {total_count}"
            )

        # Check tier distribution
        tier_counts = cls.get_tier_counts()
        expected_counts = {
            DataTier.COMMUNITY: 13,  # Updated: DataGov_Catalog added
            DataTier.PROFESSIONAL: 49,  # Updated: DataGov_Full added
            DataTier.ENTERPRISE: 8,
        }

        for tier, expected in expected_counts.items():
            actual = tier_counts.get(tier, 0)
            if actual != expected:
                errors.append(
                    f"Tier {tier.value} count mismatch: expected {expected}, got {actual}"
                )

        # Check for naming convention compliance
        for connector_name in cls.TIER_MAP.keys():
            if not connector_name.replace("_", "").replace("Connector", "").isalnum():
                warnings.append(
                    f"Connector name '{connector_name}' may not follow naming convention"
                )

        # Check for duplicates (should be impossible with dict, but good to verify)
        connector_names = list(cls.TIER_MAP.keys())
        if len(connector_names) != len(set(connector_names)):
            errors.append("Duplicate connector names found in registry")

        return {
            "valid": len(errors) == 0,
            "total_connectors": total_count,
            "tier_counts": tier_counts,
            "errors": errors,
            "warnings": warnings,
        }


# Run validation on module import (catches configuration errors early)
_validation_result = ConnectorRegistry.validate_registry_integrity()
if not _validation_result["valid"]:
    import warnings

    warnings.warn(
        f"Connector registry validation failed: {_validation_result['errors']}", UserWarning
    )
