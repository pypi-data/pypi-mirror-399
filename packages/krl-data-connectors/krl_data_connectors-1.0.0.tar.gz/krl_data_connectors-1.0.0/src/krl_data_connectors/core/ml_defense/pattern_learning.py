"""
Pattern Learning for KRL Defense System.

Week 15: ML-enhanced behavioral pattern recognition and learning.
Learns and recognizes usage patterns for enhanced protection.
"""

import hashlib
import logging
import math
import statistics
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from collections import Counter, deque
import json

logger = logging.getLogger(__name__)


class PatternType(Enum):
    """Types of behavioral patterns."""
    TEMPORAL = "temporal"  # Time-based patterns
    SEQUENTIAL = "sequential"  # Action sequences
    VOLUMETRIC = "volumetric"  # Volume/rate patterns
    CONTEXTUAL = "contextual"  # Context-based patterns
    COMPOSITE = "composite"  # Multi-dimensional patterns
    CYCLIC = "cyclic"  # Repeating cycles
    TREND = "trend"  # Trend patterns


class PatternConfidence(Enum):
    """Confidence levels for patterns."""
    TENTATIVE = "tentative"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ESTABLISHED = "established"


class LearningMode(Enum):
    """Pattern learning modes."""
    SUPERVISED = "supervised"
    UNSUPERVISED = "unsupervised"
    SEMI_SUPERVISED = "semi_supervised"
    REINFORCEMENT = "reinforcement"


@dataclass
class Event:
    """Base event for pattern learning."""
    event_id: str
    event_type: str
    timestamp: datetime
    source_id: str
    properties: Dict[str, Any] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)
    
    def to_sequence_item(self) -> str:
        """Convert to sequence representation."""
        return f"{self.event_type}:{','.join(f'{k}={v}' for k, v in sorted(self.properties.items()))}"


@dataclass
class Pattern:
    """Learned behavioral pattern."""
    pattern_id: str
    pattern_type: PatternType
    name: str
    description: str
    confidence: PatternConfidence
    support: float  # Frequency support (0-1)
    occurrences: int
    first_seen: datetime
    last_seen: datetime
    features: Dict[str, Any] = field(default_factory=dict)
    conditions: List[str] = field(default_factory=list)
    is_normal: bool = True  # Normal vs anomalous pattern
    source_ids: Set[str] = field(default_factory=set)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "pattern_id": self.pattern_id,
            "pattern_type": self.pattern_type.value,
            "name": self.name,
            "description": self.description,
            "confidence": self.confidence.value,
            "support": self.support,
            "occurrences": self.occurrences,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "features": self.features,
            "conditions": self.conditions,
            "is_normal": self.is_normal,
            "source_ids": list(self.source_ids)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Pattern':
        """Deserialize from dictionary."""
        return cls(
            pattern_id=data["pattern_id"],
            pattern_type=PatternType(data["pattern_type"]),
            name=data["name"],
            description=data["description"],
            confidence=PatternConfidence(data["confidence"]),
            support=data["support"],
            occurrences=data["occurrences"],
            first_seen=datetime.fromisoformat(data["first_seen"]),
            last_seen=datetime.fromisoformat(data["last_seen"]),
            features=data.get("features", {}),
            conditions=data.get("conditions", []),
            is_normal=data.get("is_normal", True),
            source_ids=set(data.get("source_ids", []))
        )


@dataclass
class PatternMatch:
    """Result of pattern matching."""
    pattern: Pattern
    match_score: float  # 0-1 how well it matches
    matched_events: List[Event]
    match_context: Dict[str, Any] = field(default_factory=dict)


@dataclass 
class SequenceRule:
    """Rule for sequence pattern detection."""
    antecedent: List[str]  # Preceding events
    consequent: str  # Expected next event
    support: float
    confidence: float
    lift: float
    
    def __hash__(self):
        return hash((tuple(self.antecedent), self.consequent))


