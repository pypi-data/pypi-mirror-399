# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
#
# ⚠️ DEPRECATION WARNING (Dec 2025):
# This module has been moved to krl-premium-backend.
# Import from: app.services.billing.rental_api
# This stub remains for backward compatibility but will be removed in v2.0.
# ----------------------------------------------------------------------

from __future__ import annotations
import warnings as _warnings
_warnings.warn(
    "krl_data_connectors.core.billing.rental_api is deprecated. "
    "Import from 'app.services.billing.rental_api' instead.",
    DeprecationWarning,
    stacklevel=2
)

"""
Temporary Model Rental API - Phase 6

FastAPI endpoints for institutional-grade temporary model rental system.
Target: $4.14M incremental ARR Year 1

Rental Mechanisms:
- Time passes: 1hr ($5) to 7-day ($99) temporary access
- Inference bundles: 100 ($4) to 5000 ($15) API calls
- Session tokens: 1hr ($25) to 24hr ($99) premium access

Revenue Architecture:
- 3-5x rental premium vs subscription (cannibalization control)
- 15% conversion to subscription within 90 days
- 12 rentals/month cap for community tier
- 6-hour cooling period between same-model rentals
"""


import hashlib
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone, UTC
from decimal import Decimal
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================

class RentalMechanismType(str, Enum):
    """Types of rental mechanisms."""
    TIME_PASS = "time_pass"
    INFERENCE_BUNDLE = "inference_bundle"
    SESSION_TOKEN = "session_token"


class TimePassType(str, Enum):
    """Time pass durations."""
    ONE_HOUR = "1_hour"
    FOUR_HOUR = "4_hour"
    TWENTY_FOUR_HOUR = "24_hour"
    THREE_DAY = "3_day"
    SEVEN_DAY = "7_day"


class InferenceBundleType(str, Enum):
    """Inference bundle sizes."""
    STARTER_100 = "starter_100"
    STANDARD_500 = "standard_500"
    PROFESSIONAL_1000 = "professional_1000"
    ENTERPRISE_5000 = "enterprise_5000"


class SessionTokenType(str, Enum):
    """Session token tiers."""
    BASIC_1HR = "basic_1hr"
    STANDARD_4HR = "standard_4hr"
    PREMIUM_24HR = "premium_24hr"


class RentalStatus(str, Enum):
    """Rental session status."""
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    EXPIRED = "expired"
    REVOKED = "revoked"
    CONVERTED = "converted"


class RentalTriggerType(str, Enum):
    """Contextual triggers for rental offers."""
    RATE_LIMIT_HIT = "rate_limit_hit"
    FEATURE_GATE = "feature_gate"
    QUOTA_WARNING = "quota_warning"
    MODEL_ACCESS = "model_access"
    INFERENCE_LIMIT = "inference_limit"
    PREMIUM_FEATURE = "premium_feature"
    TIME_SENSITIVE = "time_sensitive"
    TRIAL_EXPIRING = "trial_expiring"


class RentalFunnelStage(str, Enum):
    """Conversion funnel stages."""
    OFFER_SHOWN = "offer_shown"
    OFFER_CLICKED = "offer_clicked"
    CHECKOUT_STARTED = "checkout_started"
    PAYMENT_ATTEMPTED = "payment_attempted"
    PAYMENT_COMPLETED = "payment_completed"
    RENTAL_ACTIVATED = "rental_activated"
    RENTAL_USED = "rental_used"
    SUBSCRIPTION_OFFERED = "subscription_offered"
    SUBSCRIPTION_CONVERTED = "subscription_converted"


# =============================================================================
# Pricing Configuration
# =============================================================================

# Time Pass Pricing (3-5x subscription hourly rate)
TIME_PASS_PRICING: Dict[TimePassType, Dict[str, Any]] = {
    TimePassType.ONE_HOUR: {
        "price": Decimal("5.00"),
        "duration_minutes": 60,
        "features": ["basic_models", "standard_inference"],
        "premium_multiplier": 3.5,
    },
    TimePassType.FOUR_HOUR: {
        "price": Decimal("15.00"),
        "duration_minutes": 240,
        "features": ["basic_models", "standard_inference", "batch_processing"],
        "premium_multiplier": 3.2,
    },
    TimePassType.TWENTY_FOUR_HOUR: {
        "price": Decimal("35.00"),
        "duration_minutes": 1440,
        "features": ["all_models", "priority_inference", "batch_processing"],
        "premium_multiplier": 3.0,
    },
    TimePassType.THREE_DAY: {
        "price": Decimal("75.00"),
        "duration_minutes": 4320,
        "features": ["all_models", "priority_inference", "batch_processing", "api_access"],
        "premium_multiplier": 2.8,
    },
    TimePassType.SEVEN_DAY: {
        "price": Decimal("99.00"),
        "duration_minutes": 10080,
        "features": ["all_models", "priority_inference", "batch_processing", "api_access", "export"],
        "premium_multiplier": 2.5,
    },
}

