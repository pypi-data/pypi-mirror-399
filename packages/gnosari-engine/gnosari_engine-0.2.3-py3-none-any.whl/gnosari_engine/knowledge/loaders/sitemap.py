"""
Sitemap loader for knowledge bases.
Migrated from legacy implementation with SOLID refactoring and enhanced architecture.
Features separate components for parsing, discovery, and loading following SRP.
"""

import asyncio
import logging
import xml.etree.ElementTree as ET
from typing import Any, Callable
from urllib.parse import urljoin
import aiohttp

from ..interfaces import IKnowledgeLoader
from ..components import Document
from ..streaming import (
    EventEmitter,
    KnowledgeEventType,
    SitemapDiscoveryStartEvent,
    SitemapDiscoveredEvent,
    SitemapUrlsCollectedEvent,
    UrlProcessingStartEvent,
    UrlProcessingCompleteEvent,
    UrlProcessingErrorEvent
)
from .website import WebsiteLoader


class SitemapParser:
    """Handles XML sitemap parsing - Single Responsibility Principle."""
    
    def __init__(self):
        """Initialize sitemap parser."""
        self._logger = logging.getLogger(__name__)
    
    def parse_sitemap_content(self, content: str) -> dict[str, list[str]]:
        """
        Parse XML sitemap content and extract URLs and nested sitemaps.
        
        Args:
            content: XML sitemap content
            
        Returns:
            Dictionary with 'urls' and 'sitemaps' lists
        """
        try:
            root = ET.fromstring(content)
            
            # Handle sitemap index (references to other sitemaps)
            if self._is_sitemap_index(root):
                return self._parse_sitemap_index(root)
            
            # Handle regular sitemap (list of URLs)
            return self._parse_url_set(root)
            
        except ET.ParseError as e:
            self._logger.error(f"Failed to parse XML sitemap: {str(e)}")
            return {"urls": [], "sitemaps": []}
    
    def _is_sitemap_index(self, root: ET.Element) -> bool:
        """Detect sitemap index vs URL set."""
        return root.tag.endswith('}sitemapindex') or root.tag == 'sitemapindex'
    
    def _parse_sitemap_index(self, root: ET.Element) -> dict[str, list[str]]:
        """Extract nested sitemap URLs."""
        sitemaps = []
        
        for sitemap_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap'):
            loc_elem = sitemap_elem.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
            if loc_elem is not None and loc_elem.text:
                sitemaps.append(loc_elem.text.strip())
        
        # Also check for elements without namespace
        for sitemap_elem in root.findall('.//sitemap'):
            loc_elem = sitemap_elem.find('.//loc')
            if loc_elem is not None and loc_elem.text:
                sitemaps.append(loc_elem.text.strip())
        
        return {"urls": [], "sitemaps": sitemaps}
    
    def _parse_url_set(self, root: ET.Element) -> dict[str, list[str]]:
        """Extract page URLs from sitemap."""
        urls = []
        
        for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
            loc_elem = url_elem.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
            if loc_elem is not None and loc_elem.text:
                urls.append(loc_elem.text.strip())
        
        # Also check for elements without namespace
        for url_elem in root.findall('.//url'):
            loc_elem = url_elem.find('.//loc')
            if loc_elem is not None and loc_elem.text:
                urls.append(loc_elem.text.strip())
        
        return {"urls": urls, "sitemaps": []}