class PatternLearner(ABC):
    """Base class for pattern learning algorithms."""
    
    def __init__(self, mode: LearningMode):
        self.mode = mode
        self.learned_patterns: List[Pattern] = []
        self.training_events: List[Event] = []
        self.is_trained = False
    
    @abstractmethod
    def learn(self, events: List[Event]) -> List[Pattern]:
        """Learn patterns from events."""
        pass
    
    @abstractmethod
    def match(self, events: List[Event]) -> List[PatternMatch]:
        """Match events against learned patterns."""
        pass
    
    @abstractmethod
    def update(self, event: Event) -> Optional[Pattern]:
        """Incrementally update with new event."""
        pass


class TemporalPatternLearner(PatternLearner):
    """Learn temporal patterns (time-of-day, day-of-week, etc.)."""
    
    def __init__(self, bin_hours: int = 1, min_support: float = 0.1):
        super().__init__(LearningMode.UNSUPERVISED)
        self.bin_hours = bin_hours
        self.min_support = min_support
        self.hourly_distributions: Dict[str, Dict[int, int]] = {}  # event_type -> hour -> count
        self.daily_distributions: Dict[str, Dict[int, int]] = {}  # event_type -> day -> count
        self.total_counts: Dict[str, int] = {}
    
    def _get_hour_bin(self, dt: datetime) -> int:
        """Get hour bin for datetime."""
        return dt.hour // self.bin_hours
    
    def learn(self, events: List[Event]) -> List[Pattern]:
        """Learn temporal patterns from events."""
        self.training_events = events
        
        # Build distributions
        for event in events:
            event_type = event.event_type
            
            if event_type not in self.hourly_distributions:
                self.hourly_distributions[event_type] = {}
                self.daily_distributions[event_type] = {}
                self.total_counts[event_type] = 0
            
            hour_bin = self._get_hour_bin(event.timestamp)
            day = event.timestamp.weekday()
            
            self.hourly_distributions[event_type][hour_bin] = \
                self.hourly_distributions[event_type].get(hour_bin, 0) + 1
            self.daily_distributions[event_type][day] = \
                self.daily_distributions[event_type].get(day, 0) + 1
            self.total_counts[event_type] += 1
        
        # Extract patterns
        patterns = []
        
        for event_type, hourly in self.hourly_distributions.items():
            total = self.total_counts[event_type]
            if total == 0:
                continue
            
            # Find peak hours
            for hour, count in hourly.items():
                support = count / total
                if support >= self.min_support:
                    pattern = Pattern(
                        pattern_id=self._generate_id(event_type, "hour", hour),
                        pattern_type=PatternType.TEMPORAL,
                        name=f"Peak hour for {event_type}",
                        description=f"{event_type} frequently occurs at hour bin {hour}",
                        confidence=self._calculate_confidence(support, count),
                        support=support,
                        occurrences=count,
                        first_seen=events[0].timestamp if events else datetime.now(),
                        last_seen=events[-1].timestamp if events else datetime.now(),
                        features={
                            "event_type": event_type,
                            "hour_bin": hour,
                            "hour_range": f"{hour * self.bin_hours:02d}:00-{(hour + 1) * self.bin_hours - 1:02d}:59"
                        }
                    )
                    patterns.append(pattern)
        
        self.learned_patterns = patterns
        self.is_trained = True
        logger.info(f"Learned {len(patterns)} temporal patterns")
        return patterns
    
    def _calculate_confidence(self, support: float, count: int) -> PatternConfidence:
        """Calculate pattern confidence."""
        if support >= 0.5 and count >= 100:
            return PatternConfidence.ESTABLISHED
        elif support >= 0.3 and count >= 50:
            return PatternConfidence.HIGH
        elif support >= 0.2 and count >= 20:
            return PatternConfidence.MEDIUM
        elif support >= 0.1 and count >= 10:
            return PatternConfidence.LOW
        else:
            return PatternConfidence.TENTATIVE
    
    def _generate_id(self, *parts) -> str:
        """Generate pattern ID."""
        data = ":".join(str(p) for p in parts)
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def match(self, events: List[Event]) -> List[PatternMatch]:
        """Match events against temporal patterns."""
        if not self.is_trained or not events:
            return []
        
        matches = []
        
        for pattern in self.learned_patterns:
            event_type = pattern.features.get("event_type")
            hour_bin = pattern.features.get("hour_bin")
            
            if event_type is None or hour_bin is None:
                continue
            
            matched_events = []
            for event in events:
                if event.event_type == event_type and self._get_hour_bin(event.timestamp) == hour_bin:
                    matched_events.append(event)
            
            if matched_events:
                match_score = len(matched_events) / len(events)
                matches.append(PatternMatch(
                    pattern=pattern,
                    match_score=match_score,
                    matched_events=matched_events
                ))
        
        return sorted(matches, key=lambda m: m.match_score, reverse=True)
    
    def update(self, event: Event) -> Optional[Pattern]:
        """Update distributions with new event."""
        event_type = event.event_type
        
        if event_type not in self.hourly_distributions:
            self.hourly_distributions[event_type] = {}
            self.daily_distributions[event_type] = {}
            self.total_counts[event_type] = 0
        
        hour_bin = self._get_hour_bin(event.timestamp)
        day = event.timestamp.weekday()
        
        self.hourly_distributions[event_type][hour_bin] = \
            self.hourly_distributions[event_type].get(hour_bin, 0) + 1
        self.daily_distributions[event_type][day] = \
            self.daily_distributions[event_type].get(day, 0) + 1
        self.total_counts[event_type] += 1
        
        return None  # Patterns updated lazily


