"""
Provider registration system following Open/Closed Principle.
Allows registering new providers without modifying core code.
"""

import logging
from typing import Any

from .interfaces import IProviderFactory
from .provider_factory import AutoDiscoveryProviderFactory
from ..interfaces import ProviderStrategy

logger = logging.getLogger(__name__)


class ProviderRegistrationError(Exception):
    """Provider registration specific errors."""
    pass


class ProviderRegistrar:
    """
    Provider registration system following Open/Closed Principle.
    
    Allows external code to register new providers without modifying
    the core factory implementation. Follows Plugin Pattern.
    
    Usage:
        registrar = ProviderRegistrar()
        registrar.register_provider("custom", CustomProvider)
        factory = registrar.create_factory()
    """

    def __init__(self):
        """Initialize empty registrar."""
        self._pending_registrations: dict[str, type[ProviderStrategy]] = {}
        logger.debug("ProviderRegistrar initialized")

    def register_provider(self, name: str, provider_class: type[ProviderStrategy]) -> None:
        """
        Register a provider for future factory creation.
        
        Args:
            name: Provider name identifier
            provider_class: Provider class implementing ProviderStrategy
            
        Raises:
            ProviderRegistrationError: If registration fails
        """
        if not name:
            raise ProviderRegistrationError("Provider name cannot be empty")
            
        if not provider_class:
            raise ProviderRegistrationError("Provider class cannot be None")
            
        if name in self._pending_registrations:
            existing = self._pending_registrations[name].__name__
            new = provider_class.__name__
            raise ProviderRegistrationError(
                f"Provider '{name}' already registered with class '{existing}'. "
                f"Cannot register with class '{new}'"
            )
            
        self._pending_registrations[name] = provider_class
        logger.info(f"Pending registration: {name} -> {provider_class.__name__}")

    def create_factory(self) -> IProviderFactory:
        """
        Create factory with all registered providers.
        
        Returns:
            IProviderFactory with all providers registered
            
        Raises:
            ProviderRegistrationError: If factory creation fails
        """
        try:
            factory = AutoDiscoveryProviderFactory()
            
            for name, provider_class in self._pending_registrations.items():
                factory.register_provider(name, provider_class)
                
            logger.info(f"Created factory with {len(self._pending_registrations)} providers")
            return factory
            
        except Exception as e:
            raise ProviderRegistrationError(f"Failed to create factory: {e}") from e

    def get_pending_registrations(self) -> dict[str, str]:
        """
        Get pending provider registrations.
        
        Returns:
            Dict mapping provider names to class names
        """
        return {name: cls.__name__ for name, cls in self._pending_registrations.items()}

    def clear_pending(self) -> None:
        """Clear all pending registrations (useful for testing)."""
        self._pending_registrations.clear()
        logger.debug("Pending registrations cleared")


def setup_standard_providers(registrar: ProviderRegistrar) -> None:
    """
    Setup standard providers in registrar.
    Follows Plugin Pattern - external configuration of providers.
    
    Args:
        registrar: ProviderRegistrar to configure
        
    Raises:
        ProviderRegistrationError: If setup fails
    """
    # Register OpenAI provider if available
    try:
        from ..provider.openai import OpenAIProvider
        registrar.register_provider("openai", OpenAIProvider)
        logger.info("Registered OpenAI provider")
    except ImportError:
        logger.warning("OpenAI provider not available - skipping registration")
    
    # Future providers can be registered here without modifying core code
    # try:
    #     from ..provider.anthropic import AnthropicProvider
    #     registrar.register_provider("anthropic", AnthropicProvider)
    #     logger.info("Registered Anthropic provider")
    # except ImportError:
    #     logger.warning("Anthropic provider not available - skipping registration")
    #
    # try:
    #     from ..provider.deepseek import DeepSeekProvider
    #     registrar.register_provider("deepseek", DeepSeekProvider)
    #     logger.info("Registered DeepSeek provider") 
    # except ImportError:
    #     logger.warning("DeepSeek provider not available - skipping registration")


def create_configured_factory() -> IProviderFactory:
    """
    Create a fully configured provider factory.
    Follows Factory Method pattern with Plugin Pattern for extensibility.
    
    Returns:
        IProviderFactory configured with all available providers
    """
    registrar = ProviderRegistrar()
    setup_standard_providers(registrar)
    return registrar.create_factory()


def create_custom_factory(custom_setup: callable) -> IProviderFactory:
    """
    Create factory with custom provider setup.
    Allows external code to configure providers without modifying core code.
    
    Args:
        custom_setup: Function that takes ProviderRegistrar and configures it
        
    Returns:
        IProviderFactory configured by custom setup function
        
    Example:
        def my_setup(registrar):
            registrar.register_provider("custom", MyCustomProvider)
            
        factory = create_custom_factory(my_setup)
    """
    registrar = ProviderRegistrar()
    custom_setup(registrar)
    return registrar.create_factory()