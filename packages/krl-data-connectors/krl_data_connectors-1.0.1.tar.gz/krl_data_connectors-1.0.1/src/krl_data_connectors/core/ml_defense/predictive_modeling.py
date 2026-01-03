"""
Predictive Modeling for KRL Defense System.

Week 15: ML-enhanced predictive threat detection.
Predicts potential threats before they materialize.
"""

import hashlib
import logging
import math
import statistics
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, TypeVar
from collections import deque, Counter
import json

logger = logging.getLogger(__name__)

T = TypeVar('T')


class PredictionType(Enum):
    """Types of predictions."""
    THREAT = "threat"  # Threat prediction
    VIOLATION = "violation"  # License violation
    ANOMALY = "anomaly"  # Anomalous behavior
    CHURN = "churn"  # License churn/abandonment
    ESCALATION = "escalation"  # Threat escalation
    ATTACK_PATTERN = "attack_pattern"  # Attack sequence


class PredictionConfidence(Enum):
    """Confidence levels for predictions."""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    
    @classmethod
    def from_score(cls, score: float) -> 'PredictionConfidence':
        if score >= 0.9:
            return cls.VERY_HIGH
        elif score >= 0.7:
            return cls.HIGH
        elif score >= 0.5:
            return cls.MEDIUM
        elif score >= 0.3:
            return cls.LOW
        else:
            return cls.VERY_LOW


class ModelType(Enum):
    """Types of predictive models."""
    MARKOV_CHAIN = "markov_chain"
    TIME_SERIES = "time_series"
    SEQUENCE = "sequence"
    PROBABILISTIC = "probabilistic"
    ENSEMBLE = "ensemble"


@dataclass
class Observation:
    """Observation for model training/prediction."""
    observation_id: str
    timestamp: datetime
    entity_id: str
    state: str
    features: Dict[str, float] = field(default_factory=dict)
    labels: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Prediction:
    """Prediction result."""
    prediction_id: str
    prediction_type: PredictionType
    model_type: ModelType
    target: str  # What is being predicted
    probability: float  # 0-1
    confidence: PredictionConfidence
    time_horizon: timedelta  # When prediction applies
    timestamp: datetime
    entity_id: str
    reasoning: List[str] = field(default_factory=list)
    evidence: Dict[str, Any] = field(default_factory=dict)
    is_verified: Optional[bool] = None  # None = not yet verified
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "prediction_id": self.prediction_id,
            "prediction_type": self.prediction_type.value,
            "model_type": self.model_type.value,
            "target": self.target,
            "probability": self.probability,
            "confidence": self.confidence.value,
            "time_horizon_seconds": self.time_horizon.total_seconds(),
            "timestamp": self.timestamp.isoformat(),
            "entity_id": self.entity_id,
            "reasoning": self.reasoning,
            "is_verified": self.is_verified
        }


@dataclass
class PredictionFeedback:
    """Feedback on prediction accuracy."""
    prediction_id: str
    actual_outcome: bool
    actual_timestamp: Optional[datetime] = None
    notes: str = ""


class PredictiveModel(ABC):
    """Base class for predictive models."""
    
    def __init__(self, model_type: ModelType, name: str):
        self.model_type = model_type
        self.name = name
        self.is_trained = False
        self.training_samples = 0
        self.accuracy_history: List[bool] = []
    
    @abstractmethod
    def train(self, observations: List[Observation]) -> Dict[str, Any]:
        """Train the model."""
        pass
    
    @abstractmethod
    def predict(self, observations: List[Observation], horizon: timedelta) -> List[Prediction]:
        """Make predictions."""
        pass
    
    @abstractmethod
    def update(self, observation: Observation) -> None:
        """Online update with new observation."""
        pass
    
    def record_feedback(self, feedback: PredictionFeedback) -> None:
        """Record prediction feedback for accuracy tracking."""
        self.accuracy_history.append(feedback.actual_outcome)
    
    @property
    def accuracy(self) -> float:
        """Calculate model accuracy."""
        if not self.accuracy_history:
            return 0.0
        return sum(self.accuracy_history) / len(self.accuracy_history)


