"""
Defense Coordinator - Unified orchestration of all protection layers.

Week 16: Defense Integration & System Hardening
Coordinates threat_response, ml_defense, and license protection systems.
"""

from __future__ import annotations

import asyncio
import logging
import hashlib
import hmac
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, TypeVar
from collections import defaultdict
import threading
import uuid

logger = logging.getLogger(__name__)


class DefenseLevel(Enum):
    """Overall system defense levels."""
    
    NORMAL = 1      # Standard operation
    ELEVATED = 2    # Increased monitoring
    HIGH = 3        # Active threat detected
    SEVERE = 4      # Multiple threats, restricted operation
    CRITICAL = 5    # Lockdown mode


class ThreatDomain(Enum):
    """Domain classification for threats."""
    
    LICENSE = "license"
    BEHAVIORAL = "behavioral"
    NETWORK = "network"
    DATA_EXFILTRATION = "data_exfiltration"
    INJECTION = "injection"
    AUTHENTICATION = "authentication"


class ResponseAction(Enum):
    """Unified response actions across all systems."""
    
    LOG = auto()
    ALERT = auto()
    THROTTLE = auto()
    BLOCK = auto()
    QUARANTINE = auto()
    REVOKE = auto()
    LOCKDOWN = auto()


@dataclass
class ThreatEvent:
    """Unified threat event from any defense system."""
    
    event_id: str
    timestamp: datetime
    domain: ThreatDomain
    source_system: str
    severity: float  # 0.0 - 1.0
    entity_id: str
    description: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    recommended_action: Optional[ResponseAction] = None
    correlation_ids: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "domain": self.domain.value,
            "source_system": self.source_system,
            "severity": self.severity,
            "entity_id": self.entity_id,
            "description": self.description,
            "evidence": self.evidence,
            "recommended_action": self.recommended_action.name if self.recommended_action else None,
            "correlation_ids": self.correlation_ids,
        }


@dataclass
class DefenseResponse:
    """Coordinated defense response."""
    
    response_id: str
    timestamp: datetime
    action: ResponseAction
    defense_level: DefenseLevel
    trigger_events: List[str]  # Event IDs that triggered this response
    target_entity: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    duration: Optional[timedelta] = None
    reversible: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "response_id": self.response_id,
            "timestamp": self.timestamp.isoformat(),
            "action": self.action.name,
            "defense_level": self.defense_level.value,
            "trigger_events": self.trigger_events,
            "target_entity": self.target_entity,
            "parameters": self.parameters,
            "duration_seconds": self.duration.total_seconds() if self.duration else None,
            "reversible": self.reversible,
        }


class DefenseSubsystem(ABC):
    """Abstract base for defense subsystems."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Subsystem name."""
        pass
    
    @property
    @abstractmethod
    def priority(self) -> int:
        """Subsystem priority (higher = more important)."""
        pass
    
    @abstractmethod
    async def process_event(self, event: ThreatEvent) -> Optional[ResponseAction]:
        """Process an event and return recommended action."""
        pass
    
    @abstractmethod
    async def execute_action(
        self,
        action: ResponseAction,
        event: ThreatEvent,
        parameters: Dict[str, Any]
    ) -> bool:
        """Execute a defense action."""
        pass
    
    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """Get subsystem status."""
        pass


