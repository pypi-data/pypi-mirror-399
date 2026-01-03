# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""
Stripe Adapter - DEPRECATED

⚠️ DEPRECATION WARNING (Dec 2025):
This module has been moved to krl-premium-backend.
Import from: app.services.billing.stripe_adapter

This stub remains for backward compatibility but will be removed in v2.0.
"""

from __future__ import annotations

import warnings
warnings.warn(
    "krl_data_connectors.core.billing.stripe_adapter is deprecated. "
    "This module has moved to krl-premium-backend. "
    "Import from 'app.services.billing.stripe_adapter' instead.",
    DeprecationWarning,
    stacklevel=2
)

import logging
import os
from datetime import datetime, UTC
from decimal import Decimal
from typing import Any, Dict, List, Optional

from .payments_adapter import (
    PaymentsAdapter,
    PaymentProvider,
    AdapterConfig,
    AdapterResult,
    AccountType,
    SubscriptionStatus,
    PaymentStatus,
    InvoiceStatus,
    WebhookEventType,
    CustomerData,
    PriceData,
    SubscriptionData,
    SubscriptionItemData,
    UsageRecordData,
    InvoiceData,
    PaymentData,
    RefundData,
    WebhookEvent,
    ConnectAccount,
    AdapterRegistry,
)

logger = logging.getLogger(__name__)

# Conditional import for stripe
try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    stripe = None


class StripeAdapter(PaymentsAdapter):
    """
    Stripe payment adapter using stripe-python SDK.
    
    Supports:
    - Stripe API for direct billing
    - Stripe Connect for marketplace/platform billing
    - Usage-based (metered) billing
    - Webhooks with signature verification
    """

    def __init__(self, config: AdapterConfig):
        super().__init__(config)
        self._stripe = None
        
    @property
    def provider(self) -> PaymentProvider:
        return PaymentProvider.STRIPE

    def initialize(self) -> AdapterResult[bool]:
        """Initialize Stripe SDK with API key."""
        if not STRIPE_AVAILABLE:
            return AdapterResult.fail(
                "stripe_not_installed",
                "stripe-python package not installed. Run: pip install stripe"
            )
        
        api_key = self.config.api_key or os.getenv("STRIPE_API_KEY")
        if not api_key:
            return AdapterResult.fail("no_api_key", "Stripe API key not configured")
        
        stripe.api_key = api_key
        if self.config.api_version:
            stripe.api_version = self.config.api_version
        
        self._stripe = stripe
        self._initialized = True
        logger.info("StripeAdapter initialized")
        return AdapterResult.ok(True)

    def health_check(self) -> AdapterResult[Dict[str, Any]]:
        """Verify Stripe connectivity."""
        if not self._initialized:
            init_result = self.initialize()
            if not init_result.success:
                return AdapterResult.fail(init_result.error_code, init_result.error_message)
        
        try:
            # Simple balance check to verify credentials
            balance = stripe.Balance.retrieve()
            return AdapterResult.ok({
                "provider": "stripe",
                "connected": True,
                "test_mode": self.config.test_mode,
            })
        except stripe.error.AuthenticationError as e:
            return AdapterResult.fail("auth_error", str(e))
        except Exception as e:
            return AdapterResult.fail("health_check_failed", str(e))

    # -------------------------------------------------------------------------
    # Customer Operations
    # -------------------------------------------------------------------------

    def create_customer(
        self,
        customer: CustomerData,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[CustomerData]:
        """Create a Stripe customer."""
        if not self._initialized:
            self.initialize()
        
        try:
            params = {
                "email": customer.email,
                "name": customer.name,
                "description": customer.description,
                "phone": customer.phone,
                "metadata": {
                    **customer.metadata,
                    f"{self.config.metadata_prefix}internal_id": customer.internal_id,
                    f"{self.config.metadata_prefix}tenant_id": customer.tenant_id or "",
                    f"{self.config.metadata_prefix}tier": customer.tier,
                },
            }
            
            if customer.address:
                params["address"] = {
                    "line1": customer.address.line1,
                    "line2": customer.address.line2,
                    "city": customer.address.city,
                    "state": customer.address.state,
                    "postal_code": customer.address.postal_code,
                    "country": customer.address.country,
                }
            
            # Handle Connect account
            kwargs = {}
            if connect_account_id:
                kwargs["stripe_account"] = connect_account_id
            
            stripe_customer = stripe.Customer.create(**params, **kwargs)
            
            customer.provider = PaymentProvider.STRIPE
            customer.provider_customer_id = stripe_customer.id
            customer.updated_at = datetime.now(UTC)
            
            logger.info(f"Created Stripe customer {stripe_customer.id}")
            return AdapterResult.ok(customer, {"stripe_id": stripe_customer.id})
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating customer: {e}")
            return AdapterResult.fail("stripe_error", str(e))

    def get_customer(
        self,
        provider_customer_id: str,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[CustomerData]:
        """Retrieve a Stripe customer."""
        if not self._initialized:
            self.initialize()
        
        try:
            kwargs = {}
            if connect_account_id:
                kwargs["stripe_account"] = connect_account_id
            
            sc = stripe.Customer.retrieve(provider_customer_id, **kwargs)
            
            customer = CustomerData(
                internal_id=sc.metadata.get(f"{self.config.metadata_prefix}internal_id", ""),
                provider=PaymentProvider.STRIPE,
                provider_customer_id=sc.id,
                email=sc.email or "",
                name=sc.name,
                description=sc.description,
                phone=sc.phone,
                tenant_id=sc.metadata.get(f"{self.config.metadata_prefix}tenant_id"),
                tier=sc.metadata.get(f"{self.config.metadata_prefix}tier", "community"),
                metadata=dict(sc.metadata) if sc.metadata else {},
            )
            
            return AdapterResult.ok(customer)
            
        except stripe.error.StripeError as e:
            return AdapterResult.fail("stripe_error", str(e))

    def update_customer(
        self,
        customer: CustomerData,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[CustomerData]:
        """Update a Stripe customer."""
        if not self._initialized:
            self.initialize()
        
        if not customer.provider_customer_id:
            return AdapterResult.fail("no_provider_id", "Customer has no provider ID")
        
        try:
            params = {
                "email": customer.email,
                "name": customer.name,
                "description": customer.description,
                "metadata": {
                    **customer.metadata,
                    f"{self.config.metadata_prefix}tier": customer.tier,
                },
            }
            
            kwargs = {}
            if connect_account_id:
                kwargs["stripe_account"] = connect_account_id
            
            stripe.Customer.modify(customer.provider_customer_id, **params, **kwargs)
            customer.updated_at = datetime.now(UTC)
            
            return AdapterResult.ok(customer)
            
        except stripe.error.StripeError as e:
            return AdapterResult.fail("stripe_error", str(e))

    def delete_customer(
        self,
        provider_customer_id: str,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[bool]:
        """Delete a Stripe customer."""
        if not self._initialized:
            self.initialize()
        
        try:
            kwargs = {}
            if connect_account_id:
                kwargs["stripe_account"] = connect_account_id
            
            stripe.Customer.delete(provider_customer_id, **kwargs)
            return AdapterResult.ok(True)
            
        except stripe.error.StripeError as e:
            return AdapterResult.fail("stripe_error", str(e))

    # -------------------------------------------------------------------------
    # Subscription Operations
    # -------------------------------------------------------------------------

    def create_subscription(
        self,
        subscription: SubscriptionData,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[SubscriptionData]:
        """Create a Stripe subscription."""
        if not self._initialized:
            self.initialize()
        
        try:
            items = []
            for item in subscription.items:
                item_data = {"price": item.provider_price_id}
                if item.quantity:
                    item_data["quantity"] = item.quantity
                items.append(item_data)
            
            params = {
                "customer": subscription.provider_customer_id,
                "items": items,
                "metadata": {
                    **subscription.metadata,
                    f"{self.config.metadata_prefix}internal_id": subscription.internal_id,
                    f"{self.config.metadata_prefix}tenant_id": subscription.tenant_id or "",
                    f"{self.config.metadata_prefix}tier": subscription.tier,
                },
            }
            
            if subscription.trial_end:
                params["trial_end"] = int(subscription.trial_end.timestamp())
            
            kwargs = {}
            if connect_account_id:
                kwargs["stripe_account"] = connect_account_id
            
            ss = stripe.Subscription.create(**params, **kwargs)
            
            subscription.provider = PaymentProvider.STRIPE
            subscription.provider_subscription_id = ss.id
            subscription.status = self._map_subscription_status(ss.status)
            subscription.current_period_start = datetime.fromtimestamp(ss.current_period_start)
            subscription.current_period_end = datetime.fromtimestamp(ss.current_period_end)
            
            # Map item IDs
            for i, si in enumerate(ss["items"]["data"]):
                if i < len(subscription.items):
                    subscription.items[i].provider_item_id = si.id
            
            logger.info(f"Created Stripe subscription {ss.id}")
            return AdapterResult.ok(subscription)
            
        except stripe.error.StripeError as e:
            return AdapterResult.fail("stripe_error", str(e))

    def get_subscription(
        self,
        provider_subscription_id: str,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[SubscriptionData]:
        """Get a Stripe subscription."""
        if not self._initialized:
            self.initialize()
        
        try:
            kwargs = {}
            if connect_account_id:
                kwargs["stripe_account"] = connect_account_id
            
            ss = stripe.Subscription.retrieve(provider_subscription_id, **kwargs)
            
            items = []
            for si in ss["items"]["data"]:
                items.append(SubscriptionItemData(
                    internal_id="",
                    provider_item_id=si.id,
                    provider_price_id=si.price.id,
                    quantity=si.quantity or 1,
                ))
            
            sub = SubscriptionData(
                internal_id=ss.metadata.get(f"{self.config.metadata_prefix}internal_id", ""),
                provider=PaymentProvider.STRIPE,
                provider_subscription_id=ss.id,
                provider_customer_id=ss.customer,
                status=self._map_subscription_status(ss.status),
                items=items,
                current_period_start=datetime.fromtimestamp(ss.current_period_start),
                current_period_end=datetime.fromtimestamp(ss.current_period_end),
                tenant_id=ss.metadata.get(f"{self.config.metadata_prefix}tenant_id"),
                tier=ss.metadata.get(f"{self.config.metadata_prefix}tier", "pro"),
            )
            
            return AdapterResult.ok(sub)
            
        except stripe.error.StripeError as e:
            return AdapterResult.fail("stripe_error", str(e))

    def update_subscription(
        self,
        subscription: SubscriptionData,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[SubscriptionData]:
        """Update subscription metadata."""
        if not self._initialized:
            self.initialize()
        
        try:
            kwargs = {}
            if connect_account_id:
                kwargs["stripe_account"] = connect_account_id
            
            stripe.Subscription.modify(
                subscription.provider_subscription_id,
                metadata={
                    **subscription.metadata,
                    f"{self.config.metadata_prefix}tier": subscription.tier,
                },
                **kwargs
            )
            
            return AdapterResult.ok(subscription)
            
        except stripe.error.StripeError as e:
            return AdapterResult.fail("stripe_error", str(e))

    def modify_subscription(
        self,
        provider_subscription_id: str,
        new_price_id: Optional[str] = None,
        quantity: Optional[int] = None,
        proration_behavior: str = "create_prorations",
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[SubscriptionData]:
        """Modify subscription (upgrade/downgrade tier)."""
        if not self._initialized:
            self.initialize()
        
        try:
            kwargs = {}
            if connect_account_id:
                kwargs["stripe_account"] = connect_account_id
            
            # Get current subscription
            ss = stripe.Subscription.retrieve(provider_subscription_id, **kwargs)
            
            if not ss["items"]["data"]:
                return AdapterResult.fail("no_items", "Subscription has no items")
            
            item_id = ss["items"]["data"][0].id
            
            update_params = {"proration_behavior": proration_behavior}
            
            if new_price_id:
                update_params["items"] = [{"id": item_id, "price": new_price_id}]
            
            if quantity is not None:
                if "items" not in update_params:
                    update_params["items"] = [{"id": item_id}]
                update_params["items"][0]["quantity"] = quantity
            
            updated = stripe.Subscription.modify(provider_subscription_id, **update_params, **kwargs)
            
            return self.get_subscription(provider_subscription_id, connect_account_id)
            
        except stripe.error.StripeError as e:
            return AdapterResult.fail("stripe_error", str(e))

    def cancel_subscription(
        self,
        provider_subscription_id: str,
        immediately: bool = False,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[SubscriptionData]:
        """Cancel a subscription."""
        if not self._initialized:
            self.initialize()
        
        try:
            kwargs = {}
            if connect_account_id:
                kwargs["stripe_account"] = connect_account_id
            
            if immediately:
                stripe.Subscription.delete(provider_subscription_id, **kwargs)
            else:
                stripe.Subscription.modify(
                    provider_subscription_id,
                    cancel_at_period_end=True,
                    **kwargs
                )
            
            return self.get_subscription(provider_subscription_id, connect_account_id)
            
        except stripe.error.StripeError as e:
            return AdapterResult.fail("stripe_error", str(e))

    def pause_subscription(
        self,
        provider_subscription_id: str,
        resume_at: Optional[datetime] = None,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[SubscriptionData]:
        """Pause subscription (via pause_collection)."""
        if not self._initialized:
            self.initialize()
        
        try:
            kwargs = {}
            if connect_account_id:
                kwargs["stripe_account"] = connect_account_id
            
            pause_params = {"behavior": "void"}
            if resume_at:
                pause_params["resumes_at"] = int(resume_at.timestamp())
            
            stripe.Subscription.modify(
                provider_subscription_id,
                pause_collection=pause_params,
                **kwargs
            )
            
            return self.get_subscription(provider_subscription_id, connect_account_id)
            
        except stripe.error.StripeError as e:
            return AdapterResult.fail("stripe_error", str(e))

    def resume_subscription(
        self,
        provider_subscription_id: str,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[SubscriptionData]:
        """Resume paused subscription."""
        if not self._initialized:
            self.initialize()
        
        try:
            kwargs = {}
            if connect_account_id:
                kwargs["stripe_account"] = connect_account_id
            
            stripe.Subscription.modify(
                provider_subscription_id,
                pause_collection="",
                **kwargs
            )
            
            return self.get_subscription(provider_subscription_id, connect_account_id)
            
        except stripe.error.StripeError as e:
            return AdapterResult.fail("stripe_error", str(e))

    # -------------------------------------------------------------------------
    # Usage-Based Billing
    # -------------------------------------------------------------------------

    def record_usage(
        self,
        usage: UsageRecordData,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[UsageRecordData]:
        """Record usage for metered billing."""
        if not self._initialized:
            self.initialize()
        
        try:
            kwargs = {}
            if connect_account_id:
                kwargs["stripe_account"] = connect_account_id
            
            params = {
                "quantity": usage.quantity,
                "timestamp": int(usage.timestamp.timestamp()),
                "action": usage.action,
            }
            
            ur = stripe.SubscriptionItem.create_usage_record(
                usage.subscription_item_id,
                **params,
                **kwargs
            )
            
            usage.provider = PaymentProvider.STRIPE
            usage.provider_usage_record_id = ur.id
            
            logger.debug(f"Recorded usage: {usage.quantity} for {usage.subscription_item_id}")
            return AdapterResult.ok(usage)
            
        except stripe.error.StripeError as e:
            return AdapterResult.fail("stripe_error", str(e))

    def get_usage_summary(
        self,
        provider_subscription_item_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[Dict[str, Any]]:
        """Get usage summary for subscription item."""
        if not self._initialized:
            self.initialize()
        
        try:
            kwargs = {}
            if connect_account_id:
                kwargs["stripe_account"] = connect_account_id
            
            summaries = stripe.SubscriptionItem.list_usage_record_summaries(
                provider_subscription_item_id,
                limit=1,
                **kwargs
            )
            
            if summaries.data:
                s = summaries.data[0]
                return AdapterResult.ok({
                    "total_usage": s.total_usage,
                    "period_start": s.period.start,
                    "period_end": s.period.end,
                })
            
            return AdapterResult.ok({"total_usage": 0})
            
        except stripe.error.StripeError as e:
            return AdapterResult.fail("stripe_error", str(e))

    # -------------------------------------------------------------------------
    # Pricing
    # -------------------------------------------------------------------------

    def create_price(
        self,
        price: PriceData,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[PriceData]:
        """Create a Stripe price."""
        if not self._initialized:
            self.initialize()
        
        try:
            params = {
                "currency": price.currency,
                "unit_amount": price.unit_amount,
                "product": price.provider_product_id,
                "metadata": {
                    **price.metadata,
                    f"{self.config.metadata_prefix}internal_id": price.internal_id,
                    f"{self.config.metadata_prefix}tier": price.tier,
                },
            }
            
            if price.price_type.value == "recurring":
                params["recurring"] = {
                    "interval": price.billing_interval.value if price.billing_interval else "month",
                    "interval_count": price.interval_count,
                }
                if price.usage_type:
                    params["recurring"]["usage_type"] = price.usage_type
            
            kwargs = {}
            if connect_account_id:
                kwargs["stripe_account"] = connect_account_id
            
            sp = stripe.Price.create(**params, **kwargs)
            
            price.provider = PaymentProvider.STRIPE
            price.provider_price_id = sp.id
            
            return AdapterResult.ok(price)
            
        except stripe.error.StripeError as e:
            return AdapterResult.fail("stripe_error", str(e))

    def get_price(
        self,
        provider_price_id: str,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[PriceData]:
        """Get a Stripe price."""
        if not self._initialized:
            self.initialize()
        
        try:
            kwargs = {}
            if connect_account_id:
                kwargs["stripe_account"] = connect_account_id
            
            sp = stripe.Price.retrieve(provider_price_id, **kwargs)
            
            price = PriceData(
                internal_id=sp.metadata.get(f"{self.config.metadata_prefix}internal_id", ""),
                provider=PaymentProvider.STRIPE,
                provider_price_id=sp.id,
                provider_product_id=sp.product,
                currency=sp.currency,
                unit_amount=sp.unit_amount or 0,
                tier=sp.metadata.get(f"{self.config.metadata_prefix}tier", "pro"),
            )
            
            return AdapterResult.ok(price)
            
        except stripe.error.StripeError as e:
            return AdapterResult.fail("stripe_error", str(e))

    def update_price(
        self,
        price: PriceData,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[PriceData]:
        """Update price metadata (Stripe prices are immutable)."""
        if not self._initialized:
            self.initialize()
        
        try:
            kwargs = {}
            if connect_account_id:
                kwargs["stripe_account"] = connect_account_id
            
            stripe.Price.modify(
                price.provider_price_id,
                metadata=price.metadata,
                **kwargs
            )
            
            return AdapterResult.ok(price)
            
        except stripe.error.StripeError as e:
            return AdapterResult.fail("stripe_error", str(e))

    def list_prices(
        self,
        product_id: Optional[str] = None,
        active: bool = True,
        limit: int = 100,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[List[PriceData]]:
        """List Stripe prices."""
        if not self._initialized:
            self.initialize()
        
        try:
            params = {"active": active, "limit": limit}
            if product_id:
                params["product"] = product_id
            
            kwargs = {}
            if connect_account_id:
                kwargs["stripe_account"] = connect_account_id
            
            prices = stripe.Price.list(**params, **kwargs)
            
            result = []
            for sp in prices.data:
                result.append(PriceData(
                    internal_id=sp.metadata.get(f"{self.config.metadata_prefix}internal_id", ""),
                    provider=PaymentProvider.STRIPE,
                    provider_price_id=sp.id,
                    provider_product_id=sp.product,
                    currency=sp.currency,
                    unit_amount=sp.unit_amount or 0,
                ))
            
            return AdapterResult.ok(result)
            
        except stripe.error.StripeError as e:
            return AdapterResult.fail("stripe_error", str(e))

    # -------------------------------------------------------------------------
    # Invoice Operations
    # -------------------------------------------------------------------------

    def get_invoice(
        self,
        provider_invoice_id: str,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[InvoiceData]:
        """Get a Stripe invoice."""
        if not self._initialized:
            self.initialize()
        
        try:
            kwargs = {}
            if connect_account_id:
                kwargs["stripe_account"] = connect_account_id
            
            si = stripe.Invoice.retrieve(provider_invoice_id, **kwargs)
            
            invoice = InvoiceData(
                internal_id="",
                provider=PaymentProvider.STRIPE,
                provider_invoice_id=si.id,
                provider_customer_id=si.customer,
                status=self._map_invoice_status(si.status),
                subtotal=si.subtotal or 0,
                tax=si.tax or 0,
                total=si.total or 0,
                amount_paid=si.amount_paid or 0,
                amount_remaining=si.amount_remaining or 0,
                currency=si.currency,
                hosted_invoice_url=si.hosted_invoice_url,
                invoice_pdf=si.invoice_pdf,
            )
            
            return AdapterResult.ok(invoice)
            
        except stripe.error.StripeError as e:
            return AdapterResult.fail("stripe_error", str(e))

    def list_invoices(
        self,
        provider_customer_id: Optional[str] = None,
        status: Optional[InvoiceStatus] = None,
        limit: int = 100,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[List[InvoiceData]]:
        """List invoices."""
        if not self._initialized:
            self.initialize()
        
        try:
            params = {"limit": limit}
            if provider_customer_id:
                params["customer"] = provider_customer_id
            if status:
                params["status"] = status.value
            
            kwargs = {}
            if connect_account_id:
                kwargs["stripe_account"] = connect_account_id
            
            invoices = stripe.Invoice.list(**params, **kwargs)
            
            result = []
            for si in invoices.data:
                result.append(InvoiceData(
                    internal_id="",
                    provider=PaymentProvider.STRIPE,
                    provider_invoice_id=si.id,
                    provider_customer_id=si.customer,
                    status=self._map_invoice_status(si.status),
                    total=si.total or 0,
                    currency=si.currency,
                ))
            
            return AdapterResult.ok(result)
            
        except stripe.error.StripeError as e:
            return AdapterResult.fail("stripe_error", str(e))

    def finalize_invoice(
        self,
        provider_invoice_id: str,
        auto_advance: bool = True,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[InvoiceData]:
        """Finalize a draft invoice."""
        if not self._initialized:
            self.initialize()
        
        try:
            kwargs = {}
            if connect_account_id:
                kwargs["stripe_account"] = connect_account_id
            
            stripe.Invoice.finalize_invoice(
                provider_invoice_id,
                auto_advance=auto_advance,
                **kwargs
            )
            
            return self.get_invoice(provider_invoice_id, connect_account_id)
            
        except stripe.error.StripeError as e:
            return AdapterResult.fail("stripe_error", str(e))

    def pay_invoice(
        self,
        provider_invoice_id: str,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[InvoiceData]:
        """Pay an open invoice."""
        if not self._initialized:
            self.initialize()
        
        try:
            kwargs = {}
            if connect_account_id:
                kwargs["stripe_account"] = connect_account_id
            
            stripe.Invoice.pay(provider_invoice_id, **kwargs)
            return self.get_invoice(provider_invoice_id, connect_account_id)
            
        except stripe.error.StripeError as e:
            return AdapterResult.fail("stripe_error", str(e))

    def void_invoice(
        self,
        provider_invoice_id: str,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[InvoiceData]:
        """Void an invoice."""
        if not self._initialized:
            self.initialize()
        
        try:
            kwargs = {}
            if connect_account_id:
                kwargs["stripe_account"] = connect_account_id
            
            stripe.Invoice.void_invoice(provider_invoice_id, **kwargs)
            return self.get_invoice(provider_invoice_id, connect_account_id)
            
        except stripe.error.StripeError as e:
            return AdapterResult.fail("stripe_error", str(e))

    # -------------------------------------------------------------------------
    # Payment Operations
    # -------------------------------------------------------------------------

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
        """Create a payment intent."""
        if not self._initialized:
            self.initialize()
        
        try:
            params = {
                "amount": amount,
                "currency": currency,
                "customer": customer_id,
                "description": description,
                "metadata": metadata or {},
            }
            
            if payment_method_id:
                params["payment_method"] = payment_method_id
                params["confirm"] = True
            
            kwargs = {}
            if connect_account_id:
                kwargs["stripe_account"] = connect_account_id
            
            pi = stripe.PaymentIntent.create(**params, **kwargs)
            
            payment = PaymentData(
                internal_id="",
                provider=PaymentProvider.STRIPE,
                provider_payment_id=pi.id,
                provider_customer_id=customer_id,
                status=self._map_payment_status(pi.status),
                amount=amount,
                currency=currency,
                metadata=metadata or {},
            )
            
            return AdapterResult.ok(payment)
            
        except stripe.error.StripeError as e:
            return AdapterResult.fail("stripe_error", str(e))

    def get_payment(
        self,
        provider_payment_id: str,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[PaymentData]:
        """Get a payment intent."""
        if not self._initialized:
            self.initialize()
        
        try:
            kwargs = {}
            if connect_account_id:
                kwargs["stripe_account"] = connect_account_id
            
            pi = stripe.PaymentIntent.retrieve(provider_payment_id, **kwargs)
            
            payment = PaymentData(
                internal_id="",
                provider=PaymentProvider.STRIPE,
                provider_payment_id=pi.id,
                provider_customer_id=pi.customer,
                status=self._map_payment_status(pi.status),
                amount=pi.amount,
                currency=pi.currency,
            )
            
            return AdapterResult.ok(payment)
            
        except stripe.error.StripeError as e:
            return AdapterResult.fail("stripe_error", str(e))

    def refund_payment(
        self,
        provider_payment_id: str,
        amount: Optional[int] = None,
        reason: Optional[str] = None,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[RefundData]:
        """Refund a payment."""
        if not self._initialized:
            self.initialize()
        
        try:
            params = {"payment_intent": provider_payment_id}
            if amount:
                params["amount"] = amount
            if reason:
                params["reason"] = reason
            
            kwargs = {}
            if connect_account_id:
                kwargs["stripe_account"] = connect_account_id
            
            refund = stripe.Refund.create(**params, **kwargs)
            
            return AdapterResult.ok(RefundData(
                internal_id="",
                provider=PaymentProvider.STRIPE,
                provider_refund_id=refund.id,
                provider_payment_id=provider_payment_id,
                amount=refund.amount,
                currency=refund.currency,
                reason=reason,
                status=refund.status,
            ))
            
        except stripe.error.StripeError as e:
            return AdapterResult.fail("stripe_error", str(e))

    # -------------------------------------------------------------------------
    # Webhook Handling
    # -------------------------------------------------------------------------

    def verify_webhook(
        self,
        payload: bytes,
        signature: str,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[bool]:
        """Verify Stripe webhook signature."""
        if not self._initialized:
            self.initialize()
        
        webhook_secret = self.config.webhook_secret or os.getenv("STRIPE_WEBHOOK_SECRET")
        if not webhook_secret:
            return AdapterResult.fail("no_webhook_secret", "Webhook secret not configured")
        
        try:
            stripe.Webhook.construct_event(payload, signature, webhook_secret)
            return AdapterResult.ok(True)
        except stripe.error.SignatureVerificationError:
            return AdapterResult.fail("invalid_signature", "Webhook signature invalid")

    def parse_webhook(
        self,
        payload: bytes,
        signature: str,
    ) -> AdapterResult[WebhookEvent]:
        """Parse and verify webhook."""
        if not self._initialized:
            self.initialize()
        
        webhook_secret = self.config.webhook_secret or os.getenv("STRIPE_WEBHOOK_SECRET")
        if not webhook_secret:
            return AdapterResult.fail("no_webhook_secret", "Webhook secret not configured")
        
        try:
            event = stripe.Webhook.construct_event(payload, signature, webhook_secret)
            
            event_type = self._map_webhook_event_type(event.type)
            
            return AdapterResult.ok(WebhookEvent(
                event_id=event.id,
                event_type=event_type,
                provider=PaymentProvider.STRIPE,
                raw_payload=dict(event),
                object_type=event.data.object.object if hasattr(event.data.object, 'object') else None,
                object_id=event.data.object.id if hasattr(event.data.object, 'id') else None,
                object_data=dict(event.data.object) if event.data.object else None,
            ))
            
        except stripe.error.SignatureVerificationError:
            return AdapterResult.fail("invalid_signature", "Webhook signature invalid")

    def handle_webhook(
        self,
        event: WebhookEvent,
    ) -> AdapterResult[Dict[str, Any]]:
        """Handle parsed webhook event."""
        logger.info(f"Handling webhook: {event.event_type.value}")
        
        # Default: return event info
        return AdapterResult.ok({
            "event_id": event.event_id,
            "event_type": event.event_type.value,
            "processed": True,
        })

    # -------------------------------------------------------------------------
    # Connect Operations
    # -------------------------------------------------------------------------

    def create_connect_account(
        self,
        account: ConnectAccount,
    ) -> AdapterResult[ConnectAccount]:
        """Create a Stripe Connect account."""
        if not self._initialized:
            self.initialize()
        
        try:
            params = {
                "type": account.account_type.value,
                "country": account.country,
                "email": account.email,
                "metadata": {
                    **account.metadata,
                    f"{self.config.metadata_prefix}internal_id": account.internal_id,
                    f"{self.config.metadata_prefix}tenant_id": account.tenant_id or "",
                    f"{self.config.metadata_prefix}tier": account.tier,
                },
            }
            
            if account.account_type == AccountType.EXPRESS:
                params["capabilities"] = {
                    "card_payments": {"requested": True},
                    "transfers": {"requested": True},
                }
            
            sa = stripe.Account.create(**params)
            
            account.provider = PaymentProvider.STRIPE_CONNECT
            account.provider_account_id = sa.id
            account.charges_enabled = sa.charges_enabled
            account.payouts_enabled = sa.payouts_enabled
            
            logger.info(f"Created Connect account {sa.id}")
            return AdapterResult.ok(account)
            
        except stripe.error.StripeError as e:
            return AdapterResult.fail("stripe_error", str(e))

    def get_connect_account(
        self,
        provider_account_id: str,
    ) -> AdapterResult[ConnectAccount]:
        """Get a Connect account."""
        if not self._initialized:
            self.initialize()
        
        try:
            sa = stripe.Account.retrieve(provider_account_id)
            
            account = ConnectAccount(
                internal_id=sa.metadata.get(f"{self.config.metadata_prefix}internal_id", ""),
                provider=PaymentProvider.STRIPE_CONNECT,
                provider_account_id=sa.id,
                account_type=AccountType(sa.type) if sa.type in [t.value for t in AccountType] else AccountType.STANDARD,
                email=sa.email,
                country=sa.country,
                charges_enabled=sa.charges_enabled,
                payouts_enabled=sa.payouts_enabled,
                tenant_id=sa.metadata.get(f"{self.config.metadata_prefix}tenant_id"),
                tier=sa.metadata.get(f"{self.config.metadata_prefix}tier", "pro"),
            )
            
            return AdapterResult.ok(account)
            
        except stripe.error.StripeError as e:
            return AdapterResult.fail("stripe_error", str(e))

    def create_account_link(
        self,
        provider_account_id: str,
        refresh_url: str,
        return_url: str,
        link_type: str = "account_onboarding",
    ) -> AdapterResult[str]:
        """Create account link for onboarding."""
        if not self._initialized:
            self.initialize()
        
        try:
            link = stripe.AccountLink.create(
                account=provider_account_id,
                refresh_url=refresh_url,
                return_url=return_url,
                type=link_type,
            )
            
            return AdapterResult.ok(link.url)
            
        except stripe.error.StripeError as e:
            return AdapterResult.fail("stripe_error", str(e))

    def create_login_link(
        self,
        provider_account_id: str,
    ) -> AdapterResult[str]:
        """Create login link for Express dashboard."""
        if not self._initialized:
            self.initialize()
        
        try:
            link = stripe.Account.create_login_link(provider_account_id)
            return AdapterResult.ok(link.url)
        except stripe.error.StripeError as e:
            return AdapterResult.fail("stripe_error", str(e))

    # -------------------------------------------------------------------------
    # Checkout
    # -------------------------------------------------------------------------

    def create_checkout_session(
        self,
        price_ids: List[str],
        customer_id: Optional[str] = None,
        success_url: str = "",
        cancel_url: str = "",
        mode: str = "subscription",
        metadata: Optional[Dict[str, str]] = None,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[Dict[str, Any]]:
        """Create Stripe Checkout session."""
        if not self._initialized:
            self.initialize()
        
        try:
            line_items = [{"price": pid, "quantity": 1} for pid in price_ids]
            
            params = {
                "line_items": line_items,
                "mode": mode,
                "success_url": success_url,
                "cancel_url": cancel_url,
                "metadata": metadata or {},
            }
            
            if customer_id:
                params["customer"] = customer_id
            
            kwargs = {}
            if connect_account_id:
                kwargs["stripe_account"] = connect_account_id
            
            session = stripe.checkout.Session.create(**params, **kwargs)
            
            return AdapterResult.ok({
                "session_id": session.id,
                "url": session.url,
            })
            
        except stripe.error.StripeError as e:
            return AdapterResult.fail("stripe_error", str(e))

    def create_billing_portal_session(
        self,
        customer_id: str,
        return_url: str,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[str]:
        """Create billing portal session."""
        if not self._initialized:
            self.initialize()
        
        try:
            kwargs = {}
            if connect_account_id:
                kwargs["stripe_account"] = connect_account_id
            
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
                **kwargs
            )
            
            return AdapterResult.ok(session.url)
            
        except stripe.error.StripeError as e:
            return AdapterResult.fail("stripe_error", str(e))

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _map_subscription_status(self, status: str) -> SubscriptionStatus:
        mapping = {
            "active": SubscriptionStatus.ACTIVE,
            "trialing": SubscriptionStatus.TRIALING,
            "past_due": SubscriptionStatus.PAST_DUE,
            "canceled": SubscriptionStatus.CANCELED,
            "unpaid": SubscriptionStatus.UNPAID,
            "incomplete": SubscriptionStatus.INCOMPLETE,
            "incomplete_expired": SubscriptionStatus.INCOMPLETE_EXPIRED,
            "paused": SubscriptionStatus.PAUSED,
        }
        return mapping.get(status, SubscriptionStatus.ACTIVE)

    def _map_invoice_status(self, status: str) -> InvoiceStatus:
        mapping = {
            "draft": InvoiceStatus.DRAFT,
            "open": InvoiceStatus.OPEN,
            "paid": InvoiceStatus.PAID,
            "void": InvoiceStatus.VOID,
            "uncollectible": InvoiceStatus.UNCOLLECTIBLE,
        }
        return mapping.get(status, InvoiceStatus.DRAFT)

    def _map_payment_status(self, status: str) -> PaymentStatus:
        mapping = {
            "requires_payment_method": PaymentStatus.PENDING,
            "requires_confirmation": PaymentStatus.PENDING,
            "requires_action": PaymentStatus.PENDING,
            "processing": PaymentStatus.PENDING,
            "succeeded": PaymentStatus.SUCCEEDED,
            "canceled": PaymentStatus.CANCELED,
        }
        return mapping.get(status, PaymentStatus.PENDING)

    def _map_webhook_event_type(self, event_type: str) -> WebhookEventType:
        mapping = {
            "customer.created": WebhookEventType.CUSTOMER_CREATED,
            "customer.updated": WebhookEventType.CUSTOMER_UPDATED,
            "customer.deleted": WebhookEventType.CUSTOMER_DELETED,
            "customer.subscription.created": WebhookEventType.SUBSCRIPTION_CREATED,
            "customer.subscription.updated": WebhookEventType.SUBSCRIPTION_UPDATED,
            "customer.subscription.deleted": WebhookEventType.SUBSCRIPTION_CANCELED,
            "customer.subscription.trial_will_end": WebhookEventType.SUBSCRIPTION_TRIAL_ENDING,
            "invoice.created": WebhookEventType.INVOICE_CREATED,
            "invoice.paid": WebhookEventType.INVOICE_PAID,
            "invoice.payment_failed": WebhookEventType.INVOICE_PAYMENT_FAILED,
            "invoice.upcoming": WebhookEventType.INVOICE_UPCOMING,
            "payment_intent.succeeded": WebhookEventType.PAYMENT_SUCCEEDED,
            "payment_intent.payment_failed": WebhookEventType.PAYMENT_FAILED,
            "charge.refunded": WebhookEventType.PAYMENT_REFUNDED,
            "account.updated": WebhookEventType.ACCOUNT_UPDATED,
            "payout.paid": WebhookEventType.PAYOUT_PAID,
        }
        return mapping.get(event_type, WebhookEventType.UNKNOWN)


# Register adapter
AdapterRegistry.register(PaymentProvider.STRIPE, StripeAdapter)
AdapterRegistry.register(PaymentProvider.STRIPE_CONNECT, StripeAdapter)


def create_stripe_adapter(
    api_key: Optional[str] = None,
    webhook_secret: Optional[str] = None,
    test_mode: bool = True,
    connect_enabled: bool = False,
) -> StripeAdapter:
    """Factory function to create StripeAdapter."""
    config = AdapterConfig(
        provider=PaymentProvider.STRIPE_CONNECT if connect_enabled else PaymentProvider.STRIPE,
        api_key=api_key,
        webhook_secret=webhook_secret,
        test_mode=test_mode,
        connect_enabled=connect_enabled,
    )
    return StripeAdapter(config)