# Inference Bundle Pricing (per-inference rates with volume discounts)
INFERENCE_BUNDLE_PRICING: Dict[InferenceBundleType, Dict[str, Any]] = {
    InferenceBundleType.STARTER_100: {
        "price": Decimal("4.00"),
        "inferences": 100,
        "per_inference": Decimal("0.040"),
        "models": ["basic"],
        "expiry_days": 30,
    },
    InferenceBundleType.STANDARD_500: {
        "price": Decimal("8.00"),
        "inferences": 500,
        "per_inference": Decimal("0.016"),
        "models": ["basic", "standard"],
        "expiry_days": 60,
    },
    InferenceBundleType.PROFESSIONAL_1000: {
        "price": Decimal("12.00"),
        "inferences": 1000,
        "per_inference": Decimal("0.012"),
        "models": ["basic", "standard", "professional"],
        "expiry_days": 90,
    },
    InferenceBundleType.ENTERPRISE_5000: {
        "price": Decimal("15.00"),
        "inferences": 5000,
        "per_inference": Decimal("0.003"),
        "models": ["all"],
        "expiry_days": 180,
    },
}

# Session Token Pricing (premium access tiers)
SESSION_TOKEN_PRICING: Dict[SessionTokenType, Dict[str, Any]] = {
    SessionTokenType.BASIC_1HR: {
        "price": Decimal("25.00"),
        "duration_minutes": 60,
        "tier": "pro",
        "priority": "standard",
        "concurrent_models": 2,
    },
    SessionTokenType.STANDARD_4HR: {
        "price": Decimal("65.00"),
        "duration_minutes": 240,
        "tier": "pro",
        "priority": "high",
        "concurrent_models": 5,
    },
    SessionTokenType.PREMIUM_24HR: {
        "price": Decimal("99.00"),
        "duration_minutes": 1440,
        "tier": "enterprise",
        "priority": "highest",
        "concurrent_models": 10,
    },
}

# Cannibalization Control Caps
RENTAL_CAPS_BY_TIER: Dict[str, Dict[str, Any]] = {
    "community": {
        "max_active_rentals": 1,
        "max_monthly_rentals": 12,
        "cooling_period_hours": 6,
        "max_monthly_spend": Decimal("150.00"),
    },
    "pro": {
        "max_active_rentals": 3,
        "max_monthly_rentals": 24,
        "cooling_period_hours": 2,
        "max_monthly_spend": Decimal("500.00"),
    },
    "enterprise": {
        "max_active_rentals": 10,
        "max_monthly_rentals": 100,
        "cooling_period_hours": 0,
        "max_monthly_spend": Decimal("5000.00"),
    },
}


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class RentalSession:
    """A temporary model rental session."""
    session_id: str
    tenant_id: str
    user_id: str
    
    # Rental type
    mechanism_type: RentalMechanismType
    rental_subtype: str  # TimePassType, InferenceBundleType, or SessionTokenType
    
    # Status
    status: RentalStatus
    
    # Timing
    created_at: datetime
    activated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Usage (for inference bundles)
    total_units: int = 0
    used_units: int = 0
    
    # Billing
    amount_paid: Decimal = Decimal("0")
    stripe_payment_intent_id: Optional[str] = None
    
    # Models
    model_ids: List[str] = field(default_factory=list)
    
    # Conversion tracking
    converted_to_subscription: bool = False
    conversion_offer_shown: bool = False
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_active(self) -> bool:
        """Check if rental is currently active."""
        if self.status != RentalStatus.ACTIVE:
            return False
        if self.expires_at and datetime.now(timezone.utc) > self.expires_at:
            return False
        if self.mechanism_type == RentalMechanismType.INFERENCE_BUNDLE:
            return self.used_units < self.total_units
        return True
    
    @property
    def time_remaining_seconds(self) -> int:
        """Get remaining time in seconds."""
        if not self.expires_at:
            return 0
        remaining = self.expires_at - datetime.now(timezone.utc)
        return max(0, int(remaining.total_seconds()))
    
    @property
    def usage_percentage(self) -> float:
        """Get usage percentage for inference bundles."""
        if self.total_units == 0:
            return 0.0
        return (self.used_units / self.total_units) * 100


@dataclass
class RentalOffer:
    """A contextual rental offer."""
    offer_id: str
    tenant_id: str
    
    # Trigger context
    trigger_type: RentalTriggerType
    trigger_context: Dict[str, Any]
    
    # Offer details
    mechanism_type: RentalMechanismType
    rental_subtype: str
    
    # Pricing
    original_price: Decimal
    offer_price: Decimal
    discount_percent: float = 0.0
    
    # Messaging (StoryBrand)
    headline: str = ""
    value_proposition: str = ""
    urgency_message: str = ""
    cta_text: str = ""
    
    # Timing
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    
    # Tracking
    shown: bool = False
    clicked: bool = False
    converted: bool = False
    
    # A/B testing
    experiment_id: Optional[str] = None
    variant_id: Optional[str] = None


