"""Session provider interfaces following SOLID principles."""

import logging
from typing import Any, Optional, Protocol, TypeVar, runtime_checkable

from ..schemas.session import SessionContext

logger = logging.getLogger(__name__)

T = TypeVar('T')  # Generic session implementation type


@runtime_checkable
class ISessionProvider(Protocol):
    """
    Base protocol for all session providers using Strategy Pattern.
    
    Each provider strategy knows how to create its specific session type:
    - OpenAI providers create SessionABC implementations
    - Anthropic providers create AnthropicSessionInterface implementations
    - Custom providers create their own session types
    
    Follows Single Responsibility Principle: Only responsible for creating and managing
    one specific type of session implementation.
    """
    
    @property
    def provider_name(self) -> str:
        """Get the provider name (e.g., 'openai_database', 'anthropic_api')."""
        ...
    
    @property
    def session_type(self) -> str:
        """Get the session type this provider creates (e.g., 'SessionABC', 'AnthropicSession')."""
        ...
    
    @property
    def is_initialized(self) -> bool:
        """Check if provider is initialized."""
        ...
    
    async def initialize(self, **config) -> None:
        """
        Initialize the provider with configuration.
        
        Args:
            **config: Provider-specific configuration parameters
        """
        ...
    
    async def cleanup(self) -> None:
        """Cleanup provider resources."""
        ...
    
    def get_session_implementation(self) -> Any:
        """
        Return the session implementation for this provider.
        
        Type is determined by the concrete provider:
        - OpenAI providers return SessionABC
        - Anthropic providers return AnthropicSessionInterface
        - Custom providers return their session type
        
        Returns:
            The concrete session implementation specific to this provider
        """
        ...


@runtime_checkable
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
        session_context: Optional[SessionContext] = None,
        **config
    ) -> ISessionProvider:
        """
        Create session provider by name.
        
        Args:
            provider_name: Name of the provider to create
            session_id: Unique session identifier
            session_context: Optional session context with team/agent info
            **config: Provider-specific configuration
            
        Returns:
            Configured session provider instance
            
        Raises:
            ValueError: If provider_name is unknown
        """
        ...




__all__ = ["ISessionProvider", "ISessionFactory"]