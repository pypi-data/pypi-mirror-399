"""
Tool streaming module for Gnosari Engine.

Provides ultra-clean streaming capabilities for tools following SOLID principles.
Uses global registry pattern for maximum simplicity and reliability.
"""

from .interfaces import (
    BaseStreamableTool,
    IStreamableTool,
    IToolStreamContext,
    ToolEventType,
    ToolStreamEvent,
)
from .mixins import (
    ProgressTracker,
    StreamableToolMixin,
    with_streaming_events,
)
from .registry import StreamContextRegistry
from .sync_context import SyncToolStreamContext

__all__ = [
    # Interfaces
    "BaseStreamableTool",
    "IStreamableTool",
    "IToolStreamContext",
    "ToolEventType",
    "ToolStreamEvent",

    # Context implementations (ULTRA-CLEAN)
    "SyncToolStreamContext",

    # Mixins and utilities
    "ProgressTracker",
    "StreamableToolMixin",
    "with_streaming_events",

    # Registry (SINGLE SOURCE OF TRUTH)
    "StreamContextRegistry",
]
