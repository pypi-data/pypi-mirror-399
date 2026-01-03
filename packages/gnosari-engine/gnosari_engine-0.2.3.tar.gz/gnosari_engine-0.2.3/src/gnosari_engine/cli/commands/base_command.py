"""
Base Command - Abstract base class for all CLI commands following SOLID principles
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
import logging

from ..interfaces import DisplayServiceInterface


class BaseCommand(ABC):
    """
    Abstract base class for all CLI commands.
    
    Implements:
    - Single Responsibility: Each command handles one specific operation
    - Open/Closed: Commands can be extended without modifying base
    - Interface Segregation: Commands only depend on interfaces they need
    - Dependency Inversion: Depends on abstractions, not concretions
    """
    
    def __init__(self, display_service: DisplayServiceInterface):
        """Initialize base command with required services"""
        self._display_service = display_service
        self._logger = logging.getLogger(f"cli.{self.__class__.__name__.lower()}")
    
    @abstractmethod
    async def execute(self, *args, **kwargs) -> None:
        """Execute the command - must be implemented by subclasses"""
        pass
    
    def _log_execution_start(self, operation: str) -> None:
        """Log the start of command execution"""
        self._logger.info(f"Starting {operation}")
    
    def _log_execution_end(self, operation: str) -> None:
        """Log the end of command execution"""
        self._logger.info(f"Completed {operation}")
    
    def _handle_error(self, error: Exception, operation: str) -> None:
        """Handle command execution errors consistently"""
        self._logger.error(f"Failed {operation}: {error}", exc_info=True)
        self._display_service.display_status(f"Failed {operation}: {error}", "error")