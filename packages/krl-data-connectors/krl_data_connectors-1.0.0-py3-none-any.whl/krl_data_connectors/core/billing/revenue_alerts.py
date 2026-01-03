# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
#
# ⚠️ DEPRECATION WARNING (Dec 2025):
# This module has been moved to krl-premium-backend.
# Import from: app.services.billing.revenue_alerts
# This stub remains for backward compatibility but will be removed in v2.0.
# ----------------------------------------------------------------------

from __future__ import annotations
import warnings as _warnings
_warnings.warn(
    "krl_data_connectors.core.billing.revenue_alerts is deprecated. "
    "Import from 'app.services.billing.revenue_alerts' instead.",
    DeprecationWarning,
    stacklevel=2
)

"""
Revenue Alerts System - Phase 3 Week 22

Real-time revenue anomaly detection and alerting:
- MRR/ARR anomaly detection
- Churn risk notifications
- Expansion opportunity alerts
- Billing failure warnings
- Revenue milestone tracking

Alert Channels:
- Dashboard (real-time)
- Webhook (external systems)
- Email digest (daily/weekly)

Integrates with all four loops:
- Observability: Metrics and telemetry
- Defense: Security-related revenue impact
- Governance: Policy violation billing
- Monetization: Usage and pricing alerts

This module provides real-time visibility into revenue health.
"""


import asyncio
import logging
import math
import statistics
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from decimal import Decimal
from enum import Enum
from typing import Any, Callable, Deque, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================

class AlertSeverity(Enum):
    """Alert severity levels."""
    CRITICAL = "critical"   # Immediate action required
    HIGH = "high"           # Action needed within hours
    MEDIUM = "medium"       # Review within 24 hours
    LOW = "low"             # Informational
    INFO = "info"           # FYI only


class AlertCategory(Enum):
    """Categories of revenue alerts."""
    REVENUE_ANOMALY = "revenue_anomaly"
    CHURN_RISK = "churn_risk"
    EXPANSION_OPPORTUNITY = "expansion"
    BILLING_FAILURE = "billing_failure"
    PAYMENT_ISSUE = "payment_issue"
    USAGE_SPIKE = "usage_spike"
    USAGE_DROP = "usage_drop"
    MILESTONE = "milestone"
    FORECAST_DEVIATION = "forecast_deviation"
    POLICY_VIOLATION = "policy_violation"


class AlertStatus(Enum):
    """Status of an alert."""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SNOOZED = "snoozed"
    ESCALATED = "escalated"


class AlertChannel(Enum):
    """Delivery channels for alerts."""
    DASHBOARD = "dashboard"
    WEBHOOK = "webhook"
    EMAIL = "email"
    SLACK = "slack"
    PAGERDUTY = "pagerduty"


