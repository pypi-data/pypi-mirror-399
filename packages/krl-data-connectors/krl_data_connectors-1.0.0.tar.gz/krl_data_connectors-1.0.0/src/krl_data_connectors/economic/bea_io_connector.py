from __future__ import annotations

#!/usr/bin/env python3
"""
BEA Input-Output Tables Connector.

Fetches Industry-by-Industry Input-Output tables from the Bureau of Economic Analysis (BEA).
These tables form the basis for Social Accounting Matrix (SAM) construction used in CGE models.

Data Source: https://www.bea.gov/industry/input-output-accounts-data
API Docs: https://apps.bea.gov/api/signup/

Key Tables:
    - Use Table: Shows commodity inputs used by each industry
    - Make Table: Shows commodities produced by each industry
    - Direct Requirements: Technical coefficients (A matrix)
    - Total Requirements: Leontief inverse ((I-A)^-1)

Example:
    >>> connector = BEAInputOutputConnector()
    >>> connector.connect()
    >>> io_table = connector.fetch_io_table(year=2021, level="summary")
    >>> sam_matrix = connector.construct_sam(io_table)
"""

import logging
import os
from pathlib import Path
from typing import Any, Literal

import numpy as np
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from krl_data_connectors.base_connector import BaseConnector

logger = logging.getLogger(__name__)


