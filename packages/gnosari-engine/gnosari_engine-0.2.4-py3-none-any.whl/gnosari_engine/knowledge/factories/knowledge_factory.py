"""
Knowledge provider factory following Open/Closed Principle.

Creates and configures knowledge providers based on team configuration
while remaining open for extension but closed for modification.
"""

import logging
from typing import Any

from ...schemas.domain.knowledge import Knowledge
from ..interfaces import IKnowledgeProvider


class KnowledgeProviderFactory:
    """
    Factory for creating knowledge providers following SOLID principles.
    
    Open for extension: New knowledge providers can be registered.
    Closed for modification: Core factory logic unchanged when adding providers.
    """

    def __init__(self):
        # Registry: provider_name -> provider_class
        self._registry: dict[str, type[IKnowledgeProvider]] = {}
        self._setup_default_providers()

    def _setup_default_providers(self) -> None:
        """Setup default knowledge providers."""
        try:
            # Register OpenSearch provider
            from ..providers.opensearch import OpenSearchKnowledgeProvider
            self._registry["opensearch"] = OpenSearchKnowledgeProvider
        except ImportError:
            logging.debug("OpenSearch provider not available")

    async def create_provider(
        self,
        provider_type: str,
        **config
    ) -> IKnowledgeProvider:
        """
        Create knowledge provider instance.

        Args:
            provider_type: Type of provider (currently only 'opensearch' is supported)
            **config: Additional configuration for the provider

        Returns:
            Uninitialized knowledge provider instance (call initialize() separately)

        Raises:
            ValueError: If provider type not supported
        """
        if provider_type not in self._registry:
            available_providers = list(self._registry.keys())
            raise ValueError(
                f"Knowledge provider '{provider_type}' not supported. "
                f"Available providers: {available_providers}"
            )

        provider_class = self._registry[provider_type]
        provider = provider_class()
        
        # Return uninitialized provider - caller handles initialization
        return provider

    def register_provider(
        self, 
        provider_name: str, 
        provider_class: type[IKnowledgeProvider]
    ) -> None:
        """Register a new knowledge provider class."""
        self._registry[provider_name] = provider_class

    def get_supported_providers(self) -> list[str]:
        """Get list of supported provider names."""
        return list(self._registry.keys())