class AnomalyType(Enum):
    """Types of revenue anomalies."""
    SUDDEN_DROP = "sudden_drop"
    GRADUAL_DECLINE = "gradual_decline"
    UNEXPECTED_SPIKE = "spike"
    DEVIATION_FROM_FORECAST = "forecast_deviation"
    SEASONAL_ANOMALY = "seasonal"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class Alert:
    """A revenue alert."""
    alert_id: str
    category: AlertCategory
    severity: AlertSeverity
    title: str
    description: str
    
    # Context
    tenant_id: Optional[str] = None
    tier: Optional[str] = None
    metric_name: Optional[str] = None
    metric_value: Optional[float] = None
    threshold_value: Optional[float] = None
    
    # Financial impact
    revenue_impact: Optional[Decimal] = None
    projected_loss: Optional[Decimal] = None
    
    # Status
    status: AlertStatus = AlertStatus.ACTIVE
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: Optional[datetime] = None
    
    # Metadata
    source: str = "revenue_alerts"
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def acknowledge(self, user: str) -> None:
        """Acknowledge the alert."""
        self.status = AlertStatus.ACKNOWLEDGED
        self.acknowledged_by = user
        self.acknowledged_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)

    def resolve(self, resolution_note: Optional[str] = None) -> None:
        """Resolve the alert."""
        self.status = AlertStatus.RESOLVED
        self.resolved_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)
        if resolution_note:
            self.metadata["resolution_note"] = resolution_note

    def snooze(self, until: datetime) -> None:
        """Snooze the alert until a specific time."""
        self.status = AlertStatus.SNOOZED
        self.metadata["snoozed_until"] = until.isoformat()
        self.updated_at = datetime.now(UTC)

    def escalate(self) -> None:
        """Escalate the alert."""
        self.status = AlertStatus.ESCALATED
        self.severity = AlertSeverity.CRITICAL
        self.updated_at = datetime.now(UTC)

    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary."""
        return {
            "alert_id": self.alert_id,
            "category": self.category.value,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "tenant_id": self.tenant_id,
            "tier": self.tier,
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
            "threshold_value": self.threshold_value,
            "revenue_impact": float(self.revenue_impact) if self.revenue_impact else None,
            "projected_loss": float(self.projected_loss) if self.projected_loss else None,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "tags": self.tags,
        }


@dataclass
class AlertRule:
    """A rule for generating alerts."""
    rule_id: str
    name: str
    category: AlertCategory
    
    # Conditions
    metric_name: str
    condition: str  # "above", "below", "change_pct"
    threshold: float
    
    # Alert details
    severity: AlertSeverity = AlertSeverity.MEDIUM
    title_template: str = "Alert: {metric_name}"
    description_template: str = "{metric_name} {condition} threshold"
    
    # Scope
    tiers: List[str] = field(default_factory=lambda: ["community", "pro", "enterprise"])
    
    # Behavior
    cooldown_minutes: int = 60
    auto_resolve_minutes: Optional[int] = None
    escalate_after_minutes: Optional[int] = None
    
    # Status
    enabled: bool = True
    
    # Timestamps
    last_triggered: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def can_trigger(self) -> bool:
        """Check if rule can trigger based on cooldown."""
        if not self.enabled:
            return False
        if self.last_triggered is None:
            return True
        
        elapsed = (datetime.now(UTC) - self.last_triggered).total_seconds() / 60
        return elapsed >= self.cooldown_minutes


@dataclass
class AlertSubscription:
    """A subscription for alert delivery."""
    subscription_id: str
    channel: AlertChannel
    
    # Targeting
    categories: List[AlertCategory] = field(default_factory=list)
    min_severity: AlertSeverity = AlertSeverity.MEDIUM
    tiers: List[str] = field(default_factory=list)
    
    # Delivery config
    endpoint: Optional[str] = None  # webhook URL, email, etc.
    headers: Dict[str, str] = field(default_factory=dict)
    
    # Batching
    batch_enabled: bool = False
    batch_interval_minutes: int = 60
    
    # Status
    enabled: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class MetricSnapshot:
    """A snapshot of a metric value."""
    metric_name: str
    value: float
    timestamp: datetime
    tenant_id: Optional[str] = None
    tier: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RevenueHealthStatus:
    """Overall revenue health status."""
    health_score: float  # 0-100
    status: str  # "healthy", "warning", "critical"
    
    # Component scores
    mrr_health: float
    churn_health: float
    growth_health: float
    billing_health: float
    
    # Active alerts summary
    critical_alerts: int
    high_alerts: int
    total_alerts: int
    
    # Key metrics
    mrr: Decimal
    mrr_trend: float  # % change
    churn_rate: float
    expansion_rate: float
    
    # Timestamp
    calculated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# Anomaly Detector
# =============================================================================

class AnomalyDetector:
    """
    Detects anomalies in revenue metrics.
    
    Uses multiple detection methods:
    - Z-score (statistical)
    - Moving average deviation
    - Seasonal decomposition
    - Forecast comparison
    """

    def __init__(self, window_size: int = 30):
        self.window_size = window_size
        self._history: Dict[str, Deque[MetricSnapshot]] = {}
        self._thresholds: Dict[str, Dict[str, float]] = {}

    def set_threshold(
        self, 
        metric_name: str, 
        z_threshold: float = 2.5,
        pct_threshold: float = 20.0
    ) -> None:
        """Set detection thresholds for a metric."""
        self._thresholds[metric_name] = {
            "z_score": z_threshold,
            "pct_change": pct_threshold,
        }

    def record_metric(self, snapshot: MetricSnapshot) -> None:
        """Record a metric snapshot."""
        key = f"{snapshot.metric_name}:{snapshot.tenant_id or 'global'}"
        
        if key not in self._history:
            self._history[key] = deque(maxlen=self.window_size * 3)
        
        self._history[key].append(snapshot)

    def detect_anomaly(
        self, 
        metric_name: str,
        current_value: float,
        tenant_id: Optional[str] = None
    ) -> Optional[Tuple[AnomalyType, float, str]]:
        """
        Detect if current value is anomalous.
        
        Returns (anomaly_type, deviation, description) or None.
        """
        key = f"{metric_name}:{tenant_id or 'global'}"
        
        if key not in self._history or len(self._history[key]) < 5:
            return None
        
        history = list(self._history[key])
        values = [s.value for s in history]
        
        # Get thresholds
        thresholds = self._thresholds.get(metric_name, {
            "z_score": 2.5,
            "pct_change": 20.0,
        })
        
        # Z-score detection
        z_score = self._calculate_z_score(values, current_value)
        if abs(z_score) > thresholds["z_score"]:
            if z_score < 0:
                return (
                    AnomalyType.SUDDEN_DROP,
                    z_score,
                    f"{metric_name} dropped significantly (z={z_score:.2f})"
                )
            else:
                return (
                    AnomalyType.UNEXPECTED_SPIKE,
                    z_score,
                    f"{metric_name} spiked unexpectedly (z={z_score:.2f})"
                )
        
        # Percentage change detection
        recent_avg = statistics.mean(values[-5:]) if len(values) >= 5 else values[-1]
        if recent_avg != 0:
            pct_change = ((current_value - recent_avg) / recent_avg) * 100
            
            if abs(pct_change) > thresholds["pct_change"]:
                if pct_change < 0:
                    return (
                        AnomalyType.GRADUAL_DECLINE,
                        pct_change,
                        f"{metric_name} declined by {abs(pct_change):.1f}%"
                    )
        
        return None

    def _calculate_z_score(self, values: List[float], current: float) -> float:
        """Calculate z-score for current value."""
        if len(values) < 2:
            return 0.0
        
        mean = statistics.mean(values)
        stdev = statistics.stdev(values)
        
        if stdev == 0:
            return 0.0
        
        return (current - mean) / stdev

    def detect_trend_anomaly(
        self,
        metric_name: str,
        tenant_id: Optional[str] = None
    ) -> Optional[Tuple[AnomalyType, float, str]]:
        """Detect trend-based anomalies (gradual changes)."""
        key = f"{metric_name}:{tenant_id or 'global'}"
        
        if key not in self._history or len(self._history[key]) < 14:
            return None
        
        history = list(self._history[key])
        values = [s.value for s in history]
        
        # Compare last 7 days to previous 7 days
        recent = values[-7:]
        previous = values[-14:-7]
        
        recent_avg = statistics.mean(recent)
        previous_avg = statistics.mean(previous)
        
        if previous_avg == 0:
            return None
        
        trend_change = ((recent_avg - previous_avg) / previous_avg) * 100
        
        if trend_change < -15:
            return (
                AnomalyType.GRADUAL_DECLINE,
                trend_change,
                f"{metric_name} showing declining trend ({trend_change:.1f}% over 7 days)"
            )
        
        return None


# =============================================================================
# Alert Manager
# =============================================================================

class AlertManager:
    """
    Manages alert lifecycle and delivery.
    
    Handles:
    - Alert creation and deduplication
    - Rule evaluation
    - Alert delivery to channels
    - Alert status management
    """

    def __init__(self):
        self._alerts: Dict[str, Alert] = {}
        self._rules: Dict[str, AlertRule] = {}
        self._subscriptions: Dict[str, AlertSubscription] = {}
        self._alert_counter: int = 0
        
        # Deduplication
        self._recent_alert_keys: Deque[str] = deque(maxlen=1000)
        
        # Delivery callbacks
        self._delivery_handlers: Dict[AlertChannel, Callable[[Alert], None]] = {}

    # -------------------------------------------------------------------------
    # Rule Management
    # -------------------------------------------------------------------------

    def add_rule(self, rule: AlertRule) -> None:
        """Add an alert rule."""
        self._rules[rule.rule_id] = rule
        logger.info(f"Added alert rule: {rule.rule_id}")

    def remove_rule(self, rule_id: str) -> None:
        """Remove an alert rule."""
        if rule_id in self._rules:
            del self._rules[rule_id]
            logger.info(f"Removed alert rule: {rule_id}")

    def get_rules(self) -> List[AlertRule]:
        """Get all alert rules."""
        return list(self._rules.values())

    def enable_rule(self, rule_id: str) -> None:
        """Enable an alert rule."""
        if rule_id in self._rules:
            self._rules[rule_id].enabled = True

    def disable_rule(self, rule_id: str) -> None:
        """Disable an alert rule."""
        if rule_id in self._rules:
            self._rules[rule_id].enabled = False

    # -------------------------------------------------------------------------
    # Subscription Management
    # -------------------------------------------------------------------------

    def add_subscription(self, subscription: AlertSubscription) -> None:
        """Add an alert subscription."""
        self._subscriptions[subscription.subscription_id] = subscription
        logger.info(f"Added subscription: {subscription.subscription_id}")

    def remove_subscription(self, subscription_id: str) -> None:
        """Remove an alert subscription."""
        if subscription_id in self._subscriptions:
            del self._subscriptions[subscription_id]

    def register_delivery_handler(
        self, 
        channel: AlertChannel, 
        handler: Callable[[Alert], None]
    ) -> None:
        """Register a delivery handler for a channel."""
        self._delivery_handlers[channel] = handler
        logger.info(f"Registered delivery handler for {channel.value}")

    # -------------------------------------------------------------------------
    # Alert Creation
    # -------------------------------------------------------------------------

    def create_alert(
        self,
        category: AlertCategory,
        severity: AlertSeverity,
        title: str,
        description: str,
        tenant_id: Optional[str] = None,
        tier: Optional[str] = None,
        metric_name: Optional[str] = None,
        metric_value: Optional[float] = None,
        revenue_impact: Optional[Decimal] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Alert:
        """Create and register a new alert."""
        # Generate ID
        self._alert_counter += 1
        alert_id = f"alert_{datetime.now(UTC).strftime('%Y%m%d')}_{self._alert_counter:06d}"
        
        alert = Alert(
            alert_id=alert_id,
            category=category,
            severity=severity,
            title=title,
            description=description,
            tenant_id=tenant_id,
            tier=tier,
            metric_name=metric_name,
            metric_value=metric_value,
            revenue_impact=revenue_impact,
            tags=tags or [],
            metadata=metadata or {},
        )
        
        # Check for deduplication
        dedup_key = f"{category.value}:{tenant_id}:{metric_name}"
        if dedup_key in self._recent_alert_keys:
            logger.debug(f"Deduplicated alert: {dedup_key}")
            # Return existing similar alert
            for existing_id, existing in self._alerts.items():
                if (existing.category == category and 
                    existing.tenant_id == tenant_id and
                    existing.status == AlertStatus.ACTIVE):
                    return existing
        
        self._alerts[alert_id] = alert
        self._recent_alert_keys.append(dedup_key)
        
        logger.info(f"Created alert {alert_id}: {title}")
        
        # Deliver alert
        self._deliver_alert(alert)
        
        return alert

    def _deliver_alert(self, alert: Alert) -> None:
        """Deliver alert to subscribed channels."""
        for sub_id, subscription in self._subscriptions.items():
            if not subscription.enabled:
                continue
            
            # Check category filter
            if subscription.categories and alert.category not in subscription.categories:
                continue
            
            # Check severity filter
            severity_order = [
                AlertSeverity.INFO,
                AlertSeverity.LOW,
                AlertSeverity.MEDIUM,
                AlertSeverity.HIGH,
                AlertSeverity.CRITICAL,
            ]
            if severity_order.index(alert.severity) < severity_order.index(subscription.min_severity):
                continue
            
            # Check tier filter
            if subscription.tiers and alert.tier not in subscription.tiers:
                continue
            
            # Deliver via handler
            handler = self._delivery_handlers.get(subscription.channel)
            if handler:
                try:
                    handler(alert)
                except Exception as e:
                    logger.error(f"Failed to deliver alert {alert.alert_id}: {e}")
            else:
                logger.debug(f"No handler for channel {subscription.channel.value}")

    # -------------------------------------------------------------------------
    # Alert Management
    # -------------------------------------------------------------------------

    def get_alert(self, alert_id: str) -> Optional[Alert]:
        """Get alert by ID."""
        return self._alerts.get(alert_id)

    def get_active_alerts(
        self,
        category: Optional[AlertCategory] = None,
        severity: Optional[AlertSeverity] = None,
        tenant_id: Optional[str] = None,
    ) -> List[Alert]:
        """Get active alerts with optional filters."""
        alerts = [
            a for a in self._alerts.values()
            if a.status in (AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED)
        ]
        
        if category:
            alerts = [a for a in alerts if a.category == category]
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        if tenant_id:
            alerts = [a for a in alerts if a.tenant_id == tenant_id]
        
        # Sort by severity then timestamp
        severity_order = {
            AlertSeverity.CRITICAL: 0,
            AlertSeverity.HIGH: 1,
            AlertSeverity.MEDIUM: 2,
            AlertSeverity.LOW: 3,
            AlertSeverity.INFO: 4,
        }
        alerts.sort(key=lambda a: (severity_order[a.severity], a.created_at))
        
        return alerts

    def acknowledge_alert(self, alert_id: str, user: str) -> bool:
        """Acknowledge an alert."""
        alert = self._alerts.get(alert_id)
        if alert:
            alert.acknowledge(user)
            return True
        return False

    def resolve_alert(self, alert_id: str, note: Optional[str] = None) -> bool:
        """Resolve an alert."""
        alert = self._alerts.get(alert_id)
        if alert:
            alert.resolve(note)
            return True
        return False

    def snooze_alert(self, alert_id: str, duration_minutes: int) -> bool:
        """Snooze an alert."""
        alert = self._alerts.get(alert_id)
        if alert:
            until = datetime.now(UTC) + timedelta(minutes=duration_minutes)
            alert.snooze(until)
            return True
        return False

    def escalate_alert(self, alert_id: str) -> bool:
        """Escalate an alert."""
        alert = self._alerts.get(alert_id)
        if alert:
            alert.escalate()
            self._deliver_alert(alert)  # Re-deliver with higher severity
            return True
        return False

    # -------------------------------------------------------------------------
    # Rule Evaluation
    # -------------------------------------------------------------------------

    def evaluate_rules(
        self,
        metrics: Dict[str, float],
        tenant_id: Optional[str] = None,
        tier: Optional[str] = None,
    ) -> List[Alert]:
        """Evaluate all rules against current metrics."""
        triggered_alerts = []
        
        for rule_id, rule in self._rules.items():
            if not rule.can_trigger():
                continue
            
            if tier and tier not in rule.tiers:
                continue
            
            metric_value = metrics.get(rule.metric_name)
            if metric_value is None:
                continue
            
            triggered = False
            
            if rule.condition == "above":
                triggered = metric_value > rule.threshold
            elif rule.condition == "below":
                triggered = metric_value < rule.threshold
            elif rule.condition == "equals":
                triggered = metric_value == rule.threshold
            
            if triggered:
                rule.last_triggered = datetime.now(UTC)
                
                title = rule.title_template.format(
                    metric_name=rule.metric_name,
                    value=metric_value,
                    threshold=rule.threshold,
                )
                description = rule.description_template.format(
                    metric_name=rule.metric_name,
                    value=metric_value,
                    threshold=rule.threshold,
                    condition=rule.condition,
                )
                
                alert = self.create_alert(
                    category=rule.category,
                    severity=rule.severity,
                    title=title,
                    description=description,
                    tenant_id=tenant_id,
                    tier=tier,
                    metric_name=rule.metric_name,
                    metric_value=metric_value,
                    metadata={"rule_id": rule_id},
                )
                triggered_alerts.append(alert)
        
        return triggered_alerts


# =============================================================================
# Revenue Alert System
# =============================================================================

class RevenueAlertSystem:
    """
    Comprehensive revenue alerting system.
    
    Integrates:
    - Anomaly detection
    - Alert management
    - Health monitoring
    - Dashboard integration
    """

    def __init__(self):
        self.anomaly_detector = AnomalyDetector()
        self.alert_manager = AlertManager()
        
        # Integration hooks
        self._dashboard_hook: Optional[Callable[[Alert], None]] = None
        self._forecaster_hook: Optional[Callable[[], Any]] = None
        self._cohort_hook: Optional[Callable[[], Any]] = None
        self._billing_hook: Optional[Callable[[], Any]] = None
        
        # Setup default rules
        self._setup_default_rules()

    def _setup_default_rules(self) -> None:
        """Setup default alert rules."""
        default_rules = [
            AlertRule(
                rule_id="mrr_drop_critical",
                name="Critical MRR Drop",
                category=AlertCategory.REVENUE_ANOMALY,
                metric_name="mrr_change_pct",
                condition="below",
                threshold=-20.0,
                severity=AlertSeverity.CRITICAL,
                title_template="Critical: MRR dropped by {value:.1f}%",
                description_template="Monthly recurring revenue decreased by {value:.1f}%, exceeding critical threshold of {threshold}%",
                cooldown_minutes=240,
            ),
            AlertRule(
                rule_id="mrr_drop_warning",
                name="MRR Drop Warning",
                category=AlertCategory.REVENUE_ANOMALY,
                metric_name="mrr_change_pct",
                condition="below",
                threshold=-10.0,
                severity=AlertSeverity.HIGH,
                title_template="Warning: MRR declined {value:.1f}%",
                description_template="Monthly recurring revenue decreased by {value:.1f}%",
                cooldown_minutes=120,
            ),
            AlertRule(
                rule_id="churn_spike",
                name="Churn Rate Spike",
                category=AlertCategory.CHURN_RISK,
                metric_name="churn_rate",
                condition="above",
                threshold=5.0,
                severity=AlertSeverity.HIGH,
                title_template="High Churn Alert: {value:.1f}% churn rate",
                description_template="Churn rate of {value:.1f}% exceeds threshold of {threshold}%",
                cooldown_minutes=60,
            ),
            AlertRule(
                rule_id="expansion_opportunity",
                name="Expansion Opportunity",
                category=AlertCategory.EXPANSION_OPPORTUNITY,
                metric_name="expansion_score",
                condition="above",
                threshold=0.8,
                severity=AlertSeverity.MEDIUM,
                title_template="Expansion Opportunity: Score {value:.2f}",
                description_template="Tenant shows high expansion potential (score: {value:.2f})",
                cooldown_minutes=1440,  # Once per day
            ),
            AlertRule(
                rule_id="billing_failure",
                name="Billing Failure",
                category=AlertCategory.BILLING_FAILURE,
                metric_name="failed_charges",
                condition="above",
                threshold=0,
                severity=AlertSeverity.HIGH,
                title_template="Billing Failure Detected",
                description_template="Failed to process {value:.0f} charge(s)",
                cooldown_minutes=60,
            ),
            AlertRule(
                rule_id="usage_spike",
                name="Usage Spike",
                category=AlertCategory.USAGE_SPIKE,
                metric_name="usage_change_pct",
                condition="above",
                threshold=200.0,
                severity=AlertSeverity.MEDIUM,
                title_template="Usage Spike: {value:.0f}% increase",
                description_template="Usage increased by {value:.0f}%, may indicate upsell opportunity or abuse",
                cooldown_minutes=30,
            ),
        ]
        
        for rule in default_rules:
            self.alert_manager.add_rule(rule)

    # -------------------------------------------------------------------------
    # Integration Hooks
    # -------------------------------------------------------------------------

    def connect_dashboard(self, hook: Callable[[Alert], None]) -> None:
        """Connect to dashboard for real-time alerts."""
        self._dashboard_hook = hook
        self.alert_manager.register_delivery_handler(
            AlertChannel.DASHBOARD, hook
        )
        logger.info("Connected to dashboard for alert delivery")

    def connect_forecaster(self, hook: Callable[[], Any]) -> None:
        """Connect to RevenueForecaster for forecast deviation alerts."""
        self._forecaster_hook = hook
        logger.info("Connected to RevenueForecaster")

    def connect_cohort_analytics(self, hook: Callable[[], Any]) -> None:
        """Connect to CohortAnalytics for cohort-based alerts."""
        self._cohort_hook = hook
        logger.info("Connected to CohortAnalytics")

    def connect_billing(self, hook: Callable[[], Any]) -> None:
        """Connect to billing system for payment alerts."""
        self._billing_hook = hook
        logger.info("Connected to billing system")

    # -------------------------------------------------------------------------
    # Metric Recording
    # -------------------------------------------------------------------------

    def record_mrr(
        self, 
        mrr: Decimal, 
        tenant_id: Optional[str] = None,
        tier: Optional[str] = None
    ) -> Optional[Alert]:
        """Record MRR and check for anomalies."""
        snapshot = MetricSnapshot(
            metric_name="mrr",
            value=float(mrr),
            timestamp=datetime.now(UTC),
            tenant_id=tenant_id,
            tier=tier,
        )
        self.anomaly_detector.record_metric(snapshot)
        
        anomaly = self.anomaly_detector.detect_anomaly(
            "mrr", float(mrr), tenant_id
        )
        
        if anomaly:
            anomaly_type, deviation, description = anomaly
            
            severity = AlertSeverity.HIGH if abs(deviation) > 3 else AlertSeverity.MEDIUM
            
            return self.alert_manager.create_alert(
                category=AlertCategory.REVENUE_ANOMALY,
                severity=severity,
                title=f"MRR Anomaly Detected",
                description=description,
                tenant_id=tenant_id,
                tier=tier,
                metric_name="mrr",
                metric_value=float(mrr),
                metadata={"anomaly_type": anomaly_type.value, "deviation": deviation},
            )
        
        return None

    def record_churn(
        self,
        churn_rate: float,
        churned_revenue: Decimal,
        tenant_id: Optional[str] = None,
        tier: Optional[str] = None
    ) -> Optional[Alert]:
        """Record churn event and create alert if significant."""
        snapshot = MetricSnapshot(
            metric_name="churn_rate",
            value=churn_rate,
            timestamp=datetime.now(UTC),
            tenant_id=tenant_id,
            tier=tier,
        )
        self.anomaly_detector.record_metric(snapshot)
        
        # Evaluate churn rules
        alerts = self.alert_manager.evaluate_rules(
            metrics={"churn_rate": churn_rate},
            tenant_id=tenant_id,
            tier=tier,
        )
        
        return alerts[0] if alerts else None

    def record_expansion(
        self,
        expansion_revenue: Decimal,
        expansion_score: float,
        tenant_id: str,
        tier: str
    ) -> Optional[Alert]:
        """Record expansion event and create opportunity alert."""
        # Evaluate expansion rules
        alerts = self.alert_manager.evaluate_rules(
            metrics={
                "expansion_score": expansion_score,
                "expansion_revenue": float(expansion_revenue),
            },
            tenant_id=tenant_id,
            tier=tier,
        )
        
        return alerts[0] if alerts else None

    def record_billing_failure(
        self,
        tenant_id: str,
        amount: Decimal,
        reason: str,
        tier: Optional[str] = None
    ) -> Alert:
        """Record billing failure and create alert."""
        return self.alert_manager.create_alert(
            category=AlertCategory.BILLING_FAILURE,
            severity=AlertSeverity.HIGH,
            title=f"Billing Failure: ${amount}",
            description=f"Failed to charge ${amount}. Reason: {reason}",
            tenant_id=tenant_id,
            tier=tier,
            metric_name="billing_failure",
            metric_value=float(amount),
            revenue_impact=amount,
            tags=["billing", "payment", "failure"],
        )

    def record_usage(
        self,
        usage_value: float,
        usage_type: str,
        tenant_id: Optional[str] = None,
        tier: Optional[str] = None
    ) -> Optional[Alert]:
        """Record usage and detect anomalies."""
        metric_name = f"usage_{usage_type}"
        
        snapshot = MetricSnapshot(
            metric_name=metric_name,
            value=usage_value,
            timestamp=datetime.now(UTC),
            tenant_id=tenant_id,
            tier=tier,
        )
        self.anomaly_detector.record_metric(snapshot)
        
        anomaly = self.anomaly_detector.detect_anomaly(
            metric_name, usage_value, tenant_id
        )
        
        if anomaly:
            anomaly_type, deviation, description = anomaly
            
            category = (
                AlertCategory.USAGE_SPIKE 
                if deviation > 0 
                else AlertCategory.USAGE_DROP
            )
            
            return self.alert_manager.create_alert(
                category=category,
                severity=AlertSeverity.MEDIUM,
                title=f"Usage Anomaly: {usage_type}",
                description=description,
                tenant_id=tenant_id,
                tier=tier,
                metric_name=metric_name,
                metric_value=usage_value,
            )
        
        return None

    # -------------------------------------------------------------------------
    # Health Monitoring
    # -------------------------------------------------------------------------

    def calculate_revenue_health(
        self,
        mrr: Decimal,
        mrr_previous: Decimal,
        churn_rate: float,
        expansion_rate: float,
        failed_charges: int = 0,
    ) -> RevenueHealthStatus:
        """Calculate overall revenue health status."""
        # MRR health (0-100)
        mrr_change = float((mrr - mrr_previous) / mrr_previous * 100) if mrr_previous else 0
        if mrr_change >= 5:
            mrr_health = 100
        elif mrr_change >= 0:
            mrr_health = 80 + mrr_change * 4
        elif mrr_change >= -5:
            mrr_health = 60 + mrr_change * 4
        else:
            mrr_health = max(0, 40 + mrr_change * 2)
        
        # Churn health (0-100)
        if churn_rate <= 2:
            churn_health = 100
        elif churn_rate <= 5:
            churn_health = 100 - (churn_rate - 2) * 20
        else:
            churn_health = max(0, 40 - (churn_rate - 5) * 10)
        
        # Growth health (0-100)
        net_revenue_retention = 100 + expansion_rate - churn_rate
        if net_revenue_retention >= 120:
            growth_health = 100
        elif net_revenue_retention >= 100:
            growth_health = 70 + (net_revenue_retention - 100) * 1.5
        else:
            growth_health = max(0, net_revenue_retention - 30)
        
        # Billing health (0-100)
        billing_health = max(0, 100 - failed_charges * 10)
        
        # Overall health score (weighted average)
        health_score = (
            mrr_health * 0.35 +
            churn_health * 0.25 +
            growth_health * 0.25 +
            billing_health * 0.15
        )
        
        # Determine status
        if health_score >= 80:
            status = "healthy"
        elif health_score >= 60:
            status = "warning"
        else:
            status = "critical"
        
        # Count active alerts
        active_alerts = self.alert_manager.get_active_alerts()
        critical_count = len([a for a in active_alerts if a.severity == AlertSeverity.CRITICAL])
        high_count = len([a for a in active_alerts if a.severity == AlertSeverity.HIGH])
        
        return RevenueHealthStatus(
            health_score=health_score,
            status=status,
            mrr_health=mrr_health,
            churn_health=churn_health,
            growth_health=growth_health,
            billing_health=billing_health,
            critical_alerts=critical_count,
            high_alerts=high_count,
            total_alerts=len(active_alerts),
            mrr=mrr,
            mrr_trend=mrr_change,
            churn_rate=churn_rate,
            expansion_rate=expansion_rate,
        )

    # -------------------------------------------------------------------------
    # Alert Retrieval
    # -------------------------------------------------------------------------

    def get_active_alerts(
        self,
        category: Optional[AlertCategory] = None,
        severity: Optional[AlertSeverity] = None,
        tenant_id: Optional[str] = None,
    ) -> List[Alert]:
        """Get active alerts with optional filters."""
        return self.alert_manager.get_active_alerts(
            category=category,
            severity=severity,
            tenant_id=tenant_id,
        )

    def get_alert_summary(self) -> Dict[str, Any]:
        """Get summary of all alerts."""
        alerts = self.alert_manager.get_active_alerts()
        
        by_severity = {}
        by_category = {}
        
        for alert in alerts:
            sev = alert.severity.value
            cat = alert.category.value
            
            by_severity[sev] = by_severity.get(sev, 0) + 1
            by_category[cat] = by_category.get(cat, 0) + 1
        
        return {
            "total_active": len(alerts),
            "by_severity": by_severity,
            "by_category": by_category,
            "oldest_alert": alerts[-1].created_at.isoformat() if alerts else None,
            "newest_alert": alerts[0].created_at.isoformat() if alerts else None,
        }


# =============================================================================
# Default Configuration
# =============================================================================

DEFAULT_ALERT_CONFIG = {
    "anomaly_detection": {
        "window_size": 30,
        "z_score_threshold": 2.5,
        "pct_change_threshold": 20.0,
    },
    "alert_thresholds": {
        "mrr_drop_critical_pct": -20.0,
        "mrr_drop_warning_pct": -10.0,
        "churn_rate_critical": 10.0,
        "churn_rate_warning": 5.0,
        "expansion_opportunity_score": 0.8,
        "usage_spike_pct": 200.0,
    },
    "delivery": {
        "default_channels": [AlertChannel.DASHBOARD],
        "critical_channels": [AlertChannel.DASHBOARD, AlertChannel.WEBHOOK],
    },
    "cooldowns": {
        "critical": 240,
        "high": 120,
        "medium": 60,
        "low": 30,
    },
}


# =============================================================================
# Factory Function
# =============================================================================

def create_revenue_alert_system(
    config: Optional[Dict[str, Any]] = None
) -> RevenueAlertSystem:
    """
    Factory function to create a configured RevenueAlertSystem.
    
    Args:
        config: Optional configuration overrides
        
    Returns:
        Configured RevenueAlertSystem instance
    """
    system = RevenueAlertSystem()
    
    effective_config = {**DEFAULT_ALERT_CONFIG, **(config or {})}
    
    # Configure anomaly detection
    anomaly_config = effective_config.get("anomaly_detection", {})
    system.anomaly_detector.window_size = anomaly_config.get("window_size", 30)
    
    # Set thresholds
    thresholds = effective_config.get("alert_thresholds", {})
    system.anomaly_detector.set_threshold(
        "mrr",
        z_threshold=anomaly_config.get("z_score_threshold", 2.5),
        pct_threshold=abs(thresholds.get("mrr_drop_warning_pct", -10.0)),
    )
    
    logger.info("Created RevenueAlertSystem with configuration")
    return system
