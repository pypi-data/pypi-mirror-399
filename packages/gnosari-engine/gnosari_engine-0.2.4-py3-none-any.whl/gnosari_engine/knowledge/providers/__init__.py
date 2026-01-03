"""
Knowledge providers module.

Contains implementations of IKnowledgeProvider for different backends:
- OpenSearchKnowledgeProvider: OpenSearch-based knowledge provider
- (Future providers can be added here following Open/Closed principle)
"""

from .opensearch import OpenSearchKnowledgeProvider, OpenSearchKnowledgeBase

__all__ = [
    "OpenSearchKnowledgeProvider",
    "OpenSearchKnowledgeBase",
]