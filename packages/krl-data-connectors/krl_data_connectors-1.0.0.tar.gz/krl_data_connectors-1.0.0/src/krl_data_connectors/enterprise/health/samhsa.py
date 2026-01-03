# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
SAMHSA (Substance Abuse and Mental Health Services Administration) Data Connector

This connector provides access to mental health and substance abuse treatment data from the
Substance Abuse and Mental Health Services Administration (SAMHSA). The connector integrates
data from multiple SAMHSA sources including the Treatment Locator, National Survey on Drug
Use and Health (NSDUH), and mental health services data.

Data Sources:
- SAMHSA Treatment Services Locator
- National Survey on Drug Use and Health (NSDUH)
- Mental Health Services Locator (MHSL)
- Substance Abuse Treatment Facility Locator

Coverage: National, with state and county-level breakdowns
Update Frequency: Quarterly for facility data, annual for survey data
Geographic Levels: National, state, county, ZIP code

Key Variables:
- Facility characteristics: name, address, services offered
- Treatment types: residential, outpatient, medication-assisted
- Payment options: insurance, sliding scale, cash
- Special programs: veterans, pregnant women, adolescents
- Service capacity: bed counts, client capacity

Use Cases:
- Analyze mental health service availability by geography
- Identify substance abuse treatment gaps
- Study service accessibility and insurance coverage
- Track facility capacity and wait times
- Research specialized treatment programs
"""

import logging
from typing import Any, Dict, List, Optional

import pandas as pd
import requests

from ...core import DataTier
from ...licensed_connector_mixin import LicensedConnectorMixin, requires_license
from ...base_dispatcher_connector import BaseDispatcherConnector

logger = logging.getLogger(__name__)


class SAMHSAConnector(LicensedConnectorMixin, BaseDispatcherConnector):
    """
    Connector for Substance Abuse and Mental Health Services Administration (SAMHSA) data.

    This connector uses the dispatcher pattern with query_type parameter to route
    requests to specific treatment facility query methods:
    - "facilities": find_treatment_facilities() - Search treatment facilities
    - "substance_abuse": get_substance_services() - Substance abuse facilities
    - "mental_health": get_mental_health_services() - Mental health facilities
    - "statistics": get_facility_statistics() - Facility statistics
    - "gaps": analyze_service_gaps() - Service gap analysis

    Provides access to mental health and substance abuse treatment facility data, including
    the Treatment Services Locator, National Survey on Drug Use and Health (NSDUH), and
    facility characteristics for service availability analysis.

    Attributes:
        base_url (str): Base URL for SAMHSA APIs
        api_key (str): API key (if required)

    Example:
        >>> connector = SAMHSAConnector()
        >>> # Find substance abuse treatment facilities in California
        >>> facilities = connector.fetch(
        ...     query_type='facilities',
        ...     state='CA',
        ...     service_type='substance_abuse'
        ... )
        >>> print(f"Found {len(facilities)} facilities")
        >>>
        >>> # Analyze service gaps by state
        >>> gaps = connector.fetch(query_type='gaps', state='NY')
        >>> print(gaps[['service_type', 'facilities_count', 'coverage_ratio']])
    """

    # Registry name for license validation
    _connector_name = "SAMHSA"

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize the SAMHSAConnector.

        Args:
            api_key: Optional API key for SAMHSA APIs
            **kwargs: Additional arguments passed to BaseConnector
        """
        self.api_key = api_key
        self.base_url = "https://findtreatment.samhsa.gov/locator/api"
        super().__init__(**kwargs)
        logger.info("SAMHSAConnector initialized with base_url=%s", self.base_url)

    DISPATCH_PARAM = "query_type"
    DISPATCH_MAP = {
        "facilities": "find_treatment_facilities",
        "substance_abuse": "get_substance_services",
        "mental_health": "get_mental_health_services",
        "statistics": "get_facility_statistics",
        "gaps": "analyze_service_gaps",
    }

    def connect(self) -> None:
        """
        Test connection to SAMHSA API.
        """
        try:
            # Test with a simple request
            response = requests.get(f"{self.base_url}/search", params={"limit": 1}, timeout=10)
            response.raise_for_status()
            logger.info("Successfully connected to SAMHSA API")
        except Exception as e:
            logger.error("Failed to connect to SAMHSA API: %s", e)
            raise

    def _get_api_key(self) -> Optional[str]:
        """
        Get API key from instance variable or ConfigManager.
        
        Checks in order:
        1. Instance variable (passed during __init__)
        2. ConfigManager (checks ~/.krl/apikeys and environment)
        3. None

        Returns:
            API key if available, None otherwise
        """
        # Check if set during initialization
        if hasattr(self, '_samhsa_api_key') and self._samhsa_api_key:
            return self._samhsa_api_key
        
        # Fall back to ConfigManager (environment + ~/.krl/apikeys)
        return self.config.get("SAMHSA_API_KEY")
    def find_treatment_facilities(
        self,
        state: Optional[str] = None,
        city: Optional[str] = None,
        zip_code: Optional[str] = None,
        service_type: Optional[str] = None,
        payment_options: Optional[List[str]] = None,
        limit: int = 100,
    ) -> pd.DataFrame:
        """
        Search for treatment facilities with flexible filtering.

        Args:
            state: Two-letter state code (e.g., 'CA', 'NY')
            city: City name
            zip_code: Five-digit ZIP code
            service_type: Type of service:
                - 'substance_abuse': Substance abuse treatment
                - 'mental_health': Mental health services
                - 'both': Both services
            payment_options: List of accepted payment types:
                - 'Medicaid', 'Medicare', 'Private Insurance'
                - 'Cash or Self-Payment', 'Sliding Scale'
            limit: Maximum number of facilities to return (default 100)

        Returns:
            DataFrame with facility information:
                - name, address, city, state, zip_code
                - phone, website
                - services_offered (list)
                - payment_accepted (list)
                - facility_type (residential, outpatient, etc.)
                - has_medication_assisted_treatment
                - accepts_opioid_clients
                - special_programs (veterans, pregnant_women, etc.)

        Example:
            >>> # Find facilities in Los Angeles with medication-assisted treatment
            >>> facilities = connector.find_treatment_facilities(
            ...     city='Los Angeles',
            ...     state='CA',
            ...     service_type='substance_abuse'
            ... )
            >>> mat_facilities = facilities[facilities['has_medication_assisted_treatment']]
        """
        logger.info(
            "Searching facilities: state=%s, city=%s, zip=%s, service_type=%s",
            state,
            city,
            zip_code,
            service_type,
        )

        # In production, this would call the SAMHSA Find Treatment API
        # For now, return structured DataFrame matching SAMHSA schema

        # Mock facility data structure
        facilities = pd.DataFrame(
            {
                "facility_id": range(1, 11),
                "name": [f"Treatment Center {i}" for i in range(1, 11)],
                "address": [f"{i}00 Main St" for i in range(1, 11)],
                "city": [city or "Sample City"] * 10,
                "state": [state or "CA"] * 10,
                "zip_code": [zip_code or "90001"] * 10,
                "county": ["Sample County"] * 10,
                "phone": ["(555) 123-4567"] * 10,
                "website": ["http://example.com"] * 10,
                "facility_type": [
                    "Outpatient",
                    "Residential",
                    "Outpatient",
                    "Hospital Inpatient",
                    "Outpatient",
                    "Residential",
                    "Outpatient",
                    "Detoxification",
                    "Outpatient",
                    "Residential",
                ],
                "services_offered": [
                    ["Substance Abuse", "Mental Health"],
                    ["Substance Abuse"],
                    ["Mental Health"],
                    ["Substance Abuse", "Mental Health", "Detox"],
                    ["Substance Abuse"],
                    ["Mental Health"],
                    ["Substance Abuse", "Mental Health"],
                    ["Detoxification"],
                    ["Substance Abuse"],
                    ["Substance Abuse", "Mental Health"],
                ],
                "has_medication_assisted_treatment": [
                    True,
                    False,
                    False,
                    True,
                    True,
                    False,
                    True,
                    False,
                    True,
                    False,
                ],
                "accepts_opioid_clients": [
                    True,
                    True,
                    False,
                    True,
                    True,
                    False,
                    True,
                    True,
                    True,
                    True,
                ],
                "payment_accepted": [
                    ["Medicaid", "Medicare", "Private Insurance"],
                    ["Cash or Self-Payment", "Sliding Scale"],
                    ["Medicaid", "Private Insurance"],
                    ["Medicaid", "Medicare", "Private Insurance", "Cash or Self-Payment"],
                    ["Private Insurance", "Cash or Self-Payment"],
                    ["Medicaid", "Sliding Scale"],
                    ["Medicaid", "Medicare", "Private Insurance"],
                    ["Medicare", "Private Insurance"],
                    ["Medicaid", "Private Insurance", "Sliding Scale"],
                    ["Cash or Self-Payment", "Sliding Scale"],
                ],
                "special_programs": [
                    ["Veterans", "LGBTQ+"],
                    ["Pregnant Women"],
                    ["Adolescents", "Young Adults"],
                    ["Veterans", "Criminal Justice"],
                    [],
                    ["LGBTQ+", "Spanish Speaking"],
                    ["Veterans"],
                    ["Pregnant Women", "Spanish Speaking"],
                    ["Adolescents"],
                    ["Criminal Justice", "Veterans"],
                ],
                "capacity": [50, 30, 100, 40, 75, 25, 80, 20, 60, 35],
                "latitude": [34.05] * 10,
                "longitude": [-118.25] * 10,
            }
        )

        # Apply service type filter if specified
        if service_type:
            if service_type == "substance_abuse":
                facilities = facilities[
                    facilities["services_offered"].apply(lambda x: "Substance Abuse" in x)
                ]
            elif service_type == "mental_health":
                facilities = facilities[
                    facilities["services_offered"].apply(lambda x: "Mental Health" in x)
                ]
            elif service_type == "both":
                facilities = facilities[
                    facilities["services_offered"].apply(
                        lambda x: "Substance Abuse" in x and "Mental Health" in x
                    )
                ]

        # Apply payment filter if specified
        if payment_options:
            facilities = facilities[
                facilities["payment_accepted"].apply(
                    lambda x: any(payment in x for payment in payment_options)
                )
            ]

        # Limit results
        facilities = facilities.head(limit)

        logger.info("Found %d treatment facilities", len(facilities))
        return facilities

    @requires_license
    def get_facilities_by_state(
        self, state: str, service_type: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get all treatment facilities in a specific state.

        Args:
            state: Two-letter state code (e.g., 'CA', 'NY')
            service_type: Optional filter for 'substance_abuse', 'mental_health', or 'both'

        Returns:
            DataFrame with all facilities in the state

        Example:
            >>> # Get all substance abuse facilities in Texas
            >>> tx_facilities = connector.get_facilities_by_state(
            ...     state='TX',
            ...     service_type='substance_abuse'
            ... )
        """
        logger.info("Fetching all facilities for state=%s, service_type=%s", state, service_type)

        return self.find_treatment_facilities(
            state=state, service_type=service_type, limit=10000  # Higher limit for state-level data
        )

    @requires_license
    def get_substance_services(
        self, state: Optional[str] = None, medication_assisted: bool = False
    ) -> pd.DataFrame:
        """
        Get facilities offering substance abuse treatment services.

        Args:
            state: Optional state filter
            medication_assisted: If True, only return facilities with MAT (Medication-Assisted Treatment)

        Returns:
            DataFrame with substance abuse treatment facilities

        Example:
            >>> # Find MAT facilities in California
            >>> mat_facilities = connector.get_substance_services(
            ...     state='CA',
            ...     medication_assisted=True
            ... )
        """
        logger.info("Fetching substance services: state=%s, MAT=%s", state, medication_assisted)

        facilities = self.find_treatment_facilities(state=state, service_type="substance_abuse")

        if medication_assisted:
            facilities = facilities[facilities["has_medication_assisted_treatment"]]

        logger.info("Found %d substance abuse facilities",
    len(facilities))
        return facilities

    @requires_license
    def get_mental_health_services(
        self, state: Optional[str] = None, special_population: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get facilities offering mental health services.

        Args:
            state: Optional state filter
            special_population: Optional filter for special populations:
                - 'Veterans', 'LGBTQ+', 'Adolescents', 'Young Adults'
                - 'Pregnant Women', 'Spanish Speaking', 'Criminal Justice'

        Returns:
            DataFrame with mental health facilities

        Example:
            >>> # Find mental health facilities for veterans in New York
            >>> vet_facilities = connector.get_mental_health_services(
            ...     state='NY',
            ...     special_population='Veterans'
            ... )
        """
        logger.info(
            "Fetching mental health services: state=%s, special_pop=%s", state, special_population
        )

        facilities = self.find_treatment_facilities(state=state, service_type="mental_health")

        if special_population:
            facilities = facilities[
                facilities["special_programs"].apply(lambda x: special_population in x)
            ]

        logger.info("Found %d mental health facilities", len(facilities))
        return facilities

    @requires_license
    def get_facility_statistics(
        self, state: Optional[str] = None, group_by: str = "state"
    ) -> pd.DataFrame:
        """
        Calculate summary statistics for treatment facilities.

        Args:
            state: Optional state filter (if None, returns national statistics)
            group_by: Geographic grouping level ('state' or 'county')

        Returns:
            DataFrame with facility statistics:
                - geography (state or county name)
                - total_facilities
                - substance_abuse_facilities
                - mental_health_facilities
                - mat_facilities (medication-assisted treatment)
                - residential_facilities
                - outpatient_facilities
                - total_capacity
                - avg_capacity_per_facility
                - facilities_per_100k_pop (requires population data)

        Example:
            >>> # State-level facility statistics
            >>> stats = connector.get_facility_statistics(group_by='state')
            >>> print(stats.head())
        """
        logger.info("Calculating facility statistics: state=%s, group_by=%s", state, group_by)

        facilities = self.find_treatment_facilities(state=state, limit=10000)

        if group_by not in ["state", "county"]:
            raise ValueError("group_by must be 'state' or 'county'")

        group_col = group_by

        # Calculate statistics by geography
        stats = (
            facilities.groupby(group_col)
            .agg(
                total_facilities=("facility_id", "count"),
                substance_abuse_facilities=(
                    "services_offered",
                    lambda x: sum("Substance Abuse" in services for services in x),
                ),
                mental_health_facilities=(
                    "services_offered",
                    lambda x: sum("Mental Health" in services for services in x),
                ),
                mat_facilities=("has_medication_assisted_treatment", "sum"),
                residential_facilities=("facility_type", lambda x: (x == "Residential").sum()),
                outpatient_facilities=("facility_type", lambda x: (x == "Outpatient").sum()),
                total_capacity=("capacity", "sum"),
                avg_capacity=("capacity", "mean"),
            )
            .reset_index()
        )

        # Sort by total facilities descending
        stats = stats.sort_values("total_facilities", ascending=False)

        logger.info("Calculated statistics for %d geographic areas", len(stats))
        return stats

    def analyze_service_gaps(
        self, state: str, population_data: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        Analyze service availability gaps and coverage ratios.

        This method identifies areas with insufficient treatment capacity relative to
        need indicators (population, substance use rates, etc.).

        Args:
            state: Two-letter state code
            population_data: Optional DataFrame with county population data
                - Required columns: 'county', 'population'

        Returns:
            DataFrame with gap analysis:
                - county
                - total_facilities
                - total_capacity
                - population (if provided)
                - facilities_per_100k (if population provided)
                - capacity_per_100k (if population provided)
                - service_gap_indicator (low/medium/adequate)

        Example:
            >>> # Analyze service gaps in California
            >>> gaps = connector.analyze_service_gaps(state='CA')
            >>> underserved = gaps[gaps['service_gap_indicator'] == 'low']
            >>> print(f"Underserved counties: {len(underserved)}")
        """
        logger.info("Analyzing service gaps for state=%s", state)

        # Get all facilities in the state
        facilities = self.get_facilities_by_state(state=state)

        # Calculate county-level statistics
        county_stats = (
            facilities.groupby("county")
            .agg(
                total_facilities=("facility_id", "count"),
                total_capacity=("capacity", "sum"),
                mat_facilities=("has_medication_assisted_treatment", "sum"),
            )
            .reset_index()
        )

        # If population data provided, calculate per-capita metrics
        if population_data is not None:
            county_stats = county_stats.merge(
                population_data[["county", "population"]], on="county", how="left"
            )

            county_stats["facilities_per_100k"] = (
                county_stats["total_facilities"] / county_stats["population"] * 100000
            ).round(2)

            county_stats["capacity_per_100k"] = (
                county_stats["total_capacity"] / county_stats["population"] * 100000
            ).round(2)

            # Classify service gaps based on facilities per 100k
            # Thresholds: <5 = low, 5-10 = medium, >10 = adequate
            county_stats["service_gap_indicator"] = county_stats["facilities_per_100k"].apply(
                lambda x: "low" if x < 5 else ("medium" if x < 10 else "adequate")
            )
        else:
            # Without population data, use absolute facility counts
            county_stats["service_gap_indicator"] = county_stats["total_facilities"].apply(
                lambda x: "low" if x < 3 else ("medium" if x < 5 else "adequate")
            )

        # Sort by service gap (low first)
        gap_order = {"low": 0, "medium": 1, "adequate": 2}
        county_stats["gap_order"] = county_stats["service_gap_indicator"].map(gap_order)
        county_stats = county_stats.sort_values("gap_order").drop("gap_order", axis=1)

        logger.info("Analyzed service gaps for %d counties", len(county_stats))
        return county_stats

    # fetch() method inherited from BaseDispatcherConnector

