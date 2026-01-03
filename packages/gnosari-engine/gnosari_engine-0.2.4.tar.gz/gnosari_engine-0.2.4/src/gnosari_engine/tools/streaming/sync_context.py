"""
Synchronous tool stream context - ULTRA SIMPLE solution with callbacks.

Instead of async queues and complex merging, tool events are emitted
immediately via callbacks for real-time streaming.
"""

import logging
from typing import Any, List, Callable, Optional
import time

from .interfaces import IToolStreamContext, ToolEventType, ToolStreamEvent

logger = logging.getLogger(__name__)


class SyncToolStreamContext(IToolStreamContext):
    """
    Synchronous tool stream context with immediate callback emission.

    ULTRA-CLEAN: Events are emitted immediately via callback for real-time streaming.
    Also maintains a buffer for fallback retrieval.
    """

    def __init__(self, event_callback: Optional[Callable[[ToolStreamEvent], None]] = None):
        self._events: List[ToolStreamEvent] = []
        self._is_active = True
        self._event_callback = event_callback

    async def emit_start(self, tool_name: str, data: dict[str, Any] | None = None) -> None:
        """Emit tool start event - immediately via callback."""
        if not self._is_active:
            return

        event = ToolStreamEvent(
            event_type=ToolEventType.TOOL_START,
            tool_name=tool_name,
            data=data or {},
            timestamp=time.time()
        )
        self._events.append(event)

        # Immediately emit via callback for real-time streaming
        if self._event_callback:
            self._event_callback(event)

        logger.debug(f"Emitted tool start event: {tool_name}")

    async def emit_progress(self, tool_name: str, data: dict[str, Any]) -> None:
        """Emit tool progress event - immediately via callback."""
        if not self._is_active:
            return

        event = ToolStreamEvent(
            event_type=ToolEventType.TOOL_PROGRESS,
            tool_name=tool_name,
            data=data,
            timestamp=time.time()
        )
        self._events.append(event)

        # Immediately emit via callback for real-time streaming
        if self._event_callback:
            self._event_callback(event)

        logger.debug(f"Emitted tool progress event: {tool_name} - {data.get('step_name', '')}")

    async def emit_result(self, tool_name: str, data: dict[str, Any]) -> None:
        """Emit tool result event - immediately via callback."""
        if not self._is_active:
            return

        event = ToolStreamEvent(
            event_type=ToolEventType.TOOL_RESULT,
            tool_name=tool_name,
            data=data,
            timestamp=time.time()
        )
        self._events.append(event)

        # Immediately emit via callback for real-time streaming
        if self._event_callback:
            self._event_callback(event)

        logger.debug(f"Emitted tool result event: {tool_name}")

    async def emit_error(self, tool_name: str, error: Exception) -> None:
        """Emit tool error event - immediately via callback."""
        if not self._is_active:
            return

        event = ToolStreamEvent(
            event_type=ToolEventType.TOOL_ERROR,
            tool_name=tool_name,
            data={
                "error": str(error),
                "error_type": type(error).__name__
            },
            timestamp=time.time()
        )
        self._events.append(event)

        # Immediately emit via callback for real-time streaming
        if self._event_callback:
            self._event_callback(event)

        logger.debug(f"Emitted tool error event: {tool_name}")

    async def emit_complete(self, tool_name: str, data: dict[str, Any] | None = None) -> None:
        """Emit tool completion event - immediately via callback."""
        if not self._is_active:
            return

        event = ToolStreamEvent(
            event_type=ToolEventType.TOOL_COMPLETE,
            tool_name=tool_name,
            data=data or {},
            timestamp=time.time()
        )
        self._events.append(event)

        # Immediately emit via callback for real-time streaming
        if self._event_callback:
            self._event_callback(event)

        logger.debug(f"Emitted tool complete event: {tool_name}")

    def get_pending_events(self) -> List[ToolStreamEvent]:
        """
        Get all pending events and clear the list.

        This allows the runner to periodically check for new events
        and yield them in the agent stream.

        Returns:
            List of events collected since last call
        """
        events = self._events.copy()
        self._events.clear()
        return events

    def deactivate(self) -> None:
        """Deactivate context - stops accepting events."""
        self._is_active = False

    def is_active(self) -> bool:
        """Check if context is active."""
        return self._is_active
