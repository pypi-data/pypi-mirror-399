# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
Observability Bridge - Phase 3 Week 20 Adjustment

Binds FederatedModelManager into the Observability Spine:
- Drift metrics → ThreatFlowTracker
- Rollback triggers → EnforcementHeatmap
- Model lineage changes → DashboardHookRegistry

Completes the closed loop between ML governance and observability.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, UTC
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

from .federated_model_manager import (
    ModelTier,
    ModelState,
    DriftSeverity,
    ModelVersion,
    DriftMetrics,
    FederatedModelManager,
    FederatedRound,
)

# Import observability components
from ..observability.threat_flow import (
    ThreatStage,
    ThreatFlowTracker,
    ThreatFlowEvent,
)
from ..observability.enforcement_heatmap import (
    EnforcementAction,
    EnforcementHeatmapTracker,
)
from ..observability.dashboard_hooks import (
    DashboardHookRegistry,
    HookType,
    DLSSnapshot,
    AnomalyCorrelation,
)
from ..observability.telemetry_ingestion import (
    TelemetryIngestion,
    TelemetryEventType,
)
from ..observability.metric_types import MetricLabels

logger = logging.getLogger(__name__)


# =============================================================================
# Enums for Bridge Events
# =============================================================================

class MLObservabilityEvent(Enum):
    """ML events that bridge to observability."""
    MODEL_REGISTERED = "model_registered"
    MODEL_ACTIVATED = "model_activated"
    MODEL_DEPRECATED = "model_deprecated"
    MODEL_ROLLED_BACK = "model_rolled_back"
    DRIFT_DETECTED = "drift_detected"
    DRIFT_RESOLVED = "drift_resolved"
    FEDERATED_ROUND_STARTED = "federated_round_started"
    FEDERATED_ROUND_COMPLETED = "federated_round_completed"
    GOVERNANCE_VIOLATION = "governance_violation"
    UPDATE_BLOCKED = "update_blocked"


# =============================================================================
# Drift → Threat Flow Mapping
# =============================================================================

def drift_severity_to_threat_stage(severity: DriftSeverity) -> ThreatStage:
    """Map drift severity to threat stage."""
    mapping = {
        DriftSeverity.NONE: ThreatStage.RESOLVED,
        DriftSeverity.LOW: ThreatStage.DETECTION,
        DriftSeverity.MEDIUM: ThreatStage.ANALYSIS,
        DriftSeverity.HIGH: ThreatStage.RESPONSE,
        DriftSeverity.CRITICAL: ThreatStage.RESPONSE,
    }
    return mapping.get(severity, ThreatStage.DETECTION)


def model_state_to_enforcement_action(state: ModelState) -> EnforcementAction:
    """Map model state to enforcement action."""
    mapping = {
        ModelState.ACTIVE: EnforcementAction.ALLOW,
        ModelState.DEGRADED: EnforcementAction.THROTTLE,
        ModelState.DEPRECATED: EnforcementAction.WARN,
        ModelState.ROLLED_BACK: EnforcementAction.BLOCK,
        ModelState.ARCHIVED: EnforcementAction.DENY,
    }
    return mapping.get(state, EnforcementAction.ALLOW)


# =============================================================================
# Observability Bridge
# =============================================================================

@dataclass
class ObservabilityBridgeConfig:
    """Configuration for the observability bridge."""
    enabled: bool = True
    emit_drift_to_threat_flow: bool = True
    emit_rollback_to_heatmap: bool = True
    emit_lineage_to_dashboard: bool = True
    emit_to_telemetry: bool = True
    
    # Threat flow settings
    drift_threat_type: str = "ml_drift"
    rollback_threat_type: str = "ml_rollback"
    
    # Heatmap dimensions
    heatmap_dimension1: str = "model_id"
    heatmap_dimension2: str = "tier"