class SequencePatternLearner(PatternLearner):
    """Learn sequential patterns using sequence mining."""
    
    def __init__(self, min_support: float = 0.1, min_confidence: float = 0.5, max_length: int = 5):
        super().__init__(LearningMode.UNSUPERVISED)
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.max_length = max_length
        self.sequence_rules: List[SequenceRule] = []
        self.event_sequences: List[List[str]] = []
        self.item_counts: Counter = Counter()
    
    def _events_to_sequences(self, events: List[Event], by_source: bool = True) -> List[List[str]]:
        """Convert events to sequences."""
        if by_source:
            # Group by source
            source_events: Dict[str, List[Event]] = {}
            for event in events:
                if event.source_id not in source_events:
                    source_events[event.source_id] = []
                source_events[event.source_id].append(event)
            
            sequences = []
            for source_id, evts in source_events.items():
                sorted_evts = sorted(evts, key=lambda e: e.timestamp)
                seq = [e.event_type for e in sorted_evts]
                sequences.append(seq)
            
            return sequences
        else:
            sorted_events = sorted(events, key=lambda e: e.timestamp)
            return [[e.event_type for e in sorted_events]]
    
    def _find_frequent_sequences(self, sequences: List[List[str]], k: int) -> Dict[Tuple[str, ...], int]:
        """Find frequent k-sequences using Apriori-like approach."""
        if k == 1:
            # Count single items
            counts: Dict[Tuple[str, ...], int] = {}
            for seq in sequences:
                for item in seq:
                    key = (item,)
                    counts[key] = counts.get(key, 0) + 1
            return counts
        
        # Get frequent (k-1)-sequences
        prev_frequent = self._find_frequent_sequences(sequences, k - 1)
        min_count = int(self.min_support * len(sequences))
        prev_items = {seq for seq, count in prev_frequent.items() if count >= min_count}
        
        # Count k-sequences
        counts: Dict[Tuple[str, ...], int] = {}
        for seq in sequences:
            for i in range(len(seq) - k + 1):
                subsequence = tuple(seq[i:i + k])
                # Check if all (k-1) subsequences are frequent
                valid = True
                for j in range(k):
                    sub = subsequence[:j] + subsequence[j+1:]
                    if sub not in prev_items:
                        valid = False
                        break
                
                if valid:
                    counts[subsequence] = counts.get(subsequence, 0) + 1
        
        return counts
    
    def _generate_rules(self, frequent_sequences: Dict[int, Dict[Tuple[str, ...], int]], 
                        total_sequences: int) -> List[SequenceRule]:
        """Generate association rules from frequent sequences."""
        rules = []
        
        for k in range(2, self.max_length + 1):
            if k not in frequent_sequences:
                continue
            
            for seq, count in frequent_sequences[k].items():
                support = count / total_sequences
                
                # Generate rules: antecedent -> consequent
                for i in range(1, k):
                    antecedent = list(seq[:i])
                    consequent = seq[i]
                    
                    # Calculate confidence
                    ant_key = tuple(antecedent)
                    if k - 1 in frequent_sequences and ant_key in frequent_sequences[k - 1]:
                        ant_count = frequent_sequences[k - 1][ant_key]
                        confidence = count / ant_count if ant_count > 0 else 0
                        
                        # Calculate lift
                        conseq_count = frequent_sequences[1].get((consequent,), 1)
                        expected = (ant_count / total_sequences) * (conseq_count / total_sequences)
                        lift = (count / total_sequences) / expected if expected > 0 else 1.0
                        
                        if confidence >= self.min_confidence:
                            rule = SequenceRule(
                                antecedent=antecedent,
                                consequent=consequent,
                                support=support,
                                confidence=confidence,
                                lift=lift
                            )
                            rules.append(rule)
        
        return rules
    
    def learn(self, events: List[Event]) -> List[Pattern]:
        """Learn sequential patterns from events."""
        self.training_events = events
        
        # Convert to sequences
        self.event_sequences = self._events_to_sequences(events)
        total = len(self.event_sequences)
        
        if total == 0:
            return []
        
        # Find frequent sequences of all lengths
        frequent_sequences: Dict[int, Dict[Tuple[str, ...], int]] = {}
        min_count = int(self.min_support * total)
        
        for k in range(1, self.max_length + 1):
            counts = self._find_frequent_sequences(self.event_sequences, k)
            frequent = {seq: count for seq, count in counts.items() if count >= min_count}
            
            if not frequent:
                break
            
            frequent_sequences[k] = frequent
        
        # Generate rules
        self.sequence_rules = self._generate_rules(frequent_sequences, total)
        
        # Convert rules to patterns
        patterns = []
        for rule in self.sequence_rules:
            pattern = Pattern(
                pattern_id=self._generate_id(rule),
                pattern_type=PatternType.SEQUENTIAL,
                name=f"{'→'.join(rule.antecedent)} → {rule.consequent}",
                description=f"After {rule.antecedent}, {rule.consequent} follows with {rule.confidence:.1%} confidence",
                confidence=self._confidence_level(rule.confidence),
                support=rule.support,
                occurrences=int(rule.support * total),
                first_seen=events[0].timestamp if events else datetime.now(),
                last_seen=events[-1].timestamp if events else datetime.now(),
                features={
                    "antecedent": rule.antecedent,
                    "consequent": rule.consequent,
                    "confidence": rule.confidence,
                    "lift": rule.lift
                }
            )
            patterns.append(pattern)
        
        self.learned_patterns = patterns
        self.is_trained = True
        logger.info(f"Learned {len(patterns)} sequential patterns from {len(self.sequence_rules)} rules")
        return patterns
    
    def _generate_id(self, rule: SequenceRule) -> str:
        """Generate pattern ID from rule."""
        data = f"{':'.join(rule.antecedent)}:{rule.consequent}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _confidence_level(self, confidence: float) -> PatternConfidence:
        """Convert confidence value to level."""
        if confidence >= 0.9:
            return PatternConfidence.ESTABLISHED
        elif confidence >= 0.7:
            return PatternConfidence.HIGH
        elif confidence >= 0.5:
            return PatternConfidence.MEDIUM
        elif confidence >= 0.3:
            return PatternConfidence.LOW
        else:
            return PatternConfidence.TENTATIVE
    
    def match(self, events: List[Event]) -> List[PatternMatch]:
        """Match events against sequential patterns."""
        if not self.is_trained or not events:
            return []
        
        sorted_events = sorted(events, key=lambda e: e.timestamp)
        event_types = [e.event_type for e in sorted_events]
        
        matches = []
        
        for rule in self.sequence_rules:
            # Find matches in sequence
            matched_indices = []
            
            for i in range(len(event_types) - len(rule.antecedent)):
                # Check antecedent match
                if event_types[i:i + len(rule.antecedent)] == rule.antecedent:
                    # Check consequent
                    if i + len(rule.antecedent) < len(event_types):
                        if event_types[i + len(rule.antecedent)] == rule.consequent:
                            matched_indices.extend(range(i, i + len(rule.antecedent) + 1))
            
            if matched_indices:
                matched_events = [sorted_events[i] for i in set(matched_indices)]
                match_score = len(matched_events) / len(events)
                
                # Find corresponding pattern
                pattern = next(
                    (p for p in self.learned_patterns 
                     if p.features.get("antecedent") == rule.antecedent 
                     and p.features.get("consequent") == rule.consequent),
                    None
                )
                
                if pattern:
                    matches.append(PatternMatch(
                        pattern=pattern,
                        match_score=match_score,
                        matched_events=matched_events
                    ))
        
        return sorted(matches, key=lambda m: m.match_score, reverse=True)
    
    def update(self, event: Event) -> Optional[Pattern]:
        """Update with new event."""
        # Simplified: just track for batch relearning
        self.training_events.append(event)
        return None
    
    def predict_next(self, recent_events: List[str]) -> List[Tuple[str, float]]:
        """Predict likely next events based on recent sequence."""
        predictions: Dict[str, float] = {}
        
        for rule in self.sequence_rules:
            # Check if recent events end with rule's antecedent
            ant_len = len(rule.antecedent)
            if len(recent_events) >= ant_len:
                if recent_events[-ant_len:] == rule.antecedent:
                    current = predictions.get(rule.consequent, 0)
                    predictions[rule.consequent] = max(current, rule.confidence)
        
        return sorted(predictions.items(), key=lambda x: x[1], reverse=True)


