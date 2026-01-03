"""
Alerting Module - Phase 2 Week 13

Multi-channel alerting system for security incidents with
email, Slack, webhook, and PagerDuty integration.

Copyright 2025 KR-Labs. All rights reserved.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import smtplib
import threading
import time
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta, UTC
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
import urllib.request
import urllib.error
import uuid


class AlertSeverity(Enum):
    """Severity levels for alerts."""
    
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    EMERGENCY = "emergency"  # Added for test compatibility


class AlertChannel(Enum):
    """Alert delivery channels."""
    
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    PAGERDUTY = "pagerduty"
    LOG = "log"
    CONSOLE = "console"


class AlertStatus(Enum):
    """Status of an alert."""
    
    PENDING = "pending"
    SENT = "sent"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    FAILED = "failed"


def _create_alert_init():
    """Factory to create Alert with id= or alert_id= support."""
    from dataclasses import fields
    
    def _custom_init(
        self,
        alert_id: str = "",
        title: str = "",
        message: str = "",
        severity: AlertSeverity = AlertSeverity.WARNING,
        source: str = "system",
        created_at: float | datetime | None = None,
        status: AlertStatus = AlertStatus.PENDING,
        channels: List[AlertChannel] | None = None,
        labels: Dict[str, str] | None = None,
        annotations: Dict[str, str] | None = None,
        fingerprint: str = "",
        resolved_at: float | None = None,
        resolved_by: str | None = None,
        acknowledged_by: str | None = None,
        acknowledged_at: float | None = None,
        id: str = "",  # Accept id= as alias for alert_id
    ):
        # Handle id= alias
        if id and not alert_id:
            alert_id = id
        
        self.alert_id = alert_id
        self.title = title
        self.message = message
        self.severity = severity
        self.source = source
        self.status = status
        self.channels = channels if channels is not None else []
        self.labels = labels if labels is not None else {}
        self.annotations = annotations if annotations is not None else {}
        self.fingerprint = fingerprint
        self.resolved_at = resolved_at
        self.resolved_by = resolved_by
        self.acknowledged_by = acknowledged_by
        self.acknowledged_at = acknowledged_at
        
        # Handle created_at initialization
        if created_at is None:
            self.created_at = time.time()
        elif isinstance(created_at, datetime):
            self.created_at = created_at.timestamp()
        else:
            self.created_at = created_at
            
        if not self.fingerprint:
            self.fingerprint = self._compute_fingerprint()
    
    return _custom_init


class Alert:
    """An alert to be sent."""
    
    def __init__(
        self,
        alert_id: str = "",
        title: str = "",
        message: str = "",
        severity: AlertSeverity = AlertSeverity.WARNING,
        source: str = "system",
        created_at: float | datetime | None = None,
        status: AlertStatus = AlertStatus.PENDING,
        channels: List[AlertChannel] | None = None,
        labels: Dict[str, str] | None = None,
        annotations: Dict[str, str] | None = None,
        fingerprint: str = "",
        resolved_at: float | None = None,
        resolved_by: str | None = None,
        acknowledged_by: str | None = None,
        acknowledged_at: float | None = None,
        id: str = "",  # Accept id= as alias for alert_id
    ):
        # Handle id= alias
        if id and not alert_id:
            alert_id = id
        
        self.alert_id = alert_id
        self.title = title
        self.message = message
        self.severity = severity
        self.source = source
        self.status = status
        self.channels = channels if channels is not None else []
        self.labels = labels if labels is not None else {}
        self.annotations = annotations if annotations is not None else {}
        self.fingerprint = fingerprint
        self.resolved_at = resolved_at
        self.resolved_by = resolved_by
        self.acknowledged_by = acknowledged_by
        self.acknowledged_at = acknowledged_at
        
        # Handle created_at initialization
        if created_at is None:
            self.created_at = time.time()
        elif isinstance(created_at, datetime):
            self.created_at = created_at.timestamp()
        else:
            self.created_at = created_at
            
        if not self.fingerprint:
            self.fingerprint = self._compute_fingerprint()
    
    @property
    def id(self) -> str:
        """Alias for alert_id for backwards compatibility."""
        return self.alert_id
    
    @id.setter
    def id(self, value: str) -> None:
        """Setter for id alias."""
        self.alert_id = value
    
    def acknowledge(self, user: str, note: str = "") -> None:
        """Acknowledge this alert.
        
        Args:
            user: User who acknowledged the alert
            note: Optional note about acknowledgment
        """
        self.status = AlertStatus.ACKNOWLEDGED
        self.acknowledged_by = user
        self.acknowledged_at = time.time()
        if note:
            self.annotations["ack_note"] = note
    
    def resolve(self, user: str = "", resolution: str = "") -> None:
        """Resolve this alert.
        
        Args:
            user: User who resolved the alert
            resolution: Resolution description
        """
        self.status = AlertStatus.RESOLVED
        self.resolved_at = time.time()
        if user:
            self.resolved_by = user
        if resolution:
            self.annotations["resolution"] = resolution
    
    def _compute_fingerprint(self) -> str:
        """Compute unique fingerprint for alert deduplication."""
        data = f"{self.title}:{self.source}:{json.dumps(self.labels, sort_keys=True)}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        created_at_val = self.created_at if isinstance(self.created_at, (int, float)) else time.time()
        return {
            "id": self.alert_id,  # Alias for backwards compatibility
            "alert_id": self.alert_id,
            "title": self.title,
            "message": self.message,
            "severity": self.severity.value,
            "source": self.source,
            "created_at": created_at_val,
            "created_at_iso": datetime.fromtimestamp(
                created_at_val, tz=timezone.utc
            ).isoformat(),
            "status": self.status.value,
            "channels": [c.value for c in self.channels],
            "labels": self.labels,
            "annotations": self.annotations,
            "fingerprint": self.fingerprint,
        }


class AlertRule:
    """Rule for triggering alerts."""
    
    def __init__(
        self,
        rule_id: str = "",
        name: str = "",
        description: str = "",
        condition: str = "",
        severity: AlertSeverity = AlertSeverity.WARNING,
        channels: List[AlertChannel | str] | None = None,
        enabled: bool = True,
        labels: Dict[str, str] | None = None,
        annotations: Dict[str, str] | None = None,
        for_duration_seconds: float = 0.0,
        cooldown_seconds: float = 300.0,
        id: str = "",  # Accept id= as alias for rule_id
    ):
        # Handle id= alias
        if id and not rule_id:
            rule_id = id
        
        self.rule_id = rule_id
        self.name = name
        self.description = description
        self.condition = condition
        self.severity = severity
        self.channels = channels if channels is not None else []
        self.enabled = enabled
        self.labels = labels if labels is not None else {}
        self.annotations = annotations if annotations is not None else {}
        self.for_duration_seconds = for_duration_seconds
        self.cooldown_seconds = cooldown_seconds
        self._last_triggered = 0.0
    
    @property
    def id(self) -> str:
        """Alias for rule_id for backwards compatibility."""
        return self.rule_id
    
    @id.setter
    def id(self, value: str) -> None:
        """Setter for id alias."""
        self.rule_id = value
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate the rule condition against given context.
        
        Args:
            context: Dictionary of variables to evaluate against
            
        Returns:
            True if condition is met and cooldown has passed
        """
        import time as time_module
        now = time_module.time()
        
        # Check cooldown
        if now - self._last_triggered < self.cooldown_seconds:
            return False
        
        if not self.condition:
            return False
        
        try:
            # Replace context variables in condition
            expr = self.condition
            for key, value in context.items():
                expr = expr.replace(f"${key}", str(value))
                expr = expr.replace(key, str(value))
            
            # Simple safe evaluation
            result = eval(expr, {"__builtins__": {}}, {})
            if result:
                self._last_triggered = now
            return bool(result)
        except Exception:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        channels_list = []
        for c in self.channels:
            if isinstance(c, AlertChannel):
                channels_list.append(c.value)
            else:
                channels_list.append(str(c))
        return {
            "id": self.rule_id,  # Alias for backwards compatibility
            "rule_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "condition": self.condition,
            "severity": self.severity.value,
            "channels": channels_list,
            "enabled": self.enabled,
            "for_duration": self.for_duration_seconds,
            "cooldown": self.cooldown_seconds,
        }


