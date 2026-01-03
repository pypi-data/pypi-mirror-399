# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

# Copyright (c) 2025 KR-Labs Foundation. All rights reserved.
# Licensed under Apache License 2.0 (see LICENSE file for details)

"""
National Household Travel Survey (NHTS) Connector

Provides access to NHTS data on travel behavior and transportation patterns
in the United States. NHTS is the authoritative source for national data on
daily travel, including trip purposes, mode choice, vehicle characteristics,
and commuting patterns.

Data Sources:
- NHTS 2017: Latest comprehensive survey (129,696 households)
- NHTS 2009: Previous survey for trend analysis
- NHTS 2001: Historical comparison

Geographic Coverage:
- National sample with state and metropolitan area representation
- Census regions and divisions
- Urban vs rural classifications

Key Domains:
- D14: Transportation & Commuting
- D25: Urban Planning (secondary)

Survey Components:
- Household data: Demographics, vehicles, location
- Person data: Individual characteristics, employment
- Trip data: Daily travel patterns, purposes, modes
- Vehicle data: Make, model, fuel type, usage
"""

import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Union

import pandas as pd
import requests

from krl_data_connectors.base_dispatcher_connector import BaseDispatcherConnector
from krl_data_connectors.core import DataTier
from krl_data_connectors.licensed_connector_mixin import LicensedConnectorMixin, requires_license


