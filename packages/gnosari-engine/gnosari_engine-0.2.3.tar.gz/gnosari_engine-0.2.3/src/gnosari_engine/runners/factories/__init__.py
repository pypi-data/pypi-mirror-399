"""
Runner-specific factory module following extreme SOLID principles.
Contains factories for providers, stream processors, and related components.
"""

from .interfaces import IProviderFactory, IStreamResultProcessor
from .provider_factory import AutoDiscoveryProviderFactory, create_default_provider_factory
from .provider_registry import (
    ProviderRegistrar,
    setup_standard_providers,
    create_configured_factory,
    create_custom_factory,
)
from .stream_processor import (
    DefaultStreamResultProcessor,
    VerboseStreamResultProcessor,
    create_default_stream_processor,
    create_verbose_stream_processor,
)

__all__ = [
    # Interfaces
    "IProviderFactory",
    "IStreamResultProcessor",
    
    # Provider factories
    "AutoDiscoveryProviderFactory",
    "ProviderRegistrar",
    
    # Stream processors
    "DefaultStreamResultProcessor",
    "VerboseStreamResultProcessor",
    
    # Factory functions
    "create_default_provider_factory",
    "setup_standard_providers",
    "create_configured_factory", 
    "create_custom_factory",
    "create_default_stream_processor",
    "create_verbose_stream_processor",
]