class ThreatCorrelationEngine:
    """Correlates threats across domains and time windows."""
    
    def __init__(
        self,
        correlation_window: timedelta = timedelta(minutes=5),
        min_events_for_pattern: int = 3
    ):
        self.correlation_window = correlation_window
        self.min_events_for_pattern = min_events_for_pattern
        self.events: List[ThreatEvent] = []
        self.correlation_groups: Dict[str, List[str]] = defaultdict(list)
        self._lock = threading.Lock()
    
    def add_event(self, event: ThreatEvent) -> List[str]:
        """Add event and return correlated event IDs."""
        with self._lock:
            # Clean old events
            cutoff = datetime.now() - self.correlation_window
            self.events = [e for e in self.events if e.timestamp > cutoff]
            
            # Find correlations
            correlated = self._find_correlations(event)
            
            # Store event
            self.events.append(event)
            
            # Update correlation groups
            if correlated:
                group_id = correlated[0] if correlated else event.event_id
                self.correlation_groups[group_id].append(event.event_id)
            
            return correlated
    
    def _find_correlations(self, event: ThreatEvent) -> List[str]:
        """Find events correlated with the new event."""
        correlated = []
        
        for existing in self.events:
            # Same entity correlation
            if existing.entity_id == event.entity_id:
                correlated.append(existing.event_id)
                continue
            
            # Domain escalation correlation
            if self._is_domain_escalation(existing, event):
                correlated.append(existing.event_id)
                continue
            
            # Evidence overlap correlation
            if self._has_evidence_overlap(existing, event):
                correlated.append(existing.event_id)
        
        return correlated
    
    def _is_domain_escalation(
        self,
        event1: ThreatEvent,
        event2: ThreatEvent
    ) -> bool:
        """Check if events represent domain escalation attack."""
        # Define escalation patterns
        escalation_paths = {
            ThreatDomain.AUTHENTICATION: [ThreatDomain.LICENSE, ThreatDomain.DATA_EXFILTRATION],
            ThreatDomain.LICENSE: [ThreatDomain.DATA_EXFILTRATION, ThreatDomain.BEHAVIORAL],
            ThreatDomain.INJECTION: [ThreatDomain.DATA_EXFILTRATION, ThreatDomain.NETWORK],
        }
        
        if event1.domain in escalation_paths:
            return event2.domain in escalation_paths[event1.domain]
        
        return False
    
    def _has_evidence_overlap(
        self,
        event1: ThreatEvent,
        event2: ThreatEvent
    ) -> bool:
        """Check if events share evidence indicators."""
        e1_values = set(str(v) for v in event1.evidence.values())
        e2_values = set(str(v) for v in event2.evidence.values())
        
        overlap = e1_values & e2_values
        return len(overlap) >= 2
    
    def get_attack_patterns(self) -> List[Dict[str, Any]]:
        """Identify potential attack patterns from correlated events."""
        patterns = []
        
        for group_id, event_ids in self.correlation_groups.items():
            if len(event_ids) >= self.min_events_for_pattern:
                group_events = [
                    e for e in self.events
                    if e.event_id in event_ids
                ]
                
                if group_events:
                    patterns.append({
                        "pattern_id": group_id,
                        "event_count": len(group_events),
                        "domains": list(set(e.domain.value for e in group_events)),
                        "entities": list(set(e.entity_id for e in group_events)),
                        "max_severity": max(e.severity for e in group_events),
                        "time_span_seconds": (
                            (max(e.timestamp for e in group_events) -
                             min(e.timestamp for e in group_events)).total_seconds()
                        ),
                    })
        
        return patterns
    
    def clear_correlation_group(self, group_id: str) -> None:
        """Clear a correlation group after response."""
        with self._lock:
            if group_id in self.correlation_groups:
                del self.correlation_groups[group_id]


