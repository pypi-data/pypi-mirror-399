"""
File loader for knowledge bases.
New implementation for loading local files (PDF, text, CSV, JSON, directories).
"""

import asyncio
import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Callable

from ..interfaces import IKnowledgeLoader
from ..components import Document


class FileLoader(IKnowledgeLoader):
    """Loads file content (PDF, text, CSV, JSON, directories)."""
    
    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize file loader.
        
        Args:
            config: Optional loader configuration
        """
        self._config = config or {}
        self._logger = logging.getLogger(__name__)
        self._supported_extensions = {
            '.txt', '.md', '.csv', '.json', '.py', '.js', '.ts', 
            '.html', '.xml', '.yaml', '.yml', '.log', '.rst'
        }
        
        # Add configured extensions
        custom_extensions = self._config.get('supported_extensions', [])
        if custom_extensions:
            self._supported_extensions.update(custom_extensions)
    
    def supports_source_type(self, source_type: str) -> bool:
        """Check if this loader supports the given source type."""
        return source_type in ["file", "pdf", "text", "csv", "json", "directory"]
    
    async def load_data(self, source: str, **options: Any) -> list[Document]:
        """
        Load and process various file types.
        
        Args:
            source: File path or directory path
            **options: Additional loading options including metadata
            
        Returns:
            List of Document objects with content and metadata
        """
        self._logger.info(f"FileLoader: Loading data from {source}")
        
        try:
            source_path = Path(source)
            
            if not source_path.exists():
                self._logger.error(f"Source path does not exist: {source}")
                return []
            
            if source_path.is_file():
                return await self._load_single_file(source_path, options.get('metadata', {}))
            elif source_path.is_dir():
                return await self._load_directory(source_path, options.get('metadata', {}))
            else:
                self._logger.error(f"Source is neither file nor directory: {source}")
                return []
                
        except Exception as e:
            self._logger.error(f"Error loading file content from {source}: {str(e)}")
            return []
    
    async def load_data_streaming(
        self,
        source: str,
        callback: Callable[[list[Document]], None],
        batch_size: int = 5,
        **options: Any
    ) -> int:
        """
        Load file data with streaming callback for real-time processing.
        
        Args:
            source: File path or directory path
            callback: Callback function called with batches of documents
            batch_size: Number of documents to batch before calling callback
            **options: Additional loading options including metadata
            
        Returns:
            Total number of documents processed
        """
        self._logger.info(f"FileLoader: Streaming data from {source}")
        
        try:
            source_path = Path(source)
            
            if not source_path.exists():
                self._logger.error(f"Source path does not exist: {source}")
                return 0
            
            batch = []
            total_processed = 0
            metadata = options.get('metadata', {})
            
            async def process_batch():
                nonlocal total_processed
                if batch:
                    callback(batch)
                    total_processed += len(batch)
                    self._logger.debug(f"Processed batch of {len(batch)} documents (total: {total_processed})")
                    batch.clear()
            
            if source_path.is_file():
                documents = await self._load_single_file(source_path, metadata)
                batch.extend(documents)
                await process_batch()
            elif source_path.is_dir():
                # Process directory files in streaming batches
                async for file_path in self._iterate_directory_files(source_path):
                    try:
                        documents = await self._load_single_file(file_path, metadata)
                        batch.extend(documents)
                        
                        if len(batch) >= batch_size:
                            await process_batch()
                            
                    except Exception as e:
                        self._logger.error(f"Error loading file {file_path}: {str(e)}")
                
                # Process remaining documents
                await process_batch()
            
            return total_processed
            
        except Exception as e:
            self._logger.error(f"Error streaming file content from {source}: {str(e)}")
            return 0
    
    async def _load_single_file(self, file_path: Path, metadata: dict[str, Any]) -> list[Document]:
        """Load content from a single file."""
        if not self._is_supported_file(file_path):
            self._logger.debug(f"Skipping unsupported file: {file_path}")
            return []
        
        try:
            # Check file size limits
            max_file_size = self._config.get('max_file_size', 10 * 1024 * 1024)  # 10MB default
            if file_path.stat().st_size > max_file_size:
                self._logger.warning(f"File too large, skipping: {file_path} ({file_path.stat().st_size} bytes)")
                return []
            
            # Read file content based on extension
            if file_path.suffix.lower() == '.json':
                content = await self._load_json_file(file_path)
            elif file_path.suffix.lower() == '.csv':
                content = await self._load_csv_file(file_path)
            else:
                content = await self._load_text_file(file_path)
            
            if not content:
                return []
            
            # Create document metadata
            doc_metadata = {
                "source": str(file_path),
                "loader": "file",
                "file_name": file_path.name,
                "file_extension": file_path.suffix,
                "file_size": file_path.stat().st_size,
                "timestamp": time.strftime('%Y-%m-%dT%H:%M:%S'),
                **metadata
            }
            
            # Chunk large files
            chunks = self._chunk_content(content, file_path)
            documents = []
            
            for i, chunk in enumerate(chunks):
                chunk_metadata = {
                    **doc_metadata,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
                
                documents.append(Document(
                    content=chunk,
                    metadata=chunk_metadata,
                    source=str(file_path),
                    doc_id=f"{file_path}#chunk_{i}" if len(chunks) > 1 else str(file_path)
                ))
            
            return documents
            
        except Exception as e:
            self._logger.error(f"Error loading file {file_path}: {str(e)}")
            return []
    
    async def _load_directory(self, dir_path: Path, metadata: dict[str, Any]) -> list[Document]:
        """Load all supported files from a directory."""
        all_documents = []
        
        async for file_path in self._iterate_directory_files(dir_path):
            try:
                documents = await self._load_single_file(file_path, metadata)
                all_documents.extend(documents)
            except Exception as e:
                self._logger.error(f"Error loading file {file_path}: {str(e)}")
        
        self._logger.info(f"Loaded {len(all_documents)} documents from directory: {dir_path}")
        return all_documents
    
    async def _iterate_directory_files(self, dir_path: Path):
        """Async generator to iterate through directory files."""
        max_depth = self._config.get('max_directory_depth', 10)
        
        def _walk_directory(path: Path, current_depth: int = 0):
            """Recursively walk directory with depth limit."""
            if current_depth > max_depth:
                return
            
            try:
                for item in path.iterdir():
                    if item.is_file() and self._is_supported_file(item):
                        yield item
                    elif item.is_dir() and not item.name.startswith('.'):
                        yield from _walk_directory(item, current_depth + 1)
            except PermissionError:
                self._logger.warning(f"Permission denied accessing: {path}")
        
        for file_path in _walk_directory(dir_path):
            yield file_path
            # Allow other coroutines to run
            await asyncio.sleep(0)
    
    async def _load_text_file(self, file_path: Path) -> str:
        """Load text file content."""
        try:
            # Try UTF-8 first, fall back to other encodings
            encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    async with asyncio.to_thread(open, file_path, 'r', encoding=encoding) as f:
                        content = await asyncio.to_thread(f.read)
                        return content
                except UnicodeDecodeError:
                    continue
            
            self._logger.error(f"Could not decode file with any encoding: {file_path}")
            return ""
            
        except Exception as e:
            self._logger.error(f"Error reading text file {file_path}: {str(e)}")
            return ""
    
    async def _load_json_file(self, file_path: Path) -> str:
        """Load JSON file and convert to readable text."""
        try:
            async with asyncio.to_thread(open, file_path, 'r', encoding='utf-8') as f:
                data = await asyncio.to_thread(json.load, f)
                # Convert JSON to pretty-printed string
                return json.dumps(data, indent=2, ensure_ascii=False)
        except Exception as e:
            self._logger.error(f"Error reading JSON file {file_path}: {str(e)}")
            return ""
    
    async def _load_csv_file(self, file_path: Path) -> str:
        """Load CSV file and convert to readable text."""
        try:
            # Read CSV and convert to text representation
            content = await self._load_text_file(file_path)
            if not content:
                return ""
            
            # Add some structure to CSV content
            lines = content.split('\n')
            if lines:
                # Format as table-like structure
                formatted_lines = []
                for i, line in enumerate(lines[:100]):  # Limit to first 100 rows
                    if line.strip():
                        if i == 0:
                            formatted_lines.append(f"CSV Headers: {line}")
                        else:
                            formatted_lines.append(f"Row {i}: {line}")
                
                if len(lines) > 100:
                    formatted_lines.append(f"... and {len(lines) - 100} more rows")
                
                return '\n'.join(formatted_lines)
            
            return content
            
        except Exception as e:
            self._logger.error(f"Error reading CSV file {file_path}: {str(e)}")
            return ""
    
    def _is_supported_file(self, file_path: Path) -> bool:
        """Check if file is supported based on extension and configuration."""
        if file_path.suffix.lower() in self._supported_extensions:
            return True
        
        # Check if it's a text file by trying to read first few bytes
        if file_path.suffix.lower() not in ['.exe', '.bin', '.so', '.dll', '.img', '.iso']:
            try:
                with open(file_path, 'rb') as f:
                    sample = f.read(1024)
                    # Simple heuristic: if most bytes are printable, consider it text
                    printable_ratio = sum(1 for b in sample if 32 <= b <= 126 or b in [9, 10, 13]) / len(sample)
                    return printable_ratio > 0.7
            except Exception:
                pass
        
        return False
    
    def _chunk_content(self, content: str, file_path: Path) -> list[str]:
        """Chunk file content if it's too large."""
        chunk_size = self._config.get('chunk_size', 8000)
        
        if len(content) <= chunk_size:
            return [content]
        
        # For code files, try to chunk by logical boundaries
        if file_path.suffix.lower() in ['.py', '.js', '.ts', '.java', '.cpp', '.c']:
            return self._chunk_code_content(content, chunk_size)
        
        # For other files, use simple text chunking
        chunks = []
        for i in range(0, len(content), chunk_size):
            chunks.append(content[i:i + chunk_size])
        
        return chunks
    
    def _chunk_code_content(self, content: str, chunk_size: int) -> list[str]:
        """Chunk code content by logical boundaries (functions, classes)."""
        lines = content.split('\n')
        chunks = []
        current_chunk = []
        current_size = 0
        
        for line in lines:
            line_size = len(line) + 1  # +1 for newline
            
            # If adding this line would exceed chunk size and we have content, start new chunk
            if current_size + line_size > chunk_size and current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
                current_size = 0
            
            current_chunk.append(line)
            current_size += line_size
        
        # Add remaining content
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks