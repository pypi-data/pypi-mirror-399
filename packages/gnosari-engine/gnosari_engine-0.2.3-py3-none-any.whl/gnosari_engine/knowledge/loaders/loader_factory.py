"""
Loader factory for knowledge loaders following Open/Closed principle.
Registry for all loaders that allows easy extension without modification.
"""

import logging
from typing import Any

from ..interfaces import IKnowledgeLoader
from .website import WebsiteLoader
from .sitemap import SitemapLoader
from .file import FileLoader


class LoaderFactory:
    """Factory for knowledge loaders following Open/Closed principle."""
    
    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize loader factory with default loaders.
        
        Args:
            config: Optional configuration passed to loaders
        """
        self._config = config or {}
        self._logger = logging.getLogger(__name__)
        
        # Initialize default loaders
        self._loaders: list[IKnowledgeLoader] = [
            WebsiteLoader(self._config.get('website', {})),
            SitemapLoader(self._config.get('sitemap', {})),
            FileLoader(self._config.get('file', {})),
        ]
        
        self._logger.info(f"LoaderFactory initialized with {len(self._loaders)} default loaders")
    
    def register_loader(self, loader: IKnowledgeLoader) -> None:
        """
        Register new loader (Open/Closed principle).
        
        Args:
            loader: IKnowledgeLoader implementation to register
        """
        if not isinstance(loader, IKnowledgeLoader):
            raise TypeError(f"Loader must implement IKnowledgeLoader protocol, got {type(loader)}")
        
        self._loaders.append(loader)
        self._logger.info(f"Registered new loader: {type(loader).__name__}")
    
    def get_loader(self, source_type: str) -> IKnowledgeLoader | None:
        """
        Get appropriate loader for source type.
        
        Args:
            source_type: Type of source to load (website, sitemap, file, etc.)
            
        Returns:
            Loader that supports the source type, or None if not found
        """
        for loader in self._loaders:
            if loader.supports_source_type(source_type):
                self._logger.debug(f"Found loader for source type '{source_type}': {type(loader).__name__}")
                return loader
        
        self._logger.warning(f"No loader found for source type: {source_type}")
        return None
    
    def supports_source_type(self, source_type: str) -> bool:
        """
        Check if any loader supports this source type.
        
        Args:
            source_type: Type of source to check
            
        Returns:
            True if any loader supports this source type
        """
        return any(loader.supports_source_type(source_type) for loader in self._loaders)
    
    def get_supported_source_types(self) -> list[str]:
        """
        Get all supported source types from all registered loaders.
        
        Returns:
            List of supported source types
        """
        supported_types = set()
        
        # Common source types to check
        known_types = [
            "website", "sitemap", "file", "pdf", "text", "csv", 
            "json", "directory", "local", "url", "http", "https"
        ]
        
        for source_type in known_types:
            if self.supports_source_type(source_type):
                supported_types.add(source_type)
        
        return sorted(list(supported_types))
    
    def get_loader_info(self) -> dict[str, Any]:
        """
        Get information about all registered loaders.
        
        Returns:
            Dictionary with loader information
        """
        loaders_info = []
        
        for loader in self._loaders:
            loader_info = {
                "class_name": type(loader).__name__,
                "module": type(loader).__module__,
                "supported_types": []
            }
            
            # Test common source types
            test_types = [
                "website", "sitemap", "file", "pdf", "text", "csv",
                "json", "directory", "local", "url"
            ]
            
            for test_type in test_types:
                if loader.supports_source_type(test_type):
                    loader_info["supported_types"].append(test_type)
            
            loaders_info.append(loader_info)
        
        return {
            "total_loaders": len(self._loaders),
            "loaders": loaders_info,
            "supported_source_types": self.get_supported_source_types()
        }
    
    async def load_data_with_auto_detection(
        self, 
        source: str, 
        source_type: str | None = None,
        **options: Any
    ) -> list[Any]:
        """
        Load data with automatic source type detection.
        
        Args:
            source: Source to load from
            source_type: Optional explicit source type. If None, will auto-detect
            **options: Additional loading options
            
        Returns:
            List of documents loaded from the source
        """
        # Auto-detect source type if not provided
        if source_type is None:
            source_type = self._detect_source_type(source)
            self._logger.info(f"Auto-detected source type for '{source}': {source_type}")
        
        # Get appropriate loader
        loader = self.get_loader(source_type)
        if not loader:
            raise ValueError(f"No loader available for source type: {source_type}")
        
        # Load data using the appropriate loader
        return await loader.load_data(source, **options)
    
    def _detect_source_type(self, source: str) -> str:
        """
        Auto-detect source type based on source string.
        
        Args:
            source: Source string to analyze
            
        Returns:
            Detected source type
        """
        source_lower = source.lower()
        
        # URL detection
        if source_lower.startswith(('http://', 'https://')):
            if 'sitemap' in source_lower or source_lower.endswith('.xml'):
                return "sitemap"
            else:
                return "website"
        
        # File path detection
        if source_lower.endswith('.xml') and ('sitemap' in source_lower or 'site-map' in source_lower):
            return "sitemap"
        elif source_lower.endswith('.pdf'):
            return "pdf"
        elif source_lower.endswith('.csv'):
            return "csv"
        elif source_lower.endswith('.json'):
            return "json"
        elif source_lower.endswith(('.txt', '.md', '.rst', '.log')):
            return "text"
        
        # Check if it's a file path
        import os
        if os.path.exists(source):
            if os.path.isdir(source):
                return "directory"
            else:
                return "file"
        
        # Default fallback
        return "website"