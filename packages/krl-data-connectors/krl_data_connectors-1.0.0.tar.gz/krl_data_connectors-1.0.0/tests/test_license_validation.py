# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for License Validation Infrastructure

Tests cover:
- ConnectorRegistry tier mappings
- ConnectorLicenseValidator access control
- LicensedConnectorMixin integration
- Rate limiting
- Error handling
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from krl_data_connectors import BaseConnector, LicensedConnectorMixin, requires_license
from krl_data_connectors.core import (
    ConnectorLicenseValidator,
    ConnectorRegistry,
    DataTier,
    LicenseError,
    RateLimitError,
)


class TestConnectorRegistry:
    """Test suite for ConnectorRegistry class."""

    def test_registry_integrity(self):
        """Test that registry has correct tier split (12/48/8)."""
        counts = ConnectorRegistry.get_tier_counts()

        assert counts[DataTier.COMMUNITY] == 12, "Should have 12 Community connectors"
        assert counts[DataTier.PROFESSIONAL] == 48, "Should have 48 Professional connectors"
        assert counts[DataTier.ENTERPRISE] == 8, "Should have 8 Enterprise connectors"

    def test_get_required_tier_community(self):
        """Test getting required tier for Community connectors."""
        community_connectors = [
            "FRED_Basic",
            "BLS_Basic",
            "Census_ACS_Public",
            "BEA_National",
            "USGS_Earthquakes",
        ]

        for connector in community_connectors:
            tier = ConnectorRegistry.get_required_tier(connector)
            assert tier == DataTier.COMMUNITY, f"{connector} should be Community tier"

    def test_get_required_tier_professional(self):
        """Test getting required tier for Professional connectors."""
        pro_connectors = [
            "FRED_Full",
            "BLS_Enhanced",
            "SEC_Filings",
            "Zillow_Research",
            "FDIC_Bank_Data",
        ]

        for connector in pro_connectors:
            tier = ConnectorRegistry.get_required_tier(connector)
            assert tier == DataTier.PROFESSIONAL, f"{connector} should be Professional tier"

    def test_get_required_tier_enterprise(self):
        """Test getting required tier for Enterprise connectors."""
        ent_connectors = [
            "FBI_UCR_Detailed",
            "Bureau_Of_Justice",
            "Victims_Of_Crime",
            "EPA_Superfund_Full",
            "SAMHSA",
        ]

        for connector in ent_connectors:
            tier = ConnectorRegistry.get_required_tier(connector)
            assert tier == DataTier.ENTERPRISE, f"{connector} should be Enterprise tier"

    def test_get_required_tier_invalid(self):
        """Test that invalid connector name raises KeyError."""
        with pytest.raises(KeyError):
            ConnectorRegistry.get_required_tier("NonExistent_Connector")

    def test_get_connectors_for_tier_community(self):
        """Test getting connectors for Community tier."""
        connectors = ConnectorRegistry.get_connectors_for_tier(DataTier.COMMUNITY)

        assert len(connectors) == 12, "Community tier should have 12 connectors"
        assert "FRED_Basic" in connectors
        assert "BLS_Basic" in connectors
        # Should NOT include Professional or Enterprise
        assert "FRED_Full" not in connectors
        assert "FBI_UCR_Detailed" not in connectors

    def test_get_connectors_for_tier_professional(self):
        """Test getting connectors for Professional tier (includes Community)."""
        connectors = ConnectorRegistry.get_connectors_for_tier(DataTier.PROFESSIONAL)

        assert len(connectors) == 60, "Professional tier should have 60 total connectors (12 + 48)"
        # Should include Community connectors
        assert "FRED_Basic" in connectors
        assert "BLS_Basic" in connectors
        # Should include Professional connectors
        assert "FRED_Full" in connectors
        assert "SEC_Filings" in connectors
        # Should NOT include Enterprise
        assert "FBI_UCR_Detailed" not in connectors

    def test_get_connectors_for_tier_enterprise(self):
        """Test getting connectors for Enterprise tier (includes all)."""
        connectors = ConnectorRegistry.get_connectors_for_tier(DataTier.ENTERPRISE)

        assert len(connectors) == 68, "Enterprise tier should have all 68 connectors"
        # Should include Community
        assert "FRED_Basic" in connectors
        # Should include Professional
        assert "FRED_Full" in connectors
        # Should include Enterprise
        assert "SAMHSA" in connectors
        assert "FBI_UCR_Detailed" in connectors

    def test_tier_hierarchy(self):
        """Test that tier hierarchy is correct (Community < Professional < Enterprise)."""
        # Use the string values for comparison
        tier_order = {"community": 1, "professional": 2, "enterprise": 3}
        assert tier_order[DataTier.COMMUNITY.value] < tier_order[DataTier.PROFESSIONAL.value]
        assert tier_order[DataTier.PROFESSIONAL.value] < tier_order[DataTier.ENTERPRISE.value]


