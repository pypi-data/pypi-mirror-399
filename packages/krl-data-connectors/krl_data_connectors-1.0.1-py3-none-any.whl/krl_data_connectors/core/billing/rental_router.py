# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
#
# ⚠️ DEPRECATION WARNING (Dec 2025):
# This module has been moved to krl-premium-backend.
# Import from: app.services.billing.rental_router
# This stub remains for backward compatibility but will be removed in v2.0.
# ----------------------------------------------------------------------

from __future__ import annotations
import warnings as _warnings
_warnings.warn(
    "krl_data_connectors.core.billing.rental_router is deprecated. "
    "Import from 'app.services.billing.rental_router' instead.",
    DeprecationWarning,
    stacklevel=2
)

"""
Rental FastAPI Router - Phase 6

REST API endpoints for the temporary model rental system.
Provides session management, offer generation, and billing integration.
"""


import logging
from datetime import datetime, timezone, UTC
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Try to import FastAPI, fallback to mock for typing
try:
    from fastapi import APIRouter, Depends, HTTPException, Header, Query, Request
    from fastapi.responses import JSONResponse
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    # Mock types for when FastAPI isn't installed
    class APIRouter:
        def __init__(self, *args, **kwargs): pass
        def get(self, *args, **kwargs): return lambda f: f
        def post(self, *args, **kwargs): return lambda f: f
        def put(self, *args, **kwargs): return lambda f: f
        def delete(self, *args, **kwargs): return lambda f: f
    
    class Depends:
        def __init__(self, *args, **kwargs): pass
    
    class HTTPException(Exception):
        def __init__(self, status_code: int, detail: str): pass
    
    def Header(*args, **kwargs): return None
    def Query(*args, **kwargs): return None
    
    class Request: pass
    class JSONResponse: pass

from .rental_api import (
    RentalMechanismType,
    RentalTriggerType,
    RentalFunnelStage,
    RentalStatus,
    get_session_manager,
    get_offer_engine,
    get_fraud_detector,
    get_conversion_tracker,
    TIME_PASS_PRICING,
    INFERENCE_BUNDLE_PRICING,
    SESSION_TOKEN_PRICING,
    RENTAL_CAPS_BY_TIER,
)


# =============================================================================
# Pydantic Request/Response Models
# =============================================================================

class CreateRentalRequest(BaseModel):
    """Request to create a new rental session."""
    mechanism_type: str = Field(..., description="Type of rental: time_pass, inference_bundle, session_token")
    rental_subtype: str = Field(..., description="Specific type within mechanism")
    model_ids: List[str] = Field(default_factory=list, description="Models to rent access to")
    payment_intent_id: Optional[str] = Field(None, description="Stripe PaymentIntent ID")
    offer_id: Optional[str] = Field(None, description="Offer ID if from contextual offer")


class ExtendRentalRequest(BaseModel):
    """Request to extend a rental session."""
    extension_type: str = Field(..., description="Extension duration: 1_hour, 4_hour, 24_hour")


class UseInferenceRequest(BaseModel):
    """Request to record inference usage."""
    count: int = Field(1, ge=1, le=100, description="Number of inferences to record")


class GenerateOfferRequest(BaseModel):
    """Request to generate a rental offer."""
    trigger_type: str = Field(..., description="Trigger type for contextual offer")
    trigger_context: Dict[str, Any] = Field(default_factory=dict, description="Context for offer generation")
    experiment_id: Optional[str] = Field(None, description="A/B test experiment ID")
    variant_id: Optional[str] = Field(None, description="A/B test variant ID")


class FraudCheckRequest(BaseModel):
    """Request for fraud check."""
    session_id: str = Field(..., description="Session ID to check")
    amount: float = Field(..., ge=0, description="Transaction amount")
    device_fingerprint: Optional[str] = Field(None, description="Device fingerprint hash")
    ip_address: Optional[str] = Field(None, description="Client IP address")


