"""
Session event publishing interfaces.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List

from ...schemas.domain.execution import AgentRunMetadata


class ISessionEventPublisher(ABC):
    """Interface for publishing session-related events."""
    
    @abstractmethod
    async def publish_messages_added(
        self, 
        session_id: str, 
        message_count: int,
        messages_data: List[str],
        metadata: Optional[AgentRunMetadata] = None
    ) -> None:
        """
        Publish event when messages are added to a session.
        
        Args:
            session_id: The session identifier
            message_count: Number of messages added
            messages_data: Serialized message data
            metadata: Optional agent run metadata for context
        """
        pass
    
    @abstractmethod
    async def publish_session_created(
        self, 
        session_id: str,
        metadata: Optional[AgentRunMetadata] = None
    ) -> None:
        """
        Publish event when a new session is created.
        
        Args:
            session_id: The session identifier
            metadata: Optional agent run metadata for context
        """
        pass
    
    @abstractmethod
    async def publish_session_cleared(
        self, 
        session_id: str,
        metadata: Optional[AgentRunMetadata] = None
    ) -> None:
        """
        Publish event when a session is cleared.
        
        Args:
            session_id: The session identifier
            metadata: Optional agent run metadata for context
        """
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up publisher resources."""
        pass


class INullSessionEventPublisher(ISessionEventPublisher):
    """Null object pattern for when event publishing is disabled."""
    
    async def publish_messages_added(
        self, 
        session_id: str, 
        message_count: int,
        messages_data: List[str],
        metadata: Optional[AgentRunMetadata] = None
    ) -> None:
        """No-op implementation."""
        pass
    
    async def publish_session_created(
        self, 
        session_id: str,
        metadata: Optional[AgentRunMetadata] = None
    ) -> None:
        """No-op implementation."""
        pass
    
    async def publish_session_cleared(
        self, 
        session_id: str,
        metadata: Optional[AgentRunMetadata] = None
    ) -> None:
        """No-op implementation."""
        pass
    
    async def cleanup(self) -> None:
        """No-op implementation."""
        pass


class NullSessionEventPublisher(INullSessionEventPublisher):
    """Concrete null object implementation."""
    pass