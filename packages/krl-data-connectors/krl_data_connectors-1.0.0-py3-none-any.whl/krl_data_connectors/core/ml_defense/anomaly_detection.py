"""
Machine Learning Anomaly Detection for KRL Defense System.

Week 15: ML-enhanced behavioral analysis and anomaly detection.
Provides statistical and ML-based detection of abnormal usage patterns.
"""

import hashlib
import logging
import math
import statistics
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from collections import deque
import json

logger = logging.getLogger(__name__)


class AnomalyType(Enum):
    """Types of anomalies detected."""
    STATISTICAL_OUTLIER = "statistical_outlier"
    TEMPORAL_PATTERN = "temporal_pattern"
    VOLUMETRIC = "volumetric"
    BEHAVIORAL_DRIFT = "behavioral_drift"
    SEQUENCE_ANOMALY = "sequence_anomaly"
    CLUSTERING_OUTLIER = "clustering_outlier"
    CONTEXTUAL = "contextual"
    COLLECTIVE = "collective"


class DetectionMethod(Enum):
    """Anomaly detection methods."""
    Z_SCORE = "z_score"
    IQR = "iqr"
    MAD = "mad"
    ISOLATION_FOREST = "isolation_forest"
    LOCAL_OUTLIER_FACTOR = "local_outlier_factor"
    AUTOENCODER = "autoencoder"
    ONE_CLASS_SVM = "one_class_svm"
    DBSCAN = "dbscan"
    LSTM_SEQUENCE = "lstm_sequence"
    ENSEMBLE = "ensemble"


