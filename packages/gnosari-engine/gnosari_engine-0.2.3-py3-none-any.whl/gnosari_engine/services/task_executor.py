"""
Task Executor Service

Provides reusable task execution functionality following SOLID principles.
This service can be used directly by library users for programmatic task execution.
"""

import logging
import uuid
from typing import Optional
from datetime import datetime

from ..schemas.domain import TaskRun
from ..runners.factory import create_enterprise_runner
from ..sessions.gnosari_session import GnosariSession
from ..sessions.repositories.task_repository import TaskRepository
from ..runners.interfaces import ExecutionResult

logger = logging.getLogger(__name__)


class TaskExecutor:
    """
    Task execution service following Single Responsibility Principle.

    Handles the complete lifecycle of task execution:
    1. Status updates (pending → in_progress → completed/failed)
    2. Agent execution
    3. Result storage

    This class can be used directly by library users for programmatic access.
    """

    def __init__(self, task_repository: Optional[TaskRepository] = None):
        """
        Initialize task executor.

        Args:
            task_repository: Optional TaskRepository instance.
                           If not provided, TaskExecutor will not update database.
        """
        self._task_repository = task_repository
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def execute_task(
        self,
        task_run: TaskRun,
        provider: str = "openai",
        database_url: Optional[str] = None
    ) -> ExecutionResult:
        """
        Execute a task with automatic status management and result storage.

        This is the main entry point for task execution. It handles:
        - Status update to 'in_progress'
        - Agent execution via runner
        - Status update to 'completed' or 'failed'
        - Result storage

        Args:
            task_run: TaskRun domain object with all execution context
            provider: LLM provider to use (openai, claude, etc.)
            database_url: Optional database URL for session persistence

        Returns:
            ExecutionResult with execution outcome

        Raises:
            Exception: If execution fails (after updating task status to 'failed')

        Example:
            ```python
            # Create TaskExecutor
            executor = TaskExecutor(task_repository)

            # Execute task
            result = await executor.execute_task(
                task_run=task_run,
                provider="openai"
            )

            print(f"Status: {result.status}")
            print(f"Output: {result.output}")
            ```
        """
        task_id = task_run.metadata.task_id
        account_id = task_run.metadata.account_id

        self._logger.info(f"Starting task execution: task_id={task_id}")

        try:
            # Step 1: Update task status to in_progress
            if task_run.context.update_status and self._task_repository:
                await self._update_task_status(
                    task_id, account_id, "in_progress"
                )

            # Step 2: Record execution start time
            task_run.metadata.execution_start = datetime.utcnow()

            # Step 3: Execute task via agent runner
            result = await self._execute_via_runner(
                task_run, provider, database_url
            )

            # Step 4: Record execution end time
            task_run.metadata.execution_end = datetime.utcnow()

            # Step 5: Update task status to completed and store result
            if task_run.context.store_result and self._task_repository:
                result_text = self._extract_result_text(result)
                await self._update_task_status_and_result(
                    task_id, account_id, "completed", result_text
                )

            self._logger.info(
                f"Task execution completed: task_id={task_id}, "
                f"duration={task_run.metadata.get_execution_duration()}s"
            )

            return result

        except Exception as e:
            # Record execution end time
            task_run.metadata.execution_end = datetime.utcnow()

            # Update task status to failed with error message
            if task_run.context.update_status and self._task_repository:
                error_message = f"Execution failed: {str(e)}"
                await self._update_task_status_and_result(
                    task_id, account_id, "failed", error_message
                )

            # Log error with full traceback
            self._logger.error(
                f"Task execution failed: task_id={task_id}, error={str(e)}",
                exc_info=True  # Include full traceback
            )

            # Re-raise if fail_on_error is True
            if task_run.context.fail_on_error:
                raise

            # Return error result
            return ExecutionResult(
                status="failed",
                output=None,
                error=str(e)
            )

    async def execute_task_stream(
        self,
        task_run: TaskRun,
        provider: str = "openai",
        database_url: Optional[str] = None
    ):
        """
        Execute a task with streaming support.

        Yields StreamEvent objects during execution. Automatically manages
        task status and result storage.

        Args:
            task_run: TaskRun domain object with all execution context
            provider: LLM provider to use
            database_url: Optional database URL for session persistence

        Yields:
            StreamEvent objects during execution

        Example:
            ```python
            async for event in executor.execute_task_stream(task_run):
                if event.event_type == "agent_message":
                    print(event.data.get("content"))
                elif event.event_type == "tool_call":
                    print(f"Tool: {event.data.get('tool_name')}")
            ```
        """
        task_id = task_run.metadata.task_id
        account_id = task_run.metadata.account_id

        self._logger.info(f"Starting streaming task execution: task_id={task_id}")

        try:
            # Update task status to in_progress
            if task_run.context.update_status and self._task_repository:
                await self._update_task_status(
                    task_id, account_id, "in_progress"
                )

            # Record execution start time
            task_run.metadata.execution_start = datetime.utcnow()

            # Execute with streaming
            final_result = None
            async for event in self._execute_via_runner_stream(
                task_run, provider, database_url
            ):
                yield event

                # Capture final result from completion event
                if event.event_type == "agent_completed":
                    # event.data is AgentCompletedData dataclass, not a dict
                    final_result = event.data.output

            # Record execution end time
            task_run.metadata.execution_end = datetime.utcnow()

            # Update task status to completed and store result
            if task_run.context.store_result and self._task_repository:
                result_text = final_result or "Agent completed execution"
                await self._update_task_status_and_result(
                    task_id, account_id, "completed", result_text
                )

            self._logger.info(f"Streaming task execution completed: task_id={task_id}")

        except Exception as e:
            # Record execution end time
            task_run.metadata.execution_end = datetime.utcnow()

            # Update task status to failed
            if task_run.context.update_status and self._task_repository:
                error_message = f"Execution failed: {str(e)}"
                await self._update_task_status_and_result(
                    task_id, account_id, "failed", error_message
                )

            # Log error with full traceback
            self._logger.error(
                f"Streaming task execution failed: task_id={task_id}, error={str(e)}",
                exc_info=True  # Include full traceback
            )

            if task_run.context.fail_on_error:
                raise

    async def _execute_via_runner(
        self,
        task_run: TaskRun,
        provider: str,
        database_url: Optional[str]
    ) -> ExecutionResult:
        """
        Execute task via agent runner (non-streaming).

        Args:
            task_run: TaskRun domain object
            provider: LLM provider
            database_url: Database URL

        Returns:
            ExecutionResult
        """
        # Convert TaskRun to AgentRun
        agent_run = task_run.to_agent_run()

        # Use session_id from metadata or generate
        session_id = (
            task_run.metadata.session_id or
            f"task-{task_run.metadata.task_id}-{uuid.uuid4().hex[:8]}"
        )
        agent_run.metadata.session_id = session_id

        # Create session manager
        session_manager = GnosariSession(
            session_id=session_id,
            provider_name=f"{provider}_database",
            agent_run=agent_run,
            database_url=database_url
        )

        # Create runner
        runner = create_enterprise_runner(provider, agent_run.context)

        try:
            await runner.initialize()
            result = await runner.run_agent(agent_run)
            return result

        finally:
            await runner.cleanup()
            await session_manager.cleanup()

    async def _execute_via_runner_stream(
        self,
        task_run: TaskRun,
        provider: str,
        database_url: Optional[str]
    ):
        """
        Execute task via agent runner (streaming).

        Args:
            task_run: TaskRun domain object
            provider: LLM provider
            database_url: Database URL

        Yields:
            StreamEvent objects
        """
        # Convert TaskRun to AgentRun
        agent_run = task_run.to_agent_run()

        # Use session_id from metadata or generate
        session_id = (
            task_run.metadata.session_id or
            f"task-{task_run.metadata.task_id}-{uuid.uuid4().hex[:8]}"
        )
        agent_run.metadata.session_id = session_id

        # Create session manager
        session_manager = GnosariSession(
            session_id=session_id,
            provider_name=f"{provider}_database",
            agent_run=agent_run,
            database_url=database_url
        )

        # Create runner
        runner = create_enterprise_runner(provider, agent_run.context)

        try:
            await runner.initialize()

            async for event in runner.run_agent_stream(agent_run):
                yield event

        finally:
            await runner.cleanup()
            await session_manager.cleanup()

    async def _update_task_status(
        self,
        task_id: int,
        account_id: int,
        status: str
    ) -> None:
        """
        Update task status in database.

        Args:
            task_id: Task ID
            account_id: Account ID
            status: New status value
        """
        if not self._task_repository:
            return

        try:
            update_data = {"status": status}
            await self._task_repository.update_task(task_id, account_id, update_data)
            self._logger.debug(f"Task #{task_id} status updated to: {status}")

        except Exception as e:
            self._logger.error(f"Failed to update task status: {e}")
            # Don't raise - status update failure shouldn't block execution

    async def _update_task_status_and_result(
        self,
        task_id: int,
        account_id: int,
        status: str,
        result: Optional[str]
    ) -> None:
        """
        Update task status and result in database.

        Args:
            task_id: Task ID
            account_id: Account ID
            status: New status value
            result: Execution result or error message
        """
        if not self._task_repository:
            return

        try:
            update_data = {
                "status": status,
                "result": result
            }
            await self._task_repository.update_task(task_id, account_id, update_data)
            self._logger.debug(f"Task #{task_id} status and result updated")

        except Exception as e:
            self._logger.error(f"Failed to update task status and result: {e}")
            # Don't raise - status update failure shouldn't block execution

    def _extract_result_text(self, result) -> str:
        """
        Extract result text from execution result.

        Args:
            result: Execution result object

        Returns:
            String representation of the result
        """
        if result is None:
            return "No result returned"

        # Check if result has an output attribute (ExecutionResult)
        if hasattr(result, 'output') and result.output is not None:
            return str(result.output)

        # Check if result has error attribute (ExecutionResult)
        if hasattr(result, 'error') and result.error is not None:
            return f"Error: {result.error}"

        # Check other common attributes
        for attr in ['message', 'response', 'text', 'content']:
            if hasattr(result, attr):
                value = getattr(result, attr)
                if value is not None:
                    return str(value)

        # Fallback to string representation
        return str(result)


__all__ = ["TaskExecutor"]
