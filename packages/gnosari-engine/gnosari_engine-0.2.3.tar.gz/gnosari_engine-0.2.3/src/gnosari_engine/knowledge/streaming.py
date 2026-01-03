"""
Knowledge loading streaming events and callback system.

This module provides a clean, type-safe event system for knowledge loading
that works WITHOUT session IDs using callbacks instead of global registry.

Best Practices:
- Strongly typed event objects (no dicts)
- Protocol-based callback interface
- Immutable event data with dataclasses
- Clear separation of concerns
"""

from dataclasses import dataclass
from typing import Protocol, Optional
from enum import Enum


class KnowledgeEventType(Enum):
    """Types of knowledge loading events."""

    # Sitemap events
    SITEMAP_DISCOVERY_START = "sitemap_discovery_start"
    SITEMAP_DISCOVERED = "sitemap_discovered"
    SITEMAP_URLS_COLLECTED = "sitemap_urls_collected"

    # URL processing events
    URL_PROCESSING_START = "url_processing_start"
    URL_CONTENT_FETCHED = "url_content_fetched"
    URL_PROCESSING_COMPLETE = "url_processing_complete"
    URL_PROCESSING_ERROR = "url_processing_error"

    # Website loading events
    WEBSITE_FETCH_START = "website_fetch_start"
    WEBSITE_CONTENT_FETCHED = "website_content_fetched"
    WEBSITE_CHUNKING_START = "website_chunking_start"
    WEBSITE_CHUNKING_COMPLETE = "website_chunking_complete"

    # Document processing events
    DOCUMENTS_BATCH_READY = "documents_batch_ready"

    # Knowledge base events
    KNOWLEDGE_BASE_LOAD_START = "knowledge_base_load_start"
    KNOWLEDGE_BASE_LOAD_COMPLETE = "knowledge_base_load_complete"
    KNOWLEDGE_BASE_LOAD_ERROR = "knowledge_base_load_error"

    # Overall progress
    LOADING_PROGRESS = "loading_progress"


@dataclass(frozen=True)
class SitemapDiscoveryStartEvent:
    """Event emitted when sitemap discovery begins."""

    sitemap_url: str
    max_depth: int


@dataclass(frozen=True)
class SitemapDiscoveredEvent:
    """Event emitted when a sitemap is discovered and parsed."""

    sitemap_url: str
    depth: int
    url_count: int
    nested_sitemap_count: int


@dataclass(frozen=True)
class SitemapUrlsCollectedEvent:
    """Event emitted when all URLs are collected from sitemap(s)."""

    sitemap_url: str
    total_urls: int
    filtered_urls: int
    final_url_count: int


@dataclass(frozen=True)
class UrlProcessingStartEvent:
    """Event emitted when starting to process a URL."""

    url: str
    url_index: int
    total_urls: int
    progress_percent: float


@dataclass(frozen=True)
class UrlContentFetchedEvent:
    """Event emitted when URL content is fetched."""

    url: str
    content_size: int
    fetch_time_ms: float


@dataclass(frozen=True)
class UrlProcessingCompleteEvent:
    """Event emitted when URL processing completes."""

    url: str
    url_index: int
    total_urls: int
    document_count: int
    success: bool


@dataclass(frozen=True)
class UrlProcessingErrorEvent:
    """Event emitted when URL processing fails."""

    url: str
    url_index: int
    error_message: str
    error_type: str


@dataclass(frozen=True)
class WebsiteFetchStartEvent:
    """Event emitted when website fetch begins."""

    url: str
    api_endpoint: str


@dataclass(frozen=True)
class WebsiteContentFetchedEvent:
    """Event emitted when website content is fetched."""

    url: str
    content_size: int
    status_code: int


@dataclass(frozen=True)
class WebsiteChunkingStartEvent:
    """Event emitted when chunking begins."""

    url: str
    content_size: int
    chunk_size: int
    chunk_overlap: int


@dataclass(frozen=True)
class WebsiteChunkingCompleteEvent:
    """Event emitted when chunking completes."""

    url: str
    total_chunks: int
    valid_chunks: int
    skipped_chunks: int


@dataclass(frozen=True)
class DocumentsBatchReadyEvent:
    """Event emitted when a batch of documents is ready."""

    batch_size: int
    total_processed: int
    source: str


@dataclass(frozen=True)
class KnowledgeBaseLoadStartEvent:
    """Event emitted when knowledge base loading starts."""

    knowledge_base_id: str
    knowledge_base_name: str
    source_count: int


@dataclass(frozen=True)
class KnowledgeBaseLoadCompleteEvent:
    """Event emitted when knowledge base loading completes."""

    knowledge_base_id: str
    total_documents: int
    success: bool
    duration_seconds: float


@dataclass(frozen=True)
class KnowledgeBaseLoadErrorEvent:
    """Event emitted when knowledge base loading fails."""

    knowledge_base_id: str
    error_message: str
    error_type: str


@dataclass(frozen=True)
class LoadingProgressEvent:
    """Event emitted for overall loading progress."""

    completed_sources: int
    total_sources: int
    documents_processed: int
    current_source: str
    progress_percent: float


# Union type for all events
KnowledgeEvent = (
    SitemapDiscoveryStartEvent |
    SitemapDiscoveredEvent |
    SitemapUrlsCollectedEvent |
    UrlProcessingStartEvent |
    UrlContentFetchedEvent |
    UrlProcessingCompleteEvent |
    UrlProcessingErrorEvent |
    WebsiteFetchStartEvent |
    WebsiteContentFetchedEvent |
    WebsiteChunkingStartEvent |
    WebsiteChunkingCompleteEvent |
    DocumentsBatchReadyEvent |
    KnowledgeBaseLoadStartEvent |
    KnowledgeBaseLoadCompleteEvent |
    KnowledgeBaseLoadErrorEvent |
    LoadingProgressEvent
)


class KnowledgeEventCallback(Protocol):
    """
    Protocol for knowledge event callbacks.

    Callbacks receive strongly-typed event objects instead of dicts.
    """

    def __call__(self, event_type: KnowledgeEventType, event: KnowledgeEvent) -> None:
        """
        Called with event type and strongly-typed event object.

        Args:
            event_type: Type of event
            event: Strongly-typed event object
        """
        ...


class EventEmitter:
    """
    Helper class for emitting knowledge loading events.

    Provides a clean interface for loaders to emit events without
    coupling to specific callback implementations.
    """

    def __init__(self, callback: Optional[KnowledgeEventCallback] = None):
        """
        Initialize event emitter.

        Args:
            callback: Optional callback for receiving events
        """
        self._callback = callback

    def emit(self, event_type: KnowledgeEventType, event: KnowledgeEvent) -> None:
        """
        Emit an event.

        Args:
            event_type: Type of event
            event: Event object
        """
        if self._callback:
            self._callback(event_type, event)

    @property
    def has_callback(self) -> bool:
        """Check if callback is configured."""
        return self._callback is not None
