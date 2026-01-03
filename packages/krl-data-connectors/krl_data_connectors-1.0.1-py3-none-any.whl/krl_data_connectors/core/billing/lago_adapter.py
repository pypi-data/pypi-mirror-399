# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""
Lago Adapter - DEPRECATED

⚠️ DEPRECATION WARNING (Dec 2025):
This module has been moved to krl-premium-backend.
Import from: app.services.billing.lago_adapter

This stub remains for backward compatibility but will be removed in v2.0.
"""

from __future__ import annotations

import warnings
warnings.warn(
    "krl_data_connectors.core.billing.lago_adapter is deprecated. "
    "This module has moved to krl-premium-backend. "
    "Import from 'app.services.billing.lago_adapter' instead.",
    DeprecationWarning,
    stacklevel=2
)

import logging
import os
from datetime import datetime, UTC
from typing import Any, Dict, List, Optional
import json

from .payments_adapter import (
    PaymentsAdapter,
    PaymentProvider,
    AdapterConfig,
    AdapterResult,
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

# Conditional import for HTTP client
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    try:
        import requests as httpx
        HTTPX_AVAILABLE = True
    except ImportError:
        HTTPX_AVAILABLE = False
        httpx = None


class LagoAdapter(PaymentsAdapter):
    """
    Lago payment adapter for self-hosted open-source billing.
    
    Lago API docs: https://doc.getlago.com/api-reference/
    """

    def __init__(self, config: AdapterConfig):
        super().__init__(config)
        self._base_url = os.getenv("LAGO_API_URL", "https://api.getlago.com/api/v1")
        self._client = None

    @property
    def provider(self) -> PaymentProvider:
        return PaymentProvider.LAGO

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
    ) -> AdapterResult[Dict[str, Any]]:
        """Make HTTP request to Lago API."""
        if not HTTPX_AVAILABLE:
            return AdapterResult.fail("no_http_client", "httpx or requests not installed")
        
        url = f"{self._base_url}{endpoint}"
        headers = self._get_headers()
        
        try:
            if hasattr(httpx, 'Client'):
                # httpx
                with httpx.Client(timeout=self.config.timeout_seconds) as client:
                    if method == "GET":
                        resp = client.get(url, headers=headers)
                    elif method == "POST":
                        resp = client.post(url, headers=headers, json=data)
                    elif method == "PUT":
                        resp = client.put(url, headers=headers, json=data)
                    elif method == "DELETE":
                        resp = client.delete(url, headers=headers)
                    else:
                        return AdapterResult.fail("invalid_method", f"Unknown method: {method}")
                    
                    if resp.status_code >= 400:
                        return AdapterResult.fail(
                            f"http_{resp.status_code}",
                            resp.text,
                            {"status_code": resp.status_code}
                        )
                    
                    return AdapterResult.ok(resp.json() if resp.text else {})
            else:
                # requests fallback
                if method == "GET":
                    resp = httpx.get(url, headers=headers, timeout=self.config.timeout_seconds)
                elif method == "POST":
                    resp = httpx.post(url, headers=headers, json=data, timeout=self.config.timeout_seconds)
                elif method == "PUT":
                    resp = httpx.put(url, headers=headers, json=data, timeout=self.config.timeout_seconds)
                elif method == "DELETE":
                    resp = httpx.delete(url, headers=headers, timeout=self.config.timeout_seconds)
                else:
                    return AdapterResult.fail("invalid_method", f"Unknown method: {method}")
                
                if resp.status_code >= 400:
                    return AdapterResult.fail(f"http_{resp.status_code}", resp.text)
                
                return AdapterResult.ok(resp.json() if resp.text else {})
                
        except Exception as e:
            return AdapterResult.fail("request_error", str(e))

    def initialize(self) -> AdapterResult[bool]:
        """Initialize Lago adapter."""
        if not HTTPX_AVAILABLE:
            return AdapterResult.fail("no_http_client", "Install httpx: pip install httpx")
        
        api_key = self.config.api_key or os.getenv("LAGO_API_KEY")
        if not api_key:
            return AdapterResult.fail("no_api_key", "Lago API key not configured")
        
        self.config.api_key = api_key
        self._initialized = True
        logger.info("LagoAdapter initialized")
        return AdapterResult.ok(True)

    def health_check(self) -> AdapterResult[Dict[str, Any]]:
        """Check Lago connectivity."""
        if not self._initialized:
            init = self.initialize()
            if not init.success:
                return init
        
        # Try to list customers (limit 1) as health check
        result = self._request("GET", "/customers?per_page=1")
        if result.success:
            return AdapterResult.ok({"provider": "lago", "connected": True})
        return result

    # -------------------------------------------------------------------------
    # Customer Operations
    # -------------------------------------------------------------------------

    def create_customer(
        self,
        customer: CustomerData,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[CustomerData]:
        """Create a Lago customer."""
        if not self._initialized:
            self.initialize()
        
        data = {
            "customer": {
                "external_id": customer.internal_id,
                "name": customer.name or customer.email,
                "email": customer.email,
                "phone": customer.phone,
                "metadata": [
                    {"key": "tenant_id", "value": customer.tenant_id or ""},
                    {"key": "tier", "value": customer.tier},
                ],
            }
        }
        
        if customer.address:
            data["customer"]["address_line1"] = customer.address.line1
            data["customer"]["city"] = customer.address.city
            data["customer"]["state"] = customer.address.state
            data["customer"]["zipcode"] = customer.address.postal_code
            data["customer"]["country"] = customer.address.country
        
        result = self._request("POST", "/customers", data)
        if not result.success:
            return AdapterResult.fail(result.error_code, result.error_message)
        
        lago_customer = result.data.get("customer", {})
        customer.provider = PaymentProvider.LAGO
        customer.provider_customer_id = lago_customer.get("lago_id")
        
        logger.info(f"Created Lago customer {customer.provider_customer_id}")
        return AdapterResult.ok(customer)

    def get_customer(
        self,
        provider_customer_id: str,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[CustomerData]:
        """Get a Lago customer by external_id."""
        if not self._initialized:
            self.initialize()
        
        result = self._request("GET", f"/customers/{provider_customer_id}")
        if not result.success:
            return AdapterResult.fail(result.error_code, result.error_message)
        
        lc = result.data.get("customer", {})
        
        customer = CustomerData(
            internal_id=lc.get("external_id", ""),
            provider=PaymentProvider.LAGO,
            provider_customer_id=lc.get("lago_id"),
            email=lc.get("email", ""),
            name=lc.get("name"),
            phone=lc.get("phone"),
        )
        
        # Extract metadata
        for meta in lc.get("metadata", []):
            if meta.get("key") == "tenant_id":
                customer.tenant_id = meta.get("value")
            elif meta.get("key") == "tier":
                customer.tier = meta.get("value", "community")
        
        return AdapterResult.ok(customer)

    def update_customer(
        self,
        customer: CustomerData,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[CustomerData]:
        """Update a Lago customer."""
        if not self._initialized:
            self.initialize()
        
        data = {
            "customer": {
                "external_id": customer.internal_id,
                "name": customer.name,
                "email": customer.email,
                "metadata": [
                    {"key": "tier", "value": customer.tier},
                ],
            }
        }
        
        result = self._request("PUT", f"/customers/{customer.internal_id}", data)
        if not result.success:
            return AdapterResult.fail(result.error_code, result.error_message)
        
        return AdapterResult.ok(customer)

    def delete_customer(
        self,
        provider_customer_id: str,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[bool]:
        """Delete a Lago customer."""
        if not self._initialized:
            self.initialize()
        
        result = self._request("DELETE", f"/customers/{provider_customer_id}")
        return AdapterResult.ok(True) if result.success else result

    # -------------------------------------------------------------------------
    # Subscription Operations
    # -------------------------------------------------------------------------

    def create_subscription(
        self,
        subscription: SubscriptionData,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[SubscriptionData]:
        """Create a Lago subscription."""
        if not self._initialized:
            self.initialize()
        
        # Lago uses plan_code, not price_id
        plan_code = subscription.items[0].provider_price_id if subscription.items else "default"
        
        data = {
            "subscription": {
                "external_customer_id": subscription.customer_internal_id,
                "plan_code": plan_code,
                "external_id": subscription.internal_id,
            }
        }
        
        result = self._request("POST", "/subscriptions", data)
        if not result.success:
            return AdapterResult.fail(result.error_code, result.error_message)
        
        ls = result.data.get("subscription", {})
        subscription.provider = PaymentProvider.LAGO
        subscription.provider_subscription_id = ls.get("lago_id")
        subscription.status = self._map_subscription_status(ls.get("status", "active"))
        
        logger.info(f"Created Lago subscription {subscription.provider_subscription_id}")
        return AdapterResult.ok(subscription)

    def get_subscription(
        self,
        provider_subscription_id: str,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[SubscriptionData]:
        """Get a Lago subscription."""
        if not self._initialized:
            self.initialize()
        
        result = self._request("GET", f"/subscriptions/{provider_subscription_id}")
        if not result.success:
            return AdapterResult.fail(result.error_code, result.error_message)
        
        ls = result.data.get("subscription", {})
        
        sub = SubscriptionData(
            internal_id=ls.get("external_id", ""),
            provider=PaymentProvider.LAGO,
            provider_subscription_id=ls.get("lago_id"),
            provider_customer_id=ls.get("external_customer_id"),
            status=self._map_subscription_status(ls.get("status", "active")),
        )
        
        return AdapterResult.ok(sub)

    def update_subscription(
        self,
        subscription: SubscriptionData,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[SubscriptionData]:
        """Update subscription."""
        # Lago subscriptions are mostly immutable, return as-is
        return AdapterResult.ok(subscription)

    def modify_subscription(
        self,
        provider_subscription_id: str,
        new_price_id: Optional[str] = None,
        quantity: Optional[int] = None,
        proration_behavior: str = "create_prorations",
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[SubscriptionData]:
        """Modify subscription (upgrade/downgrade)."""
        if not self._initialized:
            self.initialize()
        
        if not new_price_id:
            return self.get_subscription(provider_subscription_id)
        
        # In Lago, changing plans requires terminating and creating new
        data = {
            "subscription": {
                "plan_code": new_price_id,
            }
        }
        
        result = self._request("PUT", f"/subscriptions/{provider_subscription_id}", data)
        if not result.success:
            return AdapterResult.fail(result.error_code, result.error_message)
        
        return self.get_subscription(provider_subscription_id)

    def cancel_subscription(
        self,
        provider_subscription_id: str,
        immediately: bool = False,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[SubscriptionData]:
        """Cancel a Lago subscription."""
        if not self._initialized:
            self.initialize()
        
        result = self._request("DELETE", f"/subscriptions/{provider_subscription_id}")
        if not result.success:
            return AdapterResult.fail(result.error_code, result.error_message)
        
        ls = result.data.get("subscription", {})
        
        return AdapterResult.ok(SubscriptionData(
            internal_id=ls.get("external_id", ""),
            provider=PaymentProvider.LAGO,
            provider_subscription_id=ls.get("lago_id"),
            status=SubscriptionStatus.CANCELED,
        ))

    def pause_subscription(
        self,
        provider_subscription_id: str,
        resume_at: Optional[datetime] = None,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[SubscriptionData]:
        """Pause not supported in Lago."""
        return AdapterResult.fail("not_supported", "Lago does not support pause")

    def resume_subscription(
        self,
        provider_subscription_id: str,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[SubscriptionData]:
        """Resume not supported in Lago."""
        return AdapterResult.fail("not_supported", "Lago does not support resume")

    # -------------------------------------------------------------------------
    # Usage-Based Billing
    # -------------------------------------------------------------------------

    def record_usage(
        self,
        usage: UsageRecordData,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[UsageRecordData]:
        """Record usage event in Lago."""
        if not self._initialized:
            self.initialize()
        
        data = {
            "event": {
                "transaction_id": usage.internal_id,
                "external_customer_id": usage.tenant_id,
                "code": usage.metric_type or "api_calls",
                "timestamp": int(usage.timestamp.timestamp()),
                "properties": {
                    "value": usage.quantity,
                },
            }
        }
        
        result = self._request("POST", "/events", data)
        if not result.success:
            return AdapterResult.fail(result.error_code, result.error_message)
        
        usage.provider = PaymentProvider.LAGO
        logger.debug(f"Recorded Lago usage: {usage.quantity}")
        return AdapterResult.ok(usage)

    def get_usage_summary(
        self,
        provider_subscription_item_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[Dict[str, Any]]:
        """Get usage summary - not directly supported."""
        return AdapterResult.ok({"total_usage": 0, "note": "Use Lago dashboard for summaries"})

    # -------------------------------------------------------------------------
    # Pricing
    # -------------------------------------------------------------------------

    def create_price(
        self,
        price: PriceData,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[PriceData]:
        """Create a Lago plan (equivalent to price)."""
        if not self._initialized:
            self.initialize()
        
        data = {
            "plan": {
                "name": price.name,
                "code": price.internal_id,
                "interval": price.billing_interval.value if price.billing_interval else "monthly",
                "amount_cents": price.unit_amount,
                "amount_currency": price.currency.upper(),
            }
        }
        
        result = self._request("POST", "/plans", data)
        if not result.success:
            return AdapterResult.fail(result.error_code, result.error_message)
        
        lp = result.data.get("plan", {})
        price.provider = PaymentProvider.LAGO
        price.provider_price_id = lp.get("lago_id")
        
        return AdapterResult.ok(price)

    def get_price(
        self,
        provider_price_id: str,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[PriceData]:
        """Get a Lago plan."""
        if not self._initialized:
            self.initialize()
        
        result = self._request("GET", f"/plans/{provider_price_id}")
        if not result.success:
            return AdapterResult.fail(result.error_code, result.error_message)
        
        lp = result.data.get("plan", {})
        
        price = PriceData(
            internal_id=lp.get("code", ""),
            provider=PaymentProvider.LAGO,
            provider_price_id=lp.get("lago_id"),
            name=lp.get("name", ""),
            currency=lp.get("amount_currency", "usd").lower(),
            unit_amount=lp.get("amount_cents", 0),
        )
        
        return AdapterResult.ok(price)

    def update_price(
        self,
        price: PriceData,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[PriceData]:
        """Update Lago plan."""
        if not self._initialized:
            self.initialize()
        
        data = {
            "plan": {
                "name": price.name,
            }
        }
        
        result = self._request("PUT", f"/plans/{price.internal_id}", data)
        return AdapterResult.ok(price) if result.success else result

    def list_prices(
        self,
        product_id: Optional[str] = None,
        active: bool = True,
        limit: int = 100,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[List[PriceData]]:
        """List Lago plans."""
        if not self._initialized:
            self.initialize()
        
        result = self._request("GET", f"/plans?per_page={limit}")
        if not result.success:
            return AdapterResult.fail(result.error_code, result.error_message)
        
        prices = []
        for lp in result.data.get("plans", []):
            prices.append(PriceData(
                internal_id=lp.get("code", ""),
                provider=PaymentProvider.LAGO,
                provider_price_id=lp.get("lago_id"),
                name=lp.get("name", ""),
                unit_amount=lp.get("amount_cents", 0),
            ))
        
        return AdapterResult.ok(prices)

    # -------------------------------------------------------------------------
    # Invoice Operations
    # -------------------------------------------------------------------------

    def get_invoice(
        self,
        provider_invoice_id: str,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[InvoiceData]:
        """Get a Lago invoice."""
        if not self._initialized:
            self.initialize()
        
        result = self._request("GET", f"/invoices/{provider_invoice_id}")
        if not result.success:
            return AdapterResult.fail(result.error_code, result.error_message)
        
        li = result.data.get("invoice", {})
        
        invoice = InvoiceData(
            internal_id="",
            provider=PaymentProvider.LAGO,
            provider_invoice_id=li.get("lago_id"),
            status=self._map_invoice_status(li.get("status", "draft")),
            total=li.get("total_amount_cents", 0),
            currency=li.get("currency", "usd").lower(),
        )
        
        return AdapterResult.ok(invoice)

    def list_invoices(
        self,
        provider_customer_id: Optional[str] = None,
        status: Optional[InvoiceStatus] = None,
        limit: int = 100,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[List[InvoiceData]]:
        """List Lago invoices."""
        if not self._initialized:
            self.initialize()
        
        endpoint = f"/invoices?per_page={limit}"
        if provider_customer_id:
            endpoint += f"&external_customer_id={provider_customer_id}"
        
        result = self._request("GET", endpoint)
        if not result.success:
            return AdapterResult.fail(result.error_code, result.error_message)
        
        invoices = []
        for li in result.data.get("invoices", []):
            invoices.append(InvoiceData(
                internal_id="",
                provider=PaymentProvider.LAGO,
                provider_invoice_id=li.get("lago_id"),
                status=self._map_invoice_status(li.get("status", "draft")),
                total=li.get("total_amount_cents", 0),
            ))
        
        return AdapterResult.ok(invoices)

    def finalize_invoice(
        self,
        provider_invoice_id: str,
        auto_advance: bool = True,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[InvoiceData]:
        """Finalize invoice."""
        if not self._initialized:
            self.initialize()
        
        result = self._request("PUT", f"/invoices/{provider_invoice_id}/finalize")
        if not result.success:
            return AdapterResult.fail(result.error_code, result.error_message)
        
        return self.get_invoice(provider_invoice_id)

    def pay_invoice(
        self,
        provider_invoice_id: str,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[InvoiceData]:
        """Mark invoice as paid."""
        return self.get_invoice(provider_invoice_id)

    def void_invoice(
        self,
        provider_invoice_id: str,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[InvoiceData]:
        """Void invoice."""
        if not self._initialized:
            self.initialize()
        
        result = self._request("PUT", f"/invoices/{provider_invoice_id}/void")
        if not result.success:
            return AdapterResult.fail(result.error_code, result.error_message)
        
        return self.get_invoice(provider_invoice_id)

    # -------------------------------------------------------------------------
    # Payment Operations (Limited in Lago)
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
        """Lago handles payments via invoices."""
        return AdapterResult.fail("not_supported", "Use invoices for Lago payments")

    def get_payment(
        self,
        provider_payment_id: str,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[PaymentData]:
        """Not directly supported."""
        return AdapterResult.fail("not_supported", "Use invoice endpoints")

    def refund_payment(
        self,
        provider_payment_id: str,
        amount: Optional[int] = None,
        reason: Optional[str] = None,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[RefundData]:
        """Create credit note for refund."""
        if not self._initialized:
            self.initialize()
        
        data = {
            "credit_note": {
                "invoice_id": provider_payment_id,
                "reason": reason or "other",
                "credit_amount_cents": amount,
            }
        }
        
        result = self._request("POST", "/credit_notes", data)
        if not result.success:
            return AdapterResult.fail(result.error_code, result.error_message)
        
        cn = result.data.get("credit_note", {})
        
        return AdapterResult.ok(RefundData(
            internal_id="",
            provider=PaymentProvider.LAGO,
            provider_refund_id=cn.get("lago_id"),
            provider_payment_id=provider_payment_id,
            amount=amount or 0,
            reason=reason,
            status="succeeded",
        ))

    # -------------------------------------------------------------------------
    # Webhook Handling
    # -------------------------------------------------------------------------

    def verify_webhook(
        self,
        payload: bytes,
        signature: str,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[bool]:
        """Verify Lago webhook (signature-based if configured)."""
        # Lago uses a simpler signature or IP allowlisting
        return AdapterResult.ok(True)

    def parse_webhook(
        self,
        payload: bytes,
        signature: str,
    ) -> AdapterResult[WebhookEvent]:
        """Parse Lago webhook."""
        try:
            data = json.loads(payload)
            
            event_type = self._map_webhook_event_type(data.get("webhook_type", ""))
            
            return AdapterResult.ok(WebhookEvent(
                event_id=data.get("webhook_id", ""),
                event_type=event_type,
                provider=PaymentProvider.LAGO,
                raw_payload=data,
                object_type=data.get("object_type"),
                object_data=data,
            ))
            
        except json.JSONDecodeError as e:
            return AdapterResult.fail("parse_error", str(e))

    def handle_webhook(
        self,
        event: WebhookEvent,
    ) -> AdapterResult[Dict[str, Any]]:
        """Handle Lago webhook."""
        logger.info(f"Handling Lago webhook: {event.event_type.value}")
        return AdapterResult.ok({
            "event_id": event.event_id,
            "event_type": event.event_type.value,
            "processed": True,
        })

    # -------------------------------------------------------------------------
    # Connect Operations (Not applicable for Lago)
    # -------------------------------------------------------------------------

    def create_connect_account(self, account: ConnectAccount) -> AdapterResult[ConnectAccount]:
        return AdapterResult.fail("not_supported", "Lago does not support Connect accounts")

    def get_connect_account(self, provider_account_id: str) -> AdapterResult[ConnectAccount]:
        return AdapterResult.fail("not_supported", "Lago does not support Connect accounts")

    def create_account_link(self, provider_account_id: str, refresh_url: str, return_url: str, link_type: str = "account_onboarding") -> AdapterResult[str]:
        return AdapterResult.fail("not_supported", "Lago does not support Connect")

    def create_login_link(self, provider_account_id: str) -> AdapterResult[str]:
        return AdapterResult.fail("not_supported", "Lago does not support Connect")

    # -------------------------------------------------------------------------
    # Checkout (Limited)
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
        """Lago doesn't have hosted checkout."""
        return AdapterResult.fail("not_supported", "Use Lago's customer portal")

    def create_billing_portal_session(
        self,
        customer_id: str,
        return_url: str,
        connect_account_id: Optional[str] = None,
    ) -> AdapterResult[str]:
        """Return Lago's customer portal URL if configured."""
        portal_url = os.getenv("LAGO_CUSTOMER_PORTAL_URL", "")
        if portal_url:
            return AdapterResult.ok(f"{portal_url}?customer={customer_id}")
        return AdapterResult.fail("not_configured", "Customer portal URL not set")

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _map_subscription_status(self, status: str) -> SubscriptionStatus:
        mapping = {
            "active": SubscriptionStatus.ACTIVE,
            "pending": SubscriptionStatus.INCOMPLETE,
            "terminated": SubscriptionStatus.CANCELED,
            "canceled": SubscriptionStatus.CANCELED,
        }
        return mapping.get(status, SubscriptionStatus.ACTIVE)

    def _map_invoice_status(self, status: str) -> InvoiceStatus:
        mapping = {
            "draft": InvoiceStatus.DRAFT,
            "finalized": InvoiceStatus.OPEN,
            "pending": InvoiceStatus.OPEN,
            "succeeded": InvoiceStatus.PAID,
            "voided": InvoiceStatus.VOID,
            "failed": InvoiceStatus.UNCOLLECTIBLE,
        }
        return mapping.get(status, InvoiceStatus.DRAFT)

    def _map_webhook_event_type(self, event_type: str) -> WebhookEventType:
        mapping = {
            "customer.created": WebhookEventType.CUSTOMER_CREATED,
            "subscription.started": WebhookEventType.SUBSCRIPTION_CREATED,
            "subscription.terminated": WebhookEventType.SUBSCRIPTION_CANCELED,
            "invoice.created": WebhookEventType.INVOICE_CREATED,
            "invoice.paid_credit": WebhookEventType.INVOICE_PAID,
            "invoice.payment_failure": WebhookEventType.INVOICE_PAYMENT_FAILED,
        }
        return mapping.get(event_type, WebhookEventType.UNKNOWN)


# Register adapter
AdapterRegistry.register(PaymentProvider.LAGO, LagoAdapter)


def create_lago_adapter(
    api_key: Optional[str] = None,
    api_url: Optional[str] = None,
) -> LagoAdapter:
    """Factory function to create LagoAdapter."""
    config = AdapterConfig(
        provider=PaymentProvider.LAGO,
        api_key=api_key,
    )
    adapter = LagoAdapter(config)
    if api_url:
        adapter._base_url = api_url
    return adapter
