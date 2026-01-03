"""
Base message handler interface.

This module defines the abstract base class for all message handlers.
Follows Interface Segregation Principle - minimal, focused interface.
"""

from abc import ABC, abstractmethod

from ...schemas.domain.queue import QueueMessage, TaskExecutionResult


class MessageHandler(ABC):
    """
    Abstract base class for message handlers.

    Follows Interface Segregation Principle - minimal interface with only essential methods.
    Open/Closed Principle - extend via subclassing without modification.
    Liskov Substitution Principle - all subclasses must maintain the contract.
    """

    @abstractmethod
    async def handle(self, message: QueueMessage) -> TaskExecutionResult:
        """
        Handle a queue message.

        Args:
            message: Queue message to process

        Returns:
            TaskExecutionResult with processing outcome

        Raises:
            Exception: If processing fails (will be caught by Celery for retry)
        """
        pass

    @abstractmethod
    def can_handle(self, message_type: str) -> bool:
        """
        Check if this handler can handle the given message type.

        Args:
            message_type: Type of message to check

        Returns:
            True if handler supports this message type
        """
        pass

    @property
    @abstractmethod
    def supported_message_types(self) -> list[str]:
        """
        Get list of supported message types.

        Returns:
            List of message type identifiers this handler can process
        """
        pass