class ObservabilityBridge:
    """
    Bridges FederatedModelManager events to the Observability Spine.
    
    Automatically emits ML governance events to:
    - ThreatFlowTracker for drift and anomalies
    - EnforcementHeatmapTracker for rollbacks and state changes
    - DashboardHookRegistry for lineage and real-time updates
    - TelemetryIngestion for metrics pipeline
    """
    
    def __init__(
        self,
        model_manager: FederatedModelManager,
        threat_tracker: Optional[ThreatFlowTracker] = None,
        heatmap_tracker: Optional[EnforcementHeatmapTracker] = None,
        dashboard_hooks: Optional[DashboardHookRegistry] = None,
        telemetry: Optional[TelemetryIngestion] = None,
        config: Optional[ObservabilityBridgeConfig] = None,
    ):
        self._manager = model_manager
        self._threat_tracker = threat_tracker
        self._heatmap_tracker = heatmap_tracker
        self._dashboard_hooks = dashboard_hooks
        self._telemetry = telemetry
        self._config = config or ObservabilityBridgeConfig()
        
        # Track active drift threats
        self._drift_threats: Dict[str, str] = {}  # model_id -> threat_id
        
        # Event history for debugging
        self._event_history: List[Dict[str, Any]] = []
        self._max_history = 1000
        
        # Register callbacks with model manager
        self._register_callbacks()
        
        logger.info("ObservabilityBridge initialized")
    
    def _register_callbacks(self) -> None:
        """Register callbacks with the model manager."""
        self._manager.on_version_change(self._on_version_change)
        self._manager.on_drift_detected(self._on_drift_detected)
        self._manager.on_rollback(self._on_rollback)
    
    # =========================================================================
    # Version Change → Dashboard Hooks
    # =========================================================================
    
    def _on_version_change(
        self,
        model_id: str,
        version: ModelVersion,
    ) -> None:
        """Handle model version changes."""
        if not self._config.enabled:
            return
        
        self._log_event(MLObservabilityEvent.MODEL_ACTIVATED, {
            "model_id": model_id,
            "version": str(version.version),
            "state": version.state.value,
            "tier": version.min_tier.value,
        })
        
        # Emit to dashboard hooks for lineage tracking
        if self._config.emit_lineage_to_dashboard and self._dashboard_hooks:
            self._emit_lineage_update(model_id, version)
        
        # Emit to telemetry
        if self._config.emit_to_telemetry and self._telemetry:
            self._emit_version_telemetry(model_id, version)
        
        # Track state changes in heatmap
        if self._config.emit_rollback_to_heatmap and self._heatmap_tracker:
            action = model_state_to_enforcement_action(version.state)
            self._heatmap_tracker.record(
                dimension1=model_id,
                dimension2=version.min_tier.value,
                action=action,
                metadata={
                    "version": str(version.version),
                    "event": "version_change",
                },
            )
    
    def _emit_lineage_update(
        self,
        model_id: str,
        version: ModelVersion,
    ) -> None:
        """Emit lineage update to dashboard hooks."""
        if not self._dashboard_hooks:
            return
        
        # Create anomaly correlation for lineage tracking
        correlation = AnomalyCorrelation(
            correlation_id=f"lineage-{model_id}-{version.version}",
            anomalies=[
                {
                    "type": "model_version",
                    "model_id": model_id,
                    "version": str(version.version),
                    "state": version.state.value,
                    "parent": version.parent_version,
                }
            ],
            correlation_type="model_lineage",
            confidence=1.0,
            root_cause=f"Model {model_id} updated to {version.version}",
            recommended_actions=[
                f"Monitor drift for {model_id}",
                "Validate performance metrics",
            ],
            metadata={
                "min_tier": version.min_tier.value,
                "training_samples": version.training_samples,
                "federation_round": version.federation_round,
            },
        )
        
        self._dashboard_hooks.emit(HookType.ANOMALY_CORRELATION, correlation)
    
    def _emit_version_telemetry(
        self,
        model_id: str,
        version: ModelVersion,
    ) -> None:
        """Emit version change to telemetry pipeline."""
        if not self._telemetry:
            return
        
        self._telemetry.ingest({
            "event_type": TelemetryEventType.ML_INFERENCE.value,
            "timestamp": datetime.now().isoformat(),
            "model_id": model_id,
            "version": str(version.version),
            "state": version.state.value,
            "tier": version.min_tier.value,
            "metrics": version.metrics.to_dict() if version.metrics else {},
        })
    
    # =========================================================================
    # Drift → Threat Flow
    # =========================================================================
    
    def _on_drift_detected(
        self,
        model_id: str,
        drift: DriftMetrics,
    ) -> None:
        """Handle drift detection events."""
        if not self._config.enabled:
            return
        
        self._log_event(MLObservabilityEvent.DRIFT_DETECTED, {
            "model_id": model_id,
            "severity": drift.severity.value,
            "data_drift": drift.data_drift_score,
            "concept_drift": drift.concept_drift_score,
        })
        
        # Emit to threat flow tracker
        if self._config.emit_drift_to_threat_flow and self._threat_tracker:
            self._emit_drift_threat(model_id, drift)
        
        # Emit to telemetry
        if self._config.emit_to_telemetry and self._telemetry:
            self._emit_drift_telemetry(model_id, drift)
        
        # Emit to dashboard hooks
        if self._config.emit_lineage_to_dashboard and self._dashboard_hooks:
            self._emit_drift_to_dashboard(model_id, drift)
    
    def _emit_drift_threat(
        self,
        model_id: str,
        drift: DriftMetrics,
    ) -> None:
        """Emit drift as a threat to ThreatFlowTracker."""
        if not self._threat_tracker:
            return
        
        threat_id = f"drift-{model_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        stage = drift_severity_to_threat_stage(drift.severity)
        
        # Track the threat
        self._threat_tracker.track_threat(
            threat_id=threat_id,
            threat_type=self._config.drift_threat_type,
            source=model_id,
            initial_stage=ThreatStage.INGESTION,
            metadata={
                "severity": drift.severity.value,
                "data_drift": drift.data_drift_score,
                "concept_drift": drift.concept_drift_score,
                "performance_degradation": drift.performance_degradation,
            },
        )
        
        # Progress through stages based on severity
        if drift.severity != DriftSeverity.NONE:
            self._threat_tracker.advance_threat(threat_id, ThreatStage.DETECTION)
        
        if drift.severity in [DriftSeverity.MEDIUM, DriftSeverity.HIGH, DriftSeverity.CRITICAL]:
            self._threat_tracker.advance_threat(threat_id, ThreatStage.ANALYSIS)
        
        if drift.severity in [DriftSeverity.HIGH, DriftSeverity.CRITICAL]:
            self._threat_tracker.advance_threat(threat_id, ThreatStage.RESPONSE)
        
        # Store for resolution tracking
        self._drift_threats[model_id] = threat_id
        
        logger.info(
            f"Drift threat {threat_id} created for {model_id} "
            f"at stage {stage.value}"
        )
    
    def _emit_drift_telemetry(
        self,
        model_id: str,
        drift: DriftMetrics,
    ) -> None:
        """Emit drift metrics to telemetry pipeline."""
        if not self._telemetry:
            return
        
        self._telemetry.ingest({
            "event_type": TelemetryEventType.ML_DRIFT.value,
            "timestamp": datetime.now().isoformat(),
            "model_id": model_id,
            "severity": drift.severity.value,
            "data_drift_score": drift.data_drift_score,
            "concept_drift_score": drift.concept_drift_score,
            "prediction_shift": drift.prediction_shift,
            "performance_degradation": drift.performance_degradation,
            "feature_drift_scores": drift.feature_drift_scores,
        })
    
    def _emit_drift_to_dashboard(
        self,
        model_id: str,
        drift: DriftMetrics,
    ) -> None:
        """Emit drift alert to dashboard hooks."""
        if not self._dashboard_hooks:
            return
        
        correlation = AnomalyCorrelation(
            correlation_id=f"drift-{model_id}-{datetime.now().strftime('%H%M%S')}",
            anomalies=[
                {
                    "type": "ml_drift",
                    "model_id": model_id,
                    "severity": drift.severity.value,
                    "data_drift": drift.data_drift_score,
                    "concept_drift": drift.concept_drift_score,
                }
            ],
            correlation_type="drift_detection",
            confidence=max(drift.data_drift_score, drift.concept_drift_score),
            root_cause=f"Model {model_id} experiencing {drift.severity.value} drift",
            recommended_actions=self._get_drift_actions(drift),
            metadata=drift.to_dict(),
        )
        
        self._dashboard_hooks.emit(HookType.ANOMALY_CORRELATION, correlation)
    
    def _get_drift_actions(self, drift: DriftMetrics) -> List[str]:
        """Get recommended actions based on drift severity."""
        actions = ["Monitor model performance"]
        
        if drift.severity == DriftSeverity.LOW:
            actions.append("Schedule retraining evaluation")
        elif drift.severity == DriftSeverity.MEDIUM:
            actions.extend([
                "Increase monitoring frequency",
                "Prepare rollback candidate",
            ])
        elif drift.severity == DriftSeverity.HIGH:
            actions.extend([
                "Consider immediate rollback",
                "Halt new traffic routing",
                "Initiate emergency retraining",
            ])
        elif drift.severity == DriftSeverity.CRITICAL:
            actions.extend([
                "IMMEDIATE ROLLBACK REQUIRED",
                "Block all model inference",
                "Escalate to on-call engineer",
            ])
        
        return actions
    
    # =========================================================================
    # Rollback → Enforcement Heatmap
    # =========================================================================
    
    def _on_rollback(
        self,
        model_id: str,
        from_version: str,
        to_version: str,
    ) -> None:
        """Handle rollback events."""
        if not self._config.enabled:
            return
        
        self._log_event(MLObservabilityEvent.MODEL_ROLLED_BACK, {
            "model_id": model_id,
            "from_version": from_version,
            "to_version": to_version,
        })
        
        # Emit to enforcement heatmap
        if self._config.emit_rollback_to_heatmap and self._heatmap_tracker:
            self._emit_rollback_heatmap(model_id, from_version, to_version)
        
        # Emit to threat flow (resolve drift threat)
        if self._config.emit_drift_to_threat_flow and self._threat_tracker:
            self._resolve_drift_threat(model_id)
        
        # Emit to telemetry
        if self._config.emit_to_telemetry and self._telemetry:
            self._emit_rollback_telemetry(model_id, from_version, to_version)
        
        # Emit to dashboard hooks
        if self._config.emit_lineage_to_dashboard and self._dashboard_hooks:
            self._emit_rollback_to_dashboard(model_id, from_version, to_version)
    
    def _emit_rollback_heatmap(
        self,
        model_id: str,
        from_version: str,
        to_version: str,
    ) -> None:
        """Emit rollback to enforcement heatmap."""
        if not self._heatmap_tracker:
            return
        
        # Record the rollback as an enforcement action
        self._heatmap_tracker.record(
            dimension1=model_id,
            dimension2=self._manager.tier.value,
            action=EnforcementAction.BLOCK,  # Rollback is blocking the bad version
            metadata={
                "event": "rollback",
                "from_version": from_version,
                "to_version": to_version,
            },
        )
        
        # Also record the activation of the rolled-back-to version
        self._heatmap_tracker.record(
            dimension1=model_id,
            dimension2=self._manager.tier.value,
            action=EnforcementAction.ALLOW,  # Now allowing the stable version
            metadata={
                "event": "rollback_activate",
                "version": to_version,
            },
        )
    
    def _resolve_drift_threat(self, model_id: str) -> None:
        """Resolve drift threat after rollback."""
        if not self._threat_tracker:
            return
        
        threat_id = self._drift_threats.get(model_id)
        if threat_id:
            self._threat_tracker.resolve_threat(
                threat_id=threat_id,
                resolution="rollback",
            )
            del self._drift_threats[model_id]
            
            logger.info(f"Drift threat {threat_id} resolved via rollback")
    
    def _emit_rollback_telemetry(
        self,
        model_id: str,
        from_version: str,
        to_version: str,
    ) -> None:
        """Emit rollback to telemetry pipeline."""
        if not self._telemetry:
            return
        
        self._telemetry.ingest({
            "event_type": TelemetryEventType.ENFORCEMENT_ACTION.value,
            "timestamp": datetime.now().isoformat(),
            "action": "model_rollback",
            "model_id": model_id,
            "from_version": from_version,
            "to_version": to_version,
            "tier": self._manager.tier.value,
        })
    
    def _emit_rollback_to_dashboard(
        self,
        model_id: str,
        from_version: str,
        to_version: str,
    ) -> None:
        """Emit rollback alert to dashboard hooks."""
        if not self._dashboard_hooks:
            return
        
        correlation = AnomalyCorrelation(
            correlation_id=f"rollback-{model_id}-{datetime.now().strftime('%H%M%S')}",
            anomalies=[
                {
                    "type": "model_rollback",
                    "model_id": model_id,
                    "from_version": from_version,
                    "to_version": to_version,
                }
            ],
            correlation_type="governance_action",
            confidence=1.0,
            root_cause=f"Model {model_id} rolled back from {from_version} to {to_version}",
            recommended_actions=[
                "Investigate root cause of rollback",
                "Review drift metrics before rollback",
                "Validate stable version performance",
            ],
            metadata={
                "tier": self._manager.tier.value,
            },
        )
        
        self._dashboard_hooks.emit(HookType.ANOMALY_CORRELATION, correlation)
    
    # =========================================================================
    # Federated Round Events
    # =========================================================================
    
    def emit_federated_round_start(self, round_obj: FederatedRound) -> None:
        """Emit federated round start event."""
        if not self._config.enabled:
            return
        
        self._log_event(MLObservabilityEvent.FEDERATED_ROUND_STARTED, {
            "model_id": round_obj.model_id,
            "round_number": round_obj.round_number,
            "expected_participants": len(round_obj.expected_participants),
        })
        
        if self._telemetry:
            self._telemetry.ingest({
                "event_type": TelemetryEventType.ML_INFERENCE.value,
                "timestamp": datetime.now().isoformat(),
                "event": "federated_round_start",
                "model_id": round_obj.model_id,
                "round_number": round_obj.round_number,
                "expected_participants": len(round_obj.expected_participants),
            })
    
    def emit_federated_round_complete(
        self,
        round_obj: FederatedRound,
        new_version: Optional[str] = None,
    ) -> None:
        """Emit federated round completion event."""
        if not self._config.enabled:
            return
        
        self._log_event(MLObservabilityEvent.FEDERATED_ROUND_COMPLETED, {
            "model_id": round_obj.model_id,
            "round_number": round_obj.round_number,
            "participation_rate": round_obj.participation_rate,
            "total_samples": round_obj.total_samples,
            "new_version": new_version,
        })
        
        if self._telemetry:
            self._telemetry.ingest({
                "event_type": TelemetryEventType.ML_INFERENCE.value,
                "timestamp": datetime.now().isoformat(),
                "event": "federated_round_complete",
                "model_id": round_obj.model_id,
                "round_number": round_obj.round_number,
                "participation_rate": round_obj.participation_rate,
                "total_samples": round_obj.total_samples,
                "new_version": new_version,
            })
        
        if self._dashboard_hooks and new_version:
            correlation = AnomalyCorrelation(
                correlation_id=f"fed-round-{round_obj.model_id}-{round_obj.round_number}",
                anomalies=[
                    {
                        "type": "federated_aggregation",
                        "model_id": round_obj.model_id,
                        "round": round_obj.round_number,
                        "participants": len(round_obj.received_updates),
                    }
                ],
                correlation_type="federated_learning",
                confidence=round_obj.participation_rate,
                root_cause=f"Federated round {round_obj.round_number} completed",
                recommended_actions=[
                    "Validate aggregated model performance",
                    "Monitor drift in next window",
                ],
                metadata={
                    "new_version": new_version,
                    "total_samples": round_obj.total_samples,
                },
            )
            self._dashboard_hooks.emit(HookType.ANOMALY_CORRELATION, correlation)
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    def _log_event(
        self,
        event: MLObservabilityEvent,
        details: Dict[str, Any],
    ) -> None:
        """Log event to internal history."""
        entry = {
            "event": event.value,
            "timestamp": datetime.now().isoformat(),
            "details": details,
        }
        
        self._event_history.append(entry)
        
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]
        
        logger.debug(f"ObservabilityBridge event: {event.value} - {details}")
    
    def get_event_history(
        self,
        event_type: Optional[MLObservabilityEvent] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get event history, optionally filtered by type."""
        history = self._event_history
        
        if event_type:
            history = [e for e in history if e["event"] == event_type.value]
        
        return history[-limit:]
    
    def get_status(self) -> Dict[str, Any]:
        """Get bridge status."""
        return {
            "enabled": self._config.enabled,
            "manager_tier": self._manager.tier.value,
            "active_drift_threats": len(self._drift_threats),
            "event_count": len(self._event_history),
            "has_threat_tracker": self._threat_tracker is not None,
            "has_heatmap_tracker": self._heatmap_tracker is not None,
            "has_dashboard_hooks": self._dashboard_hooks is not None,
            "has_telemetry": self._telemetry is not None,
        }


# =============================================================================
# Factory Function
# =============================================================================

def create_observability_bridge(
    model_manager: FederatedModelManager,
    threat_tracker: Optional[ThreatFlowTracker] = None,
    heatmap_tracker: Optional[EnforcementHeatmapTracker] = None,
    dashboard_hooks: Optional[DashboardHookRegistry] = None,
    telemetry: Optional[TelemetryIngestion] = None,
) -> ObservabilityBridge:
    """Create an observability bridge for a model manager."""
    return ObservabilityBridge(
        model_manager=model_manager,
        threat_tracker=threat_tracker,
        heatmap_tracker=heatmap_tracker,
        dashboard_hooks=dashboard_hooks,
        telemetry=telemetry,
    )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "MLObservabilityEvent",
    "ObservabilityBridgeConfig",
    "ObservabilityBridge",
    "create_observability_bridge",
    "drift_severity_to_threat_stage",
    "model_state_to_enforcement_action",
]
