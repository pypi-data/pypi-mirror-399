"""Task definition dataclass for Highway Driver.

A TaskDefinition captures all metadata about a decorated function
that will be converted to a Highway workflow task.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import timedelta
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from highway.ast_utils import FunctionAnalysis


class TaskType(Enum):
    """Type of task execution."""

    SHELL = "shell"
    PYTHON = "python"
    HTTP = "http"
    TOOL = "tool"  # Generic Highway tool (e.g., tools.llm.call)
    WORKFLOW = "workflow"  # Execute another workflow


@dataclass
class TaskDefinition:
    """Definition of a task registered with the Driver.

    Attributes:
        name: Function name (auto-extracted)
        func: The decorated function
        task_type: Type of task (shell, python, http, tool, workflow)
        depends: List of task names this depends on
        timeout: Execution timeout in seconds
        schedule: Cron expression or interval string (e.g., "0 * * * *" or "@every 60s")
        run_at: Specific execution time (NotImplemented)
        retries: Number of retry attempts on failure
        retry_delay: Initial delay between retries in seconds
        backoff_rate: Multiplier for exponential backoff (e.g., 2.0)
        delay: Durable delay before task execution (uses Highway's WaitOperator)
        tool_name: Highway tool name for TOOL type (e.g., "tools.llm.call")
        workflow_name: Workflow name for WORKFLOW type (uses latest version)
        workflow_definition_id: Specific workflow definition ID for WORKFLOW type
        analysis: AST analysis of the function (populated by Driver)
    """

    name: str
    func: Callable[..., Any]
    task_type: TaskType
    depends: list[str] = field(default_factory=list)
    timeout: int = 300
    schedule: str | None = None
    run_at: str | None = None
    retries: int = 0
    retry_delay: float = 1.0
    backoff_rate: float = 2.0
    delay: timedelta | None = None
    tool_name: str | None = None
    workflow_name: str | None = None
    workflow_definition_id: str | None = None
    analysis: FunctionAnalysis | None = None

    def __post_init__(self) -> None:
        """Validate task definition after creation."""
        if self.timeout <= 0:
            raise ValueError("timeout must be positive, got %d" % self.timeout)
        if self.retries < 0:
            raise ValueError("retries must be non-negative, got %d" % self.retries)
        if self.retry_delay < 0:
            raise ValueError("retry_delay must be non-negative, got %s" % self.retry_delay)
        if self.backoff_rate < 1.0:
            raise ValueError("backoff_rate must be >= 1.0, got %s" % self.backoff_rate)
        if self.delay is not None and self.delay.total_seconds() <= 0:
            raise ValueError("delay must be positive, got %s" % self.delay)

    def get_result_key(self) -> str:
        """Get the result key for this task in Highway workflow."""
        return "%s_result" % self.name

    def validate_depends(self, available_tasks: set[str]) -> list[str]:
        """Validate that all dependencies exist.

        Args:
            available_tasks: Set of registered task names

        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        for dep in self.depends:
            if dep not in available_tasks:
                errors.append(
                    "Task '%s' depends on '%s' which is not registered" % (self.name, dep)
                )
        return errors