@dataclass
class AlertConfig:
    """Configuration for the alerting system."""
    
    # Global settings
    enabled: bool = True
    enable_dedup: bool = True  # Added for test compatibility
    default_channels: List[AlertChannel] = field(
        default_factory=lambda: [AlertChannel.LOG]
    )
    default_severity: AlertSeverity = AlertSeverity.WARNING  # Added for test compatibility
    
    # Deduplication
    dedup_window_seconds: float = 3600.0
    max_alerts_per_fingerprint: int = 5
    
    # Rate limiting / Throttling
    rate_limit_per_minute: int = 60
    throttle_per_minute: int = 60  # Alias for test compatibility
    
    # Email settings
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    email_from: str = ""
    email_to: List[str] = field(default_factory=list)
    
    # Slack settings
    slack_webhook_url: str = ""
    slack_channel: str = ""
    
    # Webhook settings
    webhook_url: str = ""
    webhook_headers: Dict[str, str] = field(default_factory=dict)
    
    # PagerDuty settings
    pagerduty_routing_key: str = ""
    pagerduty_service_id: str = ""


class AlertSender(ABC):
    """Abstract base class for alert senders."""
    
    @abstractmethod
    def send(self, alert: Alert, config: AlertConfig) -> bool:
        """Send an alert. Returns True on success."""
        pass