class MarkovChainModel(PredictiveModel):
    """Markov chain for state transition prediction."""
    
    def __init__(self, order: int = 1):
        super().__init__(ModelType.MARKOV_CHAIN, "MarkovChain")
        self.order = order
        self.transition_counts: Dict[Tuple[str, ...], Dict[str, int]] = {}
        self.state_counts: Dict[str, int] = Counter()
        self.states: Set[str] = set()
    
    def train(self, observations: List[Observation]) -> Dict[str, Any]:
        """Train Markov chain on observation sequences."""
        # Group by entity
        entity_sequences: Dict[str, List[str]] = {}
        for obs in sorted(observations, key=lambda o: o.timestamp):
            if obs.entity_id not in entity_sequences:
                entity_sequences[obs.entity_id] = []
            entity_sequences[obs.entity_id].append(obs.state)
            self.states.add(obs.state)
            self.state_counts[obs.state] += 1
        
        # Count transitions
        for entity_id, sequence in entity_sequences.items():
            for i in range(len(sequence) - self.order):
                current_state = tuple(sequence[i:i + self.order])
                next_state = sequence[i + self.order]
                
                if current_state not in self.transition_counts:
                    self.transition_counts[current_state] = {}
                
                self.transition_counts[current_state][next_state] = \
                    self.transition_counts[current_state].get(next_state, 0) + 1
        
        self.is_trained = True
        self.training_samples = len(observations)
        
        return {
            "states": len(self.states),
            "transitions": len(self.transition_counts),
            "samples": self.training_samples
        }
    
    def get_transition_probabilities(self, current_state: Tuple[str, ...]) -> Dict[str, float]:
        """Get transition probabilities from current state."""
        if current_state not in self.transition_counts:
            # Fall back to marginal distribution
            total = sum(self.state_counts.values())
            if total == 0:
                return {}
            return {s: c / total for s, c in self.state_counts.items()}
        
        counts = self.transition_counts[current_state]
        total = sum(counts.values())
        
        if total == 0:
            return {}
        
        return {s: c / total for s, c in counts.items()}
    
    def predict(self, observations: List[Observation], horizon: timedelta) -> List[Prediction]:
        """Predict next states for entities."""
        if not self.is_trained:
            return []
        
        # Group recent observations by entity
        entity_states: Dict[str, List[str]] = {}
        for obs in sorted(observations, key=lambda o: o.timestamp):
            if obs.entity_id not in entity_states:
                entity_states[obs.entity_id] = []
            entity_states[obs.entity_id].append(obs.state)
        
        predictions = []
        
        for entity_id, states in entity_states.items():
            if len(states) < self.order:
                continue
            
            current = tuple(states[-self.order:])
            probs = self.get_transition_probabilities(current)
            
            for next_state, prob in probs.items():
                if prob > 0.1:  # Only significant predictions
                    prediction = Prediction(
                        prediction_id=self._generate_id(entity_id, next_state),
                        prediction_type=self._infer_type(next_state),
                        model_type=self.model_type,
                        target=next_state,
                        probability=prob,
                        confidence=PredictionConfidence.from_score(prob),
                        time_horizon=horizon,
                        timestamp=datetime.now(),
                        entity_id=entity_id,
                        reasoning=[
                            f"Current state sequence: {' -> '.join(current)}",
                            f"Historical transition probability: {prob:.2%}"
                        ],
                        evidence={
                            "current_state": list(current),
                            "transition_count": self.transition_counts.get(current, {}).get(next_state, 0)
                        }
                    )
                    predictions.append(prediction)
        
        return predictions
    
    def _generate_id(self, entity_id: str, target: str) -> str:
        data = f"{entity_id}:{target}:{datetime.now().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _infer_type(self, state: str) -> PredictionType:
        """Infer prediction type from state."""
        state_lower = state.lower()
        if any(kw in state_lower for kw in ["threat", "attack", "malicious"]):
            return PredictionType.THREAT
        elif any(kw in state_lower for kw in ["violat", "breach", "invalid"]):
            return PredictionType.VIOLATION
        elif any(kw in state_lower for kw in ["anomal", "unusual", "suspicious"]):
            return PredictionType.ANOMALY
        elif any(kw in state_lower for kw in ["churn", "cancel", "abandon"]):
            return PredictionType.CHURN
        elif any(kw in state_lower for kw in ["escalat", "critical", "severe"]):
            return PredictionType.ESCALATION
        else:
            return PredictionType.THREAT
    
    def update(self, observation: Observation) -> None:
        """Update with new observation."""
        self.states.add(observation.state)
        self.state_counts[observation.state] += 1