@dataclass
class RentalCreditBalance:
    """Tenant's rental credit balance."""
    tenant_id: str
    
    # Balance
    available_credits: Decimal = Decimal("0")
    pending_credits: Decimal = Decimal("0")
    
    # History
    total_credits_added: Decimal = Decimal("0")
    total_credits_used: Decimal = Decimal("0")
    
    # Expiration
    credits_expiring_soon: Decimal = Decimal("0")
    expiration_date: Optional[datetime] = None
    
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RentalTransaction:
    """A rental billing transaction."""
    transaction_id: str
    tenant_id: str
    session_id: str
    
    # Type
    transaction_type: str  # purchase, refund, credit_usage, conversion_credit
    
    # Amount
    amount: Decimal
    
    # Status (no default - required field)
    status: str  # pending, completed, failed, refunded
    
    # Currency with default
    currency: str = "usd"
    
    # Stripe
    stripe_payment_intent_id: Optional[str] = None
    stripe_refund_id: Optional[str] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None


@dataclass
class FraudCheckResult:
    """Result of rental fraud check."""
    session_id: str
    tenant_id: str
    
    # Risk assessment
    is_approved: bool
    risk_score: float  # 0-100
    risk_level: str  # low, medium, high, critical
    
    # Signals
    signals: List[Dict[str, Any]] = field(default_factory=list)
    
    # Enforcement
    action: str = "allow"  # allow, challenge, block
    reason: str = ""
    
    # Velocity
    velocity_check_passed: bool = True
    
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ConversionEvent:
    """Rental-to-subscription conversion event."""
    event_id: str
    tenant_id: str
    session_id: str
    
    # Funnel stage
    stage: RentalFunnelStage
    
    # Context
    context: Dict[str, Any] = field(default_factory=dict)
    
    # A/B test
    experiment_id: Optional[str] = None
    variant_id: Optional[str] = None
    
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# =============================================================================
# Rental Session Manager
# =============================================================================