class TrackConversionRequest(BaseModel):
    """Request to track conversion event."""
    session_id: str = Field(..., description="Rental session ID")
    stage: str = Field(..., description="Funnel stage")
    context: Dict[str, Any] = Field(default_factory=dict, description="Event context")
    experiment_id: Optional[str] = Field(None, description="A/B test experiment ID")
    variant_id: Optional[str] = Field(None, description="A/B test variant ID")


class RentalSessionResponse(BaseModel):
    """Rental session response."""
    session_id: str
    tenant_id: str
    user_id: str
    mechanism_type: str
    rental_subtype: str
    status: str
    created_at: str
    activated_at: Optional[str]
    expires_at: Optional[str]
    total_units: int
    used_units: int
    amount_paid: float
    model_ids: List[str]
    is_active: bool
    time_remaining_seconds: int
    usage_percentage: float


class RentalOfferResponse(BaseModel):
    """Rental offer response."""
    offer_id: str
    mechanism_type: str
    rental_subtype: str
    original_price: float
    offer_price: float
    discount_percent: float
    headline: str
    value_proposition: str
    urgency_message: str
    cta_text: str
    expires_at: str


class FraudCheckResponse(BaseModel):
    """Fraud check response."""
    session_id: str
    is_approved: bool
    risk_score: float
    risk_level: str
    action: str
    reason: str
    signals: List[Dict[str, Any]]


class CapsCheckResponse(BaseModel):
    """Rental caps check response."""
    within_caps: bool
    active_rentals: int
    max_active_rentals: int
    monthly_rentals: int
    max_monthly_rentals: int
    monthly_spend: float
    max_monthly_spend: float


class FunnelMetricsResponse(BaseModel):
    """Funnel metrics response."""
    period: Dict[str, str]
    stage_counts: Dict[str, int]
    conversion_rates: Dict[str, float]
    total_events: int


# =============================================================================
# FastAPI Router
# =============================================================================

router = APIRouter(prefix="/api/v1/rentals", tags=["rentals"])


# -----------------------------------------------------------------------------
# Session Endpoints
# -----------------------------------------------------------------------------

@router.post("/sessions", response_model=RentalSessionResponse)
async def create_rental_session(
    request: CreateRentalRequest,
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
    x_user_id: str = Header(..., alias="X-User-ID"),
):
    """
    Create a new rental session.
    
    Validates caps, checks fraud, and creates pending session.
    Session must be activated after payment confirmation.
    """
    manager = get_session_manager()
    fraud = get_fraud_detector()
    
    # Validate mechanism type
    try:
        mechanism = RentalMechanismType(request.mechanism_type)
    except ValueError:
        raise HTTPException(400, f"Invalid mechanism type: {request.mechanism_type}")
    
    # Check caps
    caps = manager.check_caps(x_tenant_id, "community")  # TODO: Get tier from auth
    if not caps["within_caps"]:
        raise HTTPException(429, "Rental caps exceeded")
    
    # Check cooling period for each model
    for model_id in request.model_ids:
        can_rent, remaining = manager.check_cooling_period(x_tenant_id, model_id, "community")
        if not can_rent:
            raise HTTPException(429, f"Cooling period active for model {model_id}: {remaining}s remaining")
    
    # Create session
    session = manager.create_session(
        tenant_id=x_tenant_id,
        user_id=x_user_id,
        mechanism_type=mechanism,
        rental_subtype=request.rental_subtype,
        model_ids=request.model_ids,
        payment_intent_id=request.payment_intent_id,
    )
    
    # Fraud check
    fraud_result = fraud.check_rental_fraud(
        tenant_id=x_tenant_id,
        session_id=session.session_id,
        amount=session.amount_paid,
    )
    
    if not fraud_result.is_approved:
        manager.revoke_session(session.session_id, fraud_result.reason)
        raise HTTPException(403, f"Fraud check failed: {fraud_result.reason}")
    
    # Track conversion event
    tracker = get_conversion_tracker()
    tracker.track_event(
        tenant_id=x_tenant_id,
        session_id=session.session_id,
        stage=RentalFunnelStage.RENTAL_ACTIVATED if request.payment_intent_id else RentalFunnelStage.CHECKOUT_STARTED,
    )
    
    return _session_to_response(session)


