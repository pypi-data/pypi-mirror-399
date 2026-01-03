"""
Knowledge management interfaces following SOLID principles.
Defines protocols for knowledge providers, knowledge bases, loaders, and factories.
"""

from typing import Any, Protocol, runtime_checkable, Callable
from datetime import datetime

from ..schemas.domain.knowledge import Knowledge


@runtime_checkable
class IKnowledgeProvider(Protocol):
    """Strategy pattern interface for knowledge providers (currently only OpenSearch is implemented)."""
    
    @property
    def provider_name(self) -> str:
        """Get the provider name identifier."""
        ...
    
    @property
    def is_initialized(self) -> bool:
        """Check if the provider is initialized and ready to use."""
        ...
    
    async def initialize(self, **config: Any) -> None:
        """Initialize the provider with configuration."""
        ...
    
    async def cleanup(self) -> None:
        """Clean up provider resources."""
        ...
    
    async def create_knowledge_base(self, knowledge: Knowledge) -> "IKnowledgeBase":
        """Create a new knowledge base from Knowledge domain object."""
        ...
    
    async def get_knowledge_base(self, knowledge_id: str) -> "IKnowledgeBase | None":
        """Retrieve an existing knowledge base by ID."""
        ...
    
    async def delete_knowledge_base(self, knowledge_id: str) -> bool:
        """Delete a knowledge base by ID. Returns True if successful."""
        ...


@runtime_checkable
class IKnowledgeBase(Protocol):
    """Interface for knowledge base operations."""
    
    @property
    def knowledge_id(self) -> str:
        """Get the knowledge base identifier."""
        ...
    
    @property
    def is_initialized(self) -> bool:
        """Check if the knowledge base is initialized and ready."""
        ...
    
    async def initialize(self) -> None:
        """Initialize the knowledge base."""
        ...
    
    async def add_data_source(self, data_source: str, **options: Any) -> int:
        """Add a data source to the knowledge base. Returns number of documents added."""
        ...
    
    async def query(self, query: str, **options: Any) -> "KnowledgeQueryResult":
        """Query the knowledge base. Returns search results."""
        ...
    
    async def get_status(self) -> "KnowledgeStatus":
        """Get current status of the knowledge base."""
        ...


@runtime_checkable
class IKnowledgeLoader(Protocol):
    """Interface for data source loaders."""
    
    def supports_source_type(self, source_type: str) -> bool:
        """Check if this loader supports the given source type."""
        ...
    
    async def load_data(self, source: str, **options: Any) -> list["Document"]:
        """Load data from a source. Returns list of documents."""
        ...
    
    async def load_data_streaming(
        self,
        source: str,
        callback: Callable[[list["Document"]], None],
        batch_size: int = 5,
        **options: Any
    ) -> int:
        """Load data with streaming callback for real-time processing. Returns total documents processed."""
        ...


@runtime_checkable
class IKnowledgeFactory(Protocol):
    """Factory interface for creating knowledge providers."""
    
    def create_provider(self, provider_name: str, **config: Any) -> IKnowledgeProvider:
        """Create a knowledge provider instance."""
        ...
    
    def register_provider(self, name: str, provider_class: type[IKnowledgeProvider]) -> None:
        """Register a new provider class."""
        ...
    
    def get_supported_providers(self) -> list[str]:
        """Get list of supported provider names."""
        ...


# Import these classes from components.py when they're available
__all__ = [
    "IKnowledgeProvider",
    "IKnowledgeBase", 
    "IKnowledgeLoader",
    "IKnowledgeFactory",
]