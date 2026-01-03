"""
KRL Fraud + Abuse Layer - DEPRECATED
=====================================

⚠️ DEPRECATION WARNING (Dec 2025):
This module has been moved to krl-premium-backend.
Import from: app.services.billing.fraud_detection

This stub remains for backward compatibility but will be removed in v2.0.

Stripe Radar integration with internal risk mesh for fraud detection
and abuse prevention across the billing system.
"""

from __future__ import annotations

import warnings
warnings.warn(
    "krl_data_connectors.core.billing.fraud_detection is deprecated. "
    "This module has moved to krl-premium-backend. "
    "Import from 'app.services.billing.fraud_detection' instead.",
    DeprecationWarning,
    stacklevel=2
)

import hashlib
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone, UTC
from decimal import Decimal
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from uuid import uuid4

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================

class RiskLevel(str, Enum):
    """Risk assessment levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FraudSignalType(str, Enum):
    """Types of fraud signals."""
    STRIPE_RADAR = "stripe_radar"
    VELOCITY_ANOMALY = "velocity_anomaly"
    DEVICE_FINGERPRINT = "device_fingerprint"
    GEO_ANOMALY = "geo_anomaly"
    PAYMENT_PATTERN = "payment_pattern"
    USAGE_ABUSE = "usage_abuse"
    IDENTITY_MISMATCH = "identity_mismatch"
    CHARGEBACK_HISTORY = "chargeback_history"


class AbuseType(str, Enum):
    """Types of abuse patterns."""
    API_ABUSE = "api_abuse"
    TRIAL_ABUSE = "trial_abuse"
    REFERRAL_FRAUD = "referral_fraud"
    MULTI_ACCOUNT = "multi_account"
    RESOURCE_EXPLOITATION = "resource_exploitation"
    CREDENTIAL_STUFFING = "credential_stuffing"
    SCRAPING = "scraping"


class EnforcementAction(str, Enum):
    """Actions to take on detected fraud/abuse."""
    ALLOW = "allow"
    CHALLENGE = "challenge"  # 3DS, CAPTCHA
    THROTTLE = "throttle"
    BLOCK = "block"
    FLAG_REVIEW = "flag_review"
    SUSPEND = "suspend"
    TERMINATE = "terminate"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class FraudSignal:
    """Individual fraud signal."""
    signal_id: str
    signal_type: FraudSignalType
    source: str
    risk_score: float  # 0-100
    confidence: float  # 0-1
    details: Dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RiskAssessment:
    """Complete risk assessment for an entity."""
    assessment_id: str
    entity_id: str
    entity_type: str  # customer, payment, subscription
    
    # Scores
    overall_risk: RiskLevel
    risk_score: float  # 0-100
    
    # Component scores
    stripe_radar_score: Optional[float] = None
    internal_risk_score: float = 0.0
    abuse_score: float = 0.0
    
    # Signals
    signals: List[FraudSignal] = field(default_factory=list)
    
    # Decision
    recommended_action: EnforcementAction = EnforcementAction.ALLOW
    action_reason: str = ""
    requires_review: bool = False
    
    assessed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AbusePattern:
    """Detected abuse pattern."""
    pattern_id: str
    abuse_type: AbuseType
    entity_id: str
    severity: RiskLevel
    evidence: List[str]
    first_detected: datetime
    last_seen: datetime
    occurrence_count: int = 1


@dataclass
class VelocityRule:
    """Velocity check rule."""
    rule_id: str
    name: str
    metric: str  # e.g., "payments", "api_calls", "signup_attempts"
    window_seconds: int
    threshold: int
    action: EnforcementAction
    scope: str = "customer"  # customer, ip, device


@dataclass
class RiskConfig:
    """Risk assessment configuration."""
    # Thresholds
    low_risk_max: float = 25.0
    medium_risk_max: float = 50.0
    high_risk_max: float = 75.0
    
    # Weights
    stripe_radar_weight: float = 0.4
    internal_signals_weight: float = 0.35
    abuse_signals_weight: float = 0.25
    
    # Auto-actions
    auto_block_threshold: float = 90.0
    auto_challenge_threshold: float = 60.0
    review_threshold: float = 50.0


DEFAULT_RISK_CONFIG = RiskConfig()


# =============================================================================
# Stripe Radar Integration
# =============================================================================

class StripeRadarIntegration:
    """
    Integrates with Stripe Radar for payment risk scoring.
    
    Retrieves:
    - Risk score (0-100)
    - Risk level (elevated, highest, etc.)
    - Rule matches
    - Fraud insights
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key
        self._cache: Dict[str, Tuple[float, datetime]] = {}
        self._cache_ttl = timedelta(minutes=5)
    
    async def get_payment_risk(
        self,
        payment_intent_id: str,
    ) -> Optional[FraudSignal]:
        """Get Stripe Radar risk assessment for payment."""
        # Check cache
        if payment_intent_id in self._cache:
            score, cached_at = self._cache[payment_intent_id]
            if datetime.now(timezone.utc) - cached_at < self._cache_ttl:
                return FraudSignal(
                    signal_id=uuid4().hex,
                    signal_type=FraudSignalType.STRIPE_RADAR,
                    source="stripe_radar",
                    risk_score=score,
                    confidence=0.9,
                    details={"payment_intent_id": payment_intent_id, "cached": True},
                )
        
        try:
            # In production: stripe.PaymentIntent.retrieve(payment_intent_id)
            # Mock response for now
            radar_data = await self._fetch_radar_data(payment_intent_id)
            
            risk_score = radar_data.get("risk_score", 0)
            
            # Cache result
            self._cache[payment_intent_id] = (risk_score, datetime.now(timezone.utc))
            
            return FraudSignal(
                signal_id=uuid4().hex,
                signal_type=FraudSignalType.STRIPE_RADAR,
                source="stripe_radar",
                risk_score=risk_score,
                confidence=0.9,
                details={
                    "payment_intent_id": payment_intent_id,
                    "risk_level": radar_data.get("risk_level"),
                    "rule_matches": radar_data.get("rule_matches", []),
                },
            )
            
        except Exception as e:
            logger.error(f"Stripe Radar fetch failed: {e}")
            return None
    
    async def _fetch_radar_data(self, payment_intent_id: str) -> Dict[str, Any]:
        """Fetch Radar data from Stripe (mock for development)."""
        # Would call Stripe API in production
        return {
            "risk_score": 15,  # Low risk
            "risk_level": "normal",
            "rule_matches": [],
        }
    
    def get_customer_risk_history(
        self,
        customer_id: str,
    ) -> List[Dict[str, Any]]:
        """Get historical risk data for customer."""
        # Would query Stripe for historical payment risks
        return []


