"""
Stream result processor implementation following extreme SOLID principles.
Handles stream event aggregation with clean separation of concerns.
"""

import logging
from collections.abc import AsyncGenerator

from .interfaces import IStreamResultProcessor
from ..interfaces import StreamEvent

logger = logging.getLogger(__name__)


class StreamProcessorError(Exception):
    """Stream processor specific errors."""
    pass


class DefaultStreamResultProcessor(IStreamResultProcessor):
    """
    Default implementation for processing streaming execution results.
    
    Follows SOLID Principles:
    - Single Responsibility: Only processes and aggregates stream results
    - Open/Closed: Open for extension via inheritance, closed for modification
    - Liskov Substitution: Can be substituted for any IStreamResultProcessor
    - Interface Segregation: Focused interface for result processing only
    - Dependency Inversion: Depends on StreamEvent abstraction
    
    Usage:
        processor = DefaultStreamResultProcessor()
        result = await processor.collect_team_result(stream)
    """

    def __init__(self, default_team_message: str = "Team execution completed", 
                 default_agent_message: str = "Agent execution completed"):
        """
        Initialize processor with default messages.
        
        Args:
            default_team_message: Default message when no team result found
            default_agent_message: Default message when no agent result found
        """
        self._default_team_message = default_team_message
        self._default_agent_message = default_agent_message
        logger.debug("DefaultStreamResultProcessor initialized")

    async def collect_team_result(self, stream: AsyncGenerator[StreamEvent, None]) -> str:
        """
        Collect and aggregate team execution results from stream.

        Args:
            stream: AsyncGenerator of StreamEvent objects

        Returns:
            Aggregated result string from team execution
            
        Raises:
            StreamProcessorError: If stream processing fails
        """
        try:
            result_data = ""
            event_count = 0
            
            async for event in stream:
                event_count += 1
                logger.debug(f"Processing team event {event_count}: {event.event_type}")
                
                if event.event_type in ("team_result", "workflow_completed", "team_completed"):
                    result_data = event.data.get("result", self._default_team_message)
                    logger.debug(f"Found team result: {result_data[:100]}...")
                    break
                    
            if not result_data and event_count > 0:
                result_data = self._default_team_message
                logger.warning("No team result found in stream, using default message")
            elif event_count == 0:
                logger.warning("Empty stream received for team execution")
                result_data = self._default_team_message
                
            logger.info(f"Team result collection completed: {len(result_data)} characters")
            return result_data
            
        except Exception as e:
            raise StreamProcessorError(f"Failed to collect team result: {e}") from e

    async def collect_agent_result(self, stream: AsyncGenerator[StreamEvent, None]) -> str:
        """
        Collect and aggregate agent execution results from stream.

        Args:
            stream: AsyncGenerator of StreamEvent objects

        Returns:
            Aggregated result string from agent execution
            
        Raises:
            StreamProcessorError: If stream processing fails
        """
        try:
            result_data = ""
            event_count = 0
            
            async for event in stream:
                event_count += 1
                logger.debug(f"Processing agent event {event_count}: {event.event_type}")
                
                if event.event_type in ("agent_result", "agent_response", "agent_completed"):
                    result_data = event.data.get("result", self._default_agent_message)
                    logger.debug(f"Found agent result: {result_data[:100]}...")
                    break
                    
            if not result_data and event_count > 0:
                result_data = self._default_agent_message
                logger.warning("No agent result found in stream, using default message")
            elif event_count == 0:
                logger.warning("Empty stream received for agent execution")
                result_data = self._default_agent_message
                
            logger.info(f"Agent result collection completed: {len(result_data)} characters")
            return result_data
            
        except Exception as e:
            raise StreamProcessorError(f"Failed to collect agent result: {e}") from e


class VerboseStreamResultProcessor(DefaultStreamResultProcessor):
    """
    Verbose stream processor that collects all events for debugging.
    Follows Open/Closed Principle - extends without modifying base class.
    """

    async def collect_team_result(self, stream: AsyncGenerator[StreamEvent, None]) -> str:
        """Collect team result with verbose logging of all events."""
        all_events = []
        result_data = ""
        
        async for event in stream:
            all_events.append(f"[{event.event_type}] {event.data}")
            if event.event_type in ("team_result", "workflow_completed", "team_completed"):
                result_data = event.data.get("result", self._default_team_message)
                
        if not result_data:
            result_data = self._default_team_message
            
        # Add verbose information to result
        verbose_info = f"\n\nDebug Events ({len(all_events)} total):\n" + "\n".join(all_events[-5:])  # Last 5 events
        return result_data + verbose_info

    async def collect_agent_result(self, stream: AsyncGenerator[StreamEvent, None]) -> str:
        """Collect agent result with verbose logging of all events."""
        all_events = []
        result_data = ""
        
        async for event in stream:
            all_events.append(f"[{event.event_type}] {event.data}")
            if event.event_type in ("agent_result", "agent_response", "agent_completed"):
                result_data = event.data.get("result", self._default_agent_message)
                
        if not result_data:
            result_data = self._default_agent_message
            
        # Add verbose information to result
        verbose_info = f"\n\nDebug Events ({len(all_events)} total):\n" + "\n".join(all_events[-5:])  # Last 5 events
        return result_data + verbose_info


def create_default_stream_processor() -> DefaultStreamResultProcessor:
    """
    Create default stream processor.
    Follows Factory Method pattern for consistent setup.
    
    Returns:
        DefaultStreamResultProcessor instance
    """
    return DefaultStreamResultProcessor()


def create_verbose_stream_processor() -> VerboseStreamResultProcessor:
    """
    Create verbose stream processor for debugging.
    
    Returns:
        VerboseStreamResultProcessor instance
    """
    return VerboseStreamResultProcessor()