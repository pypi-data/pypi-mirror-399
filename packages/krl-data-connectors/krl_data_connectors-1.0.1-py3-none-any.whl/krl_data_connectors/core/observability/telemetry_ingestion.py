# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
Telemetry Ingestion - Phase 3 Week 18

Real-time telemetry ingestion pipeline for defense events.
Supports:
- Async batch ingestion (< 10ms target)
- Event correlation
- Anomaly flagging
- DLS component scoring
- Multi-sink routing (memory, file, remote)

Performance Budgets:
- Telemetry batch: < 10ms
- Event correlation: < 5ms
- Sink write: < 2ms per sink
"""

from __future__ import annotations

import asyncio
import json
import queue
import threading
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    List,
    Optional,
    Protocol,
    Set,
    Tuple,
)
import uuid


# =============================================================================
# Performance Budgets
# =============================================================================

BUDGET_TELEMETRY_BATCH_MS = 10.0
BUDGET_CORRELATION_MS = 5.0
BUDGET_SINK_WRITE_MS = 2.0

# Batch configuration
DEFAULT_BATCH_SIZE = 100
DEFAULT_FLUSH_INTERVAL_SEC = 1.0
MAX_QUEUE_SIZE = 10_000


# =============================================================================
# Event Types
# =============================================================================

class TelemetryEventType(Enum):
    """Types of telemetry events."""
    
    # Enforcement events
    ENFORCEMENT_DECISION = "enforcement.decision"
    ENFORCEMENT_ACTION = "enforcement.action"
    ENFORCEMENT_RESULT = "enforcement.result"
    
    # ML events
    ML_INFERENCE = "ml.inference"
    ML_PREDICTION = "ml.prediction"
    ML_DRIFT = "ml.drift"
    ML_RETRAIN = "ml.retrain"
    
    # License events
    LICENSE_VALIDATION = "license.validation"
    LICENSE_REFRESH = "license.refresh"
    LICENSE_ANOMALY = "license.anomaly"
    
    # Policy events
    POLICY_PUSH = "policy.push"
    POLICY_APPLY = "policy.apply"
    POLICY_ROLLBACK = "policy.rollback"
    
    # Threat events
    THREAT_DETECTED = "threat.detected"
    THREAT_RESPONSE = "threat.response"
    THREAT_MITIGATED = "threat.mitigated"
    
    # Access events
    API_REQUEST = "api.request"
    API_RESPONSE = "api.response"
    CROWN_JEWEL_ACCESS = "crownjewel.access"
    
    # System events
    SYSTEM_HEALTH = "system.health"
    SYSTEM_ERROR = "system.error"
    SYSTEM_METRIC = "system.metric"
    
    # Revenue events
    TIER_CHECK = "tier.check"
    TIER_VIOLATION = "tier.violation"
    BILLING_EVENT = "billing.event"


# =============================================================================
# Telemetry Event
# =============================================================================

@dataclass
class TelemetryEvent:
    """
    A single telemetry event.
    
    Attributes:
        event_id: Unique event identifier
        event_type: Type of telemetry event
        timestamp: Unix timestamp (ms precision)
        source: Event source (service/component)
        correlation_id: Request correlation ID
        tenant_id: Tenant identifier
        payload: Event-specific data
        tags: Event tags for filtering
        dls_component: DLS component this affects (if any)
    """
    event_id: str
    event_type: TelemetryEventType
    timestamp: float
    source: str
    payload: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    tenant_id: Optional[str] = None
    tags: Set[str] = field(default_factory=set)
    dls_component: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        event_type: TelemetryEventType,
        source: str,
        payload: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> "TelemetryEvent":
        """Factory method to create event with auto-generated ID and timestamp."""
        return cls(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            timestamp=time.time(),
            source=source,
            payload=payload or {},
            **kwargs,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp,
            "source": self.source,
            "payload": self.payload,
            "correlation_id": self.correlation_id,
            "tenant_id": self.tenant_id,
            "tags": list(self.tags),
            "dls_component": self.dls_component,
        }
    
    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TelemetryEvent":
        """Deserialize from dictionary."""
        return cls(
            event_id=data["event_id"],
            event_type=TelemetryEventType(data["event_type"]),
            timestamp=data["timestamp"],
            source=data["source"],
            payload=data.get("payload", {}),
            correlation_id=data.get("correlation_id"),
            tenant_id=data.get("tenant_id"),
            tags=set(data.get("tags", [])),
            dls_component=data.get("dls_component"),
        )


# =============================================================================
# Telemetry Sink Interface
# =============================================================================

class TelemetrySink(ABC):
    """
    Abstract base for telemetry event sinks.
    
    Sinks receive batches of events and persist them
    to their backing store.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Sink identifier."""
        ...
    
    @abstractmethod
    async def write_batch(self, events: List[TelemetryEvent]) -> bool:
        """
        Write a batch of events.
        
        Returns True if all events were written successfully.
        """
        ...
    
    @abstractmethod
    async def close(self) -> None:
        """Close the sink and release resources."""
        ...


class MemorySink(TelemetrySink):
    """
    In-memory sink for testing and development.
    
    Stores events in a bounded list.
    """
    
    def __init__(self, max_events: int = 10_000):
        self._events: List[TelemetryEvent] = []
        self._max_events = max_events
        self._lock = asyncio.Lock()
    
    @property
    def name(self) -> str:
        return "memory"
    
    async def write_batch(self, events: List[TelemetryEvent]) -> bool:
        async with self._lock:
            self._events.extend(events)
            # Trim to max size
            if len(self._events) > self._max_events:
                self._events = self._events[-self._max_events:]
        return True
    
    async def close(self) -> None:
        self._events.clear()
    
    def get_events(
        self,
        event_type: Optional[TelemetryEventType] = None,
        source: Optional[str] = None,
        since: Optional[float] = None,
    ) -> List[TelemetryEvent]:
        """Query stored events."""
        results = self._events
        
        if event_type:
            results = [e for e in results if e.event_type == event_type]
        if source:
            results = [e for e in results if e.source == source]
        if since:
            results = [e for e in results if e.timestamp >= since]
        
        return results


class FileSink(TelemetrySink):
    """
    File-based sink for local persistence.
    
    Writes events as JSONL (one JSON object per line).
    """
    
    def __init__(self, path: str, rotate_mb: int = 100):
        self._path = path
        self._rotate_mb = rotate_mb
        self._lock = asyncio.Lock()
    
    @property
    def name(self) -> str:
        return f"file:{self._path}"
    
    async def write_batch(self, events: List[TelemetryEvent]) -> bool:
        async with self._lock:
            try:
                with open(self._path, "a") as f:
                    for event in events:
                        f.write(event.to_json() + "\n")
                return True
            except Exception:
                return False
    
    async def close(self) -> None:
        pass  # Nothing to close


class CallbackSink(TelemetrySink):
    """
    Callback-based sink for custom processing.
    
    Useful for integrating with external systems.
    """
    
    def __init__(
        self,
        name: str,
        callback: Callable[[List[TelemetryEvent]], bool],
    ):
        self._name = name
        self._callback = callback
    
    @property
    def name(self) -> str:
        return self._name
    
    async def write_batch(self, events: List[TelemetryEvent]) -> bool:
        return self._callback(events)
    
    async def close(self) -> None:
        pass


# =============================================================================
# Event Correlator
# =============================================================================

class EventCorrelator:
    """
    Correlates related telemetry events.
    
    Uses correlation IDs and temporal proximity to
    link events into sequences.
    """
    
    def __init__(
        self,
        window_sec: float = 60.0,
        max_sequences: int = 10_000,
    ):
        self._window_sec = window_sec
        self._max_sequences = max_sequences
        self._sequences: Dict[str, List[TelemetryEvent]] = defaultdict(list)
        self._lock = threading.Lock()
    
    def correlate(self, event: TelemetryEvent) -> Optional[str]:
        """
        Add event to correlation sequence.
        
        Returns sequence ID if correlated with existing sequence.
        """
        if not event.correlation_id:
            return None
        
        with self._lock:
            seq_id = event.correlation_id
            self._sequences[seq_id].append(event)
            
            # Prune old sequences
            self._prune_sequences()
            
            return seq_id
    
    def get_sequence(self, correlation_id: str) -> List[TelemetryEvent]:
        """Get all events in a correlation sequence."""
        with self._lock:
            return self._sequences.get(correlation_id, []).copy()
    
    def _prune_sequences(self) -> None:
        """Remove old sequences outside the window."""
        cutoff = time.time() - self._window_sec
        
        to_remove = []
        for seq_id, events in self._sequences.items():
            if not events or events[-1].timestamp < cutoff:
                to_remove.append(seq_id)
        
        for seq_id in to_remove:
            del self._sequences[seq_id]
        
        # Trim to max size
        while len(self._sequences) > self._max_sequences:
            oldest_id = min(
                self._sequences.keys(),
                key=lambda k: self._sequences[k][0].timestamp
            )
            del self._sequences[oldest_id]


# =============================================================================
# DLS Scorer
# =============================================================================

class DLSScorer:
    """
    Defense Liveness Score calculator from telemetry.
    
    Aggregates telemetry events to compute DLS components:
    - Detection Accuracy (DA)
    - Enforcement Latency (EL)
    - Telemetry Coverage (TC)
    - Policy Delivery Success (PDS)
    - False Positive Rate (FPR)
    - Drift Rate (DR)
    - Chaos Survival (CS)
    """
    
    def __init__(self, window_sec: float = 300.0):
        self._window_sec = window_sec
        self._events: List[TelemetryEvent] = []
        self._lock = threading.Lock()
    
    def ingest(self, event: TelemetryEvent) -> None:
        """Add event for DLS calculation."""
        with self._lock:
            self._events.append(event)
            self._prune_old()
    
    def _prune_old(self) -> None:
        """Remove events outside window."""
        cutoff = time.time() - self._window_sec
        self._events = [e for e in self._events if e.timestamp >= cutoff]
    
    def compute_scores(self) -> Dict[str, float]:
        """
        Compute DLS component scores.
        
        Returns dict with scores 0-100 for each component.
        """
        with self._lock:
            self._prune_old()
            
            scores = {
                "detection_accuracy": self._calc_detection_accuracy(),
                "enforcement_latency": self._calc_enforcement_latency(),
                "telemetry_coverage": self._calc_telemetry_coverage(),
                "policy_delivery": self._calc_policy_delivery(),
                "false_positive_rate": self._calc_false_positive_rate(),
                "drift_rate": self._calc_drift_rate(),
                "chaos_survival": self._calc_chaos_survival(),
            }
            
            return scores
    
    def compute_dls(self) -> float:
        """
        Compute aggregate Defense Liveness Score.
        
        DLS = (0.20 × DA) + (0.15 × EL) + (0.15 × TC) + 
              (0.15 × PDS) + (0.15 × (100 - FPR)) + 
              (0.10 × (100 - DR)) + (0.10 × CS)
        """
        scores = self.compute_scores()
        
        dls = (
            0.20 * scores["detection_accuracy"] +
            0.15 * scores["enforcement_latency"] +
            0.15 * scores["telemetry_coverage"] +
            0.15 * scores["policy_delivery"] +
            0.15 * (100 - scores["false_positive_rate"]) +
            0.10 * (100 - scores["drift_rate"]) +
            0.10 * scores["chaos_survival"]
        )
        
        return min(100.0, max(0.0, dls))
    
    def _calc_detection_accuracy(self) -> float:
        """Calculate detection accuracy from threat events."""
        threat_events = [
            e for e in self._events
            if e.event_type in (
                TelemetryEventType.THREAT_DETECTED,
                TelemetryEventType.THREAT_MITIGATED,
            )
        ]
        
        if not threat_events:
            return 95.0  # Default when no threats
        
        detected = len([e for e in threat_events if e.event_type == TelemetryEventType.THREAT_DETECTED])
        mitigated = len([e for e in threat_events if e.event_type == TelemetryEventType.THREAT_MITIGATED])
        
        if detected == 0:
            return 100.0
        
        return min(100.0, (mitigated / detected) * 100)
    
    def _calc_enforcement_latency(self) -> float:
        """Calculate enforcement latency score."""
        enforcement_events = [
            e for e in self._events
            if e.event_type == TelemetryEventType.ENFORCEMENT_RESULT
        ]
        
        if not enforcement_events:
            return 95.0
        
        # Get latencies from payloads
        latencies = [
            e.payload.get("latency_ms", 50.0)
            for e in enforcement_events
        ]
        
        avg_latency = sum(latencies) / len(latencies)
        
        # Score: 100 at 0ms, 0 at 100ms+
        return max(0.0, 100.0 - avg_latency)
    
    def _calc_telemetry_coverage(self) -> float:
        """Calculate telemetry coverage based on event diversity."""
        if not self._events:
            return 50.0
        
        # Count unique event types seen
        event_types_seen = len(set(e.event_type for e in self._events))
        total_event_types = len(TelemetryEventType)
        
        return (event_types_seen / total_event_types) * 100
    
    def _calc_policy_delivery(self) -> float:
        """Calculate policy delivery success rate."""
        policy_events = [
            e for e in self._events
            if e.event_type in (
                TelemetryEventType.POLICY_PUSH,
                TelemetryEventType.POLICY_APPLY,
            )
        ]
        
        if not policy_events:
            return 95.0
        
        pushed = len([e for e in policy_events if e.event_type == TelemetryEventType.POLICY_PUSH])
        applied = len([e for e in policy_events if e.event_type == TelemetryEventType.POLICY_APPLY])
        
        if pushed == 0:
            return 100.0
        
        return min(100.0, (applied / pushed) * 100)
    
    def _calc_false_positive_rate(self) -> float:
        """Calculate false positive rate from enforcement events."""
        enforcement_events = [
            e for e in self._events
            if e.event_type == TelemetryEventType.ENFORCEMENT_RESULT
        ]
        
        if not enforcement_events:
            return 5.0  # Default low FPR
        
        false_positives = len([
            e for e in enforcement_events
            if e.payload.get("false_positive", False)
        ])
        
        return (false_positives / len(enforcement_events)) * 100
    
    def _calc_drift_rate(self) -> float:
        """Calculate model drift rate from ML events."""
        ml_events = [
            e for e in self._events
            if e.event_type == TelemetryEventType.ML_DRIFT
        ]
        
        if not ml_events:
            return 5.0  # Default low drift
        
        # More drift events = higher drift rate
        # Normalize: 10+ drift events in window = 100% drift
        return min(100.0, len(ml_events) * 10)
    
    def _calc_chaos_survival(self) -> float:
        """Calculate chaos survival from system events."""
        system_events = [
            e for e in self._events
            if e.event_type in (
                TelemetryEventType.SYSTEM_HEALTH,
                TelemetryEventType.SYSTEM_ERROR,
            )
        ]
        
        if not system_events:
            return 95.0
        
        errors = len([e for e in system_events if e.event_type == TelemetryEventType.SYSTEM_ERROR])
        health = len([e for e in system_events if e.event_type == TelemetryEventType.SYSTEM_HEALTH])
        
        if errors == 0:
            return 100.0
        
        # More health events relative to errors = higher survival
        return max(0.0, 100.0 - (errors / (health + errors)) * 100)


# =============================================================================
# Telemetry Ingestion Pipeline
# =============================================================================

class TelemetryIngestion:
    """
    Real-time telemetry ingestion pipeline.
    
    Features:
    - Async batch processing (< 10ms budget)
    - Event correlation
    - DLS scoring
    - Multi-sink routing
    """
    
    def __init__(
        self,
        batch_size: int = DEFAULT_BATCH_SIZE,
        flush_interval_sec: float = DEFAULT_FLUSH_INTERVAL_SEC,
        enable_correlation: bool = True,
        enable_dls: bool = True,
    ):
        self._batch_size = batch_size
        self._flush_interval_sec = flush_interval_sec
        self._enable_correlation = enable_correlation
        self._enable_dls = enable_dls
        
        # Event queue
        self._queue: queue.Queue[TelemetryEvent] = queue.Queue(maxsize=MAX_QUEUE_SIZE)
        
        # Sinks
        self._sinks: List[TelemetrySink] = []
        
        # Correlator
        self._correlator = EventCorrelator() if enable_correlation else None
        
        # DLS Scorer
        self._dls_scorer = DLSScorer() if enable_dls else None
        
        # Processing state
        self._running = False
        self._flush_task: Optional[asyncio.Task] = None
        self._stats = {
            "events_received": 0,
            "events_flushed": 0,
            "batches_flushed": 0,
            "flush_time_total_ms": 0.0,
        }
    
    def add_sink(self, sink: TelemetrySink) -> None:
        """Add a telemetry sink."""
        self._sinks.append(sink)
    
    def ingest(self, event: TelemetryEvent) -> bool:
        """
        Ingest a single telemetry event.
        
        Returns False if queue is full.
        """
        try:
            self._queue.put_nowait(event)
            self._stats["events_received"] += 1
            
            # Correlate
            if self._correlator:
                self._correlator.correlate(event)
            
            # Update DLS
            if self._dls_scorer:
                self._dls_scorer.ingest(event)
            
            return True
        except queue.Full:
            return False
    
    def ingest_batch(self, events: List[TelemetryEvent]) -> int:
        """
        Ingest multiple events.
        
        Returns count of successfully queued events.
        """
        count = 0
        for event in events:
            if self.ingest(event):
                count += 1
        return count
    
    async def flush(self) -> int:
        """
        Flush pending events to sinks.
        
        Returns count of events flushed.
        """
        start_time = time.time()
        
        # Drain queue
        events = []
        while not self._queue.empty() and len(events) < self._batch_size:
            try:
                events.append(self._queue.get_nowait())
            except queue.Empty:
                break
        
        if not events:
            return 0
        
        # Write to all sinks
        for sink in self._sinks:
            sink_start = time.time()
            try:
                await sink.write_batch(events)
            except Exception:
                pass  # Log error but continue
            
            sink_time_ms = (time.time() - sink_start) * 1000
            if sink_time_ms > BUDGET_SINK_WRITE_MS:
                # Budget exceeded - could log warning
                pass
        
        # Update stats
        flush_time_ms = (time.time() - start_time) * 1000
        self._stats["events_flushed"] += len(events)
        self._stats["batches_flushed"] += 1
        self._stats["flush_time_total_ms"] += flush_time_ms
        
        return len(events)
    
    async def start(self) -> None:
        """Start the ingestion pipeline."""
        if self._running:
            return
        
        self._running = True
        self._flush_task = asyncio.create_task(self._flush_loop())
    
    async def stop(self) -> None:
        """Stop the ingestion pipeline and flush remaining events."""
        self._running = False
        
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
        
        # Final flush
        while not self._queue.empty():
            await self.flush()
        
        # Close sinks
        for sink in self._sinks:
            await sink.close()
    
    async def _flush_loop(self) -> None:
        """Background flush loop."""
        while self._running:
            await self.flush()
            await asyncio.sleep(self._flush_interval_sec)
    
    def get_dls(self) -> Optional[float]:
        """Get current Defense Liveness Score."""
        if self._dls_scorer:
            return self._dls_scorer.compute_dls()
        return None
    
    def get_dls_components(self) -> Optional[Dict[str, float]]:
        """Get DLS component scores."""
        if self._dls_scorer:
            return self._dls_scorer.compute_scores()
        return None
    
    def get_correlation_sequence(self, correlation_id: str) -> List[TelemetryEvent]:
        """Get correlated event sequence."""
        if self._correlator:
            return self._correlator.get_sequence(correlation_id)
        return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get ingestion statistics."""
        stats = self._stats.copy()
        stats["queue_size"] = self._queue.qsize()
        stats["sinks"] = [s.name for s in self._sinks]
        
        if stats["batches_flushed"] > 0:
            stats["avg_flush_time_ms"] = (
                stats["flush_time_total_ms"] / stats["batches_flushed"]
            )
        else:
            stats["avg_flush_time_ms"] = 0.0
        
        if self._dls_scorer:
            stats["current_dls"] = self._dls_scorer.compute_dls()
        
        return stats


# =============================================================================
# Convenience Functions
# =============================================================================

# Global ingestion instance
_global_ingestion: Optional[TelemetryIngestion] = None


def get_global_ingestion() -> TelemetryIngestion:
    """Get or create global telemetry ingestion instance."""
    global _global_ingestion
    
    if _global_ingestion is None:
        _global_ingestion = TelemetryIngestion()
        _global_ingestion.add_sink(MemorySink())  # Default memory sink
    
    return _global_ingestion


def emit_event(
    event_type: TelemetryEventType,
    source: str,
    payload: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> bool:
    """
    Emit a telemetry event to the global ingestion pipeline.
    
    Usage:
        emit_event(
            TelemetryEventType.ML_INFERENCE,
            "ml-service",
            {"model": "anomaly-v2", "latency_ms": 4.2},
        )
    """
    event = TelemetryEvent.create(
        event_type=event_type,
        source=source,
        payload=payload,
        **kwargs,
    )
    
    return get_global_ingestion().ingest(event)