class TimeSeriesPredictor(PredictiveModel):
    """Time series prediction using exponential smoothing."""
    
    def __init__(self, alpha: float = 0.3, beta: float = 0.1):
        super().__init__(ModelType.TIME_SERIES, "ExponentialSmoothing")
        self.alpha = alpha  # Level smoothing
        self.beta = beta  # Trend smoothing
        self.series_data: Dict[str, List[Tuple[datetime, float]]] = {}
        self.levels: Dict[str, float] = {}
        self.trends: Dict[str, float] = {}
    
    def train(self, observations: List[Observation]) -> Dict[str, Any]:
        """Train on observation values."""
        # Group by entity and extract numeric values
        for obs in sorted(observations, key=lambda o: o.timestamp):
            entity_id = obs.entity_id
            
            # Extract target value (use risk score or default)
            value = obs.features.get("risk_score", obs.features.get("value", 0.0))
            
            if entity_id not in self.series_data:
                self.series_data[entity_id] = []
            
            self.series_data[entity_id].append((obs.timestamp, value))
        
        # Initialize levels and trends
        for entity_id, series in self.series_data.items():
            if len(series) >= 2:
                # Initial level is first value
                self.levels[entity_id] = series[0][1]
                # Initial trend from first two values
                self.trends[entity_id] = series[1][1] - series[0][1]
                
                # Apply exponential smoothing
                for i in range(2, len(series)):
                    value = series[i][1]
                    prev_level = self.levels[entity_id]
                    prev_trend = self.trends[entity_id]
                    
                    self.levels[entity_id] = self.alpha * value + (1 - self.alpha) * (prev_level + prev_trend)
                    self.trends[entity_id] = self.beta * (self.levels[entity_id] - prev_level) + (1 - self.beta) * prev_trend
        
        self.is_trained = True
        self.training_samples = len(observations)
        
        return {
            "series_count": len(self.series_data),
            "samples": self.training_samples
        }
    
    def predict(self, observations: List[Observation], horizon: timedelta) -> List[Prediction]:
        """Predict future values."""
        if not self.is_trained:
            return []
        
        predictions = []
        horizon_steps = max(1, int(horizon.total_seconds() / 3600))  # Convert to hours
        
        for entity_id in self.levels:
            if entity_id not in self.levels:
                continue
            
            level = self.levels[entity_id]
            trend = self.trends.get(entity_id, 0)
            
            # Forecast
            forecast = level + trend * horizon_steps
            
            # Determine if this predicts a threat
            if forecast > 0.7:  # High risk threshold
                # Calculate confidence based on trend stability
                series = self.series_data.get(entity_id, [])
                if len(series) >= 5:
                    recent_values = [v for _, v in series[-5:]]
                    variance = statistics.variance(recent_values) if len(recent_values) > 1 else 0.5
                    confidence_score = max(0.3, 1 - min(1, variance))
                else:
                    confidence_score = 0.5
                
                prediction = Prediction(
                    prediction_id=self._generate_id(entity_id),
                    prediction_type=PredictionType.THREAT if forecast > 0.9 else PredictionType.ANOMALY,
                    model_type=self.model_type,
                    target=f"risk_level_{forecast:.2f}",
                    probability=min(1.0, forecast),
                    confidence=PredictionConfidence.from_score(confidence_score),
                    time_horizon=horizon,
                    timestamp=datetime.now(),
                    entity_id=entity_id,
                    reasoning=[
                        f"Current level: {level:.3f}",
                        f"Trend: {'+' if trend > 0 else ''}{trend:.3f}/step",
                        f"Forecasted value: {forecast:.3f} in {horizon_steps} steps"
                    ],
                    evidence={
                        "level": level,
                        "trend": trend,
                        "forecast": forecast,
                        "horizon_steps": horizon_steps
                    }
                )
                predictions.append(prediction)
        
        return predictions
    
    def _generate_id(self, entity_id: str) -> str:
        data = f"ts:{entity_id}:{datetime.now().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def update(self, observation: Observation) -> None:
        """Update with new observation."""
        entity_id = observation.entity_id
        value = observation.features.get("risk_score", observation.features.get("value", 0.0))
        
        if entity_id not in self.series_data:
            self.series_data[entity_id] = []
            self.levels[entity_id] = value
            self.trends[entity_id] = 0
        else:
            prev_level = self.levels[entity_id]
            prev_trend = self.trends[entity_id]
            
            self.levels[entity_id] = self.alpha * value + (1 - self.alpha) * (prev_level + prev_trend)
            self.trends[entity_id] = self.beta * (self.levels[entity_id] - prev_level) + (1 - self.beta) * prev_trend
        
        self.series_data[entity_id].append((observation.timestamp, value))


