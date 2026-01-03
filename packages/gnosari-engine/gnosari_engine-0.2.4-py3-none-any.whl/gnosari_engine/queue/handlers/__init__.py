"""
Queue message handlers.

This module contains all message handlers for processing queue messages.
Follows Open/Closed Principle - new handlers can be added without modifying existing code.
"""

from .base import MessageHandler
from .task_execution_handler import TaskExecutionHandler

__all__ = ["MessageHandler", "TaskExecutionHandler"]
