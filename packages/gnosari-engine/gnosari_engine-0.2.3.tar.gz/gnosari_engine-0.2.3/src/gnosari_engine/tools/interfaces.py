"""
Tool interfaces following Interface Segregation Principle.

Each interface has a single, focused responsibility to ensure clean
separation of concerns and easy testing.
"""

from abc import abstractmethod
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class IToolProvider(Protocol):
    """
    Base protocol for all tool providers.
    
    Follows Interface Segregation Principle by focusing only on provider
    management responsibilities.
    """

    @property
    def provider_name(self) -> str:
        """Get the provider name (e.g., 'openai', 'anthropic')."""
        ...

    @property
    def tool_name(self) -> str:
        """Get the tool name (e.g., 'knowledge_query')."""
        ...

    @property
    def is_initialized(self) -> bool:
        """Check if tool is initialized."""
        ...

    async def initialize(self, **config) -> None:
        """Initialize the tool with provider-specific configuration."""
        ...

    async def cleanup(self) -> None:
        """Cleanup tool resources."""
        ...

    def get_tool_implementation(self) -> Any:
        """Return the provider-specific tool implementation."""
        ...


@runtime_checkable
class ISyncTool(Protocol):
    """
    Protocol for synchronous tool execution.
    
    Separated from IToolProvider to follow Interface Segregation Principle.
    """

    def execute(self, **kwargs) -> Any:
        """Execute tool synchronously."""
        ...


@runtime_checkable
class IAsyncTool(Protocol):
    """
    Protocol for asynchronous tool execution.
    
    Separated from IToolProvider to follow Interface Segregation Principle.
    """

    async def execute(self, **kwargs) -> Any:
        """Execute tool asynchronously."""
        ...