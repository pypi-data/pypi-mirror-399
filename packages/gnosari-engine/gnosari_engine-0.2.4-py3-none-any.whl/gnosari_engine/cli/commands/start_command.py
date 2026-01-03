"""
Start Command - Starts the queue worker/consumer process.

This command starts the Celery worker that processes async task execution messages.
Follows SOLID principles with clear separation of concerns.
"""

import sys
from typing import Optional

from .base_command import BaseCommand
from ..interfaces import DisplayServiceInterface
from ...queue.worker_service import WorkerService
from ...queue.errors import WorkerError


class StartCommand(BaseCommand):
    """
    Command to start the queue worker/consumer.

    Follows Single Responsibility Principle - only handles worker startup.
    Provides beautiful, user-friendly output showing worker status.
    """

    def __init__(self, display_service: DisplayServiceInterface):
        """
        Initialize start command.

        Args:
            display_service: Display service for output
        """
        super().__init__(display_service)

    async def execute(
        self,
        concurrency: int = 4,
        queue: str = "task_execution",
        log_level: str = "INFO",
    ) -> None:
        """
        Execute the start command.

        Args:
            concurrency: Number of concurrent worker processes
            queue: Queue name to consume from
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        operation = "worker start"
        self._log_execution_start(operation)

        try:
            # Display beautiful startup header
            self._display_service.display_header()

            self._display_service.display_status(
                "🚀 Starting Gnosari Queue Worker", "info"
            )
            self._display_service.display_status(
                f"📋 Queue: {queue}", "info"
            )
            self._display_service.display_status(
                f"⚙️  Concurrency: {concurrency} workers", "info"
            )
            self._display_service.display_status(
                f"📊 Log Level: {log_level}", "info"
            )

            self._display_service.display_status(
                "\n✅ Worker is ready - Press Ctrl+C to stop gracefully\n",
                "success"
            )

            # Create and start worker service
            # This is a blocking call
            worker = WorkerService(
                concurrency=concurrency, queue_name=queue, log_level=log_level
            )

            worker.start()

        except KeyboardInterrupt:
            # Graceful shutdown on Ctrl+C
            self._display_service.display_status(
                "\n🛑 Worker stopped by user", "info"
            )
            self._log_execution_end(operation)
            sys.exit(0)

        except WorkerError as e:
            # Worker-specific errors
            self._handle_error(e, operation)
            self._display_service.display_status(
                f"Worker error: {e.message}", "error"
            )
            sys.exit(1)

        except Exception as e:
            # Unexpected errors
            self._handle_error(e, operation)
            self._display_service.display_status(
                f"Failed to start worker: {str(e)}", "error"
            )
            sys.exit(1)
