"""
Provider factory implementation following extreme SOLID principles.
Handles provider creation and registration with clean separation of concerns.
"""

import logging
from typing import Any

from .interfaces import IProviderFactory
from ..interfaces import ProviderStrategy

logger = logging.getLogger(__name__)


class ProviderFactoryError(Exception):
    """Provider factory specific errors."""
    pass


class AutoDiscoveryProviderFactory(IProviderFactory):
    """
    Auto-discovery provider factory implementation.
    
    Follows SOLID Principles:
    - Single Responsibility: Only creates and manages provider instances
    - Open/Closed: Open for new providers via registration, closed for modification
    - Liskov Substitution: All providers implement ProviderStrategy protocol
    - Interface Segregation: Clean factory interface without unnecessary methods
    - Dependency Inversion: Depends on ProviderStrategy abstraction
    
    Usage:
        factory = AutoDiscoveryProviderFactory()
        factory.register_provider("openai", OpenAIProvider)
        provider = factory.create_provider("openai")
    """

    def __init__(self):
        """Initialize empty provider registry."""
        self._registry: dict[str, type[ProviderStrategy]] = {}
        logger.debug("AutoDiscoveryProviderFactory initialized")

    def create_provider(self, provider_name: str) -> ProviderStrategy:
        """
        Create provider strategy instance by name.

        Args:
            provider_name: Name of the provider to create

        Returns:
            ProviderStrategy instance ready for use

        Raises:
            ProviderFactoryError: If provider_name is unknown or creation fails
        """
        if not provider_name:
            raise ProviderFactoryError("Provider name cannot be empty")

        if provider_name not in self._registry:
            available = ", ".join(self._registry.keys()) if self._registry else "none"
            raise ProviderFactoryError(
                f"Unknown provider '{provider_name}'. Available providers: {available}"
            )

        try:
            provider_class = self._registry[provider_name]
            instance = provider_class()
            logger.info(f"Created provider instance: {provider_name}")
            return instance
        except Exception as e:
            raise ProviderFactoryError(
                f"Failed to create provider '{provider_name}': {e}"
            ) from e

    def register_provider(self, name: str, provider_class: type[ProviderStrategy]) -> None:
        """
        Register a new provider class.

        Args:
            name: Provider name identifier
            provider_class: Provider class that implements ProviderStrategy

        Raises:
            ProviderFactoryError: If name already registered or provider_class invalid
        """
        if not name:
            raise ProviderFactoryError("Provider name cannot be empty")

        if not provider_class:
            raise ProviderFactoryError("Provider class cannot be None")

        if name in self._registry:
            existing_class = self._registry[name].__name__
            new_class = provider_class.__name__
            raise ProviderFactoryError(
                f"Provider '{name}' already registered with class '{existing_class}'. "
                f"Cannot register with class '{new_class}'"
            )

        # Validate that provider_class implements the protocol
        required_methods = ['provider_name', 'initialize', 'cleanup', 'run_agent', 'run_agent_stream']
        for method in required_methods:
            if not hasattr(provider_class, method):
                raise ProviderFactoryError(
                    f"Provider class '{provider_class.__name__}' missing required method: {method}"
                )

        self._registry[name] = provider_class
        logger.info(f"Registered provider: {name} -> {provider_class.__name__}")

    def get_available_providers(self) -> list[str]:
        """
        Get list of all registered provider names.

        Returns:
            List of available provider names
        """
        return list(self._registry.keys())

    def unregister_provider(self, name: str) -> None:
        """
        Unregister a provider (useful for testing).

        Args:
            name: Provider name to unregister

        Raises:
            ProviderFactoryError: If provider not found
        """
        if name not in self._registry:
            raise ProviderFactoryError(f"Provider '{name}' not registered")

        del self._registry[name]
        logger.info(f"Unregistered provider: {name}")

    def clear_registry(self) -> None:
        """Clear all registered providers (useful for testing)."""
        self._registry.clear()
        logger.debug("Provider registry cleared")


def create_default_provider_factory() -> AutoDiscoveryProviderFactory:
    """
    Create a provider factory with default providers registered.
    Follows Factory Method pattern for consistent setup.
    
    Returns:
        AutoDiscoveryProviderFactory with standard providers registered
    """
    factory = AutoDiscoveryProviderFactory()
    
    # Register standard providers
    try:
        from ..provider.openai import OpenAIProvider
        factory.register_provider("openai", OpenAIProvider)
    except ImportError:
        logger.warning("OpenAI provider not available - skipping registration")
    
    try:
        from ..provider.claude import ClaudeProvider
        factory.register_provider("claude", ClaudeProvider)
    except ImportError:
        logger.warning("Claude provider not available - skipping registration")
    
    logger.info(f"Default provider factory created with {len(factory.get_available_providers())} providers")
    return factory