# =============================================================================
# Velocity Tracker
# =============================================================================

class VelocityTracker:
    """
    Tracks event velocities for anomaly detection.
    
    Monitors:
    - Payment attempts per time window
    - API call rates
    - Signup attempts from IP/device
    - Resource consumption spikes
    """
    
    def __init__(self):
        # Sliding window counters: {scope_key: [(timestamp, count), ...]}
        self._counters: Dict[str, List[Tuple[datetime, int]]] = defaultdict(list)
        self._rules: Dict[str, VelocityRule] = {}
    
    def add_rule(self, rule: VelocityRule) -> None:
        """Add velocity rule."""
        self._rules[rule.rule_id] = rule
    
    def record_event(
        self,
        metric: str,
        scope_value: str,
        count: int = 1,
    ) -> None:
        """Record an event for velocity tracking."""
        key = f"{metric}:{scope_value}"
        now = datetime.now(timezone.utc)
        self._counters[key].append((now, count))
        
        # Cleanup old entries (keep last hour)
        cutoff = now - timedelta(hours=1)
        self._counters[key] = [
            (ts, c) for ts, c in self._counters[key]
            if ts > cutoff
        ]
    
    def check_velocity(
        self,
        metric: str,
        scope_value: str,
    ) -> List[FraudSignal]:
        """Check if velocity exceeds any rules."""
        signals = []
        key = f"{metric}:{scope_value}"
        
        for rule in self._rules.values():
            if rule.metric != metric:
                continue
            
            # Count events in window
            now = datetime.now(timezone.utc)
            window_start = now - timedelta(seconds=rule.window_seconds)
            
            count = sum(
                c for ts, c in self._counters.get(key, [])
                if ts > window_start
            )
            
            if count > rule.threshold:
                risk_score = min(100, (count / rule.threshold) * 50 + 25)
                
                signals.append(FraudSignal(
                    signal_id=uuid4().hex,
                    signal_type=FraudSignalType.VELOCITY_ANOMALY,
                    source="velocity_tracker",
                    risk_score=risk_score,
                    confidence=0.85,
                    details={
                        "rule_id": rule.rule_id,
                        "rule_name": rule.name,
                        "metric": metric,
                        "count": count,
                        "threshold": rule.threshold,
                        "window_seconds": rule.window_seconds,
                        "recommended_action": rule.action.value,
                    },
                ))
        
        return signals
    
    def get_velocity_stats(
        self,
        metric: str,
        scope_value: str,
        window_seconds: int,
    ) -> Dict[str, Any]:
        """Get velocity statistics for metric."""
        key = f"{metric}:{scope_value}"
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(seconds=window_seconds)
        
        events = [
            (ts, c) for ts, c in self._counters.get(key, [])
            if ts > window_start
        ]
        
        return {
            "metric": metric,
            "scope": scope_value,
            "window_seconds": window_seconds,
            "event_count": len(events),
            "total_count": sum(c for _, c in events),
        }


