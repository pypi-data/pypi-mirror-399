"""Provider-agnostic session orchestrator using Strategy Pattern."""

import logging
from typing import TypeVar, Generic, Any, Optional

from .interfaces import ISessionProvider, ISessionFactory
from .components import SessionConfiguration, SessionInitializer
from ..schemas.domain.execution import AgentRun

logger = logging.getLogger(__name__)

T = TypeVar('T')  # Generic session type


class GnosariSession(Generic[T]):
    """
    Provider-agnostic session orchestrator using Strategy Pattern.
    
    The session provider determines what type of session implementation
    is returned. No framework-specific methods needed.
    
    Follows SOLID principles:
    - Single Responsibility: Only orchestrates session lifecycle
    - Open/Closed: Open for new providers, closed for modification
    - Liskov Substitution: All providers are interchangeable
    - Interface Segregation: Depends only on ISessionProvider
    - Dependency Inversion: Depends on abstractions, not concrete implementations
    """
    
    def __init__(
        self,
        session_id: str,
        provider_name: str,
        agent_run: AgentRun,
        provider: Optional[ISessionProvider] = None,
        session_factory: Optional[ISessionFactory] = None,
        **provider_config
    ):
        """
        Initialize session orchestrator.
        
        Args:
            session_id: Unique session identifier
            provider_name: Name of the session provider to use
            agent_run: Optional AgentRun with execution context
            provider: Optional pre-configured provider instance
            session_factory: Optional factory for creating providers
            **provider_config: Provider-specific configuration parameters
        """
        # Strict validation - agent_run is required
        if agent_run is None:
            raise ValueError("agent_run parameter cannot be None. GnosariSession requires a valid AgentRun context.")
        if not hasattr(agent_run, 'metadata') or agent_run.metadata is None:
            raise ValueError("agent_run.metadata cannot be None. AgentRun must have valid metadata.")
        if not agent_run.metadata.session_id:
            raise ValueError("agent_run.metadata.session_id cannot be empty. AgentRun metadata must have a valid session_id.")
            
        logger.info(f"Creating GnosariSession: session_id={session_id}, provider_name={provider_name}")
        logger.debug(f"AgentRun context provided: agent_id={agent_run.agent.id}, team_id={agent_run.team.id}")
        
        config = SessionConfiguration(
            provider_name=provider_name,
            agent_run=agent_run,
            provider=provider,
            **provider_config
        )
        
        self._initializer = SessionInitializer(config)
        self._session_factory = session_factory
        
        # Store original context for runtime provider switching
        self._original_context = agent_run
        
        logger.debug(f"GnosariSession created successfully for session {session_id}")
    
    
    @property
    def agent_run(self) -> AgentRun:
        """Get the agent run context."""
        if self._original_context is None:
            raise RuntimeError("AgentRun context is None. This indicates a serious programming error.")
        return self._original_context
    
    @property
    def is_initialized(self) -> bool:
        """Check if session is initialized."""
        return self._initializer.is_initialized
    
    @property
    def provider_name(self) -> Optional[str]:
        """Get current provider name."""
        if self._initializer.provider is not None:
            return self._initializer.provider.provider_name
        return None
    
    @property
    def session_type(self) -> Optional[str]:
        """Get current session type."""
        if self._initializer.provider is not None:
            return self._initializer.provider.session_type
        return None
    
    @property
    def session_context(self) -> AgentRun:
        """Get current execution context."""
        return self.agent_run  # Use the validated property
    
    async def get_session(self) -> T:
        """
        Get session implementation from the configured provider.
        
        Returns:
            Session implementation specific to the provider:
            - OpenAI providers return SessionABC
            - Anthropic providers return AnthropicSessionInterface  
            - Custom providers return their own session type
        """
        logger.debug(f"Getting session implementation for session {self.agent_run.metadata.session_id}")
        
        await self._ensure_initialized()
        
        if self._initializer.provider is None:
            logger.error(f"Provider not available after initialization for session {self.agent_run.metadata.session_id}")
            raise RuntimeError("Provider not available after initialization")
        
        session_impl = self._initializer.provider.get_session_implementation()
        logger.debug(f"Retrieved session implementation of type {type(session_impl).__name__} for session {self.agent_run.metadata.session_id}")
        return session_impl
    
    async def switch_provider(
        self, 
        provider_name: str, 
        agent_run: Optional[AgentRun] = None,
        **config
    ) -> None:
        """
        Switch to different provider at runtime.
        
        Follows Open/Closed Principle: Can switch to any provider that
        implements ISessionProvider without modifying core logic.
        
        Args:
            provider_name: Name of the new provider
            agent_run: Optional new AgentRun context
            **config: Provider-specific configuration
        """
        logger.info(f"Switching provider for session {self.agent_run.metadata.session_id} from '{self.provider_name}' to '{provider_name}'")
        
        try:
            # Clean up current provider
            logger.debug(f"Cleaning up current provider for session {self.agent_run.metadata.session_id}")
            await self._initializer.cleanup()
            
            # Use provided context or fallback to original
            effective_context = agent_run or self._original_context
            
            if effective_context:
                logger.debug(f"Using AgentRun context for provider switch: agent_id={effective_context.agent.id}, team_id={effective_context.team.id}")
            
            # Create new configuration
            new_config = SessionConfiguration(
                provider_name=provider_name,
                agent_run=effective_context,
                **config
            )
            
            # Reinitialize with new configuration
            self._initializer = SessionInitializer(new_config)
            
            # Initialize new provider
            logger.debug(f"Initializing new provider '{provider_name}' for session {self.agent_run.metadata.session_id}")
            await self._initializer.initialize(session_factory=self._session_factory)
            
            logger.info(f"Provider switch completed successfully for session {self.agent_run.metadata.session_id}: now using '{provider_name}'")
            
        except Exception as e:
            logger.error(f"Failed to switch provider for session {self.agent_run.metadata.session_id}: {e}")
            raise
    
    async def cleanup(self) -> None:
        """Clean up session resources."""
        logger.debug(f"Cleaning up GnosariSession for session {self.agent_run.metadata.session_id}")
        await self._initializer.cleanup()
        logger.debug(f"GnosariSession cleanup completed for session {self.agent_run.metadata.session_id}")
    
    async def _ensure_initialized(self) -> None:
        """Ensure session is initialized before use."""
        if not self._initializer.is_initialized:
            logger.debug(f"Initializing session {self.agent_run.metadata.session_id}")
            await self._initializer.initialize(session_factory=self._session_factory)
        else:
            logger.debug(f"Session {self.agent_run.metadata.session_id} already initialized")
    
    # Context manager support for proper resource cleanup
    async def __aenter__(self) -> "GnosariSession[T]":
        """Async context manager entry."""
        logger.debug(f"Entering GnosariSession context manager for session {self.agent_run.metadata.session_id}")
        await self._ensure_initialized()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        logger.debug(f"Exiting GnosariSession context manager for session {self.agent_run.metadata.session_id}")
        await self.cleanup()


__all__ = ["GnosariSession"]