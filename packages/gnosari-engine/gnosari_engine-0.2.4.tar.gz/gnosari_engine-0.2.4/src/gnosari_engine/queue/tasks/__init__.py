"""
Celery task definitions.

This module contains all Celery task definitions for async job processing.
Follows Single Responsibility Principle - each task has a single purpose.
"""

import asyncio
import logging
from typing import Any, Dict

from ..celery_app import celery_app
from ..handlers.task_execution_handler import TaskExecutionHandler
from ...config.env_helpers import get_database_url
from ...schemas.domain.queue import TaskExecutionMessage

logger = logging.getLogger(__name__)


@celery_app.task(
    name="gnosari.queue.tasks.process_task_execution",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
)
def process_task_execution(self, message_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process task execution message.

    This is the Celery task that wraps the async handler.
    Celery tasks must be synchronous, so we use asyncio.run() to execute the async handler.

    Args:
        message_dict: Task execution message as dictionary

    Returns:
        Result dictionary with execution outcome

    Raises:
        Exception: If execution fails (will trigger Celery retry)
    """
    # Create message object from dict
    message = TaskExecutionMessage(**message_dict)

    logger.info(
        f"Processing task execution: "
        f"task_id={message.task_id}, message_id={message.message_id}, "
        f"attempt={self.request.retries + 1}/{message.max_retries + 1}"
    )

    # Log task info for user-friendly output
    logger.info(
        f"📥 Received task execution request: Task #{message.task_id} "
        f"(message: {message.message_id})"
    )

    # Get default database URL
    default_database_url = get_database_url()

    # Create handler
    handler = TaskExecutionHandler(default_database_url=default_database_url)

    # Run async handler in event loop
    try:
        # Get or create event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Run async handler
        result = loop.run_until_complete(handler.handle(message))

        logger.info(
            f"✅ Task execution completed: "
            f"task_id={message.task_id}, status={result.status}, "
            f"duration={result.duration_seconds:.2f}s"
        )

        # Return result as dict
        return result.model_dump()

    except Exception as e:
        logger.error(
            f"❌ Task execution failed: "
            f"task_id={message.task_id}, error={str(e)}"
        )
        raise


__all__ = ["process_task_execution"]
