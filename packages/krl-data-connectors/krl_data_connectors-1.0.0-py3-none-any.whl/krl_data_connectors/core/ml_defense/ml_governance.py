# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
ML Governance Policy Engine - Phase 3 Week 20

Enforces ML governance policies across tiers with observability integration.

Key Features:
- Policy-based model access control
- Training data governance
- Model audit logging
- Compliance checks
- Integration with observability spine
"""

from __future__ import annotations

import hashlib
import logging
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from enum import Enum
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Protocol,
    Set,
    Tuple,
    TypeVar,
)

from .federated_model_manager import (
    ModelTier,
    ModelState,
    GovernanceMode,
    ModelVersion,
    DriftMetrics,
    DriftSeverity,
    FederatedModelManager,
    TIER_GOVERNANCE,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================

class PolicyAction(Enum):
    """Actions that can be governed by policy."""
    MODEL_INFERENCE = "model_inference"
    MODEL_TRAIN = "model_train"
    MODEL_UPDATE = "model_update"
    MODEL_ROLLBACK = "model_rollback"
    MODEL_REGISTER = "model_register"
    MODEL_DELETE = "model_delete"
    DATA_ACCESS = "data_access"
    DATA_EXPORT = "data_export"
    FEDERATED_PARTICIPATE = "federated_participate"
    FEDERATED_COORDINATE = "federated_coordinate"


class PolicyDecision(Enum):
    """Policy evaluation decisions."""
    ALLOW = "allow"
    DENY = "deny"
    AUDIT = "audit"         # Allow but log
    WARN = "warn"           # Allow with warning
    REQUIRE_APPROVAL = "require_approval"


class ComplianceStandard(Enum):
    """Compliance standards for ML governance."""
    INTERNAL = "internal"
    SOC2 = "soc2"
    HIPAA = "hipaa"
    GDPR = "gdpr"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"
    NIST = "nist"


class AuditEventType(Enum):
    """Types of audit events for ML operations."""
    MODEL_ACCESSED = "model_accessed"
    MODEL_TRAINED = "model_trained"
    MODEL_UPDATED = "model_updated"
    MODEL_REGISTERED = "model_registered"
    MODEL_DELETED = "model_deleted"
    MODEL_ROLLED_BACK = "model_rolled_back"
    DRIFT_DETECTED = "drift_detected"
    POLICY_EVALUATED = "policy_evaluated"
    POLICY_VIOLATED = "policy_violated"
    FEDERATED_ROUND_STARTED = "federated_round_started"
    FEDERATED_UPDATE_SUBMITTED = "federated_update_submitted"
    FEDERATED_AGGREGATION_COMPLETE = "federated_aggregation_complete"
    DATA_ACCESS_REQUEST = "data_access_request"
    COMPLIANCE_CHECK = "compliance_check"


class DataClassification(Enum):
    """Data classification levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class AuditEvent:
    """
    Audit event for ML governance.
    
    Immutable record of governance-relevant events.
    """
    event_id: str
    event_type: AuditEventType
    timestamp: datetime
    actor_id: str
    actor_tier: ModelTier
    
    # What was accessed/modified
    resource_type: str
    resource_id: str
    
    # Action details
    action: PolicyAction
    decision: PolicyDecision
    
    # Context
    metadata: Dict[str, Any] = field(default_factory=dict)
    compliance_tags: Set[ComplianceStandard] = field(default_factory=set)
    
    # Signature for integrity
    signature: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "actor_id": self.actor_id,
            "actor_tier": self.actor_tier.value,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "action": self.action.value,
            "decision": self.decision.value,
            "metadata": self.metadata,
            "compliance_tags": [t.value for t in self.compliance_tags],
            "signature": self.signature,
        }
    
    def compute_signature(self, secret: str) -> str:
        """Compute HMAC signature for integrity."""
        import hmac
        data = f"{self.event_id}:{self.event_type.value}:{self.timestamp.isoformat()}:{self.actor_id}:{self.resource_id}"
        return hmac.new(secret.encode(), data.encode(), hashlib.sha256).hexdigest()


