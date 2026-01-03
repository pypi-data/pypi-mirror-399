"""
Quarantine and Isolation Module for KRL Data Connectors.

Implements license isolation, feature lockdown, and controlled
degradation for security threat containment.

Features:
- License quarantine management
- Feature lockdown mechanisms
- Graceful degradation
- Isolation policy enforcement
"""

import hashlib
import json
import logging
import secrets
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from uuid import uuid4

logger = logging.getLogger(__name__)


class QuarantineStatus(Enum):
    """Status of quarantine."""
    
    ACTIVE = "active"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    RELEASED = "released"
    EXPIRED = "expired"


class QuarantineLevel(Enum):
    """Level of quarantine strictness."""
    
    OBSERVATION = 0  # Monitor only
    RESTRICTED = 1   # Limited features
    ISOLATED = 2     # Minimal access
    LOCKED = 3       # No access
    TERMINATED = 4   # Complete shutdown


class FeatureState(Enum):
    """State of a feature."""
    
    ENABLED = "enabled"
    DEGRADED = "degraded"
    DISABLED = "disabled"
    LOCKED = "locked"


@dataclass
class QuarantineEntry:
    """Entry for a quarantined entity."""
    
    entry_id: str
    entity_type: str  # license, client, user, feature
    entity_id: str
    level: QuarantineLevel
    status: QuarantineStatus
    reason: str
    created_at: datetime
    expires_at: Optional[datetime]
    created_by: str = "system"
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    restrictions: Dict[str, Any] = field(default_factory=dict)
    audit_log: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_audit_entry(self, action: str, details: str, actor: str = "system") -> None:
        """Add entry to audit log."""
        self.audit_log.append({
            "timestamp": datetime.now(UTC).isoformat(),
            "action": action,
            "details": details,
            "actor": actor,
        })
    
    @property
    def is_active(self) -> bool:
        """Check if quarantine is currently active."""
        if self.status not in [QuarantineStatus.ACTIVE, QuarantineStatus.APPROVED]:
            return False
        
        if self.expires_at and datetime.now(UTC) > self.expires_at:
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "entry_id": self.entry_id,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "level": self.level.value,
            "status": self.status.value,
            "reason": self.reason,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_by": self.created_by,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "restrictions": self.restrictions,
            "is_active": self.is_active,
            "audit_log": self.audit_log,
        }


@dataclass
class FeatureLockdown:
    """Feature lockdown configuration."""
    
    feature_name: str
    state: FeatureState
    original_state: FeatureState
    reason: str
    locked_at: datetime
    locked_by: str = "system"
    unlock_conditions: List[str] = field(default_factory=list)
    degradation_config: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "feature_name": self.feature_name,
            "state": self.state.value,
            "original_state": self.original_state.value,
            "reason": self.reason,
            "locked_at": self.locked_at.isoformat(),
            "locked_by": self.locked_by,
            "unlock_conditions": self.unlock_conditions,
            "degradation_config": self.degradation_config,
        }


@dataclass 
class DegradationPolicy:
    """Policy for graceful degradation."""
    
    policy_id: str
    name: str
    trigger_conditions: List[Dict[str, Any]]
    degradation_steps: List[Dict[str, Any]]
    recovery_steps: List[Dict[str, Any]]
    priority: int = 0
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "policy_id": self.policy_id,
            "name": self.name,
            "trigger_conditions": self.trigger_conditions,
            "degradation_steps": self.degradation_steps,
            "recovery_steps": self.recovery_steps,
            "priority": self.priority,
            "enabled": self.enabled,
        }


