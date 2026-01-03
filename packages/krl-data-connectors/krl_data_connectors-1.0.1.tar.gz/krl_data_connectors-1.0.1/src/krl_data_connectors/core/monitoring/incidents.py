"""
Incident Management Module - Phase 2 Week 13

Automated incident response with playbooks, escalation,
and remediation workflows.

Copyright 2025 KR-Labs. All rights reserved.
"""

from __future__ import annotations

import asyncio
import json
import threading
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta, UTC
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
import uuid


class IncidentSeverity(Enum):
    """Severity levels for incidents."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(Enum):
    """Status of an incident."""
    
    DETECTED = "detected"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    MITIGATING = "mitigating"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IncidentCategory(Enum):
    """Categories of security incidents."""
    
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    LICENSE_VIOLATION = "license_violation"
    INTEGRITY_FAILURE = "integrity_failure"
    DATA_BREACH = "data_breach"
    DOS_ATTACK = "dos_attack"
    ANOMALY = "anomaly"
    SYSTEM_FAILURE = "system_failure"


@dataclass
class IncidentEvent:
    """An event in the incident timeline."""
    
    event_id: str
    timestamp: float
    event_type: str
    description: str
    actor: str
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "timestamp_iso": datetime.fromtimestamp(
                self.timestamp, tz=timezone.utc
            ).isoformat(),
            "event_type": self.event_type,
            "description": self.description,
            "actor": self.actor,
            "data": self.data,
        }


@dataclass
class Incident:
    """A security incident."""
    
    incident_id: str
    title: str
    description: str
    severity: IncidentSeverity
    category: IncidentCategory
    status: IncidentStatus
    created_at: float
    source: str
    affected_entities: List[str] = field(default_factory=list)
    labels: Dict[str, str] = field(default_factory=dict)
    timeline: List[IncidentEvent] = field(default_factory=list)
    assignee: str | None = None
    resolved_at: float | None = None
    root_cause: str = ""
    remediation: str = ""
    playbook_id: str | None = None
    playbook_results: Dict[str, Any] = field(default_factory=dict)
    
    def add_event(
        self,
        event_type: str,
        description: str,
        actor: str = "system",
        data: Dict[str, Any] | None = None
    ) -> IncidentEvent:
        """Add event to timeline."""
        event = IncidentEvent(
            event_id=str(uuid.uuid4())[:8],
            timestamp=time.time(),
            event_type=event_type,
            description=description,
            actor=actor,
            data=data or {},
        )
        self.timeline.append(event)
        return event
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "incident_id": self.incident_id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity.value,
            "category": self.category.value,
            "status": self.status.value,
            "created_at": self.created_at,
            "created_at_iso": datetime.fromtimestamp(
                self.created_at, tz=timezone.utc
            ).isoformat(),
            "source": self.source,
            "affected_entities": self.affected_entities,
            "labels": self.labels,
            "timeline": [e.to_dict() for e in self.timeline],
            "assignee": self.assignee,
            "resolved_at": self.resolved_at,
            "root_cause": self.root_cause,
            "remediation": self.remediation,
            "playbook_id": self.playbook_id,
        }


class PlaybookAction(ABC):
    """Abstract base class for playbook actions."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Action name."""
        pass
    
    @abstractmethod
    def execute(self, incident: Incident, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the action. Returns result dict."""
        pass
    
    @abstractmethod
    def rollback(self, incident: Incident, context: Dict[str, Any]) -> bool:
        """Rollback the action. Returns success."""
        pass


class BlockIPAction(PlaybookAction):
    """Action to block an IP address."""
    
    @property
    def name(self) -> str:
        return "block_ip"
    
    def execute(self, incident: Incident, context: Dict[str, Any]) -> Dict[str, Any]:
        """Block the IP address."""
        ip = context.get("ip_address")
        if not ip:
            return {"success": False, "error": "No IP address in context"}
        
        # In production, this would interact with firewall/WAF
        incident.add_event(
            "action_executed",
            f"Blocked IP address: {ip}",
            actor="playbook"
        )
        
        return {"success": True, "blocked_ip": ip}
    
    def rollback(self, incident: Incident, context: Dict[str, Any]) -> bool:
        """Unblock the IP address."""
        ip = context.get("ip_address")
        if ip:
            incident.add_event(
                "action_rollback",
                f"Unblocked IP address: {ip}",
                actor="playbook"
            )
            return True
        return False


class RevokeLicenseAction(PlaybookAction):
    """Action to revoke a license."""
    
    @property
    def name(self) -> str:
        return "revoke_license"
    
    def execute(self, incident: Incident, context: Dict[str, Any]) -> Dict[str, Any]:
        """Revoke the license."""
        license_id = context.get("license_id")
        if not license_id:
            return {"success": False, "error": "No license ID in context"}
        
        incident.add_event(
            "action_executed",
            f"Revoked license: {license_id}",
            actor="playbook"
        )
        
        return {"success": True, "revoked_license": license_id}
    
    def rollback(self, incident: Incident, context: Dict[str, Any]) -> bool:
        """Reinstate the license."""
        license_id = context.get("license_id")
        if license_id:
            incident.add_event(
                "action_rollback",
                f"Reinstated license: {license_id}",
                actor="playbook"
            )
            return True
        return False


class TerminateSessionsAction(PlaybookAction):
    """Action to terminate user sessions."""
    
    @property
    def name(self) -> str:
        return "terminate_sessions"
    
    def execute(self, incident: Incident, context: Dict[str, Any]) -> Dict[str, Any]:
        """Terminate sessions."""
        user_id = context.get("user_id")
        if not user_id:
            return {"success": False, "error": "No user ID in context"}
        
        incident.add_event(
            "action_executed",
            f"Terminated all sessions for user: {user_id}",
            actor="playbook"
        )
        
        return {"success": True, "user_id": user_id, "sessions_terminated": True}
    
    def rollback(self, incident: Incident, context: Dict[str, Any]) -> bool:
        """Cannot rollback session termination."""
        return False


class EnableFailsafeAction(PlaybookAction):
    """Action to enable failsafe mode."""
    
    @property
    def name(self) -> str:
        return "enable_failsafe"
    
    def execute(self, incident: Incident, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enable failsafe mode."""
        mode = context.get("mode", "degraded")
        
        incident.add_event(
            "action_executed",
            f"Enabled failsafe mode: {mode}",
            actor="playbook"
        )
        
        return {"success": True, "failsafe_mode": mode}
    
    def rollback(self, incident: Incident, context: Dict[str, Any]) -> bool:
        """Disable failsafe mode."""
        incident.add_event(
            "action_rollback",
            "Disabled failsafe mode",
            actor="playbook"
        )
        return True


class NotifyAction(PlaybookAction):
    """Action to send notifications."""
    
    @property
    def name(self) -> str:
        return "notify"
    
    def execute(self, incident: Incident, context: Dict[str, Any]) -> Dict[str, Any]:
        """Send notification."""
        channels = context.get("channels", ["log"])
        message = context.get("message", f"Incident {incident.incident_id}: {incident.title}")
        
        incident.add_event(
            "notification_sent",
            f"Notified via: {', '.join(channels)}",
            actor="playbook",
            data={"message": message}
        )
        
        return {"success": True, "channels": channels}
    
    def rollback(self, incident: Incident, context: Dict[str, Any]) -> bool:
        """Cannot rollback notification."""
        return False


@dataclass
class PlaybookStep:
    """A step in a playbook."""
    
    step_id: str
    action: str
    description: str
    condition: str | None = None  # Expression to evaluate
    context_override: Dict[str, Any] = field(default_factory=dict)
    on_failure: str = "continue"  # continue, abort, skip
    timeout_seconds: float = 60.0


@dataclass
class Playbook:
    """Automated incident response playbook."""
    
    playbook_id: str
    name: str
    description: str
    trigger_categories: List[IncidentCategory]
    trigger_severities: List[IncidentSeverity]
    steps: List[PlaybookStep]
    enabled: bool = True
    auto_execute: bool = True
    cooldown_seconds: float = 300.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "playbook_id": self.playbook_id,
            "name": self.name,
            "description": self.description,
            "trigger_categories": [c.value for c in self.trigger_categories],
            "trigger_severities": [s.value for s in self.trigger_severities],
            "steps": [
                {
                    "step_id": s.step_id,
                    "action": s.action,
                    "description": s.description,
                    "condition": s.condition,
                    "on_failure": s.on_failure,
                }
                for s in self.steps
            ],
            "enabled": self.enabled,
            "auto_execute": self.auto_execute,
        }