@dataclass
class PolicyRule:
    """
    A single policy rule.
    
    Defines conditions and resulting action for a policy evaluation.
    """
    rule_id: str
    name: str
    description: str
    
    # Matching conditions
    actions: Set[PolicyAction]
    tiers: Set[ModelTier]
    resource_patterns: List[str] = field(default_factory=list)  # Regex patterns
    
    # Conditions
    conditions: Dict[str, Any] = field(default_factory=dict)
    
    # Result
    decision: PolicyDecision = PolicyDecision.ALLOW
    priority: int = 0  # Higher = evaluated first
    
    # Compliance
    compliance_standards: Set[ComplianceStandard] = field(default_factory=set)
    
    enabled: bool = True


@dataclass
class PolicyEvaluationResult:
    """Result of a policy evaluation."""
    allowed: bool
    decision: PolicyDecision
    matching_rules: List[str]
    reasons: List[str]
    required_actions: List[str] = field(default_factory=list)
    audit_required: bool = False
    evaluated_at: datetime = field(default_factory=datetime.now)


@dataclass
class DataGovernancePolicy:
    """
    Data governance policy for training data.
    
    Controls how data can be used for ML training.
    """
    policy_id: str
    name: str
    
    # Data classification
    allowed_classifications: Set[DataClassification]
    
    # Retention
    max_retention_days: int
    require_anonymization: bool
    
    # Access
    allowed_tiers: Set[ModelTier]
    require_consent: bool
    
    # Compliance
    compliance_standards: Set[ComplianceStandard]
    
    # Audit
    audit_all_access: bool = True


@dataclass
class ModelGovernanceConfig:
    """
    Per-model governance configuration.
    
    Customizes governance rules for specific models.
    """
    model_id: str
    
    # Access control
    min_tier: ModelTier = ModelTier.COMMUNITY
    allowed_actors: Optional[Set[str]] = None  # None = all
    
    # Training restrictions
    require_approval_for_updates: bool = False
    max_training_frequency_hours: int = 24
    
    # Drift handling
    drift_auto_rollback_threshold: DriftSeverity = DriftSeverity.HIGH
    
    # Data requirements
    min_training_samples: int = 100
    data_classification_required: DataClassification = DataClassification.INTERNAL
    
    # Audit
    audit_all_inferences: bool = False
    audit_all_updates: bool = True
    
    # Compliance
    compliance_standards: Set[ComplianceStandard] = field(default_factory=set)


# =============================================================================
# Policy Engine
# =============================================================================

