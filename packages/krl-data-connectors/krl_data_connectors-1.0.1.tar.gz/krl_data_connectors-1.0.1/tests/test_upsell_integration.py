"""
Tests for UpsellMessageIntegration - StoryBrand Message Wiring

Tests the integration between:
- Billing UpsellEngine triggers
- StoryBrand personalized messages
- Email delivery (mock)
- In-app notification queue
- A/B test variant assignment
- Conversion tracking

Run with: pytest tests/test_upsell_integration.py -v
"""

import pytest
import asyncio
from datetime import datetime, timedelta, UTC
from decimal import Decimal
from unittest.mock import Mock, AsyncMock, patch

from krl_data_connectors.core.billing import (
    # Core billing
    BillingTier,
    UpsellTriggerType,
    UpsellEvent,
    AdaptiveBillingController,
    BillingBridge,
    create_billing_controller,
    create_billing_bridge,
    # Upsell integration
    DeliveryChannel,
    EmailProvider,
    EmailConfig,
    IntegrationConfig,
    UpsellMessageIntegration,
    InAppNotificationPayload,
    create_upsell_integration,
    wire_integration_to_billing,
    get_template_key_for_event,
    TRIGGER_TO_TEMPLATE_MAP,
    # StoryBrand
    UPSELL_MESSAGES_STORYBRAND,
    personalize_upsell_message,
    # In-app
    NotificationFormat,
    # Awareness
    AwarenessStage,
    detect_awareness_stage,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def sample_upsell_event() -> UpsellEvent:
    """Create a sample upsell event."""
    return UpsellEvent(
        event_id="evt-001",
        trigger_id="trig-usage-80",
        tenant_id="tenant-123",
        timestamp=datetime.now(),
        trigger_type=UpsellTriggerType.USAGE_THRESHOLD,
        source_tier=BillingTier.COMMUNITY,
        target_tier=BillingTier.PRO,
        trigger_context={
            "usage_percentage": 85,
            "metric": "api_calls",
            "limit": 10000,
            "current": 8500,
        },
        message="You're at 85% capacity",
        cta_url="https://krlabs.dev/upgrade",
    )


@pytest.fixture
def sample_customer_data() -> dict:
    """Sample customer data for personalization."""
    return {
        "tenant_id": "tenant-123",
        "name": "Jane Smith",
        "company_name": "Acme Analytics",
        "email": "jane@acme.com",
        "role": "Data Science Lead",
        "industry": "Healthcare",
    }


@pytest.fixture
def sample_usage_data() -> dict:
    """Sample usage data for personalization."""
    return {
        "tenant_id": "tenant-123",
        "total_api_calls": 8500,
        "total_inferences": 2300,
        "model_count": 3,
        "data_sources": 5,
        "monthly_growth": 0.45,
        "top_model": "patient_risk_v2",
    }


@pytest.fixture
def mock_integration_config() -> IntegrationConfig:
    """Create a mock integration config."""
    return IntegrationConfig(
        enabled_channels=[
            DeliveryChannel.EMAIL,
            DeliveryChannel.IN_APP_BANNER,
        ],
        email_config=EmailConfig(
            provider=EmailProvider.MOCK,
            from_email="test@krlabs.dev",
        ),
        ab_testing_enabled=True,
        track_opens=True,
        track_clicks=True,
    )


# =============================================================================
# Template Mapping Tests
# =============================================================================

class TestTemplateMappings:
    """Test trigger type to StoryBrand template mappings."""
    
    def test_usage_threshold_community_to_pro(self, sample_upsell_event):
        """Usage threshold triggers should map to capacity_expansion."""
        template = get_template_key_for_event(sample_upsell_event)
        assert template == "capacity_expansion"
    
    def test_feature_gate_community_to_pro(self):
        """Feature gate triggers should map to federated_learning."""
        event = UpsellEvent(
            event_id="evt-002",
            trigger_id="trig-feature",
            tenant_id="tenant-456",
            timestamp=datetime.now(),
            trigger_type=UpsellTriggerType.FEATURE_GATE,
            source_tier=BillingTier.COMMUNITY,
            target_tier=BillingTier.PRO,
            trigger_context={"feature": "federated_learning"},
            message="",
            cta_url="",
        )
        template = get_template_key_for_event(event)
        assert template == "federated_learning"
    
    def test_tier_violation_mapping(self):
        """Tier violation triggers should map to tier_violation template."""
        event = UpsellEvent(
            event_id="evt-003",
            trigger_id="trig-violation",
            tenant_id="tenant-789",
            timestamp=datetime.now(),
            trigger_type=UpsellTriggerType.TIER_VIOLATION,
            source_tier=BillingTier.COMMUNITY,
            target_tier=BillingTier.PRO,
            trigger_context={"violation_type": "rate_limit"},
            message="",
            cta_url="",
        )
        template = get_template_key_for_event(event)
        assert template == "tier_violation"
    
    def test_risk_increase_pro_to_enterprise(self):
        """Risk increase triggers should map to risk_audit."""
        event = UpsellEvent(
            event_id="evt-004",
            trigger_id="trig-risk",
            tenant_id="tenant-101",
            timestamp=datetime.now(),
            trigger_type=UpsellTriggerType.RISK_INCREASE,
            source_tier=BillingTier.PRO,
            target_tier=BillingTier.ENTERPRISE,
            trigger_context={"risk_score": 0.75},
            message="",
            cta_url="",
        )
        template = get_template_key_for_event(event)
        assert template == "risk_audit"
    
    def test_value_realization_mapping(self):
        """Value realization triggers should map correctly."""
        event = UpsellEvent(
            event_id="evt-005",
            trigger_id="trig-value",
            tenant_id="tenant-202",
            timestamp=datetime.now(),
            trigger_type=UpsellTriggerType.VALUE_REALIZATION,
            source_tier=BillingTier.PRO,
            target_tier=BillingTier.ENTERPRISE,
            trigger_context={"roi_multiple": 12.5},
            message="",
            cta_url="",
        )
        template = get_template_key_for_event(event)
        assert template == "value_realization"


# =============================================================================
# Personalization Tests
# =============================================================================

class TestMessagePersonalization:
    """Test StoryBrand message personalization."""
    
    def test_personalize_capacity_expansion(
        self, sample_customer_data, sample_usage_data
    ):
        """Test capacity expansion message personalization."""
        result = personalize_upsell_message(
            template_key="capacity_expansion",
            customer_data=sample_customer_data,
            usage_data=sample_usage_data,
            ab_variant="B",
        )
        
        assert result is not None
        assert "Acme Analytics" in result.get("opening", "") or \
               "Jane" in result.get("opening", "")
        assert result.get("cta_url") is not None
    
    def test_ab_variant_selection(self, sample_customer_data, sample_usage_data):
        """Test A/B variant selection works."""
        result_a = personalize_upsell_message(
            template_key="capacity_expansion",
            customer_data=sample_customer_data,
            usage_data=sample_usage_data,
            ab_variant="A",
        )
        
        result_b = personalize_upsell_message(
            template_key="capacity_expansion",
            customer_data=sample_customer_data,
            usage_data=sample_usage_data,
            ab_variant="B",
        )
        
        # Both should return results
        assert result_a is not None
        assert result_b is not None
        
        # Subject lines may differ by variant
        # (A is traditional, B is StoryBrand narrative)
    
    def test_template_not_found(self, sample_customer_data, sample_usage_data):
        """Test handling of unknown template."""
        result = personalize_upsell_message(
            template_key="nonexistent_template",
            customer_data=sample_customer_data,
            usage_data=sample_usage_data,
        )
        # Should return None or empty for unknown templates
        # Implementation may vary


# =============================================================================
# Integration Tests
# =============================================================================

class TestUpsellMessageIntegration:
    """Test the main integration class."""
    
    def test_create_integration(self, mock_integration_config):
        """Test creating an integration instance."""
        integration = UpsellMessageIntegration(
            config=mock_integration_config,
        )
        
        assert integration is not None
        status = integration.get_status()
        assert "email" in status["enabled_channels"]
        assert status["email_provider"] == "mock"
    
    @pytest.mark.asyncio
    async def test_handle_upsell_event_email(
        self,
        sample_upsell_event,
        sample_customer_data,
        sample_usage_data,
        mock_integration_config,
    ):
        """Test handling upsell event with email delivery."""
        integration = UpsellMessageIntegration(
            config=mock_integration_config,
            customer_data_provider=lambda tid: sample_customer_data,
            usage_data_provider=lambda tid: sample_usage_data,
        )
        
        result = await integration.handle_upsell_event(sample_upsell_event)
        
        assert result["success"] is True
        assert result["tracking_id"].startswith("krl-upsell-")
        assert "email" in result["channels"]
        assert result["channels"]["email"]["success"] is True
    
    @pytest.mark.asyncio
    async def test_handle_upsell_event_inapp(
        self,
        sample_upsell_event,
        sample_customer_data,
        sample_usage_data,
        mock_integration_config,
    ):
        """Test handling upsell event with in-app notification."""
        integration = UpsellMessageIntegration(
            config=mock_integration_config,
            customer_data_provider=lambda tid: sample_customer_data,
            usage_data_provider=lambda tid: sample_usage_data,
        )
        
        result = await integration.handle_upsell_event(sample_upsell_event)
        
        assert "in_app" in result["channels"]
        assert result["channels"]["in_app"]["success"] is True
        
        # Check notification was queued
        pending = integration.get_pending_notifications("tenant-123")
        assert len(pending) > 0
    
    def test_ab_variant_assignment_deterministic(self, mock_integration_config):
        """Test A/B variant assignment is deterministic per tenant."""
        integration = UpsellMessageIntegration(config=mock_integration_config)
        
        # Same tenant should get same variant
        variant1 = integration._get_ab_variant("tenant-abc")
        variant2 = integration._get_ab_variant("tenant-abc")
        assert variant1 == variant2
        
        # Different tenants may get different variants
        variant3 = integration._get_ab_variant("tenant-xyz")
        # (variant3 might equal variant1 or not, based on hash)


# =============================================================================
# Conversion Tracking Tests
# =============================================================================

class TestConversionTracking:
    """Test conversion tracking functionality."""
    
    @pytest.mark.asyncio
    async def test_track_email_open(
        self,
        sample_upsell_event,
        sample_customer_data,
        sample_usage_data,
        mock_integration_config,
    ):
        """Test email open tracking."""
        integration = UpsellMessageIntegration(
            config=mock_integration_config,
            customer_data_provider=lambda tid: sample_customer_data,
            usage_data_provider=lambda tid: sample_usage_data,
        )
        
        # Process event first
        result = await integration.handle_upsell_event(sample_upsell_event)
        tracking_id = result["tracking_id"]
        
        # Track open
        opened = integration.track_email_open(tracking_id)
        assert opened is True
        
        # Verify in metrics
        metrics = integration.get_conversion_metrics()
        assert metrics["variants"]["A"]["opened"] + \
               metrics["variants"]["B"]["opened"] >= 1
    
    @pytest.mark.asyncio
    async def test_track_conversion(
        self,
        sample_upsell_event,
        sample_customer_data,
        sample_usage_data,
        mock_integration_config,
    ):
        """Test conversion tracking."""
        integration = UpsellMessageIntegration(
            config=mock_integration_config,
            customer_data_provider=lambda tid: sample_customer_data,
            usage_data_provider=lambda tid: sample_usage_data,
        )
        
        # Process event
        result = await integration.handle_upsell_event(sample_upsell_event)
        tracking_id = result["tracking_id"]
        
        # Simulate conversion
        converted = integration.track_conversion(
            tracking_id,
            {"amount": 49.00, "tier": "pro"}
        )
        assert converted is True
        
        # Check metrics
        metrics = integration.get_conversion_metrics()
        assert metrics["variants"]["A"]["converted"] + \
               metrics["variants"]["B"]["converted"] >= 1


# =============================================================================
# In-App Notification Tests
# =============================================================================

class TestInAppNotifications:
    """Test in-app notification functionality."""
    
    @pytest.mark.asyncio
    async def test_notification_queue(
        self,
        sample_upsell_event,
        sample_customer_data,
        sample_usage_data,
        mock_integration_config,
    ):
        """Test notifications are queued correctly."""
        integration = UpsellMessageIntegration(
            config=mock_integration_config,
            customer_data_provider=lambda tid: sample_customer_data,
            usage_data_provider=lambda tid: sample_usage_data,
        )
        
        await integration.handle_upsell_event(sample_upsell_event)
        
        pending = integration.get_pending_notifications("tenant-123")
        assert len(pending) == 1
        
        notification = pending[0]
        assert notification["tenant_id"] == "tenant-123"
        assert notification["format"] == NotificationFormat.BANNER.value
        assert notification["cta_url"] is not None
    
    @pytest.mark.asyncio
    async def test_notification_dismissal(
        self,
        sample_upsell_event,
        sample_customer_data,
        sample_usage_data,
        mock_integration_config,
    ):
        """Test notification dismissal."""
        integration = UpsellMessageIntegration(
            config=mock_integration_config,
            customer_data_provider=lambda tid: sample_customer_data,
            usage_data_provider=lambda tid: sample_usage_data,
        )
        
        await integration.handle_upsell_event(sample_upsell_event)
        
        pending = integration.get_pending_notifications("tenant-123")
        notification_id = pending[0]["notification_id"]
        
        # Dismiss
        dismissed = integration.dismiss_notification(notification_id, "tenant-123")
        assert dismissed is True
        
        # Should be gone
        remaining = integration.get_pending_notifications("tenant-123")
        assert len(remaining) == 0


# =============================================================================
# Factory Function Tests
# =============================================================================

class TestFactoryFunctions:
    """Test factory function creation."""
    
    def test_create_upsell_integration(self):
        """Test create_upsell_integration factory."""
        integration = create_upsell_integration(
            email_provider=EmailProvider.MOCK,
            from_email="test@example.com",
        )
        
        assert integration is not None
        status = integration.get_status()
        assert status["email_provider"] == "mock"


# =============================================================================
# Awareness Routing Tests
# =============================================================================

class TestAwarenessRouting:
    """Test awareness stage detection and routing."""
    
    def test_detect_unaware_stage(self):
        """Test detecting unaware stage from generic signals."""
        stage, confidence = detect_awareness_stage(
            search_query="data analytics software",
            utm_source="google",
            referrer="https://google.com/search",
        )
        # Generic search without brand = likely unaware or problem-aware
        assert stage in [AwarenessStage.UNAWARE, AwarenessStage.PROBLEM_AWARE]
    
    def test_detect_product_aware_stage(self):
        """Test detecting product-aware stage from branded signals."""
        stage, confidence = detect_awareness_stage(
            search_query="krl analytics pricing",
            utm_source="google",
            referrer="https://google.com/search?q=krl+analytics",
        )
        # Branded search = product or most aware
        assert stage in [AwarenessStage.PRODUCT_AWARE, AwarenessStage.MOST_AWARE]


# =============================================================================
# Integration with BillingBridge Tests
# =============================================================================

class TestBillingBridgeIntegration:
    """Test integration with BillingBridge."""
    
    def test_connect_upsell_integration(self):
        """Test connecting upsell integration to billing bridge."""
        controller = create_billing_controller()
        bridge = create_billing_bridge(controller)
        
        integration = create_upsell_integration(
            email_provider=EmailProvider.MOCK,
        )
        
        # Connect
        bridge.connect_upsell_integration(integration)
        
        # Verify in status
        status = bridge.get_status()
        assert status["connections"]["upsell_integration"] is True
        assert "upsell_integration" in status
    
    def test_get_pending_notifications_via_bridge(self):
        """Test getting notifications through the bridge."""
        controller = create_billing_controller()
        bridge = create_billing_bridge(controller)
        integration = create_upsell_integration(email_provider=EmailProvider.MOCK)
        
        bridge.connect_upsell_integration(integration)
        
        # Should return empty list initially
        notifications = bridge.get_pending_notifications("tenant-test")
        assert notifications == []


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
