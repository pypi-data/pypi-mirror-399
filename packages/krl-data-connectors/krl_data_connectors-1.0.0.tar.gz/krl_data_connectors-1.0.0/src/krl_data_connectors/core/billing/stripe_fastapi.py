# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""
Stripe FastAPI Integration - DEPRECATED

⚠️ DEPRECATION WARNING (Dec 2025):
This module has been moved to krl-premium-backend.
Import from: app.services.billing.stripe_fastapi

This stub remains for backward compatibility but will be removed in v2.0.
"""

from __future__ import annotations

import warnings
warnings.warn(
    "krl_data_connectors.core.billing.stripe_fastapi is deprecated. "
    "This module has moved to krl-premium-backend. "
    "Import from 'app.services.billing.stripe_fastapi' instead.",
    DeprecationWarning,
    stacklevel=2
)

import hashlib
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from enum import Enum
from http import HTTPStatus
from typing import Any, Callable, Dict, List, Optional, Protocol, Set

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class StripeConfig:
    """
    Stripe configuration from environment.
    
    Required env vars:
    - STRIPE_SECRET_KEY: API key (sk_test_* or sk_live_*)
    - STRIPE_WEBHOOK_SECRET: Webhook signing secret (whsec_*)
    
    Optional:
    - STRIPE_CONNECT_FEE_PERCENT: Platform fee percentage (default: 0)
    - STRIPE_API_VERSION: API version override
    """
    secret_key: str = ""
    webhook_secret: str = ""
    connect_fee_percent: float = 0.0
    api_version: Optional[str] = None
    test_mode: bool = True
    
    @classmethod
    def from_env(cls) -> "StripeConfig":
        """Load configuration from environment variables."""
        secret_key = os.getenv("STRIPE_SECRET_KEY", "")
        return cls(
            secret_key=secret_key,
            webhook_secret=os.getenv("STRIPE_WEBHOOK_SECRET", ""),
            connect_fee_percent=float(os.getenv("STRIPE_CONNECT_FEE_PERCENT", "0")),
            api_version=os.getenv("STRIPE_API_VERSION"),
            test_mode=secret_key.startswith("sk_test_") if secret_key else True,
        )


# =============================================================================
# Idempotency Table (In-Memory for SDK, DB for production)
# =============================================================================

@dataclass
class ProcessedStripeEvent:
    """
    Record of processed Stripe webhook event.
    
    In production, this should be a database model:
    
    class ProcessedStripeEvent(Base):
        __tablename__ = "processed_stripe_events"
        event_id = Column(String(255), primary_key=True)
        processed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
        event_type = Column(String(100))
        tenant_id = Column(String(100), nullable=True)
    """
    event_id: str
    processed_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    event_type: str = ""
    tenant_id: Optional[str] = None


class IdempotencyStore:
    """
    In-memory idempotency store for processed events.
    
    Production implementation should use database (SQLAlchemy/SQLModel).
    """
    
    def __init__(self, max_events: int = 10000, ttl_hours: int = 24):
        self._events: Dict[str, ProcessedStripeEvent] = {}
        self._max_events = max_events
        self._ttl = timedelta(hours=ttl_hours)
    
    def exists(self, event_id: str) -> bool:
        """Check if event has been processed."""
        event = self._events.get(event_id)
        if event is None:
            return False
        # Check TTL
        if datetime.now(UTC) - event.processed_at > self._ttl:
            del self._events[event_id]
            return False
        return True
    
    def mark_processed(
        self,
        event_id: str,
        event_type: str = "",
        tenant_id: Optional[str] = None,
    ) -> None:
        """Mark event as processed."""
        # Evict oldest if at capacity
        if len(self._events) >= self._max_events:
            oldest_id = min(self._events, key=lambda k: self._events[k].processed_at)
            del self._events[oldest_id]
        
        self._events[event_id] = ProcessedStripeEvent(
            event_id=event_id,
            event_type=event_type,
            tenant_id=tenant_id,
        )
    
    def cleanup_expired(self) -> int:
        """Remove expired events. Returns count removed."""
        now = datetime.now(UTC)
        expired = [
            eid for eid, event in self._events.items()
            if now - event.processed_at > self._ttl
        ]
        for eid in expired:
            del self._events[eid]
        return len(expired)


# =============================================================================
# Tenant Resolution
# =============================================================================

class TenantProfile(Protocol):
    """Protocol for tenant profile (your ORM model)."""
    id: str
    stripe_customer_id: Optional[str]
    stripe_account_id: Optional[str]
    billing_tier: str
    country: str
    owner_email: str


@dataclass
class TenantMapping:
    """
    Mapping between Stripe identifiers and internal tenant.
    
    Used by webhook handler to resolve tenant from event data.
    """
    tenant_id: str
    stripe_customer_id: Optional[str] = None
    stripe_account_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    tier: str = "community"


class TenantResolver:
    """
    Resolves tenant from Stripe webhook event data.
    
    In production, this queries your database. This implementation
    provides an in-memory cache for the SDK.
    """
    
    def __init__(self):
        self._by_customer: Dict[str, TenantMapping] = {}
        self._by_account: Dict[str, TenantMapping] = {}
        self._by_tenant: Dict[str, TenantMapping] = {}
    
    def register(self, mapping: TenantMapping) -> None:
        """Register a tenant mapping."""
        self._by_tenant[mapping.tenant_id] = mapping
        if mapping.stripe_customer_id:
            self._by_customer[mapping.stripe_customer_id] = mapping
        if mapping.stripe_account_id:
            self._by_account[mapping.stripe_account_id] = mapping
    
    def resolve(self, event_data: Dict[str, Any]) -> Optional[TenantMapping]:
        """
        Resolve tenant from webhook event data.
        
        Tries in order:
        1. customer ID
        2. account ID
        3. metadata.tenant_id
        """
        # Try customer
        customer_id = event_data.get("customer")
        if customer_id and customer_id in self._by_customer:
            return self._by_customer[customer_id]
        
        # Try account
        account_id = event_data.get("account")
        if account_id and account_id in self._by_account:
            return self._by_account[account_id]
        
        # Try metadata
        metadata = event_data.get("metadata") or {}
        tenant_id = metadata.get("tenant_id")
        if tenant_id and tenant_id in self._by_tenant:
            return self._by_tenant[tenant_id]
        
        return None


# =============================================================================
# Stripe Adapter (Enhanced with Idempotency)
# =============================================================================

class StripeAdapterEnhanced:
    """
    Enhanced StripeAdapter with idempotency and FastAPI DI support.
    
    This wraps the base StripeAdapter and adds:
    - Idempotency key generation/tracking
    - Tenant context propagation
    - Metadata → Entitlement mapping
    
    All engines resolve this via FastAPI Depends().
    """
    
    def __init__(self, config: Optional[StripeConfig] = None):
        self.config = config or StripeConfig.from_env()
        self._stripe = None
        self._initialized = False
        
        # Idempotency tracking
        self._idempotency_keys: Set[str] = set()
    
    def initialize(self) -> bool:
        """Initialize Stripe SDK."""
        try:
            import stripe
            stripe.api_key = self.config.secret_key
            if self.config.api_version:
                stripe.api_version = self.config.api_version
            self._stripe = stripe
            self._initialized = True
            logger.info(f"StripeAdapter initialized (test_mode={self.config.test_mode})")
            return True
        except ImportError:
            logger.error("stripe-python not installed")
            return False
    
    def _ensure_initialized(self) -> None:
        """Ensure SDK is initialized."""
        if not self._initialized:
            self.initialize()
    
    def _generate_idempotency_key(
        self,
        operation: str,
        tenant_id: str,
        *args: Any,
    ) -> str:
        """
        Generate deterministic idempotency key.
        
        Keys are based on operation + tenant + params, ensuring
        the same logical operation produces the same key.
        """
        components = [operation, tenant_id] + [str(a) for a in args]
        key_input = ":".join(components)
        return hashlib.sha256(key_input.encode()).hexdigest()[:32]
    
    # =========================================================================
    # Account Sync Port
    # =========================================================================
    
    def create_connect_account(
        self,
        tenant_id: str,
        email: str,
        country: str,
        tier: str = "pro",
        account_type: str = "express",
    ) -> Dict[str, Any]:
        """
        Create Stripe Connect account for tenant.
        
        Maps tier to account type:
        - Community: Standard (for testing only)
        - Pro: Express (simplified onboarding)
        - Enterprise: Custom (full white-label)
        """
        self._ensure_initialized()
        
        capabilities = {
            "card_payments": {"requested": True},
            "transfers": {"requested": True},
        }
        
        account = self._stripe.Account.create(
            type=account_type,
            country=country,
            email=email,
            capabilities=capabilities,
            metadata={
                "tenant_id": tenant_id,
                "tier": tier,
            },
        )
        
        logger.info(f"Created Connect account {account.id} for tenant {tenant_id}")
        
        return {
            "account_id": account.id,
            "charges_enabled": account.charges_enabled,
            "payouts_enabled": account.payouts_enabled,
            "details_submitted": account.details_submitted,
        }
    
    def update_connect_account(
        self,
        account_id: str,
        tenant_id: str,
        tier: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Update Connect account with latest KYC/capabilities."""
        self._ensure_initialized()
        
        update_params = {
            "metadata": {
                "tenant_id": tenant_id,
                "tier": tier,
            },
        }
        update_params.update(kwargs)
        
        account = self._stripe.Account.modify(account_id, **update_params)
        
        return {
            "account_id": account.id,
            "charges_enabled": account.charges_enabled,
            "payouts_enabled": account.payouts_enabled,
        }
    
    def get_connect_account(self, account_id: str) -> Dict[str, Any]:
        """Retrieve Connect account details."""
        self._ensure_initialized()
        
        account = self._stripe.Account.retrieve(account_id)
        
        return {
            "account_id": account.id,
            "type": account.type,
            "email": account.email,
            "country": account.country,
            "charges_enabled": account.charges_enabled,
            "payouts_enabled": account.payouts_enabled,
            "metadata": dict(account.metadata) if account.metadata else {},
        }
    
    def sync_subscription(
        self,
        subscription_id: str,
    ) -> Dict[str, Any]:
        """
        Sync subscription state with internal systems.
        
        Maps product.metadata and price.metadata to:
        - EntitlementEngine: feature flags and quotas
        - BillingStateMachine: subscription state
        - LimitsGateway: rate limits and quotas
        
        Returns mapping for engines to consume.
        """
        self._ensure_initialized()
        
        sub = self._stripe.Subscription.retrieve(
            subscription_id,
            expand=["items.data.price.product"],
        )
        
        # Extract metadata from all levels
        sub_metadata = dict(sub.metadata) if sub.metadata else {}
        
        items_data = []
        entitlements = []
        limits = {}
        
        for item in sub["items"]["data"]:
            price = item.price
            product = price.product if hasattr(price, "product") else None
            
            price_metadata = dict(price.metadata) if price.metadata else {}
            product_metadata = {}
            if product and hasattr(product, "metadata"):
                product_metadata = dict(product.metadata)
            
            # Extract entitlements from product metadata
            # Convention: entitlement_* keys define features
            for key, value in product_metadata.items():
                if key.startswith("entitlement_"):
                    feature = key.replace("entitlement_", "")
                    entitlements.append({
                        "feature": feature,
                        "value": value,
                        "source": "product_metadata",
                    })
            
            # Extract limits from price metadata
            # Convention: limit_* keys define quotas
            for key, value in price_metadata.items():
                if key.startswith("limit_"):
                    limit_name = key.replace("limit_", "")
                    try:
                        limits[limit_name] = int(value)
                    except ValueError:
                        limits[limit_name] = value
            
            items_data.append({
                "item_id": item.id,
                "price_id": price.id,
                "product_id": product.id if product else None,
                "quantity": item.quantity,
                "price_metadata": price_metadata,
                "product_metadata": product_metadata,
            })
        
        # Map subscription status to state machine
        state_mapping = {
            "trialing": "TRIAL",
            "active": "ACTIVE",
            "past_due": "PAST_DUE",
            "canceled": "CANCELED",
            "unpaid": "SUSPENDED",
        }
        billing_state = state_mapping.get(sub.status, "ACTIVE")
        
        return {
            "subscription_id": sub.id,
            "customer_id": sub.customer,
            "status": sub.status,
            "billing_state": billing_state,
            "current_period_start": sub.current_period_start,
            "current_period_end": sub.current_period_end,
            "cancel_at_period_end": sub.cancel_at_period_end,
            "tenant_id": sub_metadata.get("tenant_id"),
            "tier": sub_metadata.get("tier", "pro"),
            "items": items_data,
            "entitlements": entitlements,
            "limits": limits,
            "metadata": sub_metadata,
        }
    
    # =========================================================================
    # Payment Operations Port (with Idempotency)
    # =========================================================================
    
    def record_usage(
        self,
        subscription_item_id: str,
        quantity: int,
        tenant_id: str,
        timestamp: Optional[int] = None,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Record usage for metered billing.
        
        Uses idempotency key to prevent duplicate charges.
        """
        self._ensure_initialized()
        
        ts = timestamp or int(time.time())
        idem_key = idempotency_key or self._generate_idempotency_key(
            "record_usage",
            tenant_id,
            subscription_item_id,
            quantity,
            ts,
        )
        
        usage_record = self._stripe.SubscriptionItem.create_usage_record(
            subscription_item_id,
            quantity=quantity,
            timestamp=ts,
            action="increment",
            idempotency_key=idem_key,
        )
        
        logger.debug(f"Recorded usage: {quantity} for item {subscription_item_id}")
        
        return {
            "usage_record_id": usage_record.id,
            "quantity": quantity,
            "timestamp": ts,
            "idempotency_key": idem_key,
        }
    
    def update_subscription_item_price(
        self,
        subscription_id: str,
        item_id: str,
        new_price_id: str,
        tenant_id: str,
        proration_behavior: str = "create_prorations",
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update subscription item price (tier upgrade/downgrade).
        
        Used by RiskPricingEngine to adjust pricing based on risk.
        """
        self._ensure_initialized()
        
        idem_key = idempotency_key or self._generate_idempotency_key(
            "update_price",
            tenant_id,
            subscription_id,
            new_price_id,
        )
        
        subscription = self._stripe.Subscription.modify(
            subscription_id,
            items=[{"id": item_id, "price": new_price_id}],
            proration_behavior=proration_behavior,
            idempotency_key=idem_key,
        )
        
        logger.info(f"Updated subscription {subscription_id} to price {new_price_id}")
        
        return {
            "subscription_id": subscription.id,
            "status": subscription.status,
            "idempotency_key": idem_key,
        }
    
    def apply_overage(
        self,
        customer_id: str,
        amount_cents: int,
        currency: str,
        description: str,
        tenant_id: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Apply overage charge to customer.
        
        Creates invoice item + finalizes invoice.
        Used by BillingPolicyTree for contract enforcement.
        """
        self._ensure_initialized()
        
        idem_key = idempotency_key or self._generate_idempotency_key(
            "apply_overage",
            tenant_id,
            customer_id,
            amount_cents,
            description,
        )
        
        # Create invoice item
        self._stripe.InvoiceItem.create(
            customer=customer_id,
            amount=amount_cents,
            currency=currency,
            description=description,
            idempotency_key=f"{idem_key}_item",
        )
        
        # Create and finalize invoice
        invoice = self._stripe.Invoice.create(
            customer=customer_id,
            auto_advance=True,
            idempotency_key=f"{idem_key}_invoice",
        )
        
        finalized = self._stripe.Invoice.finalize_invoice(invoice.id)
        
        logger.info(f"Applied overage {amount_cents} cents to customer {customer_id}")
        
        return {
            "invoice_id": finalized.id,
            "amount": amount_cents,
            "currency": currency,
            "status": finalized.status,
            "hosted_invoice_url": finalized.hosted_invoice_url,
            "idempotency_key": idem_key,
        }
    
    def apply_discount(
        self,
        subscription_id: str,
        tenant_id: str,
        coupon_id: Optional[str] = None,
        promotion_code: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Apply discount to subscription.
        
        Supports both coupon IDs and promotion codes.
        """
        self._ensure_initialized()
        
        idem_key = idempotency_key or self._generate_idempotency_key(
            "apply_discount",
            tenant_id,
            subscription_id,
            coupon_id or promotion_code or "",
        )
        
        update_params: Dict[str, Any] = {"idempotency_key": idem_key}
        
        if coupon_id:
            update_params["coupon"] = coupon_id
        elif promotion_code:
            update_params["promotion_code"] = promotion_code
        
        subscription = self._stripe.Subscription.modify(
            subscription_id,
            **update_params,
        )
        
        logger.info(f"Applied discount to subscription {subscription_id}")
        
        return {
            "subscription_id": subscription.id,
            "discount": dict(subscription.discount) if subscription.discount else None,
            "idempotency_key": idem_key,
        }
    
    def create_checkout_session(
        self,
        customer_id: str,
        price_id: str,
        tenant_id: str,
        tier: str,
        mode: str = "subscription",
        success_url: str = "",
        cancel_url: str = "",
    ) -> Dict[str, Any]:
        """
        Create Stripe Checkout session.
        
        Used by UpsellEngine to create upgrade offers.
        """
        self._ensure_initialized()
        
        session = self._stripe.checkout.Session.create(
            customer=customer_id,
            line_items=[{"price": price_id, "quantity": 1}],
            mode=mode,
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "tenant_id": tenant_id,
                "tier": tier,
            },
        )
        
        logger.info(f"Created checkout session {session.id} for tenant {tenant_id}")
        
        return {
            "session_id": session.id,
            "url": session.url,
        }
    
    # =========================================================================
    # Webhook Verification
    # =========================================================================
    
    def verify_webhook(
        self,
        payload: bytes,
        signature: str,
    ) -> Dict[str, Any]:
        """
        Verify and parse webhook.
        
        Returns parsed event data or raises exception.
        """
        self._ensure_initialized()
        
        event = self._stripe.Webhook.construct_event(
            payload,
            signature,
            self.config.webhook_secret,
        )
        
        return {
            "event_id": event.id,
            "event_type": event.type,
            "data": dict(event.data.object),
            "created": event.created,
        }


# =============================================================================
# FastAPI Dependency Injection
# =============================================================================

# Singleton instance
_stripe_adapter: Optional[StripeAdapterEnhanced] = None
_idempotency_store: Optional[IdempotencyStore] = None
_tenant_resolver: Optional[TenantResolver] = None


def get_stripe_adapter() -> StripeAdapterEnhanced:
    """
    FastAPI dependency for StripeAdapter.
    
    Usage:
        @app.post("/api/record-usage")
        async def record_usage(
            adapter: StripeAdapterEnhanced = Depends(get_stripe_adapter)
        ):
            ...
    """
    global _stripe_adapter
    if _stripe_adapter is None:
        _stripe_adapter = StripeAdapterEnhanced()
        _stripe_adapter.initialize()
    return _stripe_adapter


def get_idempotency_store() -> IdempotencyStore:
    """FastAPI dependency for idempotency store."""
    global _idempotency_store
    if _idempotency_store is None:
        _idempotency_store = IdempotencyStore()
    return _idempotency_store


def get_tenant_resolver() -> TenantResolver:
    """FastAPI dependency for tenant resolver."""
    global _tenant_resolver
    if _tenant_resolver is None:
        _tenant_resolver = TenantResolver()
    return _tenant_resolver


def configure_stripe_adapter(config: StripeConfig) -> StripeAdapterEnhanced:
    """Configure and return StripeAdapter singleton."""
    global _stripe_adapter
    _stripe_adapter = StripeAdapterEnhanced(config)
    _stripe_adapter.initialize()
    return _stripe_adapter


# =============================================================================
# Four-Loop Event Handlers (Protocols)
# =============================================================================

class BillingStateMachineProtocol(Protocol):
    """Protocol for BillingStateMachine integration."""
    
    def to_past_due(self, tenant_id: str, data: Dict[str, Any]) -> None: ...
    def to_active(self, tenant_id: str, data: Dict[str, Any]) -> None: ...
    def to_canceled(self, tenant_id: str, data: Dict[str, Any]) -> None: ...


class EntitlementEngineProtocol(Protocol):
    """Protocol for EntitlementEngine integration."""
    
    def refresh_from_metadata(
        self, tenant_id: str, metadata: Dict[str, Any]
    ) -> None: ...
    
    def apply_entitlements(
        self, tenant_id: str, entitlements: List[Dict[str, Any]]
    ) -> None: ...


class FraudDetectionEngineProtocol(Protocol):
    """Protocol for FraudDetectionEngine integration."""
    
    def clear_risk(self, tenant_id: str, data: Dict[str, Any]) -> None: ...
    def flag_suspicious(self, tenant_id: str, data: Dict[str, Any]) -> None: ...


class ContractEnforcementProtocol(Protocol):
    """Protocol for ContractEnforcementEngine integration."""
    
    def flag_payment_failure(self, tenant_id: str, data: Dict[str, Any]) -> None: ...
    def record_payment(self, tenant_id: str, data: Dict[str, Any]) -> None: ...
    def record_credit(self, tenant_id: str, data: Dict[str, Any]) -> None: ...


class LimitsGatewayProtocol(Protocol):
    """Protocol for LimitsGateway integration."""
    
    def sync_limits(self, tenant_id: str, limits: Dict[str, Any]) -> None: ...


# =============================================================================
# Webhook Event Router
# =============================================================================

class WebhookEventRouter:
    """
    Routes webhook events to four synchronized loops.
    
    This is the fan-out layer between HTTP and domain logic.
    No Stripe objects escape this boundary.
    """
    
    def __init__(
        self,
        adapter: StripeAdapterEnhanced,
        idempotency_store: IdempotencyStore,
        tenant_resolver: TenantResolver,
    ):
        self.adapter = adapter
        self.idempotency_store = idempotency_store
        self.tenant_resolver = tenant_resolver
        
        # Engine references (set via connect_*)
        self._billing_state_machine: Optional[BillingStateMachineProtocol] = None
        self._entitlement_engine: Optional[EntitlementEngineProtocol] = None
        self._fraud_detection: Optional[FraudDetectionEngineProtocol] = None
        self._contract_enforcement: Optional[ContractEnforcementProtocol] = None
        self._limits_gateway: Optional[LimitsGatewayProtocol] = None
    
    # =========================================================================
    # Engine Connection
    # =========================================================================
    
    def connect_billing_state_machine(
        self, engine: BillingStateMachineProtocol
    ) -> None:
        """Connect BillingStateMachine for subscription state updates."""
        self._billing_state_machine = engine
    
    def connect_entitlement_engine(
        self, engine: EntitlementEngineProtocol
    ) -> None:
        """Connect EntitlementEngine for feature flag updates."""
        self._entitlement_engine = engine
    
    def connect_fraud_detection(
        self, engine: FraudDetectionEngineProtocol
    ) -> None:
        """Connect FraudDetectionEngine for risk updates."""
        self._fraud_detection = engine
    
    def connect_contract_enforcement(
        self, engine: ContractEnforcementProtocol
    ) -> None:
        """Connect ContractEnforcementEngine for SLA tracking."""
        self._contract_enforcement = engine
    
    def connect_limits_gateway(
        self, engine: LimitsGatewayProtocol
    ) -> None:
        """Connect LimitsGateway for quota updates."""
        self._limits_gateway = engine
    
    # =========================================================================
    # Event Routing
    # =========================================================================
    
    def route_event(
        self,
        event_id: str,
        event_type: str,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Route parsed webhook event to appropriate engines.
        
        Returns routing result summary.
        """
        # Check idempotency
        if self.idempotency_store.exists(event_id):
            return {"status": "already_processed", "event_id": event_id}
        
        # Resolve tenant
        tenant = self.tenant_resolver.resolve(data)
        tenant_id = tenant.tenant_id if tenant else data.get("metadata", {}).get("tenant_id")
        
        if not tenant_id:
            logger.warning(f"Could not resolve tenant for event {event_id}")
            # Still mark as processed to avoid retries
            self.idempotency_store.mark_processed(event_id, event_type)
            return {"status": "no_tenant", "event_id": event_id}
        
        # Route by event type
        routed_to = []
        
        try:
            if event_type == "invoice.payment_failed":
                self._handle_payment_failed(tenant_id, data)
                routed_to.extend(["billing_state_machine", "contract_enforcement"])
            
            elif event_type == "invoice.paid":
                self._handle_invoice_paid(tenant_id, data)
                routed_to.extend(["billing_state_machine", "contract_enforcement"])
            
            elif event_type == "charge.refunded":
                self._handle_refund(tenant_id, data)
                routed_to.append("contract_enforcement")
            
            elif event_type == "payment_intent.succeeded":
                self._handle_payment_succeeded(tenant_id, data)
                routed_to.append("fraud_detection")
            
            elif event_type == "customer.updated":
                self._handle_customer_updated(tenant_id, data)
                routed_to.append("entitlement_engine")
            
            elif event_type == "customer.subscription.updated":
                self._handle_subscription_updated(tenant_id, data)
                routed_to.extend(["entitlement_engine", "limits_gateway"])
            
            elif event_type == "account.updated":
                self._handle_account_updated(tenant_id, data)
                routed_to.extend(["entitlement_engine", "limits_gateway"])
            
            # Mark as processed
            self.idempotency_store.mark_processed(event_id, event_type, tenant_id)
            
            logger.info(f"Routed event {event_id} ({event_type}) to {routed_to}")
            
            return {
                "status": "processed",
                "event_id": event_id,
                "event_type": event_type,
                "tenant_id": tenant_id,
                "routed_to": routed_to,
            }
            
        except Exception as e:
            logger.error(f"Error routing event {event_id}: {e}")
            return {
                "status": "error",
                "event_id": event_id,
                "error": str(e),
            }
    
    # =========================================================================
    # Event Handlers
    # =========================================================================
    
    def _handle_payment_failed(self, tenant_id: str, data: Dict[str, Any]) -> None:
        """Handle invoice.payment_failed event."""
        if self._billing_state_machine:
            self._billing_state_machine.to_past_due(tenant_id, data)
        
        if self._contract_enforcement:
            self._contract_enforcement.flag_payment_failure(tenant_id, data)
    
    def _handle_invoice_paid(self, tenant_id: str, data: Dict[str, Any]) -> None:
        """Handle invoice.paid event."""
        if self._billing_state_machine:
            self._billing_state_machine.to_active(tenant_id, data)
        
        if self._contract_enforcement:
            self._contract_enforcement.record_payment(tenant_id, data)
    
    def _handle_refund(self, tenant_id: str, data: Dict[str, Any]) -> None:
        """Handle charge.refunded event."""
        if self._contract_enforcement:
            self._contract_enforcement.record_credit(tenant_id, data)
    
    def _handle_payment_succeeded(self, tenant_id: str, data: Dict[str, Any]) -> None:
        """Handle payment_intent.succeeded event."""
        if self._fraud_detection:
            self._fraud_detection.clear_risk(tenant_id, data)
    
    def _handle_customer_updated(self, tenant_id: str, data: Dict[str, Any]) -> None:
        """Handle customer.updated event."""
        metadata = data.get("metadata") or {}
        if self._entitlement_engine:
            self._entitlement_engine.refresh_from_metadata(tenant_id, metadata)
    
    def _handle_subscription_updated(self, tenant_id: str, data: Dict[str, Any]) -> None:
        """Handle customer.subscription.updated event."""
        # Sync full subscription data
        subscription_id = data.get("id")
        if subscription_id:
            sync_result = self.adapter.sync_subscription(subscription_id)
            
            if self._entitlement_engine and sync_result.get("entitlements"):
                self._entitlement_engine.apply_entitlements(
                    tenant_id, sync_result["entitlements"]
                )
            
            if self._limits_gateway and sync_result.get("limits"):
                self._limits_gateway.sync_limits(tenant_id, sync_result["limits"])
    
    def _handle_account_updated(self, tenant_id: str, data: Dict[str, Any]) -> None:
        """Handle account.updated event (Connect)."""
        account_id = data.get("id")
        if account_id:
            account_data = self.adapter.get_connect_account(account_id)
            metadata = account_data.get("metadata", {})
            
            if self._entitlement_engine:
                self._entitlement_engine.refresh_from_metadata(tenant_id, metadata)


# =============================================================================
# FastAPI Router Factory
# =============================================================================

def create_stripe_webhook_router():
    """
    Create FastAPI router for Stripe webhooks.
    
    Usage:
        from fastapi import FastAPI
        from .stripe_fastapi import create_stripe_webhook_router
        
        app = FastAPI()
        app.include_router(create_stripe_webhook_router())
    
    Returns APIRouter that handles /stripe/webhook endpoint.
    """
    try:
        from fastapi import APIRouter, Depends, Header, HTTPException, Request
    except ImportError:
        logger.error("FastAPI not installed. Run: pip install fastapi")
        return None
    
    router = APIRouter(prefix="/stripe", tags=["stripe"])
    
    @router.post("/webhook", status_code=HTTPStatus.NO_CONTENT)
    async def stripe_webhook(
        request: Request,
        stripe_signature: str = Header(alias="stripe-signature"),
        adapter: StripeAdapterEnhanced = Depends(get_stripe_adapter),
        idempotency_store: IdempotencyStore = Depends(get_idempotency_store),
        tenant_resolver: TenantResolver = Depends(get_tenant_resolver),
    ):
        """
        Stripe webhook endpoint.
        
        1. Verifies signature
        2. Checks idempotency
        3. Routes to four loops
        """
        payload = await request.body()
        
        # Verify signature
        try:
            event_data = adapter.verify_webhook(payload, stripe_signature)
        except Exception as e:
            logger.warning(f"Webhook verification failed: {e}")
            raise HTTPException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                detail="Invalid signature",
            )
        
        event_id = event_data["event_id"]
        event_type = event_data["event_type"]
        data = event_data["data"]
        
        # Check idempotency
        if idempotency_store.exists(event_id):
            logger.debug(f"Duplicate webhook: {event_id}")
            return  # Already processed
        
        # Create router and route event
        event_router = WebhookEventRouter(
            adapter=adapter,
            idempotency_store=idempotency_store,
            tenant_resolver=tenant_resolver,
        )
        
        # Wire up engines (in production, these come from DI)
        # event_router.connect_billing_state_machine(...)
        # event_router.connect_entitlement_engine(...)
        # etc.
        
        result = event_router.route_event(event_id, event_type, data)
        
        if result.get("status") == "error":
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Processing failed"),
            )
        
        return  # 204 No Content
    
    return router


# =============================================================================
# Product/Price Metadata Schema
# =============================================================================

METADATA_SCHEMA = """
Stripe Product/Price Metadata Schema for KRL Billing Integration
================================================================

Product Metadata (stripe.Product.metadata):
------------------------------------------
- entitlement_api_access: "true" | "false"
- entitlement_advanced_analytics: "true" | "false"
- entitlement_custom_integrations: "true" | "false"
- entitlement_sso_saml: "true" | "false"
- entitlement_dedicated_support: "true" | "false"
- tier: "community" | "pro" | "enterprise"

Price Metadata (stripe.Price.metadata):
---------------------------------------
- limit_api_calls: "10000" | "100000" | "1000000"
- limit_ml_inferences: "1000" | "10000" | "100000"
- limit_storage_gb: "1" | "10" | "100"
- limit_team_members: "1" | "5" | "unlimited"
- tier: "community" | "pro" | "enterprise"

Subscription Metadata (stripe.Subscription.metadata):
-----------------------------------------------------
- tenant_id: "<uuid>"
- tier: "community" | "pro" | "enterprise"
- billing_cycle: "monthly" | "annual"

Customer Metadata (stripe.Customer.metadata):
---------------------------------------------
- tenant_id: "<uuid>"
- tier: "community" | "pro" | "enterprise"
- company_name: "<string>"

Connect Account Metadata (stripe.Account.metadata):
---------------------------------------------------
- tenant_id: "<uuid>"
- tier: "community" | "pro" | "enterprise"
- platform: "krl"
"""


def get_metadata_schema() -> str:
    """Return the metadata schema documentation."""
    return METADATA_SCHEMA
