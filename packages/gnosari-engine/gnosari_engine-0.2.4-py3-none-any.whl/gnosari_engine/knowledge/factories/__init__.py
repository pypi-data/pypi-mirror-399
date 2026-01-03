"""
Knowledge provider factory system following SOLID principles.

Provides auto-discovery and registration capabilities for knowledge providers
while remaining open for extension but closed for modification.
"""

from .knowledge_factory import KnowledgeProviderFactory

__all__ = ["KnowledgeProviderFactory"]