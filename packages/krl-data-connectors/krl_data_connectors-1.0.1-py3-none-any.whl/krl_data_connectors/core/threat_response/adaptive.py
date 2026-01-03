"""
Adaptive Response Engine - Phase 2 Week 14

Dynamic threat response with graduated escalation and policy adjustment.

Copyright 2025 KR-Labs. All rights reserved.
"""

import json
import logging
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Threat level classifications."""
    
    NONE = 0
    LOW = 1
    ELEVATED = 2
    HIGH = 3
    SEVERE = 4
    CRITICAL = 5


class ResponseAction(Enum):
    """Types of response actions."""
    
    LOG = "log"
    ALERT = "alert"
    THROTTLE = "throttle"
    CHALLENGE = "challenge"
    RESTRICT = "restrict"
    SUSPEND = "suspend"
    REVOKE = "revoke"
    BLOCK = "block"
    QUARANTINE = "quarantine"
    ESCALATE = "escalate"


class PolicyScope(Enum):
    """Scope of policy application."""
    
    USER = "user"
    LICENSE = "license"
    SESSION = "session"
    IP = "ip"
    ORGANIZATION = "organization"
    GLOBAL = "global"


@dataclass
class PolicyRule:
    """Rule within a response policy."""
    
    id: str = field(default_factory=lambda: f"rule_{uuid.uuid4().hex[:8]}")
    name: str = ""
    description: str = ""
    condition: str = ""  # Expression to evaluate
    threat_levels: List[ThreatLevel] = field(default_factory=list)
    actions: List[ResponseAction] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    enabled: bool = True
    cooldown_seconds: int = 0
    max_triggers_per_hour: int = 0
    
    _last_triggered: Optional[datetime] = field(default=None, repr=False)
    _trigger_count: int = field(default=0, repr=False)
    _trigger_reset_time: Optional[datetime] = field(default=None, repr=False)
    
    def can_trigger(self) -> bool:
        """Check if rule can be triggered."""
        if not self.enabled:
            return False
        
        now = datetime.now()
        
        # Check cooldown
        if self.cooldown_seconds > 0 and self._last_triggered:
            cooldown_end = self._last_triggered + timedelta(seconds=self.cooldown_seconds)
            if now < cooldown_end:
                return False
        
        # Check rate limit
        if self.max_triggers_per_hour > 0:
            if self._trigger_reset_time is None or now > self._trigger_reset_time:
                self._trigger_count = 0
                self._trigger_reset_time = now + timedelta(hours=1)
            
            if self._trigger_count >= self.max_triggers_per_hour:
                return False
        
        return True
    
    def record_trigger(self) -> None:
        """Record that the rule was triggered."""
        self._last_triggered = datetime.now()
        self._trigger_count += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "condition": self.condition,
            "threat_levels": [t.value for t in self.threat_levels],
            "actions": [a.value for a in self.actions],
            "parameters": self.parameters,
            "priority": self.priority,
            "enabled": self.enabled,
            "cooldown_seconds": self.cooldown_seconds,
            "max_triggers_per_hour": self.max_triggers_per_hour,
        }


@dataclass
class ResponsePolicy:
    """Response policy containing rules."""
    
    id: str = field(default_factory=lambda: f"policy_{uuid.uuid4().hex[:8]}")
    name: str = ""
    description: str = ""
    scope: PolicyScope = PolicyScope.GLOBAL
    rules: List[PolicyRule] = field(default_factory=list)
    default_actions: List[ResponseAction] = field(default_factory=list)
    escalation_chain: List[str] = field(default_factory=list)  # User/group IDs
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_rule(self, rule: PolicyRule) -> None:
        """Add a rule to the policy."""
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.priority, reverse=True)
        self.updated_at = datetime.now()
    
    def remove_rule(self, rule_id: str) -> bool:
        """Remove a rule from the policy."""
        for i, rule in enumerate(self.rules):
            if rule.id == rule_id:
                self.rules.pop(i)
                self.updated_at = datetime.now()
                return True
        return False
    
    def get_matching_rules(self, threat_level: ThreatLevel) -> List[PolicyRule]:
        """Get rules that match the given threat level."""
        return [
            rule for rule in self.rules
            if rule.enabled and (
                not rule.threat_levels or
                threat_level in rule.threat_levels
            )
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "scope": self.scope.value,
            "rules": [r.to_dict() for r in self.rules],
            "default_actions": [a.value for a in self.default_actions],
            "escalation_chain": self.escalation_chain,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class EscalationTrigger:
    """Trigger for escalation."""
    
    id: str = field(default_factory=lambda: f"esc_{uuid.uuid4().hex[:8]}")
    name: str = ""
    condition: str = ""
    from_level: ThreatLevel = ThreatLevel.NONE
    to_level: ThreatLevel = ThreatLevel.LOW
    threshold_count: int = 1
    threshold_window_seconds: int = 3600
    notification_targets: List[str] = field(default_factory=list)
    enabled: bool = True
    
    _event_times: List[datetime] = field(default_factory=list, repr=False)
    
    def record_event(self) -> bool:
        """Record an event and check if escalation threshold is met."""
        now = datetime.now()
        
        # Add current event
        self._event_times.append(now)
        
        # Remove old events outside window
        cutoff = now - timedelta(seconds=self.threshold_window_seconds)
        self._event_times = [t for t in self._event_times if t > cutoff]
        
        # Check if threshold is met
        return len(self._event_times) >= self.threshold_count
    
    def reset(self) -> None:
        """Reset event counter."""
        self._event_times.clear()


@dataclass
class AdaptiveDecision:
    """Decision made by the adaptive response engine."""
    
    id: str = field(default_factory=lambda: f"decision_{uuid.uuid4().hex[:12]}")
    timestamp: datetime = field(default_factory=datetime.now)
    entity_id: str = ""
    entity_type: str = ""
    threat_level: ThreatLevel = ThreatLevel.NONE
    previous_level: ThreatLevel = ThreatLevel.NONE
    actions: List[ResponseAction] = field(default_factory=list)
    triggered_rules: List[str] = field(default_factory=list)
    rationale: str = ""
    confidence: float = 0.0
    auto_remediation: bool = False
    requires_approval: bool = False
    approved: bool = False
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    executed: bool = False
    executed_at: Optional[datetime] = None
    result: Optional[str] = None
    
    def approve(self, user: str) -> None:
        """Approve the decision."""
        self.approved = True
        self.approved_by = user
        self.approved_at = datetime.now()
    
    def reject(self, user: str, reason: str) -> None:
        """Reject the decision."""
        self.approved = False
        self.approved_by = user
        self.approved_at = datetime.now()
        self.result = f"Rejected: {reason}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "threat_level": self.threat_level.value,
            "previous_level": self.previous_level.value,
            "actions": [a.value for a in self.actions],
            "triggered_rules": self.triggered_rules,
            "rationale": self.rationale,
            "confidence": self.confidence,
            "auto_remediation": self.auto_remediation,
            "requires_approval": self.requires_approval,
            "approved": self.approved,
            "approved_by": self.approved_by,
            "executed": self.executed,
            "result": self.result,
        }


@dataclass
class ResponseConfig:
    """Configuration for adaptive response engine."""
    
    enabled: bool = True
    auto_respond: bool = True
    require_approval_above: ThreatLevel = ThreatLevel.HIGH
    default_escalation_delay: int = 300  # seconds
    max_escalation_level: ThreatLevel = ThreatLevel.CRITICAL
    enable_auto_deescalation: bool = True
    deescalation_cooldown: int = 3600  # seconds
    log_all_decisions: bool = True
    notify_on_escalation: bool = True
    action_timeout: int = 30  # seconds


class AdaptiveResponseEngine:
    """
    Adaptive Response Engine.
    
    Dynamically adjusts threat response based on threat levels,
    policies, and behavioral patterns.
    """
    
    def __init__(self, config: Optional[ResponseConfig] = None):
        self.config = config or ResponseConfig()
        self.policies: Dict[str, ResponsePolicy] = {}
        self.escalation_triggers: Dict[str, EscalationTrigger] = {}
        self.entity_threat_levels: Dict[str, ThreatLevel] = {}
        self.decisions: Dict[str, AdaptiveDecision] = {}
        self.action_handlers: Dict[ResponseAction, Callable] = {}
        self._subscribers: List[Callable[[AdaptiveDecision], None]] = []
        self._lock = threading.Lock()
        
        # Initialize default policies
        self._init_default_policies()
        
        # Register default action handlers
        self._register_default_handlers()
    
    def _init_default_policies(self) -> None:
        """Initialize default response policies."""
        # License abuse policy
        license_policy = ResponsePolicy(
            id="policy_license_abuse",
            name="License Abuse Response",
            scope=PolicyScope.LICENSE,
        )
        license_policy.add_rule(PolicyRule(
            name="Rate limit on suspicious activity",
            threat_levels=[ThreatLevel.ELEVATED],
            actions=[ResponseAction.THROTTLE, ResponseAction.LOG],
            parameters={"rate_limit_factor": 0.5},
        ))
        license_policy.add_rule(PolicyRule(
            name="Challenge on high threat",
            threat_levels=[ThreatLevel.HIGH],
            actions=[ResponseAction.CHALLENGE, ResponseAction.ALERT],
            parameters={"challenge_type": "captcha"},
        ))
        license_policy.add_rule(PolicyRule(
            name="Suspend on severe threat",
            threat_levels=[ThreatLevel.SEVERE, ThreatLevel.CRITICAL],
            actions=[ResponseAction.SUSPEND, ResponseAction.ESCALATE],
            parameters={"suspension_hours": 24},
        ))
        self.add_policy(license_policy)
        
        # Authentication policy
        auth_policy = ResponsePolicy(
            id="policy_auth",
            name="Authentication Threat Response",
            scope=PolicyScope.USER,
        )
        auth_policy.add_rule(PolicyRule(
            name="Log failed attempts",
            threat_levels=[ThreatLevel.LOW],
            actions=[ResponseAction.LOG],
        ))
        auth_policy.add_rule(PolicyRule(
            name="Restrict on multiple failures",
            threat_levels=[ThreatLevel.ELEVATED, ThreatLevel.HIGH],
            actions=[ResponseAction.RESTRICT, ResponseAction.CHALLENGE],
            parameters={"lockout_minutes": 15},
        ))
        auth_policy.add_rule(PolicyRule(
            name="Block on brute force",
            threat_levels=[ThreatLevel.SEVERE, ThreatLevel.CRITICAL],
            actions=[ResponseAction.BLOCK, ResponseAction.ALERT],
            parameters={"block_hours": 24},
        ))
        self.add_policy(auth_policy)
    
    def _register_default_handlers(self) -> None:
        """Register default action handlers."""
        self.action_handlers[ResponseAction.LOG] = self._handle_log
        self.action_handlers[ResponseAction.ALERT] = self._handle_alert
        self.action_handlers[ResponseAction.THROTTLE] = self._handle_throttle
        self.action_handlers[ResponseAction.CHALLENGE] = self._handle_challenge
        self.action_handlers[ResponseAction.RESTRICT] = self._handle_restrict
        self.action_handlers[ResponseAction.SUSPEND] = self._handle_suspend
        self.action_handlers[ResponseAction.REVOKE] = self._handle_revoke
        self.action_handlers[ResponseAction.BLOCK] = self._handle_block
        self.action_handlers[ResponseAction.QUARANTINE] = self._handle_quarantine
        self.action_handlers[ResponseAction.ESCALATE] = self._handle_escalate
    
    def add_policy(self, policy: ResponsePolicy) -> None:
        """Add a response policy."""
        self.policies[policy.id] = policy
        logger.info(f"Added response policy: {policy.name}")
    
    def remove_policy(self, policy_id: str) -> bool:
        """Remove a response policy."""
        if policy_id in self.policies:
            del self.policies[policy_id]
            return True
        return False
    
    def get_policy(self, policy_id: str) -> Optional[ResponsePolicy]:
        """Get a policy by ID."""
        return self.policies.get(policy_id)
    
    def add_escalation_trigger(self, trigger: EscalationTrigger) -> None:
        """Add an escalation trigger."""
        self.escalation_triggers[trigger.id] = trigger
    
    def register_action_handler(
        self,
        action: ResponseAction,
        handler: Callable[[str, str, Dict[str, Any]], bool],
    ) -> None:
        """Register a custom action handler."""
        self.action_handlers[action] = handler
    
    def assess_threat_level(
        self,
        entity_id: str,
        entity_type: str,
        indicators: Dict[str, Any],
    ) -> ThreatLevel:
        """Assess the threat level for an entity based on indicators."""
        threat_score = indicators.get("threat_score", 0)
        
        # Map score to threat level
        if threat_score >= 90:
            return ThreatLevel.CRITICAL
        elif threat_score >= 75:
            return ThreatLevel.SEVERE
        elif threat_score >= 60:
            return ThreatLevel.HIGH
        elif threat_score >= 40:
            return ThreatLevel.ELEVATED
        elif threat_score >= 20:
            return ThreatLevel.LOW
        else:
            return ThreatLevel.NONE
    
    def update_threat_level(
        self,
        entity_id: str,
        entity_type: str,
        new_level: ThreatLevel,
        reason: str = "",
    ) -> AdaptiveDecision:
        """Update the threat level for an entity and determine response."""
        with self._lock:
            # Get previous level
            key = f"{entity_type}:{entity_id}"
            previous_level = self.entity_threat_levels.get(key, ThreatLevel.NONE)
            
            # Update level
            self.entity_threat_levels[key] = new_level
        
        # Determine response
        decision = self.determine_response(
            entity_id=entity_id,
            entity_type=entity_type,
            threat_level=new_level,
            previous_level=previous_level,
            reason=reason,
        )
        
        # Check if auto-execution is appropriate
        if self.config.auto_respond and not decision.requires_approval:
            self.execute_decision(decision)
        
        return decision
    
    def determine_response(
        self,
        entity_id: str,
        entity_type: str,
        threat_level: ThreatLevel,
        previous_level: ThreatLevel = ThreatLevel.NONE,
        reason: str = "",
    ) -> AdaptiveDecision:
        """Determine the appropriate response for a threat."""
        decision = AdaptiveDecision(
            entity_id=entity_id,
            entity_type=entity_type,
            threat_level=threat_level,
            previous_level=previous_level,
            rationale=reason,
        )
        
        # Find applicable policies
        scope = self._entity_type_to_scope(entity_type)
        applicable_policies = [
            p for p in self.policies.values()
            if p.enabled and p.scope in [scope, PolicyScope.GLOBAL]
        ]
        
        # Collect actions from matching rules
        actions_set: Set[ResponseAction] = set()
        
        for policy in applicable_policies:
            matching_rules = policy.get_matching_rules(threat_level)
            
            for rule in matching_rules:
                if rule.can_trigger():
                    # Evaluate rule condition if present
                    if rule.condition:
                        # Simple condition evaluation (could be extended)
                        try:
                            if not self._evaluate_condition(rule.condition, {
                                "threat_level": threat_level.value,
                                "entity_id": entity_id,
                                "entity_type": entity_type,
                            }):
                                continue
                        except Exception:
                            continue
                    
                    actions_set.update(rule.actions)
                    decision.triggered_rules.append(rule.id)
                    rule.record_trigger()
        
        decision.actions = list(actions_set)
        
        # Determine if approval is required
        if threat_level.value >= self.config.require_approval_above.value:
            decision.requires_approval = True
        
        # Calculate confidence based on threat level change
        if threat_level.value > previous_level.value:
            decision.confidence = min(1.0, 0.5 + (threat_level.value - previous_level.value) * 0.1)
        else:
            decision.confidence = 0.7
        
        # Store decision
        self.decisions[decision.id] = decision
        
        # Notify subscribers
        for subscriber in self._subscribers:
            try:
                subscriber(decision)
            except Exception as e:
                logger.error(f"Error notifying subscriber: {e}")
        
        return decision
    
    def execute_decision(self, decision: AdaptiveDecision) -> bool:
        """Execute a response decision."""
        if decision.requires_approval and not decision.approved:
            logger.warning(f"Decision {decision.id} requires approval before execution")
            return False
        
        if decision.executed:
            logger.warning(f"Decision {decision.id} already executed")
            return False
        
        success = True
        results = []
        
        for action in decision.actions:
            handler = self.action_handlers.get(action)
            if handler:
                try:
                    result = handler(
                        decision.entity_id,
                        decision.entity_type,
                        {"threat_level": decision.threat_level},
                    )
                    results.append(f"{action.value}: {'success' if result else 'failed'}")
                    if not result:
                        success = False
                except Exception as e:
                    logger.error(f"Error executing action {action.value}: {e}")
                    results.append(f"{action.value}: error - {str(e)}")
                    success = False
            else:
                logger.warning(f"No handler for action: {action.value}")
        
        decision.executed = True
        decision.executed_at = datetime.now()
        decision.result = "; ".join(results)
        
        return success
    
    def approve_decision(self, decision_id: str, user: str) -> bool:
        """Approve a pending decision."""
        decision = self.decisions.get(decision_id)
        if not decision:
            return False
        
        decision.approve(user)
        
        if self.config.auto_respond:
            self.execute_decision(decision)
        
        return True
    
    def reject_decision(self, decision_id: str, user: str, reason: str) -> bool:
        """Reject a pending decision."""
        decision = self.decisions.get(decision_id)
        if not decision:
            return False
        
        decision.reject(user, reason)
        return True
    
    def get_entity_threat_level(
        self,
        entity_id: str,
        entity_type: str,
    ) -> ThreatLevel:
        """Get the current threat level for an entity."""
        key = f"{entity_type}:{entity_id}"
        return self.entity_threat_levels.get(key, ThreatLevel.NONE)
    
    def deescalate(
        self,
        entity_id: str,
        entity_type: str,
        levels: int = 1,
        reason: str = "",
    ) -> Optional[AdaptiveDecision]:
        """Manually deescalate threat level."""
        key = f"{entity_type}:{entity_id}"
        current_level = self.entity_threat_levels.get(key, ThreatLevel.NONE)
        
        if current_level == ThreatLevel.NONE:
            return None
        
        new_level_value = max(0, current_level.value - levels)
        new_level = ThreatLevel(new_level_value)
        
        return self.update_threat_level(
            entity_id=entity_id,
            entity_type=entity_type,
            new_level=new_level,
            reason=f"Manual deescalation: {reason}",
        )
    
    def get_pending_decisions(self) -> List[AdaptiveDecision]:
        """Get decisions awaiting approval."""
        return [
            d for d in self.decisions.values()
            if d.requires_approval and not d.approved and d.approved_by is None
        ]
    
    def get_decisions(
        self,
        entity_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[AdaptiveDecision]:
        """Get recent decisions."""
        decisions = list(self.decisions.values())
        
        if entity_id:
            decisions = [d for d in decisions if d.entity_id == entity_id]
        if entity_type:
            decisions = [d for d in decisions if d.entity_type == entity_type]
        
        decisions.sort(key=lambda d: d.timestamp, reverse=True)
        return decisions[:limit]
    
    def subscribe(self, callback: Callable[[AdaptiveDecision], None]) -> None:
        """Subscribe to decision notifications."""
        self._subscribers.append(callback)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get response statistics."""
        total_decisions = len(self.decisions)
        executed = sum(1 for d in self.decisions.values() if d.executed)
        pending = sum(1 for d in self.decisions.values() if d.requires_approval and not d.approved)
        
        by_threat_level: Dict[int, int] = {}
        by_action: Dict[str, int] = {}
        
        for decision in self.decisions.values():
            level = decision.threat_level.value
            by_threat_level[level] = by_threat_level.get(level, 0) + 1
            
            for action in decision.actions:
                by_action[action.value] = by_action.get(action.value, 0) + 1
        
        return {
            "total_decisions": total_decisions,
            "executed": executed,
            "pending_approval": pending,
            "by_threat_level": by_threat_level,
            "by_action": by_action,
            "active_policies": len([p for p in self.policies.values() if p.enabled]),
            "entities_monitored": len(self.entity_threat_levels),
        }
    
    def _entity_type_to_scope(self, entity_type: str) -> PolicyScope:
        """Map entity type to policy scope."""
        mapping = {
            "user": PolicyScope.USER,
            "license": PolicyScope.LICENSE,
            "session": PolicyScope.SESSION,
            "ip": PolicyScope.IP,
            "organization": PolicyScope.ORGANIZATION,
        }
        return mapping.get(entity_type, PolicyScope.GLOBAL)
    
    def _evaluate_condition(
        self,
        condition: str,
        context: Dict[str, Any],
    ) -> bool:
        """Evaluate a simple condition expression."""
        # Simple evaluation - could be extended with a proper expression parser
        try:
            # Replace variables with values
            expr = condition
            for key, value in context.items():
                expr = expr.replace(f"${key}", str(value))
            
            # Simple comparisons
            if ">=" in expr:
                parts = expr.split(">=")
                return float(parts[0].strip()) >= float(parts[1].strip())
            elif "<=" in expr:
                parts = expr.split("<=")
                return float(parts[0].strip()) <= float(parts[1].strip())
            elif ">" in expr:
                parts = expr.split(">")
                return float(parts[0].strip()) > float(parts[1].strip())
            elif "<" in expr:
                parts = expr.split("<")
                return float(parts[0].strip()) < float(parts[1].strip())
            elif "==" in expr:
                parts = expr.split("==")
                return parts[0].strip() == parts[1].strip()
            
            return True
        except Exception:
            return True
    
    # Default action handlers
    def _handle_log(self, entity_id: str, entity_type: str, params: Dict) -> bool:
        """Handle LOG action."""
        logger.info(f"Threat response logged for {entity_type}:{entity_id}")
        return True
    
    def _handle_alert(self, entity_id: str, entity_type: str, params: Dict) -> bool:
        """Handle ALERT action."""
        logger.warning(f"ALERT: Threat detected for {entity_type}:{entity_id}")
        return True
    
    def _handle_throttle(self, entity_id: str, entity_type: str, params: Dict) -> bool:
        """Handle THROTTLE action."""
        logger.info(f"Throttling {entity_type}:{entity_id}")
        return True
    
    def _handle_challenge(self, entity_id: str, entity_type: str, params: Dict) -> bool:
        """Handle CHALLENGE action."""
        logger.info(f"Challenging {entity_type}:{entity_id}")
        return True
    
    def _handle_restrict(self, entity_id: str, entity_type: str, params: Dict) -> bool:
        """Handle RESTRICT action."""
        logger.info(f"Restricting {entity_type}:{entity_id}")
        return True
    
    def _handle_suspend(self, entity_id: str, entity_type: str, params: Dict) -> bool:
        """Handle SUSPEND action."""
        logger.warning(f"Suspending {entity_type}:{entity_id}")
        return True
    
    def _handle_revoke(self, entity_id: str, entity_type: str, params: Dict) -> bool:
        """Handle REVOKE action."""
        logger.warning(f"Revoking access for {entity_type}:{entity_id}")
        return True
    
    def _handle_block(self, entity_id: str, entity_type: str, params: Dict) -> bool:
        """Handle BLOCK action."""
        logger.warning(f"Blocking {entity_type}:{entity_id}")
        return True
    
    def _handle_quarantine(self, entity_id: str, entity_type: str, params: Dict) -> bool:
        """Handle QUARANTINE action."""
        logger.warning(f"Quarantining {entity_type}:{entity_id}")
        return True
    
    def _handle_escalate(self, entity_id: str, entity_type: str, params: Dict) -> bool:
        """Handle ESCALATE action."""
        logger.warning(f"Escalating threat for {entity_type}:{entity_id}")
        return True
