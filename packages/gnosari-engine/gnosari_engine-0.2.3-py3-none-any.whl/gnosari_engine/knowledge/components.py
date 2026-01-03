"""
Knowledge management components and domain objects.
Contains data structures for documents, query results, and status information.
"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class Document(BaseModel):
    """Represents a loaded document with content and metadata."""
    
    content: str = Field(..., description="The text content of the document")
    metadata: dict[str, Any] = Field(
        default_factory=dict, 
        description="Document metadata (URL, title, etc.)"
    )
    source: str = Field(..., description="Original source location (URL, file path, etc.)")
    doc_id: str | None = Field(
        default=None, 
        description="Unique document identifier within the knowledge base"
    )


class KnowledgeQueryResult(BaseModel):
    """Result from knowledge base query operations."""
    
    results: list[Document] = Field(..., description="List of matching documents")
    query: str = Field(..., description="The original query string")
    total_found: int = Field(..., description="Total number of results found")
    execution_time_ms: float = Field(..., description="Query execution time in milliseconds")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional result metadata (scores, filters, etc.)"
    )


class KnowledgeStatus(BaseModel):
    """Knowledge base status and health information."""
    
    knowledge_id: str = Field(..., description="Knowledge base identifier")
    document_count: int = Field(..., description="Number of documents in the knowledge base")
    last_updated: datetime | None = Field(
        default=None,
        description="Timestamp of last update"
    )
    status: Literal["ready", "loading", "error", "empty"] = Field(
        ..., 
        description="Current status of the knowledge base"
    )
    provider: str = Field(..., description="Provider name (currently only opensearch is supported)")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Provider-specific status information"
    )


class LoadingProgress(BaseModel):
    """Progress information during data loading operations."""
    
    total_sources: int = Field(..., description="Total number of data sources to process")
    completed_sources: int = Field(..., description="Number of completed sources")
    current_source: str = Field(..., description="Currently processing source")
    documents_processed: int = Field(..., description="Total documents processed so far")
    errors: list[str] = Field(
        default_factory=list,
        description="List of error messages encountered"
    )
    
    @property
    def progress_percentage(self) -> float:
        """Calculate completion percentage."""
        if self.total_sources == 0:
            return 0.0
        return (self.completed_sources / self.total_sources) * 100.0


__all__ = [
    "Document",
    "KnowledgeQueryResult", 
    "KnowledgeStatus",
    "LoadingProgress",
]