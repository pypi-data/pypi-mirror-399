# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
CDC PLACES (Population Level Analysis and Community Estimates) Connector

This module provides access to CDC PLACES data for local-area health estimates.

Data Source: CDC PLACES - Local Data for Better Health
Coverage: 2019-2024, all counties (~3,143), census tracts (~84,000), and places
Update Frequency: Annual
Geographic Scope: County, census tract, ZIP code, and place levels
Model: Small-area estimation using BRFSS + ACS + Census data

Key Research Applications:
- County-level chronic disease prevalence (15,715 county-years for 2019-2023)
- Tract-level health equity analysis (420,000 tract-years for 2019-2023)
- Local health intervention targeting
- Geographic health disparity identification
- Small-area health surveillance
- Community health needs assessment

Available Measures (40 total):
- Health Outcomes (12): Diabetes, heart disease, stroke, asthma, COPD, kidney disease, etc.
- Prevention (9): Checkups, cancer screening, dental visits, vaccines
- Risk Behaviors (4): Smoking, obesity, physical inactivity, binge drinking
- Health Status (3): General health, physical health, mental health
- Disabilities (7): Cognitive, hearing, vision, mobility, self-care, independent living
- Social Needs (5): Food insecurity, housing cost burden, social isolation

Author: KR-Labs
Date: November 13, 2025
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Any, Dict, List, Literal, Optional, Set

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from krl_data_connectors.base_dispatcher_connector import BaseDispatcherConnector

from ...core import DataTier
from ...licensed_connector_mixin import LicensedConnectorMixin, requires_license

logger = logging.getLogger(__name__)


@dataclass
class DiseaseConfig:
    """
    Configuration for a specific chronic disease's data requirements and causal structure.

    This enables disease-agnostic modeling: swap the disease_type parameter and the
    connector/model pipeline automatically adapts target variables, covariates, and
    causal DAG without code changes.

    Attributes:
        disease_id: Unique identifier (e.g., 'diabetes', 'hypertension')
        display_name: Human-readable name (e.g., 'Type 2 Diabetes')
        places_measure_id: CDC PLACES measure ID (e.g., 'DIABETES')
        target_variable: Column name for model target (e.g., 'diabetes_prevalence')
        key_predictors: Most important covariates (ranked by causal strength)
        causal_dag: Disease-specific DAG edges as (source, target, weight) tuples
        available_years: Years where data is reliable (e.g., 2019-2023)
        geographic_levels: Supported geographies ('county', 'tract', etc.)
        proxy_measures: Alternate measures if primary unavailable
        prevalence_range: Expected prevalence bounds for validation (min, max %)
        temporal_lag: Typical years between exposure and outcome
        metadata: Additional disease-specific notes
    """

    disease_id: str
    display_name: str
    places_measure_id: str
    target_variable: str
    key_predictors: List[str]
    causal_dag: List[tuple] = field(default_factory=list)  # (source, target, weight)
    available_years: tuple = (2019, 2023)
    geographic_levels: Set[str] = field(default_factory=lambda: {"county", "tract"})
    proxy_measures: Dict[str, str] = field(default_factory=dict)
    prevalence_range: tuple = (0.0, 100.0)
    temporal_lag: int = 5
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate_features(self, available_features: Set[str]) -> Dict[str, Any]:
        """
        Check which required predictors are available in dataset.

        Args:
            available_features: Set of column names in dataset

        Returns:
            Dict with 'available', 'missing', 'proxies_available'
        """
        required = set(self.key_predictors)
        available = required & available_features
        missing = required - available_features

        # Check for proxies
        proxies = {}
        for missing_var in missing:
            if missing_var in self.proxy_measures:
                proxy = self.proxy_measures[missing_var]
                if proxy in available_features:
                    proxies[missing_var] = proxy

        return {
            "available": list(available),
            "missing": list(missing - set(proxies.keys())),
            "proxies_available": proxies,
            "coverage": len(available) / len(required) if required else 1.0,
        }


