"""
Threat Intelligence Module - Phase 2 Week 14

Threat feeds, IoC management, reputation databases, and threat scoring.

Copyright 2025 KR-Labs. All rights reserved.
"""

import hashlib
import json
import logging
import threading
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

logger = logging.getLogger(__name__)


class IoCType(Enum):
    """Types of Indicators of Compromise."""
    
    IP_ADDRESS = "ip_address"
    DOMAIN = "domain"
    URL = "url"
    FILE_HASH = "file_hash"
    EMAIL = "email"
    LICENSE_KEY = "license_key"
    USER_AGENT = "user_agent"
    API_KEY = "api_key"
    FINGERPRINT = "fingerprint"
    PATTERN = "pattern"


class ThreatCategory(Enum):
    """Categories of threats."""
    
    MALWARE = "malware"
    PHISHING = "phishing"
    BOTNET = "botnet"
    RANSOMWARE = "ransomware"
    APT = "apt"
    INSIDER = "insider"
    LICENSE_ABUSE = "license_abuse"
    CREDENTIAL_THEFT = "credential_theft"
    DATA_EXFILTRATION = "data_exfiltration"
    DENIAL_OF_SERVICE = "denial_of_service"
    UNKNOWN = "unknown"


class ThreatSeverity(Enum):
    """Threat severity levels."""
    
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class FeedSource(Enum):
    """Sources of threat intelligence feeds."""
    
    INTERNAL = "internal"
    COMMERCIAL = "commercial"
    OPEN_SOURCE = "open_source"
    GOVERNMENT = "government"
    ISAC = "isac"  # Information Sharing and Analysis Center
    CUSTOM = "custom"


@dataclass
class IoC:
    """Indicator of Compromise."""
    
    id: str = field(default_factory=lambda: f"ioc_{uuid.uuid4().hex[:12]}")
    ioc_type: IoCType = IoCType.IP_ADDRESS
    value: str = ""
    category: ThreatCategory = ThreatCategory.UNKNOWN
    severity: ThreatSeverity = ThreatSeverity.MEDIUM
    confidence: float = 0.5  # 0.0 to 1.0
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    source: str = ""
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    expiry: Optional[datetime] = None
    active: bool = True
    
    def __post_init__(self):
        """Normalize value based on type."""
        if self.ioc_type == IoCType.IP_ADDRESS:
            self.value = self.value.strip().lower()
        elif self.ioc_type == IoCType.DOMAIN:
            self.value = self.value.strip().lower()
        elif self.ioc_type == IoCType.FILE_HASH:
            self.value = self.value.strip().lower()
        elif self.ioc_type == IoCType.EMAIL:
            self.value = self.value.strip().lower()
    
    def is_expired(self) -> bool:
        """Check if IoC has expired."""
        if self.expiry is None:
            return False
        return datetime.now() > self.expiry
    
    def matches(self, value: str) -> bool:
        """Check if a value matches this IoC."""
        if not self.active or self.is_expired():
            return False
        
        normalized = value.strip().lower()
        
        if self.ioc_type == IoCType.PATTERN:
            import re
            try:
                return bool(re.match(self.value, normalized))
            except re.error:
                return False
        
        return normalized == self.value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "type": self.ioc_type.value,
            "value": self.value,
            "category": self.category.value,
            "severity": self.severity.value,
            "confidence": self.confidence,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "source": self.source,
            "tags": self.tags,
            "metadata": self.metadata,
            "expiry": self.expiry.isoformat() if self.expiry else None,
            "active": self.active,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IoC":
        """Create from dictionary."""
        return cls(
            id=data.get("id", f"ioc_{uuid.uuid4().hex[:12]}"),
            ioc_type=IoCType(data.get("type", "ip_address")),
            value=data.get("value", ""),
            category=ThreatCategory(data.get("category", "unknown")),
            severity=ThreatSeverity(data.get("severity", 2)),
            confidence=data.get("confidence", 0.5),
            first_seen=datetime.fromisoformat(data["first_seen"]) if "first_seen" in data else datetime.now(),
            last_seen=datetime.fromisoformat(data["last_seen"]) if "last_seen" in data else datetime.now(),
            source=data.get("source", ""),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
            expiry=datetime.fromisoformat(data["expiry"]) if data.get("expiry") else None,
            active=data.get("active", True),
        )