class SequencePredictor(PredictiveModel):
    """Sequence pattern prediction for attack patterns."""
    
    def __init__(self, min_support: float = 0.1, max_sequence_length: int = 5):
        super().__init__(ModelType.SEQUENCE, "SequencePattern")
        self.min_support = min_support
        self.max_length = max_sequence_length
        self.attack_patterns: List[Tuple[List[str], str, float]] = []  # (pattern, outcome, probability)
        self.sequences: Dict[str, List[str]] = {}
    
    def train(self, observations: List[Observation]) -> Dict[str, Any]:
        """Learn attack sequence patterns."""
        # Group observations into sequences by entity
        for obs in sorted(observations, key=lambda o: o.timestamp):
            if obs.entity_id not in self.sequences:
                self.sequences[obs.entity_id] = []
            self.sequences[obs.entity_id].append(obs.state)
        
        # Find patterns that lead to threat states
        threat_keywords = ["threat", "attack", "breach", "critical", "malicious"]
        
        pattern_counts: Dict[Tuple[str, ...], Dict[str, int]] = {}
        
        for entity_id, sequence in self.sequences.items():
            for i in range(len(sequence)):
                # Check if current state is a threat
                if any(kw in sequence[i].lower() for kw in threat_keywords):
                    # Look at preceding states as patterns
                    for length in range(1, min(self.max_length + 1, i + 1)):
                        pattern = tuple(sequence[i - length:i])
                        outcome = sequence[i]
                        
                        if pattern not in pattern_counts:
                            pattern_counts[pattern] = {}
                        
                        pattern_counts[pattern][outcome] = \
                            pattern_counts[pattern].get(outcome, 0) + 1
        
        # Calculate probabilities
        total_sequences = len(self.sequences)
        
        for pattern, outcomes in pattern_counts.items():
            total_pattern = sum(outcomes.values())
            support = total_pattern / max(1, total_sequences)
            
            if support >= self.min_support:
                for outcome, count in outcomes.items():
                    probability = count / total_pattern
                    self.attack_patterns.append((list(pattern), outcome, probability))
        
        # Sort by probability
        self.attack_patterns.sort(key=lambda x: x[2], reverse=True)
        
        self.is_trained = True
        self.training_samples = len(observations)
        
        return {
            "patterns_learned": len(self.attack_patterns),
            "sequences_analyzed": len(self.sequences),
            "samples": self.training_samples
        }
    
    def predict(self, observations: List[Observation], horizon: timedelta) -> List[Prediction]:
        """Predict based on current sequence matching."""
        if not self.is_trained or not self.attack_patterns:
            return []
        
        # Get recent state sequence for each entity
        entity_recent: Dict[str, List[str]] = {}
        for obs in sorted(observations, key=lambda o: o.timestamp):
            if obs.entity_id not in entity_recent:
                entity_recent[obs.entity_id] = []
            entity_recent[obs.entity_id].append(obs.state)
        
        predictions = []
        
        for entity_id, recent in entity_recent.items():
            # Check each pattern
            for pattern, outcome, probability in self.attack_patterns[:20]:  # Top 20 patterns
                pattern_len = len(pattern)
                
                if len(recent) >= pattern_len:
                    # Check if recent sequence ends with pattern
                    if recent[-pattern_len:] == pattern:
                        prediction = Prediction(
                            prediction_id=self._generate_id(entity_id, outcome),
                            prediction_type=PredictionType.ATTACK_PATTERN,
                            model_type=self.model_type,
                            target=outcome,
                            probability=probability,
                            confidence=PredictionConfidence.from_score(probability),
                            time_horizon=horizon,
                            timestamp=datetime.now(),
                            entity_id=entity_id,
                            reasoning=[
                                f"Detected attack pattern: {' → '.join(pattern)}",
                                f"This pattern historically leads to: {outcome}",
                                f"Pattern confidence: {probability:.2%}"
                            ],
                            evidence={
                                "pattern": pattern,
                                "pattern_length": pattern_len,
                                "recent_states": recent[-pattern_len:]
                            }
                        )
                        predictions.append(prediction)
        
        return predictions
    
    def _generate_id(self, entity_id: str, target: str) -> str:
        data = f"seq:{entity_id}:{target}:{datetime.now().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def update(self, observation: Observation) -> None:
        """Update sequences with new observation."""
        if observation.entity_id not in self.sequences:
            self.sequences[observation.entity_id] = []
        self.sequences[observation.entity_id].append(observation.state)


