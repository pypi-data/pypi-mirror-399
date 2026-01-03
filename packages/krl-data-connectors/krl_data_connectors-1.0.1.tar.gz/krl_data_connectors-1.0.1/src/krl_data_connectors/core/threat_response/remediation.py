"""
Automated Remediation Engine - Phase 2 Week 14

Safe automated response execution with rollback capabilities.

Copyright 2025 KR-Labs. All rights reserved.
"""

import json
import logging
import subprocess
import threading
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class ActionType(Enum):
    """Types of remediation actions."""
    
    SCRIPT = "script"
    API_CALL = "api_call"
    CONFIG_CHANGE = "config_change"
    SERVICE_RESTART = "service_restart"
    ACCESS_REVOKE = "access_revoke"
    RATE_LIMIT = "rate_limit"
    FEATURE_DISABLE = "feature_disable"
    DATA_BACKUP = "data_backup"
    NOTIFICATION = "notification"
    CUSTOM = "custom"


class ActionStatus(Enum):
    """Status of a remediation action."""
    
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    SKIPPED = "skipped"


class SafetyLevel(Enum):
    """Safety level for remediation actions."""
    
    SAFE = 1  # Can be auto-executed
    MODERATE = 2  # Requires basic validation
    RISKY = 3  # Requires approval
    CRITICAL = 4  # Requires multi-approval


