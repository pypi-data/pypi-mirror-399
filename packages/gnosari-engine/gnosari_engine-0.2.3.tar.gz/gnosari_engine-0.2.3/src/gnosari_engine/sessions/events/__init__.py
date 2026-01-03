"""
Session event publishing system.
"""

from .interfaces import ISessionEventPublisher, NullSessionEventPublisher
from .models import (
    SessionEventBase,
    MessagesAddedEvent, 
    SessionCreatedEvent, 
    SessionClearedEvent
)
# Import factory lazily to avoid circular imports

try:
    from .redis_publisher import RedisSessionEventPublisher
    REDIS_PUBLISHER_AVAILABLE = True
except ImportError:
    REDIS_PUBLISHER_AVAILABLE = False
    RedisSessionEventPublisher = None


def create_event_publisher(
    publisher_type: str = "null",
    **kwargs
) -> ISessionEventPublisher:
    """
    Factory function to create event publishers.
    
    Args:
        publisher_type: Type of publisher ("redis" or "null")
        **kwargs: Publisher-specific configuration
        
    Returns:
        Configured event publisher instance
        
    Raises:
        ValueError: If publisher type is unknown or unavailable
    """
    if publisher_type == "null":
        return NullSessionEventPublisher()
    
    elif publisher_type == "redis":
        if not REDIS_PUBLISHER_AVAILABLE:
            raise ImportError(
                "Redis publisher is not available. Install with: pip install redis"
            )
        return RedisSessionEventPublisher(**kwargs)
    
    else:
        raise ValueError(f"Unknown publisher type: {publisher_type}")


__all__ = [
    "ISessionEventPublisher",
    "NullSessionEventPublisher", 
    "SessionEventBase",
    "MessagesAddedEvent",
    "SessionCreatedEvent", 
    "SessionClearedEvent",
    "create_event_publisher",
    "REDIS_PUBLISHER_AVAILABLE",
]

if REDIS_PUBLISHER_AVAILABLE:
    __all__.append("RedisSessionEventPublisher")