class RentalSessionManager:
    """
    Manages rental sessions lifecycle.
    
    Responsibilities:
    - Session creation and activation
    - Usage tracking and metering
    - Expiration management
    - Extension handling
    """
    
    def __init__(self):
        # In-memory storage (production: database)
        self._sessions: Dict[str, RentalSession] = {}
        self._tenant_sessions: Dict[str, List[str]] = {}
        self._model_sessions: Dict[str, List[str]] = {}
        
        # Cooling period tracker
        self._cooling_periods: Dict[str, datetime] = {}  # tenant:model -> cooldown_ends
    
    def create_session(
        self,
        tenant_id: str,
        user_id: str,
        mechanism_type: RentalMechanismType,
        rental_subtype: str,
        model_ids: List[str],
        payment_intent_id: Optional[str] = None,
    ) -> RentalSession:
        """Create a new rental session."""
        session_id = f"rental_{uuid.uuid4().hex[:16]}"
        
        # Get pricing
        price, units, duration = self._get_pricing_details(mechanism_type, rental_subtype)
        
        session = RentalSession(
            session_id=session_id,
            tenant_id=tenant_id,
            user_id=user_id,
            mechanism_type=mechanism_type,
            rental_subtype=rental_subtype,
            status=RentalStatus.PENDING,
            created_at=datetime.now(timezone.utc),
            total_units=units,
            amount_paid=price,
            stripe_payment_intent_id=payment_intent_id,
            model_ids=model_ids,
        )
        
        self._sessions[session_id] = session
        
        if tenant_id not in self._tenant_sessions:
            self._tenant_sessions[tenant_id] = []
        self._tenant_sessions[tenant_id].append(session_id)
        
        for model_id in model_ids:
            key = f"{tenant_id}:{model_id}"
            if key not in self._model_sessions:
                self._model_sessions[key] = []
            self._model_sessions[key].append(session_id)
        
        logger.info(f"Created rental session {session_id} for tenant {tenant_id}")
        return session
    
    def activate_session(self, session_id: str) -> RentalSession:
        """Activate a pending rental session."""
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        if session.status != RentalStatus.PENDING:
            raise ValueError(f"Session {session_id} is not pending")
        
        now = datetime.now(timezone.utc)
        session.status = RentalStatus.ACTIVE
        session.activated_at = now
        
        # Set expiration for time-based rentals
        if session.mechanism_type in (RentalMechanismType.TIME_PASS, RentalMechanismType.SESSION_TOKEN):
            duration = self._get_duration_minutes(session.mechanism_type, session.rental_subtype)
            session.expires_at = now + timedelta(minutes=duration)
        
        logger.info(f"Activated rental session {session_id}")
        return session
    
    def use_inference(self, session_id: str, count: int = 1) -> Tuple[bool, int]:
        """
        Record inference usage for a bundle session.
        
        Returns: (success, remaining_units)
        """
        session = self._sessions.get(session_id)
        if not session or not session.is_active:
            return False, 0
        
        if session.mechanism_type != RentalMechanismType.INFERENCE_BUNDLE:
            return True, 0  # Time-based, no unit tracking
        
        remaining = session.total_units - session.used_units
        if count > remaining:
            return False, remaining
        
        session.used_units += count
        remaining = session.total_units - session.used_units
        
        logger.debug(f"Session {session_id}: used {count}, remaining {remaining}")
        return True, remaining
    
    def extend_session(self, session_id: str, extension_type: str) -> RentalSession:
        """Extend an active session."""
        session = self._sessions.get(session_id)
        if not session or not session.is_active:
            raise ValueError(f"Session {session_id} not active")
        
        # Get extension pricing
        extension_minutes = self._get_extension_minutes(extension_type)
        session.expires_at = session.expires_at + timedelta(minutes=extension_minutes)
        
        logger.info(f"Extended session {session_id} by {extension_minutes} minutes")
        return session
    
    def revoke_session(self, session_id: str, reason: str = "") -> RentalSession:
        """Revoke a rental session."""
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        session.status = RentalStatus.REVOKED
        session.metadata["revoke_reason"] = reason
        session.metadata["revoked_at"] = datetime.now(timezone.utc).isoformat()
        
        logger.info(f"Revoked session {session_id}: {reason}")
        return session
    
    def get_session(self, session_id: str) -> Optional[RentalSession]:
        """Get a rental session by ID."""
        return self._sessions.get(session_id)
    
    def get_tenant_sessions(
        self,
        tenant_id: str,
        active_only: bool = False,
    ) -> List[RentalSession]:
        """Get all sessions for a tenant."""
        session_ids = self._tenant_sessions.get(tenant_id, [])
        sessions = [self._sessions[sid] for sid in session_ids if sid in self._sessions]
        
        if active_only:
            sessions = [s for s in sessions if s.is_active]
        
        return sessions
    
    def check_caps(self, tenant_id: str, tier: str) -> Dict[str, Any]:
        """Check if tenant is within rental caps."""
        caps = RENTAL_CAPS_BY_TIER.get(tier, RENTAL_CAPS_BY_TIER["community"])
        sessions = self.get_tenant_sessions(tenant_id)
        
        active_count = sum(1 for s in sessions if s.is_active)
        month_start = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0)
        monthly_count = sum(1 for s in sessions if s.created_at >= month_start)
        monthly_spend = sum(s.amount_paid for s in sessions if s.created_at >= month_start)
        
        return {
            "within_caps": (
                active_count < caps["max_active_rentals"] and
                monthly_count < caps["max_monthly_rentals"] and
                monthly_spend < caps["max_monthly_spend"]
            ),
            "active_rentals": active_count,
            "max_active_rentals": caps["max_active_rentals"],
            "monthly_rentals": monthly_count,
            "max_monthly_rentals": caps["max_monthly_rentals"],
            "monthly_spend": float(monthly_spend),
            "max_monthly_spend": float(caps["max_monthly_spend"]),
        }
    
    def check_cooling_period(
        self,
        tenant_id: str,
        model_id: str,
        tier: str,
    ) -> Tuple[bool, int]:
        """
        Check if cooling period allows rental.
        
        Returns: (can_rent, seconds_remaining)
        """
        caps = RENTAL_CAPS_BY_TIER.get(tier, RENTAL_CAPS_BY_TIER["community"])
        cooling_hours = caps.get("cooling_period_hours", 6)
        
        if cooling_hours == 0:
            return True, 0
        
        key = f"{tenant_id}:{model_id}"
        cooldown_ends = self._cooling_periods.get(key)
        
        if cooldown_ends is None:
            return True, 0
        
        now = datetime.now(timezone.utc)
        if now >= cooldown_ends:
            del self._cooling_periods[key]
            return True, 0
        
        remaining = int((cooldown_ends - now).total_seconds())
        return False, remaining
    
    def set_cooling_period(self, tenant_id: str, model_id: str, tier: str) -> None:
        """Set cooling period after rental ends."""
        caps = RENTAL_CAPS_BY_TIER.get(tier, RENTAL_CAPS_BY_TIER["community"])
        cooling_hours = caps.get("cooling_period_hours", 6)
        
        if cooling_hours == 0:
            return
        
        key = f"{tenant_id}:{model_id}"
        self._cooling_periods[key] = datetime.now(timezone.utc) + timedelta(hours=cooling_hours)
    
    def _get_pricing_details(
        self,
        mechanism: RentalMechanismType,
        subtype: str,
    ) -> Tuple[Decimal, int, int]:
        """Get price, units, and duration for a rental type."""
        if mechanism == RentalMechanismType.TIME_PASS:
            try:
                pass_type = TimePassType(subtype)
            except ValueError:
                pass_type = TimePassType.ONE_HOUR
            pricing = TIME_PASS_PRICING[pass_type]
            return pricing["price"], 0, pricing["duration_minutes"]
        
        elif mechanism == RentalMechanismType.INFERENCE_BUNDLE:
            try:
                bundle_type = InferenceBundleType(subtype)
            except ValueError:
                bundle_type = InferenceBundleType.STARTER_100
            pricing = INFERENCE_BUNDLE_PRICING[bundle_type]
            return pricing["price"], pricing["inferences"], 0
        
        elif mechanism == RentalMechanismType.SESSION_TOKEN:
            try:
                token_type = SessionTokenType(subtype)
            except ValueError:
                token_type = SessionTokenType.BASIC_1HR
            pricing = SESSION_TOKEN_PRICING[token_type]
            return pricing["price"], 0, pricing["duration_minutes"]
        
        return Decimal("5.00"), 0, 60
    
    def _get_duration_minutes(self, mechanism: RentalMechanismType, subtype: str) -> int:
        """Get duration in minutes for a rental type."""
        _, _, duration = self._get_pricing_details(mechanism, subtype)
        return duration if duration > 0 else 60
    
    def _get_extension_minutes(self, extension_type: str) -> int:
        """Get extension duration in minutes."""
        extensions = {
            "1_hour": 60,
            "4_hour": 240,
            "24_hour": 1440,
        }
        return extensions.get(extension_type, 60)


