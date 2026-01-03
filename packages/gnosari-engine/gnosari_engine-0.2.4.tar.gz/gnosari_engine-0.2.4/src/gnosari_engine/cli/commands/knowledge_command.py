"""
Knowledge Command - Handles knowledge base loading and management operations
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from .base_command import BaseCommand
from ..interfaces import (
    ConfigurationLoaderInterface,
    DisplayServiceInterface,
    DomainFactoryInterface
)
from ..logging_config import LoggingConfigurator
from ...knowledge.services import KnowledgeLoaderService, KnowledgeLoadError
from ...knowledge.streaming import (
    KnowledgeEventType,
    KnowledgeEvent,
    SitemapDiscoveryStartEvent,
    SitemapDiscoveredEvent,
    SitemapUrlsCollectedEvent,
    UrlProcessingStartEvent,
    UrlProcessingCompleteEvent,
    UrlProcessingErrorEvent,
    WebsiteFetchStartEvent,
    WebsiteContentFetchedEvent,
    WebsiteChunkingStartEvent,
    WebsiteChunkingCompleteEvent,
    KnowledgeBaseLoadStartEvent,
    KnowledgeBaseLoadCompleteEvent,
    KnowledgeBaseLoadErrorEvent,
    LoadingProgressEvent
)


class KnowledgeCommand(BaseCommand):
    """
    Single Responsibility: Handle knowledge base operations (load, status, etc.)
    Open/Closed: Easy to extend with new knowledge operations
    Dependency Inversion: Depends on abstractions, not concretions
    """
    
    def __init__(
        self,
        config_loader: ConfigurationLoaderInterface,
        display_service: DisplayServiceInterface,
        domain_factory: DomainFactoryInterface,
        logging_configurator: LoggingConfigurator,
        knowledge_loader_service: Optional[KnowledgeLoaderService] = None
    ):
        super().__init__(display_service)
        self._config_loader = config_loader
        self._domain_factory = domain_factory
        self._logging_configurator = logging_configurator
        self._knowledge_loader_service = knowledge_loader_service or KnowledgeLoaderService()
    
    async def execute(self, *args, **kwargs) -> None:
        """Base execute method - subcommands will override this"""
        raise NotImplementedError("Use specific subcommand methods like load()")
    
    async def load(
        self,
        team_config: Path,
        agent_id: Optional[str] = None,
        provider: str = "opensearch",
        force_reload: bool = False,
        debug: bool = False,
        verbose: bool = False,
        log_level: Optional[str] = None,
        log_file: Optional[str] = None,
        structured_logs: bool = False
    ) -> None:
        """Load knowledge sources for a team or specific agent"""
        
        operation = f"knowledge load for {'agent ' + agent_id if agent_id else 'all agents'}"
        self._log_execution_start(operation)
        
        try:
            # Configure logging first
            self._configure_logging(
                log_level, debug, verbose, log_file, structured_logs
            )
            
            self._display_service.display_header()
            self._display_service.display_status(
                f"🧠 Loading knowledge sources from: {team_config}",
                "info"
            )
            if agent_id:
                self._display_service.display_status(
                    f"   Filtering for agent: {agent_id}",
                    "info"
                )

            # Create event callback for real-time display updates
            # Three-tier output system:
            # 1. Default (essential): High-level progress (knowledge base, URL discovery, URL processing summary)
            # 2. Verbose: Detailed progress (individual URL processing, fetch/chunk details)
            # 3. Debug: Raw events and technical details
            def event_callback(event_type: KnowledgeEventType, event: KnowledgeEvent) -> None:
                # === TIER 1: ESSENTIAL EVENTS (ALWAYS SHOWN) ===

                # Knowledge base level
                if event_type == KnowledgeEventType.KNOWLEDGE_BASE_LOAD_START:
                    event = event  # type: KnowledgeBaseLoadStartEvent
                    self._display_service.display_status(
                        f"📚 Loading: {event.knowledge_base_name} ({event.source_count} sources) - ID: {event.knowledge_base_id}",
                        "info"
                    )

                elif event_type == KnowledgeEventType.LOADING_PROGRESS:
                    event = event  # type: LoadingProgressEvent
                    if event.current_source and event.progress_percent == 0.0:
                        # Show which agents use this knowledge base at the start
                        self._display_service.display_status(
                            f"   → {event.current_source}",
                            "info"
                        )

                elif event_type == KnowledgeEventType.KNOWLEDGE_BASE_LOAD_COMPLETE:
                    event = event  # type: KnowledgeBaseLoadCompleteEvent
                    self._display_service.display_status(
                        f"✅ Completed: {event.knowledge_base_id} - {event.total_documents} docs in {event.duration_seconds:.2f}s",
                        "success"
                    )

                elif event_type == KnowledgeEventType.KNOWLEDGE_BASE_LOAD_ERROR:
                    event = event  # type: KnowledgeBaseLoadErrorEvent
                    self._display_service.display_status(
                        f"❌ Error: {event.knowledge_base_id} - {event.error_message}",
                        "error"
                    )

                # Sitemap discovery (essential)
                elif event_type == KnowledgeEventType.SITEMAP_DISCOVERY_START:
                    event = event  # type: SitemapDiscoveryStartEvent
                    self._display_service.display_status(
                        f"🗺️  Discovering URLs from sitemap (max depth: {event.max_depth})...",
                        "info"
                    )

                elif event_type == KnowledgeEventType.SITEMAP_URLS_COLLECTED:
                    event = event  # type: SitemapUrlsCollectedEvent
                    filtered_msg = f" (filtered {abs(event.filtered_urls)})" if event.filtered_urls != 0 else ""
                    self._display_service.display_status(
                        f"📋 Discovered {event.final_url_count} URLs from sitemap{filtered_msg}",
                        "info"
                    )

                # URL processing progress (essential summary)
                elif event_type == KnowledgeEventType.URL_PROCESSING_START:
                    event = event  # type: UrlProcessingStartEvent
                    # Show progress with a clean progress indicator
                    self._display_service.display_status(
                        f"⏳ Processing URL {event.url_index + 1}/{event.total_urls} ({event.progress_percent:.0f}%)...",
                        "info"
                    )

                elif event_type == KnowledgeEventType.URL_PROCESSING_COMPLETE:
                    event = event  # type: UrlProcessingCompleteEvent
                    self._display_service.display_status(
                        f"✓ URL {event.url_index + 1}/{event.total_urls}: {event.document_count} documents",
                        "success"
                    )

                # Errors (always show)
                elif event_type == KnowledgeEventType.URL_PROCESSING_ERROR:
                    event = event  # type: UrlProcessingErrorEvent
                    self._display_service.display_status(
                        f"✗ Error processing URL {event.url_index + 1}: {event.error_message}",
                        "error"
                    )

                # === TIER 2: VERBOSE EVENTS (DETAILED PROGRESS) ===
                elif verbose:
                    # Sitemap discovery details
                    if event_type == KnowledgeEventType.SITEMAP_DISCOVERED:
                        event = event  # type: SitemapDiscoveredEvent
                        self._display_service.display_status(
                            f"  └─ Found sitemap at depth {event.depth}: {event.url_count} URLs, {event.nested_sitemap_count} nested sitemaps",
                            "info"
                        )

                    # URL fetch details
                    elif event_type == KnowledgeEventType.WEBSITE_FETCH_START:
                        event = event  # type: WebsiteFetchStartEvent
                        self._display_service.display_status(
                            f"  └─ 🌐 Fetching: {event.url}",
                            "info"
                        )

                    elif event_type == KnowledgeEventType.WEBSITE_CONTENT_FETCHED:
                        event = event  # type: WebsiteContentFetchedEvent
                        size_kb = event.content_size / 1024
                        self._display_service.display_status(
                            f"  └─ ✓ Fetched {size_kb:.1f}KB (HTTP {event.status_code})",
                            "success"
                        )

                    # Chunking details
                    elif event_type == KnowledgeEventType.WEBSITE_CHUNKING_START:
                        event = event  # type: WebsiteChunkingStartEvent
                        self._display_service.display_status(
                            f"  └─ ✂️  Chunking {event.content_size} chars into {event.chunk_size} char chunks",
                            "info"
                        )

                    elif event_type == KnowledgeEventType.WEBSITE_CHUNKING_COMPLETE:
                        event = event  # type: WebsiteChunkingCompleteEvent
                        skipped_msg = f", {event.skipped_chunks} skipped" if event.skipped_chunks > 0 else ""
                        self._display_service.display_status(
                            f"  └─ ✓ Created {event.valid_chunks} chunks{skipped_msg}",
                            "success"
                        )

            # Use the knowledge loader service with event callback
            # Always pass callback - it handles verbose filtering internally
            result = await self._knowledge_loader_service.load_from_team_config(
                team_config_path=team_config,
                agent_id=agent_id,
                provider=provider,
                force_reload=force_reload,
                event_callback=event_callback
            )
            
            # Display results
            if result.success:
                kb_text = "knowledge base" if result.total_knowledge_bases == 1 else "knowledge bases"
                agent_text = "agent" if result.total_agents == 1 else "agents"
                self._display_service.display_status(
                    f"✅ Successfully loaded {result.total_documents} documents "
                    f"into {result.total_knowledge_bases} {kb_text} "
                    f"(available to {result.total_agents} {agent_text})",
                    "success"
                )
            else:
                self._display_service.display_status(
                    f"⚠️ Partially loaded {result.total_documents} documents "
                    f"with {len(result.errors)} errors",
                    "warning"
                )
            
            # Display errors if any
            if result.errors and verbose:
                for error in result.errors:
                    self._display_service.display_status(f"  ✗ {error}", "error")
            
            self._log_execution_end(operation)
            
        except KnowledgeLoadError as e:
            self._handle_error(e, operation)
            if verbose:
                import traceback
                self._display_service.display_status(traceback.format_exc(), "error")
            sys.exit(1)
        except Exception as e:
            self._handle_error(e, operation)
            if verbose:
                import traceback
                self._display_service.display_status(traceback.format_exc(), "error")
            sys.exit(1)
    
    def _configure_logging(
        self, 
        log_level: Optional[str],
        debug: bool,
        verbose: bool,
        log_file: Optional[str],
        structured_logs: bool
    ) -> None:
        """Configure logging with provided parameters"""
        self._logging_configurator.configure_from_cli_args(
            log_level=log_level,
            debug=debug,
            verbose=verbose,
            log_file=log_file,
            structured_logs=structured_logs,
            session_id=None  # Not applicable for knowledge loading
        )