class DefenseLevelManager:
    """Manages system-wide defense level."""
    
    def __init__(
        self,
        initial_level: DefenseLevel = DefenseLevel.NORMAL,
        auto_escalation: bool = True,
        auto_de_escalation: bool = True,
        escalation_threshold: float = 0.7,
        de_escalation_time: timedelta = timedelta(minutes=30)
    ):
        self.current_level = initial_level
        self.auto_escalation = auto_escalation
        self.auto_de_escalation = auto_de_escalation
        self.escalation_threshold = escalation_threshold
        self.de_escalation_time = de_escalation_time
        
        self.level_history: List[Tuple[datetime, DefenseLevel]] = [
            (datetime.now(), initial_level)
        ]
        self.last_threat_time: Optional[datetime] = None
        self._lock = threading.Lock()
        
        # Level-specific configurations
        self.level_configs: Dict[DefenseLevel, Dict[str, Any]] = {
            DefenseLevel.NORMAL: {
                "monitoring_interval": 60,
                "log_verbosity": "info",
                "auto_block": False,
            },
            DefenseLevel.ELEVATED: {
                "monitoring_interval": 30,
                "log_verbosity": "debug",
                "auto_block": False,
            },
            DefenseLevel.HIGH: {
                "monitoring_interval": 10,
                "log_verbosity": "debug",
                "auto_block": True,
            },
            DefenseLevel.SEVERE: {
                "monitoring_interval": 5,
                "log_verbosity": "debug",
                "auto_block": True,
                "restrict_new_connections": True,
            },
            DefenseLevel.CRITICAL: {
                "monitoring_interval": 1,
                "log_verbosity": "debug",
                "auto_block": True,
                "restrict_new_connections": True,
                "lockdown_mode": True,
            },
        }
    
    def evaluate_level(
        self,
        recent_events: List[ThreatEvent],
        attack_patterns: List[Dict[str, Any]]
    ) -> DefenseLevel:
        """Evaluate what defense level should be based on threats."""
        if not recent_events:
            return DefenseLevel.NORMAL
        
        # Calculate threat score
        max_severity = max(e.severity for e in recent_events)
        avg_severity = sum(e.severity for e in recent_events) / len(recent_events)
        domain_count = len(set(e.domain for e in recent_events))
        pattern_count = len(attack_patterns)
        
        # Weighted threat score
        threat_score = (
            max_severity * 0.3 +
            avg_severity * 0.2 +
            min(domain_count / 3, 1.0) * 0.2 +
            min(pattern_count / 2, 1.0) * 0.3
        )
        
        # Map score to level
        if threat_score >= 0.9:
            return DefenseLevel.CRITICAL
        elif threat_score >= 0.75:
            return DefenseLevel.SEVERE
        elif threat_score >= 0.6:
            return DefenseLevel.HIGH
        elif threat_score >= 0.4:
            return DefenseLevel.ELEVATED
        else:
            return DefenseLevel.NORMAL
    
    def set_level(self, level: DefenseLevel, reason: str = "") -> bool:
        """Manually set defense level."""
        with self._lock:
            old_level = self.current_level
            self.current_level = level
            self.level_history.append((datetime.now(), level))
            
            logger.info(
                f"Defense level changed: {old_level.name} -> {level.name}. "
                f"Reason: {reason}"
            )
            
            return True
    
    def check_de_escalation(self) -> bool:
        """Check if system should de-escalate."""
        if not self.auto_de_escalation:
            return False
        
        if self.current_level == DefenseLevel.NORMAL:
            return False
        
        if not self.last_threat_time:
            return True
        
        time_since_threat = datetime.now() - self.last_threat_time
        return time_since_threat >= self.de_escalation_time
    
    def de_escalate(self) -> bool:
        """De-escalate defense level by one step."""
        with self._lock:
            if self.current_level == DefenseLevel.NORMAL:
                return False
            
            new_level = DefenseLevel(self.current_level.value - 1)
            old_level = self.current_level
            self.current_level = new_level
            self.level_history.append((datetime.now(), new_level))
            
            logger.info(
                f"Defense level de-escalated: {old_level.name} -> {new_level.name}"
            )
            
            return True
    
    def escalate(self, reason: str = "") -> bool:
        """Escalate defense level by one step."""
        with self._lock:
            if self.current_level == DefenseLevel.CRITICAL:
                return False
            
            new_level = DefenseLevel(self.current_level.value + 1)
            old_level = self.current_level
            self.current_level = new_level
            self.level_history.append((datetime.now(), new_level))
            self.last_threat_time = datetime.now()
            
            logger.info(
                f"Defense level escalated: {old_level.name} -> {new_level.name}. "
                f"Reason: {reason}"
            )
            
            return True
    
    def get_config(self) -> Dict[str, Any]:
        """Get configuration for current defense level."""
        return self.level_configs.get(self.current_level, {})
    
    def get_history(
        self,
        since: Optional[datetime] = None
    ) -> List[Tuple[datetime, DefenseLevel]]:
        """Get defense level history."""
        if since:
            return [
                (ts, level) for ts, level in self.level_history
                if ts >= since
            ]
        return self.level_history.copy()