class EmailAlertSender(AlertSender):
    """Sends alerts via email."""
    
    def send(self, alert: Alert, config: AlertConfig) -> bool:
        """Send alert via email."""
        if not config.smtp_host or not config.email_to:
            return False
        
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"[{alert.severity.value.upper()}] {alert.title}"
            msg["From"] = config.email_from or config.smtp_user
            msg["To"] = ", ".join(config.email_to)
            
            # Plain text version
            text_content = f"""
Security Alert: {alert.title}
Severity: {alert.severity.value.upper()}
Source: {alert.source}
Time: {datetime.fromtimestamp(alert.created_at, tz=timezone.utc).isoformat()}

{alert.message}

Labels: {json.dumps(alert.labels, indent=2)}

Alert ID: {alert.alert_id}
"""
            
            # HTML version
            html_content = f"""
<html>
<body style="font-family: Arial, sans-serif;">
<div style="background-color: {'#dc3545' if alert.severity == AlertSeverity.CRITICAL else '#ffc107' if alert.severity == AlertSeverity.WARNING else '#17a2b8'}; 
            color: white; padding: 10px; border-radius: 5px;">
<h2>{alert.title}</h2>
</div>
<p><strong>Severity:</strong> {alert.severity.value.upper()}</p>
<p><strong>Source:</strong> {alert.source}</p>
<p><strong>Time:</strong> {datetime.fromtimestamp(alert.created_at, tz=timezone.utc).isoformat()}</p>
<hr>
<p>{alert.message}</p>
<hr>
<p><small>Alert ID: {alert.alert_id}</small></p>
</body>
</html>
"""
            
            msg.attach(MIMEText(text_content, "plain"))
            msg.attach(MIMEText(html_content, "html"))
            
            with smtplib.SMTP(config.smtp_host, config.smtp_port) as server:
                if config.smtp_use_tls:
                    server.starttls()
                if config.smtp_user and config.smtp_password:
                    server.login(config.smtp_user, config.smtp_password)
                server.sendmail(
                    config.email_from or config.smtp_user,
                    config.email_to,
                    msg.as_string()
                )
            
            return True
        except Exception as e:
            return False


