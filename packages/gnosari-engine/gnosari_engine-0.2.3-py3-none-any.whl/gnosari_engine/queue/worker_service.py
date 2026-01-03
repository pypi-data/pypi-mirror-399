"""
Worker service for processing queue messages.

This module provides the worker service that processes messages from the queue.
Follows Single Responsibility Principle - only manages worker lifecycle.
"""

import logging
import signal
import sys
from typing import Optional

from .celery_app import celery_app

logger = logging.getLogger(__name__)


class WorkerService:
    """
    Worker service for processing queue messages.

    Follows Single Responsibility Principle - only manages worker lifecycle.
    Provides user-friendly output for received messages and their execution status.
    """

    def __init__(
        self,
        concurrency: int = 4,
        queue_name: str = "task_execution",
        log_level: str = "INFO",
    ):
        """
        Initialize worker service.

        Args:
            concurrency: Number of concurrent worker processes
            queue_name: Queue name to consume from
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self._concurrency = concurrency
        self._queue_name = queue_name
        self._log_level = log_level
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

    def start(self) -> None:
        """
        Start the worker service.

        This is a blocking call that runs the Celery worker.
        The worker will process messages from the queue and display
        user-friendly output for each message.
        """
        self._logger.info(
            f"Starting Gnosari Queue Worker: "
            f"queue={self._queue_name}, concurrency={self._concurrency}"
        )

        # Print user-friendly startup message
        print("\n" + "=" * 70)
        print("🚀 GNOSARI QUEUE WORKER STARTING")
        print("=" * 70)
        print(f"📋 Queue: {self._queue_name}")
        print(f"⚙️  Concurrency: {self._concurrency} workers")
        print(f"📊 Log Level: {self._log_level}")
        print("=" * 70)
        print("\n✅ Worker is ready and waiting for messages...")
        print("   Press Ctrl+C to stop gracefully\n")

        # Start Celery worker with optimized settings
        celery_app.worker_main(
            [
                "worker",
                f"--loglevel={self._log_level}",
                f"--concurrency={self._concurrency}",
                f"--queues={self._queue_name}",
                "--pool=prefork",  # Use process pool for better isolation
                "--autoscale=10,3",  # Auto-scale between 3 and 10 workers
                "--max-tasks-per-child=1000",  # Restart worker after 1000 tasks
                "--without-gossip",  # Disable gossip for better performance
                "--without-mingle",  # Disable mingle for faster startup
                "--without-heartbeat",  # Disable heartbeat for simplicity
            ]
        )

    def _handle_shutdown(self, signum, frame):
        """
        Handle shutdown signals gracefully.

        Args:
            signum: Signal number (SIGINT or SIGTERM)
            frame: Current stack frame
        """
        print("\n" + "=" * 70)
        print("🛑 SHUTTING DOWN GRACEFULLY")
        print("=" * 70)
        print("⏳ Waiting for current tasks to complete...")
        print("   (This may take a moment)\n")

        self._logger.info("Received shutdown signal, stopping worker...")
        sys.exit(0)
