"""
Knowledge management module for Gnosari Engine.

This module provides a SOLID-based architecture for knowledge management with support for
multiple providers (OpenSearch, Embedchain) and data loaders (website, sitemap, files).

The architecture follows SOLID principles:
- Single Responsibility: Each component has one clear purpose
- Open/Closed: Easy to add new providers and loaders without modification
- Liskov Substitution: All providers are interchangeable through interfaces  
- Interface Segregation: Focused interfaces for specific operations
- Dependency Inversion: Depends on abstractions, not concretions

Main components:
- IKnowledgeProvider: Provider interface for different knowledge backends
- IKnowledgeBase: Interface for knowledge base operations
- IKnowledgeLoader: Interface for data source loaders
- IKnowledgeFactory: Factory for creating providers
"""

from .components import (
    Document,
    KnowledgeQueryResult,
    KnowledgeStatus,
    LoadingProgress,
)
from .interfaces import (
    IKnowledgeProvider,
    IKnowledgeBase,
    IKnowledgeLoader,
    IKnowledgeFactory,
)
from .providers import (
    OpenSearchKnowledgeProvider,
    OpenSearchKnowledgeBase,
)
from .loaders import (
    WebsiteLoader,
    SitemapLoader,
    SitemapParser,
    SitemapDiscovery,
    FileLoader,
    LoaderFactory,
)

__all__ = [
    # Components
    "Document",
    "KnowledgeQueryResult", 
    "KnowledgeStatus",
    "LoadingProgress",
    # Interfaces
    "IKnowledgeProvider",
    "IKnowledgeBase",
    "IKnowledgeLoader", 
    "IKnowledgeFactory",
    # Providers
    "OpenSearchKnowledgeProvider",
    "OpenSearchKnowledgeBase",
    # Loaders
    "WebsiteLoader",
    "SitemapLoader",
    "SitemapParser", 
    "SitemapDiscovery",
    "FileLoader",
    "LoaderFactory",
]