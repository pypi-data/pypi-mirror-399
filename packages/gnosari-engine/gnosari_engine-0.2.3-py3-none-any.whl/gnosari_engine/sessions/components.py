"""Session components following Single Responsibility Principle."""

import logging
from typing import Optional

from .interfaces import ISessionProvider
from ..schemas.domain.execution import AgentRun

logger = logging.getLogger(__name__)


class SessionConfiguration:
    """
    Immutable configuration for session initialization.
    
    Follows Single Responsibility Principle: Only responsible for validating 
    and storing session configuration data.
    """
    
    def __init__(
        self,
        provider_name: str,
        agent_run: Optional[AgentRun] = None,
        provider: Optional[ISessionProvider] = None,
        **provider_config
    ):
        """
        Initialize session configuration.
        
        Args:
            provider_name: Name of the session provider to use
            agent_run: Optional AgentRun with execution context
            provider: Optional pre-configured provider instance
            **provider_config: Provider-specific configuration parameters
        """
        session_id = agent_run.metadata.session_id if agent_run else "unknown"
        logger.debug(f"Creating SessionConfiguration: session_id={session_id}, provider_name={provider_name}")
        
        self.session_id = session_id
        self.provider_name = provider_name
        self.agent_run = agent_run
        self.provider = provider
        self.provider_config = provider_config
        
        if agent_run:
            logger.debug(f"AgentRun provided: agent_id={agent_run.agent.id}, team_id={agent_run.team.id}")
        
        if provider_config:
            # Log config keys but not values for security
            config_keys = list(provider_config.keys())
            logger.debug(f"Provider config keys: {config_keys}")
        
        self._validate()
        logger.debug(f"SessionConfiguration created successfully for session {session_id}")
    
    def _validate(self) -> None:
        """Validate configuration parameters."""
        logger.debug(f"Validating SessionConfiguration for session {self.session_id}")
        
        if not self.session_id or not isinstance(self.session_id, str):
            logger.error(f"Invalid session_id: {self.session_id}")
            raise ValueError("session_id must be a non-empty string")
        
        if not self.provider_name or not isinstance(self.provider_name, str):
            logger.error(f"Invalid provider_name: {self.provider_name}")
            raise ValueError("provider_name must be a non-empty string")
        
        if self.agent_run is not None and not isinstance(self.agent_run, AgentRun):
            logger.error(f"Invalid agent_run type: {type(self.agent_run)}")
            raise ValueError("agent_run must be an AgentRun instance")
        
        logger.debug(f"SessionConfiguration validation passed for session {self.session_id}")


class SessionInitializer:
    """
    Handles session provider initialization following Single Responsibility Principle.
    
    Responsible only for managing the lifecycle of session providers.
    """
    
    def __init__(self, config: SessionConfiguration):
        """
        Initialize with configuration.
        
        Args:
            config: Validated session configuration
        """
        logger.debug(f"Creating SessionInitializer for session {config.session_id}")
        self._config = config
        self._provider: Optional[ISessionProvider] = None
        self._is_initialized = False
        logger.debug(f"SessionInitializer created for session {config.session_id}")
    
    @property
    def provider(self) -> Optional[ISessionProvider]:
        """Get the initialized provider."""
        return self._provider
    
    @property
    def is_initialized(self) -> bool:
        """Check if initialization is complete."""
        return self._is_initialized
    
    async def initialize(self, session_factory=None) -> None:
        """
        Initialize provider based on configuration.
        
        Args:
            session_factory: Optional session factory for creating providers
        """
        logger.debug(f"Initializing SessionInitializer for session {self._config.session_id}")
        
        if self._is_initialized:
            logger.debug(f"SessionInitializer already initialized for session {self._config.session_id}")
            return
        
        try:
            # Use pre-configured provider if available
            if self._config.provider is not None:
                logger.debug(f"Using pre-configured provider for session {self._config.session_id}")
                self._provider = self._config.provider
            else:
                # Create provider using factory
                if session_factory is None:
                    logger.debug(f"Creating default SessionFactory for session {self._config.session_id}")
                    from .factories.session_factory import SessionFactory
                    session_factory = SessionFactory()
                
                logger.debug(f"Creating provider '{self._config.provider_name}' for session {self._config.session_id}")
                self._provider = session_factory.create_provider(
                    provider_name=self._config.provider_name,
                    session_id=self._config.session_id,
                    agent_run=self._config.agent_run
                )
            
            # Initialize the provider with configuration
            logger.debug(f"Initializing provider '{self._config.provider_name}' for session {self._config.session_id}")
            await self._provider.initialize(**self._config.provider_config)
            self._is_initialized = True
            
            logger.info(f"SessionInitializer successfully initialized for session {self._config.session_id} with provider '{self._config.provider_name}'")
            
        except Exception as e:
            logger.error(f"Failed to initialize SessionInitializer for session {self._config.session_id}: {e}")
            raise
    
    async def cleanup(self) -> None:
        """Clean up provider resources."""
        logger.debug(f"Cleaning up SessionInitializer for session {self._config.session_id}")
        
        if self._provider is not None:
            try:
                logger.debug(f"Cleaning up provider '{self._config.provider_name}' for session {self._config.session_id}")
                await self._provider.cleanup()
                logger.debug(f"Provider cleanup completed for session {self._config.session_id}")
            except Exception as e:
                logger.error(f"Error during provider cleanup for session {self._config.session_id}: {e}")
                # Continue with cleanup even if provider cleanup fails
        
        self._provider = None
        self._is_initialized = False
        logger.debug(f"SessionInitializer cleanup completed for session {self._config.session_id}")


__all__ = ["SessionConfiguration", "SessionInitializer"]