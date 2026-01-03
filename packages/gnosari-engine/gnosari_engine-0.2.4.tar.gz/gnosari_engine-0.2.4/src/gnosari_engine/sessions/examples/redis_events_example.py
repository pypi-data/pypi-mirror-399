"""
Example usage of Redis session event publishing.

This example demonstrates how to use the session event publishing system
with Redis for real-time monitoring of session activities.
"""

import asyncio
import logging
from typing import Optional

from ..events import (
    SessionProviderWithEventsFactory,
    create_event_publisher,
    REDIS_PUBLISHER_AVAILABLE
)
from ...schemas.domain.execution import AgentRun, AgentRunMetadata

# Configure logging to see event publishing in action
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_session_with_events():
    """
    Example of creating and using a session with Redis event publishing.
    """
    
    if not REDIS_PUBLISHER_AVAILABLE:
        logger.warning("Redis is not available. Install with: pip install redis")
        return
    
    # Create mock AgentRun with metadata
    metadata = AgentRunMetadata(
        account_id=123,
        team_id=456,
        agent_id=789,
        team_identifier="example_team",
        agent_identifier="example_agent",
        session_id="session_123"
    )
    
    # For a complete AgentRun, you would normally have agent and team objects
    # This is a simplified example focusing on the event publishing
    
    session_id = "example_session_001"
    
    # Method 1: Create session provider with events using factory
    logger.info("Creating session provider with Redis events...")
    
    try:
        provider = SessionProviderWithEventsFactory.create_openai_database_provider_with_events(
            session_id=session_id,
            agent_run=None,  # Would normally have full AgentRun object
            event_publisher_type="redis",
            redis_url="redis://localhost:6379/0"
        )
        
        # Initialize the provider
        await provider.initialize()
        
        # Get the session implementation
        session = provider.get_session_implementation()
        
        # Simulate adding messages (this will trigger events)
        logger.info("Adding messages to session...")
        
        # Mock message items (would normally be actual conversation items)
        mock_messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        
        await session.add_items(mock_messages)
        
        # Simulate clearing session (this will trigger events)
        logger.info("Clearing session...")
        await session.clear_session()
        
        # Clean up
        await provider.cleanup()
        
        logger.info("Example completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in example: {e}")


async def example_direct_event_publisher():
    """
    Example of using event publisher directly.
    """
    
    if not REDIS_PUBLISHER_AVAILABLE:
        logger.warning("Redis is not available. Install with: pip install redis")
        return
    
    logger.info("Creating Redis event publisher directly...")
    
    try:
        # Create event publisher directly
        publisher = create_event_publisher(
            publisher_type="redis",
            redis_url="redis://localhost:6379/0"
        )
        
        # Create mock metadata
        metadata = AgentRunMetadata(
            account_id=123,
            team_id=456,
            agent_id=789,
            team_identifier="direct_example_team",
            agent_identifier="direct_example_agent"
        )
        
        session_id = "direct_example_session"
        
        # Publish various events
        logger.info("Publishing session created event...")
        await publisher.publish_session_created(session_id, metadata)
        
        logger.info("Publishing messages added event...")
        mock_messages_data = [
            '{"role": "user", "content": "Hello"}',
            '{"role": "assistant", "content": "Hi there!"}',
            '{"role": "user", "content": "How are you?"}'
        ]
        await publisher.publish_messages_added(session_id, 3, mock_messages_data, metadata)
        
        logger.info("Publishing session cleared event...")
        await publisher.publish_session_cleared(session_id, metadata)
        
        # Clean up
        await publisher.cleanup()
        
        logger.info("Direct publisher example completed!")
        
    except Exception as e:
        logger.error(f"Error in direct publisher example: {e}")


async def example_redis_subscriber():
    """
    Example Redis subscriber to monitor session events.
    
    This would typically run in a separate process/service.
    """
    
    if not REDIS_PUBLISHER_AVAILABLE:
        logger.warning("Redis is not available. Install with: pip install redis")
        return
    
    try:
        import redis.asyncio as redis
        
        # Create Redis client for subscribing
        redis_client = redis.Redis.from_url("redis://localhost:6379/0")
        
        # Subscribe to session events
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(
            "session.messages_added",
            "session.created", 
            "session.cleared",
            "session:example_session_001",  # Session-specific events
            "session:direct_example_session"
        )
        
        logger.info("Listening for session events... (Press Ctrl+C to stop)")
        
        async for message in pubsub.listen():
            if message['type'] == 'message':
                channel = message['channel'].decode('utf-8')
                data = message['data'].decode('utf-8')
                logger.info(f"Received event on {channel}: {data}")
        
        await redis_client.aclose()
        
    except Exception as e:
        logger.error(f"Error in subscriber example: {e}")


if __name__ == "__main__":
    logger.info("Starting Redis session events examples...")
    
    # Run the examples
    asyncio.run(example_session_with_events())
    asyncio.run(example_direct_event_publisher())
    
    logger.info("Examples completed. You can run the subscriber example separately.")
    logger.info("To monitor events in real-time, run: python -c \"import asyncio; from examples.redis_events_example import example_redis_subscriber; asyncio.run(example_redis_subscriber())\"")