# =============================================================================
# Abuse Pattern Detector
# =============================================================================

class AbusePatternDetector:
    """
    Detects abuse patterns across customer behavior.
    
    Patterns:
    - Trial abuse (repeated trials)
    - Multi-account fraud
    - API abuse patterns
    - Resource exploitation
    """
    
    def __init__(self):
        self._patterns: Dict[str, AbusePattern] = {}
        self._fingerprints: Dict[str, Set[str]] = defaultdict(set)  # fingerprint -> entity_ids
    
    def detect_trial_abuse(
        self,
        customer_id: str,
        email: str,
        device_fingerprint: Optional[str],
        ip_address: Optional[str],
    ) -> Optional[AbusePattern]:
        """Detect trial abuse patterns."""
        evidence = []
        severity = RiskLevel.LOW
        
        # Check email domain patterns
        email_domain = email.split("@")[-1] if "@" in email else ""
        disposable_domains = {"tempmail.com", "guerrillamail.com", "10minutemail.com"}
        
        if email_domain in disposable_domains:
            evidence.append(f"Disposable email domain: {email_domain}")
            severity = RiskLevel.MEDIUM
        
        # Check device fingerprint reuse
        if device_fingerprint:
            self._fingerprints[device_fingerprint].add(customer_id)
            if len(self._fingerprints[device_fingerprint]) > 1:
                evidence.append(f"Device fingerprint seen with {len(self._fingerprints[device_fingerprint])} accounts")
                severity = RiskLevel.HIGH
        
        # Check IP reuse
        if ip_address:
            self._fingerprints[f"ip:{ip_address}"].add(customer_id)
            if len(self._fingerprints[f"ip:{ip_address}"]) > 3:
                evidence.append(f"IP address linked to {len(self._fingerprints[f'ip:{ip_address}'])} accounts")
                severity = RiskLevel.HIGH
        
        if not evidence:
            return None
        
        pattern_key = f"trial_abuse:{customer_id}"
        now = datetime.now(timezone.utc)
        
        if pattern_key in self._patterns:
            pattern = self._patterns[pattern_key]
            pattern.evidence.extend(evidence)
            pattern.last_seen = now
            pattern.occurrence_count += 1
            pattern.severity = severity
        else:
            pattern = AbusePattern(
                pattern_id=uuid4().hex,
                abuse_type=AbuseType.TRIAL_ABUSE,
                entity_id=customer_id,
                severity=severity,
                evidence=evidence,
                first_detected=now,
                last_seen=now,
            )
            self._patterns[pattern_key] = pattern
        
        return pattern
    
    def detect_api_abuse(
        self,
        customer_id: str,
        endpoint: str,
        request_count: int,
        error_rate: float,
    ) -> Optional[AbusePattern]:
        """Detect API abuse patterns."""
        evidence = []
        severity = RiskLevel.LOW
        
        # High error rate indicates potential scraping/fuzzing
        if error_rate > 0.5:
            evidence.append(f"High error rate: {error_rate:.1%}")
            severity = RiskLevel.MEDIUM
        
        # Unusual request patterns
        if request_count > 10000:  # Per hour threshold
            evidence.append(f"Unusually high request count: {request_count}")
            severity = RiskLevel.HIGH
        
        if not evidence:
            return None
        
        return AbusePattern(
            pattern_id=uuid4().hex,
            abuse_type=AbuseType.API_ABUSE,
            entity_id=customer_id,
            severity=severity,
            evidence=evidence,
            first_detected=datetime.now(timezone.utc),
            last_seen=datetime.now(timezone.utc),
        )
    
    def get_abuse_score(self, customer_id: str) -> float:
        """Calculate abuse score for customer."""
        patterns = [
            p for p in self._patterns.values()
            if p.entity_id == customer_id
        ]
        
        if not patterns:
            return 0.0
        
        severity_scores = {
            RiskLevel.LOW: 15,
            RiskLevel.MEDIUM: 35,
            RiskLevel.HIGH: 65,
            RiskLevel.CRITICAL: 90,
        }
        
        max_score = max(severity_scores[p.severity] for p in patterns)
        occurrence_bonus = min(20, sum(p.occurrence_count for p in patterns) * 2)
        
        return min(100, max_score + occurrence_bonus)


