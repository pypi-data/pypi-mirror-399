"""
Factory for creating session providers with event publishers.
"""

import os
from typing import Optional

from .interfaces import ISessionEventPublisher, NullSessionEventPublisher
from ..providers.openai.database import OpenAIDatabaseSessionProvider
from ...schemas.domain.execution import AgentRun

# Import Redis publisher directly to avoid circular imports
try:
    from .redis_publisher import RedisSessionEventPublisher
    REDIS_PUBLISHER_AVAILABLE = True
except ImportError:
    REDIS_PUBLISHER_AVAILABLE = False
    RedisSessionEventPublisher = None


class SessionProviderWithEventsFactory:
    """
    Factory for creating session providers with integrated event publishing.
    
    Follows SOLID principles by using dependency injection for event publishers
    and following the factory pattern for clean instantiation.
    """
    
    @staticmethod
    def create_openai_database_provider_with_events(
        session_id: str,
        agent_run: Optional[AgentRun] = None,
        event_publisher_type: str = "redis",
        redis_url: Optional[str] = None,
        **kwargs
    ) -> OpenAIDatabaseSessionProvider:
        """
        Create OpenAI database session provider with event publishing.
        
        Args:
            session_id: Unique session identifier
            agent_run: Optional AgentRun with team/agent context and metadata
            event_publisher_type: Type of event publisher ("redis" or "null")
            redis_url: Optional Redis URL (uses environment or default if not provided)
            **kwargs: Additional configuration for the session provider
            
        Returns:
            Configured OpenAI database session provider with event publishing
        """
        # Create event publisher
        event_publisher = SessionProviderWithEventsFactory._create_event_publisher(
            publisher_type=event_publisher_type,
            redis_url=redis_url
        )
        
        # Create session provider with event publisher
        return OpenAIDatabaseSessionProvider(
            session_id=session_id,
            agent_run=agent_run,
            event_publisher=event_publisher
        )
    
    @staticmethod
    def _create_event_publisher(
        publisher_type: str = "redis",
        redis_url: Optional[str] = None
    ) -> ISessionEventPublisher:
        """
        Create event publisher based on configuration.
        
        Args:
            publisher_type: Type of publisher ("redis" or "null")
            redis_url: Optional Redis URL for Redis publisher
            
        Returns:
            Configured event publisher
        """
        if publisher_type == "redis" and REDIS_PUBLISHER_AVAILABLE:
            # Use Redis URL from parameter, environment, or default
            effective_redis_url = (
                redis_url or 
                os.getenv("GNOSARI_REDIS_URL") or 
                os.getenv("REDIS_URL") or 
                "redis://localhost:6379/0"
            )
            
            return RedisSessionEventPublisher(redis_url=effective_redis_url)
        else:
            # Fall back to null publisher if Redis is not available or not requested
            return NullSessionEventPublisher()
    
    @staticmethod
    def get_default_event_publisher_type() -> str:
        """
        Get the default event publisher type based on environment.
        
        Returns:
            "redis" if Redis is available and configured, "null" otherwise
        """
        if REDIS_PUBLISHER_AVAILABLE:
            # Check if Redis URL is configured
            redis_url = (
                os.getenv("GNOSARI_REDIS_URL") or 
                os.getenv("REDIS_URL")
            )
            if redis_url:
                return "redis"
        
        return "null"