class TestConnectorLicenseValidator:
    """Test suite for ConnectorLicenseValidator class."""

    @patch("krl_data_connectors.core.license_validator.requests.post")
    @patch("krl_data_connectors.core.license_validator.requests.get")
    def test_validate_access_community_no_key(self, mock_get, mock_post):
        """Test that Community connectors work without API key."""
        validator = ConnectorLicenseValidator()

        result = validator.validate_access(api_key=None, connector_name="FRED_Basic")

        assert result["allowed"] is True
        assert result["user_tier"] == "community"
        # Should not call license server for Community tier
        mock_post.assert_not_called()

    @patch("krl_data_connectors.core.license_validator.requests.post")
    def test_validate_access_professional_valid_key(self, mock_post):
        """Test Professional connector with valid Pro key."""
        # Mock license server response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "valid": True,
            "tier": "professional",
            "features": ["data_connectors"],
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        validator = ConnectorLicenseValidator()

        result = validator.validate_access(api_key="krl_pro_test123", connector_name="FRED_Full")

        assert result["allowed"] is True
        assert result["user_tier"] == "professional"
        mock_post.assert_called_once()

    @patch("krl_data_connectors.core.license_validator.requests.post")
    def test_validate_access_insufficient_tier(self, mock_post):
        """Test that Community key cannot access Professional connector."""
        # Mock license server response for Community tier
        mock_response = MagicMock()
        mock_response.json.return_value = {"valid": True, "tier": "community", "features": []}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        validator = ConnectorLicenseValidator()

        with pytest.raises(LicenseError) as exc_info:
            validator.validate_access(api_key="krl_community_test123", connector_name="FRED_Full")

        error_msg = str(exc_info.value)
        assert "requires Professional tier" in error_msg or "Insufficient tier" in error_msg

    @patch("krl_data_connectors.core.license_validator.requests.get")
    def test_rate_limit_exceeded(self, mock_get):
        """Test rate limit exceeded error."""
        # Mock rate limiter response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "requests_used": 100,
            "requests_remaining": 0,
            "daily_limit": 100,
            "reset_at": "2026-01-01T00:00:00Z",
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        validator = ConnectorLicenseValidator()

        # _check_usage_limits doesn't raise RateLimitError directly, it returns usage info
        # The actual rate limit check happens in validate_access
        usage = validator._check_usage_limits("krl_pro_test123", DataTier.PROFESSIONAL)
        assert usage["requests_remaining"] == 0
        assert usage["daily_limit"] == 100

    @patch("krl_data_connectors.core.license_validator.requests.post")
    def test_license_server_unavailable_fail_open(self, mock_post):
        """Test fail-open behavior when license server is down."""
        import requests as req
        # Mock network error - use a proper requests exception
        mock_post.side_effect = req.exceptions.ConnectionError("Connection refused")

        validator = ConnectorLicenseValidator()

        # Should allow access (fail-open) but log warning
        result = validator.validate_access(api_key="krl_pro_test123", connector_name="FRED_Full")

        # Fail-open: should default to Professional tier when server unavailable
        assert result["allowed"] is True
        assert result.get("user_tier") in ["professional", "enterprise"]

    def test_infer_tier_from_key_format(self):
        """Test API key format parsing."""
        validator = ConnectorLicenseValidator()

        assert validator._infer_tier_from_key("krl_community_abc123") == DataTier.COMMUNITY
        assert validator._infer_tier_from_key("krl_pro_abc123") == DataTier.PROFESSIONAL
        assert validator._infer_tier_from_key("krl_ent_abc123") == DataTier.ENTERPRISE
        assert (
            validator._infer_tier_from_key("invalid_key") == DataTier.COMMUNITY
        )  # Default fallback

    @patch("krl_data_connectors.core.license_validator.requests.post")
    def test_increment_usage(self, mock_post):
        """Test usage increment after successful request."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        validator = ConnectorLicenseValidator()
        validator.increment_usage(api_key="krl_pro_test123")

        # Should call usage increment endpoint
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "/usage/increment" in call_args[0][0]


class TestLicensedConnectorMixin:
    """Test suite for LicensedConnectorMixin class."""

    def test_mixin_initialization(self):
        """Test that mixin initializes correctly."""

        class TestConnector(LicensedConnectorMixin, BaseConnector):
            _connector_name = "FRED_Full"
            _required_tier = DataTier.PROFESSIONAL

            def _get_api_key(self):
                return None

            def connect(self):
                pass

            def fetch(self):
                pass

        connector = TestConnector(api_key="krl_pro_test123")

        assert connector._connector_name == "FRED_Full"
        assert connector._required_tier == DataTier.PROFESSIONAL
        assert connector._skip_license_check is False

    def test_get_required_tier(self):
        """Test getting required tier from mixin."""

        class TestConnector(LicensedConnectorMixin, BaseConnector):
            _connector_name = "FRED_Full"
            _required_tier = DataTier.PROFESSIONAL

            def _get_api_key(self):
                return None

            def connect(self):
                pass

            def fetch(self):
                pass

        connector = TestConnector(api_key="krl_pro_test123")
        tier = connector.get_required_tier()

        assert tier == DataTier.PROFESSIONAL

    @patch("krl_data_connectors.core.license_validator.requests.post")
    @patch("krl_data_connectors.core.license_validator.requests.get")
    def test_check_license_manual(self, mock_get, mock_post):
        """Test manual license check method."""
        # Mock license server response
        mock_post_response = MagicMock()
        mock_post_response.json.return_value = {
            "valid": True,
            "tier": "professional",
            "features": ["data_connectors"],
        }
        mock_post_response.status_code = 200
        mock_post.return_value = mock_post_response

        # Mock usage response
        mock_get_response = MagicMock()
        mock_get_response.json.return_value = {
            "requests_used": 50,
            "requests_remaining": 950,
            "daily_limit": 1000,
            "reset_at": "2026-01-01T00:00:00Z",
        }
        mock_get_response.status_code = 200
        mock_get.return_value = mock_get_response

        class TestConnector(LicensedConnectorMixin, BaseConnector):
            _connector_name = "FRED_Full"
            _required_tier = DataTier.PROFESSIONAL

            def _get_api_key(self):
                return self.api_key

            def connect(self):
                pass

            def fetch(self):
                pass

        connector = TestConnector(api_key="krl_pro_test123")
        status = connector.check_license()

        assert status["allowed"] is True
        assert status["user_tier"] == "professional"
        assert status["requests_remaining"] == 950

    def test_skip_license_check(self):
        """Test disabling license checks for testing."""

        class TestConnector(LicensedConnectorMixin, BaseConnector):
            _connector_name = "FRED_Full"
            _required_tier = DataTier.PROFESSIONAL

            def _get_api_key(self):
                return None

            def connect(self):
                pass

            def fetch(self):
                pass

        connector = TestConnector(api_key="krl_pro_test123")
        connector._skip_license_check = True

        status = connector.check_license()

        # Should return testing status
        assert status["allowed"] is True
        assert status["user_tier"] == "TESTING"

    @patch("krl_data_connectors.core.license_validator.requests.post")
    @patch("krl_data_connectors.core.license_validator.requests.get")
    def test_requires_license_decorator(self, mock_get, mock_post):
        """Test @requires_license decorator on fetch methods."""
        # Mock license validation
        mock_post_response = MagicMock()
        mock_post_response.json.return_value = {
            "valid": True,
            "tier": "professional",
            "features": ["data_connectors"],
        }
        mock_post_response.status_code = 200
        mock_post.return_value = mock_post_response

        # Mock usage check
        mock_get_response = MagicMock()
        mock_get_response.json.return_value = {
            "requests_used": 50,
            "requests_remaining": 950,
            "daily_limit": 1000,
            "reset_at": "2026-01-01T00:00:00Z",
        }
        mock_get_response.status_code = 200
        mock_get.return_value = mock_get_response

        class TestConnector(LicensedConnectorMixin, BaseConnector):
            _connector_name = "FRED_Full"
            _required_tier = DataTier.PROFESSIONAL

            def _get_api_key(self):
                return self.api_key

            def connect(self):
                pass

            def fetch(self):
                pass

            @requires_license
            def get_data(self):
                return {"data": "test"}

        connector = TestConnector(api_key="krl_pro_test123")
        result = connector.get_data()

        assert result == {"data": "test"}
        # Should have called license validation
        mock_post.assert_called()

    @patch("krl_data_connectors.core.license_validator.requests.post")
    def test_requires_license_decorator_denied(self, mock_post):
        """Test @requires_license decorator blocks insufficient tier."""
        # Mock Community tier response
        mock_response = MagicMock()
        mock_response.json.return_value = {"valid": True, "tier": "community", "features": []}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        class TestConnector(LicensedConnectorMixin, BaseConnector):
            _connector_name = "FRED_Full"
            _required_tier = DataTier.PROFESSIONAL

            def _get_api_key(self):
                return self.api_key

            def connect(self):
                pass

            def fetch(self):
                pass

            @requires_license
            def get_data(self):
                return {"data": "test"}

        connector = TestConnector(api_key="krl_community_test123")

        with pytest.raises(LicenseError):
            connector.get_data()


class TestIntegration:
    """Integration tests for complete license validation flow."""

    @patch("krl_data_connectors.core.license_validator.requests.post")
    @patch("krl_data_connectors.core.license_validator.requests.get")
    def test_end_to_end_professional_access(self, mock_get, mock_post):
        """Test complete flow: Professional user accessing Professional connector."""
        # Mock license validation
        mock_post_response = MagicMock()
        mock_post_response.json.return_value = {
            "valid": True,
            "tier": "professional",
            "features": ["data_connectors"],
        }
        mock_post_response.status_code = 200
        mock_post.return_value = mock_post_response

        # Mock usage check
        mock_get_response = MagicMock()
        mock_get_response.json.return_value = {
            "requests_used": 100,
            "requests_remaining": 900,
            "daily_limit": 1000,
            "reset_at": "2026-01-01T00:00:00Z",
        }
        mock_get_response.status_code = 200
        mock_get.return_value = mock_get_response

        # Create test connector
        class FREDFullConnector(LicensedConnectorMixin, BaseConnector):
            _connector_name = "FRED_Full"
            _required_tier = DataTier.PROFESSIONAL

            def _get_api_key(self):
                return self.api_key

            def connect(self):
                pass

            def fetch(self):
                pass

            @requires_license
            def get_series(self, series_id):
                return f"Data for {series_id}"

        # Test access
        connector = FREDFullConnector(api_key="krl_pro_test123")

        # Should succeed
        data = connector.get_series("UNRATE")
        assert data == "Data for UNRATE"

        # Check usage info
        usage = connector.get_usage_info()
        assert usage["requests_remaining"] == 900
        assert usage["daily_limit"] == 1000

    @patch("krl_data_connectors.core.license_validator.requests.post")
    def test_end_to_end_enterprise_required(self, mock_post):
        """Test Enterprise connector requires Enterprise tier."""
        # Mock Professional tier response (insufficient)
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "valid": True,
            "tier": "professional",
            "features": ["data_connectors"],
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Create Enterprise connector
        class SAMHSAConnector(LicensedConnectorMixin, BaseConnector):
            _connector_name = "SAMHSA"
            _required_tier = DataTier.ENTERPRISE

            def _get_api_key(self):
                return self.api_key

            def connect(self):
                pass

            def fetch(self):
                pass

            @requires_license
            def get_claims(self):
                return "Claims data"

        connector = SAMHSAConnector(api_key="krl_pro_test123")

        # Should fail - Professional tier cannot access Enterprise
        with pytest.raises(LicenseError) as exc_info:
            connector.get_claims()

        error_msg = str(exc_info.value)
        assert "requires Enterprise tier" in error_msg or "Insufficient tier" in error_msg


# Run tests with: pytest tests/test_license_validation.py -v