class BayesianPredictor(PredictiveModel):
    """Bayesian probability-based predictor."""
    
    def __init__(self):
        super().__init__(ModelType.PROBABILISTIC, "NaiveBayes")
        self.priors: Dict[str, float] = {}  # P(class)
        self.likelihoods: Dict[str, Dict[str, Dict[Any, float]]] = {}  # P(feature|class)
        self.classes: Set[str] = set()
        self.features: Set[str] = set()
    
    def train(self, observations: List[Observation]) -> Dict[str, Any]:
        """Train Naive Bayes classifier."""
        # Use state as class label
        class_counts: Counter = Counter()
        feature_value_counts: Dict[str, Dict[str, Counter]] = {}
        
        for obs in observations:
            class_label = obs.state
            self.classes.add(class_label)
            class_counts[class_label] += 1
            
            for feature, value in obs.features.items():
                self.features.add(feature)
                
                if feature not in feature_value_counts:
                    feature_value_counts[feature] = {}
                if class_label not in feature_value_counts[feature]:
                    feature_value_counts[feature][class_label] = Counter()
                
                # Discretize continuous values
                if isinstance(value, float):
                    value = round(value, 1)
                
                feature_value_counts[feature][class_label][value] += 1
        
        # Calculate priors
        total = sum(class_counts.values())
        self.priors = {c: count / total for c, count in class_counts.items()}
        
        # Calculate likelihoods with Laplace smoothing
        self.likelihoods = {}
        for feature, class_counters in feature_value_counts.items():
            self.likelihoods[feature] = {}
            
            # Get all unique values for this feature
            all_values = set()
            for counter in class_counters.values():
                all_values.update(counter.keys())
            
            for class_label in self.classes:
                self.likelihoods[feature][class_label] = {}
                counter = class_counters.get(class_label, Counter())
                total_class = class_counts[class_label]
                
                for value in all_values:
                    count = counter.get(value, 0)
                    # Laplace smoothing
                    prob = (count + 1) / (total_class + len(all_values))
                    self.likelihoods[feature][class_label][value] = prob
        
        self.is_trained = True
        self.training_samples = len(observations)
        
        return {
            "classes": len(self.classes),
            "features": len(self.features),
            "samples": self.training_samples
        }
    
    def predict(self, observations: List[Observation], horizon: timedelta) -> List[Prediction]:
        """Predict class probabilities for observations."""
        if not self.is_trained:
            return []
        
        predictions = []
        
        for obs in observations:
            # Calculate P(class|features) for each class
            class_probs: Dict[str, float] = {}
            
            for class_label in self.classes:
                # Start with prior (in log space for numerical stability)
                log_prob = math.log(self.priors.get(class_label, 1e-10))
                
                # Multiply by likelihoods
                for feature, value in obs.features.items():
                    if feature in self.likelihoods:
                        # Discretize
                        if isinstance(value, float):
                            value = round(value, 1)
                        
                        likelihood = self.likelihoods[feature].get(class_label, {}).get(value, 1e-10)
                        log_prob += math.log(likelihood)
                
                class_probs[class_label] = log_prob
            
            # Convert to probabilities (softmax)
            max_log = max(class_probs.values())
            exp_probs = {c: math.exp(lp - max_log) for c, lp in class_probs.items()}
            total = sum(exp_probs.values())
            probs = {c: p / total for c, p in exp_probs.items()}
            
            # Create predictions for high-risk classes
            threat_classes = [c for c in probs if any(
                kw in c.lower() for kw in ["threat", "attack", "critical", "breach"]
            )]
            
            for class_label in threat_classes:
                prob = probs[class_label]
                if prob > 0.2:  # Only significant probabilities
                    prediction = Prediction(
                        prediction_id=self._generate_id(obs.entity_id, class_label),
                        prediction_type=PredictionType.THREAT,
                        model_type=self.model_type,
                        target=class_label,
                        probability=prob,
                        confidence=PredictionConfidence.from_score(prob),
                        time_horizon=horizon,
                        timestamp=datetime.now(),
                        entity_id=obs.entity_id,
                        reasoning=[
                            f"Bayesian classification predicts: {class_label}",
                            f"Posterior probability: {prob:.2%}",
                            f"Based on {len(obs.features)} features"
                        ],
                        evidence={
                            "features": dict(obs.features),
                            "all_class_probs": {c: f"{p:.3f}" for c, p in probs.items()}
                        }
                    )
                    predictions.append(prediction)
        
        return predictions
    
    def _generate_id(self, entity_id: str, target: str) -> str:
        data = f"bayes:{entity_id}:{target}:{datetime.now().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def update(self, observation: Observation) -> None:
        """Update with new observation."""
        # Simplified: just track for periodic retraining
        pass


