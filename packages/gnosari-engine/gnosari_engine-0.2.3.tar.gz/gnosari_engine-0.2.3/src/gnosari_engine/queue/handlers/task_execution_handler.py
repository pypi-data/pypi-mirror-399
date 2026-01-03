"""
Handler for task execution messages.

This module implements the message handler for asynchronous task execution.
Follows Single Responsibility Principle - only handles task execution messages.
"""

import logging
from pathlib import Path
from typing import Optional

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from ...config.env_helpers import get_database_url
from ...cli.services import DomainFactory
from ...prompts.agent_prompt_builder import AgentPromptBuilder
from ...schemas.domain.queue import (
    MessageStatus,
    QueueMessage,
    TaskExecutionMessage,
    TaskExecutionResult,
)
from ...services.task_executor import TaskExecutor
from ...sessions.repositories.task_repository import TaskRepository
from ..errors import TaskNotFoundError
from .base import MessageHandler


# Create configuration service for loading team configs
from ...config.configuration_service import ConfigurationService
from ...factories.configuration_service_factory import ConfigurationServiceFactory

logger = logging.getLogger(__name__)


class TaskExecutionHandler(MessageHandler):
    """
    Handler for task execution messages.

    Follows Single Responsibility Principle - only handles task execution.
    Depends on abstractions (TaskExecutor, TaskRepository) not concretions.
    """

    def __init__(self, default_database_url: Optional[str] = None):
        """
        Initialize handler.

        Args:
            default_database_url: Default database URL if not in message
        """
        self._default_database_url = default_database_url or get_database_url()
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @property
    def supported_message_types(self) -> list[str]:
        """Get supported message types."""
        return ["task_execution"]

    def can_handle(self, message_type: str) -> bool:
        """Check if handler supports message type."""
        return message_type in self.supported_message_types

    async def handle(self, message: QueueMessage) -> TaskExecutionResult:
        """
        Handle task execution message.

        Args:
            message: TaskExecutionMessage to process

        Returns:
            TaskExecutionResult with execution outcome

        Raises:
            ValueError: If message is not TaskExecutionMessage
            TaskNotFoundError: If task not found in database
        """
        # Validate message type
        if not isinstance(message, TaskExecutionMessage):
            raise ValueError(
                f"Expected TaskExecutionMessage, got {type(message).__name__}"
            )

        # Mark message as started
        message.mark_started()

        self._logger.info(
            f"Handling task execution message: "
            f"task_id={message.task_id}, message_id={message.message_id}"
        )

        try:
            # Execute task
            output = await self._execute_task(message)

            # Mark message as completed
            message.mark_completed()

            # Return success result
            return TaskExecutionResult(
                message_id=message.message_id,
                task_id=message.task_id,
                status=MessageStatus.COMPLETED,
                output=output,
                error=None,
                duration_seconds=message.get_processing_duration(),
                retry_count=message.retry_count,
            )

        except TaskNotFoundError as e:
            # Task not found - don't retry
            self._logger.error(f"Task not found: {e}", exc_info=True)
            message.mark_completed()

            return TaskExecutionResult(
                message_id=message.message_id,
                task_id=message.task_id,
                status=MessageStatus.FAILED,
                output=None,
                error=str(e),
                duration_seconds=message.get_processing_duration(),
                retry_count=message.retry_count,
            )

        except Exception as e:
            # Other errors - mark as failed
            self._logger.error(
                f"Task execution failed: task_id={message.task_id}, error={str(e)}",
                exc_info=True  # Include full traceback
            )

            message.mark_completed()

            return TaskExecutionResult(
                message_id=message.message_id,
                task_id=message.task_id,
                status=MessageStatus.FAILED,
                output=None,
                error=str(e),
                duration_seconds=message.get_processing_duration(),
                retry_count=message.retry_count,
            )

    async def _execute_task(self, message: TaskExecutionMessage) -> str:
        """
        Execute task using TaskExecutor service.

        Args:
            message: Task execution message

        Returns:
            Execution output string

        Raises:
            TaskNotFoundError: If task not found
            Exception: If execution fails
        """
        # Get database URL
        database_url = message.database_url or self._default_database_url
        if not database_url:
            raise ValueError("Database URL is required for task execution")

        # Initialize database connection
        engine = create_async_engine(
            database_url,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=3600,
            pool_pre_ping=True,
            echo=False,
        )

        session_factory = async_sessionmaker(
            engine, expire_on_commit=False, autoflush=False
        )

        try:
            # Initialize services
            task_repository = TaskRepository(session_factory)
            task_executor = TaskExecutor(task_repository=task_repository)
            domain_factory = DomainFactory()
            prompt_builder = AgentPromptBuilder()

            # Create configuration service
            config_service_factory = ConfigurationServiceFactory()
            config_service = config_service_factory.create()  # Uses default "eager" strategy

            # Load task from database
            self._logger.info(
                f"Loading task {message.task_id} for account {message.account_id}"
            )
            task_data = await task_repository.get_task(
                message.task_id, message.account_id
            )

            if not task_data:
                raise TaskNotFoundError(message.task_id, message.account_id)

            # Create Task domain object
            task = domain_factory.create_task_from_dict(task_data)
            self._logger.info(f"Created Task domain object: {task.title}")

            # Load team configuration
            self._logger.info(f"Loading team configuration: {message.team_config_path}")
            team = config_service.load_team_configuration(
                Path(message.team_config_path)
            )
            self._logger.info(f"Loaded team: {team.name}")

            # Create TaskRun
            self._logger.info(f"Creating TaskRun for task {message.task_id}")
            task_run = domain_factory.create_task_run(
                task=task,
                team=team,
                prompt_builder=prompt_builder,
                stream=False,  # No streaming in async mode
                debug=message.debug,
                tool_streaming=message.tool_streaming,
                stream_merger=message.stream_merger,
                session_id=message.session_id,
                account_id=message.account_id,
            )

            # Execute task
            self._logger.info(f"Executing task {message.task_id} via TaskExecutor")
            result = await task_executor.execute_task(
                task_run=task_run, provider=message.provider, database_url=database_url
            )

            # Extract output
            if result.status == "completed":
                output = result.output or "Task completed successfully"
                self._logger.info(f"Task {message.task_id} completed successfully")
                return str(output)
            else:
                error = result.error or "Task execution failed"
                self._logger.error(
                    f"Task {message.task_id} failed: {error}",
                    exc_info=True  # Include full traceback if available
                )
                raise Exception(error)

        finally:
            # Cleanup database connection
            await engine.dispose()
