"""
Message dispatcher for sending messages to queue.

This module provides the dispatcher service for sending task execution messages to the queue.
Follows Single Responsibility Principle - only responsible for message dispatch.
"""

import logging
import uuid
from typing import Optional

from ..schemas.domain.queue import MessagePriority, TaskExecutionMessage
from .celery_app import celery_app
from .errors import MessageDispatchError


class MessageDispatcher:
    """
    Message dispatcher service.

    Follows Single Responsibility Principle - only dispatches messages.
    Depends on Celery abstraction, not direct Redis access (Dependency Inversion).
    """

    def __init__(self):
        """Initialize dispatcher with logger."""
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def dispatch_task_execution(
        self,
        task_id: int,
        account_id: int,
        team_config_path: str,
        provider: str = "openai",
        session_id: Optional[str] = None,
        database_url: Optional[str] = None,
        debug: bool = False,
        tool_streaming: bool = True,
        stream_merger: str = "time_ordered",
        priority: MessagePriority = MessagePriority.NORMAL,
        max_retries: int = 3,
        assigned_agent_identifier: Optional[str] = None,
    ) -> str:
        """
        Dispatch task execution message to queue.

        Args:
            task_id: Task database ID
            account_id: Account ID for multi-tenancy
            team_config_path: Path to team YAML configuration
            provider: LLM provider to use
            session_id: Optional session ID for tracking
            database_url: Optional database URL (uses env if not provided)
            debug: Enable debug mode
            tool_streaming: Enable tool streaming
            stream_merger: Stream merger strategy
            priority: Message priority level
            max_retries: Maximum retry attempts
            assigned_agent_identifier: Optional agent identifier from YAML

        Returns:
            Message ID for tracking

        Raises:
            MessageDispatchError: If message dispatch fails
        """
        # Generate unique message ID
        message_id = f"task-{task_id}-{uuid.uuid4().hex[:8]}"

        try:
            # Create message domain object (Pydantic validation happens here)
            message = TaskExecutionMessage(
                message_id=message_id,
                task_id=task_id,
                account_id=account_id,
                team_config_path=team_config_path,
                provider=provider,
                session_id=session_id,
                database_url=database_url,
                debug=debug,
                tool_streaming=tool_streaming,
                stream_merger=stream_merger,
                priority=priority,
                max_retries=max_retries,
                assigned_agent_identifier=assigned_agent_identifier,
            )

            self._logger.info(
                f"Dispatching task execution message: "
                f"task_id={task_id}, message_id={message_id}, priority={priority.value}"
            )

            # Dispatch to Celery
            celery_app.send_task(
                "gnosari.queue.tasks.process_task_execution",
                kwargs={"message_dict": message.model_dump()},
                task_id=message_id,
                priority=self._get_celery_priority(priority),
                queue="task_execution",
            )

            self._logger.info(f"Message dispatched successfully: {message_id}")
            return message_id

        except Exception as e:
            self._logger.error(
                f"Failed to dispatch task execution message: "
                f"task_id={task_id}, error={str(e)}"
            )
            raise MessageDispatchError(
                f"Failed to dispatch task {task_id} to queue: {str(e)}",
                original_error=e,
            ) from e

    def _get_celery_priority(self, priority: MessagePriority) -> int:
        """
        Convert MessagePriority to Celery priority number.

        Args:
            priority: MessagePriority enum value

        Returns:
            Celery priority (0-9, higher is more important)
        """
        priority_map = {
            MessagePriority.HIGH: 9,
            MessagePriority.NORMAL: 5,
            MessagePriority.LOW: 1,
        }
        return priority_map.get(priority, 5)