@dataclass
class IncidentConfig:
    """Configuration for incident management."""
    
    # Auto-creation
    auto_create_from_alerts: bool = True
    alert_severity_mapping: Dict[str, IncidentSeverity] = field(default_factory=dict)
    
    # Escalation
    escalation_timeout_seconds: Dict[str, float] = field(default_factory=dict)
    
    # Playbooks
    playbooks_enabled: bool = True
    auto_execute_playbooks: bool = True
    
    # Retention
    retention_days: int = 90


class PlaybookExecutor:
    """Executes incident response playbooks."""
    
    def __init__(self):
        self._actions: Dict[str, PlaybookAction] = {}
        self._register_default_actions()
    
    def _register_default_actions(self) -> None:
        """Register default playbook actions."""
        default_actions = [
            BlockIPAction(),
            RevokeLicenseAction(),
            TerminateSessionsAction(),
            EnableFailsafeAction(),
            NotifyAction(),
        ]
        
        for action in default_actions:
            self._actions[action.name] = action
    
    def register_action(self, action: PlaybookAction) -> None:
        """Register a custom action."""
        self._actions[action.name] = action
    
    def execute(
        self,
        playbook: Playbook,
        incident: Incident,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a playbook for an incident."""
        results = {
            "playbook_id": playbook.playbook_id,
            "incident_id": incident.incident_id,
            "steps": [],
            "success": True,
            "aborted": False,
        }
        
        incident.playbook_id = playbook.playbook_id
        incident.add_event(
            "playbook_started",
            f"Started playbook: {playbook.name}",
            actor="system"
        )
        
        for step in playbook.steps:
            step_result = self._execute_step(step, incident, context)
            results["steps"].append(step_result)
            
            if not step_result["success"]:
                if step.on_failure == "abort":
                    results["success"] = False
                    results["aborted"] = True
                    incident.add_event(
                        "playbook_aborted",
                        f"Playbook aborted at step: {step.step_id}",
                        actor="system"
                    )
                    break
                elif step.on_failure == "skip":
                    continue
        
        if not results["aborted"]:
            incident.add_event(
                "playbook_completed",
                f"Playbook completed: {playbook.name}",
                actor="system"
            )
        
        incident.playbook_results = results
        return results
    
    def _execute_step(
        self,
        step: PlaybookStep,
        incident: Incident,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single playbook step."""
        result = {
            "step_id": step.step_id,
            "action": step.action,
            "success": False,
            "skipped": False,
            "error": None,
        }
        
        # Check condition
        if step.condition:
            try:
                if not self._evaluate_condition(step.condition, context):
                    result["skipped"] = True
                    result["success"] = True
                    return result
            except Exception as e:
                result["error"] = f"Condition evaluation failed: {e}"
                return result
        
        # Get action
        action = self._actions.get(step.action)
        if not action:
            result["error"] = f"Unknown action: {step.action}"
            return result
        
        # Merge context
        step_context = {**context, **step.context_override}
        
        # Execute
        try:
            action_result = action.execute(incident, step_context)
            result["success"] = action_result.get("success", False)
            result["result"] = action_result
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate step condition."""
        # Simple condition evaluation
        for key, value in context.items():
            condition = condition.replace(f"${key}", json.dumps(value))
        
        try:
            return bool(eval(condition, {"__builtins__": {}}, {}))
        except Exception:
            return False


class IncidentManager:
    """
    Manages security incidents with automated response.
    
    Features:
    - Incident lifecycle management
    - Playbook-based automation
    - Timeline tracking
    - Escalation handling
    """
    
    def __init__(self, config: IncidentConfig | None = None):
        self.config = config or IncidentConfig()
        self._incidents: Dict[str, Incident] = {}
        self._playbooks: Dict[str, Playbook] = {}
        self._playbook_cooldowns: Dict[str, float] = {}
        self._executor = PlaybookExecutor()
        self._callbacks: List[Callable[[Incident], None]] = []
        self._lock = threading.RLock()
        
        # Register default playbooks
        self._register_default_playbooks()
    
    def _register_default_playbooks(self) -> None:
        """Register default incident playbooks."""
        # Brute force playbook
        self.add_playbook(Playbook(
            playbook_id="pb_brute_force",
            name="Brute Force Response",
            description="Respond to authentication brute force attacks",
            trigger_categories=[IncidentCategory.AUTHENTICATION],
            trigger_severities=[IncidentSeverity.HIGH, IncidentSeverity.CRITICAL],
            steps=[
                PlaybookStep(
                    step_id="1",
                    action="block_ip",
                    description="Block attacking IP",
                ),
                PlaybookStep(
                    step_id="2",
                    action="terminate_sessions",
                    description="Terminate compromised sessions",
                    condition="$user_id != None",
                ),
                PlaybookStep(
                    step_id="3",
                    action="notify",
                    description="Notify security team",
                    context_override={"channels": ["slack", "email"]},
                ),
            ],
        ))
        
        # License violation playbook
        self.add_playbook(Playbook(
            playbook_id="pb_license_violation",
            name="License Violation Response",
            description="Respond to license abuse",
            trigger_categories=[IncidentCategory.LICENSE_VIOLATION],
            trigger_severities=[IncidentSeverity.MEDIUM, IncidentSeverity.HIGH, IncidentSeverity.CRITICAL],
            steps=[
                PlaybookStep(
                    step_id="1",
                    action="revoke_license",
                    description="Revoke abused license",
                ),
                PlaybookStep(
                    step_id="2",
                    action="notify",
                    description="Notify account team",
                    context_override={"channels": ["email"]},
                ),
            ],
        ))
        
        # Integrity failure playbook
        self.add_playbook(Playbook(
            playbook_id="pb_integrity_failure",
            name="Integrity Failure Response",
            description="Respond to integrity check failures",
            trigger_categories=[IncidentCategory.INTEGRITY_FAILURE],
            trigger_severities=[IncidentSeverity.CRITICAL],
            steps=[
                PlaybookStep(
                    step_id="1",
                    action="enable_failsafe",
                    description="Enable blocked mode",
                    context_override={"mode": "blocked"},
                ),
                PlaybookStep(
                    step_id="2",
                    action="terminate_sessions",
                    description="Terminate all sessions",
                ),
                PlaybookStep(
                    step_id="3",
                    action="notify",
                    description="Alert all channels",
                    context_override={"channels": ["slack", "email", "pagerduty"]},
                ),
            ],
        ))
    
    def _generate_incident_id(self) -> str:
        """Generate unique incident ID."""
        return f"INC-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
    
    def create_incident(
        self,
        title: str,
        description: str,
        severity: IncidentSeverity,
        category: IncidentCategory,
        source: str,
        affected_entities: List[str] | None = None,
        labels: Dict[str, str] | None = None,
        context: Dict[str, Any] | None = None,
    ) -> Incident:
        """Create a new incident."""
        incident = Incident(
            incident_id=self._generate_incident_id(),
            title=title,
            description=description,
            severity=severity,
            category=category,
            status=IncidentStatus.DETECTED,
            created_at=time.time(),
            source=source,
            affected_entities=affected_entities or [],
            labels=labels or {},
        )
        
        incident.add_event(
            "incident_created",
            f"Incident created from {source}",
            actor="system"
        )
        
        with self._lock:
            self._incidents[incident.incident_id] = incident
        
        # Notify callbacks
        self._notify_callbacks(incident)
        
        # Auto-execute playbook
        if self.config.playbooks_enabled and self.config.auto_execute_playbooks:
            self._auto_execute_playbook(incident, context or {})
        
        return incident
    
    def _auto_execute_playbook(
        self,
        incident: Incident,
        context: Dict[str, Any]
    ) -> None:
        """Automatically execute matching playbook."""
        for playbook in self._playbooks.values():
            if not playbook.enabled or not playbook.auto_execute:
                continue
            
            # Check triggers
            if incident.category not in playbook.trigger_categories:
                continue
            if incident.severity not in playbook.trigger_severities:
                continue
            
            # Check cooldown
            cooldown_key = f"{playbook.playbook_id}:{incident.category.value}"
            last_run = self._playbook_cooldowns.get(cooldown_key, 0)
            if time.time() - last_run < playbook.cooldown_seconds:
                continue
            
            # Execute
            self._executor.execute(playbook, incident, context)
            self._playbook_cooldowns[cooldown_key] = time.time()
            break  # Only execute one playbook
    
    def update_status(
        self,
        incident_id: str,
        status: IncidentStatus,
        actor: str = "system",
        note: str = ""
    ) -> bool:
        """Update incident status."""
        with self._lock:
            if incident_id not in self._incidents:
                return False
            
            incident = self._incidents[incident_id]
            old_status = incident.status
            incident.status = status
            
            if status == IncidentStatus.RESOLVED:
                incident.resolved_at = time.time()
            
            incident.add_event(
                "status_change",
                f"Status changed: {old_status.value} → {status.value}. {note}".strip(),
                actor=actor
            )
            
            self._notify_callbacks(incident)
            return True
    
    def assign(
        self,
        incident_id: str,
        assignee: str,
        actor: str = "system"
    ) -> bool:
        """Assign incident to someone."""
        with self._lock:
            if incident_id not in self._incidents:
                return False
            
            incident = self._incidents[incident_id]
            old_assignee = incident.assignee
            incident.assignee = assignee
            
            incident.add_event(
                "assigned",
                f"Assigned to {assignee}" + (f" (from {old_assignee})" if old_assignee else ""),
                actor=actor
            )
            
            return True
    
    def add_note(
        self,
        incident_id: str,
        note: str,
        actor: str = "system"
    ) -> bool:
        """Add note to incident timeline."""
        with self._lock:
            if incident_id not in self._incidents:
                return False
            
            incident = self._incidents[incident_id]
            incident.add_event("note_added", note, actor=actor)
            return True
    
    def set_root_cause(
        self,
        incident_id: str,
        root_cause: str,
        actor: str = "system"
    ) -> bool:
        """Set incident root cause."""
        with self._lock:
            if incident_id not in self._incidents:
                return False
            
            incident = self._incidents[incident_id]
            incident.root_cause = root_cause
            incident.add_event(
                "root_cause_identified",
                f"Root cause: {root_cause}",
                actor=actor
            )
            return True
    
    def add_playbook(self, playbook: Playbook) -> None:
        """Add a playbook."""
        with self._lock:
            self._playbooks[playbook.playbook_id] = playbook
    
    def remove_playbook(self, playbook_id: str) -> bool:
        """Remove a playbook."""
        with self._lock:
            if playbook_id in self._playbooks:
                del self._playbooks[playbook_id]
                return True
            return False
    
    def execute_playbook(
        self,
        incident_id: str,
        playbook_id: str,
        context: Dict[str, Any] | None = None
    ) -> Dict[str, Any] | None:
        """Manually execute a playbook on an incident."""
        with self._lock:
            if incident_id not in self._incidents:
                return None
            if playbook_id not in self._playbooks:
                return None
            
            incident = self._incidents[incident_id]
            playbook = self._playbooks[playbook_id]
            
            return self._executor.execute(playbook, incident, context or {})
    
    def _notify_callbacks(self, incident: Incident) -> None:
        """Notify all callbacks of incident update."""
        for callback in self._callbacks:
            try:
                callback(incident)
            except Exception:
                pass
    
    def subscribe(self, callback: Callable[[Incident], None]) -> None:
        """Subscribe to incident events."""
        with self._lock:
            self._callbacks.append(callback)
    
    def unsubscribe(self, callback: Callable[[Incident], None]) -> None:
        """Unsubscribe from incident events."""
        with self._lock:
            if callback in self._callbacks:
                self._callbacks.remove(callback)
    
    def get_incident(self, incident_id: str) -> Incident | None:
        """Get incident by ID."""
        return self._incidents.get(incident_id)
    
    def get_incidents(
        self,
        status: IncidentStatus | None = None,
        severity: IncidentSeverity | None = None,
        category: IncidentCategory | None = None,
        limit: int = 100
    ) -> List[Incident]:
        """Get incidents matching criteria."""
        results = []
        
        for incident in sorted(
            self._incidents.values(),
            key=lambda i: i.created_at,
            reverse=True
        ):
            if status and incident.status != status:
                continue
            if severity and incident.severity != severity:
                continue
            if category and incident.category != category:
                continue
            
            results.append(incident)
            if len(results) >= limit:
                break
        
        return results
    
    def get_active_incidents(self) -> List[Incident]:
        """Get all non-resolved incidents."""
        return [
            i for i in self._incidents.values()
            if i.status not in (IncidentStatus.RESOLVED, IncidentStatus.CLOSED)
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get incident statistics."""
        by_severity = defaultdict(int)
        by_status = defaultdict(int)
        by_category = defaultdict(int)
        
        for incident in self._incidents.values():
            by_severity[incident.severity.value] += 1
            by_status[incident.status.value] += 1
            by_category[incident.category.value] += 1
        
        return {
            "total_incidents": len(self._incidents),
            "active_incidents": len(self.get_active_incidents()),
            "by_severity": dict(by_severity),
            "by_status": dict(by_status),
            "by_category": dict(by_category),
            "playbooks": len(self._playbooks),
        }


# Global instance
_global_incident_manager: IncidentManager | None = None


def get_incident_manager() -> IncidentManager:
    """Get or create global incident manager."""
    global _global_incident_manager
    if _global_incident_manager is None:
        _global_incident_manager = IncidentManager()
    return _global_incident_manager