@dataclass
class ThreatActor:
    """Threat actor profile."""
    
    id: str = field(default_factory=lambda: f"actor_{uuid.uuid4().hex[:12]}")
    name: str = ""
    aliases: List[str] = field(default_factory=list)
    description: str = ""
    motivation: str = ""  # financial, espionage, hacktivism, etc.
    sophistication: str = ""  # low, medium, high, advanced
    country: Optional[str] = None
    sectors_targeted: List[str] = field(default_factory=list)
    ttps: List[str] = field(default_factory=list)  # Tactics, Techniques, Procedures
    associated_iocs: List[str] = field(default_factory=list)  # IoC IDs
    first_seen: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "aliases": self.aliases,
            "description": self.description,
            "motivation": self.motivation,
            "sophistication": self.sophistication,
            "country": self.country,
            "sectors_targeted": self.sectors_targeted,
            "ttps": self.ttps,
            "associated_iocs": self.associated_iocs,
            "first_seen": self.first_seen.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "active": self.active,
        }


@dataclass
class ThreatScore:
    """Aggregated threat score for an entity."""
    
    entity_id: str = ""
    entity_type: str = ""  # user, license, ip, etc.
    score: float = 0.0  # 0.0 (safe) to 100.0 (critical threat)
    factors: Dict[str, float] = field(default_factory=dict)
    ioc_matches: List[str] = field(default_factory=list)
    risk_indicators: List[str] = field(default_factory=list)
    calculated_at: datetime = field(default_factory=datetime.now)
    confidence: float = 0.5
    
    @property
    def risk_level(self) -> str:
        """Get risk level category."""
        if self.score >= 80:
            return "critical"
        elif self.score >= 60:
            return "high"
        elif self.score >= 40:
            return "medium"
        elif self.score >= 20:
            return "low"
        return "minimal"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "score": self.score,
            "risk_level": self.risk_level,
            "factors": self.factors,
            "ioc_matches": self.ioc_matches,
            "risk_indicators": self.risk_indicators,
            "calculated_at": self.calculated_at.isoformat(),
            "confidence": self.confidence,
        }


@dataclass
class ThreatReport:
    """Comprehensive threat report."""
    
    id: str = field(default_factory=lambda: f"report_{uuid.uuid4().hex[:12]}")
    title: str = ""
    summary: str = ""
    threat_level: ThreatSeverity = ThreatSeverity.MEDIUM
    category: ThreatCategory = ThreatCategory.UNKNOWN
    actors: List[str] = field(default_factory=list)
    iocs: List[str] = field(default_factory=list)
    affected_systems: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    author: str = ""
    status: str = "draft"  # draft, published, archived
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "summary": self.summary,
            "threat_level": self.threat_level.value,
            "category": self.category.value,
            "actors": self.actors,
            "iocs": self.iocs,
            "affected_systems": self.affected_systems,
            "recommendations": self.recommendations,
            "timeline": self.timeline,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "author": self.author,
            "status": self.status,
        }