class ResponseExecutor:
    """Executes coordinated defense responses."""
    
    def __init__(self):
        self.active_responses: Dict[str, DefenseResponse] = {}
        self.response_history: List[DefenseResponse] = []
        self.executors: Dict[ResponseAction, List[Callable]] = defaultdict(list)
        self._lock = threading.Lock()
    
    def register_executor(
        self,
        action: ResponseAction,
        executor: Callable[[DefenseResponse], bool]
    ) -> None:
        """Register an executor for an action type."""
        self.executors[action].append(executor)
    
    async def execute(
        self,
        response: DefenseResponse,
        subsystems: List[DefenseSubsystem]
    ) -> bool:
        """Execute a defense response across subsystems."""
        with self._lock:
            self.active_responses[response.response_id] = response
        
        success = True
        
        try:
            # Execute through registered executors
            for executor in self.executors.get(response.action, []):
                try:
                    if not executor(response):
                        success = False
                except Exception as e:
                    logger.error(f"Executor failed for {response.action}: {e}")
                    success = False
            
            # Execute through subsystems in priority order
            sorted_subsystems = sorted(
                subsystems,
                key=lambda s: s.priority,
                reverse=True
            )
            
            for subsystem in sorted_subsystems:
                try:
                    # Create a dummy event for execution context
                    event = ThreatEvent(
                        event_id=response.trigger_events[0] if response.trigger_events else "manual",
                        timestamp=response.timestamp,
                        domain=ThreatDomain.LICENSE,  # Default domain
                        source_system="coordinator",
                        severity=0.5,
                        entity_id=response.target_entity,
                        description="Coordinated response execution"
                    )
                    
                    result = await subsystem.execute_action(
                        response.action,
                        event,
                        response.parameters
                    )
                    
                    if not result:
                        logger.warning(
                            f"Subsystem {subsystem.name} failed to execute "
                            f"{response.action.name}"
                        )
                except Exception as e:
                    logger.error(
                        f"Subsystem {subsystem.name} error during "
                        f"{response.action.name}: {e}"
                    )
                    success = False
            
            # Record response
            self.response_history.append(response)
            
            # Schedule expiration if duration is set
            if response.duration:
                asyncio.create_task(
                    self._schedule_expiration(response)
                )
            
        finally:
            if not response.duration:
                with self._lock:
                    if response.response_id in self.active_responses:
                        del self.active_responses[response.response_id]
        
        return success
    
    async def _schedule_expiration(self, response: DefenseResponse) -> None:
        """Schedule response expiration."""
        if response.duration:
            await asyncio.sleep(response.duration.total_seconds())
            
            with self._lock:
                if response.response_id in self.active_responses:
                    del self.active_responses[response.response_id]
                    logger.info(f"Response {response.response_id} expired")
    
    def revoke(self, response_id: str) -> bool:
        """Revoke an active response."""
        with self._lock:
            if response_id not in self.active_responses:
                return False
            
            response = self.active_responses[response_id]
            if not response.reversible:
                logger.warning(f"Response {response_id} is not reversible")
                return False
            
            del self.active_responses[response_id]
            logger.info(f"Response {response_id} revoked")
            return True
    
    def get_active_responses(
        self,
        entity_id: Optional[str] = None
    ) -> List[DefenseResponse]:
        """Get active responses, optionally filtered by entity."""
        with self._lock:
            if entity_id:
                return [
                    r for r in self.active_responses.values()
                    if r.target_entity == entity_id
                ]
            return list(self.active_responses.values())


