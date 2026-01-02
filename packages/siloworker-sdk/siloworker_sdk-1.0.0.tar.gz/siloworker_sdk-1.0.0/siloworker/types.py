"""Type definitions for SiloWorker SDK."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union
from dataclasses import dataclass


@dataclass
class WorkflowNode:
    """Represents a workflow node."""
    id: str
    type: str
    config: Dict[str, Any]
    position: Optional[Dict[str, float]] = None


@dataclass
class WorkflowConnection:
    """Represents a connection between workflow nodes."""
    from_node: str  # 'from' is a Python keyword
    to: str
    condition: Optional[str] = None


@dataclass
class Trigger:
    """Represents a workflow trigger."""
    type: Literal["manual", "webhook", "schedule", "email", "sms"]
    config: Optional[Dict[str, Any]] = None
    schedule: Optional[str] = None  # cron expression
    input: Optional[Dict[str, Any]] = None


@dataclass
class RetryPolicy:
    """Represents a retry policy."""
    max_attempts: Optional[int] = None
    backoff_strategy: Optional[Literal["fixed", "exponential"]] = None
    initial_delay_ms: Optional[int] = None
    max_delay_ms: Optional[int] = None


@dataclass
class StepResult:
    """Represents the result of a workflow step."""
    node_id: str
    type: str
    config: Dict[str, Any]
    status: Literal["success", "failed", "skipped"]
    duration_ms: int
    timestamp: str
    output: Optional[Any] = None
    error: Optional[str] = None
    using_platform_credentials: Optional[bool] = None
    resumed: Optional[bool] = None


@dataclass
class RunResults:
    """Represents the results of a workflow run."""
    steps: List[StepResult]
    duration_ms: Optional[int] = None
    total_cost: Optional[float] = None


@dataclass
class Agent:
    """Represents a workflow agent."""
    agent_id: str
    project_id: str
    name: str
    nodes: List[WorkflowNode]
    connections: List[WorkflowConnection]
    webhook_secret: str
    created_at: str
    description: Optional[str] = None
    trigger: Optional[Trigger] = None
    retry_policy: Optional[RetryPolicy] = None
    timeout_seconds: Optional[int] = None
    updated_at: Optional[str] = None


@dataclass
class Run:
    """Represents a workflow run."""
    run_id: str
    agent_id: str
    project_id: str
    workspace_id: str
    input: Dict[str, Any]
    status: Literal["queued", "running", "completed", "failed", "cancelled"]
    trigger_type: str
    created_at: str
    webhook: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    results: Optional[RunResults] = None


@dataclass
class Project:
    """Represents a project."""
    project_id: str
    workspace_id: str
    name: str
    created_at: str
    description: Optional[str] = None


@dataclass
class Schedule:
    """Represents a schedule."""
    schedule_id: str
    agent_id: str
    project_id: str
    input: Dict[str, Any]
    enabled: bool
    created_at: str
    cron: Optional[str] = None
    interval_seconds: Optional[int] = None
    next_run: Optional[str] = None


@dataclass
class Workspace:
    """Represents a workspace."""
    workspace_id: str
    name: str
    owner_email: str
    api_key: str
    plan: Literal["free", "pro", "enterprise"]
    runs_this_month: int
    created_at: str
    api_keys: Optional[Dict[str, Any]] = None


@dataclass
class Template:
    """Represents a workflow template."""
    id: str
    name: str
    nodes: List[WorkflowNode]
    connections: List[WorkflowConnection]
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None


@dataclass
class Tool:
    """Represents an available tool."""
    type: str
    name: str
    description: str
    config_schema: Optional[Dict[str, Any]] = None


@dataclass
class WebhookEvent:
    """Represents a webhook event."""
    type: Literal["run.started", "run.completed", "run.failed", "step.completed", "step.failed"]
    data: Dict[str, Any]
    webhook_id: str
    signature: str


# Configuration types
SiloWorkerConfig = Dict[str, Union[str, int, bool]]