class VolumetricPatternLearner(PatternLearner):
    """Learn volumetric patterns (rates, volumes, bursts)."""
    
    def __init__(self, window_minutes: int = 60, min_support: float = 0.1):
        super().__init__(LearningMode.UNSUPERVISED)
        self.window_minutes = window_minutes
        self.min_support = min_support
        self.rate_baselines: Dict[str, Dict[str, float]] = {}  # event_type -> stats
        self.burst_thresholds: Dict[str, float] = {}
    
    def _calculate_rates(self, events: List[Event], event_type: str) -> Dict[str, float]:
        """Calculate rate statistics for event type."""
        type_events = [e for e in events if e.event_type == event_type]
        
        if len(type_events) < 2:
            return {"mean": 0, "std": 0, "max": 0, "min": 0}
        
        # Sort by timestamp
        sorted_events = sorted(type_events, key=lambda e: e.timestamp)
        
        # Calculate events per window
        window = timedelta(minutes=self.window_minutes)
        windows: List[int] = []
        
        start = sorted_events[0].timestamp
        end = sorted_events[-1].timestamp
        current = start
        
        while current < end:
            count = sum(1 for e in sorted_events 
                       if current <= e.timestamp < current + window)
            windows.append(count)
            current += window
        
        if not windows:
            return {"mean": 0, "std": 0, "max": 0, "min": 0}
        
        return {
            "mean": statistics.mean(windows),
            "std": statistics.stdev(windows) if len(windows) > 1 else 0,
            "max": max(windows),
            "min": min(windows),
            "windows": len(windows)
        }
    
    def learn(self, events: List[Event]) -> List[Pattern]:
        """Learn volumetric patterns."""
        self.training_events = events
        
        # Get unique event types
        event_types = set(e.event_type for e in events)
        
        patterns = []
        
        for event_type in event_types:
            stats = self._calculate_rates(events, event_type)
            self.rate_baselines[event_type] = stats
            
            if stats["mean"] == 0:
                continue
            
            # Normal rate pattern
            pattern = Pattern(
                pattern_id=self._generate_id(event_type, "rate"),
                pattern_type=PatternType.VOLUMETRIC,
                name=f"Normal rate for {event_type}",
                description=f"Expected {stats['mean']:.1f}±{stats['std']:.1f} events per {self.window_minutes}min",
                confidence=self._confidence_from_windows(stats.get("windows", 0)),
                support=1.0,  # Baseline pattern
                occurrences=int(stats.get("windows", 0)),
                first_seen=events[0].timestamp if events else datetime.now(),
                last_seen=events[-1].timestamp if events else datetime.now(),
                features={
                    "event_type": event_type,
                    "mean_rate": stats["mean"],
                    "std_rate": stats["std"],
                    "max_rate": stats["max"],
                    "min_rate": stats["min"],
                    "window_minutes": self.window_minutes
                }
            )
            patterns.append(pattern)
            
            # Calculate burst threshold
            self.burst_thresholds[event_type] = stats["mean"] + 3 * stats["std"]
        
        self.learned_patterns = patterns
        self.is_trained = True
        logger.info(f"Learned {len(patterns)} volumetric patterns")
        return patterns
    
    def _generate_id(self, *parts) -> str:
        """Generate pattern ID."""
        data = ":".join(str(p) for p in parts)
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _confidence_from_windows(self, windows: int) -> PatternConfidence:
        """Calculate confidence from number of observation windows."""
        if windows >= 1000:
            return PatternConfidence.ESTABLISHED
        elif windows >= 100:
            return PatternConfidence.HIGH
        elif windows >= 20:
            return PatternConfidence.MEDIUM
        elif windows >= 5:
            return PatternConfidence.LOW
        else:
            return PatternConfidence.TENTATIVE
    
    def match(self, events: List[Event]) -> List[PatternMatch]:
        """Match events against volumetric patterns."""
        if not self.is_trained or not events:
            return []
        
        matches = []
        
        for pattern in self.learned_patterns:
            event_type = pattern.features.get("event_type")
            if not event_type:
                continue
            
            type_events = [e for e in events if e.event_type == event_type]
            
            if not type_events:
                continue
            
            # Calculate current rate
            current_stats = self._calculate_rates(type_events, event_type)
            baseline = self.rate_baselines.get(event_type, {})
            
            if baseline.get("mean", 0) == 0:
                continue
            
            # Calculate match score based on how close to baseline
            mean_diff = abs(current_stats["mean"] - baseline["mean"])
            std = baseline.get("std", 1) or 1
            z_score = mean_diff / std
            
            # Higher match score for rates closer to baseline
            match_score = max(0, 1 - (z_score / 3))
            
            matches.append(PatternMatch(
                pattern=pattern,
                match_score=match_score,
                matched_events=type_events,
                match_context={
                    "current_rate": current_stats["mean"],
                    "baseline_rate": baseline["mean"],
                    "z_score": z_score
                }
            ))
        
        return sorted(matches, key=lambda m: m.match_score, reverse=True)
    
    def update(self, event: Event) -> Optional[Pattern]:
        """Update baselines with new event."""
        # Track events for periodic recomputation
        self.training_events.append(event)
        return None
    
    def detect_burst(self, events: List[Event], window: Optional[timedelta] = None) -> Dict[str, bool]:
        """Detect burst patterns in recent events."""
        if not self.is_trained:
            return {}
        
        window = window or timedelta(minutes=self.window_minutes)
        recent_cutoff = datetime.now() - window
        
        recent_events = [e for e in events if e.timestamp >= recent_cutoff]
        
        bursts = {}
        event_types = set(e.event_type for e in recent_events)
        
        for event_type in event_types:
            count = sum(1 for e in recent_events if e.event_type == event_type)
            threshold = self.burst_thresholds.get(event_type, float('inf'))
            bursts[event_type] = count > threshold
        
        return bursts