class DiseaseRegistry:
    """
    Central registry of chronic disease configurations for modular modeling.

    This enables the platform to handle any chronic disease without code changes:
    - Policy analyst selects disease from dropdown
    - Registry provides disease-specific config
    - Connector pulls appropriate PLACES data
    - Model pipeline adapts DAG and features automatically
    - Forecasts generated with disease-specific causal weights

    Usage:
        >>> registry = DiseaseRegistry()
        >>> config = registry.get_config('diabetes')
        >>> print(config.key_predictors)
        ['obesity', 'smoking', 'physical_inactivity', 'poverty_rate', 'education_level']

        >>> # Analyst switches to hypertension - no code changes needed
        >>> config = registry.get_config('hypertension')
        >>> print(config.key_predictors)
        ['obesity', 'smoking', 'sodium_intake', 'stress', 'poverty_rate']
    """

    def __init__(self):
        """Initialize disease registry with pre-configured chronic diseases."""
        self._registry: Dict[str, DiseaseConfig] = {}
        self._load_default_diseases()

    def _load_default_diseases(self):
        """Load standard chronic disease configurations."""

        # Type 2 Diabetes
        self.register(
            DiseaseConfig(
                disease_id="diabetes",
                display_name="Type 2 Diabetes",
                places_measure_id="DIABETES",
                target_variable="diabetes_prevalence",
                key_predictors=[
                    "obesity",  # Strongest predictor (BMI >30)
                    "physical_inactivity",  # Sedentary lifestyle
                    "smoking",  # Insulin resistance
                    "poverty_rate",  # SES barriers to care
                    "education_level",  # Health literacy
                    "uninsured_rate",  # Access to prevention
                    "mental_health",  # Depression comorbidity
                ],
                causal_dag=[
                    # Social determinants → Behaviors
                    ("poverty_rate", "obesity", 0.35),
                    ("poverty_rate", "physical_inactivity", 0.28),
                    ("education_level", "obesity", -0.32),
                    ("education_level", "smoking", -0.25),
                    ("uninsured_rate", "mental_health", 0.22),
                    # Behaviors → Intermediate outcomes
                    ("obesity", "diabetes_prevalence", 0.45),  # Strongest path
                    ("physical_inactivity", "diabetes_prevalence", 0.28),
                    ("smoking", "diabetes_prevalence", 0.18),
                    ("mental_health", "diabetes_prevalence", 0.15),
                    # Direct SES effects
                    ("poverty_rate", "diabetes_prevalence", 0.20),
                    ("uninsured_rate", "diabetes_prevalence", 0.12),
                ],
                prevalence_range=(5.0, 18.0),  # Typical county range 5-18%
                temporal_lag=10,  # Diabetes develops over ~10 years
                metadata={
                    "primary_mechanism": "insulin_resistance",
                    "modifiable_factors": ["obesity", "physical_inactivity", "diet"],
                    "screening_age": 35,
                    "intervention_roi": 3.2,  # $3.20 saved per $1 spent on prevention
                },
            )
        )

        # Hypertension (High Blood Pressure)
        self.register(
            DiseaseConfig(
                disease_id="hypertension",
                display_name="Hypertension",
                places_measure_id="BPHIGH",
                target_variable="hypertension_prevalence",
                key_predictors=[
                    "obesity",  # Primary risk factor
                    "smoking",  # Vascular damage
                    "physical_inactivity",  # Cardiovascular fitness
                    "sodium_intake",  # Dietary sodium (proxy: diet quality)
                    "stress",  # Chronic stress (proxy: mental_health)
                    "poverty_rate",  # SES/stress
                    "education_level",  # Health knowledge
                    "uninsured_rate",  # Access to treatment
                ],
                causal_dag=[
                    ("poverty_rate", "obesity", 0.35),
                    ("poverty_rate", "stress", 0.40),  # Stronger for hypertension
                    ("education_level", "sodium_intake", -0.28),
                    ("obesity", "hypertension_prevalence", 0.42),
                    ("smoking", "hypertension_prevalence", 0.35),
                    ("stress", "hypertension_prevalence", 0.30),  # Key for BP
                    ("sodium_intake", "hypertension_prevalence", 0.25),
                    ("poverty_rate", "hypertension_prevalence", 0.18),
                ],
                proxy_measures={
                    "sodium_intake": "obesity",  # High-sodium diet correlates with obesity
                    "stress": "mental_health",  # Mental health as stress proxy
                },
                prevalence_range=(20.0, 45.0),  # Higher prevalence than diabetes
                temporal_lag=5,
                metadata={
                    "primary_mechanism": "vascular_resistance",
                    "modifiable_factors": ["sodium", "obesity", "exercise", "stress"],
                    "screening_age": 18,
                    "intervention_roi": 4.5,
                },
            )
        )

        # Coronary Heart Disease
        self.register(
            DiseaseConfig(
                disease_id="heart_disease",
                display_name="Coronary Heart Disease",
                places_measure_id="CHD",
                target_variable="heart_disease_prevalence",
                key_predictors=[
                    "smoking",  # Strongest for CHD
                    "obesity",
                    "physical_inactivity",
                    "high_cholesterol",  # Lipid profile critical
                    "hypertension",  # Upstream condition
                    "diabetes",  # Comorbidity
                    "poverty_rate",
                    "education_level",
                    "uninsured_rate",
                ],
                causal_dag=[
                    ("smoking", "heart_disease_prevalence", 0.50),  # Dominant risk
                    ("obesity", "high_cholesterol", 0.38),
                    ("obesity", "hypertension", 0.42),
                    ("high_cholesterol", "heart_disease_prevalence", 0.45),
                    ("hypertension", "heart_disease_prevalence", 0.40),
                    ("diabetes", "heart_disease_prevalence", 0.35),
                    ("physical_inactivity", "heart_disease_prevalence", 0.25),
                    ("poverty_rate", "heart_disease_prevalence", 0.15),
                ],
                proxy_measures={
                    "high_cholesterol": "obesity",  # If cholesterol unavailable
                },
                prevalence_range=(3.0, 12.0),
                temporal_lag=15,
                metadata={
                    "primary_mechanism": "atherosclerosis",
                    "modifiable_factors": ["smoking", "cholesterol", "blood_pressure"],
                    "screening_age": 40,
                    "intervention_roi": 5.8,
                },
            )
        )

        # COPD (Chronic Obstructive Pulmonary Disease)
        self.register(
            DiseaseConfig(
                disease_id="copd",
                display_name="Chronic Obstructive Pulmonary Disease",
                places_measure_id="COPD",
                target_variable="copd_prevalence",
                key_predictors=[
                    "smoking",  # Dominant factor (80-90% of cases)
                    "air_quality",  # Environmental exposure (proxy: urbanization)
                    "occupational_exposure",  # Industrial jobs (proxy: industry_rate)
                    "poverty_rate",  # Access to healthcare
                    "education_level",  # Smoking prevention
                    "uninsured_rate",
                ],
                causal_dag=[
                    ("smoking", "copd_prevalence", 0.70),  # Overwhelming dominance
                    ("air_quality", "copd_prevalence", 0.25),
                    ("occupational_exposure", "copd_prevalence", 0.20),
                    ("poverty_rate", "smoking", 0.30),
                    ("education_level", "smoking", -0.35),
                    ("poverty_rate", "copd_prevalence", 0.12),
                ],
                proxy_measures={
                    "air_quality": "urbanization_rate",
                    "occupational_exposure": "manufacturing_employment",
                },
                prevalence_range=(4.0, 15.0),
                temporal_lag=20,  # Long latency period
                metadata={
                    "primary_mechanism": "airway_inflammation",
                    "modifiable_factors": ["smoking", "air_quality", "workplace_safety"],
                    "screening_age": 40,
                    "intervention_roi": 2.8,
                },
            )
        )

        # Chronic Kidney Disease
        self.register(
            DiseaseConfig(
                disease_id="kidney_disease",
                display_name="Chronic Kidney Disease",
                places_measure_id="KIDNEY",
                target_variable="kidney_disease_prevalence",
                key_predictors=[
                    "diabetes",  # Diabetic nephropathy (primary cause)
                    "hypertension",  # Hypertensive nephropathy
                    "obesity",  # Metabolic syndrome
                    "smoking",
                    "poverty_rate",
                    "uninsured_rate",  # Delayed diagnosis
                    "education_level",
                ],
                causal_dag=[
                    ("diabetes", "kidney_disease_prevalence", 0.50),  # Leading cause
                    ("hypertension", "kidney_disease_prevalence", 0.45),
                    ("obesity", "diabetes", 0.45),
                    ("obesity", "hypertension", 0.42),
                    ("smoking", "kidney_disease_prevalence", 0.20),
                    ("poverty_rate", "kidney_disease_prevalence", 0.15),
                    ("uninsured_rate", "kidney_disease_prevalence", 0.18),  # Late detection
                ],
                prevalence_range=(2.0, 8.0),
                temporal_lag=15,
                metadata={
                    "primary_mechanism": "glomerular_damage",
                    "modifiable_factors": ["diabetes_control", "blood_pressure", "obesity"],
                    "screening_age": 50,
                    "intervention_roi": 6.2,  # High due to dialysis costs
                },
            )
        )

        # Stroke
        self.register(
            DiseaseConfig(
                disease_id="stroke",
                display_name="Stroke",
                places_measure_id="STROKE",
                target_variable="stroke_prevalence",
                key_predictors=[
                    "hypertension",  # Primary risk
                    "smoking",
                    "diabetes",
                    "obesity",
                    "physical_inactivity",
                    "poverty_rate",
                    "uninsured_rate",
                    "education_level",
                ],
                causal_dag=[
                    ("hypertension", "stroke_prevalence", 0.55),  # Dominant
                    ("smoking", "stroke_prevalence", 0.40),
                    ("diabetes", "stroke_prevalence", 0.35),
                    ("obesity", "hypertension", 0.42),
                    ("physical_inactivity", "stroke_prevalence", 0.22),
                    ("poverty_rate", "stroke_prevalence", 0.18),
                ],
                prevalence_range=(2.0, 6.0),
                temporal_lag=10,
                metadata={
                    "primary_mechanism": "cerebrovascular_damage",
                    "modifiable_factors": ["blood_pressure", "smoking", "cholesterol"],
                    "screening_age": 40,
                    "intervention_roi": 7.5,  # High due to disability costs
                },
            )
        )

    def register(self, config: DiseaseConfig):
        """Register a new disease configuration."""
        self._registry[config.disease_id] = config
        logger.info(f"Registered disease config: {config.disease_id} ({config.display_name})")

    def get_config(self, disease_id: str) -> DiseaseConfig:
        """
        Get disease configuration by ID.

        Args:
            disease_id: Disease identifier (e.g., 'diabetes', 'hypertension')

        Returns:
            DiseaseConfig for the requested disease

        Raises:
            ValueError: If disease_id not found in registry
        """
        if disease_id not in self._registry:
            available = ", ".join(self._registry.keys())
            raise ValueError(
                f"Unknown disease_id: {disease_id}. " f"Available diseases: {available}"
            )
        return self._registry[disease_id]

    def list_diseases(self) -> List[Dict[str, str]]:
        """
        List all registered diseases.

        Returns:
            List of dicts with disease_id and display_name
        """
        return [
            {"disease_id": config.disease_id, "display_name": config.display_name}
            for config in self._registry.values()
        ]

    def validate_disease_data(self, disease_id: str, dataframe: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate that required features are available for a disease.

        Args:
            disease_id: Disease to validate
            dataframe: DataFrame with available features

        Returns:
            Validation report with available/missing features
        """
        config = self.get_config(disease_id)
        available_features = set(dataframe.columns)
        return config.validate_features(available_features)


class PLACESConnector(LicensedConnectorMixin, BaseDispatcherConnector):
    """
    Connector for CDC PLACES local-area health estimates.

    PLACES provides model-based estimates at county, tract, place, and ZIP levels
    using small-area estimation methods combining BRFSS survey data with Census
    demographics. This enables county and tract-level analysis where direct survey
    estimates would be unreliable due to small sample sizes.

    This connector uses the dispatcher pattern with query_type parameter:
    - "chronic_disease": analyze_chronic_disease() - Chronic disease prevalence
    - "risk_behaviors": track_risk_behaviors() - Behavioral risk factors
    - "prevention": get_preventive_care() - Preventive service use
    - "health_status": get_health_status() - General health indicators
    - "disparities": analyze_health_disparities() - Geographic health equity

    Key Datasets:
    - County: swc5-untb (2024 release), duw2-7jbt (2022 release), ~3,143 counties/year
    - Tract: cwsq-ngmh (2024 release), ~84,000 tracts/year
    - Years: 2019-2024 (check data.cdc.gov for latest)

    Example Usage:
        >>> conn = PLACESConnector()
        >>>
        >>> # Get county-level diabetes for all years
        >>> diabetes = conn.fetch(
        ...     query_type='chronic_disease',
        ...     disease_type='diabetes',
        ...     geographic_level='county',
        ...     year_start=2019,
        ...     year_end=2023
        ... )
        >>> print(f"Counties: {len(diabetes)}")  # ~15,715 (3,143 counties × 5 years)
        >>>
        >>> # Get tract-level heart disease for California
        >>> heart = conn.fetch(
        ...     query_type='chronic_disease',
        ...     disease_type='heart_disease',
        ...     geographic_level='tract',
        ...     state='CA',
        ...     year=2023
        ... )
        >>> print(f"CA tracts: {len(heart)}")  # ~9,000 tracts
    """

    # Dispatcher configuration
    DISPATCH_PARAM = "query_type"
    DISPATCH_MAP = {
        "chronic_disease": "analyze_chronic_disease",
        "risk_behaviors": "track_risk_behaviors",
        "prevention": "get_preventive_care",
        "health_status": "get_health_status",
        "disparities": "analyze_health_disparities",
    }

    # License metadata
    _connector_name = "Places"
    _required_tier = DataTier.PROFESSIONAL

    # CDC PLACES API endpoints (Socrata Open Data API)
    # TODO: CRITICAL - VERIFY THESE ENDPOINTS ARE CURRENT
    # Last verified: Never (auto-generated from documentation)
    # Status: FAILING - returning "No data for measure DIABETES, year 2022"
    #
    # How to verify:
    # 1. Visit: https://chronicdata.cdc.gov/browse?category=500+Cities+%26+Places
    # 2. Search: "PLACES tract 2024" or "PLACES census tract 2024"
    # 3. Open dataset → API → note the resource ID (e.g., "cwsq-ngmh")
    # 4. Test: curl "https://data.cdc.gov/resource/cwsq-ngmh.json?\$limit=1"
    # 5. If returns data → endpoint valid, if 404 → update ID below
    #
    # Alternative verification using R:
    # install.packages("CDCPLACES")
    # library(CDCPLACES)
    # df <- get_places(geography="census", state="CA", measure="DIABETES", release="2024")
    #
    ENDPOINTS = {
        "county_2024": "swc5-untb",  # Most recent county data - NEEDS VERIFICATION
        "county_2023": "47z2-297k",  # 2023 release - NEEDS VERIFICATION
        "county_2022": "duw2-7jbt",  # 2022 release - NEEDS VERIFICATION
        "tract_2024": "cwsq-ngmh",  # Most recent tract data (2022 BRFSS) - NEEDS VERIFICATION
        "tract_2023": "em5e-5hvn",  # 2023 release (2021 BRFSS) - NEEDS VERIFICATION
        "tract_2022": "nw2y-v4gm",  # 2022 release (2020 BRFSS) - NEEDS VERIFICATION
        "tract_2021": "373s-ayzu",  # 2021 release (2019 BRFSS) - NEEDS VERIFICATION
        "tract_2020": "4ai3-zynv",  # 2020 release (2018 BRFSS) - NEEDS VERIFICATION
    }

    # Measure mappings from common names to PLACES measure IDs
    MEASURE_MAP = {
        # Chronic diseases (Health Outcomes)
        "diabetes": "DIABETES",
        "heart_disease": "CHD",
        "coronary_heart_disease": "CHD",
        "stroke": "STROKE",
        "asthma": "CASTHMA",
        "copd": "COPD",
        "kidney_disease": "KIDNEY",
        "cancer": "CANCER",
        "arthritis": "ARTHRITIS",
        "high_blood_pressure": "BPHIGH",
        "high_cholesterol": "HIGHCHOL",
        "obesity": "OBESITY",
        # Risk behaviors
        "smoking": "CSMOKING",
        "current_smoking": "CSMOKING",
        "physical_inactivity": "LPA",
        "no_exercise": "LPA",
        "binge_drinking": "BINGE",
        # Mental health (Health Status)
        "depression": "DEPRESSION",
        "mental_health": "MHLTH",
        "poor_mental_health": "MHLTH",
        "physical_health": "PHLTH",
        "poor_physical_health": "PHLTH",
        "general_health": "GHLTH",
        "poor_general_health": "GHLTH",
        # Prevention
        "checkup": "CHECKUP",
        "annual_checkup": "CHECKUP",
        "dental_visit": "DENTAL",
        "colon_screening": "COLON_SCREEN",
        "mammography": "MAMMOUSE",
        "cervical_screening": "CERVICAL",
    }

    def __init__(self, **kwargs):
        """
        Initialize PLACES connector.

        Args:
            **kwargs: Additional configuration options
        """
        super().__init__(**kwargs)
        self.base_url = "https://data.cdc.gov/resource"

        # Initialize disease registry for modular disease handling
        self.disease_registry = DiseaseRegistry()

        # Configure session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.headers.update(
            {"User-Agent": "KRL-Data-Connectors/0.4.0", "Accept": "application/json"}
        )

    def _get_api_key(self) -> Optional[str]:
        """
        Get CDC API key from configuration.

        Returns:
            API key if configured, None otherwise (PLACES API is open)
        """
        # PLACES API is public and doesn't require authentication
        # Return None to skip API key in requests
        return None

    def connect(self) -> None:
        """
        Test connection to PLACES API.

        PLACES data is publicly accessible without authentication.
        """
        logger.info("PLACES connector initialized (API open access)")
        logger.info(f"Registered diseases: {len(self.disease_registry.list_diseases())}")

    def get_disease_config(self, disease_id: str) -> DiseaseConfig:
        """
        Get configuration for a specific disease.

        Args:
            disease_id: Disease identifier (e.g., 'diabetes', 'hypertension')

        Returns:
            DiseaseConfig with target variable, predictors, and causal DAG

        Example:
            >>> conn = PLACESConnector()
            >>> config = conn.get_disease_config('diabetes')
            >>> print(config.key_predictors)
            ['obesity', 'smoking', 'physical_inactivity', ...]
        """
        return self.disease_registry.get_config(disease_id)

    def list_available_diseases(self) -> List[Dict[str, str]]:
        """
        List all diseases with pre-configured support.

        Returns:
            List of dicts with disease_id and display_name

        Example:
            >>> conn = PLACESConnector()
            >>> diseases = conn.list_available_diseases()
            >>> for d in diseases:
            ...     print(f"{d['disease_id']}: {d['display_name']}")
            diabetes: Type 2 Diabetes
            hypertension: Hypertension
            heart_disease: Coronary Heart Disease
            ...
        """
        return self.disease_registry.list_diseases()

    def validate_disease_features(self, disease_id: str, dataframe: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate that required features are available for disease modeling.

        Args:
            disease_id: Disease to validate
            dataframe: DataFrame with available features

        Returns:
            Dict with validation results:
                - available: List of present predictors
                - missing: List of absent predictors
                - proxies_available: Dict of proxy substitutions
                - coverage: Fraction of required features available (0.0-1.0)

        Example:
            >>> df = pd.DataFrame({'obesity': [...], 'smoking': [...]})
            >>> validation = conn.validate_disease_features('diabetes', df)
            >>> print(f"Coverage: {validation['coverage']:.1%}")
            Coverage: 85.7%
        """
        return self.disease_registry.validate_disease_data(disease_id, dataframe)

    def _get_endpoint_id(
        self,
        geographic_level: Literal["county", "tract", "place", "zcta"],
        year: Optional[int] = None,
    ) -> str:
        """
        Get the appropriate Socrata dataset ID for the requested geography and year.

        CDC PLACES releases have overlapping data years based on BRFSS data collection:
        County endpoints:
        - swc5-untb (county_2024): 2021-2022 data
        - duw2-7jbt (county_2022): 2019-2020 data

        Tract endpoints (BRFSS year shown):
        - cwsq-ngmh (tract_2024): 2022 BRFSS data
        - em5e-5hvn (tract_2023): 2021 BRFSS data
        - nw2y-v4gm (tract_2022): 2020 BRFSS data
        - 373s-ayzu (tract_2021): 2019 BRFSS data
        - 4ai3-zynv (tract_2020): 2018 BRFSS data

        Args:
            geographic_level: Geographic level ('county', 'tract', 'place', 'zcta')
            year: Data year (defaults to most recent)

        Returns:
            Socrata dataset ID (e.g., 'swc5-untb')
        """
        if geographic_level == "county":
            if year is None or year >= 2021:
                return self.ENDPOINTS["county_2024"]  # swc5-untb: 2021-2022
            else:
                return self.ENDPOINTS["county_2022"]  # duw2-7jbt: 2019-2020

        elif geographic_level == "tract":
            # Tract data: each release contains one BRFSS year
            if year is None or year >= 2022:
                return self.ENDPOINTS["tract_2024"]  # 2022 BRFSS
            elif year == 2021:
                return self.ENDPOINTS["tract_2023"]  # 2021 BRFSS
            elif year == 2020:
                return self.ENDPOINTS["tract_2022"]  # 2020 BRFSS
            elif year == 2019:
                return self.ENDPOINTS["tract_2021"]  # 2019 BRFSS
            elif year == 2018:
                return self.ENDPOINTS["tract_2020"]  # 2018 BRFSS
            else:
                logger.warning(
                    f"Year {year} not available for tract data, using most recent (2022)"
                )
                return self.ENDPOINTS["tract_2024"]
        else:
            raise ValueError(
                f"Geographic level {geographic_level} not yet supported. Use 'county' or 'tract'."
            )

    def _build_soql_query(
        self,
        measure_id: str,
        year: Optional[int] = None,
        state: Optional[str] = None,
        data_value_type: str = "Age-adjusted prevalence",
    ) -> str:
        """
        Build SoQL query for CDC PLACES API.

        Args:
            measure_id: PLACES measure ID (e.g., 'DIABETES', 'CHD')
            year: Data year filter
            state: State abbreviation filter (e.g., 'CA', 'TX')
            data_value_type: Type of prevalence (default: age-adjusted)

        Returns:
            SoQL WHERE clause
        """
        conditions = [f"measureid='{measure_id}'"]

        if year:
            conditions.append(f"year='{year}'")

        if state:
            conditions.append(f"stateabbr='{state.upper()}'")

        conditions.append(f"data_value_type='{data_value_type}'")

        return " AND ".join(conditions)

    @requires_license
    def analyze_chronic_disease(
        self,
        disease_type: str,
        geographic_level: Literal["county", "tract"] = "county",
        year: Optional[int] = None,
        year_start: Optional[int] = None,
        year_end: Optional[int] = None,
        state: Optional[str] = None,
        include_demographics: bool = False,
        return_config: bool = False,
    ) -> pd.DataFrame:
        """
        Get chronic disease prevalence estimates at county or tract level.

        **DISEASE-AGNOSTIC**: Automatically adapts to any registered chronic disease.
        No code changes needed to switch from diabetes to hypertension to heart disease.

        This method is compatible with BRFSSConnector.analyze_chronic_disease() but
        returns county/tract-level estimates instead of state-level.

        Args:
            disease_type: Disease to analyze (supports registry lookup):
                - 'diabetes': Type 2 diabetes prevalence
                - 'hypertension' / 'high_blood_pressure': Hypertension
                - 'heart_disease' / 'coronary_heart_disease': CHD
                - 'stroke': Stroke prevalence
                - 'asthma': Current asthma
                - 'copd': COPD prevalence
                - 'kidney_disease': Chronic kidney disease
                - 'obesity': Adult obesity
                - 'high_cholesterol': High cholesterol
            geographic_level: 'county' (default) or 'tract'
            year: Single year to fetch (e.g., 2023)
            year_start: Start year for multi-year panel (e.g., 2019)
            year_end: End year for multi-year panel (e.g., 2023)
            state: State abbreviation filter (e.g., 'CA') or None for all states
            include_demographics: If True, include demographic breakdowns (future)
            return_config: If True, return (data, config) tuple with disease config

        Returns:
            DataFrame with columns:
                - geography: County/tract name
                - geography_id: FIPS code
                - state: State abbreviation
                - year: Data year
                - prevalence: Age-adjusted prevalence (%)
                - confidence_low: 95% CI lower bound
                - confidence_high: 95% CI upper bound
                - total_population: Total population
                - data_source: 'PLACES'
                - measure: Full measure name
                - disease_id: Normalized disease identifier

            If return_config=True, returns (DataFrame, DiseaseConfig)

        Example - Disease-agnostic workflow:
            >>> conn = PLACESConnector()
            >>>
            >>> # Analyst selects diabetes from dropdown
            >>> df_diabetes = conn.fetch(
            ...     query_type='chronic_disease',
            ...     disease_type='diabetes',
            ...     geographic_level='county',
            ...     year_start=2019,
            ...     year_end=2023
            ... )
            >>> print(f"Diabetes: {len(df_diabetes)} counties")
            Diabetes: 15715 counties
            >>>
            >>> # Analyst switches to hypertension - no code changes!
            >>> df_hypertension = conn.fetch(
            ...     query_type='chronic_disease',
            ...     disease_type='hypertension',
            ...     geographic_level='county',
            ...     year_start=2019,
            ...     year_end=2023
            ... )
            >>> print(f"Hypertension: {len(df_hypertension)} counties")
            Hypertension: 15715 counties
            >>>
            >>> # Get disease config for DAG construction
            >>> df, config = conn.fetch(
            ...     query_type='chronic_disease',
            ...     disease_type='diabetes',
            ...     geographic_level='county',
            ...     year=2023,
            ...     return_config=True
            ... )
            >>> print(f"Key predictors: {config.key_predictors}")
            >>> print(f"DAG edges: {len(config.causal_dag)}")
        """
        logger.info(f"Fetching PLACES data: {disease_type}, level={geographic_level}, year={year}")

        # Try to get disease config from registry (enables modular DAG construction)
        disease_config = None
        try:
            disease_config = self.disease_registry.get_config(disease_type.lower())
            measure_id = disease_config.places_measure_id
            logger.info(f"Using disease registry config: {disease_config.display_name}")
            logger.debug(f"Key predictors: {disease_config.key_predictors}")
        except ValueError:
            # Fall back to direct MEASURE_MAP lookup (for non-registered diseases)
            measure_id = self.MEASURE_MAP.get(disease_type.lower())
            if not measure_id:
                raise ValueError(
                    f"Unknown disease type: {disease_type}. "
                    f"Available: {', '.join(self.MEASURE_MAP.keys())}"
                )
            logger.info(f"Using direct measure mapping: {measure_id}")

        # Determine years to fetch
        if year:
            years = [year]
        elif year_start and year_end:
            years = list(range(year_start, year_end + 1))
        else:
            # Default to most recent year
            years = [2023]

        # Fetch data for each year
        all_data = []
        for yr in years:
            try:
                year_data = self._fetch_places_data(
                    measure_id=measure_id, geographic_level=geographic_level, year=yr, state=state
                )
                year_data["year"] = yr
                year_data["disease_id"] = disease_type.lower()  # Normalized ID
                all_data.append(year_data)
                logger.info(f"  ✅ {yr}: {len(year_data)} {geographic_level} records")
            except Exception as e:
                logger.warning(f"  ⚠️  {yr}: Failed ({str(e)}), skipping")
                continue

        if not all_data:
            raise Exception(f"No data successfully fetched for {disease_type}")

        # Combine all years
        combined = pd.concat(all_data, ignore_index=True)
        logger.info(f"Successfully fetched {len(combined)} records across {len(all_data)} years")

        # Add metadata for reproducibility
        combined.attrs["disease_id"] = disease_type.lower()
        combined.attrs["geographic_level"] = geographic_level
        combined.attrs["years"] = years
        combined.attrs["fetch_timestamp"] = datetime.now().isoformat()
        if disease_config:
            combined.attrs["disease_config"] = disease_config.disease_id

        # Return data with optional config
        if return_config and disease_config:
            return combined, disease_config
        elif return_config:
            logger.warning("return_config=True but disease not in registry; returning data only")

        return combined

    def _fetch_places_data(
        self, measure_id: str, geographic_level: str, year: int, state: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Fetch data from CDC PLACES API for a single year.

        Args:
            measure_id: PLACES measure ID (e.g., 'DIABETES')
            geographic_level: 'county' or 'tract'
            year: Data year
            state: State filter (optional)

        Returns:
            DataFrame with raw PLACES data
        """
        # Get appropriate endpoint
        endpoint_id = self._get_endpoint_id(geographic_level, year)
        url = f"{self.base_url}/{endpoint_id}.json"

        # CRITICAL FIX: Tract-level data uses "Crude prevalence", county uses "Age-adjusted prevalence"
        data_value_type = (
            "Crude prevalence" if geographic_level == "tract" else "Age-adjusted prevalence"
        )

        # Build query
        where_clause = self._build_soql_query(
            measure_id=measure_id,
            year=year,
            state=state,
            data_value_type=data_value_type,  # Pass correct type for geography level
        )

        # Query parameters
        params = {
            "$where": where_clause,
            "$limit": 50000,  # High limit for county/tract data
            "$offset": 0,
        }

        # Add API key if available
        api_key = self._get_api_key()
        if api_key:
            params["$$app_token"] = api_key

        logger.info(f"Querying CDC PLACES API: {url}")
        logger.debug(f"Query: {where_clause}")

        # Fetch data with pagination
        all_records = []
        while True:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            records = response.json()
            if not records:
                break

            all_records.extend(records)

            # Check if more pages exist
            if len(records) < params["$limit"]:
                break

            # Next page
            params["$offset"] += params["$limit"]

        logger.info(f"Received {len(all_records)} records from CDC PLACES API")

        if not all_records:
            raise ValueError(f"No data returned for measure {measure_id}, year {year}")

        # Convert to DataFrame and transform
        df = pd.DataFrame(all_records)
        return self._transform_places_response(df, geographic_level)

    def _transform_places_response(self, df: pd.DataFrame, geographic_level: str) -> pd.DataFrame:
        """
        Transform raw PLACES API response to standardized format.

        Converts CDC PLACES column names to match BRFSSConnector output format
        for compatibility with existing analysis code.

        Args:
            df: Raw PLACES DataFrame
            geographic_level: 'county' or 'tract'

        Returns:
            Standardized DataFrame with columns matching BRFSSConnector format
        """
        # Map PLACES columns to standard format
        transformed = pd.DataFrame()

        # Geography information
        if geographic_level == "county":
            transformed["geography"] = df.get("locationname", "")
            transformed["geography_id"] = df.get("locationid", "")
        else:  # tract
            transformed["geography"] = df.get("locationname", "")
            transformed["geography_id"] = df.get("locationid", "")

        transformed["state"] = df.get("stateabbr", "")

        # Health measure data
        transformed["prevalence"] = pd.to_numeric(df.get("data_value", 0), errors="coerce")
        transformed["confidence_low"] = pd.to_numeric(
            df.get("low_confidence_limit", 0), errors="coerce"
        )
        transformed["confidence_high"] = pd.to_numeric(
            df.get("high_confidence_limit", 0), errors="coerce"
        )
        transformed["total_population"] = (
            pd.to_numeric(df.get("totalpopulation", 0), errors="coerce").fillna(0).astype(int)
        )

        # Metadata
        transformed["data_source"] = "PLACES"
        transformed["measure"] = df.get("measure", "")
        transformed["measure_id"] = df.get("measureid", "")
        transformed["category"] = df.get("category", "")

        # For compatibility with BRFSS format, add these columns
        # (PLACES doesn't have sample_size since it's model-based)
        transformed["sample_size"] = transformed["total_population"]  # Use population as proxy
        transformed["age_adjusted_prevalence"] = transformed[
            "prevalence"
        ]  # PLACES uses age-adjusted by default

        # Drop rows with missing prevalence
        transformed = transformed[transformed["prevalence"].notna()].copy()

        logger.info(f"Transformed {len(transformed)} {geographic_level} records")

        return transformed

    @requires_license
    def track_risk_behaviors(
        self,
        behavior: str,
        geographic_level: Literal["county", "tract"] = "county",
        year: Optional[int] = None,
        year_start: Optional[int] = None,
        year_end: Optional[int] = None,
        state: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Get behavioral risk factor prevalence at county or tract level.

        Compatible with BRFSSConnector.track_risk_behaviors() but returns
        county/tract-level estimates.

        Args:
            behavior: Risk behavior to track:
                - 'smoking': Current smoking
                - 'obesity': Adult obesity
                - 'physical_inactivity': No leisure-time physical activity
                - 'binge_drinking': Binge drinking
                - 'depression': Depression diagnosis
            geographic_level: 'county' (default) or 'tract'
            year: Single year (e.g., 2023)
            year_start: Start year for panel data
            year_end: End year for panel data
            state: State abbreviation filter or None

        Returns:
            DataFrame with same structure as analyze_chronic_disease()
        """
        # Reuse chronic disease method (same API, different measures)
        return self.analyze_chronic_disease(
            disease_type=behavior,
            geographic_level=geographic_level,
            year=year,
            year_start=year_start,
            year_end=year_end,
            state=state,
            include_demographics=False,
        )

    @requires_license
    def get_preventive_care(
        self,
        service: str,
        geographic_level: Literal["county", "tract"] = "county",
        year: Optional[int] = None,
        state: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Get preventive care utilization at county or tract level.

        Args:
            service: Preventive service:
                - 'checkup': Annual checkup
                - 'dental_visit': Dental visit in past year
                - 'colon_screening': Colorectal cancer screening
                - 'mammography': Mammography use
                - 'cervical_screening': Cervical cancer screening
            geographic_level: 'county' or 'tract'
            year: Data year (defaults to most recent)
            state: State filter or None

        Returns:
            DataFrame with same structure as analyze_chronic_disease()
        """
        return self.analyze_chronic_disease(
            disease_type=service,
            geographic_level=geographic_level,
            year=year,
            state=state,
            include_demographics=False,
        )

    @requires_license
    def get_health_status(
        self,
        indicator: str,
        geographic_level: Literal["county", "tract"] = "county",
        year: Optional[int] = None,
        state: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Get general health status indicators at county or tract level.

        Args:
            indicator: Health status indicator:
                - 'general_health': Poor or fair general health
                - 'physical_health': ≥14 days poor physical health
                - 'mental_health': ≥14 days poor mental health
            geographic_level: 'county' or 'tract'
            year: Data year (defaults to most recent)
            state: State filter or None

        Returns:
            DataFrame with same structure as analyze_chronic_disease()
        """
        return self.analyze_chronic_disease(
            disease_type=indicator,
            geographic_level=geographic_level,
            year=year,
            state=state,
            include_demographics=False,
        )

    @requires_license
    def analyze_health_disparities(
        self,
        measures: List[str],
        geographic_level: Literal["county", "tract"] = "county",
        year: int = 2023,
        disparity_type: str = "geographic",
    ) -> pd.DataFrame:
        """
        Analyze health disparities across geographies.

        Args:
            measures: List of measures to compare (e.g., ['diabetes', 'heart_disease'])
            geographic_level: 'county' or 'tract'
            year: Data year
            disparity_type: Type of disparity analysis (currently only 'geographic')

        Returns:
            DataFrame with disparity metrics across geographies
        """
        # Fetch all measures
        data_frames = []
        for measure in measures:
            df = self.analyze_chronic_disease(
                disease_type=measure, geographic_level=geographic_level, year=year
            )
            df["measure_type"] = measure
            data_frames.append(df)

        # Combine all measures
        combined = pd.concat(data_frames, ignore_index=True)

        # Calculate disparity metrics
        disparity_summary = (
            combined.groupby("measure_type")
            .agg({"prevalence": ["mean", "std", "min", "max"], "geography": "count"})
            .reset_index()
        )

        disparity_summary.columns = [
            "measure",
            "mean_prevalence",
            "std_prevalence",
            "min_prevalence",
            "max_prevalence",
            "n_geographies",
        ]
        disparity_summary["disparity_ratio"] = (
            disparity_summary["max_prevalence"] / disparity_summary["min_prevalence"]
        )

        logger.info(
            f"Analyzed disparities for {len(measures)} measures across {len(combined)} geographies"
        )

        return disparity_summary