class Severity(Enum):
    """Anomaly severity levels."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class FeatureVector:
    """Feature vector for ML analysis."""
    feature_id: str
    timestamp: datetime
    features: Dict[str, float]
    labels: Dict[str, str] = field(default_factory=dict)
    source_id: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_array(self, feature_names: List[str]) -> List[float]:
        """Convert to numeric array for ML models."""
        return [self.features.get(name, 0.0) for name in feature_names]
    
    def normalize(self, means: Dict[str, float], stds: Dict[str, float]) -> 'FeatureVector':
        """Normalize features using z-score normalization."""
        normalized = {}
        for name, value in self.features.items():
            if name in stds and stds[name] > 0:
                normalized[name] = (value - means.get(name, 0)) / stds[name]
            else:
                normalized[name] = value
        return FeatureVector(
            feature_id=self.feature_id,
            timestamp=self.timestamp,
            features=normalized,
            labels=self.labels.copy(),
            source_id=self.source_id,
            context=self.context.copy()
        )


@dataclass
class Anomaly:
    """Detected anomaly record."""
    anomaly_id: str
    anomaly_type: AnomalyType
    detection_method: DetectionMethod
    severity: Severity
    score: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    timestamp: datetime
    source_id: str
    feature_vector: Optional[FeatureVector]
    description: str
    contributing_factors: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    is_false_positive: bool = False
    reviewed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "anomaly_id": self.anomaly_id,
            "anomaly_type": self.anomaly_type.value,
            "detection_method": self.detection_method.value,
            "severity": self.severity.value,
            "score": self.score,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "source_id": self.source_id,
            "description": self.description,
            "contributing_factors": self.contributing_factors,
            "context": self.context,
            "is_false_positive": self.is_false_positive,
            "reviewed": self.reviewed
        }


@dataclass
class DetectionResult:
    """Result from an anomaly detector."""
    is_anomaly: bool
    score: float  # Anomaly score 0.0-1.0
    confidence: float
    method: DetectionMethod
    details: Dict[str, Any] = field(default_factory=dict)


class AnomalyDetector(ABC):
    """Base class for anomaly detectors."""
    
    def __init__(self, method: DetectionMethod, threshold: float = 0.5):
        self.method = method
        self.threshold = threshold
        self.is_trained = False
        self.training_samples = 0
        
    @abstractmethod
    def train(self, data: List[FeatureVector]) -> None:
        """Train the detector on normal data."""
        pass
    
    @abstractmethod
    def detect(self, feature_vector: FeatureVector) -> DetectionResult:
        """Detect if feature vector is anomalous."""
        pass
    
    @abstractmethod
    def update(self, feature_vector: FeatureVector, is_anomaly: bool) -> None:
        """Online update with new data point."""
        pass


class ZScoreDetector(AnomalyDetector):
    """Z-score based anomaly detection."""
    
    def __init__(self, threshold: float = 3.0, window_size: int = 1000):
        super().__init__(DetectionMethod.Z_SCORE, threshold)
        self.window_size = window_size
        self.feature_means: Dict[str, float] = {}
        self.feature_stds: Dict[str, float] = {}
        self.feature_windows: Dict[str, deque] = {}
        
    def train(self, data: List[FeatureVector]) -> None:
        """Calculate baseline statistics from training data."""
        if not data:
            return
            
        # Initialize feature windows
        feature_values: Dict[str, List[float]] = {}
        for fv in data:
            for name, value in fv.features.items():
                if name not in feature_values:
                    feature_values[name] = []
                feature_values[name].append(value)
        
        # Calculate statistics
        for name, values in feature_values.items():
            self.feature_means[name] = statistics.mean(values)
            self.feature_stds[name] = statistics.stdev(values) if len(values) > 1 else 1.0
            self.feature_windows[name] = deque(values[-self.window_size:], maxlen=self.window_size)
        
        self.is_trained = True
        self.training_samples = len(data)
        logger.info(f"ZScoreDetector trained on {len(data)} samples, {len(self.feature_means)} features")
    
    def detect(self, feature_vector: FeatureVector) -> DetectionResult:
        """Detect anomaly using z-score method."""
        if not self.is_trained:
            return DetectionResult(False, 0.0, 0.0, self.method)
        
        z_scores = {}
        max_z_score = 0.0
        anomalous_features = []
        
        for name, value in feature_vector.features.items():
            if name in self.feature_stds and self.feature_stds[name] > 0:
                z = abs(value - self.feature_means[name]) / self.feature_stds[name]
                z_scores[name] = z
                if z > max_z_score:
                    max_z_score = z
                if z > self.threshold:
                    anomalous_features.append(name)
        
        # Convert z-score to anomaly score (0-1)
        score = min(1.0, max_z_score / (self.threshold * 2))
        is_anomaly = max_z_score > self.threshold
        
        # Confidence based on training samples
        confidence = min(1.0, self.training_samples / 100)
        
        return DetectionResult(
            is_anomaly=is_anomaly,
            score=score,
            confidence=confidence,
            method=self.method,
            details={
                "max_z_score": max_z_score,
                "z_scores": z_scores,
                "anomalous_features": anomalous_features,
                "threshold": self.threshold
            }
        )
    
    def update(self, feature_vector: FeatureVector, is_anomaly: bool) -> None:
        """Update statistics with new data point."""
        if is_anomaly:
            return  # Don't update baseline with anomalies
        
        for name, value in feature_vector.features.items():
            if name not in self.feature_windows:
                self.feature_windows[name] = deque(maxlen=self.window_size)
                self.feature_means[name] = value
                self.feature_stds[name] = 1.0
            else:
                self.feature_windows[name].append(value)
                values = list(self.feature_windows[name])
                self.feature_means[name] = statistics.mean(values)
                self.feature_stds[name] = statistics.stdev(values) if len(values) > 1 else 1.0
        
        self.training_samples += 1


class IQRDetector(AnomalyDetector):
    """Interquartile Range based anomaly detection."""
    
    def __init__(self, multiplier: float = 1.5, window_size: int = 1000):
        super().__init__(DetectionMethod.IQR, multiplier)
        self.multiplier = multiplier
        self.window_size = window_size
        self.feature_q1: Dict[str, float] = {}
        self.feature_q3: Dict[str, float] = {}
        self.feature_windows: Dict[str, deque] = {}
    
    def _calculate_quartiles(self, values: List[float]) -> Tuple[float, float]:
        """Calculate Q1 and Q3."""
        sorted_values = sorted(values)
        n = len(sorted_values)
        q1_idx = n // 4
        q3_idx = (3 * n) // 4
        return sorted_values[q1_idx], sorted_values[q3_idx]
    
    def train(self, data: List[FeatureVector]) -> None:
        """Calculate quartiles from training data."""
        if not data:
            return
        
        feature_values: Dict[str, List[float]] = {}
        for fv in data:
            for name, value in fv.features.items():
                if name not in feature_values:
                    feature_values[name] = []
                feature_values[name].append(value)
        
        for name, values in feature_values.items():
            if len(values) >= 4:
                self.feature_q1[name], self.feature_q3[name] = self._calculate_quartiles(values)
                self.feature_windows[name] = deque(values[-self.window_size:], maxlen=self.window_size)
        
        self.is_trained = True
        self.training_samples = len(data)
        logger.info(f"IQRDetector trained on {len(data)} samples")
    
    def detect(self, feature_vector: FeatureVector) -> DetectionResult:
        """Detect anomaly using IQR method."""
        if not self.is_trained:
            return DetectionResult(False, 0.0, 0.0, self.method)
        
        max_deviation = 0.0
        anomalous_features = []
        
        for name, value in feature_vector.features.items():
            if name in self.feature_q1 and name in self.feature_q3:
                q1 = self.feature_q1[name]
                q3 = self.feature_q3[name]
                iqr = q3 - q1
                
                if iqr > 0:
                    lower_bound = q1 - self.multiplier * iqr
                    upper_bound = q3 + self.multiplier * iqr
                    
                    if value < lower_bound:
                        deviation = (lower_bound - value) / iqr
                        if deviation > max_deviation:
                            max_deviation = deviation
                        anomalous_features.append(name)
                    elif value > upper_bound:
                        deviation = (value - upper_bound) / iqr
                        if deviation > max_deviation:
                            max_deviation = deviation
                        anomalous_features.append(name)
        
        score = min(1.0, max_deviation / 2)
        is_anomaly = max_deviation > 0
        confidence = min(1.0, self.training_samples / 100)
        
        return DetectionResult(
            is_anomaly=is_anomaly,
            score=score,
            confidence=confidence,
            method=self.method,
            details={
                "max_deviation": max_deviation,
                "anomalous_features": anomalous_features
            }
        )
    
    def update(self, feature_vector: FeatureVector, is_anomaly: bool) -> None:
        """Update quartiles with new data."""
        if is_anomaly:
            return
        
        for name, value in feature_vector.features.items():
            if name not in self.feature_windows:
                self.feature_windows[name] = deque(maxlen=self.window_size)
            
            self.feature_windows[name].append(value)
            values = list(self.feature_windows[name])
            if len(values) >= 4:
                self.feature_q1[name], self.feature_q3[name] = self._calculate_quartiles(values)
        
        self.training_samples += 1


class MADDetector(AnomalyDetector):
    """Median Absolute Deviation based anomaly detection."""
    
    def __init__(self, threshold: float = 3.5, window_size: int = 1000):
        super().__init__(DetectionMethod.MAD, threshold)
        self.window_size = window_size
        self.feature_medians: Dict[str, float] = {}
        self.feature_mads: Dict[str, float] = {}
        self.feature_windows: Dict[str, deque] = {}
        self.k = 1.4826  # Consistency constant for normal distribution
    
    def _calculate_mad(self, values: List[float]) -> Tuple[float, float]:
        """Calculate median and MAD."""
        median = statistics.median(values)
        deviations = [abs(v - median) for v in values]
        mad = statistics.median(deviations)
        return median, mad
    
    def train(self, data: List[FeatureVector]) -> None:
        """Calculate median and MAD from training data."""
        if not data:
            return
        
        feature_values: Dict[str, List[float]] = {}
        for fv in data:
            for name, value in fv.features.items():
                if name not in feature_values:
                    feature_values[name] = []
                feature_values[name].append(value)
        
        for name, values in feature_values.items():
            if len(values) >= 2:
                self.feature_medians[name], self.feature_mads[name] = self._calculate_mad(values)
                self.feature_windows[name] = deque(values[-self.window_size:], maxlen=self.window_size)
        
        self.is_trained = True
        self.training_samples = len(data)
        logger.info(f"MADDetector trained on {len(data)} samples")
    
    def detect(self, feature_vector: FeatureVector) -> DetectionResult:
        """Detect anomaly using MAD method."""
        if not self.is_trained:
            return DetectionResult(False, 0.0, 0.0, self.method)
        
        max_modified_z = 0.0
        anomalous_features = []
        modified_z_scores = {}
        
        for name, value in feature_vector.features.items():
            if name in self.feature_medians and name in self.feature_mads:
                median = self.feature_medians[name]
                mad = self.feature_mads[name]
                
                if mad > 0:
                    modified_z = abs(value - median) / (self.k * mad)
                    modified_z_scores[name] = modified_z
                    
                    if modified_z > max_modified_z:
                        max_modified_z = modified_z
                    if modified_z > self.threshold:
                        anomalous_features.append(name)
        
        score = min(1.0, max_modified_z / (self.threshold * 2))
        is_anomaly = max_modified_z > self.threshold
        confidence = min(1.0, self.training_samples / 100)
        
        return DetectionResult(
            is_anomaly=is_anomaly,
            score=score,
            confidence=confidence,
            method=self.method,
            details={
                "max_modified_z": max_modified_z,
                "modified_z_scores": modified_z_scores,
                "anomalous_features": anomalous_features
            }
        )
    
    def update(self, feature_vector: FeatureVector, is_anomaly: bool) -> None:
        """Update statistics with new data."""
        if is_anomaly:
            return
        
        for name, value in feature_vector.features.items():
            if name not in self.feature_windows:
                self.feature_windows[name] = deque(maxlen=self.window_size)
            
            self.feature_windows[name].append(value)
            values = list(self.feature_windows[name])
            if len(values) >= 2:
                self.feature_medians[name], self.feature_mads[name] = self._calculate_mad(values)
        
        self.training_samples += 1


class IsolationForestDetector(AnomalyDetector):
    """Simple Isolation Forest implementation for anomaly detection."""
    
    def __init__(self, n_trees: int = 100, sample_size: int = 256, threshold: float = 0.6):
        super().__init__(DetectionMethod.ISOLATION_FOREST, threshold)
        self.n_trees = n_trees
        self.sample_size = sample_size
        self.trees: List[Dict[str, Any]] = []
        self.feature_names: List[str] = []
        self.c_factor = 0.0  # Normalization constant
    
    def _c(self, n: int) -> float:
        """Average path length of unsuccessful search in BST."""
        if n <= 1:
            return 0
        return 2.0 * (math.log(n - 1) + 0.5772156649) - (2.0 * (n - 1) / n)
    
    def _build_tree(self, data: List[List[float]], max_depth: int) -> Dict[str, Any]:
        """Build an isolation tree."""
        if len(data) <= 1 or max_depth == 0:
            return {"type": "leaf", "size": len(data)}
        
        # Select random feature and split point
        n_features = len(data[0]) if data else 0
        if n_features == 0:
            return {"type": "leaf", "size": len(data)}
        
        feature_idx = hash(str(time.time_ns())) % n_features
        feature_values = [row[feature_idx] for row in data]
        min_val, max_val = min(feature_values), max(feature_values)
        
        if min_val == max_val:
            return {"type": "leaf", "size": len(data)}
        
        split_value = min_val + (max_val - min_val) * (hash(str(time.time_ns() + 1)) % 100) / 100
        
        left_data = [row for row in data if row[feature_idx] < split_value]
        right_data = [row for row in data if row[feature_idx] >= split_value]
        
        return {
            "type": "node",
            "feature": feature_idx,
            "split": split_value,
            "left": self._build_tree(left_data, max_depth - 1),
            "right": self._build_tree(right_data, max_depth - 1)
        }
    
    def _path_length(self, point: List[float], tree: Dict[str, Any], depth: int = 0) -> float:
        """Calculate path length for a point in a tree."""
        if tree["type"] == "leaf":
            return depth + self._c(tree["size"])
        
        if point[tree["feature"]] < tree["split"]:
            return self._path_length(point, tree["left"], depth + 1)
        else:
            return self._path_length(point, tree["right"], depth + 1)
    
    def train(self, data: List[FeatureVector]) -> None:
        """Train isolation forest on data."""
        if not data:
            return
        
        # Extract feature names and convert to arrays
        self.feature_names = list(data[0].features.keys())
        arrays = [fv.to_array(self.feature_names) for fv in data]
        
        # Calculate normalization constant
        self.c_factor = self._c(min(self.sample_size, len(arrays)))
        
        # Build trees
        max_depth = int(math.ceil(math.log2(max(self.sample_size, 2))))
        self.trees = []
        
        for _ in range(self.n_trees):
            # Sample data
            sample_size = min(self.sample_size, len(arrays))
            indices = [hash(str(time.time_ns() + i)) % len(arrays) for i in range(sample_size)]
            sample = [arrays[i] for i in indices]
            
            tree = self._build_tree(sample, max_depth)
            self.trees.append(tree)
        
        self.is_trained = True
        self.training_samples = len(data)
        logger.info(f"IsolationForestDetector trained with {self.n_trees} trees")
    
    def detect(self, feature_vector: FeatureVector) -> DetectionResult:
        """Detect anomaly using isolation forest."""
        if not self.is_trained or not self.trees:
            return DetectionResult(False, 0.0, 0.0, self.method)
        
        point = feature_vector.to_array(self.feature_names)
        
        # Calculate average path length
        total_path = sum(self._path_length(point, tree) for tree in self.trees)
        avg_path = total_path / len(self.trees)
        
        # Calculate anomaly score
        if self.c_factor > 0:
            score = 2 ** (-avg_path / self.c_factor)
        else:
            score = 0.5
        
        is_anomaly = score > self.threshold
        confidence = min(1.0, len(self.trees) / 50)
        
        return DetectionResult(
            is_anomaly=is_anomaly,
            score=score,
            confidence=confidence,
            method=self.method,
            details={
                "avg_path_length": avg_path,
                "n_trees": len(self.trees)
            }
        )
    
    def update(self, feature_vector: FeatureVector, is_anomaly: bool) -> None:
        """Isolation forest doesn't support online updates."""
        pass