class CompositePatternLearner(PatternLearner):
    """Combine multiple pattern learners."""
    
    def __init__(
        self,
        learners: Optional[List[PatternLearner]] = None,
        fusion_strategy: str = "union"
    ):
        super().__init__(LearningMode.UNSUPERVISED)
        self.learners = learners or [
            TemporalPatternLearner(),
            SequencePatternLearner(),
            VolumetricPatternLearner()
        ]
        self.fusion_strategy = fusion_strategy
    
    def learn(self, events: List[Event]) -> List[Pattern]:
        """Learn patterns using all learners."""
        self.training_events = events
        all_patterns = []
        
        for learner in self.learners:
            try:
                patterns = learner.learn(events)
                all_patterns.extend(patterns)
            except Exception as e:
                logger.warning(f"Pattern learning failed for {type(learner).__name__}: {e}")
        
        # Deduplicate and merge
        if self.fusion_strategy == "union":
            self.learned_patterns = all_patterns
        else:
            # Keep highest confidence for duplicates
            pattern_map: Dict[str, Pattern] = {}
            for p in all_patterns:
                key = f"{p.pattern_type.value}:{p.name}"
                if key not in pattern_map or p.confidence.value > pattern_map[key].confidence.value:
                    pattern_map[key] = p
            self.learned_patterns = list(pattern_map.values())
        
        self.is_trained = True
        logger.info(f"Composite learner found {len(self.learned_patterns)} patterns")
        return self.learned_patterns
    
    def match(self, events: List[Event]) -> List[PatternMatch]:
        """Match using all learners."""
        all_matches = []
        
        for learner in self.learners:
            if learner.is_trained:
                try:
                    matches = learner.match(events)
                    all_matches.extend(matches)
                except Exception as e:
                    logger.warning(f"Pattern matching failed for {type(learner).__name__}: {e}")
        
        return sorted(all_matches, key=lambda m: m.match_score, reverse=True)
    
    def update(self, event: Event) -> Optional[Pattern]:
        """Update all learners."""
        for learner in self.learners:
            try:
                learner.update(event)
            except Exception as e:
                logger.warning(f"Update failed for {type(learner).__name__}: {e}")
        
        return None