class EnsemblePredictor(PredictiveModel):
    """Ensemble of multiple predictive models."""
    
    def __init__(self, models: Optional[List[PredictiveModel]] = None):
        super().__init__(ModelType.ENSEMBLE, "EnsemblePredictor")
        self.models = models or [
            MarkovChainModel(),
            TimeSeriesPredictor(),
            SequencePredictor(),
            BayesianPredictor()
        ]
        self.model_weights: Dict[str, float] = {}
    
    def train(self, observations: List[Observation]) -> Dict[str, Any]:
        """Train all ensemble models."""
        results = {}
        
        for model in self.models:
            try:
                result = model.train(observations)
                results[model.name] = result
                self.model_weights[model.name] = 1.0  # Start with equal weights
            except Exception as e:
                logger.warning(f"Training failed for {model.name}: {e}")
                results[model.name] = {"error": str(e)}
                self.model_weights[model.name] = 0.0
        
        self.is_trained = any(m.is_trained for m in self.models)
        self.training_samples = len(observations)
        
        return {
            "models": results,
            "ensemble_trained": self.is_trained
        }
    
    def predict(self, observations: List[Observation], horizon: timedelta) -> List[Prediction]:
        """Get ensemble predictions."""
        if not self.is_trained:
            return []
        
        all_predictions: Dict[str, List[Prediction]] = {}  # target -> predictions
        
        for model in self.models:
            if not model.is_trained:
                continue
            
            weight = self.model_weights.get(model.name, 1.0)
            if weight <= 0:
                continue
            
            try:
                preds = model.predict(observations, horizon)
                for pred in preds:
                    key = f"{pred.entity_id}:{pred.target}"
                    if key not in all_predictions:
                        all_predictions[key] = []
                    all_predictions[key].append(pred)
            except Exception as e:
                logger.warning(f"Prediction failed for {model.name}: {e}")
        
        # Aggregate predictions
        ensemble_predictions = []
        
        for key, preds in all_predictions.items():
            if not preds:
                continue
            
            # Weighted average probability
            total_weight = sum(self.model_weights.get(p.model_type.value, 1.0) for p in preds)
            if total_weight == 0:
                continue
            
            weighted_prob = sum(
                p.probability * self.model_weights.get(p.model_type.value, 1.0)
                for p in preds
            ) / total_weight
            
            # Combine reasoning
            combined_reasoning = []
            for p in preds:
                combined_reasoning.append(f"[{p.model_type.value}] {p.reasoning[0] if p.reasoning else 'No reason'}")
            
            # Use first prediction as base
            base = preds[0]
            
            ensemble_pred = Prediction(
                prediction_id=self._generate_id(base.entity_id, base.target),
                prediction_type=base.prediction_type,
                model_type=ModelType.ENSEMBLE,
                target=base.target,
                probability=weighted_prob,
                confidence=PredictionConfidence.from_score(weighted_prob),
                time_horizon=horizon,
                timestamp=datetime.now(),
                entity_id=base.entity_id,
                reasoning=combined_reasoning,
                evidence={
                    "model_count": len(preds),
                    "model_types": [p.model_type.value for p in preds],
                    "individual_probs": [p.probability for p in preds]
                }
            )
            ensemble_predictions.append(ensemble_pred)
        
        return ensemble_predictions
    
    def _generate_id(self, entity_id: str, target: str) -> str:
        data = f"ensemble:{entity_id}:{target}:{datetime.now().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def update(self, observation: Observation) -> None:
        """Update all models."""
        for model in self.models:
            try:
                model.update(observation)
            except Exception as e:
                logger.warning(f"Update failed for {model.name}: {e}")
    
    def update_weights(self) -> None:
        """Update model weights based on accuracy."""
        total_accuracy = sum(m.accuracy for m in self.models if m.accuracy > 0)
        
        if total_accuracy > 0:
            for model in self.models:
                self.model_weights[model.name] = model.accuracy / total_accuracy


