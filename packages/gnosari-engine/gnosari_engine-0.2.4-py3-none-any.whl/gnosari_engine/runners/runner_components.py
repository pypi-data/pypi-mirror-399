"""
Runner components following Single Responsibility Principle.
Extracted from GnosariRunner for better separation of concerns.
"""

import logging
from typing import Any

from .interfaces import ProviderStrategy, StreamEvent
from .factories.interfaces import IProviderFactory
from .factories.provider_factory import create_default_provider_factory

logger = logging.getLogger(__name__)


class RunnerConfigurationError(Exception):
    """Configuration validation errors."""
    pass


class RunnerConfiguration:
    """
    Immutable configuration class for runner initialization.
    Follows Single Responsibility Principle for configuration validation.
    """
    
    def __init__(
        self,
        provider_name: str | None = None,
        provider: ProviderStrategy | None = None,
        provider_factory: IProviderFactory | None = None,
        **provider_config
    ):
        self.provider_name = provider_name
        self.provider = provider
        self.provider_factory = provider_factory or create_default_provider_factory()
        self.provider_config = provider_config
        
        self._validate()
    
    def _validate(self) -> None:
        """Validate configuration parameters."""
        if self.provider is None and self.provider_name is None:
            raise RunnerConfigurationError(
                "Must provide either 'provider_name' or 'provider' instance"
            )
        
        if self.provider is not None and self.provider_name is not None:
            logger.warning(
                "Both provider instance and provider_name provided. "
                "Using provider instance, ignoring provider_name."
            )


class RunnerInitializer:
    """
    Handles runner initialization logic following Single Responsibility Principle.
    Separates initialization concerns from the main runner class.
    """
    
    def __init__(self, config: RunnerConfiguration):
        self._config = config
        self._provider: ProviderStrategy | None = None
        self._provider_name: str | None = None
        self._is_initialized = False
    
    @property
    def provider(self) -> ProviderStrategy:
        """Get the initialized provider."""
        if self._provider is None:
            raise RuntimeError("Provider not initialized. Call initialize() first.")
        return self._provider
    
    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        if self._provider_name is None:
            raise RuntimeError("Provider not initialized. Call initialize() first.")
        return self._provider_name
    
    @property
    def is_initialized(self) -> bool:
        """Check if initialization is complete."""
        return self._is_initialized
    
    async def initialize(self) -> None:
        """
        Initialize provider based on configuration.
        Follows Single Responsibility Principle.
        """
        if self._is_initialized:
            return
        
        try:
            if self._config.provider is not None:
                # Direct provider injection (Dependency Injection)
                self._provider = self._config.provider
                self._provider_name = self._provider.provider_name
            else:
                # Factory-based provider creation (Open/Closed Principle)
                self._provider = self._config.provider_factory.create_provider(
                    self._config.provider_name
                )
                self._provider_name = self._config.provider_name
            
            # Initialize the provider with configuration
            await self._provider.initialize(**self._config.provider_config)
            self._is_initialized = True
            
            logger.info(f"Provider '{self._provider_name}' initialized successfully")
            
        except Exception as e:
            self._cleanup_on_error()
            raise RuntimeError(
                f"Failed to initialize provider '{self._config.provider_name}': {e}"
            ) from e
    
    async def cleanup(self) -> None:
        """Cleanup initialized resources."""
        if self._is_initialized and self._provider:
            try:
                await self._provider.cleanup()
                logger.info(f"Provider '{self._provider_name}' cleaned up successfully")
            except Exception as e:
                logger.error(f"Error during provider cleanup: {e}")
            finally:
                self._cleanup_on_error()
    
    def _cleanup_on_error(self) -> None:
        """Reset state on error."""
        self._provider = None
        self._provider_name = None
        self._is_initialized = False


class ProviderContextEnricher:
    """
    Handles stream event enrichment following Single Responsibility Principle.
    Separates event enrichment concerns from the main runner logic.
    """
    
    def __init__(self, provider_name: str):
        self._provider_name = provider_name
    
    def enrich_event(self, event: StreamEvent) -> StreamEvent:
        """
        Enrich stream event with provider context.
        Follows Single Responsibility Principle - only handles event enrichment.
        """
        # Handle different data types properly
        if hasattr(event.data, 'provider'):
            # If data has a provider attribute, check if it's set
            if not getattr(event.data, 'provider', None) or getattr(event.data, 'provider') == "unknown":
                event.data.provider = self._provider_name
        elif isinstance(event.data, dict):
            # If data is a dictionary, use dictionary operations
            if "provider" not in event.data:
                event.data["provider"] = self._provider_name
        return event
    
    def create_error_event(self, error: Exception) -> StreamEvent:
        """Create standardized error event with provider context."""
        return StreamEvent(
            "execution_error", 
            {
                "error": str(error), 
                "provider": self._provider_name,
                "error_type": type(error).__name__
            }
        )