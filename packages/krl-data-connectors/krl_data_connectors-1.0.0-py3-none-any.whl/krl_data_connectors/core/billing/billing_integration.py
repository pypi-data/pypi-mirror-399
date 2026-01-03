# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
#
# ⚠️ DEPRECATION WARNING (Dec 2025):
# This module has been moved to krl-premium-backend.
# Import from: app.services.billing.billing_integration
# This stub remains for backward compatibility but will be removed in v2.0.
# ----------------------------------------------------------------------

from __future__ import annotations

import warnings as _warnings
_warnings.warn(
    "krl_data_connectors.core.billing.billing_integration is deprecated. "
    "Import from 'app.services.billing.billing_integration' instead.",
    DeprecationWarning,
    stacklevel=2
)


"""
KRL Billing Integration - Week 23 Day 5
=====================================

Ties PaymentsAdapter implementations to BillingBridge and
AdaptiveBillingController for production billing operations.

Orchestrates:
- UsageMeter → UnitNormalizer → PaymentsAdapter.record_usage()
- RiskPricingEngine → PaymentsAdapter.update_price()
- UpsellEngine → PaymentsAdapter.modify_subscription()
- WebhookDispatcher → TelemetryIngestion (closed loop)
"""


import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone, UTC
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Protocol, TypeVar
from uuid import uuid4

logger = logging.getLogger(__name__)


# =============================================================================
# Type Definitions
# =============================================================================

class PaymentProvider(str, Enum):
    """Supported payment providers."""
    STRIPE = "stripe"
    LAGO = "lago"
    KILL_BILL = "kill_bill"
    MOCK = "mock"


@dataclass
class BillingEvent:
    """Event from billing system."""
    event_id: str
    event_type: str
    provider: PaymentProvider
    customer_id: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class UsageRecord:
    """Normalized usage record for billing."""
    customer_id: str
    subscription_id: str
    metric_name: str
    quantity: float
    unit: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PriceUpdate:
    """Price update request."""
    price_id: str
    new_amount: float
    currency: str = "usd"
    reason: str = ""
    effective_date: Optional[datetime] = None


@dataclass
class SubscriptionChange:
    """Subscription modification request."""
    subscription_id: str
    customer_id: str
    new_tier: str
    reason: str
    prorate: bool = True
    immediate: bool = False


# =============================================================================
# Protocol Definitions
# =============================================================================

class TelemetryIngestionProtocol(Protocol):
    """Protocol for telemetry ingestion."""
    async def ingest(self, event: Dict[str, Any]) -> None: ...


class UsageMeterProtocol(Protocol):
    """Protocol for usage metering."""
    def get_usage(self, customer_id: str, start: datetime, end: datetime) -> List[Dict[str, Any]]: ...


class RiskPricingEngineProtocol(Protocol):
    """Protocol for risk pricing engine."""
    def get_price_adjustment(self, customer_id: str) -> Optional[PriceUpdate]: ...


class UpsellEngineProtocol(Protocol):
    """Protocol for upsell engine."""
    def get_upgrade_recommendation(self, customer_id: str) -> Optional[SubscriptionChange]: ...


# =============================================================================
# Billing Integration Manager
# =============================================================================