class PolicyEngine:
    """
    Central policy engine for ML governance.
    
    Evaluates policies and enforces governance rules.
    """
    
    def __init__(self):
        self._rules: Dict[str, PolicyRule] = {}
        self._model_configs: Dict[str, ModelGovernanceConfig] = {}
        self._data_policies: Dict[str, DataGovernancePolicy] = {}
        self._lock = threading.RLock()
        
        # Default rules
        self._initialize_default_rules()
    
    def _initialize_default_rules(self) -> None:
        """Set up default governance rules."""
        # Community tier restrictions
        self.add_rule(PolicyRule(
            rule_id="community_no_federated",
            name="Community: No Federated Participation",
            description="Community tier cannot participate in federated learning",
            actions={PolicyAction.FEDERATED_PARTICIPATE, PolicyAction.FEDERATED_COORDINATE},
            tiers={ModelTier.COMMUNITY},
            decision=PolicyDecision.DENY,
            priority=100,
        ))
        
        self.add_rule(PolicyRule(
            rule_id="community_no_train",
            name="Community: No Model Training",
            description="Community tier uses static models only",
            actions={PolicyAction.MODEL_TRAIN, PolicyAction.MODEL_UPDATE},
            tiers={ModelTier.COMMUNITY},
            decision=PolicyDecision.DENY,
            priority=100,
        ))
        
        # Pro tier restrictions
        self.add_rule(PolicyRule(
            rule_id="pro_no_coordinate",
            name="Pro: No Federated Coordination",
            description="Pro tier can participate but not coordinate federated rounds",
            actions={PolicyAction.FEDERATED_COORDINATE},
            tiers={ModelTier.PRO},
            decision=PolicyDecision.DENY,
            priority=100,
        ))
        
        # Audit rules
        self.add_rule(PolicyRule(
            rule_id="audit_model_updates",
            name="Audit: Model Updates",
            description="All model updates require audit logging",
            actions={PolicyAction.MODEL_UPDATE, PolicyAction.MODEL_ROLLBACK},
            tiers={ModelTier.COMMUNITY, ModelTier.PRO, ModelTier.ENTERPRISE},
            decision=PolicyDecision.AUDIT,
            priority=50,
        ))
        
        # Enterprise can do everything
        self.add_rule(PolicyRule(
            rule_id="enterprise_allow_all",
            name="Enterprise: Allow All",
            description="Enterprise tier has full access",
            actions=set(PolicyAction),
            tiers={ModelTier.ENTERPRISE},
            decision=PolicyDecision.ALLOW,
            priority=10,
        ))
    
    def add_rule(self, rule: PolicyRule) -> None:
        """Add a policy rule."""
        with self._lock:
            self._rules[rule.rule_id] = rule
    
    def remove_rule(self, rule_id: str) -> bool:
        """Remove a policy rule."""
        with self._lock:
            if rule_id in self._rules:
                del self._rules[rule_id]
                return True
            return False
    
    def set_model_config(self, config: ModelGovernanceConfig) -> None:
        """Set governance config for a model."""
        with self._lock:
            self._model_configs[config.model_id] = config
    
    def get_model_config(self, model_id: str) -> Optional[ModelGovernanceConfig]:
        """Get governance config for a model."""
        return self._model_configs.get(model_id)
    
    def add_data_policy(self, policy: DataGovernancePolicy) -> None:
        """Add a data governance policy."""
        with self._lock:
            self._data_policies[policy.policy_id] = policy
    
    def evaluate(
        self,
        action: PolicyAction,
        actor_tier: ModelTier,
        resource_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> PolicyEvaluationResult:
        """
        Evaluate a policy request.
        
        Returns whether the action is allowed and any requirements.
        """
        context = context or {}
        matching_rules: List[PolicyRule] = []
        
        with self._lock:
            # Sort by priority (descending)
            sorted_rules = sorted(
                self._rules.values(),
                key=lambda r: r.priority,
                reverse=True
            )
            
            for rule in sorted_rules:
                if not rule.enabled:
                    continue
                
                # Check action match
                if action not in rule.actions:
                    continue
                
                # Check tier match
                if actor_tier not in rule.tiers:
                    continue
                
                # Check resource pattern
                if rule.resource_patterns:
                    import re
                    matched = False
                    for pattern in rule.resource_patterns:
                        if re.match(pattern, resource_id):
                            matched = True
                            break
                    if not matched:
                        continue
                
                # Check conditions
                if not self._evaluate_conditions(rule.conditions, context):
                    continue
                
                matching_rules.append(rule)
        
        # Determine final decision
        if not matching_rules:
            # Default allow
            return PolicyEvaluationResult(
                allowed=True,
                decision=PolicyDecision.ALLOW,
                matching_rules=[],
                reasons=["No matching rules, default allow"],
            )
        
        # Most restrictive wins
        final_rule = matching_rules[0]
        for rule in matching_rules:
            if self._is_more_restrictive(rule.decision, final_rule.decision):
                final_rule = rule
        
        allowed = final_rule.decision in [
            PolicyDecision.ALLOW,
            PolicyDecision.AUDIT,
            PolicyDecision.WARN,
        ]
        
        return PolicyEvaluationResult(
            allowed=allowed,
            decision=final_rule.decision,
            matching_rules=[r.rule_id for r in matching_rules],
            reasons=[f"{final_rule.name}: {final_rule.description}"],
            audit_required=final_rule.decision == PolicyDecision.AUDIT,
            required_actions=["approval"] if final_rule.decision == PolicyDecision.REQUIRE_APPROVAL else [],
        )
    
    def _evaluate_conditions(
        self,
        conditions: Dict[str, Any],
        context: Dict[str, Any],
    ) -> bool:
        """Evaluate rule conditions against context."""
        for key, expected in conditions.items():
            actual = context.get(key)
            
            if isinstance(expected, dict):
                # Complex condition
                op = expected.get("op", "eq")
                value = expected.get("value")
                
                if op == "eq" and actual != value:
                    return False
                elif op == "ne" and actual == value:
                    return False
                elif op == "gt" and not (actual is not None and actual > value):
                    return False
                elif op == "lt" and not (actual is not None and actual < value):
                    return False
                elif op == "in" and actual not in value:
                    return False
                elif op == "contains" and value not in (actual or []):
                    return False
            else:
                # Simple equality
                if actual != expected:
                    return False
        
        return True
    
    def _is_more_restrictive(self, a: PolicyDecision, b: PolicyDecision) -> bool:
        """Check if decision a is more restrictive than b."""
        order = [
            PolicyDecision.ALLOW,
            PolicyDecision.AUDIT,
            PolicyDecision.WARN,
            PolicyDecision.REQUIRE_APPROVAL,
            PolicyDecision.DENY,
        ]
        return order.index(a) > order.index(b)


# =============================================================================
# Audit Logger
# =============================================================================

class AuditLogger:
    """
    Audit logger for ML governance events.
    
    Provides tamper-evident logging with optional signatures.
    """
    
    def __init__(
        self,
        max_events: int = 100000,
        signing_secret: Optional[str] = None,
    ):
        self._events: List[AuditEvent] = []
        self._max_events = max_events
        self._secret = signing_secret
        self._lock = threading.RLock()
        self._sinks: List[Callable[[AuditEvent], None]] = []
        self._event_counter = 0
    
    def log(
        self,
        event_type: AuditEventType,
        actor_id: str,
        actor_tier: ModelTier,
        resource_type: str,
        resource_id: str,
        action: PolicyAction,
        decision: PolicyDecision,
        metadata: Optional[Dict[str, Any]] = None,
        compliance_tags: Optional[Set[ComplianceStandard]] = None,
    ) -> AuditEvent:
        """Log an audit event."""
        with self._lock:
            self._event_counter += 1
            event_id = f"audit-{self._event_counter:08d}"
            
            event = AuditEvent(
                event_id=event_id,
                event_type=event_type,
                timestamp=datetime.now(),
                actor_id=actor_id,
                actor_tier=actor_tier,
                resource_type=resource_type,
                resource_id=resource_id,
                action=action,
                decision=decision,
                metadata=metadata or {},
                compliance_tags=compliance_tags or set(),
            )
            
            # Sign if secret provided
            if self._secret:
                event.signature = event.compute_signature(self._secret)
            
            # Store
            self._events.append(event)
            
            # Trim if needed
            if len(self._events) > self._max_events:
                self._events = self._events[-self._max_events:]
            
            # Notify sinks
            for sink in self._sinks:
                try:
                    sink(event)
                except Exception as e:
                    logger.warning(f"Audit sink error: {e}")
            
            return event
    
    def add_sink(self, sink: Callable[[AuditEvent], None]) -> None:
        """Add an audit event sink."""
        self._sinks.append(sink)
    
    def query(
        self,
        event_type: Optional[AuditEventType] = None,
        actor_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        action: Optional[PolicyAction] = None,
        since: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[AuditEvent]:
        """Query audit events."""
        with self._lock:
            results = []
            
            for event in reversed(self._events):
                if event_type and event.event_type != event_type:
                    continue
                if actor_id and event.actor_id != actor_id:
                    continue
                if resource_id and event.resource_id != resource_id:
                    continue
                if action and event.action != action:
                    continue
                if since and event.timestamp < since:
                    continue
                
                results.append(event)
                
                if len(results) >= limit:
                    break
            
            return results
    
    def verify_event(self, event: AuditEvent) -> bool:
        """Verify event signature integrity."""
        if not self._secret or not event.signature:
            return True  # No signature to verify
        
        expected = event.compute_signature(self._secret)
        return event.signature == expected
    
    def export_events(
        self,
        since: Optional[datetime] = None,
        format: str = "json",
    ) -> str:
        """Export audit events."""
        import json
        
        events = self.query(since=since, limit=len(self._events))
        
        if format == "json":
            return json.dumps([e.to_dict() for e in events], indent=2)
        elif format == "csv":
            lines = ["event_id,event_type,timestamp,actor_id,resource_id,action,decision"]
            for e in events:
                lines.append(
                    f"{e.event_id},{e.event_type.value},{e.timestamp.isoformat()},"
                    f"{e.actor_id},{e.resource_id},{e.action.value},{e.decision.value}"
                )
            return "\n".join(lines)
        else:
            return str([e.to_dict() for e in events])


# =============================================================================
# Governance Controller
# =============================================================================

class GovernanceController:
    """
    High-level governance controller.
    
    Integrates policy engine, audit logging, and model manager.
    """
    
    def __init__(
        self,
        model_manager: Optional[FederatedModelManager] = None,
        signing_secret: Optional[str] = None,
    ):
        self._policy_engine = PolicyEngine()
        self._audit_logger = AuditLogger(signing_secret=signing_secret)
        self._model_manager = model_manager
        
        # Register for model manager events if provided
        if self._model_manager:
            self._model_manager.on_version_change(self._on_model_version_change)
            self._model_manager.on_drift_detected(self._on_drift_detected)
            self._model_manager.on_rollback(self._on_rollback)
    
    @property
    def policy_engine(self) -> PolicyEngine:
        return self._policy_engine
    
    @property
    def audit_logger(self) -> AuditLogger:
        return self._audit_logger
    
    def check_and_log(
        self,
        action: PolicyAction,
        actor_id: str,
        actor_tier: ModelTier,
        resource_type: str,
        resource_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> PolicyEvaluationResult:
        """
        Check policy and log the evaluation.
        
        Combines policy evaluation with audit logging.
        """
        # Evaluate policy
        result = self._policy_engine.evaluate(
            action=action,
            actor_tier=actor_tier,
            resource_id=resource_id,
            context=context,
        )
        
        # Determine audit event type
        if result.allowed:
            event_type = AuditEventType.POLICY_EVALUATED
        else:
            event_type = AuditEventType.POLICY_VIOLATED
        
        # Log
        self._audit_logger.log(
            event_type=event_type,
            actor_id=actor_id,
            actor_tier=actor_tier,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            decision=result.decision,
            metadata={
                "matching_rules": result.matching_rules,
                "reasons": result.reasons,
                "context": context,
            },
        )
        
        return result
    
    def log_model_access(
        self,
        actor_id: str,
        actor_tier: ModelTier,
        model_id: str,
        access_type: str = "inference",
    ) -> None:
        """Log model access for audit."""
        self._audit_logger.log(
            event_type=AuditEventType.MODEL_ACCESSED,
            actor_id=actor_id,
            actor_tier=actor_tier,
            resource_type="model",
            resource_id=model_id,
            action=PolicyAction.MODEL_INFERENCE,
            decision=PolicyDecision.ALLOW,
            metadata={"access_type": access_type},
        )
    
    def log_data_access(
        self,
        actor_id: str,
        actor_tier: ModelTier,
        dataset_id: str,
        purpose: str,
        classification: DataClassification,
    ) -> None:
        """Log training data access for audit."""
        self._audit_logger.log(
            event_type=AuditEventType.DATA_ACCESS_REQUEST,
            actor_id=actor_id,
            actor_tier=actor_tier,
            resource_type="dataset",
            resource_id=dataset_id,
            action=PolicyAction.DATA_ACCESS,
            decision=PolicyDecision.ALLOW,
            metadata={
                "purpose": purpose,
                "classification": classification.value,
            },
        )
    
    def run_compliance_check(
        self,
        standard: ComplianceStandard,
    ) -> Dict[str, Any]:
        """
        Run a compliance check against a standard.
        
        Returns compliance status and any violations.
        """
        violations: List[Dict[str, Any]] = []
        checks_passed = 0
        checks_failed = 0
        
        # Check model governance configs
        for model_id, config in self._policy_engine._model_configs.items():
            if standard not in config.compliance_standards:
                continue
            
            # Check if model has required settings for compliance
            if standard == ComplianceStandard.HIPAA:
                if not config.audit_all_inferences:
                    violations.append({
                        "model_id": model_id,
                        "check": "audit_all_inferences",
                        "message": "HIPAA requires audit logging of all inferences",
                    })
                    checks_failed += 1
                else:
                    checks_passed += 1
                
                if config.data_classification_required not in [
                    DataClassification.CONFIDENTIAL,
                    DataClassification.RESTRICTED,
                ]:
                    violations.append({
                        "model_id": model_id,
                        "check": "data_classification",
                        "message": "HIPAA requires confidential or restricted data classification",
                    })
                    checks_failed += 1
                else:
                    checks_passed += 1
        
        # Log compliance check
        self._audit_logger.log(
            event_type=AuditEventType.COMPLIANCE_CHECK,
            actor_id="system",
            actor_tier=ModelTier.ENTERPRISE,
            resource_type="compliance",
            resource_id=standard.value,
            action=PolicyAction.DATA_ACCESS,
            decision=PolicyDecision.AUDIT,
            metadata={
                "standard": standard.value,
                "passed": checks_passed,
                "failed": checks_failed,
                "violations": len(violations),
            },
            compliance_tags={standard},
        )
        
        return {
            "standard": standard.value,
            "compliant": len(violations) == 0,
            "checks_passed": checks_passed,
            "checks_failed": checks_failed,
            "violations": violations,
            "checked_at": datetime.now().isoformat(),
        }
    
    def _on_model_version_change(
        self,
        model_id: str,
        version: ModelVersion,
    ) -> None:
        """Handle model version changes from manager."""
        tier = self._model_manager.tier if self._model_manager else ModelTier.COMMUNITY
        
        if version.state == ModelState.ACTIVE:
            event_type = AuditEventType.MODEL_UPDATED
        else:
            event_type = AuditEventType.MODEL_REGISTERED
        
        self._audit_logger.log(
            event_type=event_type,
            actor_id=self._model_manager.participant_id if self._model_manager else "system",
            actor_tier=tier,
            resource_type="model",
            resource_id=model_id,
            action=PolicyAction.MODEL_UPDATE,
            decision=PolicyDecision.ALLOW,
            metadata={
                "version": str(version.version),
                "state": version.state.value,
            },
        )
    
    def _on_drift_detected(
        self,
        model_id: str,
        drift: DriftMetrics,
    ) -> None:
        """Handle drift detection from manager."""
        tier = self._model_manager.tier if self._model_manager else ModelTier.COMMUNITY
        
        self._audit_logger.log(
            event_type=AuditEventType.DRIFT_DETECTED,
            actor_id="system",
            actor_tier=tier,
            resource_type="model",
            resource_id=model_id,
            action=PolicyAction.MODEL_INFERENCE,
            decision=PolicyDecision.WARN,
            metadata={
                "severity": drift.severity.value,
                "data_drift": drift.data_drift_score,
                "concept_drift": drift.concept_drift_score,
            },
        )
    
    def _on_rollback(
        self,
        model_id: str,
        from_version: str,
        to_version: str,
    ) -> None:
        """Handle rollback from manager."""
        tier = self._model_manager.tier if self._model_manager else ModelTier.COMMUNITY
        
        self._audit_logger.log(
            event_type=AuditEventType.MODEL_ROLLED_BACK,
            actor_id="system",
            actor_tier=tier,
            resource_type="model",
            resource_id=model_id,
            action=PolicyAction.MODEL_ROLLBACK,
            decision=PolicyDecision.ALLOW,
            metadata={
                "from_version": from_version,
                "to_version": to_version,
            },
        )
    
    def get_governance_summary(self) -> Dict[str, Any]:
        """Get governance summary statistics."""
        recent_events = self._audit_logger.query(
            since=datetime.now() - timedelta(hours=24),
            limit=10000,
        )
        
        # Count by type
        by_type: Dict[str, int] = {}
        by_decision: Dict[str, int] = {}
        violations = 0
        
        for event in recent_events:
            by_type[event.event_type.value] = by_type.get(event.event_type.value, 0) + 1
            by_decision[event.decision.value] = by_decision.get(event.decision.value, 0) + 1
            if event.event_type == AuditEventType.POLICY_VIOLATED:
                violations += 1
        
        return {
            "period": "last_24_hours",
            "total_events": len(recent_events),
            "by_event_type": by_type,
            "by_decision": by_decision,
            "violations": violations,
            "model_configs": len(self._policy_engine._model_configs),
            "policy_rules": len(self._policy_engine._rules),
        }


# =============================================================================
# Factory Functions
# =============================================================================

def create_governance_controller(
    model_manager: Optional[FederatedModelManager] = None,
    signing_secret: Optional[str] = None,
) -> GovernanceController:
    """Create a governance controller."""
    return GovernanceController(
        model_manager=model_manager,
        signing_secret=signing_secret,
    )


def create_hipaa_compliant_model_config(
    model_id: str,
    min_tier: ModelTier = ModelTier.PRO,
) -> ModelGovernanceConfig:
    """Create a HIPAA-compliant model governance config."""
    return ModelGovernanceConfig(
        model_id=model_id,
        min_tier=min_tier,
        require_approval_for_updates=True,
        audit_all_inferences=True,
        audit_all_updates=True,
        data_classification_required=DataClassification.CONFIDENTIAL,
        compliance_standards={ComplianceStandard.HIPAA},
    )


def create_gdpr_compliant_model_config(
    model_id: str,
    min_tier: ModelTier = ModelTier.PRO,
) -> ModelGovernanceConfig:
    """Create a GDPR-compliant model governance config."""
    return ModelGovernanceConfig(
        model_id=model_id,
        min_tier=min_tier,
        require_approval_for_updates=True,
        audit_all_inferences=True,
        audit_all_updates=True,
        data_classification_required=DataClassification.CONFIDENTIAL,
        compliance_standards={ComplianceStandard.GDPR},
    )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Enums
    "PolicyAction",
    "PolicyDecision",
    "ComplianceStandard",
    "AuditEventType",
    "DataClassification",
    # Data Classes
    "AuditEvent",
    "PolicyRule",
    "PolicyEvaluationResult",
    "DataGovernancePolicy",
    "ModelGovernanceConfig",
    # Classes
    "PolicyEngine",
    "AuditLogger",
    "GovernanceController",
    # Factories
    "create_governance_controller",
    "create_hipaa_compliant_model_config",
    "create_gdpr_compliant_model_config",
]