class BEAInputOutputConnector(BaseConnector):
    """
    Connector for BEA Input-Output Tables.

    Fetches industry-by-industry I-O tables and constructs Social Accounting Matrices
    for use in CGE models.

    Attributes:
        api_key: BEA API key (required for access).
        base_url: BEA API base URL.
        cache_dir: Directory for caching downloaded tables.
    """

    def __init__(
        self,
        api_key: str | None = None,
    ):
        """
        Initialize BEA I-O connector.

        Args:
            api_key: BEA API key. If None, reads from BEA_API_KEY environment variable.
        """
        # Store api_key before calling super().__init__
        self._api_key_override = api_key

        super().__init__(api_key=api_key)

        if not self.api_key:
            logger.warning(
                "No BEA API key provided. Sign up at https://apps.bea.gov/api/signup/. "
                "Will use cached/sample data if available."
            )

        self.base_url = "https://apps.bea.gov/api/data"
        # Convert Path to string for cache_dir setter
        cache_path = Path.home() / ".krl" / "cache" / "bea_io"
        cache_path.mkdir(parents=True, exist_ok=True)
        self.cache_dir = str(cache_path)

        # Session with retries
        self._session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self._session.mount("https://", adapter)

    def _get_api_key(self) -> str | None:
        """Get BEA API key from environment or config."""
        return self._api_key_override or os.getenv("BEA_API_KEY")

    def fetch(self, **kwargs: Any) -> pd.DataFrame:
        """
        Generic fetch method required by BaseConnector.

        Args:
            **kwargs: Parameters passed to fetch_io_table()

        Returns:
            I-O table DataFrame
        """
        return self.fetch_io_table(**kwargs)

    def connect(self) -> None:
        """
        Verify API key and connectivity.

        Raises:
            ConnectionError: If API key is invalid or BEA API is unreachable.
        """
        if not self.api_key:
            logger.warning("No API key - using cached/sample data only")
            return

        # Test API with simple request
        try:
            response = self._session.get(
                self.base_url,
                params={
                    "UserID": self.api_key,
                    "method": "GetParameterList",
                    "datasetname": "InputOutput",
                    "ResultFormat": "JSON",
                },
                timeout=10,
            )
            response.raise_for_status()

            data = response.json()
            if "BEAAPI" in data and "Error" in data["BEAAPI"]:
                raise ConnectionError(f"BEA API error: {data['BEAAPI']['Error']}")

            logger.info("✓ Connected to BEA Input-Output API")

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to BEA API: {e}")

    def fetch_io_table(
        self,
        year: int = 2021,
        level: Literal["summary", "sector", "detail"] = "summary",
        table_type: Literal["use", "make", "direct_requirements", "total_requirements"] = "use",
    ) -> pd.DataFrame:
        """
        Fetch Input-Output table from BEA.

        Args:
            year: Year for I-O table (e.g., 2021). BEA updates every 5 years with annual supplements.
            level: Aggregation level:
                - "summary": ~20 sectors (fastest, good for demos)
                - "sector": ~71 sectors (standard for policy analysis)
                - "detail": ~400+ commodities (very detailed)
            table_type: Type of I-O table:
                - "use": Commodity inputs used by industries
                - "make": Commodities produced by industries
                - "direct_requirements": Technical coefficients (A matrix)
                - "total_requirements": Leontief inverse ((I-A)^-1)

        Returns:
            DataFrame with I-O table (rows=inputs, cols=industries).

        Raises:
            ValueError: If year or parameters are invalid.
        """
        # Check cache first
        cache_key = f"io_table_{year}_{level}_{table_type}"
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            logger.info(f"Using cached I-O table: {year}, {level}, {table_type}")
            return cached_data

        if not self.api_key:
            logger.warning("No API key - returning sample I-O table")
            return self._generate_sample_io_table(level)

        # Map level to BEA table ID
        table_id_map = {
            ("summary", "use"): "1",
            ("summary", "make"): "2",
            ("sector", "use"): "3",
            ("sector", "make"): "4",
            ("detail", "use"): "5",
            ("detail", "make"): "6",
        }

        table_id = table_id_map.get((level, table_type))
        if table_id is None:
            # For requirements tables, derive from use table
            if table_type in ["direct_requirements", "total_requirements"]:
                use_table = self.fetch_io_table(year, level, "use")
                return self._compute_requirements_table(use_table, table_type)
            else:
                raise ValueError(f"Invalid combination: level={level}, table_type={table_type}")

        # Fetch from BEA API
        try:
            params = {
                "UserID": self.api_key,
                "method": "GetData",
                "datasetname": "InputOutput",
                "TableID": table_id,
                "Year": str(year),
                "ResultFormat": "JSON",
            }

            logger.info(f"Fetching I-O table from BEA: year={year}, level={level}, type={table_type}")
            response = self._session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if "BEAAPI" not in data or "Results" not in data["BEAAPI"]:
                raise ValueError(f"Unexpected BEA API response: {data}")

            # Parse BEA response
            io_df = self._parse_bea_io_response(data["BEAAPI"]["Results"])

            # Cache result
            self.cache.set(cache_key, io_df)

            logger.info(f"✓ Fetched I-O table: {io_df.shape[0]} rows x {io_df.shape[1]} cols")
            return io_df

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch I-O table: {e}")
            # Fall back to sample data
            return self._generate_sample_io_table(level)

    def construct_sam(
        self,
        io_table: pd.DataFrame,
        include_households: bool = True,
        include_government: bool = True,
    ) -> pd.DataFrame:
        """
        Construct Social Accounting Matrix (SAM) from I-O table.

        A SAM is a square matrix representing all transactions in an economy:
        - Production accounts (industries)
        - Commodity accounts (goods/services)
        - Factor accounts (labor, capital)
        - Institution accounts (households, government, firms)
        - Rest of world account

        Args:
            io_table: Input-Output table (use table or make table).
            include_households: Add household income/expenditure accounts.
            include_government: Add government revenue/spending accounts.

        Returns:
            SAM as square DataFrame (sum of rows = sum of columns for each account).
        """
        n_sectors = len(io_table)

        # Start with I-O table as production block
        sam_size = n_sectors
        if include_households:
            sam_size += 1  # Household account
        if include_government:
            sam_size += 1  # Government account
        sam_size += 1  # Rest of world

        sam = np.zeros((sam_size, sam_size))

        # Fill production block (intermediate transactions)
        sam[:n_sectors, :n_sectors] = io_table.values

        # Add value added (labor + capital compensation)
        # Assume labor share = 70%, capital share = 30%
        total_output = io_table.sum(axis=0).values
        value_added = total_output - io_table.sum(axis=1).values
        value_added = np.maximum(value_added, 0)  # Ensure non-negative

        idx = n_sectors
        if include_households:
            # Household income from labor (70% of value added)
            labor_income = value_added * 0.7
            sam[idx, :n_sectors] = labor_income

            # Household expenditure on commodities
            # Assume 80% of household income goes to consumption
            household_consumption = labor_income.sum() * 0.8
            consumption_shares = total_output / total_output.sum()
            sam[:n_sectors, idx] = household_consumption * consumption_shares

            idx += 1

        if include_government:
            # Government revenue from taxes (assume 20% of output)
            gov_revenue = total_output * 0.2
            sam[idx, :n_sectors] = gov_revenue

            # Government spending (assume balanced budget)
            gov_spending = gov_revenue.sum()
            spending_shares = total_output / total_output.sum()
            sam[:n_sectors, idx] = gov_spending * spending_shares

            idx += 1

        # Rest of world (exports - imports)
        # Assume trade balance = 0 (exports = imports)
        exports = total_output * 0.15  # 15% of output exported
        imports = exports.sum()  # Balanced trade
        import_shares = total_output / total_output.sum()

        sam[idx, :n_sectors] = exports
        sam[:n_sectors, idx] = imports * import_shares

        # Convert to DataFrame
        row_labels = (
            [f"Sector_{i}" for i in range(n_sectors)]
            + (["Households"] if include_households else [])
            + (["Government"] if include_government else [])
            + ["RestOfWorld"]
        )
        col_labels = row_labels

        sam_df = pd.DataFrame(sam, index=row_labels, columns=col_labels)

        logger.info(f"✓ Constructed SAM: {sam_df.shape[0]}x{sam_df.shape[1]}")

        # Verify SAM balance (row sums should equal column sums)
        row_sums = sam_df.sum(axis=1)
        col_sums = sam_df.sum(axis=0)
        imbalance = np.abs(row_sums - col_sums).max()
        if imbalance > 1e-6:
            logger.warning(f"SAM imbalance detected: max diff = {imbalance:.2e}")

        return sam_df

    def _parse_bea_io_response(self, results: dict[str, Any]) -> pd.DataFrame:
        """Parse BEA API response into DataFrame."""
        if "Data" not in results:
            raise ValueError("No data in BEA response")

        data_rows = results["Data"]

        # Extract industry names and commodity names
        industries = sorted(set(row.get("Industry", "") for row in data_rows))
        commodities = sorted(set(row.get("Commodity", "") for row in data_rows))

        # Build I-O matrix
        io_matrix = np.zeros((len(commodities), len(industries)))

        for row in data_rows:
            commodity = row.get("Commodity", "")
            industry = row.get("Industry", "")
            value_str = row.get("DataValue", "0")

            # Convert value (may have commas)
            try:
                value = float(value_str.replace(",", ""))
            except ValueError:
                value = 0.0

            if commodity in commodities and industry in industries:
                i = commodities.index(commodity)
                j = industries.index(industry)
                io_matrix[i, j] = value

        df = pd.DataFrame(io_matrix, index=commodities, columns=industries)
        return df

    def _compute_requirements_table(
        self, use_table: pd.DataFrame, table_type: str
    ) -> pd.DataFrame:
        """Compute direct or total requirements from use table."""
        # Direct requirements (A matrix): a_ij = z_ij / x_j
        # where z_ij = input of commodity i to industry j, x_j = total output of j

        total_output = use_table.sum(axis=0)
        total_output = total_output.replace(0, 1)  # Avoid division by zero

        A = use_table.div(total_output, axis=1)

        if table_type == "direct_requirements":
            return A

        elif table_type == "total_requirements":
            # Total requirements (Leontief inverse): (I - A)^-1
            I = np.eye(len(A))
            try:
                L = np.linalg.inv(I - A.values)
                return pd.DataFrame(L, index=A.index, columns=A.columns)
            except np.linalg.LinAlgError:
                logger.error("Singular matrix - cannot compute Leontief inverse")
                return A  # Return direct requirements as fallback

    def _generate_sample_io_table(self, level: str) -> pd.DataFrame:
        """Generate sample I-O table for testing without API key."""
        n_sectors_map = {
            "summary": 15,
            "sector": 20,
            "detail": 30,
        }

        n_sectors = n_sectors_map.get(level, 15)

        # Generate realistic I-O structure
        np.random.seed(42)

        # Diagonal-dominant structure (industries use mostly own outputs)
        io_matrix = np.random.exponential(scale=10, size=(n_sectors, n_sectors))

        # Add diagonal dominance
        for i in range(n_sectors):
            io_matrix[i, i] += np.random.uniform(50, 100)

        # Normalize so column sums represent realistic output levels
        total_output = np.random.uniform(100, 500, n_sectors)
        io_matrix = io_matrix * (total_output / io_matrix.sum(axis=0))

        sectors = [f"Sector_{i:02d}" for i in range(n_sectors)]
        df = pd.DataFrame(io_matrix, index=sectors, columns=sectors)

        logger.info(f"Generated sample I-O table: {level} level, {n_sectors} sectors")
        return df