class BillingIntegrationManager:
    """
    Manages integration between billing components and payment adapters.
    
    Coordinates:
    - Usage synchronization to payment providers
    - Price updates from risk pricing engine
    - Subscription modifications from upsell engine
    - Webhook event routing to telemetry
    """
    
    def __init__(
        self,
        default_provider: PaymentProvider = PaymentProvider.STRIPE,
        sync_interval_seconds: int = 60,
    ):
        self.default_provider = default_provider
        self.sync_interval_seconds = sync_interval_seconds
        
        # Adapters registry
        self._adapters: Dict[PaymentProvider, Any] = {}
        
        # Component references
        self._telemetry: Optional[TelemetryIngestionProtocol] = None
        self._usage_meter: Optional[UsageMeterProtocol] = None
        self._risk_engine: Optional[RiskPricingEngineProtocol] = None
        self._upsell_engine: Optional[UpsellEngineProtocol] = None
        
        # State
        self._running = False
        self._sync_task: Optional[asyncio.Task] = None
        self._event_handlers: Dict[str, List[Callable]] = {}
        
        # Metrics
        self._metrics = {
            "usage_syncs": 0,
            "price_updates": 0,
            "subscription_changes": 0,
            "webhook_events": 0,
            "errors": 0,
        }
        
        logger.info(f"BillingIntegrationManager initialized with {default_provider.value}")
    
    # -------------------------------------------------------------------------
    # Registration
    # -------------------------------------------------------------------------
    
    def register_adapter(self, provider: PaymentProvider, adapter: Any) -> None:
        """Register a payment adapter."""
        self._adapters[provider] = adapter
        logger.info(f"Registered adapter for {provider.value}")
    
    def register_telemetry(self, telemetry: TelemetryIngestionProtocol) -> None:
        """Register telemetry ingestion for closed-loop feedback."""
        self._telemetry = telemetry
        logger.info("Telemetry ingestion registered")
    
    def register_usage_meter(self, meter: UsageMeterProtocol) -> None:
        """Register usage meter for usage sync."""
        self._usage_meter = meter
        logger.info("Usage meter registered")
    
    def register_risk_engine(self, engine: RiskPricingEngineProtocol) -> None:
        """Register risk pricing engine."""
        self._risk_engine = engine
        logger.info("Risk pricing engine registered")
    
    def register_upsell_engine(self, engine: UpsellEngineProtocol) -> None:
        """Register upsell engine."""
        self._upsell_engine = engine
        logger.info("Upsell engine registered")
    
    def on_event(self, event_type: str, handler: Callable) -> None:
        """Register event handler."""
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)
    
    # -------------------------------------------------------------------------
    # Adapter Access
    # -------------------------------------------------------------------------
    
    def get_adapter(self, provider: Optional[PaymentProvider] = None) -> Any:
        """Get payment adapter for provider."""
        provider = provider or self.default_provider
        if provider not in self._adapters:
            raise ValueError(f"No adapter registered for {provider.value}")
        return self._adapters[provider]
    
    # -------------------------------------------------------------------------
    # Usage Synchronization
    # -------------------------------------------------------------------------
    
    async def sync_usage(
        self,
        customer_id: str,
        subscription_id: str,
        provider: Optional[PaymentProvider] = None,
    ) -> Dict[str, Any]:
        """
        Sync usage from meter to payment provider.
        
        Flow: UsageMeter → UnitNormalizer → PaymentsAdapter.record_usage()
        """
        provider = provider or self.default_provider
        adapter = self.get_adapter(provider)
        
        try:
            # Get usage from meter
            if self._usage_meter:
                now = datetime.now(timezone.utc)
                usage_records = self._usage_meter.get_usage(
                    customer_id,
                    start=datetime(now.year, now.month, 1, tzinfo=timezone.utc),
                    end=now,
                )
            else:
                usage_records = []
            
            results = []
            for record in usage_records:
                # Record usage through adapter
                result = await adapter.record_usage(
                    subscription_id=subscription_id,
                    quantity=record.get("quantity", 0),
                    timestamp=record.get("timestamp", now),
                    action=record.get("metric", "api_call"),
                    idempotency_key=f"{customer_id}-{record.get('id', uuid4().hex)}",
                )
                results.append(result)
            
            self._metrics["usage_syncs"] += 1
            
            return {
                "success": True,
                "customer_id": customer_id,
                "records_synced": len(results),
                "provider": provider.value,
            }
            
        except Exception as e:
            self._metrics["errors"] += 1
            logger.error(f"Usage sync failed for {customer_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def record_single_usage(
        self,
        usage: UsageRecord,
        provider: Optional[PaymentProvider] = None,
    ) -> Dict[str, Any]:
        """Record single usage event immediately."""
        provider = provider or self.default_provider
        adapter = self.get_adapter(provider)
        
        try:
            result = await adapter.record_usage(
                subscription_id=usage.subscription_id,
                quantity=usage.quantity,
                timestamp=usage.timestamp,
                action=usage.metric_name,
                idempotency_key=f"{usage.customer_id}-{usage.timestamp.isoformat()}",
            )
            
            self._metrics["usage_syncs"] += 1
            return {"success": True, "result": result}
            
        except Exception as e:
            self._metrics["errors"] += 1
            logger.error(f"Single usage record failed: {e}")
            return {"success": False, "error": str(e)}
    
    # -------------------------------------------------------------------------
    # Price Updates
    # -------------------------------------------------------------------------
    
    async def apply_price_update(
        self,
        update: PriceUpdate,
        provider: Optional[PaymentProvider] = None,
    ) -> Dict[str, Any]:
        """
        Apply price update from risk pricing engine.
        
        Flow: RiskPricingEngine → PaymentsAdapter.update_price()
        """
        provider = provider or self.default_provider
        adapter = self.get_adapter(provider)
        
        try:
            result = await adapter.update_price(
                price_id=update.price_id,
                new_amount=int(update.new_amount * 100),  # Convert to cents
                currency=update.currency,
            )
            
            self._metrics["price_updates"] += 1
            
            # Emit event for telemetry
            await self._emit_billing_event(BillingEvent(
                event_id=uuid4().hex,
                event_type="price.updated",
                provider=provider,
                customer_id="system",
                data={
                    "price_id": update.price_id,
                    "new_amount": update.new_amount,
                    "reason": update.reason,
                },
            ))
            
            return {"success": True, "result": result}
            
        except Exception as e:
            self._metrics["errors"] += 1
            logger.error(f"Price update failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def check_and_apply_price_adjustments(
        self,
        customer_id: str,
        provider: Optional[PaymentProvider] = None,
    ) -> Optional[Dict[str, Any]]:
        """Check risk engine for price adjustments and apply."""
        if not self._risk_engine:
            return None
        
        adjustment = self._risk_engine.get_price_adjustment(customer_id)
        if adjustment:
            return await self.apply_price_update(adjustment, provider)
        return None
    
    # -------------------------------------------------------------------------
    # Subscription Management
    # -------------------------------------------------------------------------
    
    async def modify_subscription(
        self,
        change: SubscriptionChange,
        provider: Optional[PaymentProvider] = None,
    ) -> Dict[str, Any]:
        """
        Modify subscription tier.
        
        Flow: UpsellEngine → PaymentsAdapter.modify_subscription()
        """
        provider = provider or self.default_provider
        adapter = self.get_adapter(provider)
        
        try:
            result = await adapter.modify_subscription(
                subscription_id=change.subscription_id,
                new_price_id=self._get_price_id_for_tier(change.new_tier),
                prorate=change.prorate,
            )
            
            self._metrics["subscription_changes"] += 1
            
            # Emit event
            await self._emit_billing_event(BillingEvent(
                event_id=uuid4().hex,
                event_type="subscription.modified",
                provider=provider,
                customer_id=change.customer_id,
                data={
                    "subscription_id": change.subscription_id,
                    "new_tier": change.new_tier,
                    "reason": change.reason,
                },
            ))
            
            return {"success": True, "result": result}
            
        except Exception as e:
            self._metrics["errors"] += 1
            logger.error(f"Subscription modification failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def check_and_apply_upgrades(
        self,
        customer_id: str,
        subscription_id: str,
        provider: Optional[PaymentProvider] = None,
    ) -> Optional[Dict[str, Any]]:
        """Check upsell engine for upgrade recommendations."""
        if not self._upsell_engine:
            return None
        
        recommendation = self._upsell_engine.get_upgrade_recommendation(customer_id)
        if recommendation:
            recommendation.subscription_id = subscription_id
            return await self.modify_subscription(recommendation, provider)
        return None
    
    def _get_price_id_for_tier(self, tier: str) -> str:
        """Map tier to price ID (configurable)."""
        # Would be configured per deployment
        tier_prices = {
            "community": "price_community_monthly",
            "pro": "price_pro_monthly",
            "enterprise": "price_enterprise_monthly",
        }
        return tier_prices.get(tier.lower(), f"price_{tier.lower()}_monthly")
    
    # -------------------------------------------------------------------------
    # Webhook Handling
    # -------------------------------------------------------------------------
    
    async def handle_webhook(
        self,
        provider: PaymentProvider,
        payload: bytes,
        signature: str,
    ) -> Dict[str, Any]:
        """
        Handle webhook from payment provider.
        
        Flow: Webhook → Adapter.handle_webhook() → TelemetryIngestion
        """
        adapter = self.get_adapter(provider)
        
        try:
            event = await adapter.handle_webhook(payload, signature)
            self._metrics["webhook_events"] += 1
            
            # Create billing event
            billing_event = BillingEvent(
                event_id=event.get("id", uuid4().hex),
                event_type=event.get("type", "unknown"),
                provider=provider,
                customer_id=event.get("data", {}).get("customer", "unknown"),
                data=event.get("data", {}),
            )
            
            # Feed to telemetry for closed loop
            await self._emit_billing_event(billing_event)
            
            # Trigger event handlers
            await self._dispatch_event(billing_event)
            
            return {"success": True, "event_type": billing_event.event_type}
            
        except Exception as e:
            self._metrics["errors"] += 1
            logger.error(f"Webhook handling failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _emit_billing_event(self, event: BillingEvent) -> None:
        """Emit billing event to telemetry for closed-loop feedback."""
        if self._telemetry:
            await self._telemetry.ingest({
                "event_type": "billing_event",
                "event_id": event.event_id,
                "billing_event_type": event.event_type,
                "provider": event.provider.value,
                "customer_id": event.customer_id,
                "data": event.data,
                "timestamp": event.timestamp.isoformat(),
            })
    
    async def _dispatch_event(self, event: BillingEvent) -> None:
        """Dispatch event to registered handlers."""
        handlers = self._event_handlers.get(event.event_type, [])
        handlers.extend(self._event_handlers.get("*", []))  # Wildcard handlers
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"Event handler error: {e}")
    
    # -------------------------------------------------------------------------
    # Sync Loop
    # -------------------------------------------------------------------------
    
    async def start(self) -> None:
        """Start the billing sync loop."""
        if self._running:
            return
        
        self._running = True
        self._sync_task = asyncio.create_task(self._sync_loop())
        logger.info("Billing integration started")
    
    async def stop(self) -> None:
        """Stop the billing sync loop."""
        self._running = False
        if self._sync_task:
            self._sync_task.cancel()
            try:
                await self._sync_task
            except asyncio.CancelledError:
                pass
        logger.info("Billing integration stopped")
    
    async def _sync_loop(self) -> None:
        """Background sync loop."""
        while self._running:
            try:
                await asyncio.sleep(self.sync_interval_seconds)
                # Periodic sync tasks could be added here
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Sync loop error: {e}")
    
    # -------------------------------------------------------------------------
    # Metrics
    # -------------------------------------------------------------------------
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get integration metrics."""
        return {
            **self._metrics,
            "registered_adapters": list(self._adapters.keys()),
            "default_provider": self.default_provider.value,
            "running": self._running,
        }


# =============================================================================
# Customer Lifecycle Manager
# =============================================================================

class CustomerLifecycleManager:
    """
    Manages customer lifecycle across payment providers.
    
    Handles:
    - Customer creation and setup
    - Subscription lifecycle
    - Multi-provider customer sync
    """
    
    def __init__(self, integration: BillingIntegrationManager):
        self.integration = integration
        self._customer_map: Dict[str, Dict[str, str]] = {}  # internal_id -> {provider: external_id}
    
    async def create_customer(
        self,
        internal_id: str,
        email: str,
        name: str,
        tier: str = "community",
        provider: Optional[PaymentProvider] = None,
    ) -> Dict[str, Any]:
        """Create customer in payment provider."""
        provider = provider or self.integration.default_provider
        adapter = self.integration.get_adapter(provider)
        
        try:
            result = await adapter.create_customer(
                email=email,
                name=name,
                metadata={"internal_id": internal_id, "tier": tier},
            )
            
            # Store mapping
            if internal_id not in self._customer_map:
                self._customer_map[internal_id] = {}
            self._customer_map[internal_id][provider.value] = result.get("id")
            
            return {"success": True, "customer": result}
            
        except Exception as e:
            logger.error(f"Customer creation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_subscription(
        self,
        internal_id: str,
        tier: str = "community",
        trial_days: int = 0,
        provider: Optional[PaymentProvider] = None,
    ) -> Dict[str, Any]:
        """Create subscription for customer."""
        provider = provider or self.integration.default_provider
        adapter = self.integration.get_adapter(provider)
        
        # Get external customer ID
        external_id = self._customer_map.get(internal_id, {}).get(provider.value)
        if not external_id:
            return {"success": False, "error": "Customer not found"}
        
        try:
            result = await adapter.create_subscription(
                customer_id=external_id,
                price_id=self.integration._get_price_id_for_tier(tier),
                trial_days=trial_days,
            )
            
            return {"success": True, "subscription": result}
            
        except Exception as e:
            logger.error(f"Subscription creation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def get_external_id(
        self,
        internal_id: str,
        provider: Optional[PaymentProvider] = None,
    ) -> Optional[str]:
        """Get external customer ID for provider."""
        provider = provider or self.integration.default_provider
        return self._customer_map.get(internal_id, {}).get(provider.value)


# =============================================================================
# Factory Function
# =============================================================================

def create_billing_integration(
    default_provider: PaymentProvider = PaymentProvider.STRIPE,
    stripe_api_key: Optional[str] = None,
    lago_api_key: Optional[str] = None,
    lago_api_url: Optional[str] = None,
) -> BillingIntegrationManager:
    """
    Factory to create fully configured BillingIntegrationManager.
    
    Args:
        default_provider: Default payment provider
        stripe_api_key: Stripe API key (for Stripe adapter)
        lago_api_key: Lago API key (for Lago adapter)
        lago_api_url: Lago API URL (for Lago adapter)
    
    Returns:
        Configured BillingIntegrationManager
    """
    manager = BillingIntegrationManager(default_provider=default_provider)
    
    # Register adapters based on provided credentials
    # Note: Actual adapter instantiation would import from respective modules
    
    if stripe_api_key:
        # Would import StripeAdapter and instantiate
        logger.info("Stripe adapter configured")
    
    if lago_api_key and lago_api_url:
        # Would import LagoAdapter and instantiate
        logger.info("Lago adapter configured")
    
    return manager


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Enums
    "PaymentProvider",
    # Data Classes
    "BillingEvent",
    "UsageRecord",
    "PriceUpdate",
    "SubscriptionChange",
    # Managers
    "BillingIntegrationManager",
    "CustomerLifecycleManager",
    # Factory
    "create_billing_integration",
]