@router.post("/sessions/{session_id}/activate", response_model=RentalSessionResponse)
async def activate_rental_session(
    session_id: str,
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
):
    """Activate a pending rental session after payment confirmation."""
    manager = get_session_manager()
    
    session = manager.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    
    if session.tenant_id != x_tenant_id:
        raise HTTPException(403, "Not authorized to activate this session")
    
    try:
        session = manager.activate_session(session_id)
    except ValueError as e:
        raise HTTPException(400, str(e))
    
    # Track activation
    tracker = get_conversion_tracker()
    tracker.track_event(
        tenant_id=x_tenant_id,
        session_id=session_id,
        stage=RentalFunnelStage.RENTAL_ACTIVATED,
    )
    
    return _session_to_response(session)


@router.get("/sessions/{session_id}", response_model=RentalSessionResponse)
async def get_rental_session(
    session_id: str,
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
):
    """Get rental session details."""
    manager = get_session_manager()
    
    session = manager.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    
    if session.tenant_id != x_tenant_id:
        raise HTTPException(403, "Not authorized to view this session")
    
    return _session_to_response(session)


@router.get("/sessions", response_model=List[RentalSessionResponse])
async def list_rental_sessions(
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
    active_only: bool = Query(False, description="Only return active sessions"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List rental sessions for tenant."""
    manager = get_session_manager()
    
    sessions = manager.get_tenant_sessions(x_tenant_id, active_only=active_only)
    
    # Paginate
    sessions = sessions[offset:offset + limit]
    
    return [_session_to_response(s) for s in sessions]


@router.post("/sessions/{session_id}/extend", response_model=RentalSessionResponse)
async def extend_rental_session(
    session_id: str,
    request: ExtendRentalRequest,
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
):
    """Extend an active rental session."""
    manager = get_session_manager()
    
    session = manager.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    
    if session.tenant_id != x_tenant_id:
        raise HTTPException(403, "Not authorized to extend this session")
    
    try:
        session = manager.extend_session(session_id, request.extension_type)
    except ValueError as e:
        raise HTTPException(400, str(e))
    
    return _session_to_response(session)


@router.post("/sessions/{session_id}/use", response_model=Dict[str, Any])
async def use_inference(
    session_id: str,
    request: UseInferenceRequest,
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
):
    """Record inference usage for bundle sessions."""
    manager = get_session_manager()
    
    session = manager.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    
    if session.tenant_id != x_tenant_id:
        raise HTTPException(403, "Not authorized to use this session")
    
    success, remaining = manager.use_inference(session_id, request.count)
    
    if not success:
        raise HTTPException(400, f"Insufficient units. Remaining: {remaining}")
    
    # Track usage
    tracker = get_conversion_tracker()
    tracker.track_event(
        tenant_id=x_tenant_id,
        session_id=session_id,
        stage=RentalFunnelStage.RENTAL_USED,
        context={"inferences_used": request.count, "remaining": remaining},
    )
    
    return {
        "success": True,
        "used": request.count,
        "remaining": remaining,
        "usage_percentage": session.usage_percentage,
    }


@router.delete("/sessions/{session_id}")
async def revoke_rental_session(
    session_id: str,
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
    reason: str = Query("user_request", description="Revocation reason"),
):
    """Revoke a rental session."""
    manager = get_session_manager()
    
    session = manager.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    
    if session.tenant_id != x_tenant_id:
        raise HTTPException(403, "Not authorized to revoke this session")
    
    manager.revoke_session(session_id, reason)
    
    return {"success": True, "session_id": session_id, "status": "revoked"}


# -----------------------------------------------------------------------------
# Offer Endpoints
# -----------------------------------------------------------------------------

@router.post("/offers", response_model=RentalOfferResponse)
async def generate_offer(
    request: GenerateOfferRequest,
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
):
    """Generate a contextual rental offer."""
    engine = get_offer_engine()
    
    # Validate trigger type
    try:
        trigger = RentalTriggerType(request.trigger_type)
    except ValueError:
        raise HTTPException(400, f"Invalid trigger type: {request.trigger_type}")
    
    offer = engine.generate_offer(
        tenant_id=x_tenant_id,
        trigger_type=trigger,
        trigger_context=request.trigger_context,
        experiment_id=request.experiment_id,
        variant_id=request.variant_id,
    )
    
    # Track offer shown
    tracker = get_conversion_tracker()
    tracker.track_event(
        tenant_id=x_tenant_id,
        session_id=offer.offer_id,
        stage=RentalFunnelStage.OFFER_SHOWN,
        experiment_id=request.experiment_id,
        variant_id=request.variant_id,
    )
    
    return _offer_to_response(offer)


@router.get("/offers/{offer_id}", response_model=RentalOfferResponse)
async def get_offer(
    offer_id: str,
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
):
    """Get rental offer details."""
    engine = get_offer_engine()
    
    offer = engine.get_offer(offer_id)
    if not offer:
        raise HTTPException(404, "Offer not found")
    
    if offer.tenant_id != x_tenant_id:
        raise HTTPException(403, "Not authorized to view this offer")
    
    return _offer_to_response(offer)


@router.post("/offers/{offer_id}/click")
async def track_offer_click(
    offer_id: str,
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
):
    """Track offer click event."""
    engine = get_offer_engine()
    
    offer = engine.get_offer(offer_id)
    if not offer:
        raise HTTPException(404, "Offer not found")
    
    engine.mark_clicked(offer_id)
    
    # Track conversion event
    tracker = get_conversion_tracker()
    tracker.track_event(
        tenant_id=x_tenant_id,
        session_id=offer_id,
        stage=RentalFunnelStage.OFFER_CLICKED,
        experiment_id=offer.experiment_id,
        variant_id=offer.variant_id,
    )
    
    return {"success": True}


# -----------------------------------------------------------------------------
# Caps & Validation Endpoints
# -----------------------------------------------------------------------------

@router.get("/caps", response_model=CapsCheckResponse)
async def check_rental_caps(
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
    tier: str = Query("community", description="Tenant tier"),
):
    """Check tenant's rental caps."""
    manager = get_session_manager()
    
    caps = manager.check_caps(x_tenant_id, tier)
    
    return CapsCheckResponse(**caps)


@router.get("/cooling/{model_id}")
async def check_cooling_period(
    model_id: str,
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
    tier: str = Query("community", description="Tenant tier"),
):
    """Check cooling period for a model."""
    manager = get_session_manager()
    
    can_rent, remaining = manager.check_cooling_period(x_tenant_id, model_id, tier)
    
    return {
        "model_id": model_id,
        "can_rent": can_rent,
        "seconds_remaining": remaining,
    }


# -----------------------------------------------------------------------------
# Fraud Endpoints
# -----------------------------------------------------------------------------

@router.post("/fraud/check", response_model=FraudCheckResponse)
async def check_fraud(
    request: FraudCheckRequest,
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
):
    """Run fraud check on a rental attempt."""
    detector = get_fraud_detector()
    
    result = detector.check_rental_fraud(
        tenant_id=x_tenant_id,
        session_id=request.session_id,
        amount=Decimal(str(request.amount)),
        device_fingerprint=request.device_fingerprint,
        ip_address=request.ip_address,
    )
    
    return FraudCheckResponse(
        session_id=result.session_id,
        is_approved=result.is_approved,
        risk_score=result.risk_score,
        risk_level=result.risk_level,
        action=result.action,
        reason=result.reason,
        signals=result.signals,
    )


# -----------------------------------------------------------------------------
# Conversion Tracking Endpoints
# -----------------------------------------------------------------------------

@router.post("/conversion/track")
async def track_conversion(
    request: TrackConversionRequest,
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
):
    """Track a conversion funnel event."""
    tracker = get_conversion_tracker()
    
    # Validate stage
    try:
        stage = RentalFunnelStage(request.stage)
    except ValueError:
        raise HTTPException(400, f"Invalid funnel stage: {request.stage}")
    
    event = tracker.track_event(
        tenant_id=x_tenant_id,
        session_id=request.session_id,
        stage=stage,
        context=request.context,
        experiment_id=request.experiment_id,
        variant_id=request.variant_id,
    )
    
    return {"success": True, "event_id": event.event_id}


@router.get("/conversion/metrics", response_model=FunnelMetricsResponse)
async def get_funnel_metrics(
    start_date: Optional[str] = Query(None, description="Start date ISO format"),
    end_date: Optional[str] = Query(None, description="End date ISO format"),
):
    """Get conversion funnel metrics."""
    tracker = get_conversion_tracker()
    
    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None
    
    metrics = tracker.get_funnel_metrics(start, end)
    
    return FunnelMetricsResponse(**metrics)


@router.get("/conversion/journey/{tenant_id}")
async def get_tenant_journey(
    tenant_id: str,
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
):
    """Get conversion journey for a tenant."""
    # Admin only or self
    if x_tenant_id != tenant_id:
        # TODO: Add admin check
        pass
    
    tracker = get_conversion_tracker()
    journey = tracker.get_tenant_journey(tenant_id)
    
    return journey


# -----------------------------------------------------------------------------
# Pricing Endpoints
# -----------------------------------------------------------------------------

@router.get("/pricing")
async def get_pricing():
    """Get all rental pricing options."""
    return {
        "time_passes": {
            k.value: {
                "price": float(v["price"]),
                "duration_minutes": v["duration_minutes"],
                "features": v["features"],
            }
            for k, v in TIME_PASS_PRICING.items()
        },
        "inference_bundles": {
            k.value: {
                "price": float(v["price"]),
                "inferences": v["inferences"],
                "per_inference": float(v["per_inference"]),
                "models": v["models"],
                "expiry_days": v["expiry_days"],
            }
            for k, v in INFERENCE_BUNDLE_PRICING.items()
        },
        "session_tokens": {
            k.value: {
                "price": float(v["price"]),
                "duration_minutes": v["duration_minutes"],
                "tier": v["tier"],
                "priority": v["priority"],
                "concurrent_models": v["concurrent_models"],
            }
            for k, v in SESSION_TOKEN_PRICING.items()
        },
    }


@router.get("/caps/tiers")
async def get_tier_caps():
    """Get rental caps by tier."""
    return {
        tier: {
            "max_active_rentals": caps["max_active_rentals"],
            "max_monthly_rentals": caps["max_monthly_rentals"],
            "cooling_period_hours": caps["cooling_period_hours"],
            "max_monthly_spend": float(caps["max_monthly_spend"]),
        }
        for tier, caps in RENTAL_CAPS_BY_TIER.items()
    }


# =============================================================================
# Helper Functions
# =============================================================================

def _session_to_response(session) -> RentalSessionResponse:
    """Convert RentalSession to response model."""
    return RentalSessionResponse(
        session_id=session.session_id,
        tenant_id=session.tenant_id,
        user_id=session.user_id,
        mechanism_type=session.mechanism_type.value,
        rental_subtype=session.rental_subtype,
        status=session.status.value,
        created_at=session.created_at.isoformat(),
        activated_at=session.activated_at.isoformat() if session.activated_at else None,
        expires_at=session.expires_at.isoformat() if session.expires_at else None,
        total_units=session.total_units,
        used_units=session.used_units,
        amount_paid=float(session.amount_paid),
        model_ids=session.model_ids,
        is_active=session.is_active,
        time_remaining_seconds=session.time_remaining_seconds,
        usage_percentage=session.usage_percentage,
    )


def _offer_to_response(offer) -> RentalOfferResponse:
    """Convert RentalOffer to response model."""
    return RentalOfferResponse(
        offer_id=offer.offer_id,
        mechanism_type=offer.mechanism_type.value,
        rental_subtype=offer.rental_subtype,
        original_price=float(offer.original_price),
        offer_price=float(offer.offer_price),
        discount_percent=offer.discount_percent,
        headline=offer.headline,
        value_proposition=offer.value_proposition,
        urgency_message=offer.urgency_message,
        cta_text=offer.cta_text,
        expires_at=offer.expires_at.isoformat() if offer.expires_at else "",
    )
