"""
Factory interfaces for tool creation and management.

Follows Interface Segregation Principle with focused responsibilities.
"""

from typing import Protocol

from ...schemas.domain.tool import Tool
from ..interfaces import IToolProvider


class IToolFactory(Protocol):
    """
    Factory interface for creating tool providers.
    
    Follows Single Responsibility Principle by focusing only on
    tool provider creation and registration.
    """

    def create_tool_provider(
        self, 
        tool: Tool,
        provider_name: str,
        agent_run=None,
        **config
    ) -> IToolProvider:
        """Create tool provider instance with optional AgentRun context."""
        ...

    def register_tool_provider(
        self, 
        tool_name: str,
        provider_name: str, 
        provider_class: type[IToolProvider]
    ) -> None:
        """Register tool provider class."""
        ...

    def get_available_tools(self, provider_name: str) -> list[str]:
        """Get available tools for provider."""
        ...