# =============================================================================
# Risk Mesh (Signal Aggregator)
# =============================================================================

class RiskMesh:
    """
    Aggregates signals from multiple sources into unified risk assessment.
    
    Sources:
    - Stripe Radar
    - Velocity tracker
    - Abuse detector
    - External risk feeds
    - Internal ML models
    """
    
    def __init__(self, config: RiskConfig = DEFAULT_RISK_CONFIG):
        self.config = config
        self.stripe_radar = StripeRadarIntegration()
        self.velocity_tracker = VelocityTracker()
        self.abuse_detector = AbusePatternDetector()
        
        # Signal processors
        self._processors: List[Callable[[str, str], List[FraudSignal]]] = []
    
    def register_signal_processor(
        self,
        processor: Callable[[str, str], List[FraudSignal]],
    ) -> None:
        """Register custom signal processor."""
        self._processors.append(processor)
    
    async def assess_risk(
        self,
        entity_id: str,
        entity_type: str,
        context: Dict[str, Any],
    ) -> RiskAssessment:
        """Perform comprehensive risk assessment."""
        signals: List[FraudSignal] = []
        
        # Collect Stripe Radar signal
        if entity_type == "payment" and "payment_intent_id" in context:
            radar_signal = await self.stripe_radar.get_payment_risk(
                context["payment_intent_id"]
            )
            if radar_signal:
                signals.append(radar_signal)
        
        # Check velocity rules
        if "customer_id" in context:
            velocity_signals = self.velocity_tracker.check_velocity(
                metric=entity_type,
                scope_value=context["customer_id"],
            )
            signals.extend(velocity_signals)
        
        # Run custom processors
        for processor in self._processors:
            try:
                custom_signals = processor(entity_id, entity_type)
                signals.extend(custom_signals)
            except Exception as e:
                logger.error(f"Signal processor error: {e}")
        
        # Calculate component scores
        stripe_score = self._extract_stripe_score(signals)
        internal_score = self._calculate_internal_score(signals)
        abuse_score = self.abuse_detector.get_abuse_score(
            context.get("customer_id", entity_id)
        )
        
        # Weighted overall score
        overall_score = (
            (stripe_score or 0) * self.config.stripe_radar_weight
            + internal_score * self.config.internal_signals_weight
            + abuse_score * self.config.abuse_signals_weight
        )
        
        # Normalize if no Stripe score
        if stripe_score is None:
            overall_score = overall_score / (1 - self.config.stripe_radar_weight)
        
        # Determine risk level
        risk_level = self._score_to_level(overall_score)
        
        # Determine action
        action, reason = self._determine_action(overall_score, signals)
        
        return RiskAssessment(
            assessment_id=uuid4().hex,
            entity_id=entity_id,
            entity_type=entity_type,
            overall_risk=risk_level,
            risk_score=round(overall_score, 2),
            stripe_radar_score=stripe_score,
            internal_risk_score=round(internal_score, 2),
            abuse_score=round(abuse_score, 2),
            signals=signals,
            recommended_action=action,
            action_reason=reason,
            requires_review=overall_score >= self.config.review_threshold,
        )
    
    def _extract_stripe_score(self, signals: List[FraudSignal]) -> Optional[float]:
        """Extract Stripe Radar score from signals."""
        for signal in signals:
            if signal.signal_type == FraudSignalType.STRIPE_RADAR:
                return signal.risk_score
        return None
    
    def _calculate_internal_score(self, signals: List[FraudSignal]) -> float:
        """Calculate internal risk score from signals."""
        internal_signals = [
            s for s in signals
            if s.signal_type != FraudSignalType.STRIPE_RADAR
        ]
        
        if not internal_signals:
            return 0.0
        
        # Weighted average by confidence
        total_weight = sum(s.confidence for s in internal_signals)
        if total_weight == 0:
            return 0.0
        
        weighted_sum = sum(s.risk_score * s.confidence for s in internal_signals)
        return weighted_sum / total_weight
    
    def _score_to_level(self, score: float) -> RiskLevel:
        """Convert numeric score to risk level."""
        if score <= self.config.low_risk_max:
            return RiskLevel.LOW
        elif score <= self.config.medium_risk_max:
            return RiskLevel.MEDIUM
        elif score <= self.config.high_risk_max:
            return RiskLevel.HIGH
        return RiskLevel.CRITICAL
    
    def _determine_action(
        self,
        score: float,
        signals: List[FraudSignal],
    ) -> Tuple[EnforcementAction, str]:
        """Determine enforcement action based on assessment."""
        if score >= self.config.auto_block_threshold:
            return EnforcementAction.BLOCK, f"Risk score {score:.1f} exceeds block threshold"
        
        if score >= self.config.auto_challenge_threshold:
            return EnforcementAction.CHALLENGE, f"Risk score {score:.1f} requires verification"
        
        # Check for specific high-risk signals
        for signal in signals:
            if signal.signal_type == FraudSignalType.CHARGEBACK_HISTORY:
                return EnforcementAction.FLAG_REVIEW, "Chargeback history detected"
        
        if score >= self.config.review_threshold:
            return EnforcementAction.FLAG_REVIEW, f"Risk score {score:.1f} requires manual review"
        
        return EnforcementAction.ALLOW, "Risk within acceptable limits"


