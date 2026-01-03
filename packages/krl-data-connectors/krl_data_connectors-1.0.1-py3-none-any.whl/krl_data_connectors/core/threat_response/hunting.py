"""
Threat Hunting Module for KRL Data Connectors.

Implements proactive threat hunting capabilities with query language,
hypothesis testing, and investigation workflows.

Features:
- Hunt query language for threat investigation
- Hypothesis-driven hunting
- Investigation playbooks
- Evidence collection and correlation
"""

import hashlib
import json
import logging
import re
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from enum import Enum
from typing import Any, Callable, Dict, Generator, List, Optional, Set, Tuple, Union
from uuid import uuid4

logger = logging.getLogger(__name__)


class HuntStatus(Enum):
    """Status of a hunt investigation."""
    
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ESCALATED = "escalated"
    ARCHIVED = "archived"


class HypothesisStatus(Enum):
    """Status of a hunt hypothesis."""
    
    PROPOSED = "proposed"
    TESTING = "testing"
    CONFIRMED = "confirmed"
    REFUTED = "refuted"
    INCONCLUSIVE = "inconclusive"


class EvidenceType(Enum):
    """Types of evidence collected during hunting."""
    
    LOG_ENTRY = "log_entry"
    NETWORK_TRAFFIC = "network_traffic"
    FILE_HASH = "file_hash"
    PROCESS_INFO = "process_info"
    USER_ACTIVITY = "user_activity"
    API_CALL = "api_call"
    CONFIGURATION = "configuration"
    ANOMALY = "anomaly"
    CORRELATION = "correlation"


@dataclass
class Evidence:
    """Evidence collected during threat hunting."""
    
    evidence_id: str
    evidence_type: EvidenceType
    source: str
    timestamp: datetime
    data: Dict[str, Any]
    relevance_score: float = 0.5
    tags: List[str] = field(default_factory=list)
    hash_value: str = ""
    notes: str = ""
    
    def __post_init__(self):
        """Generate hash if not provided."""
        if not self.hash_value:
            content = json.dumps(self.data, sort_keys=True).encode()
            self.hash_value = hashlib.sha256(content).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "evidence_id": self.evidence_id,
            "evidence_type": self.evidence_type.value,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "relevance_score": self.relevance_score,
            "tags": self.tags,
            "hash_value": self.hash_value,
            "notes": self.notes,
        }


