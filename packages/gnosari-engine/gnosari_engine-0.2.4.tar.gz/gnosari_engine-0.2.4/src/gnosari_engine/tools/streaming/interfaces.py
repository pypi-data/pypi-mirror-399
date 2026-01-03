"""
Tool streaming interfaces following SOLID principles.

These interfaces define contracts for tool streaming capabilities
without coupling to specific implementations.
"""

import time
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from enum import Enum
from typing import Any, Protocol, runtime_checkable

from ...runners.interfaces import StreamEvent


class ToolEventType(Enum):
    """Tool streaming event types."""
    
    TOOL_START = "tool_start"
    TOOL_PROGRESS = "tool_progress" 
    TOOL_RESULT = "tool_stream_result"  # Different from standard OpenAI tool_result
    TOOL_ERROR = "tool_stream_error"    # Different from standard OpenAI tool_error
    TOOL_COMPLETE = "tool_complete"


class ToolStreamEvent:
    """
    Represents a tool streaming event.
    
    Follows Single Responsibility Principle: Only manages tool event data.
    """
    
    def __init__(
        self,
        tool_name: str,
        event_type: ToolEventType,
        data: dict[str, Any],
        timestamp: float | None = None
    ):
        self.tool_name = tool_name
        self.event_type = event_type
        self.data = data
        self.timestamp = timestamp or time.time()
    
    def to_stream_event(self) -> StreamEvent:
        """Convert to base StreamEvent for runner integration."""
        return StreamEvent(
            event_type=self.event_type.value,
            data={
                "tool_name": self.tool_name,
                "timestamp": self.timestamp,
                **self.data
            },
            timestamp=self.timestamp
        )


@runtime_checkable
class IToolEventEmitter(Protocol):
    """
    Protocol for tool event emission.
    
    Follows Interface Segregation Principle: Focused only on event emission.
    """
    
    async def emit_event(self, event: ToolStreamEvent) -> None:
        """Emit a tool streaming event."""
        ...


@runtime_checkable
class IToolStreamContext(Protocol):
    """
    Protocol for tool streaming context.
    
    Follows Dependency Inversion Principle: Tools depend on this abstraction.
    """
    
    async def emit_start(self, tool_name: str, data: dict[str, Any] | None = None) -> None:
        """Emit tool start event."""
        ...
    
    async def emit_progress(self, tool_name: str, data: dict[str, Any]) -> None:
        """Emit tool progress event."""
        ...
    
    async def emit_result(self, tool_name: str, data: dict[str, Any]) -> None:
        """Emit tool intermediate result event."""
        ...
    
    async def emit_error(self, tool_name: str, error: Exception) -> None:
        """Emit tool error event."""
        ...
    
    async def emit_complete(self, tool_name: str, data: dict[str, Any] | None = None) -> None:
        """Emit tool completion event."""
        ...


@runtime_checkable
class IStreamableTool(Protocol):
    """
    Protocol for tools that support streaming.
    
    Follows Interface Segregation Principle: Optional streaming capability.
    """
    
    def supports_streaming(self) -> bool:
        """Check if tool supports streaming."""
        ...
    
    def set_stream_context(self, context: IToolStreamContext) -> None:
        """Inject streaming context into tool."""
        ...


@runtime_checkable
class IToolStreamManager(Protocol):
    """
    Protocol for managing tool streaming.
    
    Follows Single Responsibility Principle: Only manages streaming.
    """
    
    async def create_stream_context(self) -> IToolStreamContext:
        """Create a new streaming context."""
        ...
    
    async def collect_events(self) -> AsyncGenerator[ToolStreamEvent, None]:
        """Collect streaming events as they occur."""
        ...
    
    async def cleanup(self) -> None:
        """Cleanup streaming resources."""
        ...


class BaseStreamableTool(ABC):
    """
    Abstract base for streamable tools.

    ULTRA-CLEAN DESIGN: Tools look up stream context from global registry
    instead of requiring complex injection mechanisms.

    Follows Template Method Pattern: Defines streaming structure,
    subclasses implement specific streaming logic.
    """

    def __init__(self):
        # Context retrieved dynamically from global registry
        self._session_id: str | None = None

    def supports_streaming(self) -> bool:
        """Tools can override to indicate streaming support."""
        return True

    def set_session_id(self, session_id: str) -> None:
        """Set session ID for registry lookup."""
        self._session_id = session_id

    def _get_stream_context(self) -> IToolStreamContext | None:
        """
        Get stream context - ULTRA-CLEAN implementation using global registry.

        Priority:
        1. Registry lookup by session ID (if set during init from agent_run)
        2. Registry current context (global fallback for same execution)
        3. None (streaming disabled)
        """
        import logging
        logger = logging.getLogger(__name__)

        # Try registry lookup by session ID
        if self._session_id:
            from .registry import StreamContextRegistry
            context = StreamContextRegistry.get(self._session_id)
            if context:
                logger.debug(f"[STREAM CONTEXT] Registry lookup for session {self._session_id}: FOUND")
                return context
            logger.debug(f"[STREAM CONTEXT] Registry lookup for session {self._session_id}: NOT FOUND")

        # Fallback to global current context (for tools created without session_id)
        from .registry import StreamContextRegistry
        current = StreamContextRegistry.get_current()
        if current:
            logger.debug(f"[STREAM CONTEXT] Using global current context")
            return current

        logger.debug(f"[STREAM CONTEXT] No context available")
        return None

    @property
    def has_stream_context(self) -> bool:
        """Check if streaming context is available."""
        return self._get_stream_context() is not None

    async def _emit_start(self, data: dict[str, Any] | None = None) -> None:
        """Protected method to emit start event."""
        context = self._get_stream_context()
        if context:
            await context.emit_start(self._get_tool_name(), data or {})

    async def _emit_progress(self, data: dict[str, Any]) -> None:
        """Protected method to emit progress event."""
        context = self._get_stream_context()
        if context:
            await context.emit_progress(self._get_tool_name(), data)

    async def _emit_result(self, data: dict[str, Any]) -> None:
        """Protected method to emit result event."""
        context = self._get_stream_context()
        if context:
            await context.emit_result(self._get_tool_name(), data)

    async def _emit_error(self, error: Exception) -> None:
        """Protected method to emit error event."""
        context = self._get_stream_context()
        if context:
            await context.emit_error(self._get_tool_name(), error)

    async def _emit_complete(self, data: dict[str, Any] | None = None) -> None:
        """Protected method to emit completion event."""
        context = self._get_stream_context()
        if context:
            await context.emit_complete(self._get_tool_name(), data or {})

    @abstractmethod
    def _get_tool_name(self) -> str:
        """Get the tool name for event emission."""
        pass