class NHTSConnector(LicensedConnectorMixin, BaseDispatcherConnector):
    """
        Connector for National Household Travel Survey (NHTS) data.

        NHTS is conducted by the Federal Highway Administration (FHWA) and provides
        comprehensive data on travel behavior in the United States. The survey
        captures daily travel patterns, mode choice, vehicle usage, and demographic
        characteristics.
    """

    # Registry name for license validation
    _connector_name = "NHTS"

    """

        This connector uses the dispatcher pattern with data_type parameter to route
        requests to specific data loading methods:
        - "household": load_household_data() - household demographics and vehicles
        - "person": load_person_data() - individual characteristics
        - "trip": load_trip_data() - daily travel patterns
        - "vehicle": load_vehicle_data() - vehicle characteristics

        Args:
            cache_dir: Directory for cache files (default: ~/.krl_cache/transportation)
            cache_ttl: Cache time-to-live in seconds (default: 90 days)
            timeout: Request timeout in seconds (default: 120 for large files)
            max_retries: Maximum number of retry attempts (default: 3)
            survey_year: NHTS survey year to use (default: "2017")

        Example:
            >>> from krl_data_connectors import NHTSConnector
    from ...licensed_connector_mixin import LicensedConnectorMixin, requires_license
    from ...core import DataTier
            >>> nhts = NHTSConnector()
            >>>
            >>> # Get household data using dispatcher
            >>> households = nhts.fetch(data_type="household")
            >>>
            >>> # Get trip data for California
            >>> ca_trips = nhts.fetch(data_type="trip", state_fips="06")
            >>>
            >>> # Analyze commute patterns
            >>> commute_stats = nhts.get_commute_statistics(geography="state")
    """

    # NHTS 2017 Data Download URLs (FHWA)
    # Public use files hosted at Oak Ridge National Laboratory (ORNL)
    BASE_URL = "https://nhts.ornl.gov/assets/2016/"

    # Main data files (CSV format)
    HOUSEHOLD_FILE_URL = (
        f"{BASE_URL}download/csv.zip"  # Contains household, person, trip, vehicle files
    )

    # 2017 Survey year (most recent)
    SURVEY_YEAR_2017 = "2017"
    SURVEY_YEAR_2009 = "2009"
    SURVEY_YEAR_2001 = "2001"

    # Data file names within the ZIP
    HOUSEHOLD_CSV = "hhpub.csv"
    PERSON_CSV = "perpub.csv"
    TRIP_CSV = "trippub.csv"
    VEHICLE_CSV = "vehpub.csv"

    # Dispatcher configuration
    DISPATCH_PARAM = "data_type"
    DISPATCH_MAP = {
        "household": "load_household_data",
        "person": "load_person_data",
        "trip": "load_trip_data",
        "vehicle": "load_vehicle_data",
    }

    def __init__(
        self,
        cache_dir: Optional[str] = None,
        cache_ttl: int = 7776000,  # 90 days (NHTS data updated infrequently)
        timeout: int = 120,
        max_retries: int = 3,
        survey_year: str = SURVEY_YEAR_2017,
    ):
        """Initialize NHTS connector."""
        # Set default cache directory for transportation data
        if cache_dir is None:
            cache_dir = str(Path.home() / ".krl_cache" / "transportation")

        super().__init__(
            api_key=None,  # No API key required
            cache_dir=cache_dir,
            cache_ttl=cache_ttl,
            timeout=timeout,
            max_retries=max_retries,
        )

        self.survey_year = survey_year
        self._household_data: Optional[pd.DataFrame] = None
        self._person_data: Optional[pd.DataFrame] = None
        self._trip_data: Optional[pd.DataFrame] = None
        self._vehicle_data: Optional[pd.DataFrame] = None

        self.logger.info(
            "NHTSConnector initialized",
            extra={
                "survey_year": survey_year,
                "cache_dir": cache_dir,
                "cache_ttl_days": cache_ttl / 86400,
            },
        )

    def _get_api_key(self) -> Optional[str]:
        """
        Get API key from configuration.

        NHTS data is publicly available and does not require an API key.

        Returns:
            None (no API key required)
        """
        return None

    def connect(self) -> None:
        """
        Establish connection to NHTS data sources.

        Since this connector uses public CSV files, "connecting"
        means initializing the HTTP session for file downloads.

        Example:
            >>> nhts = NHTSConnector()
            >>> nhts.connect()
            >>> print("Connected successfully")
            Connected successfully
        """
        try:
            self.session = self._init_session()
            self.logger.info("Connection established to NHTS data sources")
        except Exception as e:
            self.logger.error(f"Failed to connect: {str(e)}")
            raise

    # fetch() method inherited from BaseDispatcherConnector

    def _download_and_extract_data(
        self,
        force_download: bool = False,
    ) -> Path:
        """
        Download and extract NHTS data files.

        Args:
            force_download: Force re-download even if cached

        Returns:
            Path to the extracted data directory

        Raises:
            requests.RequestException: If download fails
        """
        # Build cache path
        cache_dir = Path(self.cache.cache_dir)
        extract_dir = cache_dir / f"nhts_{self.survey_year}"

        # Check if already extracted
        household_file = extract_dir / self.HOUSEHOLD_CSV
        if household_file.exists() and not force_download:
            self.logger.info(f"Using cached NHTS data from {extract_dir}")
            return extract_dir

        # Download ZIP file
        zip_filename = f"nhts_{self.survey_year}.zip"
        zip_path = cache_dir / zip_filename

        if not zip_path.exists() or force_download:
            self.logger.info(f"Downloading NHTS {self.survey_year} data")

            # Ensure session is initialized
            if self.session is None:
                self.connect()

            # Download file
            session = self.session
            if session is None:
                raise RuntimeError("Failed to initialize session")

            response = session.get(self.HOUSEHOLD_FILE_URL, stream=True, timeout=self.timeout)
            response.raise_for_status()

            # Create cache directory
            cache_dir.mkdir(parents=True, exist_ok=True)

            # Download with progress indication
            total_size = int(response.headers.get("content-length", 0))
            block_size = 1024 * 1024  # 1MB chunks

            with open(zip_path, "wb") as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=block_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0 and downloaded % (block_size * 10) == 0:
                            progress = (downloaded / total_size) * 100
                            self.logger.debug(f"Download progress: {progress:.1f}%")

            self.logger.info(
                f"Downloaded NHTS {self.survey_year} data",
                extra={"size_mb": zip_path.stat().st_size / (1024 * 1024)},
            )

        # Extract ZIP file
        import zipfile

        extract_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)

        self.logger.info(f"Extracted NHTS data to {extract_dir}")

        return extract_dir

    def load_household_data(
        self,
        force_download: bool = False,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Load NHTS household-level data.

        Household data includes demographic information, location,
        vehicle ownership, and household characteristics.

        Args:
            force_download: Force re-download of data file

        Returns:
            DataFrame with household-level data

        Key Variables:
            - HOUSEID: Unique household identifier
            - HHSTATE: State FIPS code
            - HHSIZE: Number of people in household
            - NUMADLT: Number of adults (18+)
            - WRKCOUNT: Number of workers
            - HHVEHCNT: Number of vehicles
            - HHFAMINC: Household income category
            - URBAN: Urban/rural classification
            - WTHHFIN: Final household weight

        Example:
            >>> nhts = NHTSConnector()
            >>> households = nhts.load_household_data()
            >>> print(f"Total households: {len(households):,}")
            Total households: 129,696
        """
        if self._household_data is None or force_download:
            extract_dir = self._download_and_extract_data(force_download)
            household_file = extract_dir / self.HOUSEHOLD_CSV

            self.logger.info("Loading household data")
            self._household_data = pd.read_csv(household_file, low_memory=False)

            self.logger.info(
                "Loaded household data",
                extra={
                    "rows": len(self._household_data),
                    "columns": len(self._household_data.columns),
                },
            )

        return self._household_data.copy()

    def load_person_data(
        self,
        force_download: bool = False,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Load NHTS person-level data.

        Person data includes individual characteristics, employment,
        education, and travel behavior.

        Args:
            force_download: Force re-download of data file

        Returns:
            DataFrame with person-level data

        Key Variables:
            - HOUSEID: Household identifier (links to household data)
            - PERSONID: Unique person identifier
            - R_AGE: Age of person
            - R_SEX: Sex (1=Male, 2=Female)
            - WORKER: Worker status
            - EDUC: Education level
            - WKFTPT: Full-time/part-time status
            - WTPERFIN: Final person weight

        Example:
            >>> nhts = NHTSConnector()
            >>> persons = nhts.load_person_data()
            >>> print(f"Total persons: {len(persons):,}")
            Total persons: 264,234
        """
        if self._person_data is None or force_download:
            extract_dir = self._download_and_extract_data(force_download)
            person_file = extract_dir / self.PERSON_CSV

            self.logger.info("Loading person data")
            self._person_data = pd.read_csv(person_file, low_memory=False)

            self.logger.info(
                "Loaded person data",
                extra={
                    "rows": len(self._person_data),
                    "columns": len(self._person_data.columns),
                },
            )

        return self._person_data.copy()

    def load_trip_data(
        self,
        force_download: bool = False,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Load NHTS trip-level data.

        Trip data includes all trips made by household members on the
        assigned travel day, with information on purpose, mode, distance,
        and duration.

        Args:
            force_download: Force re-download of data file

        Returns:
            DataFrame with trip-level data

        Key Variables:
            - HOUSEID: Household identifier
            - PERSONID: Person identifier
            - TDTRPNUM: Trip number for the person
            - TRPTRANS: Transportation mode
            - WHYTRP1S: Trip purpose
            - TRPMILES: Trip distance in miles
            - TRVLCMIN: Travel time in minutes
            - WTTRDFIN: Final trip weight

        Example:
            >>> nhts = NHTSConnector()
            >>> trips = nhts.load_trip_data()
            >>> print(f"Total trips: {len(trips):,}")
            Total trips: 923,572
        """
        if self._trip_data is None or force_download:
            extract_dir = self._download_and_extract_data(force_download)
            trip_file = extract_dir / self.TRIP_CSV

            self.logger.info("Loading trip data")
            self._trip_data = pd.read_csv(trip_file, low_memory=False)

            self.logger.info(
                "Loaded trip data",
                extra={
                    "rows": len(self._trip_data),
                    "columns": len(self._trip_data.columns),
                },
            )

        return self._trip_data.copy()

    def load_vehicle_data(
        self,
        force_download: bool = False,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Load NHTS vehicle-level data.

        Vehicle data includes characteristics of household vehicles,
        including make, model, year, fuel type, and annual mileage.

        Args:
            force_download: Force re-download of data file

        Returns:
            DataFrame with vehicle-level data

        Key Variables:
            - HOUSEID: Household identifier
            - VEHID: Vehicle number within household
            - VEHYEAR: Vehicle model year
            - MAKE: Vehicle make
            - MODEL: Vehicle model
            - FUELTYPE: Fuel type
            - VEHTYPE: Vehicle type
            - ANNMILES: Annual miles driven

        Example:
            >>> nhts = NHTSConnector()
            >>> vehicles = nhts.load_vehicle_data()
            >>> print(f"Total vehicles: {len(vehicles):,}")
            Total vehicles: 256,115
        """
        if self._vehicle_data is None or force_download:
            extract_dir = self._download_and_extract_data(force_download)
            vehicle_file = extract_dir / self.VEHICLE_CSV

            self.logger.info("Loading vehicle data")
            self._vehicle_data = pd.read_csv(vehicle_file, low_memory=False)

            self.logger.info(
                "Loaded vehicle data",
                extra={
                    "rows": len(self._vehicle_data),
                    "columns": len(self._vehicle_data.columns),
                },
            )

        return self._vehicle_data.copy()

    @requires_license
    def get_trips_by_state(
        self,
        state_fips: str,
        force_download: bool = False,
    ) -> pd.DataFrame:
        """
        Get all trips for a specific state.

        Args:
            state_fips: State FIPS code (e.g., "06" for California)
            force_download: Force re-download of data

        Returns:
            DataFrame with trips from the specified state

        Example:
            >>> nhts = NHTSConnector()
            >>> ca_trips = nhts.get_trips_by_state(state_fips="06")
            >>> print(f"California trips: {len(ca_trips):,}")
        """
        # Load household and trip data
        households = self.load_household_data(force_download)
        trips = self.load_trip_data(force_download)

        # Filter households to state
        state_households = households[
            households["HHSTATE"].astype(str).str.zfill(2) == str(state_fips).zfill(2)
        ]

        # Filter trips to those households
        state_trips = trips[trips["HOUSEID"].isin(state_households["HOUSEID"])]

        self.logger.info(
            f"Filtered trips for state {state_fips}",
            extra={
                "state_fips": state_fips,
                "trips": len(state_trips),
            },
        )

        return state_trips

    @requires_license
    def get_commute_statistics(
        self,
        geography: str = "national",
        state_fips: Optional[str] = None,
        force_download: bool = False,
    ) -> pd.DataFrame:
        """
        Calculate commute statistics (mode choice, distance, time).

        Args:
            geography: Geographic level ("national", "state")
            state_fips: State FIPS code (required if geography="state")
            force_download: Force re-download of data

        Returns:
            DataFrame with commute statistics by mode

        Statistics include:
            - Total commute trips
            - Average distance (miles)
            - Average travel time (minutes)
            - Mode share (percentage)

        Example:
            >>> nhts = NHTSConnector()
            >>> national_commute = nhts.get_commute_statistics(geography="national")
            >>> print(national_commute[['mode', 'trips', 'avg_miles', 'mode_share']])
        """
        # Load trip data
        trips = self.load_trip_data(force_download)

        # Filter to commute trips (WHYTRP1S == 03 = To/from work)
        commute_trips = trips[trips["WHYTRP1S"] == 3].copy()

        # Filter by state if specified
        if geography == "state":
            if state_fips is None:
                raise ValueError("state_fips required for state-level statistics")

            households = self.load_household_data(force_download)
            state_households = households[
                households["HHSTATE"].astype(str).str.zfill(2) == str(state_fips).zfill(2)
            ]
            commute_trips = commute_trips[
                commute_trips["HOUSEID"].isin(state_households["HOUSEID"])
            ]

        # Calculate statistics by mode
        stats = (
            commute_trips.groupby("TRPTRANS")
            .agg(
                {
                    "TDTRPNUM": "count",  # Count trips
                    "TRPMILES": "mean",  # Average distance
                    "TRVLCMIN": "mean",  # Average time
                }
            )
            .reset_index()
        )

        stats.columns = ["mode", "trips", "avg_miles", "avg_minutes"]

        # Calculate mode share
        total_trips = stats["trips"].sum()
        stats["mode_share"] = (stats["trips"] / total_trips * 100).round(2)

        # Sort by mode share descending
        stats = stats.sort_values("mode_share", ascending=False)

        self.logger.info(
            f"Calculated commute statistics ({geography})",
            extra={
                "geography": geography,
                "total_commute_trips": total_trips,
                "modes": len(stats),
            },
        )

        return stats

    @requires_license
    def get_mode_share(
        self,
        trip_purpose: Optional[str] = None,
        state_fips: Optional[str] = None,
        force_download: bool = False,
    ) -> pd.DataFrame:
        """
        Calculate mode share for trips.

        Args:
            trip_purpose: Trip purpose code (None = all purposes)
                - "03" = To/from work
                - "04" = School/church
                - "05" = Medical/dental
                - "06" = Shopping/errands
                - "07" = Social/recreational
            state_fips: State FIPS code (None = national)
            force_download: Force re-download of data

        Returns:
            DataFrame with mode share percentages

        Example:
            >>> nhts = NHTSConnector()
            >>> mode_share = nhts.get_mode_share(trip_purpose="03")  # Commute
            >>> print(mode_share[['mode', 'trips', 'share_pct']])
        """
        # Load trip data
        trips = self.load_trip_data(force_download)

        # Filter by purpose if specified
        if trip_purpose is not None:
            trips = trips[trips["WHYTRP1S"] == int(trip_purpose)]

        # Filter by state if specified
        if state_fips is not None:
            households = self.load_household_data(force_download)
            state_households = households[
                households["HHSTATE"].astype(str).str.zfill(2) == str(state_fips).zfill(2)
            ]
            trips = trips[trips["HOUSEID"].isin(state_households["HOUSEID"])]

        # Calculate mode share
        mode_counts = trips["TRPTRANS"].value_counts()
        mode_share = pd.DataFrame(
            {
                "mode": mode_counts.index,
                "trips": mode_counts.values,
                "share_pct": (mode_counts / mode_counts.sum() * 100).round(2),
            }
        )

        mode_share = mode_share.sort_values("share_pct", ascending=False)

        self.logger.info(
            "Calculated mode share",
            extra={
                "trip_purpose": trip_purpose,
                "state_fips": state_fips,
                "total_trips": mode_share["trips"].sum(),
            },
        )

        return mode_share

    @requires_license
    def get_vehicle_ownership_by_state(
        self,
        force_download: bool = False,
    ) -> pd.DataFrame:
        """
        Calculate vehicle ownership statistics by state.

        Args:
            force_download: Force re-download of data

        Returns:
            DataFrame with vehicle ownership statistics by state

        Statistics include:
            - Average vehicles per household
            - Zero-vehicle household percentage
            - Multi-vehicle household percentage

        Example:
            >>> nhts = NHTSConnector()
            >>> veh_ownership = nhts.get_vehicle_ownership_by_state()
            >>> print(veh_ownership[['state', 'avg_vehicles', 'zero_veh_pct']])
        """
        # Load household data
        households = self.load_household_data(force_download)

        # Calculate statistics by state
        stats = (
            households.groupby("HHSTATE")
            .agg(
                {
                    "HHVEHCNT": [
                        "mean",
                        lambda x: (x == 0).mean() * 100,
                        lambda x: (x >= 2).mean() * 100,
                    ],
                    "HOUSEID": "count",
                }
            )
            .reset_index()
        )

        stats.columns = ["state", "avg_vehicles", "zero_veh_pct", "multi_veh_pct", "households"]

        # Format state FIPS as 2-digit string
        stats["state"] = stats["state"].astype(str).str.zfill(2)

        # Round percentages
        stats["avg_vehicles"] = stats["avg_vehicles"].round(2)
        stats["zero_veh_pct"] = stats["zero_veh_pct"].round(2)
        stats["multi_veh_pct"] = stats["multi_veh_pct"].round(2)

        # Sort by average vehicles descending
        stats = stats.sort_values("avg_vehicles", ascending=False)

        self.logger.info("Calculated vehicle ownership by state", extra={"states": len(stats)})

        return stats

    @requires_license
    def get_trip_purpose_distribution(
        self,
        state_fips: Optional[str] = None,
        force_download: bool = False,
    ) -> pd.DataFrame:
        """
        Calculate distribution of trip purposes.

        Args:
            state_fips: State FIPS code (None = national)
            force_download: Force re-download of data

        Returns:
            DataFrame with trip purpose distribution

        Example:
            >>> nhts = NHTSConnector()
            >>> purposes = nhts.get_trip_purpose_distribution()
            >>> print(purposes[['purpose', 'trips', 'share_pct']])
        """
        # Load trip data
        trips = self.load_trip_data(force_download)

        # Filter by state if specified
        if state_fips is not None:
            households = self.load_household_data(force_download)
            state_households = households[
                households["HHSTATE"].astype(str).str.zfill(2) == str(state_fips).zfill(2)
            ]
            trips = trips[trips["HOUSEID"].isin(state_households["HOUSEID"])]

        # Calculate purpose distribution
        purpose_counts = trips["WHYTRP1S"].value_counts()
        purpose_dist = pd.DataFrame(
            {
                "purpose": purpose_counts.index,
                "trips": purpose_counts.values,
                "share_pct": (purpose_counts / purpose_counts.sum() * 100).round(2),
            }
        )

        purpose_dist = purpose_dist.sort_values("share_pct", ascending=False)

        self.logger.info(
            "Calculated trip purpose distribution",
            extra={
                "state_fips": state_fips,
                "total_trips": purpose_dist["trips"].sum(),
            },
        )

        return purpose_dist

    def __repr__(self) -> str:
        """String representation of the connector."""
        return (
            f"NHTSConnector("
            f"cache_dir='{self.cache.cache_dir}', "
            f"survey_year='{self.survey_year}', "
            f"connected={self.session is not None})"
        )