class ThreatFeed(ABC):
    """Abstract base class for threat intelligence feeds."""
    
    def __init__(
        self,
        name: str,
        source: FeedSource,
        refresh_interval: int = 3600,
    ):
        self.name = name
        self.source = source
        self.refresh_interval = refresh_interval
        self.last_refresh: Optional[datetime] = None
        self.iocs: Dict[str, IoC] = {}
        self.enabled = True
        self._lock = threading.Lock()
    
    @abstractmethod
    def fetch(self) -> List[IoC]:
        """Fetch IoCs from the feed."""
        pass
    
    def refresh(self) -> int:
        """Refresh the feed and return count of new IoCs."""
        if not self.enabled:
            return 0
        
        try:
            new_iocs = self.fetch()
            count = 0
            
            with self._lock:
                for ioc in new_iocs:
                    if ioc.id not in self.iocs:
                        count += 1
                    self.iocs[ioc.id] = ioc
                
                self.last_refresh = datetime.now()
            
            logger.info(f"Feed {self.name} refreshed: {count} new IoCs")
            return count
            
        except Exception as e:
            logger.error(f"Error refreshing feed {self.name}: {e}")
            return 0
    
    def needs_refresh(self) -> bool:
        """Check if feed needs to be refreshed."""
        if self.last_refresh is None:
            return True
        
        elapsed = (datetime.now() - self.last_refresh).total_seconds()
        return elapsed >= self.refresh_interval
    
    def get_active_iocs(self) -> List[IoC]:
        """Get all active, non-expired IoCs."""
        with self._lock:
            return [
                ioc for ioc in self.iocs.values()
                if ioc.active and not ioc.is_expired()
            ]


class InternalFeed(ThreatFeed):
    """Internal threat intelligence feed."""
    
    def __init__(
        self,
        name: str = "internal",
        data_path: Optional[Path] = None,
    ):
        super().__init__(name, FeedSource.INTERNAL, refresh_interval=300)
        self.data_path = data_path
    
    def fetch(self) -> List[IoC]:
        """Fetch IoCs from internal storage."""
        if self.data_path and self.data_path.exists():
            try:
                with open(self.data_path) as f:
                    data = json.load(f)
                return [IoC.from_dict(item) for item in data.get("iocs", [])]
            except Exception as e:
                logger.error(f"Error loading internal feed: {e}")
        return []
    
    def add_ioc(self, ioc: IoC) -> None:
        """Add an IoC to the internal feed."""
        with self._lock:
            self.iocs[ioc.id] = ioc
        
        self._persist()
    
    def remove_ioc(self, ioc_id: str) -> bool:
        """Remove an IoC from the internal feed."""
        with self._lock:
            if ioc_id in self.iocs:
                del self.iocs[ioc_id]
                self._persist()
                return True
        return False
    
    def _persist(self) -> None:
        """Persist IoCs to storage."""
        if self.data_path:
            try:
                data = {"iocs": [ioc.to_dict() for ioc in self.iocs.values()]}
                self.data_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.data_path, "w") as f:
                    json.dump(data, f, indent=2)
            except Exception as e:
                logger.error(f"Error persisting internal feed: {e}")


class OpenSourceFeed(ThreatFeed):
    """Open source threat intelligence feed (OSINT)."""
    
    def __init__(
        self,
        name: str,
        url: str,
        parser: Optional[Callable[[str], List[IoC]]] = None,
    ):
        super().__init__(name, FeedSource.OPEN_SOURCE, refresh_interval=3600)
        self.url = url
        self.parser = parser or self._default_parser
    
    def fetch(self) -> List[IoC]:
        """Fetch IoCs from the open source feed."""
        try:
            import urllib.request
            
            req = urllib.request.Request(
                self.url,
                headers={"User-Agent": "KRL-ThreatIntel/1.0"}
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                content = response.read().decode("utf-8")
            
            return self.parser(content)
            
        except Exception as e:
            logger.error(f"Error fetching open source feed {self.name}: {e}")
            return []
    
    def _default_parser(self, content: str) -> List[IoC]:
        """Default parser for line-separated IoCs."""
        iocs = []
        
        for line in content.strip().split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            # Auto-detect IoC type
            ioc_type = self._detect_ioc_type(line)
            
            iocs.append(IoC(
                ioc_type=ioc_type,
                value=line,
                source=self.name,
                category=ThreatCategory.UNKNOWN,
            ))
        
        return iocs
    
    def _detect_ioc_type(self, value: str) -> IoCType:
        """Detect IoC type from value."""
        import re
        
        # IP address
        if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", value):
            return IoCType.IP_ADDRESS
        
        # Email
        if re.match(r"^[^@]+@[^@]+\.[^@]+$", value):
            return IoCType.EMAIL
        
        # URL
        if value.startswith(("http://", "https://")):
            return IoCType.URL
        
        # File hash (MD5, SHA1, SHA256)
        if re.match(r"^[a-f0-9]{32}$", value, re.IGNORECASE):
            return IoCType.FILE_HASH
        if re.match(r"^[a-f0-9]{40}$", value, re.IGNORECASE):
            return IoCType.FILE_HASH
        if re.match(r"^[a-f0-9]{64}$", value, re.IGNORECASE):
            return IoCType.FILE_HASH
        
        # Domain
        if re.match(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z]{2,})+$", value, re.IGNORECASE):
            return IoCType.DOMAIN
        
        return IoCType.PATTERN