# =============================================================================
# Fraud Detection Engine
# =============================================================================

class FraudDetectionEngine:
    """
    Main fraud detection engine coordinating all components.
    
    Provides:
    - Real-time transaction screening
    - Customer risk profiling
    - Abuse detection
    - Enforcement actions
    """
    
    def __init__(self, config: RiskConfig = DEFAULT_RISK_CONFIG):
        self.config = config
        self.risk_mesh = RiskMesh(config)
        
        # Event handlers
        self._on_high_risk: List[Callable[[RiskAssessment], None]] = []
        self._on_block: List[Callable[[RiskAssessment], None]] = []
        
        # Initialize default velocity rules
        self._setup_default_rules()
    
    def _setup_default_rules(self) -> None:
        """Setup default velocity rules."""
        default_rules = [
            VelocityRule(
                rule_id="payment_velocity",
                name="Payment Velocity",
                metric="payment",
                window_seconds=3600,  # 1 hour
                threshold=10,
                action=EnforcementAction.CHALLENGE,
            ),
            VelocityRule(
                rule_id="failed_payment_velocity",
                name="Failed Payment Velocity",
                metric="failed_payment",
                window_seconds=900,  # 15 minutes
                threshold=3,
                action=EnforcementAction.BLOCK,
            ),
            VelocityRule(
                rule_id="signup_velocity",
                name="Signup Velocity (IP)",
                metric="signup",
                window_seconds=86400,  # 24 hours
                threshold=5,
                action=EnforcementAction.FLAG_REVIEW,
                scope="ip",
            ),
        ]
        
        for rule in default_rules:
            self.risk_mesh.velocity_tracker.add_rule(rule)
    
    def on_high_risk(self, handler: Callable[[RiskAssessment], None]) -> None:
        """Register handler for high-risk assessments."""
        self._on_high_risk.append(handler)
    
    def on_block(self, handler: Callable[[RiskAssessment], None]) -> None:
        """Register handler for block actions."""
        self._on_block.append(handler)
    
    async def screen_payment(
        self,
        payment_intent_id: str,
        customer_id: str,
        amount: Decimal,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RiskAssessment:
        """Screen payment for fraud."""
        # Record velocity event
        self.risk_mesh.velocity_tracker.record_event("payment", customer_id)
        
        context = {
            "payment_intent_id": payment_intent_id,
            "customer_id": customer_id,
            "amount": str(amount),
            **(metadata or {}),
        }
        
        assessment = await self.risk_mesh.assess_risk(
            entity_id=payment_intent_id,
            entity_type="payment",
            context=context,
        )
        
        # Trigger handlers
        if assessment.overall_risk in (RiskLevel.HIGH, RiskLevel.CRITICAL):
            for handler in self._on_high_risk:
                try:
                    handler(assessment)
                except Exception as e:
                    logger.error(f"High risk handler error: {e}")
        
        if assessment.recommended_action == EnforcementAction.BLOCK:
            for handler in self._on_block:
                try:
                    handler(assessment)
                except Exception as e:
                    logger.error(f"Block handler error: {e}")
        
        return assessment
    
    async def screen_signup(
        self,
        customer_id: str,
        email: str,
        ip_address: Optional[str] = None,
        device_fingerprint: Optional[str] = None,
    ) -> RiskAssessment:
        """Screen new signup for abuse."""
        # Record velocity
        if ip_address:
            self.risk_mesh.velocity_tracker.record_event("signup", ip_address)
        
        # Check trial abuse
        self.risk_mesh.abuse_detector.detect_trial_abuse(
            customer_id=customer_id,
            email=email,
            device_fingerprint=device_fingerprint,
            ip_address=ip_address,
        )
        
        context = {
            "customer_id": customer_id,
            "email": email,
            "ip_address": ip_address,
            "device_fingerprint": device_fingerprint,
        }
        
        return await self.risk_mesh.assess_risk(
            entity_id=customer_id,
            entity_type="signup",
            context=context,
        )
    
    def record_failed_payment(self, customer_id: str) -> None:
        """Record failed payment for velocity tracking."""
        self.risk_mesh.velocity_tracker.record_event("failed_payment", customer_id)
    
    def get_customer_risk_profile(self, customer_id: str) -> Dict[str, Any]:
        """Get risk profile for customer."""
        abuse_score = self.risk_mesh.abuse_detector.get_abuse_score(customer_id)
        velocity_stats = self.risk_mesh.velocity_tracker.get_velocity_stats(
            metric="payment",
            scope_value=customer_id,
            window_seconds=86400,
        )
        
        return {
            "customer_id": customer_id,
            "abuse_score": abuse_score,
            "payment_velocity_24h": velocity_stats,
            "assessed_at": datetime.now(timezone.utc).isoformat(),
        }


# =============================================================================
# Factory Function
# =============================================================================

def create_fraud_detection_engine(
    config: Optional[RiskConfig] = None,
) -> FraudDetectionEngine:
    """Create configured FraudDetectionEngine."""
    return FraudDetectionEngine(config=config or DEFAULT_RISK_CONFIG)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Enums
    "RiskLevel",
    "FraudSignalType",
    "AbuseType",
    "EnforcementAction",
    # Data Classes
    "FraudSignal",
    "RiskAssessment",
    "AbusePattern",
    "VelocityRule",
    "RiskConfig",
    "DEFAULT_RISK_CONFIG",
    # Classes
    "StripeRadarIntegration",
    "VelocityTracker",
    "AbusePatternDetector",
    "RiskMesh",
    "FraudDetectionEngine",
    # Factory
    "create_fraud_detection_engine",
]
