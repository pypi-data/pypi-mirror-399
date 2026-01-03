"""
Base classes for provider-agnostic tools.

Follows Single Responsibility Principle: Only defines tool logic.
Subclasses implement provider-specific execution.
"""

from abc import ABC, abstractmethod
from typing import Any

from ...schemas.domain.tool import Tool


class BaseProviderAgnosticTool(ABC):
    """
    Base class for provider-agnostic tools.
    
    Follows Single Responsibility Principle: Only defines tool logic.
    Subclasses implement provider-specific execution.
    """

    def __init__(self, tool_config: Tool):
        self.tool_config = tool_config
        self.name = tool_config.name or tool_config.id
        self.description = tool_config.description
        self.args = tool_config.args

    @abstractmethod
    async def execute_core_logic(self, **kwargs) -> Any:
        """Core tool logic that's provider-agnostic."""
        pass

    @abstractmethod
    def get_input_schema(self) -> dict[str, Any]:
        """Get tool input schema."""
        pass

    @abstractmethod
    def get_output_schema(self) -> dict[str, Any]:
        """Get tool output schema."""
        pass

    async def initialize(self, **config) -> None:
        """Initialize tool with configuration (optional override)."""
        pass

    async def execute(self, **kwargs) -> Any:
        """Execute the tool (standard interface)."""
        return await self.execute_core_logic(**kwargs)

    async def cleanup(self) -> None:
        """Cleanup tool resources (optional override)."""
        pass
