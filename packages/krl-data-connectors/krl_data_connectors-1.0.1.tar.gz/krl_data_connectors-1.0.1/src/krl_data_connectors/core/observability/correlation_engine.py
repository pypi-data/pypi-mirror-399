# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
Correlation Engine - Phase 3 Week 19

Anomaly correlation and root cause analysis engine.
Links related events across time and space to identify patterns.

Features:
- Temporal correlation (events close in time)
- Spatial correlation (events from same source/tenant)
- Causal correlation (event chains)
- Pattern matching against known attack signatures
- Root cause inference
- Recommended action generation
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
import uuid
import hashlib

from .dashboard_hooks import (
    AnomalyCorrelation,
    DashboardEvent,
    DashboardEventType,
    get_dashboard_registry,
)
from .telemetry_ingestion import TelemetryEvent, TelemetryEventType


# =============================================================================
# Correlation Types
# =============================================================================

class CorrelationType(Enum):
    """Types of correlation relationships."""
    
    TEMPORAL = "temporal"       # Close in time
    SPATIAL = "spatial"         # Same source/target
    CAUSAL = "causal"           # One caused the other
    PATTERN = "pattern"         # Matches known pattern
    TENANT = "tenant"           # Same tenant
    SESSION = "session"         # Same correlation_id


# =============================================================================
# Correlation Rules
# =============================================================================

@dataclass
class CorrelationRule:
    """
    A rule for correlating events.
    
    Attributes:
        rule_id: Unique rule identifier
        name: Human-readable name
        description: Rule description
        event_types: Event types this rule applies to
        correlation_type: Type of correlation
        time_window_sec: Max time between correlated events
        min_events: Minimum events to trigger correlation
        severity_boost: Severity multiplier when matched
        pattern_signature: Optional pattern hash for pattern matching
    """
    rule_id: str
    name: str
    description: str
    event_types: Set[TelemetryEventType]
    correlation_type: CorrelationType
    time_window_sec: float = 60.0
    min_events: int = 2
    severity_boost: float = 1.5
    pattern_signature: Optional[str] = None
    root_cause_template: Optional[str] = None
    action_template: Optional[str] = None


# Pre-defined correlation rules
BUILT_IN_RULES: List[CorrelationRule] = [
    CorrelationRule(
        rule_id="license_anomaly_cluster",
        name="License Anomaly Cluster",
        description="Multiple license anomalies from same tenant",
        event_types={TelemetryEventType.LICENSE_ANOMALY},
        correlation_type=CorrelationType.TENANT,
        time_window_sec=300.0,
        min_events=3,
        severity_boost=2.0,
        root_cause_template="Potential license sharing or abuse from tenant {tenant_id}",
        action_template="Review tenant {tenant_id} license usage; consider rate limiting",
    ),
    CorrelationRule(
        rule_id="enforcement_cascade",
        name="Enforcement Cascade",
        description="Chain of escalating enforcement actions",
        event_types={
            TelemetryEventType.ENFORCEMENT_DECISION,
            TelemetryEventType.ENFORCEMENT_ACTION,
            TelemetryEventType.ENFORCEMENT_RESULT,
        },
        correlation_type=CorrelationType.CAUSAL,
        time_window_sec=30.0,
        min_events=3,
        severity_boost=1.5,
        root_cause_template="Enforcement cascade triggered by {trigger_event}",
        action_template="Review enforcement rules for over-sensitivity",
    ),
    CorrelationRule(
        rule_id="threat_wave",
        name="Threat Wave",
        description="Multiple threats detected in short window",
        event_types={
            TelemetryEventType.THREAT_DETECTED,
            TelemetryEventType.THREAT_RESPONSE,
        },
        correlation_type=CorrelationType.TEMPORAL,
        time_window_sec=60.0,
        min_events=5,
        severity_boost=2.0,
        root_cause_template="Coordinated threat activity detected",
        action_template="Escalate to security team; enable enhanced monitoring",
    ),
    CorrelationRule(
        rule_id="ml_drift_cluster",
        name="ML Drift Cluster",
        description="Multiple ML drift events indicating model degradation",
        event_types={TelemetryEventType.ML_DRIFT},
        correlation_type=CorrelationType.TEMPORAL,
        time_window_sec=600.0,
        min_events=3,
        severity_boost=1.8,
        root_cause_template="Model {model_name} showing consistent drift",
        action_template="Trigger model retraining; review feature pipeline",
    ),
    CorrelationRule(
        rule_id="tier_violation_pattern",
        name="Tier Violation Pattern",
        description="Repeated tier violations suggesting upgrade candidate",
        event_types={TelemetryEventType.TIER_VIOLATION},
        correlation_type=CorrelationType.TENANT,
        time_window_sec=3600.0,  # 1 hour
        min_events=5,
        severity_boost=1.2,
        root_cause_template="Tenant {tenant_id} consistently hitting tier limits",
        action_template="Send upgrade prompt to tenant {tenant_id}",
    ),
    CorrelationRule(
        rule_id="api_abuse_pattern",
        name="API Abuse Pattern",
        description="Unusual API request patterns",
        event_types={
            TelemetryEventType.API_REQUEST,
            TelemetryEventType.CROWN_JEWEL_ACCESS,
        },
        correlation_type=CorrelationType.SPATIAL,
        time_window_sec=60.0,
        min_events=10,
        severity_boost=2.5,
        root_cause_template="API abuse detected from {source}",
        action_template="Apply rate limiting to {source}; review for blocking",
    ),
]


