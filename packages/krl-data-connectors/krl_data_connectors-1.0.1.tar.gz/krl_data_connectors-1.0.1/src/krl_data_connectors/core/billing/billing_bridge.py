from __future__ import annotations

# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
#
# ⚠️ DEPRECATION WARNING (Dec 2025):
# This module has been moved to krl-premium-backend.
# Import from: app.services.billing.billing_bridge
# This stub remains for backward compatibility but will be removed in v2.0.
# ----------------------------------------------------------------------
import warnings as _warnings
_warnings.warn(
    "krl_data_connectors.core.billing.billing_bridge is deprecated. "
    "Import from 'app.services.billing.billing_bridge' instead.",
    DeprecationWarning,
    stacklevel=2
)

"""
Billing Bridge - Phase 3 Week 21

Connects AdaptiveBillingController to the three synchronized loops:
1. Observability Loop → TelemetryIngestion → UsageMeter
2. Adaptive Defense Loop → ThreatFlowTracker → RiskPricingEngine
3. Model Governance Loop → FederatedModelManager → UpsellEngine

Completes the Monetization Loop as the fourth synchronized system.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, UTC
from decimal import Decimal
from typing import Any, Callable, Dict, List, Optional

from . import (
    AdaptiveBillingController,
    BillingTier,
    UsageMetricType,
    RevenueEventType,
    UpsellEvent,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class BillingBridgeConfig:
    """Configuration for billing bridge."""
    enabled: bool = True
    
    # Telemetry integration
    ingest_telemetry: bool = True
    telemetry_sample_rate: float = 1.0  # 1.0 = all events
    
    # Defense integration
    ingest_defense_events: bool = True
    update_risk_on_threats: bool = True
    
    # Governance integration
    ingest_governance_events: bool = True
    trigger_upsells_on_feature_gates: bool = True
    
    # DLS integration
    sync_dls_to_risk: bool = True
    dls_sync_interval_seconds: int = 60
    
    # Revenue event routing
    emit_to_dashboard: bool = True
    emit_to_telemetry: bool = True


# =============================================================================
# Telemetry Event Mapping
# =============================================================================

TELEMETRY_TO_USAGE_MAP: Dict[str, UsageMetricType] = {
    # API events
    "api.request": UsageMetricType.API_CALLS,
    "api.response": UsageMetricType.API_CALLS,
    
    # ML events
    "ml.inference": UsageMetricType.ML_INFERENCES,
    "ml.prediction": UsageMetricType.ML_INFERENCES,
    "ml.drift": UsageMetricType.ANOMALY_ANALYSES,
    "ml.retrain": UsageMetricType.ML_TRAINING_MINUTES,
    
    # Threat events
    "threat.detected": UsageMetricType.THREAT_DETECTIONS,
    "threat.response": UsageMetricType.ENFORCEMENT_ACTIONS,
    "threat.mitigated": UsageMetricType.THREAT_DETECTIONS,
    
    # Enforcement events
    "enforcement.decision": UsageMetricType.ENFORCEMENT_ACTIONS,
    "enforcement.action": UsageMetricType.ENFORCEMENT_ACTIONS,
    
    # Crown jewel events
    "crownjewel.access": UsageMetricType.CROWN_JEWEL_ACCESSES,
}


# =============================================================================
# Billing Bridge
# =============================================================================

class BillingBridge:
    """
    Bridges billing to the three synchronized loops.
    
    Wires:
    - TelemetryIngestion events → UsageMeter.record_usage
    - ThreatFlowTracker events → RiskPricingEngine.update_*_score
    - FederatedModelManager events → UpsellEngine + UsageMeter
    - DLS scores → RiskPricingEngine.update_dls_score
    - Revenue events → DashboardHookRegistry
    """
    
    def __init__(
        self,
        billing_controller: AdaptiveBillingController,
        config: Optional[BillingBridgeConfig] = None,
    ):
        self._billing = billing_controller
        self._config = config or BillingBridgeConfig()
        
        # External components (set via connect_* methods)
        self._telemetry = None
        self._threat_tracker = None
        self._model_manager = None
        self._dashboard_hooks = None
        self._dls_scorer = None
        
        # Tracking
        self._events_processed = 0
        self._last_dls_sync: Optional[datetime] = None
        
        logger.info("BillingBridge initialized")
    
    # =========================================================================
    # Connection Methods
    # =========================================================================
    
    def connect_telemetry(self, telemetry_ingestion: Any) -> None:
        """
        Connect to Observability Loop via TelemetryIngestion.
        
        Registers callback to receive telemetry events for usage metering.
        """
        self._telemetry = telemetry_ingestion
        
        if hasattr(telemetry_ingestion, 'add_processor'):
            telemetry_ingestion.add_processor(self._process_telemetry_event)
            logger.info("Connected to TelemetryIngestion")
        elif hasattr(telemetry_ingestion, 'on_event'):
            telemetry_ingestion.on_event(self._process_telemetry_event)
            logger.info("Connected to TelemetryIngestion via on_event")
    
    def connect_threat_tracker(self, threat_tracker: Any) -> None:
        """
        Connect to Adaptive Defense Loop via ThreatFlowTracker.
        
        Registers callback for threat events to update risk scores.
        """
        self._threat_tracker = threat_tracker
        
        if hasattr(threat_tracker, 'on_threat_event'):
            threat_tracker.on_threat_event(self._process_threat_event)
            logger.info("Connected to ThreatFlowTracker")
        elif hasattr(threat_tracker, 'add_listener'):
            threat_tracker.add_listener(self._process_threat_event)
            logger.info("Connected to ThreatFlowTracker via add_listener")
    
    def connect_model_manager(self, model_manager: Any) -> None:
        """
        Connect to Model Governance Loop via FederatedModelManager.
        
        Registers callbacks for model events.
        """
        self._model_manager = model_manager
        
        if hasattr(model_manager, 'on_version_change'):
            model_manager.on_version_change(self._on_model_version_change)
        if hasattr(model_manager, 'on_drift_detected'):
            model_manager.on_drift_detected(self._on_drift_detected)
        
        logger.info("Connected to FederatedModelManager")
    
    def connect_dashboard_hooks(self, dashboard_hooks: Any) -> None:
        """
        Connect to Dashboard for revenue event emission.
        """
        self._dashboard_hooks = dashboard_hooks
        
        # Register billing controller's revenue events to emit to dashboard
        self._billing.on_revenue_event(self._emit_to_dashboard)
        
        logger.info("Connected to DashboardHookRegistry")
    
    def connect_dls_scorer(self, dls_scorer: Any) -> None:
        """
        Connect to DLS scorer for risk pricing integration.
        """
        self._dls_scorer = dls_scorer
        
        if hasattr(dls_scorer, 'on_score_update'):
            dls_scorer.on_score_update(self._on_dls_update)
            logger.info("Connected to DLS scorer")
    
    # =========================================================================
    # Observability Loop Integration
    # =========================================================================
    
    def _process_telemetry_event(self, event: Any) -> None:
        """Process telemetry event for usage metering."""
        if not self._config.enabled or not self._config.ingest_telemetry:
            return
        
        try:
            # Handle different event formats
            if hasattr(event, 'event_type'):
                event_type = event.event_type.value if hasattr(event.event_type, 'value') else str(event.event_type)
                tenant_id = getattr(event, 'tenant_id', None) or 'default'
                metadata = getattr(event, 'payload', {})
            elif isinstance(event, dict):
                event_type = event.get('event_type', '')
                tenant_id = event.get('tenant_id', 'default')
                metadata = event
            else:
                return
            
            # Sample if configured
            if self._config.telemetry_sample_rate < 1.0:
                import random
                if random.random() > self._config.telemetry_sample_rate:
                    return
            
            # Ingest
            self._billing.ingest_telemetry_event(tenant_id, event_type, metadata)
            self._events_processed += 1
            
        except Exception as e:
            logger.warning(f"Error processing telemetry event: {e}")
    
    # =========================================================================
    # Adaptive Defense Loop Integration
    # =========================================================================
    
    def _process_threat_event(self, event: Any) -> None:
        """Process threat event for risk scoring."""
        if not self._config.enabled or not self._config.ingest_defense_events:
            return
        
        try:
            # Extract event data
            if hasattr(event, 'threat_type'):
                event_type = "threat_detected"
                severity = getattr(event, 'severity', 'medium')
                tenant_id = getattr(event, 'tenant_id', None) or 'default'
                metadata = {"threat_type": event.threat_type}
            elif isinstance(event, dict):
                event_type = event.get('event_type', 'threat_detected')
                severity = event.get('severity', 'medium')
                tenant_id = event.get('tenant_id', 'default')
                metadata = event
            else:
                return
            
            # Severity to string
            if hasattr(severity, 'value'):
                severity = severity.value
            
            # Ingest
            self._billing.ingest_defense_event(
                tenant_id=tenant_id,
                event_type=event_type,
                severity=severity,
                metadata=metadata,
            )
            self._events_processed += 1
            
        except Exception as e:
            logger.warning(f"Error processing threat event: {e}")
    
    def process_enforcement_heatmap(
        self,
        tenant_id: str,
        action: str,
        dimension1: str,
        dimension2: str,
    ) -> None:
        """Process enforcement heatmap data for risk scoring."""
        if not self._config.enabled:
            return
        
        # Map enforcement actions to risk contribution
        action_severity = {
            "ALLOW": None,  # No risk impact
            "WARN": "low",
            "THROTTLE": "medium",
            "BLOCK": "high",
            "DENY": "high",
            "QUARANTINE": "critical",
        }
        
        severity = action_severity.get(action.upper())
        if severity:
            self._billing.ingest_defense_event(
                tenant_id=tenant_id,
                event_type="enforcement_action",
                severity=severity,
                metadata={
                    "action": action,
                    "dimension1": dimension1,
                    "dimension2": dimension2,
                },
            )
    
    # =========================================================================
    # Model Governance Loop Integration
    # =========================================================================
    
    def _on_model_version_change(
        self,
        model_id: str,
        version: Any,
    ) -> None:
        """Handle model version changes."""
        if not self._config.enabled or not self._config.ingest_governance_events:
            return
        
        try:
            # Get tenant from version metadata
            tenant_id = "default"
            if hasattr(version, 'metadata'):
                tenant_id = version.metadata.get('tenant_id', 'default')
            
            # Check if this was a federated update
            federation_round = getattr(version, 'federation_round', None)
            
            if federation_round is not None:
                self._billing.ingest_governance_event(
                    tenant_id=tenant_id,
                    event_type="federated_round",
                    model_id=model_id,
                    metadata={
                        "version": str(version.version) if hasattr(version, 'version') else str(version),
                        "federation_round": federation_round,
                    },
                )
            
            self._events_processed += 1
            
        except Exception as e:
            logger.warning(f"Error processing model version change: {e}")
    
    def _on_drift_detected(
        self,
        model_id: str,
        drift: Any,
    ) -> None:
        """Handle drift detection events."""
        if not self._config.enabled or not self._config.ingest_governance_events:
            return
        
        try:
            # Get severity
            severity = "medium"
            if hasattr(drift, 'severity'):
                severity = drift.severity.value if hasattr(drift.severity, 'value') else str(drift.severity)
            
            # Default tenant
            tenant_id = "default"
            
            self._billing.ingest_governance_event(
                tenant_id=tenant_id,
                event_type="drift_detected",
                model_id=model_id,
                metadata={
                    "severity": severity,
                    "data_drift": getattr(drift, 'data_drift_score', 0),
                    "concept_drift": getattr(drift, 'concept_drift_score', 0),
                },
            )
            
            self._events_processed += 1
            
        except Exception as e:
            logger.warning(f"Error processing drift event: {e}")
    
    def check_ml_feature_access(
        self,
        tenant_id: str,
        model_type: str,
    ) -> tuple[bool, Optional[UpsellEvent]]:
        """
        Check if tenant can access an ML model type.
        
        Used by FederatedModelManager for tier gating.
        """
        if not self._config.trigger_upsells_on_feature_gates:
            return True, None
        
        # Map model types to features
        feature = f"ml_{model_type}"
        return self._billing.check_feature_access(tenant_id, feature)
    
    # =========================================================================
    # DLS Integration
    # =========================================================================
    
    def _on_dls_update(self, tenant_id: str, dls_score: float) -> None:
        """Handle DLS score updates."""
        if not self._config.enabled or not self._config.sync_dls_to_risk:
            return
        
        self._billing.update_dls_score(tenant_id, dls_score)
        self._last_dls_sync = datetime.now()
    
    def sync_dls_score(self, tenant_id: str, dls_score: float) -> None:
        """
        Manually sync DLS score to billing risk engine.
        
        Called periodically or on significant DLS changes.
        """
        if not self._config.enabled:
            return
        
        self._billing.update_dls_score(tenant_id, dls_score)
        self._last_dls_sync = datetime.now()
    
    # =========================================================================
    # Dashboard Integration
    # =========================================================================
    
    def _emit_to_dashboard(self, event: Dict[str, Any]) -> None:
        """Emit revenue event to dashboard."""
        if not self._config.emit_to_dashboard or not self._dashboard_hooks:
            return
        
        try:
            # Map revenue events to dashboard hook types
            event_type = event.get('event_type', '')
            
            if hasattr(self._dashboard_hooks, 'emit'):
                # Create appropriate dashboard event
                if event_type in ['upsell_triggered', 'tier_violation', 'threshold_exceeded']:
                    # These are alert-worthy
                    self._dashboard_hooks.emit('REVENUE_ALERT', event)
                else:
                    # Standard update
                    self._dashboard_hooks.emit('BILLING_UPDATE', event)
                    
        except Exception as e:
            logger.warning(f"Error emitting to dashboard: {e}")
    
    # =========================================================================
    # Direct Integration Methods
    # =========================================================================
    
    def record_api_call(
        self,
        tenant_id: str,
        endpoint: str,
        response_time_ms: float,
    ) -> None:
        """Directly record an API call for billing."""
        self._billing.ingest_telemetry_event(
            tenant_id=tenant_id,
            event_type="api.request",
            metadata={
                "endpoint": endpoint,
                "response_time_ms": response_time_ms,
            },
        )
    
    def record_ml_inference(
        self,
        tenant_id: str,
        model_id: str,
        latency_ms: float,
    ) -> None:
        """Directly record an ML inference for billing."""
        self._billing.ingest_telemetry_event(
            tenant_id=tenant_id,
            event_type="ml.inference",
            metadata={
                "model_id": model_id,
                "latency_ms": latency_ms,
            },
        )
    
    def record_threat_detection(
        self,
        tenant_id: str,
        threat_type: str,
        severity: str,
    ) -> None:
        """Directly record a threat detection for billing."""
        self._billing.ingest_defense_event(
            tenant_id=tenant_id,
            event_type="threat_detected",
            severity=severity,
            metadata={"threat_type": threat_type},
        )
    
    def record_tier_violation(
        self,
        tenant_id: str,
        violation_type: str,
    ) -> None:
        """Record a tier violation."""
        self._billing.record_tier_violation(tenant_id, violation_type)
    
    # =========================================================================
    # StoryBrand Upsell Integration
    # =========================================================================
    
    def connect_upsell_integration(
        self,
        integration: Any,  # UpsellMessageIntegration
    ) -> None:
        """
        Connect StoryBrand upsell message integration.
        
        This wires personalized StoryBrand narrative messages to:
        - UpsellEngine triggers → Email delivery (SendGrid/SMTP)
        - UpsellEngine triggers → In-app notifications (banner/modal/toast)
        - Revenue events → Conversion tracking
        
        Usage:
        ```python
        from krl_data_connectors.core.billing import (
            create_upsell_integration,
            EmailProvider,
        )
        
        # Create integration with email provider
        integration = create_upsell_integration(
            email_provider=EmailProvider.SENDGRID,
            email_api_key=os.environ["SENDGRID_API_KEY"],
            customer_data_provider=lambda tid: fetch_customer(tid),
            usage_data_provider=lambda tid: fetch_usage(tid),
        )
        
        # Wire to billing bridge
        bridge.connect_upsell_integration(integration)
        ```
        """
        # Wire upsell events to the integration handler
        if hasattr(self._billing, 'upsell_engine') and self._billing.upsell_engine:
            self._billing.upsell_engine.on_upsell_triggered(
                lambda event: integration.handle_upsell_event(event)
            )
            logger.info("Connected UpsellMessageIntegration to UpsellEngine")
        
        # Wire revenue events for conversion tracking
        self._billing.on_revenue_event(
            lambda event: self._track_revenue_conversion(event, integration)
        )
        
        self._upsell_integration = integration
        logger.info("StoryBrand upsell integration connected")
    
    def _track_revenue_conversion(
        self,
        event: Dict[str, Any],
        integration: Any,
    ) -> None:
        """Track revenue events for conversion attribution."""
        try:
            # Look for upgrade/purchase events
            event_type = event.get('event_type', '')
            if event_type in ['tier_upgrade', 'purchase', 'subscription_upgrade']:
                # Check if there's a tracking_id from a recent upsell
                tracking_id = event.get('tracking_id') or event.get('metadata', {}).get('tracking_id')
                if tracking_id:
                    integration.track_conversion(
                        tracking_id,
                        {
                            "amount": event.get("amount"),
                            "tier": event.get("tier"),
                            "event_type": event_type,
                        }
                    )
        except Exception as e:
            logger.warning(f"Error tracking revenue conversion: {e}")
    
    def get_pending_notifications(self, tenant_id: str) -> List[Dict[str, Any]]:
        """
        Get pending in-app notifications for a tenant.
        
        Called by dashboard to render upgrade notifications.
        Returns list of notification payloads for frontend rendering.
        """
        if hasattr(self, '_upsell_integration') and self._upsell_integration:
            return self._upsell_integration.get_pending_notifications(tenant_id)
        return []
    
    def dismiss_notification(self, notification_id: str, tenant_id: str) -> bool:
        """Dismiss an in-app notification."""
        if hasattr(self, '_upsell_integration') and self._upsell_integration:
            return self._upsell_integration.dismiss_notification(notification_id, tenant_id)
        return False
    
    # =========================================================================
    # Status & Reporting
    # =========================================================================
    
    def get_status(self) -> Dict[str, Any]:
        """Get bridge status."""
        status = {
            "enabled": self._config.enabled,
            "events_processed": self._events_processed,
            "last_dls_sync": self._last_dls_sync.isoformat() if self._last_dls_sync else None,
            "connections": {
                "telemetry": self._telemetry is not None,
                "threat_tracker": self._threat_tracker is not None,
                "model_manager": self._model_manager is not None,
                "dashboard_hooks": self._dashboard_hooks is not None,
                "dls_scorer": self._dls_scorer is not None,
                "upsell_integration": hasattr(self, '_upsell_integration') and self._upsell_integration is not None,
            },
            "config": {
                "ingest_telemetry": self._config.ingest_telemetry,
                "ingest_defense": self._config.ingest_defense_events,
                "ingest_governance": self._config.ingest_governance_events,
                "sync_dls": self._config.sync_dls_to_risk,
            },
        }
        
        # Add upsell integration status if connected
        if hasattr(self, '_upsell_integration') and self._upsell_integration:
            status["upsell_integration"] = self._upsell_integration.get_status()
        
        return status


# =============================================================================
# Factory Function
# =============================================================================

def create_billing_bridge(
    billing_controller: AdaptiveBillingController,
    config: Optional[BillingBridgeConfig] = None,
) -> BillingBridge:
    """Create a billing bridge."""
    return BillingBridge(billing_controller, config)


def create_full_billing_stack(
    telemetry: Any = None,
    threat_tracker: Any = None,
    model_manager: Any = None,
    dashboard_hooks: Any = None,
    dls_scorer: Any = None,
) -> tuple[AdaptiveBillingController, BillingBridge]:
    """
    Create a fully connected billing stack.
    
    Returns (controller, bridge) tuple.
    """
    from . import create_billing_controller
    
    controller = create_billing_controller()
    bridge = BillingBridge(controller)
    
    if telemetry:
        bridge.connect_telemetry(telemetry)
    if threat_tracker:
        bridge.connect_threat_tracker(threat_tracker)
    if model_manager:
        bridge.connect_model_manager(model_manager)
    if dashboard_hooks:
        bridge.connect_dashboard_hooks(dashboard_hooks)
    if dls_scorer:
        bridge.connect_dls_scorer(dls_scorer)
    
    return controller, bridge


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "BillingBridgeConfig",
    "BillingBridge",
    "TELEMETRY_TO_USAGE_MAP",
    "create_billing_bridge",
    "create_full_billing_stack",
]