# =============================================================================
# Rental Offer Engine
# =============================================================================

class RentalOfferEngine:
    """
    Generates contextual rental offers based on user behavior.
    
    Uses StoryBrand framework for messaging:
    - Character (user) has a problem
    - Guide (KRL) has a plan
    - Calls to action drive conversion
    """
    
    def __init__(self):
        self._offers: Dict[str, RentalOffer] = {}
        self._tenant_offers: Dict[str, List[str]] = {}
    
    def generate_offer(
        self,
        tenant_id: str,
        trigger_type: RentalTriggerType,
        trigger_context: Dict[str, Any],
        experiment_id: Optional[str] = None,
        variant_id: Optional[str] = None,
    ) -> RentalOffer:
        """Generate a contextual rental offer."""
        # Select best mechanism for trigger
        mechanism, subtype = self._select_mechanism(trigger_type, trigger_context)
        
        # Get pricing
        price = self._get_price(mechanism, subtype)
        
        # Apply any variant discounts
        discount = 0.0
        if variant_id and variant_id.startswith("discount_"):
            discount = float(variant_id.split("_")[1]) / 100
        
        offer_price = price * Decimal(str(1 - discount))
        
        # Generate messaging
        headline, value_prop, urgency, cta = self._generate_messaging(
            trigger_type, trigger_context, mechanism, subtype
        )
        
        offer_id = f"offer_{uuid.uuid4().hex[:16]}"
        offer = RentalOffer(
            offer_id=offer_id,
            tenant_id=tenant_id,
            trigger_type=trigger_type,
            trigger_context=trigger_context,
            mechanism_type=mechanism,
            rental_subtype=subtype,
            original_price=price,
            offer_price=offer_price,
            discount_percent=discount * 100,
            headline=headline,
            value_proposition=value_prop,
            urgency_message=urgency,
            cta_text=cta,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
            experiment_id=experiment_id,
            variant_id=variant_id,
        )
        
        self._offers[offer_id] = offer
        if tenant_id not in self._tenant_offers:
            self._tenant_offers[tenant_id] = []
        self._tenant_offers[tenant_id].append(offer_id)
        
        return offer
    
    def get_offer(self, offer_id: str) -> Optional[RentalOffer]:
        """Get an offer by ID."""
        return self._offers.get(offer_id)
    
    def mark_shown(self, offer_id: str) -> None:
        """Mark offer as shown."""
        offer = self._offers.get(offer_id)
        if offer:
            offer.shown = True
    
    def mark_clicked(self, offer_id: str) -> None:
        """Mark offer as clicked."""
        offer = self._offers.get(offer_id)
        if offer:
            offer.clicked = True
    
    def mark_converted(self, offer_id: str) -> None:
        """Mark offer as converted."""
        offer = self._offers.get(offer_id)
        if offer:
            offer.converted = True
    
    def _select_mechanism(
        self,
        trigger_type: RentalTriggerType,
        context: Dict[str, Any],
    ) -> Tuple[RentalMechanismType, str]:
        """Select best rental mechanism for trigger."""
        # Map triggers to optimal mechanisms
        trigger_mapping = {
            RentalTriggerType.RATE_LIMIT_HIT: (
                RentalMechanismType.TIME_PASS,
                TimePassType.FOUR_HOUR.value,
            ),
            RentalTriggerType.FEATURE_GATE: (
                RentalMechanismType.SESSION_TOKEN,
                SessionTokenType.STANDARD_4HR.value,
            ),
            RentalTriggerType.QUOTA_WARNING: (
                RentalMechanismType.INFERENCE_BUNDLE,
                InferenceBundleType.STANDARD_500.value,
            ),
            RentalTriggerType.MODEL_ACCESS: (
                RentalMechanismType.SESSION_TOKEN,
                SessionTokenType.BASIC_1HR.value,
            ),
            RentalTriggerType.INFERENCE_LIMIT: (
                RentalMechanismType.INFERENCE_BUNDLE,
                InferenceBundleType.PROFESSIONAL_1000.value,
            ),
            RentalTriggerType.PREMIUM_FEATURE: (
                RentalMechanismType.SESSION_TOKEN,
                SessionTokenType.PREMIUM_24HR.value,
            ),
            RentalTriggerType.TIME_SENSITIVE: (
                RentalMechanismType.TIME_PASS,
                TimePassType.ONE_HOUR.value,
            ),
            RentalTriggerType.TRIAL_EXPIRING: (
                RentalMechanismType.TIME_PASS,
                TimePassType.THREE_DAY.value,
            ),
        }
        
        return trigger_mapping.get(
            trigger_type,
            (RentalMechanismType.TIME_PASS, TimePassType.FOUR_HOUR.value),
        )
    
    def _get_price(self, mechanism: RentalMechanismType, subtype: str) -> Decimal:
        """Get price for a rental type."""
        if mechanism == RentalMechanismType.TIME_PASS:
            try:
                return TIME_PASS_PRICING[TimePassType(subtype)]["price"]
            except (ValueError, KeyError):
                return Decimal("15.00")
        
        elif mechanism == RentalMechanismType.INFERENCE_BUNDLE:
            try:
                return INFERENCE_BUNDLE_PRICING[InferenceBundleType(subtype)]["price"]
            except (ValueError, KeyError):
                return Decimal("8.00")
        
        elif mechanism == RentalMechanismType.SESSION_TOKEN:
            try:
                return SESSION_TOKEN_PRICING[SessionTokenType(subtype)]["price"]
            except (ValueError, KeyError):
                return Decimal("25.00")
        
        return Decimal("15.00")
    
    def _generate_messaging(
        self,
        trigger_type: RentalTriggerType,
        context: Dict[str, Any],
        mechanism: RentalMechanismType,
        subtype: str,
    ) -> Tuple[str, str, str, str]:
        """Generate StoryBrand messaging for offer."""
        # Problem-focused headlines by trigger
        headlines = {
            RentalTriggerType.RATE_LIMIT_HIT: "Don't Let Limits Stop Your Progress",
            RentalTriggerType.FEATURE_GATE: "Unlock Premium Features Instantly",
            RentalTriggerType.QUOTA_WARNING: "Running Low? Get More Inferences",
            RentalTriggerType.MODEL_ACCESS: "Access This Model Right Now",
            RentalTriggerType.INFERENCE_LIMIT: "Need More Inference Power?",
            RentalTriggerType.PREMIUM_FEATURE: "Premium Access Awaits",
            RentalTriggerType.TIME_SENSITIVE: "Quick Access When You Need It",
            RentalTriggerType.TRIAL_EXPIRING: "Extend Your Premium Experience",
        }
        
        # Value propositions by mechanism
        value_props = {
            RentalMechanismType.TIME_PASS: "Get unlimited access for a fixed time period. No commitment, no subscription.",
            RentalMechanismType.INFERENCE_BUNDLE: "Pay only for what you use. Inferences never expire.",
            RentalMechanismType.SESSION_TOKEN: "Enterprise-grade priority access. Maximum performance.",
        }
        
        # Urgency messaging
        urgency_messages = {
            RentalTriggerType.RATE_LIMIT_HIT: "Your rate limit resets in {reset_time}. Get instant access now.",
            RentalTriggerType.FEATURE_GATE: "This feature is available with a quick unlock.",
            RentalTriggerType.QUOTA_WARNING: "Only {remaining}% of your quota remains.",
            RentalTriggerType.TIME_SENSITIVE: "Time-limited access available now.",
        }
        
        # CTAs by mechanism
        ctas = {
            RentalMechanismType.TIME_PASS: "Get Time Pass",
            RentalMechanismType.INFERENCE_BUNDLE: "Buy Inferences",
            RentalMechanismType.SESSION_TOKEN: "Unlock Access",
        }
        
        headline = headlines.get(trigger_type, "Upgrade Your Experience")
        value_prop = value_props.get(mechanism, "Flexible access on your terms.")
        urgency = urgency_messages.get(trigger_type, "Limited time offer.")
        cta = ctas.get(mechanism, "Get Access")
        
        # Format urgency with context
        if "{reset_time}" in urgency:
            urgency = urgency.format(reset_time=context.get("reset_time", "soon"))
        if "{remaining}" in urgency:
            urgency = urgency.format(remaining=context.get("remaining_percent", "10"))
        
        return headline, value_prop, urgency, cta