@dataclass
class Hypothesis:
    """Hunting hypothesis for investigation."""
    
    hypothesis_id: str
    title: str
    description: str
    indicators: List[str]
    detection_logic: str
    status: HypothesisStatus = HypothesisStatus.PROPOSED
    confidence: float = 0.0
    evidence: List[Evidence] = field(default_factory=list)
    test_results: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    def add_evidence(self, evidence: Evidence) -> None:
        """Add evidence to the hypothesis."""
        self.evidence.append(evidence)
        self.updated_at = datetime.now(UTC)
        
        # Update confidence based on evidence
        relevant_evidence = [e for e in self.evidence if e.relevance_score > 0.5]
        if len(relevant_evidence) >= 3:
            avg_relevance = sum(e.relevance_score for e in relevant_evidence) / len(relevant_evidence)
            self.confidence = min(0.95, avg_relevance * 0.8 + 0.1 * len(relevant_evidence))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "hypothesis_id": self.hypothesis_id,
            "title": self.title,
            "description": self.description,
            "indicators": self.indicators,
            "detection_logic": self.detection_logic,
            "status": self.status.value,
            "confidence": self.confidence,
            "evidence_count": len(self.evidence),
            "test_results": self.test_results,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class Hunt:
    """Threat hunting investigation."""
    
    hunt_id: str
    name: str
    description: str
    objective: str
    scope: Dict[str, Any]
    hypotheses: List[Hypothesis] = field(default_factory=list)
    evidence: List[Evidence] = field(default_factory=list)
    status: HuntStatus = HuntStatus.DRAFT
    priority: int = 0
    created_by: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    findings: List[Dict[str, Any]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def start(self) -> None:
        """Start the hunt investigation."""
        self.status = HuntStatus.ACTIVE
        self.started_at = datetime.now(UTC)
    
    def pause(self) -> None:
        """Pause the hunt."""
        self.status = HuntStatus.PAUSED
    
    def complete(self, findings: List[Dict[str, Any]]) -> None:
        """Complete the hunt with findings."""
        self.status = HuntStatus.COMPLETED
        self.completed_at = datetime.now(UTC)
        self.findings = findings
    
    def escalate(self, reason: str) -> None:
        """Escalate the hunt."""
        self.status = HuntStatus.ESCALATED
        self.findings.append({
            "type": "escalation",
            "reason": reason,
            "timestamp": datetime.now(UTC).isoformat(),
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "hunt_id": self.hunt_id,
            "name": self.name,
            "description": self.description,
            "objective": self.objective,
            "scope": self.scope,
            "hypotheses": [h.to_dict() for h in self.hypotheses],
            "evidence_count": len(self.evidence),
            "status": self.status.value,
            "priority": self.priority,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "findings": self.findings,
            "tags": self.tags,
        }


class HuntQuery:
    """
    Query language for threat hunting.
    
    Supports searching across various data sources with
    filtering, aggregation, and correlation capabilities.
    """
    
    def __init__(self, query_string: str):
        """Initialize hunt query.
        
        Args:
            query_string: Query string in hunt query language
        """
        self.query_string = query_string
        self.parsed = self._parse(query_string)
    
    def _parse(self, query_string: str) -> Dict[str, Any]:
        """Parse query string into structured format."""
        parsed = {
            "source": "*",
            "filters": [],
            "fields": ["*"],
            "time_range": None,
            "limit": 1000,
            "aggregations": [],
            "correlations": [],
        }
        
        # Split into clauses
        clauses = query_string.strip().split("|")
        
        for clause in clauses:
            clause = clause.strip()
            
            # Source clause: source=<name>
            if clause.startswith("source="):
                parsed["source"] = clause.split("=", 1)[1].strip()
            
            # Time range: timerange=<start>,<end>
            elif clause.startswith("timerange="):
                time_str = clause.split("=", 1)[1].strip()
                if "," in time_str:
                    start, end = time_str.split(",", 1)
                    parsed["time_range"] = {"start": start.strip(), "end": end.strip()}
                else:
                    parsed["time_range"] = {"relative": time_str}
            
            # Filter clause: where <field> <op> <value>
            elif clause.startswith("where "):
                filter_expr = clause[6:].strip()
                parsed["filters"].append(self._parse_filter(filter_expr))
            
            # Field selection: select <fields>
            elif clause.startswith("select "):
                fields_str = clause[7:].strip()
                parsed["fields"] = [f.strip() for f in fields_str.split(",")]
            
            # Limit: limit=<n>
            elif clause.startswith("limit="):
                try:
                    parsed["limit"] = int(clause.split("=", 1)[1].strip())
                except ValueError:
                    pass
            
            # Aggregation: agg <func>(<field>) as <alias>
            elif clause.startswith("agg "):
                agg_expr = clause[4:].strip()
                parsed["aggregations"].append(self._parse_aggregation(agg_expr))
            
            # Correlation: correlate <field> with <source>.<field>
            elif clause.startswith("correlate "):
                corr_expr = clause[10:].strip()
                parsed["correlations"].append(self._parse_correlation(corr_expr))
        
        return parsed
    
    def _parse_filter(self, expr: str) -> Dict[str, Any]:
        """Parse a filter expression."""
        # Support operators: =, !=, >, <, >=, <=, contains, regex, in
        operators = ["!=", ">=", "<=", "=", ">", "<", " contains ", " regex ", " in "]
        
        for op in operators:
            if op in expr:
                parts = expr.split(op, 1)
                field = parts[0].strip()
                value = parts[1].strip().strip("'\"")
                
                # Handle 'in' operator with list
                if op.strip() == "in":
                    value = [v.strip().strip("'\"") for v in value.strip("()[]").split(",")]
                
                return {
                    "field": field,
                    "operator": op.strip(),
                    "value": value,
                }
        
        return {"field": expr, "operator": "exists", "value": True}
    
    def _parse_aggregation(self, expr: str) -> Dict[str, Any]:
        """Parse an aggregation expression."""
        # Pattern: func(field) as alias [group by field]
        match = re.match(r"(\w+)\(([^)]+)\)(?:\s+as\s+(\w+))?(?:\s+group\s+by\s+(.+))?", expr)
        
        if match:
            return {
                "function": match.group(1),
                "field": match.group(2).strip(),
                "alias": match.group(3) or match.group(1),
                "group_by": match.group(4).strip() if match.group(4) else None,
            }
        
        return {"function": "count", "field": "*", "alias": "count"}
    
    def _parse_correlation(self, expr: str) -> Dict[str, Any]:
        """Parse a correlation expression."""
        # Pattern: field with source.field
        match = re.match(r"(\S+)\s+with\s+(\S+)\.(\S+)", expr)
        
        if match:
            return {
                "local_field": match.group(1),
                "remote_source": match.group(2),
                "remote_field": match.group(3),
            }
        
        return {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Get parsed query as dictionary."""
        return self.parsed


class DataSource(ABC):
    """Abstract base class for hunt data sources."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Data source name."""
        pass
    
    @abstractmethod
    def search(
        self,
        filters: List[Dict[str, Any]],
        fields: List[str],
        time_range: Optional[Dict[str, Any]],
        limit: int,
    ) -> List[Dict[str, Any]]:
        """Search the data source."""
        pass
    
    @abstractmethod
    def aggregate(
        self,
        aggregations: List[Dict[str, Any]],
        filters: List[Dict[str, Any]],
        time_range: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Aggregate data from the source."""
        pass


class InMemoryDataSource(DataSource):
    """In-memory data source for testing and caching."""
    
    def __init__(self, source_name: str, data: Optional[List[Dict[str, Any]]] = None):
        """Initialize in-memory data source.
        
        Args:
            source_name: Name of the data source
            data: Initial data records
        """
        self._name = source_name
        self._data = data or []
    
    @property
    def name(self) -> str:
        """Data source name."""
        return self._name
    
    def add_record(self, record: Dict[str, Any]) -> None:
        """Add a record to the data source."""
        if "timestamp" not in record:
            record["timestamp"] = datetime.now(UTC).isoformat()
        self._data.append(record)
    
    def search(
        self,
        filters: List[Dict[str, Any]],
        fields: List[str],
        time_range: Optional[Dict[str, Any]],
        limit: int,
    ) -> List[Dict[str, Any]]:
        """Search the data source."""
        results = []
        
        for record in self._data:
            if len(results) >= limit:
                break
            
            # Apply time range filter
            if time_range and "timestamp" in record:
                record_time = record["timestamp"]
                if isinstance(record_time, str):
                    record_time = datetime.fromisoformat(record_time.replace("Z", "+00:00"))
                
                # Skip time range check for relative - would need current time context
            
            # Apply filters
            if self._matches_filters(record, filters):
                # Select fields
                if fields == ["*"]:
                    results.append(record)
                else:
                    results.append({f: record.get(f) for f in fields if f in record})
        
        return results
    
    def _matches_filters(self, record: Dict[str, Any], filters: List[Dict[str, Any]]) -> bool:
        """Check if record matches all filters."""
        for f in filters:
            field = f["field"]
            op = f["operator"]
            value = f["value"]
            
            record_value = record.get(field)
            
            if op == "=":
                if str(record_value) != str(value):
                    return False
            elif op == "!=":
                if str(record_value) == str(value):
                    return False
            elif op == ">":
                if not (record_value and record_value > value):
                    return False
            elif op == "<":
                if not (record_value and record_value < value):
                    return False
            elif op == ">=":
                if not (record_value and record_value >= value):
                    return False
            elif op == "<=":
                if not (record_value and record_value <= value):
                    return False
            elif op == "contains":
                if not (record_value and value in str(record_value)):
                    return False
            elif op == "regex":
                if not (record_value and re.search(value, str(record_value))):
                    return False
            elif op == "in":
                if str(record_value) not in value:
                    return False
            elif op == "exists":
                if field not in record:
                    return False
        
        return True
    
    def aggregate(
        self,
        aggregations: List[Dict[str, Any]],
        filters: List[Dict[str, Any]],
        time_range: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Aggregate data from the source."""
        # Get filtered data
        data = self.search(filters, ["*"], time_range, len(self._data))
        
        results = {}
        for agg in aggregations:
            func = agg["function"]
            field = agg["field"]
            alias = agg["alias"]
            group_by = agg.get("group_by")
            
            if group_by:
                # Grouped aggregation
                groups: Dict[str, List[Any]] = defaultdict(list)
                for record in data:
                    group_key = str(record.get(group_by, "unknown"))
                    if field == "*":
                        groups[group_key].append(1)
                    else:
                        if field in record:
                            groups[group_key].append(record[field])
                
                results[alias] = {}
                for group_key, values in groups.items():
                    results[alias][group_key] = self._apply_agg_func(func, values)
            else:
                # Simple aggregation
                values = []
                for record in data:
                    if field == "*":
                        values.append(1)
                    elif field in record:
                        values.append(record[field])
                
                results[alias] = self._apply_agg_func(func, values)
        
        return results
    
    def _apply_agg_func(self, func: str, values: List[Any]) -> Any:
        """Apply aggregation function to values."""
        if not values:
            return 0
        
        if func == "count":
            return len(values)
        elif func == "sum":
            return sum(v for v in values if isinstance(v, (int, float)))
        elif func == "avg":
            nums = [v for v in values if isinstance(v, (int, float))]
            return sum(nums) / len(nums) if nums else 0
        elif func == "min":
            return min(values)
        elif func == "max":
            return max(values)
        elif func == "distinct":
            return len(set(str(v) for v in values))
        
        return len(values)


@dataclass
class Playbook:
    """Investigation playbook for guided threat hunting."""
    
    playbook_id: str
    name: str
    description: str
    threat_type: str
    steps: List[Dict[str, Any]]
    required_sources: List[str]
    expected_indicators: List[str]
    response_actions: List[str]
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "playbook_id": self.playbook_id,
            "name": self.name,
            "description": self.description,
            "threat_type": self.threat_type,
            "steps": self.steps,
            "required_sources": self.required_sources,
            "expected_indicators": self.expected_indicators,
            "response_actions": self.response_actions,
            "created_at": self.created_at.isoformat(),
            "tags": self.tags,
        }


class ThreatHunter:
    """
    Proactive threat hunting system.
    
    Enables hypothesis-driven hunting, query-based investigation,
    and evidence collection for security analysis.
    """
    
    def __init__(self):
        """Initialize threat hunter."""
        self._data_sources: Dict[str, DataSource] = {}
        self._hunts: Dict[str, Hunt] = {}
        self._playbooks: Dict[str, Playbook] = {}
        self._evidence_store: Dict[str, Evidence] = {}
        
        # Hunt templates
        self._templates: Dict[str, Dict[str, Any]] = {}
        
        # Query cache
        self._query_cache: Dict[str, Tuple[datetime, Any]] = {}
        self._cache_ttl = timedelta(minutes=5)
        
        logger.info("ThreatHunter initialized")
    
    # Data Source Management
    
    def register_source(self, source: DataSource) -> None:
        """Register a data source for hunting.
        
        Args:
            source: Data source to register
        """
        self._data_sources[source.name] = source
        logger.info(f"Registered data source: {source.name}")
    
    def get_sources(self) -> List[str]:
        """Get list of registered data source names."""
        return list(self._data_sources.keys())
    
    # Query Execution
    
    def execute_query(
        self,
        query: Union[str, HuntQuery],
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """Execute a hunt query.
        
        Args:
            query: Query string or HuntQuery object
            use_cache: Whether to use cached results
            
        Returns:
            Query results
        """
        if isinstance(query, str):
            query = HuntQuery(query)
        
        query_hash = hashlib.md5(query.query_string.encode()).hexdigest()
        
        # Check cache
        if use_cache and query_hash in self._query_cache:
            cached_time, cached_result = self._query_cache[query_hash]
            if datetime.now(UTC) - cached_time < self._cache_ttl:
                return cached_result
        
        # Execute query
        parsed = query.parsed
        source_name = parsed["source"]
        
        # Get data sources to query
        if source_name == "*":
            sources = list(self._data_sources.values())
        elif source_name in self._data_sources:
            sources = [self._data_sources[source_name]]
        else:
            return {"error": f"Unknown data source: {source_name}", "results": []}
        
        # Execute search on each source
        all_results = []
        for source in sources:
            try:
                if parsed["aggregations"]:
                    agg_results = source.aggregate(
                        parsed["aggregations"],
                        parsed["filters"],
                        parsed["time_range"],
                    )
                    all_results.append({
                        "source": source.name,
                        "aggregations": agg_results,
                    })
                else:
                    search_results = source.search(
                        parsed["filters"],
                        parsed["fields"],
                        parsed["time_range"],
                        parsed["limit"],
                    )
                    all_results.extend([
                        {**r, "_source": source.name}
                        for r in search_results
                    ])
            except Exception as e:
                logger.error(f"Query error on {source.name}: {e}")
        
        result = {
            "query": query.query_string,
            "timestamp": datetime.now(UTC).isoformat(),
            "results": all_results,
            "count": len(all_results),
        }
        
        # Cache result
        self._query_cache[query_hash] = (datetime.now(UTC), result)
        
        return result
    
    # Hunt Management
    
    def create_hunt(
        self,
        name: str,
        description: str,
        objective: str,
        scope: Dict[str, Any],
        hypotheses: Optional[List[Dict[str, Any]]] = None,
        created_by: str = "",
        priority: int = 0,
        tags: Optional[List[str]] = None,
    ) -> Hunt:
        """Create a new threat hunt.
        
        Args:
            name: Hunt name
            description: Hunt description
            objective: Hunt objective
            scope: Hunt scope definition
            hypotheses: Initial hypotheses
            created_by: Creator identifier
            priority: Hunt priority
            tags: Hunt tags
            
        Returns:
            Created Hunt
        """
        hunt_id = f"HUNT-{datetime.now(UTC).strftime('%Y%m%d')}-{uuid4().hex[:8]}"
        
        hunt = Hunt(
            hunt_id=hunt_id,
            name=name,
            description=description,
            objective=objective,
            scope=scope,
            created_by=created_by,
            priority=priority,
            tags=tags or [],
        )
        
        # Add initial hypotheses
        if hypotheses:
            for h_data in hypotheses:
                hypothesis = Hypothesis(
                    hypothesis_id=f"HYP-{uuid4().hex[:8]}",
                    title=h_data.get("title", ""),
                    description=h_data.get("description", ""),
                    indicators=h_data.get("indicators", []),
                    detection_logic=h_data.get("detection_logic", ""),
                )
                hunt.hypotheses.append(hypothesis)
        
        self._hunts[hunt_id] = hunt
        logger.info(f"Created hunt: {hunt_id} - {name}")
        
        return hunt
    
    def start_hunt(self, hunt_id: str) -> bool:
        """Start a hunt investigation.
        
        Args:
            hunt_id: Hunt identifier
            
        Returns:
            True if started successfully
        """
        if hunt_id not in self._hunts:
            return False
        
        hunt = self._hunts[hunt_id]
        hunt.start()
        logger.info(f"Started hunt: {hunt_id}")
        
        return True
    
    def add_hypothesis(
        self,
        hunt_id: str,
        title: str,
        description: str,
        indicators: List[str],
        detection_logic: str,
    ) -> Optional[Hypothesis]:
        """Add a hypothesis to a hunt.
        
        Args:
            hunt_id: Hunt identifier
            title: Hypothesis title
            description: Hypothesis description
            indicators: Expected indicators
            detection_logic: Detection query/logic
            
        Returns:
            Created Hypothesis or None
        """
        if hunt_id not in self._hunts:
            return None
        
        hypothesis = Hypothesis(
            hypothesis_id=f"HYP-{uuid4().hex[:8]}",
            title=title,
            description=description,
            indicators=indicators,
            detection_logic=detection_logic,
        )
        
        self._hunts[hunt_id].hypotheses.append(hypothesis)
        logger.info(f"Added hypothesis to {hunt_id}: {hypothesis.hypothesis_id}")
        
        return hypothesis
    
    def test_hypothesis(
        self,
        hunt_id: str,
        hypothesis_id: str,
    ) -> Dict[str, Any]:
        """Test a hypothesis using its detection logic.
        
        Args:
            hunt_id: Hunt identifier
            hypothesis_id: Hypothesis identifier
            
        Returns:
            Test results
        """
        if hunt_id not in self._hunts:
            return {"error": "Hunt not found"}
        
        hunt = self._hunts[hunt_id]
        hypothesis = None
        for h in hunt.hypotheses:
            if h.hypothesis_id == hypothesis_id:
                hypothesis = h
                break
        
        if not hypothesis:
            return {"error": "Hypothesis not found"}
        
        # Update status
        hypothesis.status = HypothesisStatus.TESTING
        
        # Execute detection logic as query
        query_result = self.execute_query(hypothesis.detection_logic, use_cache=False)
        
        # Analyze results
        result_count = query_result.get("count", 0)
        
        test_result = {
            "hypothesis_id": hypothesis_id,
            "tested_at": datetime.now(UTC).isoformat(),
            "query": hypothesis.detection_logic,
            "result_count": result_count,
            "sample_results": query_result.get("results", [])[:10],
        }
        
        # Update hypothesis based on results
        hypothesis.test_results.append(test_result)
        
        if result_count > 0:
            # Evidence found - may support hypothesis
            for record in query_result.get("results", [])[:20]:
                evidence = self.collect_evidence(
                    evidence_type=EvidenceType.LOG_ENTRY,
                    source=record.get("_source", "query"),
                    data=record,
                    hunt_id=hunt_id,
                )
                hypothesis.add_evidence(evidence)
            
            if hypothesis.confidence > 0.7:
                hypothesis.status = HypothesisStatus.CONFIRMED
            else:
                hypothesis.status = HypothesisStatus.TESTING
        else:
            # No evidence found
            hypothesis.status = HypothesisStatus.INCONCLUSIVE
        
        test_result["final_status"] = hypothesis.status.value
        test_result["confidence"] = hypothesis.confidence
        
        return test_result
    
    def complete_hunt(
        self,
        hunt_id: str,
        summary: str,
        recommendations: List[str],
    ) -> bool:
        """Complete a hunt with findings.
        
        Args:
            hunt_id: Hunt identifier
            summary: Hunt summary
            recommendations: Recommendations based on findings
            
        Returns:
            True if completed successfully
        """
        if hunt_id not in self._hunts:
            return False
        
        hunt = self._hunts[hunt_id]
        
        # Compile findings
        findings = [
            {
                "type": "summary",
                "content": summary,
            },
            {
                "type": "recommendations",
                "content": recommendations,
            },
        ]
        
        # Add hypothesis results
        for hypothesis in hunt.hypotheses:
            findings.append({
                "type": "hypothesis_result",
                "hypothesis_id": hypothesis.hypothesis_id,
                "title": hypothesis.title,
                "status": hypothesis.status.value,
                "confidence": hypothesis.confidence,
                "evidence_count": len(hypothesis.evidence),
            })
        
        hunt.complete(findings)
        logger.info(f"Completed hunt: {hunt_id}")
        
        return True
    
    # Evidence Management
    
    def collect_evidence(
        self,
        evidence_type: EvidenceType,
        source: str,
        data: Dict[str, Any],
        hunt_id: Optional[str] = None,
        relevance_score: float = 0.5,
        tags: Optional[List[str]] = None,
        notes: str = "",
    ) -> Evidence:
        """Collect evidence during hunting.
        
        Args:
            evidence_type: Type of evidence
            source: Evidence source
            data: Evidence data
            hunt_id: Associated hunt (optional)
            relevance_score: Relevance score (0-1)
            tags: Evidence tags
            notes: Additional notes
            
        Returns:
            Collected Evidence
        """
        evidence_id = f"EV-{uuid4().hex[:12]}"
        
        evidence = Evidence(
            evidence_id=evidence_id,
            evidence_type=evidence_type,
            source=source,
            timestamp=datetime.now(UTC),
            data=data,
            relevance_score=relevance_score,
            tags=tags or [],
            notes=notes,
        )
        
        self._evidence_store[evidence_id] = evidence
        
        # Associate with hunt
        if hunt_id and hunt_id in self._hunts:
            self._hunts[hunt_id].evidence.append(evidence)
        
        return evidence
    
    def search_evidence(
        self,
        hunt_id: Optional[str] = None,
        evidence_type: Optional[EvidenceType] = None,
        min_relevance: float = 0.0,
        tags: Optional[List[str]] = None,
    ) -> List[Evidence]:
        """Search collected evidence.
        
        Args:
            hunt_id: Filter by hunt
            evidence_type: Filter by type
            min_relevance: Minimum relevance score
            tags: Filter by tags
            
        Returns:
            Matching evidence
        """
        results = []
        
        if hunt_id:
            if hunt_id not in self._hunts:
                return []
            evidence_list = self._hunts[hunt_id].evidence
        else:
            evidence_list = list(self._evidence_store.values())
        
        for evidence in evidence_list:
            if evidence_type and evidence.evidence_type != evidence_type:
                continue
            
            if evidence.relevance_score < min_relevance:
                continue
            
            if tags:
                if not any(t in evidence.tags for t in tags):
                    continue
            
            results.append(evidence)
        
        return results
    
    # Playbook Management
    
    def register_playbook(self, playbook: Playbook) -> None:
        """Register an investigation playbook.
        
        Args:
            playbook: Playbook to register
        """
        self._playbooks[playbook.playbook_id] = playbook
        logger.info(f"Registered playbook: {playbook.playbook_id} - {playbook.name}")
    
    def create_playbook(
        self,
        name: str,
        description: str,
        threat_type: str,
        steps: List[Dict[str, Any]],
        required_sources: List[str],
        expected_indicators: List[str],
        response_actions: List[str],
        tags: Optional[List[str]] = None,
    ) -> Playbook:
        """Create a new investigation playbook.
        
        Args:
            name: Playbook name
            description: Playbook description
            threat_type: Target threat type
            steps: Investigation steps
            required_sources: Required data sources
            expected_indicators: Expected threat indicators
            response_actions: Recommended response actions
            tags: Playbook tags
            
        Returns:
            Created Playbook
        """
        playbook_id = f"PB-{uuid4().hex[:12]}"
        
        playbook = Playbook(
            playbook_id=playbook_id,
            name=name,
            description=description,
            threat_type=threat_type,
            steps=steps,
            required_sources=required_sources,
            expected_indicators=expected_indicators,
            response_actions=response_actions,
            tags=tags or [],
        )
        
        self._playbooks[playbook_id] = playbook
        logger.info(f"Created playbook: {playbook_id} - {name}")
        
        return playbook
    
    def get_playbooks(
        self,
        threat_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Playbook]:
        """Get playbooks matching criteria.
        
        Args:
            threat_type: Filter by threat type
            tags: Filter by tags
            
        Returns:
            Matching playbooks
        """
        results = []
        
        for playbook in self._playbooks.values():
            if threat_type and playbook.threat_type != threat_type:
                continue
            
            if tags:
                if not any(t in playbook.tags for t in tags):
                    continue
            
            results.append(playbook)
        
        return results
    
    def run_playbook(
        self,
        playbook_id: str,
        hunt_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run a playbook investigation.
        
        Args:
            playbook_id: Playbook identifier
            hunt_id: Hunt to associate results with
            
        Returns:
            Playbook execution results
        """
        if playbook_id not in self._playbooks:
            return {"error": "Playbook not found"}
        
        playbook = self._playbooks[playbook_id]
        
        # Check required sources
        missing_sources = [
            s for s in playbook.required_sources
            if s not in self._data_sources
        ]
        
        if missing_sources:
            return {
                "error": "Missing required data sources",
                "missing": missing_sources,
            }
        
        # Create hunt if not provided
        if not hunt_id:
            hunt = self.create_hunt(
                name=f"Playbook: {playbook.name}",
                description=playbook.description,
                objective=f"Investigate {playbook.threat_type}",
                scope={"playbook_id": playbook_id},
                tags=playbook.tags,
            )
            hunt_id = hunt.hunt_id
            self.start_hunt(hunt_id)
        
        # Execute playbook steps
        results = {
            "playbook_id": playbook_id,
            "hunt_id": hunt_id,
            "started_at": datetime.now(UTC).isoformat(),
            "steps": [],
            "indicators_found": [],
        }
        
        for idx, step in enumerate(playbook.steps):
            step_result = {
                "step_number": idx + 1,
                "name": step.get("name", f"Step {idx + 1}"),
                "status": "pending",
            }
            
            # Execute step based on type
            step_type = step.get("type", "query")
            
            if step_type == "query":
                query = step.get("query", "")
                if query:
                    query_result = self.execute_query(query, use_cache=False)
                    step_result["status"] = "completed"
                    step_result["result_count"] = query_result.get("count", 0)
                    
                    # Check for indicators
                    for record in query_result.get("results", []):
                        for indicator in playbook.expected_indicators:
                            if indicator in str(record):
                                results["indicators_found"].append({
                                    "indicator": indicator,
                                    "step": idx + 1,
                                    "record": record,
                                })
            
            elif step_type == "hypothesis":
                hypothesis = self.add_hypothesis(
                    hunt_id=hunt_id,
                    title=step.get("title", ""),
                    description=step.get("description", ""),
                    indicators=step.get("indicators", []),
                    detection_logic=step.get("detection_logic", ""),
                )
                
                if hypothesis:
                    test_result = self.test_hypothesis(hunt_id, hypothesis.hypothesis_id)
                    step_result["status"] = "completed"
                    step_result["hypothesis_result"] = test_result
            
            results["steps"].append(step_result)
        
        results["completed_at"] = datetime.now(UTC).isoformat()
        results["indicators_count"] = len(results["indicators_found"])
        
        return results
    
    # Statistics
    
    def get_stats(self) -> Dict[str, Any]:
        """Get threat hunting statistics."""
        hunts = list(self._hunts.values())
        
        return {
            "total_hunts": len(hunts),
            "active_hunts": len([h for h in hunts if h.status == HuntStatus.ACTIVE]),
            "completed_hunts": len([h for h in hunts if h.status == HuntStatus.COMPLETED]),
            "total_evidence": len(self._evidence_store),
            "data_sources": len(self._data_sources),
            "playbooks": len(self._playbooks),
            "hypotheses_tested": sum(
                len(h.hypotheses) for h in hunts
            ),
            "confirmed_hypotheses": sum(
                len([hyp for hyp in h.hypotheses if hyp.status == HypothesisStatus.CONFIRMED])
                for h in hunts
            ),
        }