class LocalOutlierFactorDetector(AnomalyDetector):
    """Simplified Local Outlier Factor detector."""
    
    def __init__(self, k_neighbors: int = 20, threshold: float = 1.5):
        super().__init__(DetectionMethod.LOCAL_OUTLIER_FACTOR, threshold)
        self.k = k_neighbors
        self.data_points: List[List[float]] = []
        self.feature_names: List[str] = []
    
    def _distance(self, p1: List[float], p2: List[float]) -> float:
        """Calculate Euclidean distance."""
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(p1, p2)))
    
    def _k_distance(self, point: List[float]) -> Tuple[float, List[int]]:
        """Calculate k-distance and k-nearest neighbors."""
        distances = [(i, self._distance(point, p)) for i, p in enumerate(self.data_points)]
        distances.sort(key=lambda x: x[1])
        
        k_neighbors = distances[:self.k]
        k_dist = k_neighbors[-1][1] if k_neighbors else 0.0
        neighbor_indices = [idx for idx, _ in k_neighbors]
        
        return k_dist, neighbor_indices
    
    def _reachability_distance(self, p1: List[float], p2_idx: int) -> float:
        """Calculate reachability distance."""
        p2 = self.data_points[p2_idx]
        k_dist_p2, _ = self._k_distance(p2)
        return max(k_dist_p2, self._distance(p1, p2))
    
    def _lrd(self, point: List[float]) -> float:
        """Calculate local reachability density."""
        _, neighbors = self._k_distance(point)
        
        if not neighbors:
            return 0.0
        
        reach_distances = [self._reachability_distance(point, n) for n in neighbors]
        sum_reach = sum(reach_distances)
        
        if sum_reach == 0:
            return float('inf')
        
        return len(neighbors) / sum_reach
    
    def train(self, data: List[FeatureVector]) -> None:
        """Store training data for LOF calculation."""
        if not data:
            return
        
        self.feature_names = list(data[0].features.keys())
        self.data_points = [fv.to_array(self.feature_names) for fv in data]
        
        self.is_trained = True
        self.training_samples = len(data)
        logger.info(f"LOFDetector trained on {len(data)} samples")
    
    def detect(self, feature_vector: FeatureVector) -> DetectionResult:
        """Detect anomaly using LOF."""
        if not self.is_trained or len(self.data_points) < self.k:
            return DetectionResult(False, 0.0, 0.0, self.method)
        
        point = feature_vector.to_array(self.feature_names)
        _, neighbors = self._k_distance(point)
        
        lrd_point = self._lrd(point)
        
        if lrd_point == 0 or lrd_point == float('inf'):
            return DetectionResult(False, 0.0, 0.0, self.method)
        
        # Calculate LOF
        lrd_neighbors = [self._lrd(self.data_points[n]) for n in neighbors]
        valid_lrds = [lrd for lrd in lrd_neighbors if lrd > 0 and lrd != float('inf')]
        
        if not valid_lrds:
            return DetectionResult(False, 0.0, 0.0, self.method)
        
        lof = sum(valid_lrds) / (len(valid_lrds) * lrd_point)
        
        # Convert LOF to score
        score = min(1.0, (lof - 1) / (self.threshold - 1)) if lof > 1 else 0.0
        is_anomaly = lof > self.threshold
        confidence = min(1.0, self.training_samples / 100)
        
        return DetectionResult(
            is_anomaly=is_anomaly,
            score=score,
            confidence=confidence,
            method=self.method,
            details={
                "lof": lof,
                "lrd": lrd_point,
                "k_neighbors": self.k
            }
        )
    
    def update(self, feature_vector: FeatureVector, is_anomaly: bool) -> None:
        """Add new point to dataset."""
        if is_anomaly:
            return
        
        point = feature_vector.to_array(self.feature_names)
        self.data_points.append(point)
        
        # Keep dataset bounded
        if len(self.data_points) > 10000:
            self.data_points = self.data_points[-5000:]
        
        self.training_samples += 1


