# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
#
# ⚠️ DEPRECATION WARNING (Dec 2025):
# This module has been moved to krl-premium-backend.
# Import from: app.services.billing.rental_stripe
# This stub remains for backward compatibility but will be removed in v2.0.
# ----------------------------------------------------------------------

from __future__ import annotations
import warnings as _warnings
_warnings.warn(
    "krl_data_connectors.core.billing.rental_stripe is deprecated. "
    "Import from 'app.services.billing.rental_stripe' instead.",
    DeprecationWarning,
    stacklevel=2
)

"""
Rental Stripe Integration - Phase 6

Stripe payment processing for temporary model rentals.
Handles payment intents, metered billing, refunds, and webhooks.

Integration Points:
- PaymentIntents for one-time rental purchases
- Price objects for standardized rental pricing
- Refunds for unused rental time/units
- Webhooks for payment confirmation

Revenue Attribution:
- Rental revenue tracking
- Conversion credit accounting
- A/B test revenue attribution
"""


import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone, UTC
from decimal import Decimal
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================

class RentalPaymentStatus(str, Enum):
    """Payment status for rentals."""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class RefundReason(str, Enum):
    """Reasons for rental refunds."""
    UNUSED_TIME = "unused_time"
    UNUSED_INFERENCES = "unused_inferences"
    TECHNICAL_ISSUE = "technical_issue"
    USER_REQUEST = "user_request"
    DUPLICATE = "duplicate"
    FRAUD = "fraud"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class RentalPaymentIntent:
    """A Stripe PaymentIntent for a rental purchase."""
    payment_intent_id: str
    tenant_id: str
    session_id: Optional[str] = None
    
    # Amount
    amount: Decimal = Decimal("0")
    currency: str = "usd"
    
    # Status
    status: RentalPaymentStatus = RentalPaymentStatus.PENDING
    
    # Stripe IDs
    stripe_payment_intent_id: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    stripe_payment_method_id: Optional[str] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None


@dataclass
class RentalRefund:
    """A refund for a rental session."""
    refund_id: str
    payment_intent_id: str
    session_id: str
    tenant_id: str
    
    # Amount
    amount: Decimal = Decimal("0")
    reason: RefundReason = RefundReason.USER_REQUEST
    
    # Stripe
    stripe_refund_id: Optional[str] = None
    
    # Status
    status: str = "pending"  # pending, succeeded, failed
    
    # Details
    usage_at_refund: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    processed_at: Optional[datetime] = None


@dataclass
class RentalPriceConfig:
    """Stripe Price configuration for rental product."""
    price_id: str
    product_id: str
    
    # Rental type
    mechanism_type: str
    rental_subtype: str
    
    # Pricing
    unit_amount: int  # in cents
    currency: str = "usd"
    
    # Stripe IDs
    stripe_price_id: Optional[str] = None
    stripe_product_id: Optional[str] = None
    
    # Metadata
    active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# =============================================================================
# Rental Stripe Adapter
# =============================================================================

