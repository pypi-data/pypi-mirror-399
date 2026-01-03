# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
Policy Enforcement Loop - Phase 3 Week 20 Adjustment

Completes the closed loop between ML governance and operational systems:
- GovernanceChange → PolicyPushService.push_policy
- FederatedUpdate → AdaptiveControls.recalibrate
- DriftEvent → TelemetryIngestion.adjust_thresholds

Positions Week 21 to drive monetization through the ML governance surface.
"""

from __future__ import annotations

import logging
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Protocol, Set

from .federated_model_manager import (
    ModelTier,
    DriftSeverity,
    ModelVersion,
    DriftMetrics,
    FederatedModelManager,
    FederatedUpdate,
    TIER_GOVERNANCE,
)
from .ml_governance import (
    PolicyAction,
    PolicyDecision,
    PolicyRule,
    PolicyEvaluationResult,
    GovernanceController,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================

class EnforcementEvent(Enum):
    """Events that trigger enforcement loop actions."""
    GOVERNANCE_CHANGE = "governance_change"
    POLICY_UPDATE = "policy_update"
    FEDERATED_UPDATE = "federated_update"
    DRIFT_DETECTED = "drift_detected"
    DRIFT_RESOLVED = "drift_resolved"
    MODEL_ROLLBACK = "model_rollback"
    THRESHOLD_BREACH = "threshold_breach"
    TIER_CHANGE = "tier_change"


class AdaptiveAction(Enum):
    """Adaptive control actions."""
    INCREASE_SAMPLING = "increase_sampling"
    DECREASE_SAMPLING = "decrease_sampling"
    TIGHTEN_THRESHOLDS = "tighten_thresholds"
    RELAX_THRESHOLDS = "relax_thresholds"
    ENABLE_FEATURE = "enable_feature"
    DISABLE_FEATURE = "disable_feature"
    ESCALATE = "escalate"
    DE_ESCALATE = "de_escalate"
    RECALIBRATE = "recalibrate"


# =============================================================================
# Protocols for External Services
# =============================================================================

class PolicyPushService(Protocol):
    """Protocol for policy push services."""
    
    def push_policy(
        self,
        policy_id: str,
        policy_data: Dict[str, Any],
        targets: List[str],
    ) -> bool:
        """Push a policy to targets."""
        ...
    
    def revoke_policy(self, policy_id: str) -> bool:
        """Revoke a policy."""
        ...


class AdaptiveControlsService(Protocol):
    """Protocol for adaptive controls."""
    
    def recalibrate(
        self,
        control_id: str,
        parameters: Dict[str, Any],
    ) -> bool:
        """Recalibrate a control."""
        ...
    
    def adjust_threshold(
        self,
        control_id: str,
        threshold_name: str,
        new_value: float,
    ) -> bool:
        """Adjust a threshold."""
        ...


class TelemetryIntegrationService(Protocol):
    """Protocol for telemetry integration."""
    
    def adjust_thresholds(
        self,
        threshold_updates: Dict[str, float],
    ) -> bool:
        """Adjust telemetry thresholds."""
        ...
    
    def update_sampling_rate(
        self,
        event_type: str,
        rate: float,
    ) -> bool:
        """Update sampling rate for event type."""
        ...


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class EnforcementChange:
    """A change that requires enforcement loop action."""
    change_id: str
    event: EnforcementEvent
    source: str
    timestamp: datetime
    
    # What changed
    change_type: str
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    
    # Context
    model_id: Optional[str] = None
    tier: Optional[ModelTier] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Enforcement
    actions_taken: List[str] = field(default_factory=list)
    processed: bool = False
    processed_at: Optional[datetime] = None


@dataclass
class ThresholdConfig:
    """Configuration for adaptive thresholds."""
    name: str
    base_value: float
    current_value: float
    min_value: float
    max_value: float
    
    # Adjustment parameters
    drift_multiplier: float = 1.5  # Multiplier when drift detected
    recovery_rate: float = 0.1    # Rate to return to base
    
    # Tier-specific overrides
    tier_overrides: Dict[ModelTier, float] = field(default_factory=dict)


@dataclass
class AdaptiveControlState:
    """State of an adaptive control."""
    control_id: str
    enabled: bool = True
    
    # Current parameters
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Thresholds
    thresholds: Dict[str, ThresholdConfig] = field(default_factory=dict)
    
    # History
    last_recalibration: Optional[datetime] = None
    recalibration_count: int = 0


# =============================================================================
# Default Service Implementations
# =============================================================================

class DefaultPolicyPushService:
    """Default implementation of PolicyPushService."""
    
    def __init__(self):
        self._policies: Dict[str, Dict[str, Any]] = {}
        self._push_history: List[Dict[str, Any]] = []
    
    def push_policy(
        self,
        policy_id: str,
        policy_data: Dict[str, Any],
        targets: List[str],
    ) -> bool:
        """Push a policy to targets."""
        self._policies[policy_id] = {
            "data": policy_data,
            "targets": targets,
            "pushed_at": datetime.now().isoformat(),
        }
        
        self._push_history.append({
            "action": "push",
            "policy_id": policy_id,
            "targets": targets,
            "timestamp": datetime.now().isoformat(),
        })
        
        logger.info(f"Policy {policy_id} pushed to {len(targets)} targets")
        return True
    
    def revoke_policy(self, policy_id: str) -> bool:
        """Revoke a policy."""
        if policy_id in self._policies:
            del self._policies[policy_id]
            
            self._push_history.append({
                "action": "revoke",
                "policy_id": policy_id,
                "timestamp": datetime.now().isoformat(),
            })
            
            logger.info(f"Policy {policy_id} revoked")
            return True
        return False
    
    def get_active_policies(self) -> Dict[str, Dict[str, Any]]:
        """Get all active policies."""
        return self._policies.copy()


class DefaultAdaptiveControlsService:
    """Default implementation of AdaptiveControlsService."""
    
    def __init__(self):
        self._controls: Dict[str, AdaptiveControlState] = {}
        self._history: List[Dict[str, Any]] = []
    
    def register_control(self, control_id: str, initial_params: Dict[str, Any]) -> None:
        """Register an adaptive control."""
        self._controls[control_id] = AdaptiveControlState(
            control_id=control_id,
            parameters=initial_params,
        )
    
    def recalibrate(
        self,
        control_id: str,
        parameters: Dict[str, Any],
    ) -> bool:
        """Recalibrate a control."""
        if control_id not in self._controls:
            self._controls[control_id] = AdaptiveControlState(control_id=control_id)
        
        state = self._controls[control_id]
        old_params = state.parameters.copy()
        state.parameters.update(parameters)
        state.last_recalibration = datetime.now()
        state.recalibration_count += 1
        
        self._history.append({
            "action": "recalibrate",
            "control_id": control_id,
            "old_params": old_params,
            "new_params": parameters,
            "timestamp": datetime.now().isoformat(),
        })
        
        logger.info(f"Control {control_id} recalibrated: {parameters}")
        return True
    
    def adjust_threshold(
        self,
        control_id: str,
        threshold_name: str,
        new_value: float,
    ) -> bool:
        """Adjust a threshold."""
        if control_id not in self._controls:
            return False
        
        state = self._controls[control_id]
        
        if threshold_name in state.thresholds:
            old_value = state.thresholds[threshold_name].current_value
            state.thresholds[threshold_name].current_value = new_value
        else:
            old_value = None
            state.thresholds[threshold_name] = ThresholdConfig(
                name=threshold_name,
                base_value=new_value,
                current_value=new_value,
                min_value=new_value * 0.5,
                max_value=new_value * 2.0,
            )
        
        self._history.append({
            "action": "adjust_threshold",
            "control_id": control_id,
            "threshold": threshold_name,
            "old_value": old_value,
            "new_value": new_value,
            "timestamp": datetime.now().isoformat(),
        })
        
        logger.info(f"Threshold {control_id}.{threshold_name} adjusted to {new_value}")
        return True
    
    def get_control_state(self, control_id: str) -> Optional[AdaptiveControlState]:
        """Get state of a control."""
        return self._controls.get(control_id)


class DefaultTelemetryIntegrationService:
    """Default implementation of TelemetryIntegrationService."""
    
    def __init__(self):
        self._thresholds: Dict[str, float] = {}
        self._sampling_rates: Dict[str, float] = {}
        self._history: List[Dict[str, Any]] = []
    
    def adjust_thresholds(
        self,
        threshold_updates: Dict[str, float],
    ) -> bool:
        """Adjust telemetry thresholds."""
        for name, value in threshold_updates.items():
            old_value = self._thresholds.get(name)
            self._thresholds[name] = value
            
            self._history.append({
                "action": "adjust_threshold",
                "threshold": name,
                "old_value": old_value,
                "new_value": value,
                "timestamp": datetime.now().isoformat(),
            })
        
        logger.info(f"Telemetry thresholds adjusted: {threshold_updates}")
        return True
    
    def update_sampling_rate(
        self,
        event_type: str,
        rate: float,
    ) -> bool:
        """Update sampling rate for event type."""
        rate = max(0.0, min(1.0, rate))  # Clamp to [0, 1]
        old_rate = self._sampling_rates.get(event_type, 1.0)
        self._sampling_rates[event_type] = rate
        
        self._history.append({
            "action": "update_sampling_rate",
            "event_type": event_type,
            "old_rate": old_rate,
            "new_rate": rate,
            "timestamp": datetime.now().isoformat(),
        })
        
        logger.info(f"Sampling rate for {event_type} updated to {rate}")
        return True
    
    def get_thresholds(self) -> Dict[str, float]:
        """Get current thresholds."""
        return self._thresholds.copy()
    
    def get_sampling_rates(self) -> Dict[str, float]:
        """Get current sampling rates."""
        return self._sampling_rates.copy()


# =============================================================================
# Policy Enforcement Loop Controller
# =============================================================================

class PolicyEnforcementLoop:
    """
    Closed-loop controller for policy enforcement.
    
    Connects:
    - GovernanceChange → PolicyPushService.push_policy
    - FederatedUpdate → AdaptiveControls.recalibrate
    - DriftEvent → TelemetryIngestion.adjust_thresholds
    """
    
    def __init__(
        self,
        model_manager: Optional[FederatedModelManager] = None,
        governance_controller: Optional[GovernanceController] = None,
        policy_service: Optional[PolicyPushService] = None,
        adaptive_controls: Optional[AdaptiveControlsService] = None,
        telemetry_integration: Optional[TelemetryIntegrationService] = None,
    ):
        self._model_manager = model_manager
        self._governance = governance_controller
        
        # Use defaults if not provided
        self._policy_service = policy_service or DefaultPolicyPushService()
        self._adaptive_controls = adaptive_controls or DefaultAdaptiveControlsService()
        self._telemetry = telemetry_integration or DefaultTelemetryIntegrationService()
        
        # Change queue and history
        self._pending_changes: List[EnforcementChange] = []
        self._processed_changes: List[EnforcementChange] = []
        self._max_history = 1000
        
        # Configuration
        self._enabled = True
        self._auto_process = True
        
        # Tier-specific threshold adjustments
        self._tier_drift_thresholds: Dict[ModelTier, Dict[str, float]] = {
            ModelTier.COMMUNITY: {
                "drift_alert": 0.5,
                "drift_critical": 0.8,
                "sampling_rate": 0.1,
            },
            ModelTier.PRO: {
                "drift_alert": 0.3,
                "drift_critical": 0.6,
                "sampling_rate": 0.5,
            },
            ModelTier.ENTERPRISE: {
                "drift_alert": 0.15,
                "drift_critical": 0.4,
                "sampling_rate": 1.0,
            },
        }
        
        # Lock for thread safety
        self._lock = threading.RLock()
        
        # Register callbacks
        self._register_callbacks()
        
        logger.info("PolicyEnforcementLoop initialized")
    
    def _register_callbacks(self) -> None:
        """Register callbacks with model manager."""
        if self._model_manager:
            self._model_manager.on_version_change(self._on_model_version_change)
            self._model_manager.on_drift_detected(self._on_drift_detected)
            self._model_manager.on_rollback(self._on_rollback)
    
    # =========================================================================
    # Event Handlers
    # =========================================================================
    
    def _on_model_version_change(
        self,
        model_id: str,
        version: ModelVersion,
    ) -> None:
        """Handle model version changes (federated updates)."""
        if not self._enabled:
            return
        
        change = EnforcementChange(
            change_id=f"ver-{model_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            event=EnforcementEvent.FEDERATED_UPDATE,
            source="model_manager",
            timestamp=datetime.now(),
            change_type="version_change",
            old_value=version.parent_version,
            new_value=str(version.version),
            model_id=model_id,
            tier=version.min_tier,
            metadata={
                "state": version.state.value,
                "federation_round": version.federation_round,
            },
        )
        
        self._queue_change(change)
        
        if self._auto_process:
            self._process_federated_update(change, version)
    
    def _on_drift_detected(
        self,
        model_id: str,
        drift: DriftMetrics,
    ) -> None:
        """Handle drift detection events."""
        if not self._enabled:
            return
        
        change = EnforcementChange(
            change_id=f"drift-{model_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            event=EnforcementEvent.DRIFT_DETECTED,
            source="model_manager",
            timestamp=datetime.now(),
            change_type="drift_detection",
            new_value=drift.severity.value,
            model_id=model_id,
            tier=self._model_manager.tier if self._model_manager else ModelTier.COMMUNITY,
            metadata=drift.to_dict(),
        )
        
        self._queue_change(change)
        
        if self._auto_process:
            self._process_drift_event(change, drift)
    
    def _on_rollback(
        self,
        model_id: str,
        from_version: str,
        to_version: str,
    ) -> None:
        """Handle rollback events."""
        if not self._enabled:
            return
        
        change = EnforcementChange(
            change_id=f"rollback-{model_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            event=EnforcementEvent.MODEL_ROLLBACK,
            source="model_manager",
            timestamp=datetime.now(),
            change_type="rollback",
            old_value=from_version,
            new_value=to_version,
            model_id=model_id,
            tier=self._model_manager.tier if self._model_manager else ModelTier.COMMUNITY,
        )
        
        self._queue_change(change)
        
        if self._auto_process:
            self._process_rollback(change)
    
    # =========================================================================
    # Processing Logic
    # =========================================================================
    
    def _process_federated_update(
        self,
        change: EnforcementChange,
        version: ModelVersion,
    ) -> None:
        """
        Process federated update: FederatedUpdate → AdaptiveControls.recalibrate
        """
        actions = []
        
        # 1. Recalibrate adaptive controls for the model
        if change.model_id:
            control_id = f"model-{change.model_id}"
            
            recalibrate_params = {
                "active_version": str(version.version),
                "min_tier": version.min_tier.value,
                "accuracy": version.metrics.accuracy if version.metrics else 0.0,
                "latency_p99": version.metrics.latency_p99_ms if version.metrics else 0.0,
                "updated_at": datetime.now().isoformat(),
            }
            
            self._adaptive_controls.recalibrate(control_id, recalibrate_params)
            actions.append(f"recalibrated:{control_id}")
        
        # 2. Push governance policy if this is a federation result
        if version.federation_round is not None:
            policy_id = f"fed-update-{change.model_id}-r{version.federation_round}"
            policy_data = {
                "model_id": change.model_id,
                "version": str(version.version),
                "federation_round": version.federation_round,
                "min_tier": version.min_tier.value,
                "effective_at": datetime.now().isoformat(),
            }
            
            # Push to appropriate tier targets
            targets = self._get_policy_targets(version.min_tier)
            self._policy_service.push_policy(policy_id, policy_data, targets)
            actions.append(f"pushed_policy:{policy_id}")
        
        # 3. Update telemetry thresholds based on new model metrics
        if version.metrics and version.metrics.accuracy > 0:
            threshold_updates = {
                f"{change.model_id}_accuracy_alert": version.metrics.accuracy * 0.9,
                f"{change.model_id}_latency_alert": version.metrics.latency_p99_ms * 1.5,
            }
            self._telemetry.adjust_thresholds(threshold_updates)
            actions.append("adjusted_telemetry_thresholds")
        
        change.actions_taken = actions
        change.processed = True
        change.processed_at = datetime.now()
        
        logger.info(f"Processed federated update for {change.model_id}: {actions}")
    
    def _process_drift_event(
        self,
        change: EnforcementChange,
        drift: DriftMetrics,
    ) -> None:
        """
        Process drift event: DriftEvent → TelemetryIngestion.adjust_thresholds
        """
        actions = []
        tier = change.tier or ModelTier.COMMUNITY
        
        # 1. Adjust telemetry thresholds based on drift severity
        tier_thresholds = self._tier_drift_thresholds.get(tier, {})
        
        if drift.severity in [DriftSeverity.HIGH, DriftSeverity.CRITICAL]:
            # Tighten thresholds and increase sampling
            threshold_updates = {
                f"{change.model_id}_drift_threshold": tier_thresholds.get("drift_critical", 0.4),
                f"{change.model_id}_anomaly_threshold": 0.5,  # More sensitive
            }
            self._telemetry.adjust_thresholds(threshold_updates)
            actions.append("tightened_thresholds")
            
            # Increase sampling rate
            self._telemetry.update_sampling_rate(
                f"{change.model_id}_inference",
                min(1.0, tier_thresholds.get("sampling_rate", 0.5) * 2.0)
            )
            actions.append("increased_sampling")
            
        elif drift.severity == DriftSeverity.MEDIUM:
            # Moderate adjustment
            threshold_updates = {
                f"{change.model_id}_drift_threshold": tier_thresholds.get("drift_alert", 0.3),
            }
            self._telemetry.adjust_thresholds(threshold_updates)
            actions.append("adjusted_thresholds")
        
        # 2. Recalibrate adaptive controls
        if change.model_id:
            control_id = f"model-{change.model_id}"
            self._adaptive_controls.recalibrate(control_id, {
                "drift_severity": drift.severity.value,
                "data_drift": drift.data_drift_score,
                "concept_drift": drift.concept_drift_score,
                "last_drift_check": datetime.now().isoformat(),
            })
            actions.append(f"recalibrated:{control_id}")
        
        # 3. Push drift alert policy
        if drift.severity in [DriftSeverity.HIGH, DriftSeverity.CRITICAL]:
            policy_id = f"drift-alert-{change.model_id}"
            policy_data = {
                "type": "drift_alert",
                "model_id": change.model_id,
                "severity": drift.severity.value,
                "action": "restrict" if drift.severity == DriftSeverity.CRITICAL else "monitor",
                "metrics": drift.to_dict(),
            }
            
            targets = self._get_policy_targets(tier)
            self._policy_service.push_policy(policy_id, policy_data, targets)
            actions.append(f"pushed_drift_policy:{policy_id}")
        
        change.actions_taken = actions
        change.processed = True
        change.processed_at = datetime.now()
        
        logger.info(f"Processed drift event for {change.model_id}: {actions}")
    
    def _process_rollback(self, change: EnforcementChange) -> None:
        """
        Process rollback: Model rollback → Policy revocation + control reset
        """
        actions = []
        
        # 1. Revoke any drift alert policies
        if change.model_id:
            drift_policy_id = f"drift-alert-{change.model_id}"
            if self._policy_service.revoke_policy(drift_policy_id):
                actions.append(f"revoked_policy:{drift_policy_id}")
        
        # 2. Reset adaptive controls to stable state
        if change.model_id:
            control_id = f"model-{change.model_id}"
            self._adaptive_controls.recalibrate(control_id, {
                "rollback_performed": True,
                "stable_version": change.new_value,
                "rolled_back_from": change.old_value,
                "reset_at": datetime.now().isoformat(),
            })
            actions.append(f"reset_controls:{control_id}")
        
        # 3. Restore normal telemetry thresholds
        tier = change.tier or ModelTier.COMMUNITY
        tier_thresholds = self._tier_drift_thresholds.get(tier, {})
        
        threshold_updates = {
            f"{change.model_id}_drift_threshold": tier_thresholds.get("drift_alert", 0.3),
            f"{change.model_id}_anomaly_threshold": 0.7,  # Normal sensitivity
        }
        self._telemetry.adjust_thresholds(threshold_updates)
        actions.append("restored_thresholds")
        
        # Restore normal sampling rate
        self._telemetry.update_sampling_rate(
            f"{change.model_id}_inference",
            tier_thresholds.get("sampling_rate", 0.5)
        )
        actions.append("restored_sampling")
        
        # 4. Push rollback notification policy
        policy_id = f"rollback-{change.model_id}-{datetime.now().strftime('%H%M%S')}"
        policy_data = {
            "type": "rollback_notification",
            "model_id": change.model_id,
            "from_version": change.old_value,
            "to_version": change.new_value,
            "rollback_time": datetime.now().isoformat(),
        }
        
        targets = self._get_policy_targets(tier)
        self._policy_service.push_policy(policy_id, policy_data, targets)
        actions.append(f"pushed_rollback_notification:{policy_id}")
        
        change.actions_taken = actions
        change.processed = True
        change.processed_at = datetime.now()
        
        logger.info(f"Processed rollback for {change.model_id}: {actions}")
    
    # =========================================================================
    # Manual Change Processing
    # =========================================================================
    
    def push_governance_change(
        self,
        rule: PolicyRule,
        action: str = "add",
    ) -> EnforcementChange:
        """
        Push a governance change: GovernanceChange → PolicyPushService.push_policy
        """
        change = EnforcementChange(
            change_id=f"gov-{rule.rule_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            event=EnforcementEvent.GOVERNANCE_CHANGE,
            source="governance_controller",
            timestamp=datetime.now(),
            change_type=f"rule_{action}",
            new_value=rule.rule_id,
            metadata={
                "rule_name": rule.name,
                "decision": rule.decision.value,
                "priority": rule.priority,
            },
        )
        
        self._queue_change(change)
        
        # Push policy
        policy_id = f"gov-rule-{rule.rule_id}"
        policy_data = {
            "rule_id": rule.rule_id,
            "name": rule.name,
            "description": rule.description,
            "actions": [a.value for a in rule.actions],
            "tiers": [t.value for t in rule.tiers],
            "decision": rule.decision.value,
            "effective_at": datetime.now().isoformat(),
        }
        
        # Determine targets from rule tiers
        targets = []
        for tier in rule.tiers:
            targets.extend(self._get_policy_targets(tier))
        
        self._policy_service.push_policy(policy_id, policy_data, list(set(targets)))
        change.actions_taken = [f"pushed_policy:{policy_id}"]
        change.processed = True
        change.processed_at = datetime.now()
        
        logger.info(f"Pushed governance change: {rule.rule_id}")
        
        return change
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    def _queue_change(self, change: EnforcementChange) -> None:
        """Queue a change for processing."""
        with self._lock:
            self._pending_changes.append(change)
    
    def _get_policy_targets(self, tier: ModelTier) -> List[str]:
        """Get policy push targets for a tier."""
        # In a real system, this would return actual service endpoints
        tier_targets = {
            ModelTier.COMMUNITY: ["community-gateway"],
            ModelTier.PRO: ["community-gateway", "pro-gateway"],
            ModelTier.ENTERPRISE: ["community-gateway", "pro-gateway", "enterprise-gateway"],
        }
        return tier_targets.get(tier, [])
    
    def process_pending(self) -> int:
        """Process all pending changes. Returns count processed."""
        processed = 0
        
        with self._lock:
            for change in self._pending_changes:
                if change.processed:
                    continue
                
                # Process based on event type
                if change.event == EnforcementEvent.FEDERATED_UPDATE:
                    # Need version for full processing
                    change.processed = True
                    change.processed_at = datetime.now()
                    processed += 1
                elif change.event == EnforcementEvent.DRIFT_DETECTED:
                    change.processed = True
                    change.processed_at = datetime.now()
                    processed += 1
                elif change.event == EnforcementEvent.MODEL_ROLLBACK:
                    self._process_rollback(change)
                    processed += 1
                elif change.event == EnforcementEvent.GOVERNANCE_CHANGE:
                    change.processed = True
                    change.processed_at = datetime.now()
                    processed += 1
            
            # Move processed to history
            newly_processed = [c for c in self._pending_changes if c.processed]
            self._processed_changes.extend(newly_processed)
            self._pending_changes = [c for c in self._pending_changes if not c.processed]
            
            # Trim history
            if len(self._processed_changes) > self._max_history:
                self._processed_changes = self._processed_changes[-self._max_history:]
        
        return processed
    
    def get_status(self) -> Dict[str, Any]:
        """Get enforcement loop status."""
        return {
            "enabled": self._enabled,
            "auto_process": self._auto_process,
            "pending_changes": len(self._pending_changes),
            "processed_changes": len(self._processed_changes),
            "has_model_manager": self._model_manager is not None,
            "has_governance": self._governance is not None,
        }
    
    def get_change_history(
        self,
        event_type: Optional[EnforcementEvent] = None,
        limit: int = 100,
    ) -> List[EnforcementChange]:
        """Get change history."""
        with self._lock:
            history = self._processed_changes
            
            if event_type:
                history = [c for c in history if c.event == event_type]
            
            return history[-limit:]


# =============================================================================
# Factory Functions
# =============================================================================

def create_enforcement_loop(
    model_manager: Optional[FederatedModelManager] = None,
    governance_controller: Optional[GovernanceController] = None,
) -> PolicyEnforcementLoop:
    """Create a policy enforcement loop."""
    return PolicyEnforcementLoop(
        model_manager=model_manager,
        governance_controller=governance_controller,
    )


def create_full_enforcement_loop(
    model_manager: FederatedModelManager,
    governance_controller: GovernanceController,
    policy_service: Optional[PolicyPushService] = None,
    adaptive_controls: Optional[AdaptiveControlsService] = None,
    telemetry_integration: Optional[TelemetryIntegrationService] = None,
) -> PolicyEnforcementLoop:
    """Create a fully configured enforcement loop."""
    return PolicyEnforcementLoop(
        model_manager=model_manager,
        governance_controller=governance_controller,
        policy_service=policy_service,
        adaptive_controls=adaptive_controls,
        telemetry_integration=telemetry_integration,
    )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Enums
    "EnforcementEvent",
    "AdaptiveAction",
    # Protocols
    "PolicyPushService",
    "AdaptiveControlsService",
    "TelemetryIntegrationService",
    # Data Classes
    "EnforcementChange",
    "ThresholdConfig",
    "AdaptiveControlState",
    # Default Implementations
    "DefaultPolicyPushService",
    "DefaultAdaptiveControlsService",
    "DefaultTelemetryIntegrationService",
    # Controller
    "PolicyEnforcementLoop",
    # Factories
    "create_enforcement_loop",
    "create_full_enforcement_loop",
]