class EnsembleDetector(AnomalyDetector):
    """Ensemble anomaly detector combining multiple methods."""
    
    def __init__(
        self,
        detectors: Optional[List[AnomalyDetector]] = None,
        voting_threshold: float = 0.5,
        weight_by_confidence: bool = True
    ):
        super().__init__(DetectionMethod.ENSEMBLE, voting_threshold)
        self.detectors = detectors or [
            ZScoreDetector(),
            IQRDetector(),
            MADDetector()
        ]
        self.weight_by_confidence = weight_by_confidence
        self.detector_weights: Dict[str, float] = {}
    
    def train(self, data: List[FeatureVector]) -> None:
        """Train all ensemble detectors."""
        for detector in self.detectors:
            try:
                detector.train(data)
                self.detector_weights[detector.method.value] = 1.0
            except Exception as e:
                logger.warning(f"Failed to train {detector.method.value}: {e}")
                self.detector_weights[detector.method.value] = 0.0
        
        self.is_trained = True
        self.training_samples = len(data)
        logger.info(f"EnsembleDetector trained with {len(self.detectors)} detectors")
    
    def detect(self, feature_vector: FeatureVector) -> DetectionResult:
        """Detect using ensemble voting."""
        if not self.is_trained:
            return DetectionResult(False, 0.0, 0.0, self.method)
        
        results: List[DetectionResult] = []
        for detector in self.detectors:
            try:
                if detector.is_trained:
                    result = detector.detect(feature_vector)
                    results.append(result)
            except Exception as e:
                logger.warning(f"Detection failed for {detector.method.value}: {e}")
        
        if not results:
            return DetectionResult(False, 0.0, 0.0, self.method)
        
        # Calculate weighted voting
        total_weight = 0.0
        weighted_score = 0.0
        anomaly_votes = 0.0
        
        for result in results:
            weight = result.confidence if self.weight_by_confidence else 1.0
            total_weight += weight
            weighted_score += result.score * weight
            if result.is_anomaly:
                anomaly_votes += weight
        
        if total_weight == 0:
            return DetectionResult(False, 0.0, 0.0, self.method)
        
        final_score = weighted_score / total_weight
        vote_ratio = anomaly_votes / total_weight
        is_anomaly = vote_ratio > self.threshold
        
        # Confidence based on agreement
        confidences = [r.confidence for r in results]
        avg_confidence = sum(confidences) / len(confidences)
        
        return DetectionResult(
            is_anomaly=is_anomaly,
            score=final_score,
            confidence=avg_confidence,
            method=self.method,
            details={
                "vote_ratio": vote_ratio,
                "individual_results": [
                    {
                        "method": r.method.value,
                        "is_anomaly": r.is_anomaly,
                        "score": r.score,
                        "confidence": r.confidence
                    }
                    for r in results
                ]
            }
        )
    
    def update(self, feature_vector: FeatureVector, is_anomaly: bool) -> None:
        """Update all detectors."""
        for detector in self.detectors:
            try:
                detector.update(feature_vector, is_anomaly)
            except Exception as e:
                logger.warning(f"Update failed for {detector.method.value}: {e}")