@dataclass
class ActionResult:
    """Result of a remediation action."""
    
    action_id: str
    status: ActionStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    output: str = ""
    error: Optional[str] = None
    rollback_available: bool = False
    rollback_data: Optional[Dict[str, Any]] = None
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Get execution duration in seconds."""
        if self.completed_at and self.started_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "action_id": self.action_id,
            "status": self.status.value,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "output": self.output,
            "error": self.error,
            "rollback_available": self.rollback_available,
            "duration_seconds": self.duration_seconds,
        }


@dataclass
class RemediationAction:
    """A remediation action definition."""
    
    id: str = field(default_factory=lambda: f"action_{uuid.uuid4().hex[:12]}")
    name: str = ""
    description: str = ""
    action_type: ActionType = ActionType.CUSTOM
    safety_level: SafetyLevel = SafetyLevel.MODERATE
    target: str = ""  # Entity or resource to act upon
    parameters: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 30
    retry_count: int = 0
    retry_delay_seconds: int = 5
    requires_confirmation: bool = False
    reversible: bool = True
    rollback_action: Optional[str] = None  # ID of rollback action
    pre_checks: List[str] = field(default_factory=list)
    post_checks: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "action_type": self.action_type.value,
            "safety_level": self.safety_level.value,
            "target": self.target,
            "parameters": self.parameters,
            "timeout_seconds": self.timeout_seconds,
            "retry_count": self.retry_count,
            "reversible": self.reversible,
            "rollback_action": self.rollback_action,
            "tags": self.tags,
        }


@dataclass
class Rollback:
    """Rollback record for a remediation action."""
    
    id: str = field(default_factory=lambda: f"rollback_{uuid.uuid4().hex[:12]}")
    action_id: str = ""
    original_action: RemediationAction = field(default_factory=RemediationAction)
    rollback_action: Optional[RemediationAction] = None
    state_before: Dict[str, Any] = field(default_factory=dict)
    state_after: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    executed_at: Optional[datetime] = None
    executed_by: Optional[str] = None
    status: ActionStatus = ActionStatus.PENDING
    result: Optional[ActionResult] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "action_id": self.action_id,
            "original_action": self.original_action.to_dict(),
            "rollback_action": self.rollback_action.to_dict() if self.rollback_action else None,
            "state_before": self.state_before,
            "created_at": self.created_at.isoformat(),
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "status": self.status.value,
        }


@dataclass
class PlaybookStep:
    """A step in a remediation playbook."""
    
    id: str = field(default_factory=lambda: f"step_{uuid.uuid4().hex[:8]}")
    name: str = ""
    action: RemediationAction = field(default_factory=RemediationAction)
    order: int = 0
    condition: Optional[str] = None  # Condition to execute this step
    on_failure: str = "abort"  # abort, continue, skip_to
    skip_to: Optional[str] = None  # Step ID to skip to on failure
    wait_after_seconds: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "action": self.action.to_dict(),
            "order": self.order,
            "condition": self.condition,
            "on_failure": self.on_failure,
            "wait_after_seconds": self.wait_after_seconds,
        }


@dataclass
class RemediationPlaybook:
    """A playbook containing multiple remediation steps."""
    
    id: str = field(default_factory=lambda: f"playbook_{uuid.uuid4().hex[:12]}")
    name: str = ""
    description: str = ""
    trigger_conditions: List[str] = field(default_factory=list)
    steps: List[PlaybookStep] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    safety_level: SafetyLevel = SafetyLevel.MODERATE
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    author: str = ""
    tags: List[str] = field(default_factory=list)
    
    def add_step(self, step: PlaybookStep) -> None:
        """Add a step to the playbook."""
        self.steps.append(step)
        self.steps.sort(key=lambda s: s.order)
        self.updated_at = datetime.now()
    
    def get_next_step(self, current_step_id: Optional[str] = None) -> Optional[PlaybookStep]:
        """Get the next step in the playbook."""
        if not self.steps:
            return None
        
        if current_step_id is None:
            return self.steps[0]
        
        for i, step in enumerate(self.steps):
            if step.id == current_step_id and i + 1 < len(self.steps):
                return self.steps[i + 1]
        
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "trigger_conditions": self.trigger_conditions,
            "steps": [s.to_dict() for s in self.steps],
            "variables": self.variables,
            "safety_level": self.safety_level.value,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "author": self.author,
            "tags": self.tags,
        }


class ActionHandler(ABC):
    """Abstract base class for action handlers."""
    
    @abstractmethod
    def execute(
        self,
        action: RemediationAction,
        context: Dict[str, Any],
    ) -> ActionResult:
        """Execute the action."""
        pass
    
    @abstractmethod
    def validate(
        self,
        action: RemediationAction,
        context: Dict[str, Any],
    ) -> Tuple[bool, str]:
        """Validate the action before execution."""
        pass
    
    def can_rollback(self, action: RemediationAction) -> bool:
        """Check if action can be rolled back."""
        return action.reversible


class ScriptHandler(ActionHandler):
    """Handler for script-based remediation actions."""
    
    def __init__(self, sandbox_dir: Optional[Path] = None):
        self.sandbox_dir = sandbox_dir
    
    def execute(
        self,
        action: RemediationAction,
        context: Dict[str, Any],
    ) -> ActionResult:
        """Execute a script action."""
        result = ActionResult(
            action_id=action.id,
            status=ActionStatus.RUNNING,
            started_at=datetime.now(),
        )
        
        try:
            script = action.parameters.get("script", "")
            args = action.parameters.get("args", [])
            
            # Execute script
            process = subprocess.run(
                [script] + args,
                capture_output=True,
                text=True,
                timeout=action.timeout_seconds,
                cwd=str(self.sandbox_dir) if self.sandbox_dir else None,
            )
            
            result.output = process.stdout
            result.error = process.stderr if process.returncode != 0 else None
            result.status = ActionStatus.COMPLETED if process.returncode == 0 else ActionStatus.FAILED
            
        except subprocess.TimeoutExpired:
            result.status = ActionStatus.FAILED
            result.error = f"Script timed out after {action.timeout_seconds} seconds"
        except Exception as e:
            result.status = ActionStatus.FAILED
            result.error = str(e)
        
        result.completed_at = datetime.now()
        return result
    
    def validate(
        self,
        action: RemediationAction,
        context: Dict[str, Any],
    ) -> Tuple[bool, str]:
        """Validate script action."""
        script = action.parameters.get("script", "")
        if not script:
            return False, "Script path is required"
        
        script_path = Path(script)
        if not script_path.exists():
            return False, f"Script not found: {script}"
        
        return True, "Valid"


class APICallHandler(ActionHandler):
    """Handler for API call remediation actions."""
    
    def execute(
        self,
        action: RemediationAction,
        context: Dict[str, Any],
    ) -> ActionResult:
        """Execute an API call action."""
        result = ActionResult(
            action_id=action.id,
            status=ActionStatus.RUNNING,
            started_at=datetime.now(),
        )
        
        try:
            import urllib.request
            import urllib.parse
            
            url = action.parameters.get("url", "")
            method = action.parameters.get("method", "POST")
            headers = action.parameters.get("headers", {})
            body = action.parameters.get("body", {})
            
            data = json.dumps(body).encode() if body else None
            
            req = urllib.request.Request(
                url,
                data=data,
                headers=headers,
                method=method,
            )
            
            with urllib.request.urlopen(req, timeout=action.timeout_seconds) as response:
                result.output = response.read().decode()
                result.status = ActionStatus.COMPLETED
            
        except Exception as e:
            result.status = ActionStatus.FAILED
            result.error = str(e)
        
        result.completed_at = datetime.now()
        return result
    
    def validate(
        self,
        action: RemediationAction,
        context: Dict[str, Any],
    ) -> Tuple[bool, str]:
        """Validate API call action."""
        url = action.parameters.get("url", "")
        if not url:
            return False, "URL is required"
        
        if not url.startswith(("http://", "https://")):
            return False, "URL must be HTTP or HTTPS"
        
        return True, "Valid"


class ExecutionSandbox:
    """Sandbox for safe action execution."""
    
    def __init__(
        self,
        sandbox_dir: Optional[Path] = None,
        max_execution_time: int = 60,
        max_memory_mb: int = 512,
    ):
        self.sandbox_dir = sandbox_dir or Path("/tmp/krl_remediation_sandbox")
        self.max_execution_time = max_execution_time
        self.max_memory_mb = max_memory_mb
        self._lock = threading.Lock()
        
        # Create sandbox directory
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)
    
    def execute(
        self,
        action: RemediationAction,
        handler: ActionHandler,
        context: Dict[str, Any],
    ) -> ActionResult:
        """Execute action in sandbox."""
        with self._lock:
            # Validate action
            is_valid, message = handler.validate(action, context)
            if not is_valid:
                return ActionResult(
                    action_id=action.id,
                    status=ActionStatus.FAILED,
                    started_at=datetime.now(),
                    completed_at=datetime.now(),
                    error=f"Validation failed: {message}",
                )
            
            # Execute with resource limits
            try:
                result = handler.execute(action, context)
                return result
            except Exception as e:
                return ActionResult(
                    action_id=action.id,
                    status=ActionStatus.FAILED,
                    started_at=datetime.now(),
                    completed_at=datetime.now(),
                    error=f"Sandbox execution error: {str(e)}",
                )
    
    def cleanup(self) -> None:
        """Clean up sandbox resources."""
        import shutil
        
        if self.sandbox_dir.exists():
            try:
                shutil.rmtree(self.sandbox_dir)
            except Exception as e:
                logger.error(f"Error cleaning sandbox: {e}")


@dataclass
class RemediationConfig:
    """Configuration for remediation engine."""
    
    enabled: bool = True
    auto_execute: bool = False
    max_auto_safety_level: SafetyLevel = SafetyLevel.SAFE
    require_approval_for: List[SafetyLevel] = field(
        default_factory=lambda: [SafetyLevel.RISKY, SafetyLevel.CRITICAL]
    )
    sandbox_enabled: bool = True
    max_execution_time: int = 60
    max_concurrent_actions: int = 5
    enable_rollback: bool = True
    rollback_retention_hours: int = 24
    log_all_actions: bool = True


class RemediationEngine:
    """
    Automated Remediation Engine.
    
    Executes remediation actions safely with rollback capabilities.
    """
    
    def __init__(self, config: Optional[RemediationConfig] = None):
        self.config = config or RemediationConfig()
        self.actions: Dict[str, RemediationAction] = {}
        self.playbooks: Dict[str, RemediationPlaybook] = {}
        self.results: Dict[str, ActionResult] = {}
        self.rollbacks: Dict[str, Rollback] = {}
        self.handlers: Dict[ActionType, ActionHandler] = {}
        self.sandbox = ExecutionSandbox() if self.config.sandbox_enabled else None
        self._subscribers: List[Callable[[ActionResult], None]] = []
        self._lock = threading.Lock()
        self._execution_semaphore = threading.Semaphore(self.config.max_concurrent_actions)
        
        # Register default handlers
        self._register_default_handlers()
    
    def _register_default_handlers(self) -> None:
        """Register default action handlers."""
        self.handlers[ActionType.SCRIPT] = ScriptHandler()
        self.handlers[ActionType.API_CALL] = APICallHandler()
    
    def register_handler(
        self,
        action_type: ActionType,
        handler: ActionHandler,
    ) -> None:
        """Register a custom action handler."""
        self.handlers[action_type] = handler
    
    def register_action(self, action: RemediationAction) -> None:
        """Register a remediation action."""
        self.actions[action.id] = action
        logger.info(f"Registered remediation action: {action.name}")
    
    def get_action(self, action_id: str) -> Optional[RemediationAction]:
        """Get a registered action."""
        return self.actions.get(action_id)
    
    def register_playbook(self, playbook: RemediationPlaybook) -> None:
        """Register a remediation playbook."""
        self.playbooks[playbook.id] = playbook
        logger.info(f"Registered playbook: {playbook.name}")
    
    def get_playbook(self, playbook_id: str) -> Optional[RemediationPlaybook]:
        """Get a registered playbook."""
        return self.playbooks.get(playbook_id)
    
    def execute_action(
        self,
        action: RemediationAction,
        context: Optional[Dict[str, Any]] = None,
        capture_state: bool = True,
    ) -> ActionResult:
        """Execute a single remediation action."""
        context = context or {}
        
        if not self.config.enabled:
            return ActionResult(
                action_id=action.id,
                status=ActionStatus.SKIPPED,
                started_at=datetime.now(),
                completed_at=datetime.now(),
                error="Remediation engine is disabled",
            )
        
        # Check if approval is required
        if action.safety_level in self.config.require_approval_for:
            if not context.get("approved", False):
                return ActionResult(
                    action_id=action.id,
                    status=ActionStatus.PENDING,
                    started_at=datetime.now(),
                    error="Action requires approval",
                )
        
        # Get handler
        handler = self.handlers.get(action.action_type)
        if not handler:
            return ActionResult(
                action_id=action.id,
                status=ActionStatus.FAILED,
                started_at=datetime.now(),
                completed_at=datetime.now(),
                error=f"No handler for action type: {action.action_type.value}",
            )
        
        # Capture state before if rollback enabled
        state_before = {}
        if capture_state and self.config.enable_rollback and action.reversible:
            state_before = self._capture_state(action, context)
        
        # Execute with semaphore
        with self._execution_semaphore:
            # Execute in sandbox if enabled
            if self.sandbox:
                result = self.sandbox.execute(action, handler, context)
            else:
                result = handler.execute(action, context)
        
        # Handle retries
        if result.status == ActionStatus.FAILED and action.retry_count > 0:
            for retry in range(action.retry_count):
                logger.info(f"Retrying action {action.name} ({retry + 1}/{action.retry_count})")
                threading.Event().wait(action.retry_delay_seconds)
                
                if self.sandbox:
                    result = self.sandbox.execute(action, handler, context)
                else:
                    result = handler.execute(action, context)
                
                if result.status == ActionStatus.COMPLETED:
                    break
        
        # Create rollback record if successful
        if result.status == ActionStatus.COMPLETED and action.reversible:
            state_after = self._capture_state(action, context) if capture_state else {}
            
            rollback = Rollback(
                action_id=action.id,
                original_action=action,
                state_before=state_before,
                state_after=state_after,
            )
            
            # Try to find or create rollback action
            if action.rollback_action:
                rollback.rollback_action = self.actions.get(action.rollback_action)
            else:
                rollback.rollback_action = self._create_rollback_action(action, state_before)
            
            result.rollback_available = rollback.rollback_action is not None
            result.rollback_data = {"rollback_id": rollback.id}
            
            self.rollbacks[rollback.id] = rollback
        
        # Store result
        self.results[result.action_id] = result
        
        # Notify subscribers
        for subscriber in self._subscribers:
            try:
                subscriber(result)
            except Exception as e:
                logger.error(f"Error notifying subscriber: {e}")
        
        return result
    
    def execute_playbook(
        self,
        playbook: RemediationPlaybook,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[ActionResult]:
        """Execute a remediation playbook."""
        context = context or {}
        context.update(playbook.variables)
        
        results = []
        
        for step in playbook.steps:
            # Evaluate condition if present
            if step.condition:
                if not self._evaluate_condition(step.condition, context):
                    results.append(ActionResult(
                        action_id=step.action.id,
                        status=ActionStatus.SKIPPED,
                        started_at=datetime.now(),
                        completed_at=datetime.now(),
                        output="Condition not met",
                    ))
                    continue
            
            # Execute step
            result = self.execute_action(step.action, context)
            results.append(result)
            
            # Handle failure
            if result.status == ActionStatus.FAILED:
                if step.on_failure == "abort":
                    logger.error(f"Playbook {playbook.name} aborted at step {step.name}")
                    break
                elif step.on_failure == "skip_to" and step.skip_to:
                    # Find and skip to specified step
                    skip_found = False
                    for next_step in playbook.steps:
                        if next_step.id == step.skip_to:
                            skip_found = True
                            break
                    if not skip_found:
                        break
                # "continue" just moves to next step
            
            # Wait if specified
            if step.wait_after_seconds > 0:
                threading.Event().wait(step.wait_after_seconds)
        
        return results
    
    def rollback_action(
        self,
        rollback_id: str,
        user: str,
        reason: str = "",
    ) -> Optional[ActionResult]:
        """Roll back a previously executed action."""
        rollback = self.rollbacks.get(rollback_id)
        if not rollback:
            logger.error(f"Rollback not found: {rollback_id}")
            return None
        
        if rollback.status == ActionStatus.ROLLED_BACK:
            logger.warning(f"Action already rolled back: {rollback_id}")
            return None
        
        if not rollback.rollback_action:
            logger.error(f"No rollback action available for: {rollback_id}")
            return None
        
        # Execute rollback
        result = self.execute_action(
            rollback.rollback_action,
            context={"rollback_reason": reason, "rollback_user": user},
            capture_state=False,  # Don't capture state for rollback
        )
        
        rollback.executed_at = datetime.now()
        rollback.executed_by = user
        rollback.status = ActionStatus.ROLLED_BACK if result.status == ActionStatus.COMPLETED else ActionStatus.FAILED
        rollback.result = result
        
        return result
    
    def get_pending_rollbacks(self, max_age_hours: int = 24) -> List[Rollback]:
        """Get rollbacks that can still be executed."""
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        
        return [
            rb for rb in self.rollbacks.values()
            if rb.status == ActionStatus.PENDING
            and rb.created_at > cutoff
            and rb.rollback_action is not None
        ]
    
    def create_action(
        self,
        name: str,
        action_type: ActionType,
        target: str,
        parameters: Dict[str, Any],
        **kwargs,
    ) -> RemediationAction:
        """Create and register a new action."""
        action = RemediationAction(
            name=name,
            action_type=action_type,
            target=target,
            parameters=parameters,
            **kwargs,
        )
        self.register_action(action)
        return action
    
    def create_playbook(
        self,
        name: str,
        description: str = "",
        **kwargs,
    ) -> RemediationPlaybook:
        """Create and register a new playbook."""
        playbook = RemediationPlaybook(
            name=name,
            description=description,
            **kwargs,
        )
        self.register_playbook(playbook)
        return playbook
    
    def subscribe(self, callback: Callable[[ActionResult], None]) -> None:
        """Subscribe to action result notifications."""
        self._subscribers.append(callback)
    
    def get_results(
        self,
        status: Optional[ActionStatus] = None,
        limit: int = 100,
    ) -> List[ActionResult]:
        """Get action results."""
        results = list(self.results.values())
        
        if status:
            results = [r for r in results if r.status == status]
        
        results.sort(key=lambda r: r.started_at, reverse=True)
        return results[:limit]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get remediation statistics."""
        total_actions = len(self.results)
        completed = sum(1 for r in self.results.values() if r.status == ActionStatus.COMPLETED)
        failed = sum(1 for r in self.results.values() if r.status == ActionStatus.FAILED)
        
        by_type: Dict[str, int] = {}
        for action in self.actions.values():
            action_type = action.action_type.value
            by_type[action_type] = by_type.get(action_type, 0) + 1
        
        return {
            "total_executions": total_actions,
            "completed": completed,
            "failed": failed,
            "success_rate": completed / total_actions if total_actions > 0 else 0,
            "registered_actions": len(self.actions),
            "registered_playbooks": len(self.playbooks),
            "pending_rollbacks": len(self.get_pending_rollbacks()),
            "actions_by_type": by_type,
        }
    
    def _capture_state(
        self,
        action: RemediationAction,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Capture current state before action execution."""
        return {
            "action_id": action.id,
            "target": action.target,
            "timestamp": datetime.now().isoformat(),
            "context": dict(context),
        }
    
    def _create_rollback_action(
        self,
        original_action: RemediationAction,
        state_before: Dict[str, Any],
    ) -> Optional[RemediationAction]:
        """Create a rollback action for the original action."""
        # This is a simple implementation - could be extended
        # to create specific rollback actions based on action type
        
        if original_action.action_type == ActionType.CONFIG_CHANGE:
            return RemediationAction(
                name=f"Rollback: {original_action.name}",
                action_type=ActionType.CONFIG_CHANGE,
                target=original_action.target,
                parameters={
                    "restore_state": state_before,
                },
                safety_level=original_action.safety_level,
            )
        
        return None
    
    def _evaluate_condition(
        self,
        condition: str,
        context: Dict[str, Any],
    ) -> bool:
        """Evaluate a condition expression."""
        try:
            # Simple variable replacement and evaluation
            for key, value in context.items():
                condition = condition.replace(f"${key}", str(value))
            
            # Basic boolean evaluation
            return bool(eval(condition, {"__builtins__": {}}, {}))
        except Exception:
            return True
    
    def cleanup(self) -> None:
        """Clean up resources."""
        if self.sandbox:
            self.sandbox.cleanup()
        
        # Clean up old rollbacks
        cutoff = datetime.now() - timedelta(hours=self.config.rollback_retention_hours)
        old_rollbacks = [
            rid for rid, rb in self.rollbacks.items()
            if rb.created_at < cutoff
        ]
        
        for rid in old_rollbacks:
            del self.rollbacks[rid]


# Import Tuple for type hints
from typing import Tuple