class QuarantineManager:
    """
    Manages quarantine, isolation, and feature lockdown.
    
    Provides mechanisms for containing security threats through
    license isolation, feature restrictions, and controlled degradation.
    """
    
    def __init__(
        self,
        auto_expire_hours: int = 24,
        require_approval: bool = False,
        max_quarantine_level: QuarantineLevel = QuarantineLevel.LOCKED,
    ):
        """Initialize quarantine manager.
        
        Args:
            auto_expire_hours: Default hours until quarantine expires
            require_approval: Whether quarantine requires approval
            max_quarantine_level: Maximum allowed quarantine level
        """
        self.auto_expire_hours = auto_expire_hours
        self.require_approval = require_approval
        self.max_quarantine_level = max_quarantine_level
        
        # Quarantine storage
        self._quarantines: Dict[str, QuarantineEntry] = {}
        self._entity_index: Dict[str, Set[str]] = defaultdict(set)
        
        # Feature lockdowns
        self._lockdowns: Dict[str, FeatureLockdown] = {}
        self._feature_states: Dict[str, FeatureState] = {}
        
        # Degradation policies
        self._degradation_policies: Dict[str, DegradationPolicy] = {}
        self._active_degradations: Dict[str, str] = {}  # entity_id -> policy_id
        
        # Event handlers
        self._event_handlers: Dict[str, List[Callable]] = defaultdict(list)
        
        # Lock for thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self._stats = {
            "quarantines_created": 0,
            "quarantines_released": 0,
            "features_locked": 0,
            "degradations_triggered": 0,
        }
        
        logger.info("QuarantineManager initialized")
    
    # Quarantine Management
    
    def quarantine(
        self,
        entity_type: str,
        entity_id: str,
        level: QuarantineLevel,
        reason: str,
        duration_hours: Optional[int] = None,
        restrictions: Optional[Dict[str, Any]] = None,
        created_by: str = "system",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QuarantineEntry:
        """Quarantine an entity.
        
        Args:
            entity_type: Type of entity (license, client, user, feature)
            entity_id: Entity identifier
            level: Quarantine level
            reason: Reason for quarantine
            duration_hours: Duration in hours (None = auto_expire_hours)
            restrictions: Specific restrictions to apply
            created_by: Who created the quarantine
            metadata: Additional metadata
            
        Returns:
            QuarantineEntry
        """
        # Enforce max level
        if level.value > self.max_quarantine_level.value:
            level = self.max_quarantine_level
            logger.warning(f"Quarantine level capped to {level.value} for {entity_id}")
        
        with self._lock:
            entry_id = f"QE-{uuid4().hex[:12]}"
            now = datetime.now(UTC)
            duration = duration_hours or self.auto_expire_hours
            
            entry = QuarantineEntry(
                entry_id=entry_id,
                entity_type=entity_type,
                entity_id=entity_id,
                level=level,
                status=QuarantineStatus.PENDING_REVIEW if self.require_approval else QuarantineStatus.ACTIVE,
                reason=reason,
                created_at=now,
                expires_at=now + timedelta(hours=duration),
                created_by=created_by,
                restrictions=restrictions or self._default_restrictions(level),
                metadata=metadata or {},
            )
            
            entry.add_audit_entry("created", f"Quarantine created: {reason}", created_by)
            
            self._quarantines[entry_id] = entry
            self._entity_index[f"{entity_type}:{entity_id}"].add(entry_id)
            self._stats["quarantines_created"] += 1
            
            logger.warning(
                f"Quarantine applied: {entity_type}:{entity_id} "
                f"at level {level.value} - {reason}"
            )
            
            self._trigger_event("quarantine_created", entry)
            
            return entry
    
    def _default_restrictions(self, level: QuarantineLevel) -> Dict[str, Any]:
        """Get default restrictions for a quarantine level."""
        restrictions = {
            QuarantineLevel.OBSERVATION: {
                "log_all_activity": True,
                "feature_access": "full",
                "rate_limit_multiplier": 1.0,
            },
            QuarantineLevel.RESTRICTED: {
                "log_all_activity": True,
                "feature_access": "basic",
                "rate_limit_multiplier": 0.5,
                "disabled_features": ["export", "bulk_operations"],
            },
            QuarantineLevel.ISOLATED: {
                "log_all_activity": True,
                "feature_access": "minimal",
                "rate_limit_multiplier": 0.1,
                "disabled_features": ["export", "bulk_operations", "api_access", "integrations"],
                "network_isolation": True,
            },
            QuarantineLevel.LOCKED: {
                "log_all_activity": True,
                "feature_access": "none",
                "rate_limit_multiplier": 0.0,
                "disabled_features": ["all"],
                "network_isolation": True,
                "session_termination": True,
            },
            QuarantineLevel.TERMINATED: {
                "log_all_activity": True,
                "feature_access": "terminated",
                "immediate_shutdown": True,
                "data_preservation": True,
            },
        }
        
        return restrictions.get(level, {})
    
    def approve_quarantine(
        self,
        entry_id: str,
        reviewer: str,
        notes: str = "",
    ) -> bool:
        """Approve a pending quarantine.
        
        Args:
            entry_id: Quarantine entry ID
            reviewer: Reviewer identifier
            notes: Approval notes
            
        Returns:
            True if approved successfully
        """
        with self._lock:
            if entry_id not in self._quarantines:
                return False
            
            entry = self._quarantines[entry_id]
            
            if entry.status != QuarantineStatus.PENDING_REVIEW:
                return False
            
            entry.status = QuarantineStatus.APPROVED
            entry.reviewed_by = reviewer
            entry.reviewed_at = datetime.now(UTC)
            entry.add_audit_entry("approved", f"Approved by {reviewer}: {notes}", reviewer)
            
            logger.info(f"Quarantine approved: {entry_id} by {reviewer}")
            self._trigger_event("quarantine_approved", entry)
            
            return True
    
    def release_quarantine(
        self,
        entry_id: str,
        released_by: str = "system",
        reason: str = "",
    ) -> bool:
        """Release a quarantine.
        
        Args:
            entry_id: Quarantine entry ID
            released_by: Who released the quarantine
            reason: Release reason
            
        Returns:
            True if released successfully
        """
        with self._lock:
            if entry_id not in self._quarantines:
                return False
            
            entry = self._quarantines[entry_id]
            entry.status = QuarantineStatus.RELEASED
            entry.add_audit_entry("released", f"Released: {reason}", released_by)
            
            self._stats["quarantines_released"] += 1
            
            logger.info(f"Quarantine released: {entry_id} - {reason}")
            self._trigger_event("quarantine_released", entry)
            
            return True
    
    def escalate_quarantine(
        self,
        entry_id: str,
        new_level: QuarantineLevel,
        reason: str,
        escalated_by: str = "system",
    ) -> bool:
        """Escalate quarantine to a higher level.
        
        Args:
            entry_id: Quarantine entry ID
            new_level: New quarantine level
            reason: Escalation reason
            escalated_by: Who escalated
            
        Returns:
            True if escalated successfully
        """
        with self._lock:
            if entry_id not in self._quarantines:
                return False
            
            entry = self._quarantines[entry_id]
            
            if new_level.value <= entry.level.value:
                return False  # Can only escalate up
            
            if new_level.value > self.max_quarantine_level.value:
                new_level = self.max_quarantine_level
            
            old_level = entry.level
            entry.level = new_level
            entry.restrictions = self._default_restrictions(new_level)
            entry.add_audit_entry(
                "escalated",
                f"Escalated from {old_level.value} to {new_level.value}: {reason}",
                escalated_by
            )
            
            logger.warning(f"Quarantine escalated: {entry_id} to level {new_level.value}")
            self._trigger_event("quarantine_escalated", {
                "entry": entry,
                "old_level": old_level,
                "new_level": new_level,
            })
            
            return True
    
    def get_quarantine_status(
        self,
        entity_type: str,
        entity_id: str,
    ) -> Optional[QuarantineEntry]:
        """Get active quarantine status for an entity.
        
        Args:
            entity_type: Entity type
            entity_id: Entity identifier
            
        Returns:
            Active QuarantineEntry or None
        """
        key = f"{entity_type}:{entity_id}"
        entry_ids = self._entity_index.get(key, set())
        
        for entry_id in entry_ids:
            entry = self._quarantines.get(entry_id)
            if entry and entry.is_active:
                return entry
        
        return None
    
    def is_quarantined(self, entity_type: str, entity_id: str) -> bool:
        """Check if entity is currently quarantined.
        
        Args:
            entity_type: Entity type
            entity_id: Entity identifier
            
        Returns:
            True if quarantined
        """
        return self.get_quarantine_status(entity_type, entity_id) is not None
    
    def get_restrictions(
        self,
        entity_type: str,
        entity_id: str,
    ) -> Dict[str, Any]:
        """Get current restrictions for an entity.
        
        Args:
            entity_type: Entity type
            entity_id: Entity identifier
            
        Returns:
            Dict of restrictions (empty if not quarantined)
        """
        entry = self.get_quarantine_status(entity_type, entity_id)
        return entry.restrictions if entry else {}
    
    # Feature Lockdown
    
    def lock_feature(
        self,
        feature_name: str,
        state: FeatureState,
        reason: str,
        locked_by: str = "system",
        unlock_conditions: Optional[List[str]] = None,
        degradation_config: Optional[Dict[str, Any]] = None,
    ) -> FeatureLockdown:
        """Lock a feature to a specific state.
        
        Args:
            feature_name: Name of the feature
            state: State to lock the feature to
            reason: Reason for lockdown
            locked_by: Who locked the feature
            unlock_conditions: Conditions required to unlock
            degradation_config: Configuration for degraded mode
            
        Returns:
            FeatureLockdown
        """
        with self._lock:
            original_state = self._feature_states.get(feature_name, FeatureState.ENABLED)
            
            lockdown = FeatureLockdown(
                feature_name=feature_name,
                state=state,
                original_state=original_state,
                reason=reason,
                locked_at=datetime.now(UTC),
                locked_by=locked_by,
                unlock_conditions=unlock_conditions or [],
                degradation_config=degradation_config or {},
            )
            
            self._lockdowns[feature_name] = lockdown
            self._feature_states[feature_name] = state
            self._stats["features_locked"] += 1
            
            logger.warning(f"Feature locked: {feature_name} -> {state.value} - {reason}")
            self._trigger_event("feature_locked", lockdown)
            
            return lockdown
    
    def unlock_feature(
        self,
        feature_name: str,
        unlocked_by: str = "system",
        reason: str = "",
    ) -> bool:
        """Unlock a feature and restore original state.
        
        Args:
            feature_name: Name of the feature
            unlocked_by: Who unlocked the feature
            reason: Unlock reason
            
        Returns:
            True if unlocked successfully
        """
        with self._lock:
            if feature_name not in self._lockdowns:
                return False
            
            lockdown = self._lockdowns.pop(feature_name)
            self._feature_states[feature_name] = lockdown.original_state
            
            logger.info(f"Feature unlocked: {feature_name} -> {lockdown.original_state.value}")
            self._trigger_event("feature_unlocked", {
                "feature_name": feature_name,
                "unlocked_by": unlocked_by,
                "reason": reason,
            })
            
            return True
    
    def get_feature_state(self, feature_name: str) -> FeatureState:
        """Get current state of a feature.
        
        Args:
            feature_name: Name of the feature
            
        Returns:
            Current FeatureState
        """
        return self._feature_states.get(feature_name, FeatureState.ENABLED)
    
    def is_feature_available(self, feature_name: str) -> bool:
        """Check if a feature is available for use.
        
        Args:
            feature_name: Name of the feature
            
        Returns:
            True if feature is enabled or degraded
        """
        state = self.get_feature_state(feature_name)
        return state in [FeatureState.ENABLED, FeatureState.DEGRADED]
    
    def get_locked_features(self) -> List[FeatureLockdown]:
        """Get all currently locked features."""
        return list(self._lockdowns.values())
    
    # Graceful Degradation
    
    def register_degradation_policy(self, policy: DegradationPolicy) -> None:
        """Register a degradation policy.
        
        Args:
            policy: Degradation policy to register
        """
        self._degradation_policies[policy.policy_id] = policy
        logger.info(f"Registered degradation policy: {policy.policy_id}")
    
    def create_degradation_policy(
        self,
        name: str,
        trigger_conditions: List[Dict[str, Any]],
        degradation_steps: List[Dict[str, Any]],
        recovery_steps: List[Dict[str, Any]],
        priority: int = 0,
    ) -> DegradationPolicy:
        """Create a new degradation policy.
        
        Args:
            name: Policy name
            trigger_conditions: Conditions that trigger degradation
            degradation_steps: Steps to execute during degradation
            recovery_steps: Steps to execute during recovery
            priority: Policy priority
            
        Returns:
            Created DegradationPolicy
        """
        policy_id = f"DP-{uuid4().hex[:12]}"
        
        policy = DegradationPolicy(
            policy_id=policy_id,
            name=name,
            trigger_conditions=trigger_conditions,
            degradation_steps=degradation_steps,
            recovery_steps=recovery_steps,
            priority=priority,
        )
        
        self._degradation_policies[policy_id] = policy
        return policy
    
    def trigger_degradation(
        self,
        entity_id: str,
        policy_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Trigger degradation for an entity using a policy.
        
        Args:
            entity_id: Entity to degrade
            policy_id: Policy to use
            context: Additional context
            
        Returns:
            True if degradation triggered
        """
        if policy_id not in self._degradation_policies:
            return False
        
        policy = self._degradation_policies[policy_id]
        
        if not policy.enabled:
            return False
        
        with self._lock:
            # Execute degradation steps
            for step in policy.degradation_steps:
                self._execute_degradation_step(entity_id, step, context)
            
            self._active_degradations[entity_id] = policy_id
            self._stats["degradations_triggered"] += 1
            
            logger.warning(f"Degradation triggered: {entity_id} using {policy.name}")
            self._trigger_event("degradation_triggered", {
                "entity_id": entity_id,
                "policy": policy,
                "context": context,
            })
            
            return True
    
    def _execute_degradation_step(
        self,
        entity_id: str,
        step: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Execute a single degradation step."""
        step_type = step.get("type")
        
        if step_type == "lock_feature":
            feature_name = step.get("feature")
            if feature_name:
                self.lock_feature(
                    feature_name=feature_name,
                    state=FeatureState.DISABLED,
                    reason=f"Degradation for {entity_id}",
                )
        
        elif step_type == "degrade_feature":
            feature_name = step.get("feature")
            config = step.get("config", {})
            if feature_name:
                self.lock_feature(
                    feature_name=feature_name,
                    state=FeatureState.DEGRADED,
                    reason=f"Degradation for {entity_id}",
                    degradation_config=config,
                )
        
        elif step_type == "quarantine":
            level = QuarantineLevel(step.get("level", QuarantineLevel.RESTRICTED.value))
            self.quarantine(
                entity_type="entity",
                entity_id=entity_id,
                level=level,
                reason="Triggered by degradation policy",
            )
        
        elif step_type == "rate_limit":
            # Rate limiting would integrate with a rate limiter
            logger.info(f"Rate limit step for {entity_id}: {step}")
    
    def recover_from_degradation(
        self,
        entity_id: str,
        recovered_by: str = "system",
    ) -> bool:
        """Recover an entity from degradation.
        
        Args:
            entity_id: Entity to recover
            recovered_by: Who triggered recovery
            
        Returns:
            True if recovered successfully
        """
        if entity_id not in self._active_degradations:
            return False
        
        policy_id = self._active_degradations[entity_id]
        policy = self._degradation_policies.get(policy_id)
        
        if not policy:
            return False
        
        with self._lock:
            # Execute recovery steps
            for step in policy.recovery_steps:
                self._execute_recovery_step(entity_id, step)
            
            del self._active_degradations[entity_id]
            
            logger.info(f"Degradation recovered: {entity_id}")
            self._trigger_event("degradation_recovered", {
                "entity_id": entity_id,
                "policy": policy,
                "recovered_by": recovered_by,
            })
            
            return True
    
    def _execute_recovery_step(
        self,
        entity_id: str,
        step: Dict[str, Any],
    ) -> None:
        """Execute a single recovery step."""
        step_type = step.get("type")
        
        if step_type == "unlock_feature":
            feature_name = step.get("feature")
            if feature_name:
                self.unlock_feature(feature_name, reason="Recovery")
        
        elif step_type == "release_quarantine":
            # Find and release quarantine
            key = f"entity:{entity_id}"
            entry_ids = self._entity_index.get(key, set())
            for entry_id in entry_ids:
                if entry_id in self._quarantines:
                    self.release_quarantine(entry_id, reason="Recovery")
    
    # Access Control Integration
    
    def check_access(
        self,
        entity_type: str,
        entity_id: str,
        feature: str,
        action: str,
    ) -> Tuple[bool, str]:
        """Check if access is allowed based on quarantine status.
        
        Args:
            entity_type: Type of entity
            entity_id: Entity identifier
            feature: Feature being accessed
            action: Action being performed
            
        Returns:
            Tuple of (allowed, reason)
        """
        # Check feature lockdown
        feature_state = self.get_feature_state(feature)
        if feature_state == FeatureState.DISABLED:
            return False, f"Feature {feature} is disabled"
        if feature_state == FeatureState.LOCKED:
            return False, f"Feature {feature} is locked"
        
        # Check entity quarantine
        quarantine = self.get_quarantine_status(entity_type, entity_id)
        if not quarantine:
            return True, "No quarantine"
        
        restrictions = quarantine.restrictions
        
        # Check feature access level
        access_level = restrictions.get("feature_access", "full")
        if access_level == "none" or access_level == "terminated":
            return False, f"Entity {entity_id} is quarantined at level {quarantine.level.value}"
        
        # Check disabled features
        disabled_features = restrictions.get("disabled_features", [])
        if "all" in disabled_features or feature in disabled_features:
            return False, f"Feature {feature} is disabled for quarantined entity"
        
        return True, "Access allowed"
    
    def get_rate_limit_multiplier(
        self,
        entity_type: str,
        entity_id: str,
    ) -> float:
        """Get rate limit multiplier for an entity.
        
        Args:
            entity_type: Type of entity
            entity_id: Entity identifier
            
        Returns:
            Rate limit multiplier (1.0 = normal, <1.0 = restricted)
        """
        quarantine = self.get_quarantine_status(entity_type, entity_id)
        if not quarantine:
            return 1.0
        
        return quarantine.restrictions.get("rate_limit_multiplier", 1.0)
    
    # Event Handling
    
    def on_event(self, event_type: str, handler: Callable) -> None:
        """Register an event handler.
        
        Args:
            event_type: Type of event
            handler: Handler function
        """
        self._event_handlers[event_type].append(handler)
    
    def _trigger_event(self, event_type: str, data: Any) -> None:
        """Trigger an event."""
        for handler in self._event_handlers.get(event_type, []):
            try:
                handler(data)
            except Exception as e:
                logger.error(f"Event handler error ({event_type}): {e}")
    
    # Maintenance
    
    def cleanup_expired(self) -> int:
        """Clean up expired quarantines.
        
        Returns:
            Number of expired entries cleaned up
        """
        with self._lock:
            now = datetime.now(UTC)
            expired_count = 0
            
            for entry_id, entry in list(self._quarantines.items()):
                if entry.expires_at and now > entry.expires_at:
                    if entry.status in [QuarantineStatus.ACTIVE, QuarantineStatus.APPROVED]:
                        entry.status = QuarantineStatus.EXPIRED
                        entry.add_audit_entry("expired", "Quarantine expired")
                        expired_count += 1
            
            return expired_count
    
    # Statistics
    
    def get_stats(self) -> Dict[str, Any]:
        """Get quarantine manager statistics."""
        active_quarantines = [
            q for q in self._quarantines.values()
            if q.is_active
        ]
        
        level_distribution = defaultdict(int)
        for q in active_quarantines:
            level_distribution[q.level.value] += 1
        
        return {
            **self._stats,
            "active_quarantines": len(active_quarantines),
            "pending_review": len([
                q for q in self._quarantines.values()
                if q.status == QuarantineStatus.PENDING_REVIEW
            ]),
            "locked_features": len(self._lockdowns),
            "active_degradations": len(self._active_degradations),
            "level_distribution": dict(level_distribution),
        }
    
    def export_state(self) -> Dict[str, Any]:
        """Export current state for backup/inspection."""
        return {
            "quarantines": {
                entry_id: entry.to_dict()
                for entry_id, entry in self._quarantines.items()
            },
            "lockdowns": {
                name: lockdown.to_dict()
                for name, lockdown in self._lockdowns.items()
            },
            "feature_states": {
                name: state.value
                for name, state in self._feature_states.items()
            },
            "active_degradations": dict(self._active_degradations),
            "stats": self.get_stats(),
            "exported_at": datetime.now(UTC).isoformat(),
        }