# =============================================================================
# Rental Fraud Detector
# =============================================================================

class RentalFraudDetector:
    """
    Fraud detection for rental system.
    
    Detects:
    - Velocity abuse (rapid purchases)
    - Multi-account abuse
    - Payment fraud signals
    - Usage pattern anomalies
    """
    
    def __init__(self):
        # Track recent activity by various dimensions
        self._purchase_velocity: Dict[str, List[datetime]] = {}  # tenant_id -> timestamps
        self._device_fingerprints: Dict[str, Set[str]] = {}  # tenant_id -> device hashes
        self._ip_addresses: Dict[str, Set[str]] = {}  # tenant_id -> IPs
    
    def check_rental_fraud(
        self,
        tenant_id: str,
        session_id: str,
        amount: Decimal,
        device_fingerprint: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> FraudCheckResult:
        """Check for fraud signals on a rental attempt."""
        signals = []
        risk_score = 0.0
        
        # Velocity check
        velocity_risk, velocity_signal = self._check_velocity(tenant_id)
        if velocity_signal:
            signals.append(velocity_signal)
            risk_score += velocity_risk
        
        # Device fingerprint check
        if device_fingerprint:
            device_risk, device_signal = self._check_device(tenant_id, device_fingerprint)
            if device_signal:
                signals.append(device_signal)
                risk_score += device_risk
        
        # IP check
        if ip_address:
            ip_risk, ip_signal = self._check_ip(tenant_id, ip_address)
            if ip_signal:
                signals.append(ip_signal)
                risk_score += ip_risk
        
        # Amount check
        if amount > Decimal("100"):
            risk_score += 10
            signals.append({
                "type": "high_amount",
                "details": {"amount": float(amount)},
                "risk_contribution": 10,
            })
        
        # Determine risk level and action
        risk_level = self._risk_level_from_score(risk_score)
        action, reason = self._determine_action(risk_score, risk_level)
        
        return FraudCheckResult(
            session_id=session_id,
            tenant_id=tenant_id,
            is_approved=(action == "allow"),
            risk_score=risk_score,
            risk_level=risk_level,
            signals=signals,
            action=action,
            reason=reason,
            velocity_check_passed=(velocity_risk < 30),
        )
    
    def record_purchase(self, tenant_id: str) -> None:
        """Record a purchase for velocity tracking."""
        if tenant_id not in self._purchase_velocity:
            self._purchase_velocity[tenant_id] = []
        
        now = datetime.now(timezone.utc)
        self._purchase_velocity[tenant_id].append(now)
        
        # Keep only last hour
        cutoff = now - timedelta(hours=1)
        self._purchase_velocity[tenant_id] = [
            ts for ts in self._purchase_velocity[tenant_id]
            if ts > cutoff
        ]
    
    def _check_velocity(self, tenant_id: str) -> Tuple[float, Optional[Dict]]:
        """Check purchase velocity."""
        purchases = self._purchase_velocity.get(tenant_id, [])
        
        # Count purchases in last hour
        now = datetime.now(timezone.utc)
        recent = [ts for ts in purchases if (now - ts).total_seconds() < 3600]
        count = len(recent)
        
        if count >= 5:
            return 40, {
                "type": "velocity_anomaly",
                "details": {"purchases_last_hour": count},
                "risk_contribution": 40,
            }
        elif count >= 3:
            return 20, {
                "type": "velocity_warning",
                "details": {"purchases_last_hour": count},
                "risk_contribution": 20,
            }
        
        return 0, None
    
    def _check_device(
        self,
        tenant_id: str,
        fingerprint: str,
    ) -> Tuple[float, Optional[Dict]]:
        """Check device fingerprint patterns."""
        if tenant_id not in self._device_fingerprints:
            self._device_fingerprints[tenant_id] = set()
        
        known_devices = self._device_fingerprints[tenant_id]
        is_new = fingerprint not in known_devices
        
        # Track the device
        known_devices.add(fingerprint)
        
        if len(known_devices) > 5:
            return 25, {
                "type": "multiple_devices",
                "details": {"device_count": len(known_devices)},
                "risk_contribution": 25,
            }
        
        if is_new and len(known_devices) > 2:
            return 15, {
                "type": "new_device",
                "details": {"device_count": len(known_devices)},
                "risk_contribution": 15,
            }
        
        return 0, None
    
    def _check_ip(
        self,
        tenant_id: str,
        ip_address: str,
    ) -> Tuple[float, Optional[Dict]]:
        """Check IP address patterns."""
        if tenant_id not in self._ip_addresses:
            self._ip_addresses[tenant_id] = set()
        
        known_ips = self._ip_addresses[tenant_id]
        is_new = ip_address not in known_ips
        
        # Track the IP
        known_ips.add(ip_address)
        
        if len(known_ips) > 10:
            return 30, {
                "type": "geo_anomaly",
                "details": {"ip_count": len(known_ips)},
                "risk_contribution": 30,
            }
        
        if is_new and len(known_ips) > 3:
            return 10, {
                "type": "new_ip",
                "details": {"ip_count": len(known_ips)},
                "risk_contribution": 10,
            }
        
        return 0, None
    
    def _risk_level_from_score(self, score: float) -> str:
        """Convert risk score to level."""
        if score >= 75:
            return "critical"
        elif score >= 50:
            return "high"
        elif score >= 25:
            return "medium"
        return "low"
    
    def _determine_action(
        self,
        score: float,
        level: str,
    ) -> Tuple[str, str]:
        """Determine enforcement action."""
        if score >= 75:
            return "block", "Risk score exceeds threshold"
        elif score >= 50:
            return "challenge", "Elevated risk requires verification"
        elif score >= 30:
            return "allow", "Medium risk - monitoring"
        return "allow", ""


# =============================================================================
# Conversion Tracker
# =============================================================================

class ConversionTracker:
    """
    Tracks rental-to-subscription conversions.
    
    Target: 15% conversion within 90 days
    """
    
    def __init__(self):
        self._events: List[ConversionEvent] = []
        self._tenant_funnel: Dict[str, Dict[str, datetime]] = {}  # tenant -> stage -> timestamp
    
    def track_event(
        self,
        tenant_id: str,
        session_id: str,
        stage: RentalFunnelStage,
        context: Optional[Dict[str, Any]] = None,
        experiment_id: Optional[str] = None,
        variant_id: Optional[str] = None,
    ) -> ConversionEvent:
        """Track a conversion funnel event."""
        event = ConversionEvent(
            event_id=f"evt_{uuid.uuid4().hex[:16]}",
            tenant_id=tenant_id,
            session_id=session_id,
            stage=stage,
            context=context or {},
            experiment_id=experiment_id,
            variant_id=variant_id,
        )
        
        self._events.append(event)
        
        # Update funnel state
        if tenant_id not in self._tenant_funnel:
            self._tenant_funnel[tenant_id] = {}
        self._tenant_funnel[tenant_id][stage.value] = event.timestamp
        
        logger.info(f"Tracked conversion event: {tenant_id} -> {stage.value}")
        return event
    
    def get_funnel_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get funnel conversion metrics."""
        if start_date is None:
            start_date = datetime.now(timezone.utc) - timedelta(days=30)
        if end_date is None:
            end_date = datetime.now(timezone.utc)
        
        # Filter events by date
        events = [
            e for e in self._events
            if start_date <= e.timestamp <= end_date
        ]
        
        # Count by stage
        stage_counts: Dict[str, int] = {}
        for stage in RentalFunnelStage:
            stage_counts[stage.value] = sum(1 for e in events if e.stage == stage)
        
        # Calculate conversion rates
        total_shown = stage_counts.get("offer_shown", 0)
        conversions = {
            "offer_to_click": self._safe_rate(
                stage_counts.get("offer_clicked", 0), total_shown
            ),
            "click_to_checkout": self._safe_rate(
                stage_counts.get("checkout_started", 0),
                stage_counts.get("offer_clicked", 0),
            ),
            "checkout_to_payment": self._safe_rate(
                stage_counts.get("payment_completed", 0),
                stage_counts.get("checkout_started", 0),
            ),
            "rental_to_subscription": self._safe_rate(
                stage_counts.get("subscription_converted", 0),
                stage_counts.get("rental_activated", 0),
            ),
        }
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "stage_counts": stage_counts,
            "conversion_rates": conversions,
            "total_events": len(events),
        }
    
    def get_tenant_journey(self, tenant_id: str) -> Dict[str, Any]:
        """Get conversion journey for a tenant."""
        funnel = self._tenant_funnel.get(tenant_id, {})
        tenant_events = [e for e in self._events if e.tenant_id == tenant_id]
        
        return {
            "tenant_id": tenant_id,
            "stages_reached": list(funnel.keys()),
            "event_count": len(tenant_events),
            "first_event": min(e.timestamp for e in tenant_events).isoformat() if tenant_events else None,
            "last_event": max(e.timestamp for e in tenant_events).isoformat() if tenant_events else None,
        }
    
    def _safe_rate(self, numerator: int, denominator: int) -> float:
        """Calculate rate safely."""
        if denominator == 0:
            return 0.0
        return round(numerator / denominator * 100, 2)


# =============================================================================
# Singleton Instances
# =============================================================================

# Global instances for API
_session_manager: Optional[RentalSessionManager] = None
_offer_engine: Optional[RentalOfferEngine] = None
_fraud_detector: Optional[RentalFraudDetector] = None
_conversion_tracker: Optional[ConversionTracker] = None


def get_session_manager() -> RentalSessionManager:
    """Get or create session manager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = RentalSessionManager()
    return _session_manager


def get_offer_engine() -> RentalOfferEngine:
    """Get or create offer engine instance."""
    global _offer_engine
    if _offer_engine is None:
        _offer_engine = RentalOfferEngine()
    return _offer_engine


def get_fraud_detector() -> RentalFraudDetector:
    """Get or create fraud detector instance."""
    global _fraud_detector
    if _fraud_detector is None:
        _fraud_detector = RentalFraudDetector()
    return _fraud_detector


def get_conversion_tracker() -> ConversionTracker:
    """Get or create conversion tracker instance."""
    global _conversion_tracker
    if _conversion_tracker is None:
        _conversion_tracker = ConversionTracker()
    return _conversion_tracker
