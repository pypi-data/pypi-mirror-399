"""
Global stream context registry for ultra-clean tool streaming.

This provides a simple, thread-safe way for tools to access stream contexts
without complex injection mechanisms.

Following SOLID principles:
- Single Responsibility: Only manages stream context lookup
- Open/Closed: Can be extended with different storage backends
- Dependency Inversion: Tools depend on this abstraction, not concrete implementations
"""

import threading
from typing import Dict, Optional
import logging

from .interfaces import IToolStreamContext

logger = logging.getLogger(__name__)


class StreamContextRegistry:
    """
    Global registry for stream contexts indexed by session ID.

    This is the SINGLE SOURCE OF TRUTH for tool stream contexts.
    Tools simply look up their context by session ID when they need it.

    Thread-safe implementation using locks.

    ULTRA-SIMPLE: Also supports a global "current" context for when
    session ID is not available during tool initialization.
    """

    _lock = threading.RLock()
    _contexts: Dict[str, IToolStreamContext] = {}
    _current_context: Optional[IToolStreamContext] = None  # Global current context

    @classmethod
    def register(cls, session_id: str, context: IToolStreamContext) -> None:
        """
        Register a stream context for a session.

        Also sets this as the current global context.

        Args:
            session_id: Unique session identifier
            context: Stream context to register
        """
        with cls._lock:
            cls._contexts[session_id] = context
            cls._current_context = context  # Set as current
            logger.debug(f"Registered stream context for session: {session_id} (also set as current)")

    @classmethod
    def get(cls, session_id: str) -> Optional[IToolStreamContext]:
        """
        Get stream context for a session.

        Args:
            session_id: Session identifier

        Returns:
            Stream context if registered, None otherwise
        """
        with cls._lock:
            return cls._contexts.get(session_id)

    @classmethod
    def get_current(cls) -> Optional[IToolStreamContext]:
        """
        Get the current global stream context.

        This is used when session ID is not available (e.g., during tool initialization).

        Returns:
            Current stream context if set, None otherwise
        """
        with cls._lock:
            return cls._current_context

    @classmethod
    def unregister(cls, session_id: str) -> None:
        """
        Unregister stream context for a session.

        Also clears current context if it matches.

        Args:
            session_id: Session identifier to unregister
        """
        with cls._lock:
            if session_id in cls._contexts:
                context = cls._contexts.pop(session_id)
                # Clear current if it was this context
                if cls._current_context is context:
                    cls._current_context = None
                logger.debug(f"Unregistered stream context for session: {session_id}")

    @classmethod
    def has_context(cls, session_id: str) -> bool:
        """
        Check if context exists for session.

        Args:
            session_id: Session identifier

        Returns:
            True if context is registered, False otherwise
        """
        with cls._lock:
            return session_id in cls._contexts

    @classmethod
    def clear_all(cls) -> None:
        """Clear all registered contexts (for testing/cleanup)."""
        with cls._lock:
            cls._contexts.clear()
            logger.debug("Cleared all stream contexts")

    @classmethod
    def get_active_sessions(cls) -> list[str]:
        """Get list of active session IDs with registered contexts."""
        with cls._lock:
            return list(cls._contexts.keys())