class SitemapDiscovery:
    """Handles recursive sitemap discovery - Single Responsibility Principle."""

    def __init__(self, max_depth: int = 5, event_emitter: EventEmitter | None = None):
        """
        Initialize sitemap discovery.

        Args:
            max_depth: Maximum recursion depth for nested sitemaps
            event_emitter: Optional event emitter for progress tracking
        """
        self._max_depth = max_depth
        self._logger = logging.getLogger(__name__)
        self._parser = SitemapParser()
        self._event_emitter = event_emitter or EventEmitter()
    
    async def discover_all_urls(self, sitemap_url: str) -> list[str]:
        """
        Recursively discover all URLs from sitemap and nested sitemaps.

        Args:
            sitemap_url: Root sitemap URL

        Returns:
            List of all discovered URLs
        """
        # Emit discovery start event
        self._event_emitter.emit(
            KnowledgeEventType.SITEMAP_DISCOVERY_START,
            SitemapDiscoveryStartEvent(sitemap_url=sitemap_url, max_depth=self._max_depth)
        )

        discovered_urls = []
        visited_sitemaps: set[str] = set()

        await self._discover_recursive(sitemap_url, discovered_urls, visited_sitemaps, 0)

        return discovered_urls
    
    async def _discover_recursive(
        self, 
        sitemap_url: str, 
        discovered_urls: list[str], 
        visited_sitemaps: set[str], 
        depth: int
    ) -> None:
        """Parallel recursive discovery with cycle detection."""
        if depth > self._max_depth:
            self._logger.warning(f"Max depth {self._max_depth} reached, stopping recursion")
            return
        
        if sitemap_url in visited_sitemaps:
            self._logger.debug(f"Already visited sitemap: {sitemap_url}")
            return
        
        visited_sitemaps.add(sitemap_url)
        self._logger.info(f"Processing sitemap at depth {depth}: {sitemap_url}")
        
        try:
            content = await self._fetch_sitemap_content(sitemap_url)
            if not content:
                return

            parsed = self._parser.parse_sitemap_content(content)

            # Add discovered URLs
            discovered_urls.extend(parsed["urls"])
            self._logger.info(f"Found {len(parsed['urls'])} URLs in sitemap: {sitemap_url}")

            # Emit sitemap discovered event
            self._event_emitter.emit(
                KnowledgeEventType.SITEMAP_DISCOVERED,
                SitemapDiscoveredEvent(
                    sitemap_url=sitemap_url,
                    depth=depth,
                    url_count=len(parsed["urls"]),
                    nested_sitemap_count=len(parsed["sitemaps"])
                )
            )

            # Process nested sitemaps in parallel
            if parsed["sitemaps"]:
                nested_tasks = []
                for nested_sitemap in parsed["sitemaps"]:
                    nested_url = urljoin(sitemap_url, nested_sitemap)
                    if nested_url not in visited_sitemaps:  # Check before creating task
                        task = self._discover_recursive(
                            nested_url, discovered_urls, visited_sitemaps, depth + 1
                        )
                        nested_tasks.append(task)

                if nested_tasks:
                    await asyncio.gather(*nested_tasks, return_exceptions=True)
        
        except Exception as e:
            self._logger.error(f"Error processing sitemap {sitemap_url}: {str(e)}")
    
    async def _fetch_sitemap_content(self, url: str) -> str | None:
        """Fetch sitemap content from URL."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        self._logger.error(f"Failed to fetch sitemap {url}: HTTP {response.status}")
                        return None
        except Exception as e:
            self._logger.error(f"Error fetching sitemap {url}: {str(e)}")
            return None


class SitemapLoader(IKnowledgeLoader):
    """
    Sitemap loader with parallel URL processing.
    Migrated from legacy with dependency injection improvements.
    """
    
    def __init__(self, config: dict[str, Any] | None = None, event_emitter: EventEmitter | None = None):
        """
        Initialize sitemap loader.

        Args:
            config: Optional loader configuration
            event_emitter: Optional event emitter for progress tracking
        """
        self._config = config or {}
        self._logger = logging.getLogger(__name__)
        self._event_emitter = event_emitter or EventEmitter()
        self._website_loader = WebsiteLoader(config, event_emitter=self._event_emitter)  # Pass event emitter
        self._discovery = SitemapDiscovery(
            max_depth=self._config.get('max_sitemap_depth', 5),
            event_emitter=self._event_emitter
        )
        self._max_concurrent_urls = self._config.get('max_concurrent_urls', 10)
    
    def supports_source_type(self, source_type: str) -> bool:
        """Check if this loader supports sitemap sources."""
        return source_type == "sitemap"
    
    async def load_data(self, source: str, **options: Any) -> list[Document]:
        """
        Load sitemap with parallel URL processing.
        Features from legacy:
        - Recursive sitemap discovery
        - Parallel content loading with semaphore
        - URL filtering and deduplication
        - Configurable concurrency limits
        
        Args:
            source: Sitemap URL
            **options: Additional loading options including metadata
            
        Returns:
            List of Document objects with content and metadata
        """
        self._logger.info(f"SitemapLoader: Loading data from sitemap {source}")

        try:
            # Discover all URLs from sitemap
            urls = await self._discovery.discover_all_urls(source)

            if not urls:
                self._logger.warning(f"No URLs found in sitemap: {source}")
                return []

            self._logger.info(f"Discovered {len(urls)} URLs from sitemap: {source}")
            total_urls = len(urls)

            # Filter URLs if configured
            urls = self._filter_urls(urls)
            filtered_urls = len(urls)

            # Limit URLs if configured
            max_urls = self._config.get('max_urls', None)
            if max_urls and len(urls) > max_urls:
                self._logger.info(f"Limiting to first {max_urls} URLs")
                urls = urls[:max_urls]

            # Emit URLs collected event
            self._event_emitter.emit(
                KnowledgeEventType.SITEMAP_URLS_COLLECTED,
                SitemapUrlsCollectedEvent(
                    sitemap_url=source,
                    total_urls=total_urls,
                    filtered_urls=filtered_urls - total_urls,
                    final_url_count=len(urls)
                )
            )
            
            # Load content from all discovered URLs in parallel
            all_documents = []
            metadata = options.get('metadata', {})
            
            # Create parallel tasks for content loading
            content_tasks = []
            for i, url in enumerate(urls):
                # Add sitemap-specific metadata
                url_metadata = {
                    "sitemap_source": source,
                    "url_index": i,
                    "total_urls": len(urls),
                    "loader": "sitemap"
                }
                if metadata:
                    url_metadata.update(metadata)
                
                # Create task for loading this URL's content
                task = self._load_url_content(url, url_metadata, i + 1, len(urls))
                content_tasks.append(task)
            
            # Execute all content loading tasks in parallel with concurrency limit
            self._logger.info(f"Loading content from {len(urls)} URLs in parallel (max concurrent: {self._max_concurrent_urls})")
            
            # Use semaphore to limit concurrent requests
            semaphore = asyncio.Semaphore(self._max_concurrent_urls)
            limited_tasks = [self._load_url_with_semaphore(semaphore, task) for task in content_tasks]
            
            results = await asyncio.gather(*limited_tasks, return_exceptions=True)
            
            # Process results and collect documents
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self._logger.error(f"Failed to load content from URL {i+1}: {str(result)}")
                elif isinstance(result, list):
                    all_documents.extend(result)
            
            self._logger.info(f"SitemapLoader: Loaded {len(all_documents)} total documents from {len(urls)} URLs")
            return all_documents
            
        except Exception as e:
            self._logger.error(f"Error loading sitemap content from {source}: {str(e)}")
            return []
    
    async def load_data_streaming(
        self,
        source: str,
        callback: Callable[[list[Document]], None],
        batch_size: int = 5,
        **options: Any
    ) -> int:
        """
        Streaming sitemap loader for real-time processing.
        
        Args:
            source: Sitemap URL
            callback: Callback function called with batches of documents
            batch_size: Number of documents to batch before calling callback
            **options: Additional loading options including metadata
            
        Returns:
            Total number of documents processed
        """
        self._logger.info(f"SitemapLoader: Streaming data from sitemap {source}")

        try:
            # Discover all URLs from sitemap
            urls = await self._discovery.discover_all_urls(source)

            if not urls:
                self._logger.warning(f"No URLs found in sitemap: {source}")
                return 0

            self._logger.info(f"Discovered {len(urls)} URLs from sitemap: {source}")
            total_urls = len(urls)

            # Filter URLs if configured
            urls = self._filter_urls(urls)
            filtered_urls = len(urls)

            # Limit URLs if configured
            max_urls = self._config.get('max_urls', None)
            if max_urls and len(urls) > max_urls:
                self._logger.info(f"Limiting to first {max_urls} URLs")
                urls = urls[:max_urls]

            # Emit URLs collected event
            self._event_emitter.emit(
                KnowledgeEventType.SITEMAP_URLS_COLLECTED,
                SitemapUrlsCollectedEvent(
                    sitemap_url=source,
                    total_urls=total_urls,
                    filtered_urls=filtered_urls - total_urls,
                    final_url_count=len(urls)
                )
            )
            
            total_processed = 0
            current_batch = []
            metadata = options.get('metadata', {})
            
            # Process URLs with concurrency control and streaming callbacks
            semaphore = asyncio.Semaphore(self._max_concurrent_urls)
            
            async def process_url_streaming(url: str, url_index: int) -> None:
                """Process a single URL and add its documents to the streaming batch."""
                nonlocal total_processed, current_batch

                async with semaphore:
                    try:
                        self._logger.info(f"Streaming URL {url_index + 1}/{len(urls)}: {url}")

                        # Emit URL processing start event
                        progress_percent = ((url_index + 1) / len(urls)) * 100
                        self._event_emitter.emit(
                            KnowledgeEventType.URL_PROCESSING_START,
                            UrlProcessingStartEvent(
                                url=url,
                                url_index=url_index,
                                total_urls=len(urls),
                                progress_percent=progress_percent
                            )
                        )

                        # Add sitemap-specific metadata
                        url_metadata = {
                            "sitemap_source": source,
                            "url_index": url_index,
                            "total_urls": len(urls),
                            "loader": "sitemap"
                        }
                        if metadata:
                            url_metadata.update(metadata)

                        # Track document count for this URL
                        url_document_count = 0

                        # Use website loader's streaming method for this URL
                        def url_callback(documents: list[Document]) -> None:
                            nonlocal current_batch, total_processed, url_document_count

                            # Track documents from this URL
                            url_document_count += len(documents)

                            # Add documents to current batch
                            current_batch.extend(documents)
                            total_processed += len(documents)

                            # Call main callback when batch is full
                            while len(current_batch) >= batch_size:
                                batch_to_send = current_batch[:batch_size]
                                current_batch = current_batch[batch_size:]
                                callback(batch_to_send)
                                self._logger.debug(f"Streamed batch of {len(batch_to_send)} documents (total: {total_processed})")

                        # Load URL content with streaming
                        await self._website_loader.load_data_streaming(url, url_callback, batch_size, metadata=url_metadata)

                        # Emit URL processing complete event
                        self._event_emitter.emit(
                            KnowledgeEventType.URL_PROCESSING_COMPLETE,
                            UrlProcessingCompleteEvent(
                                url=url,
                                url_index=url_index,
                                total_urls=len(urls),
                                document_count=url_document_count,
                                success=True
                            )
                        )

                    except Exception as e:
                        self._logger.error(f"Error streaming content from URL {url}: {str(e)}")

                        # Emit URL processing error event
                        self._event_emitter.emit(
                            KnowledgeEventType.URL_PROCESSING_ERROR,
                            UrlProcessingErrorEvent(
                                url=url,
                                url_index=url_index,
                                error_message=str(e),
                                error_type=type(e).__name__
                            )
                        )
            
            # Create tasks for all URLs
            tasks = [process_url_streaming(url, i) for i, url in enumerate(urls)]
            
            # Execute all URL processing tasks
            self._logger.info(f"Processing {len(urls)} URLs in streaming mode (max concurrent: {self._max_concurrent_urls})")
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Send any remaining documents in final batch
            if current_batch:
                callback(current_batch)
                self._logger.debug(f"Streamed final batch of {len(current_batch)} documents")
            
            self._logger.info(f"SitemapLoader: Streamed {total_processed} total documents from {len(urls)} URLs")
            return total_processed
            
        except Exception as e:
            self._logger.error(f"Error streaming sitemap content from {source}: {str(e)}")
            return 0
    
    async def _load_url_content(
        self,
        url: str,
        url_metadata: dict[str, Any],
        url_num: int,
        total_urls: int
    ) -> list[Document]:
        """Load content from a single URL."""
        try:
            self._logger.info(f"Loading content from URL {url_num}/{total_urls}: {url}")

            # Emit URL processing start event
            progress_percent = (url_num / total_urls) * 100
            self._event_emitter.emit(
                KnowledgeEventType.URL_PROCESSING_START,
                UrlProcessingStartEvent(
                    url=url,
                    url_index=url_num - 1,
                    total_urls=total_urls,
                    progress_percent=progress_percent
                )
            )

            documents = await self._website_loader.load_data(url, metadata=url_metadata)

            # Emit URL processing complete event
            self._event_emitter.emit(
                KnowledgeEventType.URL_PROCESSING_COMPLETE,
                UrlProcessingCompleteEvent(
                    url=url,
                    url_index=url_num - 1,
                    total_urls=total_urls,
                    document_count=len(documents),
                    success=True
                )
            )

            return documents

        except Exception as e:
            self._logger.error(f"Error loading content from URL {url}: {str(e)}")

            # Emit URL processing error event
            self._event_emitter.emit(
                KnowledgeEventType.URL_PROCESSING_ERROR,
                UrlProcessingErrorEvent(
                    url=url,
                    url_index=url_num - 1,
                    error_message=str(e),
                    error_type=type(e).__name__
                )
            )

            return []
    
    async def _load_url_with_semaphore(self, semaphore: asyncio.Semaphore, task) -> list[Document]:
        """Execute URL loading task with semaphore to limit concurrency."""
        async with semaphore:
            return await task
    
    def _filter_urls(self, urls: list[str]) -> list[str]:
        """URL filtering with allow/block patterns."""
        if not urls:
            return urls
        
        # Filter by allowed patterns
        allowed_patterns = self._config.get('allowed_url_patterns', [])
        if allowed_patterns:
            filtered_urls = []
            for url in urls:
                if any(pattern in url for pattern in allowed_patterns):
                    filtered_urls.append(url)
            urls = filtered_urls
        
        # Filter out blocked patterns
        blocked_patterns = self._config.get('blocked_url_patterns', [])
        if blocked_patterns:
            urls = [url for url in urls if not any(pattern in url for pattern in blocked_patterns)]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url in urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        
        return unique_urls