@dataclass
class AnomalyConfig:
    """Configuration for anomaly detection system."""
    enabled: bool = True
    primary_method: DetectionMethod = DetectionMethod.ENSEMBLE
    z_score_threshold: float = 3.0
    iqr_multiplier: float = 1.5
    mad_threshold: float = 3.5
    isolation_forest_trees: int = 100
    lof_neighbors: int = 20
    ensemble_threshold: float = 0.5
    min_training_samples: int = 100
    auto_update: bool = True
    severity_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "low": 0.3,
        "medium": 0.5,
        "high": 0.7,
        "critical": 0.9
    })


class AnomalyDetectionEngine:
    """Main engine for ML-based anomaly detection."""
    
    def __init__(self, config: Optional[AnomalyConfig] = None):
        self.config = config or AnomalyConfig()
        self.detectors: Dict[DetectionMethod, AnomalyDetector] = {}
        self.primary_detector: Optional[AnomalyDetector] = None
        self.anomaly_history: List[Anomaly] = []
        self.false_positive_feedback: Dict[str, bool] = {}
        self._initialize_detectors()
    
    def _initialize_detectors(self) -> None:
        """Initialize configured detectors."""
        self.detectors[DetectionMethod.Z_SCORE] = ZScoreDetector(
            threshold=self.config.z_score_threshold
        )
        self.detectors[DetectionMethod.IQR] = IQRDetector(
            multiplier=self.config.iqr_multiplier
        )
        self.detectors[DetectionMethod.MAD] = MADDetector(
            threshold=self.config.mad_threshold
        )
        self.detectors[DetectionMethod.ISOLATION_FOREST] = IsolationForestDetector(
            n_trees=self.config.isolation_forest_trees
        )
        self.detectors[DetectionMethod.LOCAL_OUTLIER_FACTOR] = LocalOutlierFactorDetector(
            k_neighbors=self.config.lof_neighbors
        )
        
        # Create ensemble
        self.detectors[DetectionMethod.ENSEMBLE] = EnsembleDetector(
            detectors=[
                self.detectors[DetectionMethod.Z_SCORE],
                self.detectors[DetectionMethod.IQR],
                self.detectors[DetectionMethod.MAD]
            ],
            voting_threshold=self.config.ensemble_threshold
        )
        
        self.primary_detector = self.detectors.get(self.config.primary_method)
    
    def train(self, data: List[FeatureVector]) -> Dict[str, Any]:
        """Train all detectors on baseline data."""
        if len(data) < self.config.min_training_samples:
            logger.warning(f"Insufficient training data: {len(data)} < {self.config.min_training_samples}")
        
        results = {}
        for method, detector in self.detectors.items():
            try:
                detector.train(data)
                results[method.value] = {
                    "success": True,
                    "samples": len(data)
                }
            except Exception as e:
                results[method.value] = {
                    "success": False,
                    "error": str(e)
                }
                logger.error(f"Training failed for {method.value}: {e}")
        
        return results
    
    def detect(
        self,
        feature_vector: FeatureVector,
        methods: Optional[List[DetectionMethod]] = None
    ) -> List[Anomaly]:
        """Detect anomalies in feature vector."""
        if not self.config.enabled:
            return []
        
        detected_anomalies = []
        methods_to_use = methods or [self.config.primary_method]
        
        for method in methods_to_use:
            detector = self.detectors.get(method)
            if not detector or not detector.is_trained:
                continue
            
            try:
                result = detector.detect(feature_vector)
                
                if result.is_anomaly:
                    severity = self._calculate_severity(result.score)
                    
                    anomaly = Anomaly(
                        anomaly_id=self._generate_anomaly_id(feature_vector, method),
                        anomaly_type=self._infer_anomaly_type(result),
                        detection_method=method,
                        severity=severity,
                        score=result.score,
                        confidence=result.confidence,
                        timestamp=datetime.now(),
                        source_id=feature_vector.source_id,
                        feature_vector=feature_vector,
                        description=self._generate_description(result, method),
                        contributing_factors=result.details.get("anomalous_features", []),
                        context=result.details
                    )
                    
                    detected_anomalies.append(anomaly)
                    self.anomaly_history.append(anomaly)
                    
                    logger.info(f"Anomaly detected: {anomaly.anomaly_id} - {anomaly.severity.value}")
                
                # Auto-update detector
                if self.config.auto_update:
                    detector.update(feature_vector, result.is_anomaly)
                    
            except Exception as e:
                logger.error(f"Detection error with {method.value}: {e}")
        
        return detected_anomalies
    
    def _calculate_severity(self, score: float) -> Severity:
        """Calculate severity from anomaly score."""
        thresholds = self.config.severity_thresholds
        
        if score >= thresholds.get("critical", 0.9):
            return Severity.CRITICAL
        elif score >= thresholds.get("high", 0.7):
            return Severity.HIGH
        elif score >= thresholds.get("medium", 0.5):
            return Severity.MEDIUM
        elif score >= thresholds.get("low", 0.3):
            return Severity.LOW
        else:
            return Severity.INFO
    
    def _infer_anomaly_type(self, result: DetectionResult) -> AnomalyType:
        """Infer anomaly type from detection result."""
        if result.method in [DetectionMethod.Z_SCORE, DetectionMethod.IQR, DetectionMethod.MAD]:
            return AnomalyType.STATISTICAL_OUTLIER
        elif result.method == DetectionMethod.ISOLATION_FOREST:
            return AnomalyType.CLUSTERING_OUTLIER
        elif result.method == DetectionMethod.LOCAL_OUTLIER_FACTOR:
            return AnomalyType.CONTEXTUAL
        elif result.method == DetectionMethod.ENSEMBLE:
            return AnomalyType.COLLECTIVE
        else:
            return AnomalyType.BEHAVIORAL_DRIFT
    
    def _generate_anomaly_id(self, fv: FeatureVector, method: DetectionMethod) -> str:
        """Generate unique anomaly ID."""
        data = f"{fv.feature_id}:{method.value}:{datetime.now().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _generate_description(self, result: DetectionResult, method: DetectionMethod) -> str:
        """Generate human-readable description."""
        anomalous = result.details.get("anomalous_features", [])
        score = result.score
        
        if anomalous:
            features_str = ", ".join(anomalous[:3])
            return f"Detected by {method.value}: Anomalous features [{features_str}] with score {score:.3f}"
        else:
            return f"Detected by {method.value}: Overall anomaly score {score:.3f}"
    
    def mark_false_positive(self, anomaly_id: str) -> bool:
        """Mark an anomaly as false positive for feedback."""
        for anomaly in self.anomaly_history:
            if anomaly.anomaly_id == anomaly_id:
                anomaly.is_false_positive = True
                anomaly.reviewed = True
                self.false_positive_feedback[anomaly_id] = True
                
                # Update detector with feedback
                if anomaly.feature_vector and self.config.auto_update:
                    detector = self.detectors.get(anomaly.detection_method)
                    if detector:
                        detector.update(anomaly.feature_vector, False)
                
                logger.info(f"Anomaly {anomaly_id} marked as false positive")
                return True
        
        return False
    
    def get_anomaly_stats(self) -> Dict[str, Any]:
        """Get anomaly detection statistics."""
        if not self.anomaly_history:
            return {"total": 0}
        
        by_severity = {}
        by_method = {}
        by_type = {}
        false_positive_count = 0
        
        for anomaly in self.anomaly_history:
            by_severity[anomaly.severity.value] = by_severity.get(anomaly.severity.value, 0) + 1
            by_method[anomaly.detection_method.value] = by_method.get(anomaly.detection_method.value, 0) + 1
            by_type[anomaly.anomaly_type.value] = by_type.get(anomaly.anomaly_type.value, 0) + 1
            if anomaly.is_false_positive:
                false_positive_count += 1
        
        return {
            "total": len(self.anomaly_history),
            "by_severity": by_severity,
            "by_method": by_method,
            "by_type": by_type,
            "false_positives": false_positive_count,
            "false_positive_rate": false_positive_count / len(self.anomaly_history) if self.anomaly_history else 0.0
        }
    
    def export_model(self) -> Dict[str, Any]:
        """Export trained model state."""
        return {
            "config": {
                "enabled": self.config.enabled,
                "primary_method": self.config.primary_method.value,
                "severity_thresholds": self.config.severity_thresholds
            },
            "detectors": {
                method.value: {
                    "is_trained": detector.is_trained,
                    "training_samples": detector.training_samples
                }
                for method, detector in self.detectors.items()
            },
            "stats": self.get_anomaly_stats()
        }