@dataclass
class CoordinatorConfig:
    """Configuration for defense coordinator."""
    
    initial_defense_level: DefenseLevel = DefenseLevel.NORMAL
    auto_escalation: bool = True
    auto_de_escalation: bool = True
    correlation_window_minutes: int = 5
    response_cache_size: int = 10000
    enable_logging: bool = True
    signing_key: Optional[str] = None
    max_events_per_entity: int = 100


class DefenseCoordinator:
    """
    Central coordinator for all defense systems.
    
    Integrates:
    - Threat response (Week 14)
    - ML defense (Week 15)
    - License protection layers
    """
    
    def __init__(self, config: Optional[CoordinatorConfig] = None):
        self.config = config or CoordinatorConfig()
        
        # Core components
        self.level_manager = DefenseLevelManager(
            initial_level=self.config.initial_defense_level,
            auto_escalation=self.config.auto_escalation,
            auto_de_escalation=self.config.auto_de_escalation
        )
        
        self.correlation_engine = ThreatCorrelationEngine(
            correlation_window=timedelta(minutes=self.config.correlation_window_minutes)
        )
        
        self.response_executor = ResponseExecutor()
        
        # Subsystem registry
        self.subsystems: Dict[str, DefenseSubsystem] = {}
        
        # Event tracking
        self.events: List[ThreatEvent] = []
        self.entity_events: Dict[str, List[ThreatEvent]] = defaultdict(list)
        
        # Response decision thresholds
        self.action_thresholds: Dict[ResponseAction, float] = {
            ResponseAction.LOG: 0.0,
            ResponseAction.ALERT: 0.3,
            ResponseAction.THROTTLE: 0.5,
            ResponseAction.BLOCK: 0.7,
            ResponseAction.QUARANTINE: 0.8,
            ResponseAction.REVOKE: 0.9,
            ResponseAction.LOCKDOWN: 0.95,
        }
        
        # Stats
        self.stats = {
            "events_processed": 0,
            "responses_issued": 0,
            "escalations": 0,
            "de_escalations": 0,
        }
        
        self._lock = threading.Lock()
        self._running = False
    
    def register_subsystem(self, subsystem: DefenseSubsystem) -> bool:
        """Register a defense subsystem."""
        with self._lock:
            if subsystem.name in self.subsystems:
                logger.warning(f"Subsystem {subsystem.name} already registered")
                return False
            
            self.subsystems[subsystem.name] = subsystem
            logger.info(f"Registered subsystem: {subsystem.name}")
            return True
    
    def unregister_subsystem(self, name: str) -> bool:
        """Unregister a defense subsystem."""
        with self._lock:
            if name not in self.subsystems:
                return False
            
            del self.subsystems[name]
            logger.info(f"Unregistered subsystem: {name}")
            return True
    
    async def process_event(self, event: ThreatEvent) -> Optional[DefenseResponse]:
        """Process a threat event through the defense pipeline."""
        self.stats["events_processed"] += 1
        
        # Store event
        with self._lock:
            self.events.append(event)
            self.entity_events[event.entity_id].append(event)
            
            # Trim entity events if needed
            if len(self.entity_events[event.entity_id]) > self.config.max_events_per_entity:
                self.entity_events[event.entity_id] = \
                    self.entity_events[event.entity_id][-self.config.max_events_per_entity:]
        
        # Correlate with existing events
        correlated_ids = self.correlation_engine.add_event(event)
        event.correlation_ids = correlated_ids
        
        # Get attack patterns
        patterns = self.correlation_engine.get_attack_patterns()
        
        # Update defense level
        recent_events = [
            e for e in self.events
            if e.timestamp > datetime.now() - timedelta(minutes=10)
        ]
        
        recommended_level = self.level_manager.evaluate_level(
            recent_events, patterns
        )
        
        if recommended_level.value > self.level_manager.current_level.value:
            self.level_manager.escalate(
                f"Threat pattern detected: {event.description}"
            )
            self.stats["escalations"] += 1
        
        # Collect recommendations from subsystems
        recommendations: List[Tuple[ResponseAction, float]] = []
        
        for subsystem in self.subsystems.values():
            try:
                recommended = await subsystem.process_event(event)
                if recommended:
                    recommendations.append((recommended, subsystem.priority))
            except Exception as e:
                logger.error(f"Subsystem {subsystem.name} processing error: {e}")
        
        # Add event's own recommendation
        if event.recommended_action:
            recommendations.append((event.recommended_action, 50))
        
        # Determine final action
        final_action = self._decide_action(event, recommendations, patterns)
        
        if final_action and final_action != ResponseAction.LOG:
            response = await self._create_and_execute_response(
                event, final_action, correlated_ids
            )
            return response
        
        # Just log the event
        if self.config.enable_logging:
            logger.info(f"Event logged: {event.event_id} - {event.description}")
        
        return None
    
    def _decide_action(
        self,
        event: ThreatEvent,
        recommendations: List[Tuple[ResponseAction, float]],
        patterns: List[Dict[str, Any]]
    ) -> ResponseAction:
        """Decide on the appropriate action."""
        if not recommendations:
            # Use severity-based default
            for action, threshold in sorted(
                self.action_thresholds.items(),
                key=lambda x: x[1],
                reverse=True
            ):
                if event.severity >= threshold:
                    return action
            return ResponseAction.LOG
        
        # Weight recommendations by priority
        action_scores: Dict[ResponseAction, float] = defaultdict(float)
        
        for action, priority in recommendations:
            action_scores[action] += priority
        
        # Apply pattern multiplier
        if patterns:
            max_pattern_severity = max(p["max_severity"] for p in patterns)
            if max_pattern_severity > 0.7:
                # Boost more aggressive actions when patterns detected
                for action in [ResponseAction.QUARANTINE, ResponseAction.BLOCK]:
                    action_scores[action] *= 1.5
        
        # Apply defense level modifier
        level_config = self.level_manager.get_config()
        if level_config.get("auto_block"):
            action_scores[ResponseAction.BLOCK] *= 1.3
        
        # Select highest scoring action
        if action_scores:
            return max(action_scores.items(), key=lambda x: x[1])[0]
        
        return ResponseAction.LOG
    
    async def _create_and_execute_response(
        self,
        event: ThreatEvent,
        action: ResponseAction,
        correlated_ids: List[str]
    ) -> DefenseResponse:
        """Create and execute a defense response."""
        response = DefenseResponse(
            response_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            action=action,
            defense_level=self.level_manager.current_level,
            trigger_events=[event.event_id] + correlated_ids[:5],
            target_entity=event.entity_id,
            parameters={
                "severity": event.severity,
                "domain": event.domain.value,
                "source": event.source_system,
            },
            duration=self._get_action_duration(action),
            reversible=action not in [ResponseAction.LOCKDOWN, ResponseAction.REVOKE]
        )
        
        # Execute across subsystems
        await self.response_executor.execute(
            response,
            list(self.subsystems.values())
        )
        
        self.stats["responses_issued"] += 1
        
        return response
    
    def _get_action_duration(self, action: ResponseAction) -> Optional[timedelta]:
        """Get default duration for an action."""
        durations = {
            ResponseAction.THROTTLE: timedelta(minutes=15),
            ResponseAction.BLOCK: timedelta(hours=1),
            ResponseAction.QUARANTINE: timedelta(hours=24),
        }
        return durations.get(action)
    
    async def check_entity(self, entity_id: str) -> Dict[str, Any]:
        """Get comprehensive status for an entity."""
        entity_status = {
            "entity_id": entity_id,
            "timestamp": datetime.now().isoformat(),
            "defense_level": self.level_manager.current_level.name,
            "active_responses": [],
            "recent_events": [],
            "risk_assessment": {},
        }
        
        # Get active responses for entity
        active = self.response_executor.get_active_responses(entity_id)
        entity_status["active_responses"] = [r.to_dict() for r in active]
        
        # Get recent events
        with self._lock:
            recent = self.entity_events.get(entity_id, [])[-10:]
            entity_status["recent_events"] = [e.to_dict() for e in recent]
        
        # Calculate risk assessment
        if recent:
            entity_status["risk_assessment"] = {
                "event_count": len(recent),
                "max_severity": max(e.severity for e in recent),
                "avg_severity": sum(e.severity for e in recent) / len(recent),
                "domains_affected": list(set(e.domain.value for e in recent)),
                "active_blocks": sum(
                    1 for r in active
                    if r.action in [ResponseAction.BLOCK, ResponseAction.QUARANTINE]
                ),
            }
        
        return entity_status
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        return {
            "timestamp": datetime.now().isoformat(),
            "defense_level": self.level_manager.current_level.name,
            "defense_level_config": self.level_manager.get_config(),
            "subsystems": {
                name: await subsystem.get_status()
                for name, subsystem in self.subsystems.items()
            },
            "statistics": self.stats.copy(),
            "active_response_count": len(
                self.response_executor.active_responses
            ),
            "attack_patterns": self.correlation_engine.get_attack_patterns(),
        }
    
    async def manual_action(
        self,
        action: ResponseAction,
        entity_id: str,
        reason: str,
        duration: Optional[timedelta] = None
    ) -> DefenseResponse:
        """Execute a manual defense action."""
        event = ThreatEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            domain=ThreatDomain.LICENSE,
            source_system="manual",
            severity=0.8,
            entity_id=entity_id,
            description=f"Manual action: {reason}",
            recommended_action=action
        )
        
        response = DefenseResponse(
            response_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            action=action,
            defense_level=self.level_manager.current_level,
            trigger_events=[event.event_id],
            target_entity=entity_id,
            parameters={"reason": reason, "manual": True},
            duration=duration,
            reversible=action not in [ResponseAction.LOCKDOWN, ResponseAction.REVOKE]
        )
        
        await self.response_executor.execute(
            response,
            list(self.subsystems.values())
        )
        
        return response
    
    async def revoke_response(self, response_id: str) -> bool:
        """Revoke an active response."""
        return self.response_executor.revoke(response_id)
    
    def sign_response(self, response: DefenseResponse) -> str:
        """Sign a response for integrity verification."""
        if not self.config.signing_key:
            raise ValueError("No signing key configured")
        
        payload = json.dumps(response.to_dict(), sort_keys=True)
        signature = hmac.new(
            self.config.signing_key.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def verify_response(self, response: DefenseResponse, signature: str) -> bool:
        """Verify response signature."""
        expected = self.sign_response(response)
        return hmac.compare_digest(expected, signature)


# Factory functions for integration
def create_coordinator(
    signing_key: Optional[str] = None,
    initial_level: DefenseLevel = DefenseLevel.NORMAL
) -> DefenseCoordinator:
    """Create a configured defense coordinator."""
    config = CoordinatorConfig(
        initial_defense_level=initial_level,
        signing_key=signing_key
    )
    return DefenseCoordinator(config)


def create_threat_event(
    domain: ThreatDomain,
    entity_id: str,
    severity: float,
    description: str,
    source: str = "unknown",
    evidence: Optional[Dict[str, Any]] = None
) -> ThreatEvent:
    """Factory for creating threat events."""
    return ThreatEvent(
        event_id=str(uuid.uuid4()),
        timestamp=datetime.now(),
        domain=domain,
        source_system=source,
        severity=max(0.0, min(1.0, severity)),
        entity_id=entity_id,
        description=description,
        evidence=evidence or {}
    )
