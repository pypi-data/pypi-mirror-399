# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
#
# ⚠️ DEPRECATION WARNING (Dec 2025):
# This module has been moved to krl-premium-backend.
# Import from: app.services.billing.payments_adapter
# This stub remains for backward compatibility but will be removed in v2.0.
# ----------------------------------------------------------------------

from __future__ import annotations

import warnings
warnings.warn(
    "krl_data_connectors.core.billing.payments_adapter is deprecated. "
    "This module has moved to krl-premium-backend. "
    "Import from 'app.services.billing.payments_adapter' instead.",
    DeprecationWarning,
    stacklevel=2
)

"""
Payments Adapter Interface

Integrates with:
- Defense: Risk scores influence payment decisions
- Governance: Policy rules gate payment operations
- Monetization: Direct integration with billing engines
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, UTC
from decimal import Decimal
from enum import Enum
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Protocol,
    TypeVar,
    Union,
    runtime_checkable,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================

class PaymentProvider(Enum):
    """Supported payment providers."""
    STRIPE = "stripe"
    STRIPE_CONNECT = "stripe_connect"
    LAGO = "lago"
    KILL_BILL = "kill_bill"
    BILLABEAR = "billabear"
    MOCK = "mock"


class AccountType(Enum):
    """Payment provider account types (Stripe Connect specific)."""
    STANDARD = "standard"    # Full Stripe dashboard access
    EXPRESS = "express"      # Simplified onboarding
    CUSTOM = "custom"        # Full white-label control


class SubscriptionStatus(Enum):
    """Subscription status states."""
    ACTIVE = "active"
    TRIALING = "trialing"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    PAUSED = "paused"


class PaymentStatus(Enum):
    """Payment/charge status."""
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    DISPUTED = "disputed"
    CANCELED = "canceled"


class InvoiceStatus(Enum):
    """Invoice status states."""
    DRAFT = "draft"
    OPEN = "open"
    PAID = "paid"
    VOID = "void"
    UNCOLLECTIBLE = "uncollectible"


class WebhookEventType(Enum):
    """Webhook event types (provider-agnostic)."""
    # Customer events
    CUSTOMER_CREATED = "customer.created"
    CUSTOMER_UPDATED = "customer.updated"
    CUSTOMER_DELETED = "customer.deleted"
    
    # Subscription events
    SUBSCRIPTION_CREATED = "subscription.created"
    SUBSCRIPTION_UPDATED = "subscription.updated"
    SUBSCRIPTION_CANCELED = "subscription.canceled"
    SUBSCRIPTION_TRIAL_ENDING = "subscription.trial_ending"
    
    # Invoice events
    INVOICE_CREATED = "invoice.created"
    INVOICE_PAID = "invoice.paid"
    INVOICE_PAYMENT_FAILED = "invoice.payment_failed"
    INVOICE_UPCOMING = "invoice.upcoming"
    
    # Payment events
    PAYMENT_SUCCEEDED = "payment.succeeded"
    PAYMENT_FAILED = "payment.failed"
    PAYMENT_REFUNDED = "payment.refunded"
    
    # Usage events
    USAGE_RECORD_CREATED = "usage.record_created"
    
    # Connect events (Stripe specific but abstracted)
    ACCOUNT_UPDATED = "account.updated"
    PAYOUT_PAID = "payout.paid"
    
    # Unknown/custom
    UNKNOWN = "unknown"


class PriceType(Enum):
    """Pricing model types."""
    ONE_TIME = "one_time"
    RECURRING = "recurring"
    USAGE_BASED = "usage_based"
    TIERED = "tiered"
    GRADUATED = "graduated"


class BillingInterval(Enum):
    """Billing intervals."""
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


# =============================================================================
# Data Classes - Domain Models
# =============================================================================

@dataclass
class Address:
    """Customer address."""
    line1: Optional[str] = None
    line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None  # ISO 3166-1 alpha-2


@dataclass
class CustomerData:
    """Customer domain model (provider-agnostic)."""
    # Internal ID
    internal_id: str
    
    # Provider mapping
    provider: PaymentProvider = PaymentProvider.STRIPE
    provider_customer_id: Optional[str] = None
    
    # Customer info
    email: str = ""
    name: Optional[str] = None
    description: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[Address] = None
    
    # KRL-specific
    tenant_id: Optional[str] = None
    tier: str = "community"
    
    # Metadata
    metadata: Dict[str, str] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class PriceData:
    """Price/plan domain model."""
    # Internal ID
    internal_id: str
    
    # Provider mapping
    provider: PaymentProvider = PaymentProvider.STRIPE
    provider_price_id: Optional[str] = None
    provider_product_id: Optional[str] = None
    
    # Pricing info
    name: str = ""
    description: Optional[str] = None
    currency: str = "usd"
    unit_amount: int = 0  # In cents
    
    # Pricing model
    price_type: PriceType = PriceType.RECURRING
    billing_interval: Optional[BillingInterval] = BillingInterval.MONTH
    interval_count: int = 1
    
    # Usage-based pricing
    usage_type: Optional[str] = None  # "metered" or "licensed"
    aggregate_usage: Optional[str] = None  # "sum", "last_during_period", "last_ever", "max"
    tiers_mode: Optional[str] = None  # "graduated" or "volume"
    tiers: Optional[List[Dict[str, Any]]] = None
    
    # KRL-specific
    tier: str = "pro"
    feature_flags: List[str] = field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, str] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class SubscriptionData:
    """Subscription domain model."""
    # Internal ID
    internal_id: str
    
    # Provider mapping
    provider: PaymentProvider = PaymentProvider.STRIPE
    provider_subscription_id: Optional[str] = None
    provider_customer_id: Optional[str] = None
    
    # Subscription info
    customer_internal_id: str = ""
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    
    # Items
    items: List[SubscriptionItemData] = field(default_factory=list)
    
    # Billing
    currency: str = "usd"
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    
    # Trial
    trial_start: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    
    # Cancellation
    cancel_at_period_end: bool = False
    canceled_at: Optional[datetime] = None
    
    # KRL-specific
    tenant_id: Optional[str] = None
    tier: str = "pro"
    
    # Metadata
    metadata: Dict[str, str] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class SubscriptionItemData:
    """Subscription item (line item) domain model."""
    internal_id: str
    provider_item_id: Optional[str] = None
    price_internal_id: str = ""
    provider_price_id: Optional[str] = None
    quantity: int = 1
    
    # Metadata
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class UsageRecordData:
    """Usage record for metered billing."""
    # Internal ID
    internal_id: str
    
    # Provider mapping
    provider: PaymentProvider = PaymentProvider.STRIPE
    provider_usage_record_id: Optional[str] = None
    
    # Usage info
    subscription_item_id: str = ""
    quantity: int = 0
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    # Action
    action: str = "increment"  # "increment" or "set"
    
    # KRL-specific
    tenant_id: Optional[str] = None
    metric_type: Optional[str] = None  # API_CALLS, ML_INFERENCES, etc.
    
    # Metadata
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class InvoiceData:
    """Invoice domain model."""
    # Internal ID
    internal_id: str
    
    # Provider mapping
    provider: PaymentProvider = PaymentProvider.STRIPE
    provider_invoice_id: Optional[str] = None
    provider_customer_id: Optional[str] = None
    
    # Invoice info
    customer_internal_id: str = ""
    status: InvoiceStatus = InvoiceStatus.DRAFT
    
    # Amounts (in cents)
    subtotal: int = 0
    tax: int = 0
    total: int = 0
    amount_paid: int = 0
    amount_remaining: int = 0
    currency: str = "usd"
    
    # Dates
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    due_date: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    
    # URLs
    hosted_invoice_url: Optional[str] = None
    invoice_pdf: Optional[str] = None
    
    # Line items
    lines: List[InvoiceLineData] = field(default_factory=list)
    
    # KRL-specific
    tenant_id: Optional[str] = None
    tier: Optional[str] = None
    
    # Metadata
    metadata: Dict[str, str] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class InvoiceLineData:
    """Invoice line item."""
    internal_id: str
    description: str = ""
    amount: int = 0
    quantity: int = 1
    price_internal_id: Optional[str] = None
    
    # Metadata
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class PaymentData:
    """Payment/charge domain model."""
    # Internal ID
    internal_id: str
    
    # Provider mapping
    provider: PaymentProvider = PaymentProvider.STRIPE
    provider_payment_id: Optional[str] = None
    provider_customer_id: Optional[str] = None
    
    # Payment info
    customer_internal_id: str = ""
    status: PaymentStatus = PaymentStatus.PENDING
    
    # Amounts (in cents)
    amount: int = 0
    amount_refunded: int = 0
    currency: str = "usd"
    
    # Payment method
    payment_method_type: Optional[str] = None
    last_four: Optional[str] = None
    
    # Error info
    failure_code: Optional[str] = None
    failure_message: Optional[str] = None
    
    # KRL-specific
    tenant_id: Optional[str] = None
    invoice_internal_id: Optional[str] = None
    
    # Metadata
    metadata: Dict[str, str] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class RefundData:
    """Refund domain model."""
    internal_id: str
    provider: PaymentProvider = PaymentProvider.STRIPE
    provider_refund_id: Optional[str] = None
    
    payment_internal_id: str = ""
    provider_payment_id: Optional[str] = None
    
    amount: int = 0
    currency: str = "usd"
    reason: Optional[str] = None
    status: str = "pending"
    
    # Metadata
    metadata: Dict[str, str] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class WebhookEvent:
    """Webhook event domain model."""
    # Event info
    event_id: str
    event_type: WebhookEventType
    provider: PaymentProvider
    
    # Raw data
    raw_payload: Dict[str, Any] = field(default_factory=dict)
    
    # Parsed data
    object_type: Optional[str] = None  # "customer", "subscription", etc.
    object_id: Optional[str] = None
    object_data: Optional[Dict[str, Any]] = None
    
    # Processing
    processed: bool = False
    processing_error: Optional[str] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    received_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class ConnectAccount:
    """Stripe Connect account (or equivalent for other providers)."""
    internal_id: str
    provider: PaymentProvider = PaymentProvider.STRIPE_CONNECT
    provider_account_id: Optional[str] = None
    
    # Account type
    account_type: AccountType = AccountType.STANDARD
    
    # Account info
    business_name: Optional[str] = None
    email: Optional[str] = None
    country: str = "US"
    
    # Capabilities
    charges_enabled: bool = False
    payouts_enabled: bool = False
    
    # KRL-specific
    tenant_id: Optional[str] = None
    tier: str = "pro"
    
    # Onboarding
    onboarding_complete: bool = False
    onboarding_url: Optional[str] = None
    
    # Metadata
    metadata: Dict[str, str] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# Result Types
# =============================================================================

T = TypeVar("T")


@dataclass
class AdapterResult(Generic[T]):
    """Result wrapper for adapter operations."""
    success: bool
    data: Optional[T] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    provider_response: Optional[Dict[str, Any]] = None
    
    @classmethod
    def ok(cls, data: T, provider_response: Optional[Dict[str, Any]] = None) -> "AdapterResult[T]":
        """Create a successful result."""
        return cls(success=True, data=data, provider_response=provider_response)
    
    @classmethod
    def fail(
        cls, 
        error_code: str, 
        error_message: str,
        provider_response: Optional[Dict[str, Any]] = None
    ) -> "AdapterResult[T]":
        """Create a failed result."""
        return cls(
            success=False,
            error_code=error_code,
            error_message=error_message,
            provider_response=provider_response,
        )


# =============================================================================
# Adapter Configuration
# =============================================================================

@dataclass
class AdapterConfig:
    """Configuration for payment adapters."""
    # Provider
    provider: PaymentProvider = PaymentProvider.STRIPE
    
    # API credentials
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    
    # Webhook secret
    webhook_secret: Optional[str] = None
    
    # Connect settings (Stripe Connect)
    connect_enabled: bool = False
    platform_account_id: Optional[str] = None
    
    # Environment
    test_mode: bool = True
    api_version: Optional[str] = None
    
    # Timeouts
    timeout_seconds: int = 30
    max_retries: int = 3
    
    # Feature flags
    idempotency_enabled: bool = True
    auto_pagination: bool = True
    
    # KRL Integration
    tier_mapping: Dict[str, AccountType] = field(default_factory=lambda: {
        "community": AccountType.STANDARD,
        "pro": AccountType.EXPRESS,
        "enterprise": AccountType.CUSTOM,
    })
    
    # Metadata
    metadata_prefix: str = "krl_"


# =============================================================================
# Abstract Adapter Interface
# =============================================================================

class PaymentsAdapter(ABC):
    """
    Abstract base class for payment provider adapters.
    
    Implementations:
    - StripeAdapter: Stripe and Stripe Connect
    - LagoAdapter: Self-hosted Lago
    - KillBillAdapter: Kill Bill
    - MockAdapter: Testing
    
    All methods return AdapterResult for consistent error handling.
    """

    def __init__(self, config: AdapterConfig):
        self.config = config
        self._initialized = False

    @property
    @abstractmethod
    def provider(self) -> PaymentProvider:
        """Get the provider type."""
        pass

    @abstractmethod
    def initialize(self) -> AdapterResult[bool]:
        """Initialize the adapter and verify credentials."""
        pass

    @abstractmethod
    def health_check(self) -> AdapterResult[Dict[str, Any]]:
        """Check provider health/connectivity."""
        pass

    # -------------------------------------------------------------------------
    # Customer Operations
    # -------------------------------------------------------------------------

    @abstractmethod
    def create_customer(
        self,
        customer: CustomerData,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[CustomerData]:
        """
        Create a customer in the payment provider.
        
        Args:
            customer: Customer data with internal_id set
            connect_account_id: For Connect, the connected account to create on
            
        Returns:
            AdapterResult with CustomerData including provider_customer_id
        """
        pass

    @abstractmethod
    def get_customer(
        self,
        provider_customer_id: str,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[CustomerData]:
        """Retrieve a customer from the payment provider."""
        pass

    @abstractmethod
    def update_customer(
        self,
        customer: CustomerData,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[CustomerData]:
        """Update customer in the payment provider."""
        pass

    @abstractmethod
    def delete_customer(
        self,
        provider_customer_id: str,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[bool]:
        """Delete a customer from the payment provider."""
        pass

    # -------------------------------------------------------------------------
    # Subscription Operations
    # -------------------------------------------------------------------------

    @abstractmethod
    def create_subscription(
        self,
        subscription: SubscriptionData,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[SubscriptionData]:
        """
        Create a subscription.
        
        Args:
            subscription: Subscription data with items
            connect_account_id: For Connect, the connected account
            
        Returns:
            AdapterResult with SubscriptionData including provider_subscription_id
        """
        pass

    @abstractmethod
    def get_subscription(
        self,
        provider_subscription_id: str,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[SubscriptionData]:
        """Retrieve a subscription."""
        pass

    @abstractmethod
    def update_subscription(
        self,
        subscription: SubscriptionData,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[SubscriptionData]:
        """Update a subscription (change items, quantity, etc.)."""
        pass

    @abstractmethod
    def modify_subscription(
        self,
        provider_subscription_id: str,
        new_price_id: Optional[str] = None,
        quantity: Optional[int] = None,
        proration_behavior: str = "create_prorations",
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[SubscriptionData]:
        """
        Modify subscription plan/tier.
        
        Used for tier upgrades/downgrades in the Monetization Loop.
        
        Args:
            provider_subscription_id: The subscription to modify
            new_price_id: New price/plan to switch to
            quantity: New quantity
            proration_behavior: "create_prorations", "none", "always_invoice"
            connect_account_id: For Connect, the connected account
        """
        pass

    @abstractmethod
    def cancel_subscription(
        self,
        provider_subscription_id: str,
        immediately: bool = False,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[SubscriptionData]:
        """
        Cancel a subscription.
        
        Args:
            provider_subscription_id: The subscription to cancel
            immediately: If True, cancel now; else at period end
            connect_account_id: For Connect, the connected account
        """
        pass

    @abstractmethod
    def pause_subscription(
        self,
        provider_subscription_id: str,
        resume_at: Optional[datetime] = None,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[SubscriptionData]:
        """Pause a subscription (if supported)."""
        pass

    @abstractmethod
    def resume_subscription(
        self,
        provider_subscription_id: str,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[SubscriptionData]:
        """Resume a paused subscription."""
        pass

    # -------------------------------------------------------------------------
    # Usage-Based Billing
    # -------------------------------------------------------------------------

    @abstractmethod
    def record_usage(
        self,
        usage: UsageRecordData,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[UsageRecordData]:
        """
        Record usage for metered billing.
        
        Integrates with UsageMeter from the Monetization Loop.
        
        Args:
            usage: Usage record with subscription_item_id and quantity
            connect_account_id: For Connect, the connected account
        """
        pass

    @abstractmethod
    def get_usage_summary(
        self,
        provider_subscription_item_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[Dict[str, Any]]:
        """Get usage summary for a subscription item."""
        pass

    # -------------------------------------------------------------------------
    # Pricing Operations
    # -------------------------------------------------------------------------

    @abstractmethod
    def create_price(
        self,
        price: PriceData,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[PriceData]:
        """Create a price/plan."""
        pass

    @abstractmethod
    def get_price(
        self,
        provider_price_id: str,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[PriceData]:
        """Get a price/plan."""
        pass

    @abstractmethod
    def update_price(
        self,
        price: PriceData,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[PriceData]:
        """
        Update price metadata (prices are usually immutable).
        
        For dynamic pricing from RiskPricingEngine, create new prices.
        """
        pass

    @abstractmethod
    def list_prices(
        self,
        product_id: Optional[str] = None,
        active: bool = True,
        limit: int = 100,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[List[PriceData]]:
        """List prices, optionally filtered by product."""
        pass

    # -------------------------------------------------------------------------
    # Invoice Operations
    # -------------------------------------------------------------------------

    @abstractmethod
    def get_invoice(
        self,
        provider_invoice_id: str,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[InvoiceData]:
        """Get an invoice."""
        pass

    @abstractmethod
    def list_invoices(
        self,
        provider_customer_id: Optional[str] = None,
        status: Optional[InvoiceStatus] = None,
        limit: int = 100,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[List[InvoiceData]]:
        """List invoices for a customer."""
        pass

    @abstractmethod
    def finalize_invoice(
        self,
        provider_invoice_id: str,
        auto_advance: bool = True,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[InvoiceData]:
        """Finalize a draft invoice."""
        pass

    @abstractmethod
    def pay_invoice(
        self,
        provider_invoice_id: str,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[InvoiceData]:
        """Attempt to pay an open invoice."""
        pass

    @abstractmethod
    def void_invoice(
        self,
        provider_invoice_id: str,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[InvoiceData]:
        """Void an invoice."""
        pass

    # -------------------------------------------------------------------------
    # Payment Operations
    # -------------------------------------------------------------------------

    @abstractmethod
    def create_payment(
        self,
        amount: int,
        currency: str,
        customer_id: str,
        payment_method_id: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[PaymentData]:
        """Create a one-time payment/charge."""
        pass

    @abstractmethod
    def get_payment(
        self,
        provider_payment_id: str,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[PaymentData]:
        """Get a payment."""
        pass

    @abstractmethod
    def refund_payment(
        self,
        provider_payment_id: str,
        amount: Optional[int] = None,  # None = full refund
        reason: Optional[str] = None,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[RefundData]:
        """
        Refund a payment (full or partial).
        
        Args:
            provider_payment_id: The payment to refund
            amount: Amount in cents (None for full refund)
            reason: "duplicate", "fraudulent", "requested_by_customer"
            connect_account_id: For Connect, the connected account
        """
        pass

    # -------------------------------------------------------------------------
    # Webhook Handling
    # -------------------------------------------------------------------------

    @abstractmethod
    def verify_webhook(
        self,
        payload: bytes,
        signature: str,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[bool]:
        """
        Verify webhook signature.
        
        Args:
            payload: Raw webhook payload bytes
            signature: Webhook signature header
        """
        pass

    @abstractmethod
    def parse_webhook(
        self,
        payload: bytes,
        signature: str,
    ) -> AdapterResult[WebhookEvent]:
        """
        Parse and verify a webhook event.
        
        Returns a provider-agnostic WebhookEvent.
        """
        pass

    @abstractmethod
    def handle_webhook(
        self,
        event: WebhookEvent,
    ) -> AdapterResult[Dict[str, Any]]:
        """
        Handle a webhook event.
        
        Default implementation routes to specific handlers.
        Override for custom handling.
        
        Returns processing result.
        """
        pass

    # -------------------------------------------------------------------------
    # Connect Operations (Stripe Connect specific)
    # -------------------------------------------------------------------------

    @abstractmethod
    def create_connect_account(
        self,
        account: ConnectAccount,
    ) -> AdapterResult[ConnectAccount]:
        """
        Create a Connect account (Stripe Connect).
        
        Maps KRL tiers to account types:
        - Community → Standard
        - Pro → Express
        - Enterprise → Custom
        """
        pass

    @abstractmethod
    def get_connect_account(
        self,
        provider_account_id: str,
    ) -> AdapterResult[ConnectAccount]:
        """Get a Connect account."""
        pass

    @abstractmethod
    def create_account_link(
        self,
        provider_account_id: str,
        refresh_url: str,
        return_url: str,
        link_type: str = "account_onboarding",
    ) -> AdapterResult[str]:
        """
        Create an account link for Connect onboarding.
        
        Returns the URL for the account holder to complete onboarding.
        """
        pass

    @abstractmethod
    def create_login_link(
        self,
        provider_account_id: str,
    ) -> AdapterResult[str]:
        """
        Create a login link for Express/Standard dashboard.
        
        Returns URL for account holder to access their dashboard.
        """
        pass

    # -------------------------------------------------------------------------
    # Checkout Operations
    # -------------------------------------------------------------------------

    @abstractmethod
    def create_checkout_session(
        self,
        price_ids: List[str],
        customer_id: Optional[str] = None,
        success_url: str = "",
        cancel_url: str = "",
        mode: str = "subscription",  # "payment", "subscription", "setup"
        metadata: Optional[Dict[str, str]] = None,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[Dict[str, Any]]:
        """
        Create a checkout session for hosted payment page.
        
        Returns session ID and URL.
        """
        pass

    @abstractmethod
    def create_billing_portal_session(
        self,
        customer_id: str,
        return_url: str,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[str]:
        """
        Create a billing portal session.
        
        Returns URL for customer self-service portal.
        """
        pass


# =============================================================================
# Protocol for Webhook Handlers
# =============================================================================

@runtime_checkable
class WebhookHandler(Protocol):
    """Protocol for webhook event handlers."""
    
    def __call__(self, event: WebhookEvent) -> AdapterResult[Dict[str, Any]]:
        """Handle a webhook event."""
        ...


# =============================================================================
# Adapter Registry
# =============================================================================

class AdapterRegistry:
    """
    Registry for payment adapters.
    
    Enables runtime selection of payment provider.
    """

    _adapters: Dict[PaymentProvider, type] = {}
    _instances: Dict[str, PaymentsAdapter] = {}

    @classmethod
    def register(cls, provider: PaymentProvider, adapter_class: type) -> None:
        """Register an adapter class for a provider."""
        cls._adapters[provider] = adapter_class
        logger.info(f"Registered adapter for {provider.value}")

    @classmethod
    def get_adapter_class(cls, provider: PaymentProvider) -> Optional[type]:
        """Get the adapter class for a provider."""
        return cls._adapters.get(provider)

    @classmethod
    def create_adapter(
        cls, 
        config: AdapterConfig,
        instance_key: Optional[str] = None,
    ) -> Optional[PaymentsAdapter]:
        """
        Create an adapter instance.
        
        Args:
            config: Adapter configuration
            instance_key: Optional key for caching instances
            
        Returns:
            PaymentsAdapter instance or None if provider not registered
        """
        # Check cache
        if instance_key and instance_key in cls._instances:
            return cls._instances[instance_key]
        
        adapter_class = cls._adapters.get(config.provider)
        if not adapter_class:
            logger.error(f"No adapter registered for {config.provider.value}")
            return None
        
        adapter = adapter_class(config)
        
        # Cache if key provided
        if instance_key:
            cls._instances[instance_key] = adapter
        
        return adapter

    @classmethod
    def list_providers(cls) -> List[PaymentProvider]:
        """List registered providers."""
        return list(cls._adapters.keys())


# =============================================================================
# ID Mapping Store (Abstract)
# =============================================================================

class IDMappingStore(ABC):
    """
    Abstract store for mapping internal IDs to provider IDs.
    
    Implementations could use:
    - In-memory dict
    - Redis
    - Database
    
    This enables:
    - Multi-provider support
    - Provider migration
    - ID correlation across systems
    """

    @abstractmethod
    def store_mapping(
        self,
        entity_type: str,  # "customer", "subscription", etc.
        internal_id: str,
        provider: PaymentProvider,
        provider_id: str,
    ) -> None:
        """Store an ID mapping."""
        pass

    @abstractmethod
    def get_provider_id(
        self,
        entity_type: str,
        internal_id: str,
        provider: PaymentProvider,
    ) -> Optional[str]:
        """Get provider ID from internal ID."""
        pass

    @abstractmethod
    def get_internal_id(
        self,
        entity_type: str,
        provider: PaymentProvider,
        provider_id: str,
    ) -> Optional[str]:
        """Get internal ID from provider ID."""
        pass

    @abstractmethod
    def delete_mapping(
        self,
        entity_type: str,
        internal_id: str,
        provider: Optional[PaymentProvider] = None,
    ) -> None:
        """Delete ID mapping(s)."""
        pass


class InMemoryIDMappingStore(IDMappingStore):
    """In-memory implementation of ID mapping store."""

    def __init__(self):
        # {entity_type: {internal_id: {provider: provider_id}}}
        self._forward: Dict[str, Dict[str, Dict[PaymentProvider, str]]] = {}
        # {entity_type: {provider: {provider_id: internal_id}}}
        self._reverse: Dict[str, Dict[PaymentProvider, Dict[str, str]]] = {}

    def store_mapping(
        self,
        entity_type: str,
        internal_id: str,
        provider: PaymentProvider,
        provider_id: str,
    ) -> None:
        # Forward mapping
        if entity_type not in self._forward:
            self._forward[entity_type] = {}
        if internal_id not in self._forward[entity_type]:
            self._forward[entity_type][internal_id] = {}
        self._forward[entity_type][internal_id][provider] = provider_id
        
        # Reverse mapping
        if entity_type not in self._reverse:
            self._reverse[entity_type] = {}
        if provider not in self._reverse[entity_type]:
            self._reverse[entity_type][provider] = {}
        self._reverse[entity_type][provider][provider_id] = internal_id

    def get_provider_id(
        self,
        entity_type: str,
        internal_id: str,
        provider: PaymentProvider,
    ) -> Optional[str]:
        return self._forward.get(entity_type, {}).get(internal_id, {}).get(provider)

    def get_internal_id(
        self,
        entity_type: str,
        provider: PaymentProvider,
        provider_id: str,
    ) -> Optional[str]:
        return self._reverse.get(entity_type, {}).get(provider, {}).get(provider_id)

    def delete_mapping(
        self,
        entity_type: str,
        internal_id: str,
        provider: Optional[PaymentProvider] = None,
    ) -> None:
        if entity_type not in self._forward:
            return
        
        if internal_id not in self._forward[entity_type]:
            return
        
        if provider:
            # Delete specific provider mapping
            provider_id = self._forward[entity_type][internal_id].pop(provider, None)
            if provider_id and entity_type in self._reverse:
                if provider in self._reverse[entity_type]:
                    self._reverse[entity_type][provider].pop(provider_id, None)
        else:
            # Delete all provider mappings for this internal ID
            for prov, prov_id in self._forward[entity_type][internal_id].items():
                if entity_type in self._reverse and prov in self._reverse[entity_type]:
                    self._reverse[entity_type][prov].pop(prov_id, None)
            del self._forward[entity_type][internal_id]


# =============================================================================
# Default Configuration
# =============================================================================

DEFAULT_ADAPTER_CONFIG = AdapterConfig(
    provider=PaymentProvider.STRIPE,
    test_mode=True,
    timeout_seconds=30,
    max_retries=3,
    idempotency_enabled=True,
    tier_mapping={
        "community": AccountType.STANDARD,
        "pro": AccountType.EXPRESS,
        "enterprise": AccountType.CUSTOM,
    },
)


# =============================================================================
# Factory Functions
# =============================================================================

def create_adapter_config(
    provider: PaymentProvider = PaymentProvider.STRIPE,
    api_key: Optional[str] = None,
    webhook_secret: Optional[str] = None,
    test_mode: bool = True,
    connect_enabled: bool = False,
    **kwargs,
) -> AdapterConfig:
    """
    Factory function to create adapter configuration.
    
    Args:
        provider: Payment provider
        api_key: API key/secret
        webhook_secret: Webhook signing secret
        test_mode: Use test/sandbox mode
        connect_enabled: Enable Connect features
        **kwargs: Additional config options
        
    Returns:
        AdapterConfig instance
    """
    return AdapterConfig(
        provider=provider,
        api_key=api_key,
        webhook_secret=webhook_secret,
        test_mode=test_mode,
        connect_enabled=connect_enabled,
        **kwargs,
    )


def create_payments_adapter(
    config: AdapterConfig,
    instance_key: Optional[str] = None,
) -> Optional[PaymentsAdapter]:
    """
    Factory function to create a payments adapter.
    
    Args:
        config: Adapter configuration
        instance_key: Optional key for caching
        
    Returns:
        PaymentsAdapter instance or None
    """
    return AdapterRegistry.create_adapter(config, instance_key)


def create_id_mapping_store() -> IDMappingStore:
    """Create an ID mapping store (in-memory by default)."""
    return InMemoryIDMappingStore()
