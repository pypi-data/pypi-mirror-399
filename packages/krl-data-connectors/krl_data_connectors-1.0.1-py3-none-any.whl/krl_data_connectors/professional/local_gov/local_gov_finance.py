# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Local Government Finance Connector (D38: Local Government Finance).

Parses Comprehensive Annual Financial Reports (CAFRs) from US municipalities
to extract financial metrics, balance sheets, and fiscal health indicators.

Data Sources:
    - Municipal CAFR PDFs (Comprehensive Annual Financial Reports)
    - Municipal websites and transparency portals
    - Government financial open data APIs

Output Format: JSONL for downstream analytics pipelines

Use Cases:
    - Municipal fiscal health analysis
    - Debt-to-revenue ratio tracking
    - Pension liability assessment
    - Revenue composition analysis
    - Cross-municipality comparisons
"""

import hashlib
import json
import logging
import re
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd

# PDF parsing libraries
try:
    import pdfplumber

    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import PyPDF2

    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

from krl_data_connectors.base_connector import BaseConnector

from ...core import DataTier
from ...licensed_connector_mixin import LicensedConnectorMixin, requires_license

logger = logging.getLogger(__name__)


class LocalGovFinanceConnector(LicensedConnectorMixin, BaseConnector):
    """
    Connector for extracting financial data from municipal CAFRs.

    Supports:
    - PDF parsing of CAFR documents
    - Financial statement extraction (balance sheet, income, cash flow)
    - Municipality metadata extraction
    - Financial ratio calculations
    - Multi-year trend analysis

    Features:
    - JSONL output pipeline
    - Robust PDF text extraction
    - Table detection and extraction
    - Financial data validation
    - Standardized metric mapping
    """

    # Registry name for license validation
    _connector_name = "Local_Gov_Finance"

    """
    Tier Mapping:
    - Tier 1-2: Basic financial metrics, revenue/expenditure totals
    - Tier 3-4: Detailed balance sheets, ratio calculations, trend analysis
    - Tier 5-6: Predictive fiscal health scoring, comparative analytics
    """

    BASE_NAME = "LocalGovFinance"

    # Financial statement patterns
    FINANCIAL_PATTERNS = {
        "balance_sheet": [
            r"Statement\s+of\s+(?:Net\s+)?(?:Financial\s+)?Position",
            r"Balance\s+Sheet",
            r"Government-Wide\s+Statement\s+of\s+Net\s+Position",
        ],
        "income_statement": [
            r"Statement\s+of\s+(?:Activities|Revenues?|Operations?)",
            r"Income\s+Statement",
            r"Government-Wide\s+Statement\s+of\s+Activities",
        ],
        "cash_flow": [
            r"Statement\s+of\s+Cash\s+Flows?",
            r"Cash\s+Flow\s+Statement",
        ],
        "fiscal_year": [
            r"(?:Fiscal\s+Year|FY)\s+(?:Ended?\s+)?(\d{4})",
            r"For\s+the\s+Year\s+Ended?\s+\w+\s+\d{1,2},?\s+(\d{4})",
        ],
    }

    # Financial metric categories
    METRIC_CATEGORIES = {
        "assets": ["cash", "investments", "receivables", "capital_assets"],
        "liabilities": [
            "accounts_payable",
            "bonds_payable",
            "pension_obligations",
            "opeb_liabilities",
        ],
        "revenues": ["taxes", "charges_for_services", "grants", "other_revenues"],
        "expenditures": ["general_government", "public_safety", "public_works", "debt_service"],
    }

    def __init__(
        self,
        output_dir: Optional[str] = None,
        use_pdfplumber: bool = True,
        extract_tables: bool = True,
        validate_financials: bool = True,
        **kwargs,
    ):
        """
        Initialize Local Government Finance Connector.

        Args:
            output_dir: Directory for JSONL output files (default: data/crawl/local_gov_finance)
            use_pdfplumber: Prefer pdfplumber over PyPDF2 for better table extraction
            extract_tables: Extract financial tables from PDFs
            validate_financials: Validate extracted financial data for consistency
            **kwargs: Additional arguments passed to BaseConnector
        """
        super().__init__(**kwargs)

        # Configuration
        self.use_pdfplumber = use_pdfplumber and PDFPLUMBER_AVAILABLE
        self.extract_tables = extract_tables
        self.validate_financials = validate_financials

        # Output directory
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            # Default to data/crawl/local_gov_finance
            base_dir = Path(self.config.get("DATA_DIR", "data"))
            self.output_dir = base_dir / "crawl" / "local_gov_finance"

        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Check library availability
        if not PDFPLUMBER_AVAILABLE and not PYPDF2_AVAILABLE:
            raise ImportError(
                "Neither pdfplumber nor PyPDF2 is installed. "
                "Install with: pip install pdfplumber PyPDF2"
            )

        if use_pdfplumber and not PDFPLUMBER_AVAILABLE:
            logger.warning(
                "pdfplumber not available, falling back to PyPDF2. "
                "Table extraction may be limited. Install with: pip install pdfplumber"
            )
            self.use_pdfplumber = False

        # Cache for parsed documents
        self._parsed_cache: Dict[str, Dict[str, Any]] = {}

        logger.info(
            "LocalGovFinanceConnector initialized",
            extra={
                "output_dir": str(self.output_dir),
                "use_pdfplumber": self.use_pdfplumber,
                "extract_tables": self.extract_tables,
            },
        )

    def _get_api_key(self) -> Optional[str]:
        """
        Get API key from configuration.

        Note: CAFRs are typically publicly available PDFs and do not
        require API authentication. This method returns None.

        Returns:
            None (no API key required)
        """
        return None

    def connect(self) -> bool:
        """
        Establish connection (no-op for file-based connector).

        Returns:
            True (always succeeds for file-based connector)
        """
        logger.info("LocalGovFinanceConnector ready (file-based, no connection required)")
        return True

    def parse_pdf(
        self,
        pdf_path: Union[str, Path],
        extract_text: bool = True,
        extract_tables: bool = True,
    ) -> Dict[str, Any]:
        """
        Parse a CAFR PDF and extract text and tables.

        Args:
            pdf_path: Path to the PDF file
            extract_text: Extract text content from PDF
            extract_tables: Extract tables from PDF (requires pdfplumber)

        Returns:
            Dictionary containing:
                - text: Extracted text content (if extract_text=True)
                - tables: List of extracted tables (if extract_tables=True)
                - num_pages: Number of pages in PDF
                - metadata: PDF metadata (title, author, etc.)

        Raises:
            FileNotFoundError: If PDF file does not exist
            Exception: If PDF parsing fails

        Example:
            >>> connector = LocalGovFinanceConnector()
            >>> result = connector.parse_pdf("city_cafr_2023.pdf")
            >>> print(f"Extracted {result['num_pages']} pages")
            >>> print(f"Found {len(result['tables'])} tables")
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        # Check cache
        cache_key = self._get_pdf_cache_key(pdf_path)
        if cache_key in self._parsed_cache:
            logger.debug(f"Using cached parse for {pdf_path.name}")
            return self._parsed_cache[cache_key]

        logger.info(f"Parsing PDF: {pdf_path.name}")

        result: Dict[str, Any] = {
            "text": "",
            "tables": [],
            "num_pages": 0,
            "metadata": {},
        }

        try:
            if self.use_pdfplumber and extract_tables:
                # Use pdfplumber for better table extraction
                result = self._parse_with_pdfplumber(pdf_path, extract_text, extract_tables)
            else:
                # Fall back to PyPDF2
                result = self._parse_with_pypdf2(pdf_path, extract_text)

            # Cache result
            self._parsed_cache[cache_key] = result

            logger.info(
                f"Successfully parsed PDF: {pdf_path.name}",
                extra={
                    "num_pages": result["num_pages"],
                    "num_tables": len(result["tables"]),
                    "text_length": len(result["text"]),
                },
            )

            return result

        except Exception as e:
            logger.error(f"Failed to parse PDF {pdf_path.name}: {e}", exc_info=True)
            raise

    def _parse_with_pdfplumber(
        self,
        pdf_path: Path,
        extract_text: bool,
        extract_tables: bool,
    ) -> Dict[str, Any]:
        """
        Parse PDF using pdfplumber (better table extraction).

        Args:
            pdf_path: Path to PDF file
            extract_text: Whether to extract text
            extract_tables: Whether to extract tables

        Returns:
            Dictionary with parsed content
        """
        result: Dict[str, Any] = {
            "text": "",
            "tables": [],
            "num_pages": 0,
            "metadata": {},
        }

        with pdfplumber.open(pdf_path) as pdf:
            result["num_pages"] = len(pdf.pages)
            result["metadata"] = pdf.metadata or {}

            all_text = []
            all_tables = []

            for page_num, page in enumerate(pdf.pages, start=1):
                # Extract text
                if extract_text:
                    page_text = page.extract_text()
                    if page_text:
                        all_text.append(page_text)

                # Extract tables
                if extract_tables:
                    tables = page.extract_tables()
                    for table in tables:
                        if table:  # Skip empty tables
                            all_tables.append(
                                {
                                    "page": page_num,
                                    "data": table,
                                }
                            )

            result["text"] = "\n\n".join(all_text)
            result["tables"] = all_tables

        return result

    def _parse_with_pypdf2(
        self,
        pdf_path: Path,
        extract_text: bool,
    ) -> Dict[str, Any]:
        """
        Parse PDF using PyPDF2 (basic text extraction only).

        Args:
            pdf_path: Path to PDF file
            extract_text: Whether to extract text

        Returns:
            Dictionary with parsed content
        """
        result: Dict[str, Any] = {
            "text": "",
            "tables": [],
            "num_pages": 0,
            "metadata": {},
        }

        with open(pdf_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            result["num_pages"] = len(pdf_reader.pages)
            result["metadata"] = pdf_reader.metadata or {}

            if extract_text:
                all_text = []
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        all_text.append(page_text)
                result["text"] = "\n\n".join(all_text)

        logger.warning(
            "PyPDF2 does not support table extraction. "
            "Install pdfplumber for better results: pip install pdfplumber"
        )

        return result

    def _get_pdf_cache_key(self, pdf_path: Path) -> str:
        """Generate cache key for parsed PDF."""
        # Use file path and modification time for cache key
        mtime = pdf_path.stat().st_mtime
        cache_str = f"{pdf_path}:{mtime}"
        return hashlib.md5(cache_str.encode(), usedforsecurity=False).hexdigest()

    def extract_municipality_metadata(self, parsed_pdf: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract municipality metadata from parsed CAFR.

        Args:
            parsed_pdf: Dictionary returned by parse_pdf()

        Returns:
            Dictionary containing:
                - municipality_name: Name of municipality
                - state: State abbreviation
                - fiscal_year: Fiscal year (YYYY)
                - report_date: Date of report
                - population: Population (if available)

        Example:
            >>> connector = LocalGovFinanceConnector()
            >>> parsed = connector.parse_pdf("city_cafr_2023.pdf")
            >>> metadata = connector.extract_municipality_metadata(parsed)
            >>> print(f"{metadata['municipality_name']}, {metadata['state']}")
            City of Springfield, IL
        """
        text = parsed_pdf.get("text", "")
        metadata: Dict[str, Any] = {}

        # Extract fiscal year
        for pattern in self.FINANCIAL_PATTERNS["fiscal_year"]:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                metadata["fiscal_year"] = int(match.group(1))
                break

        # Extract municipality name (usually in first few lines)
        first_lines = text[:1000]  # First ~1000 characters

        # Common patterns for municipality names
        name_patterns = [
            r"(?:City|Town|Village|County|Township)\s+of\s+([\w\s]+)",
            r"([\w\s]+)\s+(?:City|Town|Village|County|Township)",
        ]

        for pattern in name_patterns:
            match = re.search(pattern, first_lines, re.IGNORECASE)
            if match:
                metadata["municipality_name"] = match.group(1).strip()
                break

        # Extract state (look for common state abbreviations)
        state_pattern = r"\b([A-Z]{2})\b"
        state_matches = re.findall(state_pattern, first_lines)
        if state_matches:
            # Filter out common false positives (like "FY", "CA" in "CAFR")
            valid_states = set(
                [
                    "AL",
                    "AK",
                    "AZ",
                    "AR",
                    "CA",
                    "CO",
                    "CT",
                    "DE",
                    "FL",
                    "GA",
                    "HI",
                    "ID",
                    "IL",
                    "IN",
                    "IA",
                    "KS",
                    "KY",
                    "LA",
                    "ME",
                    "MD",
                    "MA",
                    "MI",
                    "MN",
                    "MS",
                    "MO",
                    "MT",
                    "NE",
                    "NV",
                    "NH",
                    "NJ",
                    "NM",
                    "NY",
                    "NC",
                    "ND",
                    "OH",
                    "OK",
                    "OR",
                    "PA",
                    "RI",
                    "SC",
                    "SD",
                    "TN",
                    "TX",
                    "UT",
                    "VT",
                    "VA",
                    "WA",
                    "WV",
                    "WI",
                    "WY",
                ]
            )
            for state in state_matches:
                if state in valid_states:
                    metadata["state"] = state
                    break

        # Extract population (if mentioned)
        pop_pattern = r"population[:\s]+(?:of\s+)?(?:approximately\s+)?([\d,]+)"
        pop_match = re.search(pop_pattern, text, re.IGNORECASE)
        if pop_match:
            pop_str = pop_match.group(1).replace(",", "")
            try:
                metadata["population"] = int(pop_str)
            except ValueError:
                pass

        logger.debug(f"Extracted metadata: {metadata}")
        return metadata

    def extract_financial_data(
        self,
        parsed_pdf: Dict[str, Any],
        statement_type: str = "balance_sheet",
    ) -> Dict[str, Any]:
        """
        Extract financial data from parsed CAFR.

        Args:
            parsed_pdf: Dictionary returned by parse_pdf()
            statement_type: Type of financial statement to extract
                ("balance_sheet", "income_statement", "cash_flow", "all")

        Returns:
            Dictionary containing extracted financial metrics

        Example:
            >>> connector = LocalGovFinanceConnector()
            >>> parsed = connector.parse_pdf("city_cafr_2023.pdf")
            >>> balance_sheet = connector.extract_financial_data(parsed, "balance_sheet")
            >>> print(f"Total Assets: ${balance_sheet['total_assets']:,.0f}")
        """
        text = parsed_pdf.get("text", "")
        tables = parsed_pdf.get("tables", [])

        if statement_type == "all":
            # Extract all statement types
            result = {
                "balance_sheet": self._extract_balance_sheet(text, tables),
                "income_statement": self._extract_income_statement(text, tables),
                "cash_flow": self._extract_cash_flow(text, tables),
            }
            # Add calculated ratios
            result["financial_ratios"] = self._calculate_financial_ratios(result)
            return result
        elif statement_type == "balance_sheet":
            return self._extract_balance_sheet(text, tables)
        elif statement_type == "income_statement":
            return self._extract_income_statement(text, tables)
        elif statement_type == "cash_flow":
            return self._extract_cash_flow(text, tables)
        else:
            logger.warning(f"Unknown statement type: {statement_type}")
            return {}

    def _extract_balance_sheet(self, text: str, tables: List[List[List[str]]]) -> Dict[str, Any]:
        """
        Extract balance sheet data (Statement of Net Position).

        Args:
            text: Extracted PDF text
            tables: Extracted tables from PDF

        Returns:
            Dictionary containing balance sheet metrics
        """
        balance_sheet = {
            "assets": {},
            "liabilities": {},
            "net_position": {},
            "totals": {},
        }

        # Patterns for key balance sheet items
        asset_patterns = {
            "cash_and_equivalents": [
                r"cash\s+and\s+(?:cash\s+)?equivalents[:\s]+([\d,]+)",
                r"cash[:\s]+([\d,]+)",
            ],
            "investments": [
                r"investments[:\s]+([\d,]+)",
                r"marketable\s+securities[:\s]+([\d,]+)",
            ],
            "receivables": [
                r"(?:accounts?\s+)?receivables?[:\s]+([\d,]+)",
                r"taxes?\s+receivable[:\s]+([\d,]+)",
            ],
            "capital_assets": [
                r"capital\s+assets[:\s]+([\d,]+)",
                r"property,?\s+plant,?\s+(?:and\s+)?equipment[:\s]+([\d,]+)",
                r"net\s+capital\s+assets[:\s]+([\d,]+)",
            ],
            "total_assets": [
                r"total\s+assets[:\s]+([\d,]+)",
                r"total\s+current\s+assets[:\s]+([\d,]+)",
            ],
        }

        liability_patterns = {
            "accounts_payable": [
                r"accounts?\s+payable[:\s]+([\d,]+)",
            ],
            "bonds_payable": [
                r"bonds?\s+payable[:\s]+([\d,]+)",
                r"long[- ]term\s+debt[:\s]+([\d,]+)",
            ],
            "pension_obligations": [
                r"(?:net\s+)?pension\s+(?:liability|obligation)[:\s]+([\d,]+)",
            ],
            "opeb_liabilities": [
                r"(?:OPEB|other\s+post[- ]?employment\s+benefits?)\s+(?:liability|obligation)[:\s]+([\d,]+)",
            ],
            "total_liabilities": [
                r"total\s+liabilities[:\s]+([\d,]+)",
            ],
        }

        net_position_patterns = {
            "net_investment_in_capital_assets": [
                r"net\s+investment\s+in\s+capital\s+assets[:\s]+([\d,]+)",
            ],
            "restricted": [
                r"restricted(?:\s+net\s+position)?[:\s]+([\d,]+)",
            ],
            "unrestricted": [
                r"unrestricted(?:\s+net\s+position)?[:\s]+([\d,]+)",
            ],
            "total_net_position": [
                r"total\s+net\s+(?:position|assets)[:\s]+([\d,]+)",
            ],
        }

        # Extract asset values
        for key, patterns in asset_patterns.items():
            value = self._extract_numeric_value(text, patterns)
            if value is not None:
                balance_sheet["assets"][key] = value

        # Extract liability values
        for key, patterns in liability_patterns.items():
            value = self._extract_numeric_value(text, patterns)
            if value is not None:
                balance_sheet["liabilities"][key] = value

        # Extract net position values
        for key, patterns in net_position_patterns.items():
            value = self._extract_numeric_value(text, patterns)
            if value is not None:
                balance_sheet["net_position"][key] = value

        # Calculate totals if not directly found
        if "total_assets" not in balance_sheet["assets"] and balance_sheet["assets"]:
            balance_sheet["totals"]["calculated_total_assets"] = sum(
                v for v in balance_sheet["assets"].values() if isinstance(v, (int, float))
            )

        if "total_liabilities" not in balance_sheet["liabilities"] and balance_sheet["liabilities"]:
            balance_sheet["totals"]["calculated_total_liabilities"] = sum(
                v for v in balance_sheet["liabilities"].values() if isinstance(v, (int, float))
            )

        logger.info(
            f"Extracted balance sheet with {len(balance_sheet['assets'])} assets, "
            f"{len(balance_sheet['liabilities'])} liabilities"
        )

        return balance_sheet

    def _extract_income_statement(self, text: str, tables: List[List[List[str]]]) -> Dict[str, Any]:
        """
        Extract income statement data (Statement of Activities).

        Args:
            text: Extracted PDF text
            tables: Extracted tables from PDF

        Returns:
            Dictionary containing income statement metrics
        """
        income_statement = {
            "revenues": {},
            "expenses": {},
            "changes": {},
            "totals": {},
        }

        # Patterns for revenue items
        revenue_patterns = {
            "property_taxes": [
                r"property\s+taxes[:\s]+([\d,]+)",
                r"taxes?[:\s]+property[:\s]+([\d,]+)",
            ],
            "sales_taxes": [
                r"sales\s+taxes[:\s]+([\d,]+)",
            ],
            "charges_for_services": [
                r"charges?\s+for\s+services[:\s]+([\d,]+)",
            ],
            "operating_grants": [
                r"operating\s+grants\s+and\s+contributions[:\s]+([\d,]+)",
            ],
            "capital_grants": [
                r"capital\s+grants\s+and\s+contributions[:\s]+([\d,]+)",
            ],
            "total_revenues": [
                r"total\s+(?:program\s+)?revenues[:\s]+([\d,]+)",
                r"total\s+general\s+revenues[:\s]+([\d,]+)",
            ],
        }

        # Patterns for expense items
        expense_patterns = {
            "general_government": [
                r"general\s+government[:\s]+([\d,]+)",
            ],
            "public_safety": [
                r"public\s+safety[:\s]+([\d,]+)",
            ],
            "public_works": [
                r"public\s+works[:\s]+([\d,]+)",
            ],
            "health_and_welfare": [
                r"(?:health\s+and\s+)?(?:human\s+)?welfare[:\s]+([\d,]+)",
            ],
            "culture_and_recreation": [
                r"culture\s+and\s+recreation[:\s]+([\d,]+)",
            ],
            "debt_service": [
                r"(?:interest\s+on\s+)?(?:long[- ]term\s+)?debt\s+service[:\s]+([\d,]+)",
            ],
            "total_expenses": [
                r"total\s+(?:program\s+)?expenses[:\s]+([\d,]+)",
            ],
        }

        # Patterns for changes in net position
        change_patterns = {
            "change_in_net_position": [
                r"change\s+in\s+net\s+(?:position|assets)[:\s]+([\d,\-\(\)]+)",
                r"(?:increase|decrease)\s+in\s+net\s+position[:\s]+([\d,\-\(\)]+)",
            ],
        }

        # Extract revenue values
        for key, patterns in revenue_patterns.items():
            value = self._extract_numeric_value(text, patterns)
            if value is not None:
                income_statement["revenues"][key] = value

        # Extract expense values
        for key, patterns in expense_patterns.items():
            value = self._extract_numeric_value(text, patterns)
            if value is not None:
                income_statement["expenses"][key] = value

        # Extract change in net position
        for key, patterns in change_patterns.items():
            value = self._extract_numeric_value(text, patterns, allow_negative=True)
            if value is not None:
                income_statement["changes"][key] = value

        # Calculate totals if not directly found
        if "total_revenues" not in income_statement["revenues"] and income_statement["revenues"]:
            income_statement["totals"]["calculated_total_revenues"] = sum(
                v for v in income_statement["revenues"].values() if isinstance(v, (int, float))
            )

        if "total_expenses" not in income_statement["expenses"] and income_statement["expenses"]:
            income_statement["totals"]["calculated_total_expenses"] = sum(
                v for v in income_statement["expenses"].values() if isinstance(v, (int, float))
            )

        logger.info(
            f"Extracted income statement with {len(income_statement['revenues'])} revenues, "
            f"{len(income_statement['expenses'])} expenses"
        )

        return income_statement

    def _extract_cash_flow(self, text: str, tables: List[List[List[str]]]) -> Dict[str, Any]:
        """
        Extract cash flow statement data.

        Args:
            text: Extracted PDF text
            tables: Extracted tables from PDF

        Returns:
            Dictionary containing cash flow metrics
        """
        cash_flow = {
            "operating_activities": {},
            "investing_activities": {},
            "financing_activities": {},
            "totals": {},
        }

        # Patterns for operating activities
        operating_patterns = {
            "cash_from_operations": [
                r"(?:net\s+)?cash\s+(?:provided\s+by|from)\s+operating\s+activities[:\s]+([\d,\-\(\)]+)",
            ],
            "cash_from_customers": [
                r"cash\s+(?:received\s+)?from\s+customers[:\s]+([\d,]+)",
            ],
            "cash_to_suppliers": [
                r"cash\s+(?:paid\s+)?to\s+suppliers[:\s]+([\d,\-\(\)]+)",
            ],
            "cash_to_employees": [
                r"cash\s+(?:paid\s+)?(?:to|for)\s+employees[:\s]+([\d,\-\(\)]+)",
            ],
        }

        # Patterns for investing activities
        investing_patterns = {
            "cash_from_investing": [
                r"(?:net\s+)?cash\s+(?:provided\s+by|from)\s+investing\s+activities[:\s]+([\d,\-\(\)]+)",
            ],
            "capital_asset_purchases": [
                r"purchase\s+of\s+capital\s+assets[:\s]+([\d,\-\(\)]+)",
                r"acquisition\s+of\s+(?:property|equipment|capital\s+assets)[:\s]+([\d,\-\(\)]+)",
            ],
            "investment_purchases": [
                r"purchase\s+of\s+investments[:\s]+([\d,\-\(\)]+)",
            ],
        }

        # Patterns for financing activities
        financing_patterns = {
            "cash_from_financing": [
                r"(?:net\s+)?cash\s+(?:provided\s+by|from)\s+financing\s+activities[:\s]+([\d,\-\(\)]+)",
            ],
            "bond_proceeds": [
                r"(?:proceeds\s+from\s+)?(?:issuance\s+of\s+)?bonds?\s+(?:issued|proceeds)[:\s]+([\d,]+)",
            ],
            "debt_payments": [
                r"(?:principal\s+)?(?:payments?\s+on|retirement\s+of)\s+(?:long[- ]term\s+)?debt[:\s]+([\d,\-\(\)]+)",
            ],
        }

        # Extract operating activities
        for key, patterns in operating_patterns.items():
            value = self._extract_numeric_value(text, patterns, allow_negative=True)
            if value is not None:
                cash_flow["operating_activities"][key] = value

        # Extract investing activities
        for key, patterns in investing_patterns.items():
            value = self._extract_numeric_value(text, patterns, allow_negative=True)
            if value is not None:
                cash_flow["investing_activities"][key] = value

        # Extract financing activities
        for key, patterns in financing_patterns.items():
            value = self._extract_numeric_value(text, patterns, allow_negative=True)
            if value is not None:
                cash_flow["financing_activities"][key] = value

        # Calculate net change in cash
        operating = cash_flow["operating_activities"].get("cash_from_operations", 0)
        investing = cash_flow["investing_activities"].get("cash_from_investing", 0)
        financing = cash_flow["financing_activities"].get("cash_from_financing", 0)

        if operating or investing or financing:
            cash_flow["totals"]["net_change_in_cash"] = operating + investing + financing

        logger.info(
            f"Extracted cash flow with {len(cash_flow['operating_activities'])} operating, "
            f"{len(cash_flow['investing_activities'])} investing, "
            f"{len(cash_flow['financing_activities'])} financing items"
        )

        return cash_flow

    def _extract_numeric_value(
        self,
        text: str,
        patterns: List[str],
        allow_negative: bool = False,
    ) -> Optional[float]:
        """
        Extract numeric value from text using regex patterns.

        Args:
            text: Text to search
            patterns: List of regex patterns to try
            allow_negative: Whether to allow negative values (parentheses or minus)

        Returns:
            Extracted numeric value or None
        """
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value_str = match.group(1)

                # Handle negative values (parentheses or minus sign)
                is_negative = False
                if allow_negative:
                    if value_str.startswith("(") and value_str.endswith(")"):
                        value_str = value_str[1:-1]
                        is_negative = True
                    elif value_str.startswith("-"):
                        value_str = value_str[1:]
                        is_negative = True

                # Remove commas and convert to float
                value_str = value_str.replace(",", "")
                try:
                    value = float(value_str)
                    if is_negative:
                        value = -value
                    return value
                except ValueError:
                    continue

        return None

    def _calculate_financial_ratios(self, financial_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate key financial ratios from extracted data.

        Args:
            financial_data: Dictionary containing balance sheet, income statement, etc.

        Returns:
            Dictionary of calculated financial ratios
        """
        ratios = {}

        balance_sheet = financial_data.get("balance_sheet", {})
        income_statement = financial_data.get("income_statement", {})

        # Get key values for ratio calculations
        total_assets = balance_sheet.get("assets", {}).get("total_assets") or balance_sheet.get(
            "totals", {}
        ).get("calculated_total_assets")

        total_liabilities = balance_sheet.get("liabilities", {}).get(
            "total_liabilities"
        ) or balance_sheet.get("totals", {}).get("calculated_total_liabilities")

        total_net_position = balance_sheet.get("net_position", {}).get("total_net_position")

        cash = balance_sheet.get("assets", {}).get("cash_and_equivalents")
        current_liabilities = balance_sheet.get("liabilities", {}).get("accounts_payable", 0)

        total_revenues = income_statement.get("revenues", {}).get(
            "total_revenues"
        ) or income_statement.get("totals", {}).get("calculated_total_revenues")

        total_expenses = income_statement.get("expenses", {}).get(
            "total_expenses"
        ) or income_statement.get("totals", {}).get("calculated_total_expenses")

        debt = balance_sheet.get("liabilities", {}).get("bonds_payable", 0)

        # Calculate debt-to-equity ratio
        if total_net_position and total_net_position > 0:
            ratios["debt_to_equity"] = (
                total_liabilities / total_net_position if total_liabilities else 0
            )

        # Calculate debt-to-assets ratio
        if total_assets and total_assets > 0:
            ratios["debt_to_assets"] = total_liabilities / total_assets if total_liabilities else 0

        # Calculate current ratio (simplified - would need current assets/liabilities)
        if cash and current_liabilities and current_liabilities > 0:
            ratios["cash_ratio"] = cash / current_liabilities

        # Calculate operating margin
        if total_revenues and total_revenues > 0:
            net_operating_result = (total_revenues or 0) - (total_expenses or 0)
            ratios["operating_margin"] = net_operating_result / total_revenues

        # Calculate debt service coverage (simplified)
        if debt and total_revenues and total_revenues > 0:
            ratios["debt_to_revenue"] = debt / total_revenues

        logger.info(f"Calculated {len(ratios)} financial ratios")
        return ratios

    def save_to_jsonl(
        self,
        data: Dict[str, Any],
        output_file: Optional[Union[str, Path]] = None,
    ) -> Path:
        """
        Save extracted data to JSONL format.

        Args:
            data: Dictionary of extracted data
            output_file: Optional output file path (default: auto-generated)

        Returns:
            Path to saved JSONL file

        Example:
            >>> connector = LocalGovFinanceConnector()
            >>> parsed = connector.parse_pdf("city_cafr_2023.pdf")
            >>> metadata = connector.extract_municipality_metadata(parsed)
            >>> output_path = connector.save_to_jsonl(metadata)
            >>> print(f"Saved to {output_path}")
        """
        if output_file is None:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            municipality = data.get("municipality_name", "unknown").replace(" ", "_")
            output_file = self.output_dir / f"{municipality}_{timestamp}.jsonl"
        else:
            output_file = Path(output_file)

        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Write JSONL
        with open(output_file, "w") as f:
            json.dump(data, f)
            f.write("\n")

        logger.info(f"Saved data to {output_file}")
        return output_file

    def fetch(self, **kwargs) -> pd.DataFrame:
        """
        Fetch financial data (placeholder for BaseConnector interface).

        For file-based connectors, use parse_pdf() and extract_* methods directly.

        Returns:
            Empty DataFrame
        """
        logger.warning(
            "fetch() not applicable for file-based connector. "
            "Use parse_pdf() and extract_* methods instead."
        )
        return pd.DataFrame()

    def validate_financial_data(
        self,
        financial_data: Dict[str, Any],
        check_balance: bool = True,
        check_completeness: bool = True,
        check_reasonableness: bool = True,
    ) -> Dict[str, Any]:
        """
        Validate extracted financial data for consistency and completeness.

        Args:
            financial_data: Dictionary with extracted financial data
            check_balance: Verify accounting equation (assets = liabilities + equity)
            check_completeness: Check for presence of required fields
            check_reasonableness: Flag suspicious values

        Returns:
            Dictionary with validation results:
                - is_valid: Overall validity (bool)
                - balance_valid: Accounting equation balanced (bool)
                - completeness_score: Percentage of expected fields present (float)
                - warnings: List of validation warnings
                - errors: List of validation errors

        Example:
            >>> result = connector.extract_financial_data(parsed, "all")
            >>> validation = connector.validate_financial_data(result)
            >>> if not validation["is_valid"]:
            ...     print(f"Warnings: {validation['warnings']}")
        """
        validation = {
            "is_valid": True,
            "balance_valid": None,
            "completeness_score": 0.0,
            "warnings": [],
            "errors": [],
        }

        # Extract balance sheet data if "all" statement type
        balance_sheet = financial_data
        if "balance_sheet" in financial_data:
            balance_sheet = financial_data["balance_sheet"]

        # Check accounting equation balance
        if check_balance and "assets" in balance_sheet:
            total_assets = balance_sheet.get("assets", {}).get("total_assets")
            total_liabilities = balance_sheet.get("liabilities", {}).get("total_liabilities")
            total_net_position = balance_sheet.get("net_position", {}).get("total_net_position")

            if total_assets and total_liabilities and total_net_position:
                expected_assets = total_liabilities + total_net_position
                difference = abs(total_assets - expected_assets)
                tolerance = total_assets * 0.01  # 1% tolerance

                if difference > tolerance:
                    validation["balance_valid"] = False
                    validation["errors"].append(
                        f"Accounting equation imbalanced: Assets ({total_assets:,.0f}) != "
                        f"Liabilities ({total_liabilities:,.0f}) + Net Position ({total_net_position:,.0f}). "
                        f"Difference: {difference:,.0f}"
                    )
                    validation["is_valid"] = False
                else:
                    validation["balance_valid"] = True

        # Check completeness
        if check_completeness:
            expected_fields = {
                "balance_sheet": [
                    "assets.cash_and_equivalents",
                    "assets.total_assets",
                    "liabilities.total_liabilities",
                    "net_position.total_net_position",
                ],
                "income_statement": [
                    "revenues.total_revenues",
                    "expenses.total_expenses",
                    "changes.change_in_net_position",
                ],
                "cash_flow": [
                    "operating_activities.cash_from_operations",
                    "totals.net_change_in_cash",
                ],
            }

            found_fields = 0
            total_fields = 0

            for statement_type, fields in expected_fields.items():
                # Handle both direct extraction and "all" type
                data_to_check = financial_data
                if statement_type in financial_data:
                    data_to_check = financial_data[statement_type]

                for field_path in fields:
                    total_fields += 1
                    parts = field_path.split(".")
                    current = data_to_check

                    try:
                        for part in parts:
                            current = current[part]
                        if current is not None:
                            found_fields += 1
                    except (KeyError, TypeError):
                        pass

            if total_fields > 0:
                validation["completeness_score"] = (found_fields / total_fields) * 100

                if validation["completeness_score"] < 50:
                    validation["warnings"].append(
                        f"Low completeness score: {validation['completeness_score']:.1f}%. "
                        f"Only {found_fields}/{total_fields} expected fields found."
                    )

        # Check reasonableness
        if check_reasonableness:
            # Check for negative assets (usually invalid)
            if "assets" in balance_sheet:
                for key, value in balance_sheet.get("assets", {}).items():
                    if value and value < 0 and key != "calculated_total_assets":
                        validation["warnings"].append(f"Negative asset value: {key} = {value:,.0f}")

            # Check for extremely high debt ratios
            if "financial_ratios" in financial_data:
                ratios = financial_data["financial_ratios"]

                debt_to_equity = ratios.get("debt_to_equity")
                if debt_to_equity and debt_to_equity > 5.0:
                    validation["warnings"].append(
                        f"Very high debt-to-equity ratio: {debt_to_equity:.2f}"
                    )

                debt_to_assets = ratios.get("debt_to_assets")
                if debt_to_assets and debt_to_assets > 0.9:
                    validation["warnings"].append(
                        f"Very high debt-to-assets ratio: {debt_to_assets:.2f}"
                    )

            # Check cash flow sanity
            if "cash_flow" in financial_data:
                cash_flow = financial_data["cash_flow"]
                net_change = cash_flow.get("totals", {}).get("net_change_in_cash")

                if net_change and abs(net_change) > 1e12:  # > $1 trillion
                    validation["warnings"].append(
                        f"Unusually large cash flow change: {net_change:,.0f}"
                    )

        return validation
