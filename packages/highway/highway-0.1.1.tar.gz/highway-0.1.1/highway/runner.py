"""HTTP-based workflow runner for Highway Driver.

This module provides the HighwayRunner class that executes Highway
workflows via direct HTTP API calls.

Architecture:
    Highway Driver -> HighwayRunner -> Highway API (httpx)
"""

from __future__ import annotations

import logging
import os
import time
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

import httpx

if TYPE_CHECKING:
    from highway.result import WorkflowResult

logger = logging.getLogger(__name__)

# Default polling configuration
DEFAULT_POLL_INTERVAL = 2.0  # seconds
DEFAULT_INITIAL_DELAY = 0.5  # seconds before first poll


class HighwayRunner:
    """Execute workflows via Highway API.

    This class provides a simple HTTP-based interface for submitting
    workflows to Highway and polling for results.

    Example:
        runner = HighwayRunner(
            api_key="hw_k1_...",
            endpoint="https://highway.solutions",
        )
        result = runner.run(workflow_json, inputs={}, timeout=300)
    """

    def __init__(
        self,
        api_key: str | None = None,
        endpoint: str | None = None,
        poll_interval: float = DEFAULT_POLL_INTERVAL,
    ) -> None:
        """Initialize Highway runner.

        Args:
            api_key: Highway API key (falls back to HIGHWAY_API_KEY env var)
            endpoint: Highway API endpoint (falls back to HIGHWAY_API_ENDPOINT)
            poll_interval: Seconds between status polls (default: 2.0)
        """
        self.api_key = api_key or os.environ.get("HIGHWAY_API_KEY", "")
        self.endpoint = (
            endpoint
            or os.environ.get("HIGHWAY_API_ENDPOINT", "https://highway.solutions")
        ).rstrip("/")
        self.poll_interval = poll_interval

        # Create HTTP client with auth header
        self._client = httpx.Client(
            base_url=self.endpoint,
            headers={
                "Authorization": "Bearer %s" % self.api_key,
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self) -> HighwayRunner:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def run(
        self,
        workflow_json: dict[str, Any],
        inputs: dict[str, Any] | None = None,
        timeout: float = 300,
        workflow_id: str | None = None,
    ) -> WorkflowResult:
        """Execute workflow and wait for completion.

        Args:
            workflow_json: Highway workflow definition JSON
            inputs: Optional workflow inputs (merged into workflow variables)
            timeout: Maximum execution time in seconds
            workflow_id: Optional workflow ID for idempotency

        Returns:
            WorkflowResult with execution results
        """
        # Submit workflow
        result = self.submit(workflow_json, inputs, workflow_id)

        if not result.run_id:
            return result

        # Poll until completion or timeout
        return self._wait_for_completion(result.run_id, timeout)

    def submit(
        self,
        workflow_json: dict[str, Any],
        inputs: dict[str, Any] | None = None,
        workflow_id: str | None = None,
    ) -> WorkflowResult:
        """Submit workflow without waiting for completion.

        Args:
            workflow_json: Highway workflow definition JSON
            inputs: Optional workflow inputs
            workflow_id: Optional workflow ID for tracking

        Returns:
            WorkflowResult with run_id (status will be 'submitted')
        """
        from highway.result import WorkflowResult, WorkflowState

        # Merge inputs into workflow variables
        if inputs:
            workflow_json = workflow_json.copy()
            variables = workflow_json.get("variables", {})
            variables.update(inputs)
            workflow_json["variables"] = variables

        try:
            response = self._client.post(
                "/api/v1/workflows",
                json={"workflow_definition": workflow_json},
            )
            response.raise_for_status()
            data = response.json()

            response_data = data.get("data", {})
            # Use workflow_run_id for status queries, fall back to run_id
            run_id = (
                response_data.get("workflow_run_id")
                or response_data.get("run_id")
                or data.get("run_id")
            )

            if not run_id:
                logger.error("No run_id in response: %s", data)
                return WorkflowResult(
                    run_id="",
                    workflow_id=workflow_id,
                    status="failed",
                    state=WorkflowState.FAILED,
                    error="No run_id in API response",
                    started_at=datetime.now(UTC),
                )

            logger.info("Workflow submitted: run_id=%s", run_id)

            return WorkflowResult(
                run_id=run_id,
                workflow_id=workflow_id,
                status="submitted",
                state=WorkflowState.SUBMITTED,
                started_at=datetime.now(UTC),
            )

        except httpx.HTTPStatusError as e:
            error_msg = "HTTP %s: %s" % (e.response.status_code, e.response.text[:500])
            logger.error("Failed to submit workflow: %s", error_msg)
            return WorkflowResult(
                run_id="",
                workflow_id=workflow_id,
                status="failed",
                state=WorkflowState.FAILED,
                error=error_msg,
                started_at=datetime.now(UTC),
            )
        except Exception as e:
            logger.error("Failed to submit workflow: %s", e)
            return WorkflowResult(
                run_id="",
                workflow_id=workflow_id,
                status="failed",
                state=WorkflowState.FAILED,
                error=str(e),
                started_at=datetime.now(UTC),
            )

    def status(self, run_id: str) -> WorkflowResult:
        """Get workflow execution status.

        Args:
            run_id: Highway workflow run ID

        Returns:
            WorkflowResult with current state
        """
        from highway.result import TaskResult, WorkflowResult, WorkflowState

        try:
            response = self._client.get("/api/v1/workflows/%s" % run_id)
            response.raise_for_status()
            data = response.json().get("data", {})

            return self._parse_run_response(data, run_id)

        except httpx.HTTPStatusError as e:
            return WorkflowResult(
                run_id=run_id,
                status="error",
                state=WorkflowState.FAILED,
                error="HTTP %s: %s" % (e.response.status_code, e.response.text[:200]),
            )
        except Exception as e:
            return WorkflowResult(
                run_id=run_id,
                status="error",
                state=WorkflowState.FAILED,
                error=str(e),
            )

    def cancel(self, run_id: str) -> bool:
        """Cancel workflow execution.

        Args:
            run_id: Highway workflow run ID

        Returns:
            True if cancellation was requested
        """
        try:
            response = self._client.post("/api/v1/workflows/%s/cancel" % run_id)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error("Failed to cancel workflow %s: %s", run_id, e)
            return False

    def _wait_for_completion(
        self,
        run_id: str,
        timeout: float,
    ) -> WorkflowResult:
        """Poll for workflow completion.

        Args:
            run_id: Highway workflow run ID
            timeout: Maximum wait time in seconds

        Returns:
            WorkflowResult with final state
        """
        from highway.result import WorkflowState

        start_time = time.time()
        time.sleep(DEFAULT_INITIAL_DELAY)

        while True:
            elapsed = time.time() - start_time
            if elapsed >= timeout:
                logger.warning("Workflow %s timed out after %.1fs", run_id, elapsed)
                return self.status(run_id)

            result = self.status(run_id)

            # Check if terminal state
            if result.state in (
                WorkflowState.COMPLETED,
                WorkflowState.FAILED,
                WorkflowState.CANCELLED,
                WorkflowState.TIMED_OUT,
            ):
                logger.info(
                    "Workflow %s finished: status=%s, elapsed=%.1fs",
                    run_id,
                    result.status,
                    elapsed,
                )
                return result

            logger.debug(
                "Workflow %s in progress: status=%s, elapsed=%.1fs",
                run_id,
                result.status,
                elapsed,
            )
            time.sleep(self.poll_interval)

    def _parse_run_response(
        self,
        data: dict[str, Any],
        run_id: str,
    ) -> WorkflowResult:
        """Parse Highway API run response into WorkflowResult.

        Args:
            data: API response data
            run_id: Workflow run ID

        Returns:
            WorkflowResult
        """
        import json as json_module

        from highway.result import TaskResult, WorkflowResult, WorkflowState

        status = data.get("status", "unknown")
        state = self._map_status_to_state(status)

        # Parse timestamps
        started_at = None
        completed_at = None
        if data.get("started_at"):
            try:
                started_at = datetime.fromisoformat(
                    data["started_at"].replace("Z", "+00:00")
                )
            except (ValueError, TypeError):
                pass
        if data.get("completed_at"):
            try:
                completed_at = datetime.fromisoformat(
                    data["completed_at"].replace("Z", "+00:00")
                )
            except (ValueError, TypeError):
                pass

        # Parse task results from workflow_definition and result
        tasks: dict[str, TaskResult] = {}
        workflow_def = data.get("workflow_definition", {})
        result_data = data.get("result", {})

        # Get task names from workflow definition
        task_defs = workflow_def.get("tasks", {})

        for task_name in task_defs:
            task_state = state
            task_error = None
            task_result: dict[str, Any] = {}

            # Check if there's output in result
            if result_data:
                output = result_data.get("output", {})
                if isinstance(output, dict):
                    task_result = output.copy()

                    # Parse __HIGHWAY_RESULT__ from stdout if present
                    stdout = output.get("stdout", "")
                    if "__HIGHWAY_RESULT__:" in stdout:
                        try:
                            json_str = stdout.split("__HIGHWAY_RESULT__:")[1].strip()
                            # Handle newlines in output
                            json_str = json_str.split("\n")[0]
                            parsed = json_module.loads(json_str)
                            task_result["parsed_result"] = parsed
                        except (json_module.JSONDecodeError, IndexError):
                            pass

                    # Check for errors
                    if output.get("exit_code", 0) != 0:
                        task_state = WorkflowState.FAILED
                        task_error = output.get("stderr") or output.get("error")
                    elif status == "completed":
                        task_state = WorkflowState.COMPLETED

            tasks[task_name] = TaskResult(
                name=task_name,
                state=task_state,
                result=task_result,
                error=task_error,
            )

        # Get error if failed
        error = None
        if status == "failed":
            error = data.get("error") or data.get("failure_reason")

        return WorkflowResult(
            run_id=run_id,
            workflow_id=data.get("workflow_id"),
            status=status,
            state=state,
            tasks=tasks,
            started_at=started_at,
            completed_at=completed_at,
            error=error,
        )

    def _map_status_to_state(self, status: str) -> WorkflowState:
        """Map Highway status string to WorkflowState enum.

        Args:
            status: Highway workflow status string

        Returns:
            WorkflowState enum value
        """
        from highway.result import WorkflowState

        status_map = {
            "pending": WorkflowState.PENDING,
            "submitted": WorkflowState.SUBMITTED,
            "running": WorkflowState.RUNNING,
            "sleeping": WorkflowState.SLEEPING,
            "waiting": WorkflowState.WAITING,
            "completed": WorkflowState.COMPLETED,
            "failed": WorkflowState.FAILED,
            "cancelled": WorkflowState.CANCELLED,
            "canceled": WorkflowState.CANCELLED,
            "timed_out": WorkflowState.TIMED_OUT,
        }

        return status_map.get(status.lower(), WorkflowState.PENDING)


# Backwards compatibility alias
StabilizeRunner = HighwayRunner