@dataclass
class PatternLearningConfig:
    """Configuration for pattern learning system."""
    enabled: bool = True
    min_events_for_learning: int = 100
    temporal_bin_hours: int = 1
    sequence_min_support: float = 0.1
    sequence_min_confidence: float = 0.5
    sequence_max_length: int = 5
    volumetric_window_minutes: int = 60
    auto_relearn_threshold: int = 1000  # Relearn after this many new events
    pattern_expiry_days: int = 30


class PatternLearningEngine:
    """Main engine for pattern learning and recognition."""
    
    def __init__(self, config: Optional[PatternLearningConfig] = None):
        self.config = config or PatternLearningConfig()
        self.composite_learner: Optional[CompositePatternLearner] = None
        self.events_since_learning: int = 0
        self.all_events: List[Event] = []
        self._initialize_learners()
    
    def _initialize_learners(self) -> None:
        """Initialize pattern learners."""
        learners = [
            TemporalPatternLearner(
                bin_hours=self.config.temporal_bin_hours
            ),
            SequencePatternLearner(
                min_support=self.config.sequence_min_support,
                min_confidence=self.config.sequence_min_confidence,
                max_length=self.config.sequence_max_length
            ),
            VolumetricPatternLearner(
                window_minutes=self.config.volumetric_window_minutes
            )
        ]
        self.composite_learner = CompositePatternLearner(learners=learners)
    
    def learn(self, events: List[Event]) -> Dict[str, Any]:
        """Learn patterns from historical events."""
        if not self.config.enabled:
            return {"success": False, "reason": "Pattern learning disabled"}
        
        if len(events) < self.config.min_events_for_learning:
            return {
                "success": False, 
                "reason": f"Insufficient events: {len(events)} < {self.config.min_events_for_learning}"
            }
        
        self.all_events = events
        patterns = self.composite_learner.learn(events)
        self.events_since_learning = 0
        
        return {
            "success": True,
            "patterns_learned": len(patterns),
            "by_type": self._count_by_type(patterns),
            "events_processed": len(events)
        }
    
    def _count_by_type(self, patterns: List[Pattern]) -> Dict[str, int]:
        """Count patterns by type."""
        counts: Dict[str, int] = {}
        for p in patterns:
            counts[p.pattern_type.value] = counts.get(p.pattern_type.value, 0) + 1
        return counts
    
    def process_event(self, event: Event) -> List[PatternMatch]:
        """Process new event and return pattern matches."""
        if not self.config.enabled or not self.composite_learner.is_trained:
            return []
        
        # Add to history
        self.all_events.append(event)
        self.events_since_learning += 1
        
        # Update learners
        self.composite_learner.update(event)
        
        # Check for relearning
        if self.events_since_learning >= self.config.auto_relearn_threshold:
            logger.info("Triggering automatic relearning")
            self.learn(self.all_events)
        
        # Match against patterns
        return self.composite_learner.match([event])
    
    def get_patterns(
        self,
        pattern_type: Optional[PatternType] = None,
        min_confidence: Optional[PatternConfidence] = None
    ) -> List[Pattern]:
        """Get learned patterns with optional filtering."""
        if not self.composite_learner or not self.composite_learner.is_trained:
            return []
        
        patterns = self.composite_learner.learned_patterns
        
        if pattern_type:
            patterns = [p for p in patterns if p.pattern_type == pattern_type]
        
        if min_confidence:
            confidence_order = [
                PatternConfidence.TENTATIVE,
                PatternConfidence.LOW,
                PatternConfidence.MEDIUM,
                PatternConfidence.HIGH,
                PatternConfidence.ESTABLISHED
            ]
            min_idx = confidence_order.index(min_confidence)
            patterns = [p for p in patterns if confidence_order.index(p.confidence) >= min_idx]
        
        return patterns
    
    def detect_anomalous_patterns(self, events: List[Event]) -> List[Pattern]:
        """Find patterns that deviate from normal."""
        if not self.composite_learner or not self.composite_learner.is_trained:
            return []
        
        matches = self.composite_learner.match(events)
        
        # Find patterns with low match scores (deviations)
        anomalous = []
        for match in matches:
            if match.match_score < 0.3:
                deviation_pattern = Pattern(
                    pattern_id=f"deviation_{match.pattern.pattern_id}",
                    pattern_type=match.pattern.pattern_type,
                    name=f"Deviation from {match.pattern.name}",
                    description=f"Events deviate from normal pattern (score: {match.match_score:.2f})",
                    confidence=match.pattern.confidence,
                    support=1 - match.match_score,
                    occurrences=len(match.matched_events),
                    first_seen=datetime.now(),
                    last_seen=datetime.now(),
                    features={
                        "original_pattern": match.pattern.name,
                        "deviation_score": 1 - match.match_score
                    },
                    is_normal=False
                )
                anomalous.append(deviation_pattern)
        
        return anomalous
    
    def export_patterns(self) -> Dict[str, Any]:
        """Export learned patterns."""
        patterns = self.get_patterns()
        return {
            "patterns": [p.to_dict() for p in patterns],
            "total": len(patterns),
            "by_type": self._count_by_type(patterns),
            "exported_at": datetime.now().isoformat()
        }
    
    def import_patterns(self, data: Dict[str, Any]) -> int:
        """Import patterns from exported data."""
        if "patterns" not in data:
            return 0
        
        imported = []
        for p_data in data["patterns"]:
            try:
                pattern = Pattern.from_dict(p_data)
                imported.append(pattern)
            except Exception as e:
                logger.warning(f"Failed to import pattern: {e}")
        
        if self.composite_learner:
            self.composite_learner.learned_patterns.extend(imported)
            self.composite_learner.is_trained = True
        
        return len(imported)
