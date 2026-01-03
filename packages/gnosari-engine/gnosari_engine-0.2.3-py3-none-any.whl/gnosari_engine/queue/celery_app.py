"""
Celery application configuration.

This module configures the Celery application for async task execution.
Follows Dependency Inversion Principle - configuration is externalized to environment.
"""

import os

from celery import Celery
from kombu import Exchange, Queue

# Get configuration from environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_DB = os.getenv("REDIS_DB", "0")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

# Build broker and backend URLs
if REDIS_PASSWORD:
    BROKER_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    RESULT_BACKEND = (
        f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    )
else:
    BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# Create Celery application
celery_app = Celery("gnosari.queue", broker=BROKER_URL, backend=RESULT_BACKEND)

# Celery configuration following best practices
celery_app.conf.update(
    # Task serialization (JSON for security and compatibility)
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    # Timezone configuration
    timezone="UTC",
    enable_utc=True,
    # Task execution reliability
    task_acks_late=True,  # Acknowledge after task completes
    task_reject_on_worker_lost=True,  # Reject if worker crashes
    task_track_started=True,  # Track when task starts
    # Event monitoring (enables Flower UI and monitoring)
    worker_send_task_events=True,  # Worker sends task events
    task_send_sent_event=True,  # Send event when task is sent
    # Retry configuration
    task_max_retries=3,
    task_default_retry_delay=60,  # 1 minute between retries
    # Result backend configuration
    result_expires=3600,  # Results expire after 1 hour
    result_extended=True,  # Store additional metadata
    # Worker configuration
    worker_prefetch_multiplier=4,  # Prefetch 4 tasks per worker
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks
    worker_disable_rate_limits=True,  # Disable rate limits for better performance
    # Priority support
    task_queue_max_priority=10,
    task_default_priority=5,
    # Queue definitions
    task_queues=(
        Queue(
            "default",
            Exchange("default"),
            routing_key="default",
            max_priority=10,
        ),
        Queue(
            "task_execution",
            Exchange("task_execution"),
            routing_key="task_execution",
            max_priority=10,
        ),
    ),
    # Default queue routing
    task_default_queue="default",
    task_default_exchange="default",
    task_default_routing_key="default",
    # Broker connection retry
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=10,
)

# Auto-discover tasks in the queue.tasks module
celery_app.autodiscover_tasks(["gnosari_engine.queue.tasks"])
