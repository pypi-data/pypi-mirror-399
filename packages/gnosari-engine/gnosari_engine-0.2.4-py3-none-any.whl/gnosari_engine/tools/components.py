"""
Tool management components following Single Responsibility Principle.

Provides tool lifecycle management and provider coordination while
maintaining clean separation of concerns.
"""

import logging
from typing import Any

from ..knowledge.interfaces import IKnowledgeProvider
from ..schemas.domain.tool import Tool
from .factories.tool_factory import AutoDiscoveryToolFactory
from .interfaces import IToolProvider


class ToolManager:
    """
    Tool manager component following Single Responsibility Principle.
    
    Responsible only for managing tool lifecycle and provider coordination.
    Delegates tool creation to factory and tool logic to providers.
    """

    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self._factory = AutoDiscoveryToolFactory()
        self._active_tools: dict[str, IToolProvider] = {}
        self._is_initialized = False

    async def initialize(self, **config):
        """Initialize tool manager with configuration."""
        # Auto-discovery is enabled by default, but can explicitly register critical tools
        self._register_critical_tools()
        
        self._is_initialized = True

    def _register_critical_tools(self):
        """
        Register only critical tools that must be available immediately.
        
        Most tools will be auto-discovered on demand, but critical tools
        (like core delegation or essential system tools) can be registered
        explicitly for guaranteed availability.
        """
        # Optional: Explicitly register critical tools if needed
        # Most tools will be auto-discovered via the factory
        pass

    async def get_tool_provider(
        self,
        tool: Tool,
        agent_run=None,
        **config
    ) -> IToolProvider:
        """
        Get tool provider instance.

        Uses caching to avoid recreating tools and follows lazy loading pattern.
        Tools automatically look up stream context from global registry.
        """
        if not self._is_initialized:
            raise RuntimeError("ToolManager not initialized")

        tool_key = f"{tool.id}_{self.provider_name}"

        if tool_key not in self._active_tools:
            # Create tool provider using factory
            provider = self._factory.create_tool_provider(
                tool,
                self.provider_name,
                agent_run=agent_run,
                **config
            )

            # Initialize the provider with agent_run context
            await provider.initialize(agent_run=agent_run, **config)

            # Cache for future use
            self._active_tools[tool_key] = provider
        else:
            # Tool is cached and will automatically get context from registry
            provider = self._active_tools[tool_key]

        return provider

    async def get_tool_implementation(self, tool: Tool, agent_run=None, **config) -> Any:
        """
        Get provider-specific tool implementation ready for use.
        
        Convenience method that combines provider creation and implementation extraction.
        
        Args:
            tool: Tool configuration
            agent_run: Optional AgentRun context for tool execution
            **config: Additional tool configuration
        """
        provider = await self.get_tool_provider(tool, agent_run=agent_run, **config)
        return provider.get_tool_implementation()

    async def cleanup(self):
        """Cleanup all active tools."""
        for tool_provider in self._active_tools.values():
            try:
                await tool_provider.cleanup()
            except Exception as e:
                logging.warning(f"Failed to cleanup tool {tool_provider.tool_name}: {e}")
        
        self._active_tools.clear()

    def get_available_tools(self) -> list[str]:
        """Get list of available tools for this provider."""
        return self._factory.get_available_tools(self.provider_name)

    @property
    def is_initialized(self) -> bool:
        """Check if tool manager is initialized."""
        return self._is_initialized