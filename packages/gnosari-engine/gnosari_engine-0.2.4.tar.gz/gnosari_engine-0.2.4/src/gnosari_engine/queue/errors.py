"""
Queue-related error classes.

This module defines all custom exceptions for the async task queue system.
Follows Single Responsibility Principle - each exception represents a specific error type.
"""

from typing import Optional


class QueueError(Exception):
    """
    Base exception for queue-related errors.

    All queue-specific exceptions inherit from this base class.
    """

    def __init__(self, message: str, error_code: Optional[str] = None):
        """
        Initialize queue error.

        Args:
            message: Human-readable error message
            error_code: Optional error code for programmatic handling
        """
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class MessageValidationError(QueueError):
    """
    Message validation failed.

    Raised when a queue message fails Pydantic validation.
    """

    def __init__(self, message: str, validation_errors: dict):
        """
        Initialize message validation error.

        Args:
            message: Error message
            validation_errors: Dictionary of validation errors from Pydantic
        """
        super().__init__(message, error_code="MESSAGE_VALIDATION_ERROR")
        self.validation_errors = validation_errors


class MessageDispatchError(QueueError):
    """
    Failed to dispatch message to queue.

    Raised when message cannot be sent to the queue broker.
    """

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        """
        Initialize message dispatch error.

        Args:
            message: Error message
            original_error: Original exception that caused dispatch failure
        """
        super().__init__(message, error_code="MESSAGE_DISPATCH_ERROR")
        self.original_error = original_error


class TaskNotFoundError(QueueError):
    """
    Task not found in database.

    Raised when attempting to execute a non-existent task.
    """

    def __init__(self, task_id: int, account_id: int):
        """
        Initialize task not found error.

        Args:
            task_id: Task database ID that was not found
            account_id: Account ID that was queried
        """
        message = f"Task {task_id} not found for account {account_id}"
        super().__init__(message, error_code="TASK_NOT_FOUND")
        self.task_id = task_id
        self.account_id = account_id


class HandlerNotFoundError(QueueError):
    """
    No handler found for message type.

    Raised when worker receives a message type with no registered handler.
    """

    def __init__(self, message_type: str):
        """
        Initialize handler not found error.

        Args:
            message_type: The message type that has no handler
        """
        message = f"No handler registered for message type: {message_type}"
        super().__init__(message, error_code="HANDLER_NOT_FOUND")
        self.message_type = message_type


class WorkerError(QueueError):
    """
    Worker-related error.

    Raised when worker encounters an error during startup or execution.
    """

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        """
        Initialize worker error.

        Args:
            message: Error message
            original_error: Original exception if available
        """
        super().__init__(message, error_code="WORKER_ERROR")
        self.original_error = original_error


class QueueConnectionError(QueueError):
    """
    Queue connection error.

    Raised when unable to connect to queue broker (Redis).
    """

    def __init__(self, message: str, broker_url: Optional[str] = None):
        """
        Initialize queue connection error.

        Args:
            message: Error message
            broker_url: URL of the broker that failed to connect (sanitized)
        """
        super().__init__(message, error_code="QUEUE_CONNECTION_ERROR")
        self.broker_url = broker_url
