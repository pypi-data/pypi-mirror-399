"""
Tool factory system following Open/Closed Principle.

Provides auto-discovery and registration capabilities while remaining
closed for modification but open for extension.
"""

from .interfaces import IToolFactory
from .tool_factory import AutoDiscoveryToolFactory

__all__ = ["IToolFactory", "AutoDiscoveryToolFactory"]