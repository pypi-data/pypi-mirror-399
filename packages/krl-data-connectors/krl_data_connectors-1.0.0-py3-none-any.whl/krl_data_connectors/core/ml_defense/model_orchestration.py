"""
Model Orchestration for KRL Defense System.

Week 15: Orchestrates multiple ML models for defense decisions.
Provides unified interface for model management and decision aggregation.
"""

import hashlib
import logging
import statistics
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from collections import deque
import json

logger = logging.getLogger(__name__)


class DecisionType(Enum):
    """Types of defense decisions."""
    ALLOW = "allow"
    WARN = "warn"
    THROTTLE = "throttle"
    BLOCK = "block"
    QUARANTINE = "quarantine"
    INVESTIGATE = "investigate"


class DecisionPriority(Enum):
    """Priority levels for decisions."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


class ModelStatus(Enum):
    """Status of ML models."""
    UNINITIALIZED = "uninitialized"
    TRAINING = "training"
    READY = "ready"
    DEGRADED = "degraded"
    FAILED = "failed"
    UPDATING = "updating"


@dataclass
class ModelInfo:
    """Information about a registered model."""
    model_id: str
    name: str
    model_type: str
    version: str
    status: ModelStatus
    accuracy: float
    last_trained: Optional[datetime]
    last_used: Optional[datetime]
    training_samples: int
    config: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class Decision:
    """Defense decision from models."""
    decision_id: str
    decision_type: DecisionType
    priority: DecisionPriority
    confidence: float  # 0-1
    timestamp: datetime
    entity_id: str
    reasoning: List[str]
    contributing_models: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    expires_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "decision_type": self.decision_type.value,
            "priority": self.priority.value,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "entity_id": self.entity_id,
            "reasoning": self.reasoning,
            "contributing_models": self.contributing_models,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None
        }


@dataclass
class ModelVote:
    """Vote from a model for decision making."""
    model_id: str
    decision_type: DecisionType
    confidence: float
    weight: float
    reasoning: str


class DecisionStrategy(ABC):
    """Strategy for aggregating model decisions."""
    
    @abstractmethod
    def aggregate(self, votes: List[ModelVote]) -> Tuple[DecisionType, float, List[str]]:
        """Aggregate votes into a decision."""
        pass


class MajorityVoteStrategy(DecisionStrategy):
    """Simple majority voting."""
    
    def aggregate(self, votes: List[ModelVote]) -> Tuple[DecisionType, float, List[str]]:
        if not votes:
            return DecisionType.ALLOW, 0.0, ["No votes received"]
        
        # Count weighted votes
        vote_counts: Dict[DecisionType, float] = {}
        for vote in votes:
            weighted = vote.confidence * vote.weight
            vote_counts[vote.decision_type] = vote_counts.get(vote.decision_type, 0) + weighted
        
        # Find winner
        winner = max(vote_counts.items(), key=lambda x: x[1])
        total_weight = sum(vote_counts.values())
        
        confidence = winner[1] / total_weight if total_weight > 0 else 0.0
        reasoning = [
            f"Majority vote: {winner[0].value} with {winner[1]:.2f} weighted votes",
            f"Total votes: {len(votes)}"
        ]
        
        return winner[0], confidence, reasoning


class ConservativeStrategy(DecisionStrategy):
    """Conservative strategy - defaults to most restrictive."""
    
    SEVERITY_ORDER = [
        DecisionType.QUARANTINE,
        DecisionType.BLOCK,
        DecisionType.INVESTIGATE,
        DecisionType.THROTTLE,
        DecisionType.WARN,
        DecisionType.ALLOW
    ]
    
    def aggregate(self, votes: List[ModelVote]) -> Tuple[DecisionType, float, List[str]]:
        if not votes:
            return DecisionType.ALLOW, 0.0, ["No votes received"]
        
        # Take most restrictive decision that has significant support
        decision_support: Dict[DecisionType, List[ModelVote]] = {}
        
        for vote in votes:
            if vote.decision_type not in decision_support:
                decision_support[vote.decision_type] = []
            decision_support[vote.decision_type].append(vote)
        
        # Check in severity order
        for decision_type in self.SEVERITY_ORDER:
            if decision_type in decision_support:
                support_votes = decision_support[decision_type]
                avg_confidence = statistics.mean(v.confidence for v in support_votes)
                
                # Need sufficient confidence for restrictive actions
                if decision_type in [DecisionType.QUARANTINE, DecisionType.BLOCK]:
                    threshold = 0.7
                elif decision_type in [DecisionType.INVESTIGATE, DecisionType.THROTTLE]:
                    threshold = 0.5
                else:
                    threshold = 0.3
                
                if avg_confidence >= threshold:
                    reasoning = [
                        f"Conservative: {decision_type.value} (severity rank)",
                        f"Support: {len(support_votes)} models, avg confidence {avg_confidence:.2f}"
                    ]
                    return decision_type, avg_confidence, reasoning
        
        return DecisionType.ALLOW, 0.5, ["No decision met threshold"]


class WeightedConsensusStrategy(DecisionStrategy):
    """Weighted consensus with model reliability."""
    
    def aggregate(self, votes: List[ModelVote]) -> Tuple[DecisionType, float, List[str]]:
        if not votes:
            return DecisionType.ALLOW, 0.0, ["No votes received"]
        
        # Weighted scoring for each decision type
        scores: Dict[DecisionType, float] = {}
        
        for vote in votes:
            score = vote.confidence * vote.weight
            scores[vote.decision_type] = scores.get(vote.decision_type, 0) + score
        
        # Normalize
        total = sum(scores.values())
        if total > 0:
            scores = {k: v / total for k, v in scores.items()}
        
        # Winner
        winner = max(scores.items(), key=lambda x: x[1])
        
        # Calculate consensus strength
        if len(scores) == 1:
            consensus = 1.0
        else:
            sorted_scores = sorted(scores.values(), reverse=True)
            consensus = sorted_scores[0] - sorted_scores[1] if len(sorted_scores) > 1 else 1.0
        
        reasoning = [
            f"Weighted consensus: {winner[0].value}",
            f"Score: {winner[1]:.2%}, consensus strength: {consensus:.2f}"
        ]
        
        return winner[0], winner[1] * consensus, reasoning


class ModelRegistry:
    """Registry for managing ML models."""
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.model_info: Dict[str, ModelInfo] = {}
        self.model_weights: Dict[str, float] = {}
    
    def register(
        self,
        model_id: str,
        model: Any,
        name: str,
        model_type: str,
        version: str = "1.0.0",
        weight: float = 1.0
    ) -> bool:
        """Register a model."""
        if model_id in self.models:
            logger.warning(f"Model {model_id} already registered, updating")
        
        self.models[model_id] = model
        self.model_weights[model_id] = weight
        
        self.model_info[model_id] = ModelInfo(
            model_id=model_id,
            name=name,
            model_type=model_type,
            version=version,
            status=ModelStatus.UNINITIALIZED,
            accuracy=0.0,
            last_trained=None,
            last_used=None,
            training_samples=0
        )
        
        logger.info(f"Registered model: {model_id} ({name})")
        return True
    
    def unregister(self, model_id: str) -> bool:
        """Unregister a model."""
        if model_id not in self.models:
            return False
        
        del self.models[model_id]
        del self.model_info[model_id]
        del self.model_weights[model_id]
        
        logger.info(f"Unregistered model: {model_id}")
        return True
    
    def get_model(self, model_id: str) -> Optional[Any]:
        """Get a registered model."""
        return self.models.get(model_id)
    
    def get_info(self, model_id: str) -> Optional[ModelInfo]:
        """Get model info."""
        return self.model_info.get(model_id)
    
    def update_status(self, model_id: str, status: ModelStatus) -> bool:
        """Update model status."""
        if model_id not in self.model_info:
            return False
        
        self.model_info[model_id].status = status
        return True
    
    def update_metrics(self, model_id: str, metrics: Dict[str, float]) -> bool:
        """Update model metrics."""
        if model_id not in self.model_info:
            return False
        
        self.model_info[model_id].metrics.update(metrics)
        
        if "accuracy" in metrics:
            self.model_info[model_id].accuracy = metrics["accuracy"]
        
        return True
    
    def get_ready_models(self) -> List[str]:
        """Get IDs of ready models."""
        return [
            model_id for model_id, info in self.model_info.items()
            if info.status == ModelStatus.READY
        ]
    
    def set_weight(self, model_id: str, weight: float) -> bool:
        """Set model weight for voting."""
        if model_id not in self.models:
            return False
        
        self.model_weights[model_id] = max(0.0, min(1.0, weight))
        return True
    
    def get_weight(self, model_id: str) -> float:
        """Get model weight."""
        return self.model_weights.get(model_id, 1.0)


class DecisionCache:
    """Cache for recent decisions."""
    
    def __init__(self, max_size: int = 10000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl = timedelta(seconds=ttl_seconds)
        self.cache: Dict[str, Decision] = {}
        self.access_times: Dict[str, datetime] = {}
    
    def put(self, decision: Decision) -> None:
        """Cache a decision."""
        self.cache[decision.decision_id] = decision
        self.access_times[decision.decision_id] = datetime.now()
        
        # Evict old entries
        if len(self.cache) > self.max_size:
            self._evict_oldest()
    
    def get(self, decision_id: str) -> Optional[Decision]:
        """Get cached decision."""
        if decision_id not in self.cache:
            return None
        
        # Check TTL
        if datetime.now() - self.access_times[decision_id] > self.ttl:
            del self.cache[decision_id]
            del self.access_times[decision_id]
            return None
        
        self.access_times[decision_id] = datetime.now()
        return self.cache[decision_id]
    
    def get_for_entity(self, entity_id: str) -> List[Decision]:
        """Get all cached decisions for entity."""
        self._cleanup_expired()
        return [d for d in self.cache.values() if d.entity_id == entity_id]
    
    def _evict_oldest(self) -> None:
        """Evict oldest entries."""
        if not self.access_times:
            return
        
        # Sort by access time and remove oldest 10%
        sorted_ids = sorted(self.access_times.items(), key=lambda x: x[1])
        to_remove = sorted_ids[:len(sorted_ids) // 10]
        
        for decision_id, _ in to_remove:
            del self.cache[decision_id]
            del self.access_times[decision_id]
    
    def _cleanup_expired(self) -> None:
        """Remove expired entries."""
        now = datetime.now()
        expired = [
            did for did, access_time in self.access_times.items()
            if now - access_time > self.ttl
        ]
        
        for decision_id in expired:
            del self.cache[decision_id]
            del self.access_times[decision_id]


@dataclass
class OrchestrationConfig:
    """Configuration for model orchestration."""
    enabled: bool = True
    default_strategy: str = "weighted_consensus"
    cache_ttl_seconds: int = 3600
    cache_max_size: int = 10000
    min_model_confidence: float = 0.3
    decision_timeout_ms: int = 1000
    parallel_execution: bool = True
    fallback_decision: DecisionType = DecisionType.ALLOW


class ModelOrchestrator:
    """Orchestrates multiple ML models for defense decisions."""
    
    def __init__(self, config: Optional[OrchestrationConfig] = None):
        self.config = config or OrchestrationConfig()
        self.registry = ModelRegistry()
        self.cache = DecisionCache(
            max_size=self.config.cache_max_size,
            ttl_seconds=self.config.cache_ttl_seconds
        )
        self.strategies: Dict[str, DecisionStrategy] = {
            "majority": MajorityVoteStrategy(),
            "conservative": ConservativeStrategy(),
            "weighted_consensus": WeightedConsensusStrategy()
        }
        self.decision_history: List[Decision] = []
        self.vote_handlers: Dict[str, Callable[[Any, Dict[str, Any]], ModelVote]] = {}
    
    def register_model(
        self,
        model_id: str,
        model: Any,
        name: str,
        model_type: str,
        vote_handler: Callable[[Any, Dict[str, Any]], ModelVote],
        weight: float = 1.0
    ) -> bool:
        """Register a model with its vote handler."""
        success = self.registry.register(
            model_id=model_id,
            model=model,
            name=name,
            model_type=model_type,
            weight=weight
        )
        
        if success:
            self.vote_handlers[model_id] = vote_handler
        
        return success
    
    def make_decision(
        self,
        entity_id: str,
        context: Dict[str, Any],
        strategy: Optional[str] = None
    ) -> Decision:
        """Make a defense decision using registered models."""
        if not self.config.enabled:
            return self._fallback_decision(entity_id, "Orchestration disabled")
        
        strategy_name = strategy or self.config.default_strategy
        decision_strategy = self.strategies.get(strategy_name, self.strategies["weighted_consensus"])
        
        # Collect votes from models
        votes = self._collect_votes(context)
        
        if not votes:
            return self._fallback_decision(entity_id, "No model votes")
        
        # Aggregate votes
        decision_type, confidence, reasoning = decision_strategy.aggregate(votes)
        
        # Create decision
        decision = Decision(
            decision_id=self._generate_id(entity_id),
            decision_type=decision_type,
            priority=self._calculate_priority(decision_type, confidence),
            confidence=confidence,
            timestamp=datetime.now(),
            entity_id=entity_id,
            reasoning=reasoning,
            contributing_models=[v.model_id for v in votes],
            metadata={
                "strategy": strategy_name,
                "votes": len(votes),
                "context_keys": list(context.keys())
            },
            expires_at=datetime.now() + timedelta(seconds=self.config.cache_ttl_seconds)
        )
        
        # Cache and log
        self.cache.put(decision)
        self.decision_history.append(decision)
        
        logger.info(f"Decision for {entity_id}: {decision_type.value} (confidence: {confidence:.2f})")
        
        return decision
    
    def _collect_votes(self, context: Dict[str, Any]) -> List[ModelVote]:
        """Collect votes from all ready models."""
        votes = []
        
        for model_id in self.registry.get_ready_models():
            model = self.registry.get_model(model_id)
            handler = self.vote_handlers.get(model_id)
            
            if not model or not handler:
                continue
            
            try:
                vote = handler(model, context)
                vote.weight = self.registry.get_weight(model_id)
                
                if vote.confidence >= self.config.min_model_confidence:
                    votes.append(vote)
                    
                    # Update last used
                    info = self.registry.get_info(model_id)
                    if info:
                        info.last_used = datetime.now()
                        
            except Exception as e:
                logger.warning(f"Vote collection failed for {model_id}: {e}")
                self.registry.update_status(model_id, ModelStatus.DEGRADED)
        
        return votes
    
    def _fallback_decision(self, entity_id: str, reason: str) -> Decision:
        """Create fallback decision."""
        return Decision(
            decision_id=self._generate_id(entity_id),
            decision_type=self.config.fallback_decision,
            priority=DecisionPriority.LOW,
            confidence=0.5,
            timestamp=datetime.now(),
            entity_id=entity_id,
            reasoning=[f"Fallback: {reason}"],
            contributing_models=[]
        )
    
    def _generate_id(self, entity_id: str) -> str:
        data = f"decision:{entity_id}:{datetime.now().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _calculate_priority(self, decision_type: DecisionType, confidence: float) -> DecisionPriority:
        """Calculate decision priority."""
        type_priority = {
            DecisionType.QUARANTINE: DecisionPriority.EMERGENCY,
            DecisionType.BLOCK: DecisionPriority.CRITICAL,
            DecisionType.INVESTIGATE: DecisionPriority.HIGH,
            DecisionType.THROTTLE: DecisionPriority.MEDIUM,
            DecisionType.WARN: DecisionPriority.LOW,
            DecisionType.ALLOW: DecisionPriority.LOW
        }
        
        base_priority = type_priority.get(decision_type, DecisionPriority.LOW)
        
        # Increase priority for high confidence
        if confidence > 0.9 and base_priority.value < DecisionPriority.EMERGENCY.value:
            return DecisionPriority(base_priority.value + 1)
        
        return base_priority
    
    def add_strategy(self, name: str, strategy: DecisionStrategy) -> None:
        """Add a custom decision strategy."""
        self.strategies[name] = strategy
    
    def get_model_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all registered models."""
        status = {}
        
        for model_id, info in self.registry.model_info.items():
            status[model_id] = {
                "name": info.name,
                "type": info.model_type,
                "status": info.status.value,
                "accuracy": info.accuracy,
                "weight": self.registry.get_weight(model_id),
                "last_used": info.last_used.isoformat() if info.last_used else None
            }
        
        return status
    
    def get_decision_stats(self) -> Dict[str, Any]:
        """Get decision statistics."""
        if not self.decision_history:
            return {"total": 0}
        
        by_type = {}
        by_priority = {}
        confidences = []
        
        for decision in self.decision_history:
            by_type[decision.decision_type.value] = by_type.get(decision.decision_type.value, 0) + 1
            by_priority[decision.priority.name] = by_priority.get(decision.priority.name, 0) + 1
            confidences.append(decision.confidence)
        
        return {
            "total": len(self.decision_history),
            "by_type": by_type,
            "by_priority": by_priority,
            "avg_confidence": statistics.mean(confidences),
            "cached": len(self.cache.cache)
        }
    
    def adjust_model_weights(self) -> None:
        """Adjust model weights based on performance."""
        for model_id, info in self.registry.model_info.items():
            if info.status == ModelStatus.READY and info.accuracy > 0:
                # Weight based on accuracy
                new_weight = 0.5 + (info.accuracy * 0.5)
                self.registry.set_weight(model_id, new_weight)
            elif info.status == ModelStatus.DEGRADED:
                # Reduce weight for degraded models
                current = self.registry.get_weight(model_id)
                self.registry.set_weight(model_id, current * 0.5)


@dataclass
class OrchestratorSnapshot:
    """Snapshot of orchestrator state for persistence."""
    timestamp: datetime
    model_status: Dict[str, Dict[str, Any]]
    decision_stats: Dict[str, Any]
    weights: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "model_status": self.model_status,
            "decision_stats": self.decision_stats,
            "weights": self.weights
        }


def create_snapshot(orchestrator: ModelOrchestrator) -> OrchestratorSnapshot:
    """Create a snapshot of orchestrator state."""
    return OrchestratorSnapshot(
        timestamp=datetime.now(),
        model_status=orchestrator.get_model_status(),
        decision_stats=orchestrator.get_decision_stats(),
        weights={
            model_id: orchestrator.registry.get_weight(model_id)
            for model_id in orchestrator.registry.models
        }
    )