class RentalStripeAdapter:
    """
    Stripe integration for rental payments.
    
    Handles:
    - Creating payment intents for rentals
    - Processing payments
    - Calculating and issuing refunds
    - Webhook event handling
    - Revenue attribution
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key
        self._stripe = None
        self._initialized = False
        
        # In-memory storage (production: database)
        self._payment_intents: Dict[str, RentalPaymentIntent] = {}
        self._refunds: Dict[str, RentalRefund] = {}
        self._prices: Dict[str, RentalPriceConfig] = {}
        
        # Initialize Stripe prices from rental pricing
        self._init_prices()
    
    def initialize(self) -> bool:
        """Initialize Stripe SDK."""
        if self._initialized:
            return True
        
        try:
            import stripe
            if self._api_key:
                stripe.api_key = self._api_key
            self._stripe = stripe
            self._initialized = True
            logger.info("RentalStripeAdapter initialized")
            return True
        except ImportError:
            logger.warning("stripe-python not installed, running in mock mode")
            return False
    
    def _init_prices(self) -> None:
        """Initialize Stripe prices from rental pricing config."""
        from .rental_api import (
            TIME_PASS_PRICING,
            INFERENCE_BUNDLE_PRICING,
            SESSION_TOKEN_PRICING,
        )
        
        # Time passes
        for pass_type, config in TIME_PASS_PRICING.items():
            self._prices[f"time_pass_{pass_type.value}"] = RentalPriceConfig(
                price_id=f"price_tp_{pass_type.value}",
                product_id=f"prod_time_pass",
                mechanism_type="time_pass",
                rental_subtype=pass_type.value,
                unit_amount=int(config["price"] * 100),
            )
        
        # Inference bundles
        for bundle_type, config in INFERENCE_BUNDLE_PRICING.items():
            self._prices[f"inference_bundle_{bundle_type.value}"] = RentalPriceConfig(
                price_id=f"price_ib_{bundle_type.value}",
                product_id=f"prod_inference_bundle",
                mechanism_type="inference_bundle",
                rental_subtype=bundle_type.value,
                unit_amount=int(config["price"] * 100),
            )
        
        # Session tokens
        for token_type, config in SESSION_TOKEN_PRICING.items():
            self._prices[f"session_token_{token_type.value}"] = RentalPriceConfig(
                price_id=f"price_st_{token_type.value}",
                product_id=f"prod_session_token",
                mechanism_type="session_token",
                rental_subtype=token_type.value,
                unit_amount=int(config["price"] * 100),
            )
    
    # -------------------------------------------------------------------------
    # Payment Intents
    # -------------------------------------------------------------------------
    
    def create_payment_intent(
        self,
        tenant_id: str,
        mechanism_type: str,
        rental_subtype: str,
        stripe_customer_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RentalPaymentIntent:
        """
        Create a Stripe PaymentIntent for a rental purchase.
        
        Returns the PaymentIntent with client_secret for frontend checkout.
        """
        # Get price config
        price_key = f"{mechanism_type}_{rental_subtype}"
        price = self._prices.get(price_key)
        
        if not price:
            raise ValueError(f"Unknown rental type: {price_key}")
        
        amount = Decimal(price.unit_amount) / 100
        
        payment_intent_id = f"pi_{uuid.uuid4().hex[:16]}"
        
        intent = RentalPaymentIntent(
            payment_intent_id=payment_intent_id,
            tenant_id=tenant_id,
            amount=amount,
            stripe_customer_id=stripe_customer_id,
            metadata={
                "mechanism_type": mechanism_type,
                "rental_subtype": rental_subtype,
                **(metadata or {}),
            },
        )
        
        # Create Stripe PaymentIntent if initialized
        if self._initialized and self._stripe:
            try:
                stripe_intent = self._stripe.PaymentIntent.create(
                    amount=price.unit_amount,
                    currency="usd",
                    customer=stripe_customer_id,
                    metadata={
                        "tenant_id": tenant_id,
                        "mechanism_type": mechanism_type,
                        "rental_subtype": rental_subtype,
                        "krl_payment_intent_id": payment_intent_id,
                    },
                    automatic_payment_methods={"enabled": True},
                )
                intent.stripe_payment_intent_id = stripe_intent.id
                intent.metadata["client_secret"] = stripe_intent.client_secret
            except Exception as e:
                logger.error(f"Failed to create Stripe PaymentIntent: {e}")
                intent.status = RentalPaymentStatus.FAILED
        else:
            # Mock client_secret for development
            intent.stripe_payment_intent_id = f"pi_mock_{uuid.uuid4().hex[:12]}"
            intent.metadata["client_secret"] = f"pi_mock_{uuid.uuid4().hex}_secret_{uuid.uuid4().hex}"
        
        self._payment_intents[payment_intent_id] = intent
        logger.info(f"Created payment intent {payment_intent_id} for ${amount}")
        
        return intent
    
    def confirm_payment(
        self,
        payment_intent_id: str,
        session_id: Optional[str] = None,
    ) -> RentalPaymentIntent:
        """Confirm a payment was successful."""
        intent = self._payment_intents.get(payment_intent_id)
        if not intent:
            raise ValueError(f"PaymentIntent {payment_intent_id} not found")
        
        intent.status = RentalPaymentStatus.SUCCEEDED
        intent.session_id = session_id
        intent.completed_at = datetime.now(timezone.utc)
        
        logger.info(f"Confirmed payment {payment_intent_id}")
        return intent
    
    def cancel_payment(self, payment_intent_id: str) -> RentalPaymentIntent:
        """Cancel a pending payment."""
        intent = self._payment_intents.get(payment_intent_id)
        if not intent:
            raise ValueError(f"PaymentIntent {payment_intent_id} not found")
        
        if intent.status not in (RentalPaymentStatus.PENDING, RentalPaymentStatus.PROCESSING):
            raise ValueError(f"Cannot cancel payment in status {intent.status}")
        
        intent.status = RentalPaymentStatus.CANCELED
        intent.completed_at = datetime.now(timezone.utc)
        
        # Cancel Stripe PaymentIntent
        if self._initialized and self._stripe and intent.stripe_payment_intent_id:
            try:
                self._stripe.PaymentIntent.cancel(intent.stripe_payment_intent_id)
            except Exception as e:
                logger.error(f"Failed to cancel Stripe PaymentIntent: {e}")
        
        logger.info(f"Canceled payment {payment_intent_id}")
        return intent
    
    def get_payment_intent(self, payment_intent_id: str) -> Optional[RentalPaymentIntent]:
        """Get a payment intent by ID."""
        return self._payment_intents.get(payment_intent_id)
    
    # -------------------------------------------------------------------------
    # Refunds
    # -------------------------------------------------------------------------
    
    def calculate_refund_amount(
        self,
        session_id: str,
        reason: RefundReason,
    ) -> Tuple[Decimal, Dict[str, Any]]:
        """
        Calculate refund amount based on usage.
        
        Time-based rentals: Pro-rated based on time remaining
        Inference bundles: Pro-rated based on unused inferences
        """
        from .rental_api import get_session_manager
        
        manager = get_session_manager()
        session = manager.get_session(session_id)
        
        if not session:
            return Decimal("0"), {"error": "Session not found"}
        
        original_amount = session.amount_paid
        usage_details = {}
        
        if session.mechanism_type.value in ("time_pass", "session_token"):
            # Pro-rate based on time
            if session.expires_at and session.activated_at:
                total_seconds = (session.expires_at - session.activated_at).total_seconds()
                remaining_seconds = session.time_remaining_seconds
                
                if total_seconds > 0:
                    unused_fraction = remaining_seconds / total_seconds
                    refund_amount = original_amount * Decimal(str(unused_fraction))
                else:
                    refund_amount = Decimal("0")
                
                usage_details = {
                    "total_seconds": int(total_seconds),
                    "remaining_seconds": remaining_seconds,
                    "unused_fraction": float(unused_fraction) if total_seconds > 0 else 0,
                }
            else:
                # Not activated, full refund
                refund_amount = original_amount
                usage_details = {"not_activated": True}
        
        else:  # inference_bundle
            # Pro-rate based on unused inferences
            if session.total_units > 0:
                unused_fraction = (session.total_units - session.used_units) / session.total_units
                refund_amount = original_amount * Decimal(str(unused_fraction))
            else:
                refund_amount = Decimal("0")
            
            usage_details = {
                "total_units": session.total_units,
                "used_units": session.used_units,
                "unused_units": session.total_units - session.used_units,
                "unused_fraction": float(unused_fraction) if session.total_units > 0 else 0,
            }
        
        # Apply minimum refund threshold
        if refund_amount < Decimal("0.50"):
            refund_amount = Decimal("0")
            usage_details["below_minimum"] = True
        
        # Round to cents
        refund_amount = refund_amount.quantize(Decimal("0.01"))
        
        return refund_amount, usage_details
    
    def create_refund(
        self,
        payment_intent_id: str,
        session_id: str,
        reason: RefundReason,
        amount: Optional[Decimal] = None,
    ) -> RentalRefund:
        """
        Create a refund for a rental purchase.
        
        If amount is not specified, calculates pro-rated refund.
        """
        intent = self._payment_intents.get(payment_intent_id)
        if not intent:
            raise ValueError(f"PaymentIntent {payment_intent_id} not found")
        
        if intent.status != RentalPaymentStatus.SUCCEEDED:
            raise ValueError(f"Cannot refund payment in status {intent.status}")
        
        # Calculate refund amount if not specified
        if amount is None:
            amount, usage_details = self.calculate_refund_amount(session_id, reason)
        else:
            usage_details = {"manual_amount": True}
        
        if amount <= 0:
            raise ValueError("Refund amount must be positive")
        
        refund_id = f"re_{uuid.uuid4().hex[:16]}"
        
        refund = RentalRefund(
            refund_id=refund_id,
            payment_intent_id=payment_intent_id,
            session_id=session_id,
            tenant_id=intent.tenant_id,
            amount=amount,
            reason=reason,
            usage_at_refund=usage_details,
        )
        
        # Create Stripe refund
        if self._initialized and self._stripe and intent.stripe_payment_intent_id:
            try:
                stripe_refund = self._stripe.Refund.create(
                    payment_intent=intent.stripe_payment_intent_id,
                    amount=int(amount * 100),
                    reason="requested_by_customer" if reason == RefundReason.USER_REQUEST else "other",
                    metadata={
                        "tenant_id": intent.tenant_id,
                        "session_id": session_id,
                        "refund_reason": reason.value,
                    },
                )
                refund.stripe_refund_id = stripe_refund.id
                refund.status = "succeeded"
                refund.processed_at = datetime.now(timezone.utc)
            except Exception as e:
                logger.error(f"Failed to create Stripe refund: {e}")
                refund.status = "failed"
        else:
            # Mock refund for development
            refund.stripe_refund_id = f"re_mock_{uuid.uuid4().hex[:12]}"
            refund.status = "succeeded"
            refund.processed_at = datetime.now(timezone.utc)
        
        # Update payment intent status
        if refund.status == "succeeded":
            if amount >= intent.amount:
                intent.status = RentalPaymentStatus.REFUNDED
            else:
                intent.status = RentalPaymentStatus.PARTIALLY_REFUNDED
        
        self._refunds[refund_id] = refund
        logger.info(f"Created refund {refund_id} for ${amount}")
        
        return refund
    
    def get_refund(self, refund_id: str) -> Optional[RentalRefund]:
        """Get a refund by ID."""
        return self._refunds.get(refund_id)
    
    def get_session_refunds(self, session_id: str) -> List[RentalRefund]:
        """Get all refunds for a session."""
        return [r for r in self._refunds.values() if r.session_id == session_id]
    
    # -------------------------------------------------------------------------
    # Webhook Handling
    # -------------------------------------------------------------------------
    
    def handle_webhook_event(self, event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle Stripe webhook events related to rentals.
        
        Events handled:
        - payment_intent.succeeded
        - payment_intent.payment_failed
        - charge.refunded
        - charge.dispute.created
        """
        handlers = {
            "payment_intent.succeeded": self._handle_payment_succeeded,
            "payment_intent.payment_failed": self._handle_payment_failed,
            "charge.refunded": self._handle_charge_refunded,
            "charge.dispute.created": self._handle_dispute_created,
        }
        
        handler = handlers.get(event_type)
        if not handler:
            return {"handled": False, "reason": "Unknown event type"}
        
        try:
            result = handler(event_data)
            return {"handled": True, "result": result}
        except Exception as e:
            logger.error(f"Webhook handler error for {event_type}: {e}")
            return {"handled": False, "error": str(e)}
    
    def _handle_payment_succeeded(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle successful payment."""
        stripe_pi_id = data.get("id")
        metadata = data.get("metadata", {})
        
        krl_pi_id = metadata.get("krl_payment_intent_id")
        if krl_pi_id and krl_pi_id in self._payment_intents:
            intent = self._payment_intents[krl_pi_id]
            intent.status = RentalPaymentStatus.SUCCEEDED
            intent.completed_at = datetime.now(timezone.utc)
            
            # Activate rental session
            from .rental_api import get_session_manager
            if intent.session_id:
                manager = get_session_manager()
                try:
                    manager.activate_session(intent.session_id)
                except Exception as e:
                    logger.error(f"Failed to activate session: {e}")
            
            return {"payment_intent_id": krl_pi_id, "action": "activated"}
        
        return {"stripe_pi_id": stripe_pi_id, "action": "unknown"}
    
    def _handle_payment_failed(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle failed payment."""
        stripe_pi_id = data.get("id")
        metadata = data.get("metadata", {})
        
        krl_pi_id = metadata.get("krl_payment_intent_id")
        if krl_pi_id and krl_pi_id in self._payment_intents:
            intent = self._payment_intents[krl_pi_id]
            intent.status = RentalPaymentStatus.FAILED
            
            return {"payment_intent_id": krl_pi_id, "action": "failed"}
        
        return {"stripe_pi_id": stripe_pi_id, "action": "unknown"}
    
    def _handle_charge_refunded(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle refund confirmation."""
        refund_id = data.get("refunds", {}).get("data", [{}])[0].get("id")
        
        # Find and update refund
        for refund in self._refunds.values():
            if refund.stripe_refund_id == refund_id:
                refund.status = "succeeded"
                refund.processed_at = datetime.now(timezone.utc)
                return {"refund_id": refund.refund_id, "action": "confirmed"}
        
        return {"stripe_refund_id": refund_id, "action": "unknown"}
    
    def _handle_dispute_created(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle dispute/chargeback."""
        charge_id = data.get("charge")
        
        # Flag for fraud review
        logger.warning(f"Dispute created for charge {charge_id}")
        
        return {"charge_id": charge_id, "action": "flagged_for_review"}
    
    # -------------------------------------------------------------------------
    # Revenue Attribution
    # -------------------------------------------------------------------------
    
    def get_rental_revenue(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        mechanism_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get rental revenue metrics.
        
        Breaks down by:
        - Mechanism type (time_pass, inference_bundle, session_token)
        - Rental subtype
        - Date range
        """
        if start_date is None:
            start_date = datetime.now(timezone.utc) - timedelta(days=30)
        if end_date is None:
            end_date = datetime.now(timezone.utc)
        
        # Filter successful payments
        payments = [
            p for p in self._payment_intents.values()
            if p.status == RentalPaymentStatus.SUCCEEDED
            and p.completed_at
            and start_date <= p.completed_at <= end_date
        ]
        
        if mechanism_type:
            payments = [
                p for p in payments
                if p.metadata.get("mechanism_type") == mechanism_type
            ]
        
        # Calculate refunds
        refunds = [
            r for r in self._refunds.values()
            if r.status == "succeeded"
            and r.processed_at
            and start_date <= r.processed_at <= end_date
        ]
        
        gross_revenue = sum(p.amount for p in payments)
        refund_amount = sum(r.amount for r in refunds)
        net_revenue = gross_revenue - refund_amount
        
        # Breakdown by mechanism
        by_mechanism = {}
        for p in payments:
            mech = p.metadata.get("mechanism_type", "unknown")
            if mech not in by_mechanism:
                by_mechanism[mech] = {"count": 0, "revenue": Decimal("0")}
            by_mechanism[mech]["count"] += 1
            by_mechanism[mech]["revenue"] += p.amount
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "gross_revenue": float(gross_revenue),
            "refunds": float(refund_amount),
            "net_revenue": float(net_revenue),
            "transaction_count": len(payments),
            "refund_count": len(refunds),
            "by_mechanism": {
                k: {"count": v["count"], "revenue": float(v["revenue"])}
                for k, v in by_mechanism.items()
            },
        }
    
    def attribute_to_experiment(
        self,
        payment_intent_id: str,
        experiment_id: str,
        variant_id: str,
    ) -> None:
        """Attribute revenue to an A/B test experiment."""
        intent = self._payment_intents.get(payment_intent_id)
        if intent:
            intent.metadata["experiment_id"] = experiment_id
            intent.metadata["variant_id"] = variant_id
            
            # Track in A/B test engine
            from .rental_ab_testing import get_ab_test_engine
            engine = get_ab_test_engine()
            engine.track_conversion(
                experiment_id=experiment_id,
                variant_id=variant_id,
                tenant_id=intent.tenant_id,
                revenue=intent.amount,
            )


# =============================================================================
# Singleton Instance
# =============================================================================

_stripe_adapter: Optional[RentalStripeAdapter] = None


def get_rental_stripe_adapter() -> RentalStripeAdapter:
    """Get or create Stripe adapter instance."""
    global _stripe_adapter
    if _stripe_adapter is None:
        _stripe_adapter = RentalStripeAdapter()
    return _stripe_adapter