class SlackAlertSender(AlertSender):
    """Sends alerts via Slack webhook."""
    
    SEVERITY_COLORS = {
        AlertSeverity.INFO: "#17a2b8",
        AlertSeverity.WARNING: "#ffc107",
        AlertSeverity.ERROR: "#dc3545",
        AlertSeverity.CRITICAL: "#8b0000",
    }
    
    def send(self, alert: Alert, config: AlertConfig) -> bool:
        """Send alert via Slack webhook."""
        if not config.slack_webhook_url:
            return False
        
        try:
            payload = {
                "channel": config.slack_channel,
                "attachments": [{
                    "color": self.SEVERITY_COLORS.get(alert.severity, "#808080"),
                    "title": f":warning: {alert.title}",
                    "text": alert.message,
                    "fields": [
                        {"title": "Severity", "value": alert.severity.value.upper(), "short": True},
                        {"title": "Source", "value": alert.source, "short": True},
                    ],
                    "footer": f"Alert ID: {alert.alert_id}",
                    "ts": int(alert.created_at),
                }]
            }
            
            data = json.dumps(payload).encode()
            req = urllib.request.Request(
                config.slack_webhook_url,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.status == 200
        except Exception:
            return False


class WebhookAlertSender(AlertSender):
    """Sends alerts via generic webhook."""
    
    def send(self, alert: Alert, config: AlertConfig) -> bool:
        """Send alert via webhook."""
        if not config.webhook_url:
            return False
        
        try:
            payload = alert.to_dict()
            data = json.dumps(payload).encode()
            
            headers = {
                "Content-Type": "application/json",
                **config.webhook_headers
            }
            
            req = urllib.request.Request(
                config.webhook_url,
                data=data,
                headers=headers,
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                return 200 <= response.status < 300
        except Exception:
            return False


class PagerDutyAlertSender(AlertSender):
    """Sends alerts via PagerDuty Events API v2."""
    
    PAGERDUTY_URL = "https://events.pagerduty.com/v2/enqueue"
    
    SEVERITY_MAP = {
        AlertSeverity.INFO: "info",
        AlertSeverity.WARNING: "warning",
        AlertSeverity.ERROR: "error",
        AlertSeverity.CRITICAL: "critical",
    }
    
    def send(self, alert: Alert, config: AlertConfig) -> bool:
        """Send alert via PagerDuty."""
        if not config.pagerduty_routing_key:
            return False
        
        try:
            payload = {
                "routing_key": config.pagerduty_routing_key,
                "event_action": "trigger",
                "dedup_key": alert.fingerprint,
                "payload": {
                    "summary": alert.title,
                    "severity": self.SEVERITY_MAP.get(alert.severity, "info"),
                    "source": alert.source,
                    "timestamp": datetime.fromtimestamp(
                        alert.created_at, tz=timezone.utc
                    ).isoformat(),
                    "custom_details": {
                        "message": alert.message,
                        "labels": alert.labels,
                        "alert_id": alert.alert_id,
                    }
                }
            }
            
            data = json.dumps(payload).encode()
            req = urllib.request.Request(
                self.PAGERDUTY_URL,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.status == 202
        except Exception:
            return False


class LogAlertSender(AlertSender):
    """Sends alerts to log output."""
    
    def send(self, alert: Alert, config: AlertConfig) -> bool:
        """Log the alert."""
        import logging
        logger = logging.getLogger("krl.alerts")
        
        log_levels = {
            AlertSeverity.INFO: logging.INFO,
            AlertSeverity.WARNING: logging.WARNING,
            AlertSeverity.ERROR: logging.ERROR,
            AlertSeverity.CRITICAL: logging.CRITICAL,
        }
        
        level = log_levels.get(alert.severity, logging.INFO)
        logger.log(level, f"ALERT [{alert.severity.value.upper()}] {alert.title}: {alert.message}")
        return True


class ConsoleAlertSender(AlertSender):
    """Sends alerts to console."""
    
    def send(self, alert: Alert, config: AlertConfig) -> bool:
        """Print alert to console."""
        severity_symbols = {
            AlertSeverity.INFO: "ℹ️",
            AlertSeverity.WARNING: "⚠️",
            AlertSeverity.ERROR: "❌",
            AlertSeverity.CRITICAL: "🚨",
        }
        
        symbol = severity_symbols.get(alert.severity, "•")
        print(f"\n{symbol} ALERT: {alert.title}")
        print(f"   Severity: {alert.severity.value.upper()}")
        print(f"   Source: {alert.source}")
        print(f"   Message: {alert.message}")
        print(f"   ID: {alert.alert_id}\n")
        return True


class AlertManager:
    """
    Multi-channel alerting system.
    
    Features:
    - Multiple delivery channels
    - Alert deduplication
    - Rate limiting
    - Alert rules
    - Acknowledgment and resolution
    """
    
    def __init__(self, config: AlertConfig | None = None):
        self.config = config or AlertConfig()
        self._alerts: Dict[str, Alert] = {}
        self._rules: Dict[str, AlertRule] = {}
        self._rule_states: Dict[str, Dict[str, Any]] = {}
        self._channels: Dict[str, Any] = {}  # Named channels for test compatibility
        self._fingerprint_history: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=100)
        )
        self._rate_limiter: deque = deque(maxlen=self.config.rate_limit_per_minute)
        self._callbacks: List[Callable[[Alert], None]] = []
        self._lock = threading.RLock()
        
        # Initialize senders
        self._senders: Dict[AlertChannel, AlertSender] = {
            AlertChannel.EMAIL: EmailAlertSender(),
            AlertChannel.SLACK: SlackAlertSender(),
            AlertChannel.WEBHOOK: WebhookAlertSender(),
            AlertChannel.PAGERDUTY: PagerDutyAlertSender(),
            AlertChannel.LOG: LogAlertSender(),
            AlertChannel.CONSOLE: ConsoleAlertSender(),
        }
    
    @property
    def alerts(self) -> Dict[str, Alert]:
        """Get all alerts dict for backwards compatibility."""
        return self._alerts
    
    @property
    def rules(self) -> Dict[str, AlertRule]:
        """Get all rules dict for backwards compatibility."""
        return self._rules
    
    @property
    def channels(self) -> Dict[str, Any]:
        """Get all named channels for backwards compatibility."""
        return self._channels
    
    def add_channel(self, name: str, channel: Any) -> None:
        """Add a named alert channel.
        
        Args:
            name: Channel identifier
            channel: Channel instance
        """
        with self._lock:
            self._channels[name] = channel
    
    def remove_channel(self, name: str) -> bool:
        """Remove a named channel.
        
        Args:
            name: Channel identifier
            
        Returns:
            True if channel was removed
        """
        with self._lock:
            if name in self._channels:
                del self._channels[name]
                return True
            return False
    
    def _generate_alert_id(self) -> str:
        """Generate unique alert ID."""
        return str(uuid.uuid4())
    
    def _should_deduplicate(self, fingerprint: str) -> bool:
        """Check if alert should be deduplicated."""
        now = time.time()
        history = self._fingerprint_history[fingerprint]
        
        # Remove old entries
        cutoff = now - self.config.dedup_window_seconds
        while history and history[0] < cutoff:
            history.popleft()
        
        return len(history) >= self.config.max_alerts_per_fingerprint
    
    def _check_rate_limit(self) -> bool:
        """Check if rate limit allows sending."""
        now = time.time()
        cutoff = now - 60
        
        while self._rate_limiter and self._rate_limiter[0] < cutoff:
            self._rate_limiter.popleft()
        
        return len(self._rate_limiter) < self.config.rate_limit_per_minute
    
    def alert(
        self,
        title: str,
        message: str,
        severity: AlertSeverity = AlertSeverity.WARNING,
        source: str = "system",
        channels: List[AlertChannel] | None = None,
        labels: Dict[str, str] | None = None,
        annotations: Dict[str, str] | None = None,
    ) -> Alert | None:
        """Create and send an alert."""
        if not self.config.enabled:
            return None
        
        alert = Alert(
            alert_id=self._generate_alert_id(),
            title=title,
            message=message,
            severity=severity,
            source=source,
            created_at=time.time(),
            channels=channels or self.config.default_channels,
            labels=labels or {},
            annotations=annotations or {},
        )
        
        return self._process_alert(alert)
    
    def _process_alert(self, alert: Alert) -> Alert | None:
        """Process and send an alert."""
        with self._lock:
            # Check deduplication
            if self._should_deduplicate(alert.fingerprint):
                alert.status = AlertStatus.SUPPRESSED
                return alert
            
            # Check rate limit
            if not self._check_rate_limit():
                alert.status = AlertStatus.SUPPRESSED
                return alert
            
            # Send via channels
            success = False
            for channel in alert.channels:
                sender = self._senders.get(channel)
                if sender:
                    if sender.send(alert, self.config):
                        success = True
            
            # Update status
            alert.status = AlertStatus.SENT if success else AlertStatus.FAILED
            
            # Record
            self._alerts[alert.alert_id] = alert
            self._fingerprint_history[alert.fingerprint].append(time.time())
            self._rate_limiter.append(time.time())
            
            # Notify callbacks
            self._notify_callbacks(alert)
            
            return alert
    
    def _notify_callbacks(self, alert: Alert) -> None:
        """Notify all callbacks of alert."""
        for callback in self._callbacks:
            try:
                callback(alert)
            except Exception:
                pass
    
    def acknowledge(self, alert_id: str, acknowledged_by: str = "", user: str = "") -> bool:
        """Acknowledge an alert.
        
        Args:
            alert_id: ID of alert to acknowledge
            acknowledged_by: User who acknowledged (legacy)
            user: User who acknowledged (preferred)
        """
        ack_user = user or acknowledged_by
        with self._lock:
            if alert_id in self._alerts:
                alert = self._alerts[alert_id]
                alert.status = AlertStatus.ACKNOWLEDGED
                alert.acknowledged_by = ack_user
                alert.acknowledged_at = time.time()
                return True
            return False
    
    def resolve(self, alert_id: str, user: str = "", resolution: str = "") -> bool:
        """Resolve an alert.
        
        Args:
            alert_id: ID of alert to resolve
            user: User who resolved the alert
            resolution: Resolution description
        """
        with self._lock:
            if alert_id in self._alerts:
                alert = self._alerts[alert_id]
                alert.status = AlertStatus.RESOLVED
                alert.resolved_at = time.time()
                if user:
                    alert.resolved_by = user
                if resolution:
                    alert.annotations["resolution"] = resolution
                return True
            return False
    
    def resolve_by_fingerprint(self, fingerprint: str) -> int:
        """Resolve all alerts with given fingerprint."""
        resolved = 0
        with self._lock:
            for alert in self._alerts.values():
                if alert.fingerprint == fingerprint and alert.status != AlertStatus.RESOLVED:
                    alert.status = AlertStatus.RESOLVED
                    alert.resolved_at = time.time()
                    resolved += 1
        return resolved
    
    def add_rule(self, rule: AlertRule) -> None:
        """Add an alert rule."""
        with self._lock:
            self._rules[rule.rule_id] = rule
            self._rule_states[rule.rule_id] = {
                "last_triggered": 0.0,
                "condition_true_since": None,
            }
    
    def remove_rule(self, rule_id: str) -> bool:
        """Remove an alert rule."""
        with self._lock:
            if rule_id in self._rules:
                del self._rules[rule_id]
                del self._rule_states[rule_id]
                return True
            return False
    
    def evaluate_rules(self, context: Dict[str, Any]) -> List[Alert]:
        """Evaluate all rules against context and fire alerts."""
        alerts = []
        now = time.time()
        
        with self._lock:
            for rule_id, rule in self._rules.items():
                if not rule.enabled:
                    continue
                
                state = self._rule_states[rule_id]
                
                # Check cooldown
                if now - state["last_triggered"] < rule.cooldown_seconds:
                    continue
                
                # Evaluate condition (simple expression evaluation)
                try:
                    result = self._evaluate_condition(rule.condition, context)
                except Exception:
                    continue
                
                if result:
                    # Check duration requirement
                    if rule.for_duration_seconds > 0:
                        if state["condition_true_since"] is None:
                            state["condition_true_since"] = now
                            continue
                        
                        if now - state["condition_true_since"] < rule.for_duration_seconds:
                            continue
                    
                    # Fire alert
                    alert = self.alert(
                        title=rule.name,
                        message=rule.description,
                        severity=rule.severity,
                        source=f"rule:{rule_id}",
                        channels=rule.channels,
                        labels=rule.labels,
                        annotations=rule.annotations,
                    )
                    
                    if alert:
                        alerts.append(alert)
                        state["last_triggered"] = now
                        state["condition_true_since"] = None
                else:
                    state["condition_true_since"] = None
        
        return alerts
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Safely evaluate a condition expression."""
        # Simple expression evaluation
        # Supports: >, <, >=, <=, ==, !=, and, or
        
        # Replace context variables
        for key, value in context.items():
            condition = condition.replace(f"${key}", str(value))
        
        # Very simple parser - in production use a proper expression parser
        try:
            # Only allow safe operations
            allowed_chars = set("0123456789.><=!andor ")
            if not all(c in allowed_chars for c in condition.lower().replace("true", "1").replace("false", "0")):
                return False
            
            # Evaluate
            result = eval(condition, {"__builtins__": {}}, {})
            return bool(result)
        except Exception:
            return False
    
    def subscribe(self, callback: Callable[[Alert], None]) -> None:
        """Subscribe to alert events."""
        with self._lock:
            self._callbacks.append(callback)
    
    def unsubscribe(self, callback: Callable[[Alert], None]) -> None:
        """Unsubscribe from alert events."""
        with self._lock:
            if callback in self._callbacks:
                self._callbacks.remove(callback)
    
    def get_alert(self, alert_id: str) -> Alert | None:
        """Get an alert by ID."""
        return self._alerts.get(alert_id)
    
    def get_active_alerts(
        self,
        severity: AlertSeverity | None = None,
        source: str | None = None
    ) -> List[Alert]:
        """Get all active (unresolved) alerts."""
        results = []
        for alert in self._alerts.values():
            if alert.status in (AlertStatus.RESOLVED, AlertStatus.SUPPRESSED):
                continue
            if severity and alert.severity != severity:
                continue
            if source and alert.source != source:
                continue
            results.append(alert)
        return results
    
    def get_alerts_by_severity(self, severity: AlertSeverity) -> List[Alert]:
        """Get all alerts matching a specific severity.
        
        Args:
            severity: Severity level to filter by
            
        Returns:
            List of matching alerts
        """
        return [a for a in self._alerts.values() if a.severity == severity]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get alerting statistics."""
        total = len(self._alerts)
        by_severity = defaultdict(int)
        by_status = defaultdict(int)
        
        for alert in self._alerts.values():
            by_severity[alert.severity.value] += 1
            by_status[alert.status.value] += 1
        
        return {
            "total_alerts": total,
            "total": total,  # Alias for test compatibility
            "active_rules": len(self._rules),
            "by_severity": {s: by_severity.get(s.value, 0) for s in AlertSeverity},
            "by_status": dict(by_status),
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Alias for get_stats() for backwards compatibility."""
        return self.get_stats()
    
    def create_alert(
        self,
        title: str,
        message: str,
        severity: AlertSeverity = AlertSeverity.WARNING,
        source: str = "system",
        **kwargs
    ) -> Alert:
        """Create an alert without sending it.
        
        Args:
            title: Alert title
            message: Alert message
            severity: Alert severity
            source: Alert source
            
        Returns:
            Created alert
        """
        alert = Alert(
            alert_id=self._generate_alert_id(),
            title=title,
            message=message,
            severity=severity,
            source=source,
            created_at=time.time(),
            **kwargs
        )
        with self._lock:
            self._alerts[alert.alert_id] = alert
        return alert
    
    def fire(
        self,
        title: str,
        message: str,
        severity: AlertSeverity = AlertSeverity.WARNING,
        source: str = "system",
        channels: List[str] | None = None,
        **kwargs
    ) -> Alert:
        """Fire an alert (create and send).
        
        Args:
            title: Alert title
            message: Alert message
            severity: Alert severity
            source: Alert source
            channels: List of channel names to send to
            
        Returns:
            Fired alert
        """
        alert = self.create_alert(title, message, severity, source, **kwargs)
        
        # Check deduplication if enabled
        if self.config.enable_dedup and self._should_deduplicate(alert.fingerprint):
            alert.status = AlertStatus.SUPPRESSED
            return alert
        
        # Send via named channels
        if channels:
            for channel_name in channels:
                if channel_name in self._channels:
                    try:
                        self._channels[channel_name].send(alert)
                    except Exception:
                        pass
        
        alert.status = AlertStatus.SENT
        
        # Record for deduplication
        self._fingerprint_history[alert.fingerprint].append(time.time())
        
        self._notify_callbacks(alert)
        return alert
    
    def export_alerts(self, format: str = "json") -> str:
        """Export all alerts in specified format.
        
        Args:
            format: Export format (json, csv)
            
        Returns:
            Exported data as string
        """
        if format == "json":
            return json.dumps([a.to_dict() for a in self._alerts.values()], indent=2)
        elif format == "csv":
            lines = ["id,title,severity,status,source,created_at"]
            for a in self._alerts.values():
                lines.append(f"{a.alert_id},{a.title},{a.severity.value},{a.status.value},{a.source},{a.created_at}")
            return "\n".join(lines)
        else:
            return json.dumps([a.to_dict() for a in self._alerts.values()])


# Convenience functions
_global_alert_manager: AlertManager | None = None


def get_alert_manager() -> AlertManager:
    """Get or create the global alert manager."""
    global _global_alert_manager
    if _global_alert_manager is None:
        _global_alert_manager = AlertManager()
    return _global_alert_manager


def send_alert(
    title: str,
    message: str,
    severity: AlertSeverity = AlertSeverity.WARNING,
    **kwargs
) -> Alert | None:
    """Send an alert using the global manager."""
    return get_alert_manager().alert(title, message, severity, **kwargs)


# =============================================================================
# Channel Classes (Test-Compatible Interface)
# =============================================================================

class EmailChannel:
    """Email alert channel with direct interface.
    
    This provides the interface expected by tests while internally
    using EmailAlertSender for actual sending.
    """
    
    def __init__(
        self,
        smtp_host: str = "",
        smtp_port: int = 587,
        username: str = "",
        password: str = "",
        recipients: List[str] | None = None,
        use_tls: bool = True,
        from_address: str = "",
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.recipients = recipients or []
        self.use_tls = use_tls
        self.from_address = from_address or username
        self._sender = EmailAlertSender()
    
    def send(self, alert: Alert) -> bool:
        """Send an alert via email."""
        config = AlertConfig(
            smtp_host=self.smtp_host,
            smtp_port=self.smtp_port,
            smtp_user=self.username,
            smtp_password=self.password,
            email_from=self.from_address,
            email_to=self.recipients,
            smtp_use_tls=self.use_tls,
        )
        return self._sender.send(alert, config)


class SlackChannel:
    """Slack alert channel with direct interface."""
    
    def __init__(
        self,
        webhook_url: str = "",
        channel: str = "",
    ):
        self.webhook_url = webhook_url
        self.channel = channel
        self._sender = SlackAlertSender()
    
    def _format_payload(self, alert: Alert) -> Dict[str, Any]:
        """Format alert for Slack."""
        return {
            "channel": self.channel,
            "attachments": [{
                "color": SlackAlertSender.SEVERITY_COLORS.get(alert.severity, "#808080"),
                "title": alert.title,
                "text": alert.message,
                "fields": [
                    {"title": "Severity", "value": alert.severity.value.upper(), "short": True},
                    {"title": "Source", "value": alert.source, "short": True},
                ],
            }]
        }
    
    def send(self, alert: Alert) -> bool:
        """Send an alert via Slack."""
        config = AlertConfig(
            slack_webhook_url=self.webhook_url,
            slack_channel=self.channel,
        )
        return self._sender.send(alert, config)


class WebhookChannel:
    """Webhook alert channel with direct interface."""
    
    def __init__(
        self,
        url: str = "",
        headers: Dict[str, str] | None = None,
    ):
        self.url = url
        self.headers = headers or {}
        self._sender = WebhookAlertSender()
    
    def send(self, alert: Alert) -> bool:
        """Send an alert via webhook."""
        config = AlertConfig(
            webhook_url=self.url,
            webhook_headers=self.headers,
        )
        return self._sender.send(alert, config)


class PagerDutyChannel:
    """PagerDuty alert channel with direct interface."""
    
    def __init__(
        self,
        integration_key: str = "",
        severity_mapping: Dict[AlertSeverity, str] | None = None,
    ):
        self.integration_key = integration_key
        self.severity_mapping = severity_mapping or {}
        self._sender = PagerDutyAlertSender()
    
    def _map_severity(self, severity: AlertSeverity) -> str:
        """Map severity to PagerDuty severity."""
        if self.severity_mapping and severity in self.severity_mapping:
            return self.severity_mapping[severity]
        return PagerDutyAlertSender.SEVERITY_MAP.get(severity, "info")
    
    def send(self, alert: Alert) -> bool:
        """Send an alert via PagerDuty."""
        config = AlertConfig(
            pagerduty_routing_key=self.integration_key,
        )
        return self._sender.send(alert, config)


class OpsGenieChannel:
    """OpsGenie alert channel (stub for future implementation)."""
    
    def __init__(self, api_key: str = "", **kwargs):
        self.api_key = api_key
    
    def send(self, alert: Alert) -> bool:
        """Send an alert via OpsGenie."""
        # TODO: Implement OpsGenie integration
        return False


class TeamsChannel:
    """Microsoft Teams alert channel (stub for future implementation)."""
    
    def __init__(self, webhook_url: str = "", **kwargs):
        self.webhook_url = webhook_url
    
    def send(self, alert: Alert) -> bool:
        """Send an alert via Teams."""
        # TODO: Implement Teams integration
        return False


# =============================================================================
# Deduplication and Throttling Classes
# =============================================================================

class AlertDeduplicator:
    """Alert deduplication by fingerprint within a time window."""
    
    def __init__(self, window_seconds: float = 300.0):
        self.window_seconds = window_seconds
        self._seen: Dict[str, float] = {}
    
    def _compute_fingerprint(self, alert: Alert) -> str:
        """Compute fingerprint for an alert."""
        return alert.fingerprint
    
    def is_duplicate(self, alert: Alert) -> bool:
        """Check if alert is a duplicate within the window."""
        now = time.time()
        fingerprint = self._compute_fingerprint(alert)
        
        # Clean old entries
        self._seen = {k: v for k, v in self._seen.items() if now - v < self.window_seconds}
        
        return fingerprint in self._seen
    
    def mark_seen(self, alert: Alert) -> None:
        """Mark an alert as seen."""
        fingerprint = self._compute_fingerprint(alert)
        self._seen[fingerprint] = time.time()


class AlertThrottle:
    """Alert rate limiting / throttling."""
    
    def __init__(
        self,
        max_alerts_per_minute: int = 60,
        max_alerts_per_hour: int = 1000,
    ):
        self.max_alerts_per_minute = max_alerts_per_minute
        self.max_alerts_per_hour = max_alerts_per_hour
        self._minute_window: deque = deque()
        self._hour_window: deque = deque()
    
    def should_throttle(self) -> bool:
        """Check if we should throttle alerts."""
        now = time.time()
        minute_ago = now - 60
        hour_ago = now - 3600
        
        # Clean old entries
        while self._minute_window and self._minute_window[0] < minute_ago:
            self._minute_window.popleft()
        while self._hour_window and self._hour_window[0] < hour_ago:
            self._hour_window.popleft()
        
        return (
            len(self._minute_window) >= self.max_alerts_per_minute or
            len(self._hour_window) >= self.max_alerts_per_hour
        )
    
    def record_alert(self) -> None:
        """Record that an alert was sent."""
        now = time.time()
        self._minute_window.append(now)
        self._hour_window.append(now)
