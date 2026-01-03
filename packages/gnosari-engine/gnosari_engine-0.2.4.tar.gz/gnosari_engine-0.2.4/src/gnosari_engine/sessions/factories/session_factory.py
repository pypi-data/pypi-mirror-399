"""Session factory implementation following Open/Closed Principle."""

import logging
from typing import Optional, Dict, Type, Callable

from .interfaces import ISessionFactory
from ..interfaces import ISessionProvider
from ..providers.openai.database import OpenAIDatabaseSessionProvider
from ..providers.claude.database import ClaudeDatabaseSessionProvider
from ..events.factory import SessionProviderWithEventsFactory
from ...schemas.domain.execution import AgentRun

logger = logging.getLogger(__name__)


class SessionFactory(ISessionFactory):
    """
    Factory for creating session providers following Open/Closed Principle.
    
    Open for extension: New providers can be registered without modifying existing code.
    Closed for modification: Core factory logic remains unchanged when adding providers.
    
    Follows Single Responsibility Principle: Only responsible for creating session providers.
    """
    
    def __init__(self):
        """Initialize factory with default providers."""
        logger.debug("Initializing SessionFactory with default providers")
        
        self._providers: Dict[str, Type[ISessionProvider]] = {
            "openai_database": OpenAIDatabaseSessionProvider,
            "claude_database": ClaudeDatabaseSessionProvider,
            # Future providers can be easily added here:
            # "anthropic_api": AnthropicAPISessionProvider,
            # "openai_redis": OpenAIRedisSessionProvider,
            # "memory": MemorySessionProvider,
        }
        
        # Factory functions for providers that need special initialization
        self._factory_functions: Dict[str, Callable] = {
            "openai_database_with_events": SessionProviderWithEventsFactory.create_openai_database_provider_with_events,
        }
        
        logger.debug(f"SessionFactory initialized with {len(self._providers)} providers: {list(self._providers.keys())}")
        logger.debug(f"SessionFactory initialized with {len(self._factory_functions)} factory functions: {list(self._factory_functions.keys())}")
    
    def register_provider(
        self, 
        provider_name: str, 
        provider_class: Type[ISessionProvider]
    ) -> None:
        """
        Register a new session provider.
        
        Enables Open/Closed Principle: Extend functionality without modifying existing code.
        
        Args:
            provider_name: Unique name for the provider
            provider_class: Provider class that implements ISessionProvider
        """
        if not hasattr(provider_class, '__annotations__'):
            # Basic duck-typing check for provider interface
            required_methods = ['provider_name', 'session_type', 'is_initialized', 'initialize', 'cleanup', 'get_session_implementation']
            missing_methods = [method for method in required_methods if not hasattr(provider_class, method)]
            if missing_methods:
                raise ValueError(f"Provider class missing required methods: {missing_methods}")
        
        self._providers[provider_name] = provider_class
    
    def register_factory_function(
        self,
        provider_name: str,
        factory_function: Callable[[str, Optional[AgentRun]], ISessionProvider]
    ) -> None:
        """
        Register a factory function for providers that need custom initialization.
        
        Args:
            provider_name: Unique name for the provider
            factory_function: Function that creates provider instances
        """
        self._factory_functions[provider_name] = factory_function
    
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
        logger.debug(f"Creating session provider '{provider_name}' for session {session_id}")
        
        if provider_name not in self._providers and provider_name not in self._factory_functions:
            available_providers = list(self._providers.keys()) + list(self._factory_functions.keys())
            logger.error(f"Unknown session provider: {provider_name}. Available: {available_providers}")
            raise ValueError(
                f"Unknown session provider: {provider_name}. "
                f"Available providers: {available_providers}"
            )
        
        try:
            # Use factory function if available (for special initialization)
            if provider_name in self._factory_functions:
                logger.debug(f"Using factory function for provider '{provider_name}'")
                factory_function = self._factory_functions[provider_name]
                provider = factory_function(session_id=session_id, agent_run=agent_run, **config)
            else:
                # Use standard class instantiation
                logger.debug(f"Using class instantiation for provider '{provider_name}'")
                provider_class = self._providers[provider_name]
                provider = provider_class(
                    session_id=session_id,
                    agent_run=agent_run
                )
            
            logger.debug(f"Successfully created provider '{provider_name}' for session {session_id}")
            return provider
            
        except Exception as e:
            logger.error(f"Failed to create provider '{provider_name}' for session {session_id}: {e}")
            raise
    
    def get_available_providers(self) -> Dict[str, str]:
        """
        Get list of available providers with their descriptions.
        
        Returns:
            Dictionary mapping provider names to their session types
        """
        providers = {}
        
        # Get from registered classes
        for name, provider_class in self._providers.items():
            try:
                # Try to get session type from class if it's a property
                if hasattr(provider_class, 'session_type'):
                    session_type = provider_class.session_type
                else:
                    # Create temporary instance to get session type
                    temp_instance = provider_class("temp", None)
                    session_type = temp_instance.session_type
                
                providers[name] = session_type
            except Exception:
                providers[name] = "Unknown"
        
        # Add factory functions
        for name in self._factory_functions.keys():
            providers[name] = "Custom"
        
        return providers
    
    def is_provider_available(self, provider_name: str) -> bool:
        """
        Check if a provider is available.
        
        Args:
            provider_name: Name of the provider to check
            
        Returns:
            True if provider is available, False otherwise
        """
        return provider_name in self._providers or provider_name in self._factory_functions


__all__ = ["SessionFactory"]