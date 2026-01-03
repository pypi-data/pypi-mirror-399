"""
Website loader for knowledge bases.
Migrated from legacy implementation with SOLID refactoring and enhanced architecture.
Features real-time streaming events for progress tracking.
"""

import logging
import os
import re
import time
from typing import Any, Callable, Optional
import aiohttp

from ..interfaces import IKnowledgeLoader
from ..components import Document
from ..streaming import (
    EventEmitter,
    KnowledgeEventType,
    WebsiteFetchStartEvent,
    WebsiteContentFetchedEvent,
    WebsiteChunkingStartEvent,
    WebsiteChunkingCompleteEvent
)


class WebsiteLoader(IKnowledgeLoader):
    """
    Website loader that fetches content through markdown conversion API.
    Migrated from legacy implementation with SOLID improvements.
    Features real-time streaming events for progress tracking.
    """

    def __init__(self, config: dict[str, Any] | None = None, event_emitter: Optional[EventEmitter] = None):
        """
        Initialize website loader.

        Args:
            config: Optional loader configuration
            event_emitter: Optional event emitter for progress tracking
        """
        self._config = config or {}
        self._logger = logging.getLogger(__name__)
        self._api_host = os.getenv("WEBSITE_LOADER_API_HOST", "https://r.ai.neomanex.com")
        self._event_emitter = event_emitter or EventEmitter()
    
    def supports_source_type(self, source_type: str) -> bool:
        """Check if this loader supports website sources."""
        return source_type == "website"
    
    async def load_data(self, source: str, **options: Any) -> list[Document]:
        """
        Load data from website URL using markdown conversion API with text chunking.

        Args:
            source: Website URL
            **options: Additional loading options including metadata
            
        Returns:
            List of Document objects with content and metadata
        """
        self._logger.info(f"WebsiteLoader: Loading data from {source}")

        try:
            api_url = f"{self._api_host}/{source}"

            # Emit fetch start event
            self._event_emitter.emit(
                KnowledgeEventType.WEBSITE_FETCH_START,
                WebsiteFetchStartEvent(url=source, api_endpoint=api_url)
            )

            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as response:
                    if response.status == 200:
                        content = await response.text()

                        # Emit content fetched event
                        self._event_emitter.emit(
                            KnowledgeEventType.WEBSITE_CONTENT_FETCHED,
                            WebsiteContentFetchedEvent(
                                url=source,
                                content_size=len(content),
                                status_code=response.status
                            )
                        )

                        # Get chunk size from config
                        chunk_size = self._config.get('chunk_size', 8000)
                        chunk_overlap = self._config.get('chunk_overlap', 200)

                        # Emit chunking start event
                        self._event_emitter.emit(
                            KnowledgeEventType.WEBSITE_CHUNKING_START,
                            WebsiteChunkingStartEvent(
                                url=source,
                                content_size=len(content),
                                chunk_size=chunk_size,
                                chunk_overlap=chunk_overlap
                            )
                        )

                        # Chunk the content for better embedding generation
                        chunks = self._chunk_text(content)
                        self._logger.info(f"WebsiteLoader: Split content into {len(chunks)} chunks")
                        
                        documents = []
                        metadata = options.get('metadata', {})
                        skipped_chunks = 0

                        for i, chunk in enumerate(chunks):
                            # Clean the chunk text to avoid API parsing issues
                            cleaned_chunk = self._clean_text(chunk)

                            # Skip empty chunks
                            if not cleaned_chunk.strip():
                                self._logger.debug(f"Skipping empty chunk {i}")
                                skipped_chunks += 1
                                continue

                            doc_metadata = {
                                "source": source,
                                "loader": "website",
                                "chunk_index": i,
                                "total_chunks": len(chunks),
                                "timestamp": time.strftime('%Y-%m-%dT%H:%M:%S')
                            }
                            if metadata:
                                doc_metadata.update(metadata)

                            documents.append(Document(
                                content=cleaned_chunk,
                                metadata=doc_metadata,
                                source=source,
                                doc_id=f"{source}#chunk_{i}"
                            ))

                        # Emit chunking complete event
                        self._event_emitter.emit(
                            KnowledgeEventType.WEBSITE_CHUNKING_COMPLETE,
                            WebsiteChunkingCompleteEvent(
                                url=source,
                                total_chunks=len(chunks),
                                valid_chunks=len(documents),
                                skipped_chunks=skipped_chunks
                            )
                        )

                        return documents
                    else:
                        self._logger.error(f"Failed to fetch content from {api_url}: HTTP {response.status}")
                        return []
                        
        except Exception as e:
            self._logger.error(f"Error loading website content from {source}: {str(e)}")
            return []
    
    async def load_data_streaming(
        self,
        source: str,
        callback: Callable[[list[Document]], None],
        batch_size: int = 5,
        **options: Any
    ) -> int:
        """
        Load data from website URL with streaming callback for real-time bulk indexing.
        
        Args:
            source: Website URL
            callback: Callback function called with batches of documents
            batch_size: Number of documents to batch before calling callback
            **options: Additional loading options including metadata
            
        Returns:
            Total number of documents processed
        """
        self._logger.info(f"WebsiteLoader: Streaming data from {source}")

        try:
            api_url = f"{self._api_host}/{source}"

            # Emit fetch start event
            self._event_emitter.emit(
                KnowledgeEventType.WEBSITE_FETCH_START,
                WebsiteFetchStartEvent(url=source, api_endpoint=api_url)
            )

            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as response:
                    if response.status == 200:
                        content = await response.text()

                        # Emit content fetched event
                        self._event_emitter.emit(
                            KnowledgeEventType.WEBSITE_CONTENT_FETCHED,
                            WebsiteContentFetchedEvent(
                                url=source,
                                content_size=len(content),
                                status_code=response.status
                            )
                        )

                        # Get chunk size from config
                        chunk_size = self._config.get('chunk_size', 8000)
                        chunk_overlap = self._config.get('chunk_overlap', 200)

                        # Emit chunking start event
                        self._event_emitter.emit(
                            KnowledgeEventType.WEBSITE_CHUNKING_START,
                            WebsiteChunkingStartEvent(
                                url=source,
                                content_size=len(content),
                                chunk_size=chunk_size,
                                chunk_overlap=chunk_overlap
                            )
                        )

                        # Process chunks and call callback in batches
                        chunks = self._chunk_text(content)
                        self._logger.info(f"WebsiteLoader: Processing {len(chunks)} chunks in streaming mode")
                        
                        batch = []
                        total_processed = 0
                        metadata = options.get('metadata', {})
                        skipped_chunks = 0

                        for i, chunk in enumerate(chunks):
                            # Clean the chunk text to avoid API parsing issues
                            cleaned_chunk = self._clean_text(chunk)

                            # Skip empty chunks
                            if not cleaned_chunk.strip():
                                self._logger.debug(f"Skipping empty chunk {i}")
                                skipped_chunks += 1
                                continue

                            doc_metadata = {
                                "source": source,
                                "loader": "website",
                                "chunk_index": i,
                                "total_chunks": len(chunks),
                                "timestamp": time.strftime('%Y-%m-%dT%H:%M:%S')
                            }
                            if metadata:
                                doc_metadata.update(metadata)

                            document = Document(
                                content=cleaned_chunk,
                                metadata=doc_metadata,
                                source=source,
                                doc_id=f"{source}#chunk_{i}"
                            )

                            batch.append(document)

                            # Call callback when batch is full
                            if len(batch) >= batch_size:
                                callback(batch)
                                total_processed += len(batch)
                                self._logger.debug(f"Processed batch of {len(batch)} documents (total: {total_processed})")
                                batch = []

                        # Process remaining documents in final batch
                        if batch:
                            callback(batch)
                            total_processed += len(batch)
                            self._logger.debug(f"Processed final batch of {len(batch)} documents (total: {total_processed})")

                        # Emit chunking complete event
                        self._event_emitter.emit(
                            KnowledgeEventType.WEBSITE_CHUNKING_COMPLETE,
                            WebsiteChunkingCompleteEvent(
                                url=source,
                                total_chunks=len(chunks),
                                valid_chunks=total_processed,
                                skipped_chunks=skipped_chunks
                            )
                        )

                        return total_processed
                    else:
                        self._logger.error(f"Failed to fetch content from {api_url}: HTTP {response.status}")
                        return 0
                        
        except Exception as e:
            self._logger.error(f"Error loading website content from {source}: {str(e)}")
            return 0
    
    def _chunk_text(self, text: str) -> list[str]:
        """
        Chunk text into smaller pieces suitable for embedding generation.
        
        Args:
            text: Input text to chunk
            
        Returns:
            List of text chunks
        """
        # Get chunk size from config (default to ~8000 characters to stay under token limits)
        chunk_size = self._config.get('chunk_size', 8000)
        chunk_overlap = self._config.get('chunk_overlap', 200)
        
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            if end >= len(text):
                # Last chunk
                chunks.append(text[start:])
                break
            
            # Try to break at a sentence boundary
            chunk_text = text[start:end]
            
            # Look for sentence endings in the last 500 characters
            sentence_endings = ['. ', '! ', '? ', '\n\n']
            best_break = -1
            
            for ending in sentence_endings:
                pos = chunk_text.rfind(ending)
                if pos > len(chunk_text) - 500:  # Only consider breaks near the end
                    best_break = max(best_break, pos + len(ending))
            
            if best_break > 0:
                chunk_text = text[start:start + best_break]
                chunks.append(chunk_text)
                start = start + best_break - chunk_overlap
            else:
                # No good break found, just split at chunk_size
                chunk_text = text[start:end]
                chunks.append(chunk_text)
                start = end - chunk_overlap
            
            # Ensure we don't go backwards
            if start < 0:
                start = 0
        
        return chunks
    
    def _clean_text(self, text: str) -> str:
        """
        Clean text to remove problematic characters that might cause API issues.
        
        Args:
            text: Input text to clean
            
        Returns:
            Cleaned text
        """
        # Replace excessive whitespace with single spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Only allow safe characters: letters, numbers, punctuation, and markdown-safe symbols
        # This comprehensive approach removes all potentially problematic Unicode characters
        allowed_chars = set()
        
        # Basic ASCII letters, numbers, and punctuation
        for i in range(32, 127):  # Printable ASCII
            allowed_chars.add(chr(i))
        
        # Add essential whitespace characters
        allowed_chars.update(['\n', '\r', '\t'])
        
        # Filter text to only include allowed characters
        text = ''.join(char for char in text if char in allowed_chars)
        
        # Fix fragment starts - if text starts with lowercase or incomplete sentence
        text = self._fix_fragment_start(text)
        
        # Strip whitespace
        text = text.strip()
        
        return text
    
    def _fix_fragment_start(self, text: str) -> str:
        """
        Fix fragment starts by finding the first complete sentence.
        
        Args:
            text: Input text that may start with a fragment
            
        Returns:
            Text starting with a complete sentence
        """
        # If text starts with a lowercase letter or incomplete word, try to find the first complete sentence
        if text and (text[0].islower() or text.startswith(('to ', 'and ', 'or ', 'but ', 'the ', 'a ', 'an '))):
            # Look for the first sentence ending followed by a capital letter
            sentence_pattern = r'[.!?]\s+[A-Z#*]'
            match = re.search(sentence_pattern, text)
            if match:
                # Start from the capital letter after the sentence ending
                start_pos = match.start() + len(match.group()) - 1
                text = text[start_pos:]
                self._logger.debug(f"Fixed fragment start, new text begins with: '{text[:50]}...'")
        
        return text