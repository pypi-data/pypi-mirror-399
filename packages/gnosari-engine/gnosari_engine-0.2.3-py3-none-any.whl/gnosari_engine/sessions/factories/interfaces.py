"""Factory interfaces for session providers."""

from typing import Optional, Protocol

from ..interfaces import ISessionProvider
from ...schemas.domain.execution import AgentRun


class ISessionFactory(Protocol):
    """
    Factory interface for creating session providers.
    
    Follows Open/Closed Principle: Open for extension (new providers),
    closed for modification (core factory interface).
    """
    
    def create_provider(
        self, 
        provider_name: str, 
        session_id: str,
        agent_run: Optional[AgentRun] = None,
        **config
    ) -> ISessionProvider:
        """
        Create session provider by name.
        
        Args:
            provider_name: Name of the provider to create
            session_id: Unique session identifier
            agent_run: Optional AgentRun with team/agent info and metadata
            **config: Provider-specific configuration
            
        Returns:
            Configured session provider instance
            
        Raises:
            ValueError: If provider_name is unknown
        """
        ...


__all__ = ["ISessionFactory"]