@dataclass
class ReputationEntry:
    """Reputation entry for an entity."""
    
    entity: str
    entity_type: str
    score: float  # -100 (malicious) to +100 (trusted)
    category: Optional[ThreatCategory] = None
    reports: int = 0
    last_reported: Optional[datetime] = None
    first_seen: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ReputationDatabase:
    """Reputation database for entities."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path
        self.entries: Dict[str, ReputationEntry] = {}
        self._lock = threading.Lock()
        
        if storage_path and storage_path.exists():
            self._load()
    
    def _get_key(self, entity: str, entity_type: str) -> str:
        """Generate unique key for entity."""
        return hashlib.sha256(f"{entity_type}:{entity}".encode()).hexdigest()[:16]
    
    def lookup(self, entity: str, entity_type: str) -> Optional[ReputationEntry]:
        """Look up entity reputation."""
        key = self._get_key(entity, entity_type)
        with self._lock:
            return self.entries.get(key)
    
    def report(
        self,
        entity: str,
        entity_type: str,
        score_delta: float,
        category: Optional[ThreatCategory] = None,
        tags: Optional[List[str]] = None,
    ) -> ReputationEntry:
        """Report on an entity, updating reputation."""
        key = self._get_key(entity, entity_type)
        
        with self._lock:
            if key in self.entries:
                entry = self.entries[key]
                # Weighted average of scores
                entry.reports += 1
                entry.score = (entry.score * (entry.reports - 1) + score_delta) / entry.reports
                entry.score = max(-100, min(100, entry.score))
                entry.last_reported = datetime.now()
                
                if category:
                    entry.category = category
                if tags:
                    entry.tags = list(set(entry.tags + tags))
            else:
                entry = ReputationEntry(
                    entity=entity,
                    entity_type=entity_type,
                    score=score_delta,
                    category=category,
                    reports=1,
                    last_reported=datetime.now(),
                    tags=tags or [],
                )
                self.entries[key] = entry
        
        self._persist()
        return entry
    
    def set_reputation(
        self,
        entity: str,
        entity_type: str,
        score: float,
        category: Optional[ThreatCategory] = None,
    ) -> ReputationEntry:
        """Set explicit reputation for an entity."""
        key = self._get_key(entity, entity_type)
        
        with self._lock:
            entry = ReputationEntry(
                entity=entity,
                entity_type=entity_type,
                score=max(-100, min(100, score)),
                category=category,
                reports=1,
                last_reported=datetime.now(),
            )
            self.entries[key] = entry
        
        self._persist()
        return entry
    
    def get_malicious(self, threshold: float = -50) -> List[ReputationEntry]:
        """Get entities with reputation below threshold."""
        with self._lock:
            return [
                entry for entry in self.entries.values()
                if entry.score <= threshold
            ]
    
    def get_trusted(self, threshold: float = 50) -> List[ReputationEntry]:
        """Get entities with reputation above threshold."""
        with self._lock:
            return [
                entry for entry in self.entries.values()
                if entry.score >= threshold
            ]
    
    def _load(self) -> None:
        """Load database from storage."""
        if self.storage_path:
            try:
                with open(self.storage_path) as f:
                    data = json.load(f)
                
                for key, entry_data in data.items():
                    self.entries[key] = ReputationEntry(
                        entity=entry_data["entity"],
                        entity_type=entry_data["entity_type"],
                        score=entry_data["score"],
                        category=ThreatCategory(entry_data["category"]) if entry_data.get("category") else None,
                        reports=entry_data.get("reports", 1),
                        last_reported=datetime.fromisoformat(entry_data["last_reported"]) if entry_data.get("last_reported") else None,
                        first_seen=datetime.fromisoformat(entry_data["first_seen"]) if entry_data.get("first_seen") else datetime.now(),
                        tags=entry_data.get("tags", []),
                    )
            except Exception as e:
                logger.error(f"Error loading reputation database: {e}")
    
    def _persist(self) -> None:
        """Persist database to storage."""
        if self.storage_path:
            try:
                data = {}
                for key, entry in self.entries.items():
                    data[key] = {
                        "entity": entry.entity,
                        "entity_type": entry.entity_type,
                        "score": entry.score,
                        "category": entry.category.value if entry.category else None,
                        "reports": entry.reports,
                        "last_reported": entry.last_reported.isoformat() if entry.last_reported else None,
                        "first_seen": entry.first_seen.isoformat(),
                        "tags": entry.tags,
                    }
                
                self.storage_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.storage_path, "w") as f:
                    json.dump(data, f, indent=2)
            except Exception as e:
                logger.error(f"Error persisting reputation database: {e}")


@dataclass
class ThreatIntelConfig:
    """Configuration for threat intelligence."""
    
    enabled: bool = True
    auto_refresh: bool = True
    refresh_interval: int = 3600  # seconds
    ioc_expiry_days: int = 90
    min_confidence: float = 0.3
    enable_reputation: bool = True
    reputation_decay_days: int = 30
    score_weights: Dict[str, float] = field(default_factory=lambda: {
        "ioc_match": 40.0,
        "reputation": 30.0,
        "behavior": 20.0,
        "historical": 10.0,
    })


class ThreatIntelligence:
    """
    Threat Intelligence System.
    
    Aggregates threat feeds, manages IoCs, maintains reputation database,
    and calculates threat scores.
    """
    
    def __init__(self, config: Optional[ThreatIntelConfig] = None):
        self.config = config or ThreatIntelConfig()
        self.feeds: Dict[str, ThreatFeed] = {}
        self.reputation_db = ReputationDatabase()
        self.actors: Dict[str, ThreatActor] = {}
        self.reports: Dict[str, ThreatReport] = {}
        self._ioc_cache: Dict[str, Set[str]] = {}  # type -> set of values
        self._subscribers: List[Callable[[IoC], None]] = []
        self._lock = threading.Lock()
        self._refresh_thread: Optional[threading.Thread] = None
        self._running = False
        
        # Add default internal feed
        self.add_feed(InternalFeed())
    
    def add_feed(self, feed: ThreatFeed) -> None:
        """Add a threat feed."""
        self.feeds[feed.name] = feed
        logger.info(f"Added threat feed: {feed.name}")
    
    def remove_feed(self, name: str) -> bool:
        """Remove a threat feed."""
        if name in self.feeds:
            del self.feeds[name]
            return True
        return False
    
    def get_feed(self, name: str) -> Optional[ThreatFeed]:
        """Get a threat feed by name."""
        return self.feeds.get(name)
    
    def refresh_feeds(self) -> Dict[str, int]:
        """Refresh all feeds that need updating."""
        results = {}
        
        for name, feed in self.feeds.items():
            if feed.needs_refresh():
                count = feed.refresh()
                results[name] = count
                
                # Update IoC cache
                self._update_ioc_cache(feed)
        
        return results
    
    def _update_ioc_cache(self, feed: ThreatFeed) -> None:
        """Update the IoC lookup cache from a feed."""
        with self._lock:
            for ioc in feed.get_active_iocs():
                ioc_type = ioc.ioc_type.value
                if ioc_type not in self._ioc_cache:
                    self._ioc_cache[ioc_type] = set()
                self._ioc_cache[ioc_type].add(ioc.value)
    
    def add_ioc(self, ioc: IoC) -> None:
        """Add an IoC to the internal feed."""
        internal_feed = self.feeds.get("internal")
        if isinstance(internal_feed, InternalFeed):
            internal_feed.add_ioc(ioc)
            
            # Notify subscribers
            for subscriber in self._subscribers:
                try:
                    subscriber(ioc)
                except Exception as e:
                    logger.error(f"Error notifying subscriber: {e}")
    
    def check_ioc(
        self,
        value: str,
        ioc_type: Optional[IoCType] = None,
    ) -> List[IoC]:
        """Check if a value matches any known IoCs."""
        matches = []
        normalized = value.strip().lower()
        
        for feed in self.feeds.values():
            for ioc in feed.get_active_iocs():
                if ioc_type and ioc.ioc_type != ioc_type:
                    continue
                
                if ioc.matches(normalized):
                    matches.append(ioc)
        
        return matches
    
    def quick_check(self, value: str, ioc_type: IoCType) -> bool:
        """Quick check if a value is in the IoC cache."""
        normalized = value.strip().lower()
        
        with self._lock:
            cache = self._ioc_cache.get(ioc_type.value, set())
            return normalized in cache
    
    def calculate_threat_score(
        self,
        entity_id: str,
        entity_type: str,
        indicators: Optional[Dict[str, Any]] = None,
    ) -> ThreatScore:
        """Calculate comprehensive threat score for an entity."""
        score = ThreatScore(
            entity_id=entity_id,
            entity_type=entity_type,
        )
        
        indicators = indicators or {}
        total_weight = 0.0
        weighted_score = 0.0
        
        # Factor 1: IoC matches
        ioc_matches = []
        for key, value in indicators.items():
            if isinstance(value, str):
                matches = self.check_ioc(value)
                for match in matches:
                    ioc_matches.append(match.id)
                    score.risk_indicators.append(
                        f"IoC match: {match.ioc_type.value} - {match.category.value}"
                    )
        
        if ioc_matches:
            ioc_weight = self.config.score_weights.get("ioc_match", 40.0)
            ioc_severity = max(
                self.check_ioc(indicators.get("ip", ""))[0].severity.value
                for _ in [1] if self.check_ioc(indicators.get("ip", ""))
            ) if self.check_ioc(indicators.get("ip", "")) else 2
            
            weighted_score += ioc_weight * (ioc_severity / 4.0) * 100
            total_weight += ioc_weight
            score.factors["ioc_match"] = len(ioc_matches) * 25.0
        else:
            total_weight += self.config.score_weights.get("ioc_match", 40.0)
        
        score.ioc_matches = ioc_matches
        
        # Factor 2: Reputation
        if self.config.enable_reputation:
            rep_entry = self.reputation_db.lookup(entity_id, entity_type)
            if rep_entry:
                rep_weight = self.config.score_weights.get("reputation", 30.0)
                # Convert -100 to +100 reputation to 0-100 threat score
                rep_threat = (100 - rep_entry.score) / 2
                weighted_score += rep_weight * rep_threat
                total_weight += rep_weight
                score.factors["reputation"] = rep_threat
                
                if rep_entry.score < 0:
                    score.risk_indicators.append(
                        f"Negative reputation: {rep_entry.score:.1f}"
                    )
            else:
                total_weight += self.config.score_weights.get("reputation", 30.0)
                weighted_score += self.config.score_weights.get("reputation", 30.0) * 50  # Neutral
        
        # Factor 3: Behavioral indicators (from passed indicators)
        behavior_score = indicators.get("behavior_score", 50.0)
        behavior_weight = self.config.score_weights.get("behavior", 20.0)
        weighted_score += behavior_weight * behavior_score
        total_weight += behavior_weight
        score.factors["behavior"] = behavior_score
        
        # Factor 4: Historical data
        historical_score = indicators.get("historical_score", 50.0)
        historical_weight = self.config.score_weights.get("historical", 10.0)
        weighted_score += historical_weight * historical_score
        total_weight += historical_weight
        score.factors["historical"] = historical_score
        
        # Calculate final score
        if total_weight > 0:
            score.score = weighted_score / total_weight
        else:
            score.score = 50.0  # Neutral default
        
        score.score = max(0, min(100, score.score))
        score.calculated_at = datetime.now()
        
        # Confidence based on data availability
        score.confidence = min(1.0, len(score.factors) / 4.0)
        
        return score
    
    def add_actor(self, actor: ThreatActor) -> None:
        """Add a threat actor profile."""
        self.actors[actor.id] = actor
    
    def get_actor(self, actor_id: str) -> Optional[ThreatActor]:
        """Get a threat actor by ID."""
        return self.actors.get(actor_id)
    
    def search_actors(self, query: str) -> List[ThreatActor]:
        """Search threat actors by name or alias."""
        query_lower = query.lower()
        results = []
        
        for actor in self.actors.values():
            if query_lower in actor.name.lower():
                results.append(actor)
            elif any(query_lower in alias.lower() for alias in actor.aliases):
                results.append(actor)
        
        return results
    
    def create_report(
        self,
        title: str,
        summary: str,
        threat_level: ThreatSeverity,
        category: ThreatCategory,
        **kwargs,
    ) -> ThreatReport:
        """Create a threat report."""
        report = ThreatReport(
            title=title,
            summary=summary,
            threat_level=threat_level,
            category=category,
            **kwargs,
        )
        self.reports[report.id] = report
        return report
    
    def get_report(self, report_id: str) -> Optional[ThreatReport]:
        """Get a threat report by ID."""
        return self.reports.get(report_id)
    
    def subscribe(self, callback: Callable[[IoC], None]) -> None:
        """Subscribe to new IoC notifications."""
        self._subscribers.append(callback)
    
    def start_auto_refresh(self) -> None:
        """Start automatic feed refresh in background."""
        if self._running:
            return
        
        self._running = True
        self._refresh_thread = threading.Thread(
            target=self._refresh_loop,
            daemon=True,
        )
        self._refresh_thread.start()
    
    def stop_auto_refresh(self) -> None:
        """Stop automatic feed refresh."""
        self._running = False
        if self._refresh_thread:
            self._refresh_thread.join(timeout=5)
            self._refresh_thread = None
    
    def _refresh_loop(self) -> None:
        """Background refresh loop."""
        while self._running:
            try:
                self.refresh_feeds()
            except Exception as e:
                logger.error(f"Error in refresh loop: {e}")
            
            time.sleep(60)  # Check every minute
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get threat intelligence statistics."""
        total_iocs = sum(
            len(feed.get_active_iocs())
            for feed in self.feeds.values()
        )
        
        iocs_by_type: Dict[str, int] = {}
        iocs_by_category: Dict[str, int] = {}
        
        for feed in self.feeds.values():
            for ioc in feed.get_active_iocs():
                ioc_type = ioc.ioc_type.value
                iocs_by_type[ioc_type] = iocs_by_type.get(ioc_type, 0) + 1
                
                category = ioc.category.value
                iocs_by_category[category] = iocs_by_category.get(category, 0) + 1
        
        return {
            "total_feeds": len(self.feeds),
            "active_feeds": sum(1 for f in self.feeds.values() if f.enabled),
            "total_iocs": total_iocs,
            "iocs_by_type": iocs_by_type,
            "iocs_by_category": iocs_by_category,
            "total_actors": len(self.actors),
            "total_reports": len(self.reports),
            "reputation_entries": len(self.reputation_db.entries),
        }
    
    def export_iocs(self, format: str = "json") -> str:
        """Export all IoCs."""
        all_iocs = []
        
        for feed in self.feeds.values():
            for ioc in feed.get_active_iocs():
                all_iocs.append(ioc.to_dict())
        
        if format == "json":
            return json.dumps(all_iocs, indent=2)
        elif format == "csv":
            lines = ["type,value,category,severity,confidence,source"]
            for ioc in all_iocs:
                lines.append(
                    f"{ioc['type']},{ioc['value']},{ioc['category']},"
                    f"{ioc['severity']},{ioc['confidence']},{ioc['source']}"
                )
            return "\n".join(lines)
        else:
            return json.dumps(all_iocs)
    
    def __enter__(self):
        """Context manager entry."""
        if self.config.auto_refresh:
            self.start_auto_refresh()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_auto_refresh()
        return False
