"""Main Highway Driver class with @task decorator.

This is the primary interface for the Highway Driver SDK.
Users import Driver and use @driver.task() to define workflows.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from datetime import timedelta
from typing import TYPE_CHECKING, Any, TypeVar

from highway.ast_utils import FunctionAnalyzer

if TYPE_CHECKING:
    from highway.runner import HighwayRunner

from highway.exceptions import (
    ConfigurationError,
    NotSupportedError,
    TaskDefinitionError,
)
from highway.result import WorkflowResult
from highway.task import TaskDefinition, TaskType

F = TypeVar("F", bound=Callable[..., Any])


class Driver:
    """Highway Driver - Simple decorator SDK for Highway Workflow Engine.

    The Driver class provides a DBOS-style decorator interface for defining
    and executing workflows on Highway. It handles:

    - Task registration via @driver.task() decorator
    - Workflow DSL generation
    - Execution via Highway API
    - Status polling and result retrieval

    All execution goes through: Driver -> Highway API (httpx)

    Example:
        from highway import Driver

        driver = Driver()  # Uses HIGHWAY_API_KEY env var

        @driver.task(shell=True)
        def backup_db():
            return "pg_dump mydb > backup.sql"

        @driver.task(py=True, depends=["backup_db"])
        def verify_backup():
            import os
            return os.path.exists("backup.sql")

        result = driver.run()
        print(result.status)  # "completed"

    Attributes:
        api_key: Highway API key for authentication
        endpoint: Highway API endpoint URL
        tasks: Registered task definitions
    """

    def __init__(
        self,
        api_key: str | None = None,
        endpoint: str = "https://highway.solutions",
    ) -> None:
        """Initialize Highway Driver.

        Args:
            api_key: Highway API key. If not provided, reads from
                     HIGHWAY_API_KEY environment variable.
            endpoint: Highway API endpoint URL.
                      Defaults to https://highway.solutions

        Note:
            API key is required. All execution goes through
            Stabilize -> Highway API.
        """
        self.api_key = api_key or os.environ.get("HIGHWAY_API_KEY", "")
        self.endpoint = endpoint
        self._tasks: dict[str, TaskDefinition] = {}
        self._analyzer = FunctionAnalyzer()

    @property
    def tasks(self) -> dict[str, TaskDefinition]:
        """Get all registered tasks."""
        return self._tasks.copy()

    def task(
        self,
        shell: bool = False,
        py: bool = False,
        http: bool = False,
        tool: str | None = None,
        workflow: str | None = None,
        workflow_id: str | None = None,
        depends: list[str] | None = None,
        timeout: int = 300,
        schedule: str | timedelta | None = None,
        run_at: str | None = None,
        retries: int = 0,
        retry_delay: float = 1.0,
        backoff: float = 2.0,
        delay: timedelta | None = None,
    ) -> Callable[[F], F]:
        """Decorator to register a task with the Driver.

        Tasks are executed on Highway Workflow Engine. The function body
        defines what the task does:

        - shell=True: Function returns a shell command string
        - py=True: Function is executed as Python code via tools.code.exec
        - http=True: Function returns HTTP request configuration
        - tool="tools.X.Y": Function returns kwargs for any Highway tool
        - workflow="name": Execute another workflow by name (latest version)
        - workflow_id="uuid": Execute specific workflow version by definition_id

        Args:
            shell: Execute as shell command (function returns command string)
            py: Execute as Python code on Highway via tools.code.exec
            http: Execute as HTTP request (function returns config dict)
            tool: Highway tool name (e.g., "tools.llm.call", "tools.database.query")
            workflow: Execute workflow by name (uses latest version)
            workflow_id: Execute specific workflow version by definition_id (UUID)
            depends: List of task names this depends on
            timeout: Execution timeout in seconds
            schedule: Recurring schedule - cron expression string (e.g., "0 * * * *")
                      or timedelta for interval-based scheduling
            run_at: Specific execution time (NotImplemented)
            retries: Number of retry attempts on failure
            retry_delay: Initial delay between retries in seconds
            backoff: Multiplier for exponential backoff (default 2.0)
            delay: Durable delay before task execution. Uses Highway's native
                   WaitOperator which suspends the workflow consuming ZERO
                   worker resources during the wait period.

        Returns:
            Decorated function (unchanged)

        Raises:
            TaskDefinitionError: If task definition is invalid
            NotSupportedError: If unsupported parameter is used

        Example:
            @driver.task(shell=True)
            def list_files():
                return "ls -la /tmp"

            @driver.task(py=True, depends=["list_files"])
            def process_output(list_files):
                return {"processed": True}

            @driver.task(http=True, retries=3, retry_delay=2.0, backoff=2.0)
            def call_webhook():
                return {
                    "url": "https://api.example.com/webhook",
                    "method": "POST",
                    "json": {"status": "done"}
                }

            @driver.task(tool="tools.llm.call")
            def summarize():
                return {
                    "prompt": "Summarize: {{list_files_result.stdout}}",
                    "model": "claude-3-haiku-20240307"
                }

            @driver.task(workflow="send_report")
            def trigger_report():
                return {"inputs": {"date": "2024-01-01"}}
        """
        # Validate task type - exactly one must be specified
        type_flags = [
            shell,
            py,
            http,
            tool is not None,
            workflow is not None,
            workflow_id is not None,
        ]
        if sum(type_flags) == 0:
            raise TaskDefinitionError(
                "Must specify exactly one task type: shell=True, py=True, http=True, "
                "tool='...', workflow='...', or workflow_id='...'"
            )
        if sum(type_flags) > 1:
            specified = []
            if shell:
                specified.append("shell")
            if py:
                specified.append("py")
            if http:
                specified.append("http")
            if tool:
                specified.append("tool='%s'" % tool)
            if workflow:
                specified.append("workflow='%s'" % workflow)
            if workflow_id:
                specified.append("workflow_id='%s'" % workflow_id)
            raise TaskDefinitionError(
                "Only one task type allowed. Got: %s" % ", ".join(specified)
            )

        # Check for unsupported features
        if run_at is not None:
            raise NotSupportedError("run_at parameter", "issuedb DRIVER-015")

        # Validate delay + schedule combination
        if delay is not None and schedule is not None:
            raise TaskDefinitionError(
                "Cannot use both delay and schedule together. "
                "delay is for one-time delayed execution, "
                "schedule is for recurring execution."
            )

        # Convert timedelta schedule to cron-like interval string
        schedule_str: str | None = None
        if schedule is not None:
            if isinstance(schedule, timedelta):
                # Convert timedelta to seconds for interval scheduling
                total_seconds = int(schedule.total_seconds())
                schedule_str = "@every %ds" % total_seconds
            else:
                schedule_str = schedule

        # Determine task type
        if shell:
            task_type = TaskType.SHELL
        elif py:
            task_type = TaskType.PYTHON
        elif http:
            task_type = TaskType.HTTP
        elif tool:
            task_type = TaskType.TOOL
        else:
            # workflow or workflow_id
            task_type = TaskType.WORKFLOW

        def decorator(func: F) -> F:
            # Check for duplicate registration
            if func.__name__ in self._tasks:
                raise TaskDefinitionError("Task '%s' is already registered" % func.__name__)

            # Analyze function with AST
            analysis = self._analyzer.analyze(func)

            # Create task definition
            task_def = TaskDefinition(
                name=func.__name__,
                func=func,
                task_type=task_type,
                depends=depends or [],
                timeout=timeout,
                schedule=schedule_str,
                retries=retries,
                retry_delay=retry_delay,
                backoff_rate=backoff,
                delay=delay,
                tool_name=tool,
                workflow_name=workflow,
                workflow_definition_id=workflow_id,
                analysis=analysis,
            )

            self._tasks[func.__name__] = task_def
            return func

        return decorator

    def run(
        self,
        wait: bool = True,
        timeout: float = 300,
        workflow_id: str | None = None,
        inputs: dict[str, Any] | None = None,
    ) -> WorkflowResult:
        """Execute all registered tasks as a workflow.

        All execution goes through Stabilize -> Highway API.

        Args:
            wait: If True, wait for completion. If False, return immediately
                  with run_id for async polling.
            timeout: Maximum time to wait for completion in seconds
            workflow_id: Custom workflow ID for idempotency. If the same
                        workflow_id is used for multiple runs, Highway will
                        return the existing workflow instead of creating a new one.
                        If not provided, a unique ID is generated.
            inputs: Workflow input variables. These are available in tasks via
                   {{inputs.key}} syntax. Example: inputs={"email": "user@example.com"}

        Returns:
            WorkflowResult with execution status and task results

        Raises:
            ConfigurationError: If API key is missing
            TaskDefinitionError: If no tasks registered or invalid dependencies

        Example:
            # Idempotent execution - same workflow_id returns same result
            result1 = driver.run(workflow_id="order-12345")
            result2 = driver.run(workflow_id="order-12345")  # Returns cached result
        """
        if not self._tasks:
            raise TaskDefinitionError("No tasks registered. Use @driver.task()")

        # Validate all dependencies exist
        task_names = set(self._tasks.keys())
        for task in self._tasks.values():
            errors = task.validate_depends(task_names)
            if errors:
                raise TaskDefinitionError("; ".join(errors))

        return self._run_via_stabilize(wait=wait, timeout=timeout, workflow_id=workflow_id, inputs=inputs)

    def _run_via_stabilize(
        self,
        wait: bool = True,
        timeout: float = 300,
        workflow_id: str | None = None,
        inputs: dict[str, Any] | None = None,
    ) -> WorkflowResult:
        """Execute tasks on Highway API via Stabilize orchestration.

        Args:
            wait: If True, wait for completion
            timeout: Maximum wait time in seconds
            workflow_id: Optional workflow ID for idempotency
            inputs: Workflow input variables

        Returns:
            WorkflowResult with execution status
        """
        if not self.api_key:
            raise ConfigurationError(
                "HIGHWAY_API_KEY not configured. "
                "Set environment variable or pass api_key to Driver()"
            )

        inputs = inputs or {}

        # Build workflow JSON with workflow-level timeout and inputs
        workflow_json = self._build_workflow(workflow_timeout=int(timeout), inputs=inputs)

        # Use Stabilize runner for execution
        runner = self._get_runner()

        if wait:
            return runner.run(workflow_json, inputs={}, timeout=timeout, workflow_id=workflow_id)
        else:
            return runner.submit(workflow_json, inputs={}, workflow_id=workflow_id)

    def _get_runner(self) -> HighwayRunner:
        """Get or create the Highway runner instance.

        Returns:
            HighwayRunner for Highway API communication
        """
        from highway.runner import HighwayRunner

        return HighwayRunner(
            api_key=self.api_key,
            endpoint=self.endpoint,
        )

    def _timedelta_to_iso8601(self, td: timedelta) -> str:
        """Convert timedelta to ISO 8601 duration format.

        Highway's WaitOperator expects durations in ISO 8601 format.

        Args:
            td: timedelta to convert

        Returns:
            ISO 8601 duration string (e.g., "PT3S", "PT7200S")

        Examples:
            timedelta(seconds=3) -> "PT3S"
            timedelta(hours=2) -> "PT7200S"
            timedelta(days=1) -> "PT86400S"
        """
        total_seconds = int(td.total_seconds())
        return "PT%dS" % total_seconds

    def _build_workflow(
        self,
        workflow_timeout: int = 300,
        inputs: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build Highway DSL workflow JSON from registered tasks.

        Args:
            workflow_timeout: Workflow-level timeout in seconds
            inputs: Workflow input variables

        Returns:
            Workflow definition dict for Highway API
        """
        # Import here to avoid circular dependency with highway_dsl
        # For now, build manually until highway_dsl is available
        import uuid

        workflow_name = "driver_workflow_%s" % uuid.uuid4().hex[:8]

        tasks_json: dict[str, Any] = {}

        for name, task in self._tasks.items():
            # If task has delay, insert a wait task first
            if task.delay is not None:
                wait_task_id = "%s_wait" % name
                wait_duration = self._timedelta_to_iso8601(task.delay)

                tasks_json[wait_task_id] = {
                    "task_id": wait_task_id,
                    "operator_type": "wait",
                    "dependencies": task.depends,  # Wait inherits original deps
                    "trigger_rule": "all_success",
                    "wait_for": wait_duration,
                }

                # Actual task depends on wait task instead of original deps
                actual_deps = [wait_task_id]
            else:
                actual_deps = task.depends

            task_json: dict[str, Any] = {
                "task_id": name,
                "operator_type": "task",
                "dependencies": actual_deps,
                "trigger_rule": "all_success",
                "result_key": task.get_result_key(),
            }

            # Add timeout for the task
            if task.timeout > 0:
                task_json["timeout_seconds"] = task.timeout

            # Add retry configuration if specified
            if task.retries > 0:
                task_json["retry_policy"] = {
                    "max_attempts": task.retries + 1,  # +1 for initial attempt
                    "initial_interval_seconds": task.retry_delay,
                    "backoff_coefficient": task.backoff_rate,
                }

            if task.task_type == TaskType.SHELL:
                # Get command from function
                command = task.func()
                task_json["function"] = "tools.shell.run"
                task_json["args"] = [command]
                task_json["kwargs"] = {}

            elif task.task_type == TaskType.HTTP:
                # Get config from function
                config = task.func()
                task_json["function"] = "tools.http.request"
                task_json["kwargs"] = config

            elif task.task_type == TaskType.PYTHON:
                # Get function source code for remote execution
                import ast
                import inspect
                import textwrap

                source = inspect.getsource(task.func)
                source = textwrap.dedent(source)

                # Use AST to strip top-level decorators properly
                tree = ast.parse(source)
                func_def = tree.body[0]
                if isinstance(func_def, ast.FunctionDef):
                    func_def.decorator_list = []  # Remove decorators
                source = ast.unparse(tree)

                # Generate wrapper that executes function and returns result as JSON
                # Highway's tools.code.exec runs this in a sandboxed environment
                wrapper = """
import json

%s

_result = %s()
# Output result in Highway-recognized format
print("__HIGHWAY_RESULT__:" + json.dumps(_result))
""" % (source, task.func.__name__)

                task_json["function"] = "tools.code.exec"
                task_json["kwargs"] = {
                    "code": wrapper,
                    "timeout": task.timeout,
                }

            elif task.task_type == TaskType.TOOL:
                # Generic Highway tool - function returns kwargs
                config = task.func()
                task_json["function"] = task.tool_name
                task_json["kwargs"] = config if isinstance(config, dict) else {}

            elif task.task_type == TaskType.WORKFLOW:
                # Execute another workflow via tools.workflow.execute
                config = task.func()
                workflow_kwargs: dict[str, Any] = {}

                # Set workflow identifier (name or definition_id)
                if task.workflow_definition_id:
                    workflow_kwargs["definition_id"] = task.workflow_definition_id
                elif task.workflow_name:
                    workflow_kwargs["workflow_name"] = task.workflow_name

                # Include inputs from function return value
                if isinstance(config, dict) and "inputs" in config:
                    workflow_kwargs["inputs"] = config["inputs"]

                task_json["function"] = "tools.workflow.execute"
                task_json["kwargs"] = workflow_kwargs

            tasks_json[name] = task_json

        # Find start_task from generated tasks (tasks with no dependencies)
        start_task: str | None = None
        no_deps = [
            task_id for task_id, task_def in tasks_json.items() if not task_def.get("dependencies")
        ]
        if no_deps:
            start_task = sorted(no_deps)[0]

        # Check for workflow-level schedule (from first scheduled task)
        scheduled_tasks = [t for t in self._tasks.values() if t.schedule]
        workflow_schedule: str | None = None
        if scheduled_tasks:
            # Use schedule from first scheduled task for workflow
            workflow_schedule = scheduled_tasks[0].schedule

        workflow_def: dict[str, Any] = {
            "name": workflow_name,
            "version": "1.0.0",
            "description": "Workflow generated by Highway Driver SDK",
            "start_task": start_task,
            "tasks": tasks_json,
            "variables": inputs or {},
            "max_active_runs": 1,
            "timeout_seconds": workflow_timeout,
        }

        # Add schedule if any tasks are scheduled
        if workflow_schedule:
            workflow_def["schedule"] = workflow_schedule

        return workflow_def

    def status(self, run_id: str) -> WorkflowResult:
        """Get current status of a workflow.

        Args:
            run_id: Highway workflow run ID

        Returns:
            WorkflowResult with current state
        """
        if not self.api_key:
            raise ConfigurationError("API key required for status()")

        runner = self._get_runner()
        return runner.status(run_id)

    def cancel(self, run_id: str) -> bool:
        """Cancel a running workflow via Stabilize.

        Args:
            run_id: Stabilize workflow run ID

        Returns:
            True if cancellation was successful
        """
        if not self.api_key:
            raise ConfigurationError("API key required for cancel()")

        runner = self._get_runner()
        return runner.cancel(run_id)

    def clear(self) -> None:
        """Clear all registered tasks.

        Useful for testing or reusing a Driver instance.
        """
        self._tasks.clear()