@dataclass
class PredictiveConfig:
    """Configuration for predictive modeling."""
    enabled: bool = True
    default_horizon_hours: int = 24
    markov_order: int = 2
    time_series_alpha: float = 0.3
    sequence_min_support: float = 0.1
    min_probability_threshold: float = 0.3
    enable_ensemble: bool = True
    feedback_window_days: int = 7


class PredictiveModelingEngine:
    """Main engine for predictive threat modeling."""
    
    def __init__(self, config: Optional[PredictiveConfig] = None):
        self.config = config or PredictiveConfig()
        self.ensemble: Optional[EnsemblePredictor] = None
        self.observations: List[Observation] = []
        self.predictions: Dict[str, Prediction] = {}
        self.feedback_log: List[PredictionFeedback] = []
        self._initialize_models()
    
    def _initialize_models(self) -> None:
        """Initialize predictive models."""
        models = [
            MarkovChainModel(order=self.config.markov_order),
            TimeSeriesPredictor(alpha=self.config.time_series_alpha),
            SequencePredictor(min_support=self.config.sequence_min_support),
            BayesianPredictor()
        ]
        self.ensemble = EnsemblePredictor(models=models)
    
    def train(self, observations: List[Observation]) -> Dict[str, Any]:
        """Train all predictive models."""
        if not self.config.enabled:
            return {"success": False, "reason": "Predictive modeling disabled"}
        
        self.observations = observations
        result = self.ensemble.train(observations)
        
        return {
            "success": self.ensemble.is_trained,
            "details": result,
            "observations_used": len(observations)
        }
    
    def predict(
        self,
        observations: Optional[List[Observation]] = None,
        horizon: Optional[timedelta] = None
    ) -> List[Prediction]:
        """Generate predictions."""
        if not self.config.enabled or not self.ensemble.is_trained:
            return []
        
        observations = observations or self.observations
        horizon = horizon or timedelta(hours=self.config.default_horizon_hours)
        
        predictions = self.ensemble.predict(observations, horizon)
        
        # Filter by threshold
        predictions = [p for p in predictions if p.probability >= self.config.min_probability_threshold]
        
        # Store predictions
        for pred in predictions:
            self.predictions[pred.prediction_id] = pred
        
        return predictions
    
    def record_feedback(self, feedback: PredictionFeedback) -> bool:
        """Record feedback on a prediction."""
        if feedback.prediction_id not in self.predictions:
            logger.warning(f"Unknown prediction ID: {feedback.prediction_id}")
            return False
        
        prediction = self.predictions[feedback.prediction_id]
        prediction.is_verified = feedback.actual_outcome
        
        self.feedback_log.append(feedback)
        self.ensemble.record_feedback(feedback)
        
        # Update model weights based on feedback
        if len(self.feedback_log) % 10 == 0:
            self.ensemble.update_weights()
        
        return True
    
    def process_observation(self, observation: Observation) -> List[Prediction]:
        """Process new observation and return predictions."""
        self.observations.append(observation)
        self.ensemble.update(observation)
        
        # Generate predictions based on recent observations
        recent = [o for o in self.observations if 
                  datetime.now() - o.timestamp <= timedelta(hours=24)]
        
        return self.predict(recent)
    
    def get_accuracy_stats(self) -> Dict[str, Any]:
        """Get prediction accuracy statistics."""
        if not self.feedback_log:
            return {"total_predictions": len(self.predictions), "verified": 0}
        
        verified = [f for f in self.feedback_log]
        correct = sum(1 for f in verified if f.actual_outcome)
        
        return {
            "total_predictions": len(self.predictions),
            "verified": len(verified),
            "correct": correct,
            "accuracy": correct / len(verified) if verified else 0,
            "model_accuracies": {
                m.name: m.accuracy for m in self.ensemble.models
            }
        }
    
    def export_model(self) -> Dict[str, Any]:
        """Export model state."""
        return {
            "config": {
                "enabled": self.config.enabled,
                "horizon_hours": self.config.default_horizon_hours
            },
            "is_trained": self.ensemble.is_trained if self.ensemble else False,
            "observations_count": len(self.observations),
            "predictions_count": len(self.predictions),
            "accuracy_stats": self.get_accuracy_stats()
        }