# =============================================================================
# Correlation Cluster
# =============================================================================

@dataclass
class CorrelationCluster:
    """
    A cluster of correlated events.
    
    Represents a group of events linked by one or more correlation rules.
    """
    cluster_id: str
    created_at: float
    correlation_type: CorrelationType
    rule_id: Optional[str]
    
    # Events in cluster
    events: List[Dict[str, Any]] = field(default_factory=list)
    event_ids: Set[str] = field(default_factory=set)
    
    # Derived attributes
    severity: float = 0.0
    tenant_ids: Set[str] = field(default_factory=set)
    sources: Set[str] = field(default_factory=set)
    
    # Analysis results
    root_cause: Optional[str] = None
    recommended_action: Optional[str] = None
    affected_components: List[str] = field(default_factory=list)
    
    def add_event(self, event: Dict[str, Any]) -> None:
        """Add an event to the cluster."""
        event_id = event.get("event_id", str(uuid.uuid4()))
        
        if event_id in self.event_ids:
            return
        
        self.events.append(event)
        self.event_ids.add(event_id)
        
        # Update derived attributes
        if tenant_id := event.get("tenant_id"):
            self.tenant_ids.add(tenant_id)
        if source := event.get("source"):
            self.sources.add(source)
        
        # Update severity (max + boost for count)
        event_severity = event.get("severity", 0.5)
        self.severity = max(self.severity, event_severity)
        if len(self.events) > 1:
            self.severity = min(1.0, self.severity * 1.1)
    
    def get_correlation_strength(self) -> float:
        """Calculate correlation strength 0.0-1.0."""
        if len(self.events) < 2:
            return 0.0
        
        # Factors: event count, time density, source overlap
        event_factor = min(1.0, len(self.events) / 10)
        
        # Time density: how close are events in time
        if len(self.events) >= 2:
            timestamps = sorted(e.get("timestamp", 0) for e in self.events)
            time_span = timestamps[-1] - timestamps[0]
            time_factor = 1.0 - min(1.0, time_span / 300.0)
        else:
            time_factor = 0.5
        
        # Source overlap
        source_factor = 1.0 if len(self.sources) == 1 else 0.5
        
        return 0.4 * event_factor + 0.4 * time_factor + 0.2 * source_factor
    
    def to_anomaly_correlation(self) -> AnomalyCorrelation:
        """Convert to AnomalyCorrelation for dashboard."""
        return AnomalyCorrelation(
            cluster_id=self.cluster_id,
            timestamp=time.time(),
            anomalies=self.events,
            correlation_strength=self.get_correlation_strength(),
            root_cause=self.root_cause,
            affected_components=self.affected_components,
            recommended_action=self.recommended_action,
        )
    
    def is_significant(self, min_events: int = 2, min_strength: float = 0.3) -> bool:
        """Check if cluster is significant enough to report."""
        return (
            len(self.events) >= min_events and
            self.get_correlation_strength() >= min_strength
        )


# =============================================================================
# Correlation Engine
# =============================================================================

class CorrelationEngine:
    """
    Event correlation and root cause analysis engine.
    
    Processes telemetry events and groups them into
    correlated clusters for analysis.
    """
    
    def __init__(
        self,
        rules: Optional[List[CorrelationRule]] = None,
        default_window_sec: float = 300.0,
        max_clusters: int = 1000,
        emit_to_dashboard: bool = True,
    ):
        """
        Initialize correlation engine.
        
        Args:
            rules: Correlation rules to apply
            default_window_sec: Default time window for correlation
            max_clusters: Maximum active clusters to track
            emit_to_dashboard: Auto-emit to dashboard hooks
        """
        self._rules = rules or BUILT_IN_RULES.copy()
        self._default_window = default_window_sec
        self._max_clusters = max_clusters
        self._emit_to_dashboard = emit_to_dashboard
        
        # Active clusters
        self._clusters: Dict[str, CorrelationCluster] = {}
        
        # Indexes for fast lookup
        self._tenant_index: Dict[str, Set[str]] = defaultdict(set)
        self._source_index: Dict[str, Set[str]] = defaultdict(set)
        self._correlation_id_index: Dict[str, Set[str]] = defaultdict(set)
        self._event_type_index: Dict[TelemetryEventType, Set[str]] = defaultdict(set)
        
        # Recent events for temporal correlation
        self._recent_events: List[Dict[str, Any]] = []
        
        self._lock = threading.Lock()
        self._stats = {
            "events_processed": 0,
            "clusters_created": 0,
            "correlations_found": 0,
        }
    
    def add_rule(self, rule: CorrelationRule) -> None:
        """Add a correlation rule."""
        self._rules.append(rule)
    
    def process_event(self, event: TelemetryEvent) -> List[CorrelationCluster]:
        """
        Process a telemetry event and find correlations.
        
        Returns list of clusters the event was added to.
        """
        event_dict = event.to_dict()
        event_dict["event_id"] = event.event_id
        
        affected_clusters = []
        
        with self._lock:
            self._stats["events_processed"] += 1
            
            # Try each applicable rule
            for rule in self._rules:
                if event.event_type not in rule.event_types:
                    continue
                
                cluster = self._find_or_create_cluster(event_dict, rule)
                if cluster:
                    affected_clusters.append(cluster)
            
            # Add to recent events
            self._recent_events.append(event_dict)
            self._prune_recent_events()
            
            # Update indexes
            self._update_indexes(event_dict, affected_clusters)
            
            # Prune old clusters
            self._prune_clusters()
        
        # Emit significant clusters
        if self._emit_to_dashboard:
            for cluster in affected_clusters:
                if cluster.is_significant():
                    self._emit_cluster(cluster)
        
        return affected_clusters
    
    def process_batch(self, events: List[TelemetryEvent]) -> Dict[str, List[CorrelationCluster]]:
        """
        Process multiple events.
        
        Returns mapping of event_id to affected clusters.
        """
        results = {}
        for event in events:
            results[event.event_id] = self.process_event(event)
        return results
    
    def get_cluster(self, cluster_id: str) -> Optional[CorrelationCluster]:
        """Get a cluster by ID."""
        with self._lock:
            return self._clusters.get(cluster_id)
    
    def get_clusters_for_tenant(self, tenant_id: str) -> List[CorrelationCluster]:
        """Get all clusters involving a tenant."""
        with self._lock:
            cluster_ids = self._tenant_index.get(tenant_id, set())
            return [self._clusters[cid] for cid in cluster_ids if cid in self._clusters]
    
    def get_significant_clusters(
        self,
        min_events: int = 2,
        min_strength: float = 0.3,
    ) -> List[CorrelationCluster]:
        """Get all significant clusters."""
        with self._lock:
            return [
                c for c in self._clusters.values()
                if c.is_significant(min_events, min_strength)
            ]
    
    def analyze_cluster(self, cluster_id: str) -> Optional[Dict[str, Any]]:
        """
        Perform detailed analysis on a cluster.
        
        Returns analysis results including root cause and recommendations.
        """
        with self._lock:
            cluster = self._clusters.get(cluster_id)
            if not cluster:
                return None
            
            # Find matching rule
            rule = next(
                (r for r in self._rules if r.rule_id == cluster.rule_id),
                None
            )
            
            # Generate root cause
            if rule and rule.root_cause_template:
                context = self._build_template_context(cluster)
                cluster.root_cause = rule.root_cause_template.format(**context)
            
            # Generate recommended action
            if rule and rule.action_template:
                context = self._build_template_context(cluster)
                cluster.recommended_action = rule.action_template.format(**context)
            
            # Identify affected components
            cluster.affected_components = list(cluster.sources)
            
            return {
                "cluster_id": cluster_id,
                "event_count": len(cluster.events),
                "correlation_strength": cluster.get_correlation_strength(),
                "severity": cluster.severity,
                "root_cause": cluster.root_cause,
                "recommended_action": cluster.recommended_action,
                "affected_components": cluster.affected_components,
                "tenant_ids": list(cluster.tenant_ids),
                "sources": list(cluster.sources),
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics."""
        with self._lock:
            return {
                **self._stats,
                "active_clusters": len(self._clusters),
                "recent_events": len(self._recent_events),
                "rules_count": len(self._rules),
            }
    
    def _find_or_create_cluster(
        self,
        event: Dict[str, Any],
        rule: CorrelationRule,
    ) -> Optional[CorrelationCluster]:
        """Find an existing cluster or create a new one."""
        # Find candidate clusters based on rule type
        candidates = self._find_candidate_clusters(event, rule)
        
        # Check time window
        now = event.get("timestamp", time.time())
        
        for cluster_id in candidates:
            cluster = self._clusters.get(cluster_id)
            if not cluster:
                continue
            
            # Check if event fits in cluster's time window
            oldest = min(e.get("timestamp", 0) for e in cluster.events)
            if now - oldest <= rule.time_window_sec:
                cluster.add_event(event)
                self._stats["correlations_found"] += 1
                return cluster
        
        # Create new cluster if we have enough matching recent events
        matching_recent = self._find_matching_recent(event, rule)
        
        if len(matching_recent) >= rule.min_events - 1:
            cluster = CorrelationCluster(
                cluster_id=str(uuid.uuid4()),
                created_at=now,
                correlation_type=rule.correlation_type,
                rule_id=rule.rule_id,
            )
            
            # Add matching recent events
            for recent in matching_recent:
                cluster.add_event(recent)
            
            # Add current event
            cluster.add_event(event)
            
            # Apply severity boost
            cluster.severity = min(1.0, cluster.severity * rule.severity_boost)
            
            self._clusters[cluster.cluster_id] = cluster
            self._stats["clusters_created"] += 1
            
            return cluster
        
        return None
    
    def _find_candidate_clusters(
        self,
        event: Dict[str, Any],
        rule: CorrelationRule,
    ) -> Set[str]:
        """Find candidate clusters based on rule type."""
        candidates: Set[str] = set()
        
        if rule.correlation_type == CorrelationType.TENANT:
            tenant_id = event.get("tenant_id")
            if tenant_id:
                candidates.update(self._tenant_index.get(tenant_id, set()))
        
        elif rule.correlation_type == CorrelationType.SPATIAL:
            source = event.get("source")
            if source:
                candidates.update(self._source_index.get(source, set()))
        
        elif rule.correlation_type == CorrelationType.SESSION:
            corr_id = event.get("correlation_id")
            if corr_id:
                candidates.update(self._correlation_id_index.get(corr_id, set()))
        
        elif rule.correlation_type in (CorrelationType.TEMPORAL, CorrelationType.CAUSAL):
            # Check clusters with same event type
            event_type = event.get("event_type")
            if event_type:
                try:
                    et = TelemetryEventType(event_type)
                    candidates.update(self._event_type_index.get(et, set()))
                except ValueError:
                    pass
        
        # Filter to clusters matching this rule
        return {
            cid for cid in candidates
            if self._clusters.get(cid, CorrelationCluster(
                cluster_id="", created_at=0, correlation_type=rule.correlation_type, rule_id=None
            )).rule_id == rule.rule_id
        }
    
    def _find_matching_recent(
        self,
        event: Dict[str, Any],
        rule: CorrelationRule,
    ) -> List[Dict[str, Any]]:
        """Find recent events matching the rule."""
        now = event.get("timestamp", time.time())
        matching = []
        
        for recent in reversed(self._recent_events):
            # Check time window
            if now - recent.get("timestamp", 0) > rule.time_window_sec:
                break
            
            # Check event type
            event_type_str = recent.get("event_type")
            try:
                event_type = TelemetryEventType(event_type_str)
            except ValueError:
                continue
            
            if event_type not in rule.event_types:
                continue
            
            # Check correlation criteria
            if rule.correlation_type == CorrelationType.TENANT:
                if recent.get("tenant_id") == event.get("tenant_id"):
                    matching.append(recent)
            
            elif rule.correlation_type == CorrelationType.SPATIAL:
                if recent.get("source") == event.get("source"):
                    matching.append(recent)
            
            elif rule.correlation_type == CorrelationType.SESSION:
                if recent.get("correlation_id") == event.get("correlation_id"):
                    matching.append(recent)
            
            elif rule.correlation_type == CorrelationType.TEMPORAL:
                matching.append(recent)
            
            elif rule.correlation_type == CorrelationType.CAUSAL:
                # For causal, check if events could be related
                matching.append(recent)
        
        return matching[:rule.min_events]
    
    def _update_indexes(
        self,
        event: Dict[str, Any],
        clusters: List[CorrelationCluster],
    ) -> None:
        """Update lookup indexes."""
        for cluster in clusters:
            cid = cluster.cluster_id
            
            if tenant_id := event.get("tenant_id"):
                self._tenant_index[tenant_id].add(cid)
            
            if source := event.get("source"):
                self._source_index[source].add(cid)
            
            if corr_id := event.get("correlation_id"):
                self._correlation_id_index[corr_id].add(cid)
            
            if event_type_str := event.get("event_type"):
                try:
                    event_type = TelemetryEventType(event_type_str)
                    self._event_type_index[event_type].add(cid)
                except ValueError:
                    pass
    
    def _prune_recent_events(self) -> None:
        """Remove old events from recent list."""
        cutoff = time.time() - self._default_window
        self._recent_events = [
            e for e in self._recent_events
            if e.get("timestamp", 0) >= cutoff
        ]
    
    def _prune_clusters(self) -> None:
        """Remove old or excess clusters."""
        now = time.time()
        
        # Remove clusters older than window
        to_remove = []
        for cid, cluster in self._clusters.items():
            if cluster.events:
                newest = max(e.get("timestamp", 0) for e in cluster.events)
                if now - newest > self._default_window:
                    to_remove.append(cid)
        
        for cid in to_remove:
            self._remove_cluster(cid)
        
        # Trim to max clusters (remove oldest)
        while len(self._clusters) > self._max_clusters:
            oldest_id = min(
                self._clusters.keys(),
                key=lambda k: self._clusters[k].created_at
            )
            self._remove_cluster(oldest_id)
    
    def _remove_cluster(self, cluster_id: str) -> None:
        """Remove a cluster and clean up indexes."""
        cluster = self._clusters.pop(cluster_id, None)
        if not cluster:
            return
        
        # Clean up indexes
        for tenant_id in cluster.tenant_ids:
            self._tenant_index[tenant_id].discard(cluster_id)
        
        for source in cluster.sources:
            self._source_index[source].discard(cluster_id)
    
    def _build_template_context(self, cluster: CorrelationCluster) -> Dict[str, Any]:
        """Build context for template formatting."""
        return {
            "tenant_id": next(iter(cluster.tenant_ids), "unknown"),
            "tenant_ids": ", ".join(cluster.tenant_ids),
            "source": next(iter(cluster.sources), "unknown"),
            "sources": ", ".join(cluster.sources),
            "event_count": len(cluster.events),
            "trigger_event": cluster.events[0].get("event_type", "unknown") if cluster.events else "unknown",
            "model_name": cluster.events[0].get("payload", {}).get("model", "unknown") if cluster.events else "unknown",
        }
    
    def _emit_cluster(self, cluster: CorrelationCluster) -> None:
        """Emit cluster to dashboard."""
        # Run analysis first
        self.analyze_cluster(cluster.cluster_id)
        
        # Convert and emit
        anomaly = cluster.to_anomaly_correlation()
        get_dashboard_registry().emit(anomaly.to_dashboard_event())


# =============================================================================
# Global Engine Instance
# =============================================================================

_global_engine: Optional[CorrelationEngine] = None


def get_correlation_engine() -> CorrelationEngine:
    """Get or create global correlation engine."""
    global _global_engine
    if _global_engine is None:
        _global_engine = CorrelationEngine()
    return _global_engine


# =============================================================================
# Convenience Functions
# =============================================================================

def correlate_event(event: TelemetryEvent) -> List[CorrelationCluster]:
    """Process an event through the global correlation engine."""
    return get_correlation_engine().process_event(event)


def get_active_correlations(min_strength: float = 0.3) -> List[AnomalyCorrelation]:
    """Get all active significant correlations."""
    clusters = get_correlation_engine().get_significant_clusters(min_strength=min_strength)
    return [c.to_anomaly_correlation() for c in clusters]


def analyze_tenant_correlations(tenant_id: str) -> List[Dict[str, Any]]:
    """Analyze all correlations involving a specific tenant."""
    engine = get_correlation_engine()
    clusters = engine.get_clusters_for_tenant(tenant_id)
    
    analyses = []
    for cluster in clusters:
        analysis = engine.analyze_cluster(cluster.cluster_id)
        if analysis:
            analyses.append(analysis)
    
    return analyses
