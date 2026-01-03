"""
Redis-based session event publisher implementation.
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse

try:
    import redis.asyncio as redis
    from redis.asyncio import Redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None
    Redis = None

from .interfaces import ISessionEventPublisher
from .models import MessagesAddedEvent, SessionCreatedEvent, SessionClearedEvent
from ...schemas.domain.execution import AgentRunMetadata

logger = logging.getLogger(__name__)


class RedisSessionEventPublisher(ISessionEventPublisher):
    """
    Redis-based implementation of session event publisher.
    
    Publishes events to Redis channels for real-time session monitoring.
    Uses the pattern: session:{session_id} for session-specific events
    and session.messages_added for global message events.
    """
    
    def __init__(
        self, 
        redis_url: str = "redis://localhost:6379/0",
        connection_timeout: int = 5,
        retry_attempts: int = 3,
        **redis_kwargs
    ):
        """
        Initialize Redis event publisher.
        
        Args:
            redis_url: Redis connection URL
            connection_timeout: Connection timeout in seconds
            retry_attempts: Number of retry attempts for failed operations
            **redis_kwargs: Additional Redis connection arguments
        """
        if not REDIS_AVAILABLE:
            raise ImportError(
                "redis package is required for RedisSessionEventPublisher. "
                "Install with: pip install redis"
            )
        
        self._redis_url = redis_url
        self._connection_timeout = connection_timeout
        self._retry_attempts = retry_attempts
        self._redis_kwargs = redis_kwargs
        self._redis_client: Optional[Redis] = None
        self._connection_available = True
        self._lock = asyncio.Lock()
    
    async def _get_redis_client(self) -> Optional[Redis]:
        """Get or create Redis client with connection pooling."""
        if not self._connection_available:
            return None
        
        if self._redis_client is None:
            async with self._lock:
                if self._redis_client is None:
                    try:
                        # Parse Redis URL for connection parameters
                        parsed_url = urlparse(self._redis_url)
                        
                        connection_kwargs = {
                            "host": parsed_url.hostname or "localhost",
                            "port": parsed_url.port or 6379,
                            "db": int(parsed_url.path.lstrip("/")) if parsed_url.path.lstrip("/") else 0,
                            "socket_connect_timeout": self._connection_timeout,
                            "socket_timeout": self._connection_timeout,
                            "retry_on_timeout": True,
                            "health_check_interval": 30,
                            **self._redis_kwargs
                        }
                        
                        if parsed_url.password:
                            connection_kwargs["password"] = parsed_url.password
                        
                        self._redis_client = redis.Redis(**connection_kwargs)
                        
                        # Test connection
                        await asyncio.wait_for(
                            self._redis_client.ping(), 
                            timeout=self._connection_timeout
                        )
                        
                        logger.info(f"Redis connection established: {self._redis_url}")
                        
                    except Exception as e:
                        logger.error(f"Failed to connect to Redis: {e}")
                        self._connection_available = False
                        self._redis_client = None
                        return None
        
        return self._redis_client
    
    async def _publish_with_retry(
        self, 
        channel: str, 
        message: str,
        session_channel: Optional[str] = None
    ) -> None:
        """
        Publish message to Redis with retry logic.
        
        Args:
            channel: Primary channel to publish to
            message: JSON message to publish
            session_channel: Optional session-specific channel
        """
        if not self._connection_available:
            logger.warning("Redis connection unavailable, skipping event publication")
            return
        
        for attempt in range(self._retry_attempts):
            try:
                redis_client = await self._get_redis_client()
                if redis_client is None:
                    return
                
                async with asyncio.timeout(self._connection_timeout):
                    # Publish to primary channel
                    await redis_client.publish(channel, message)
                    
                    # Publish to session-specific channel if provided
                    if session_channel:
                        await redis_client.publish(session_channel, message)
                    
                    logger.debug(f"Published event to Redis channels: {channel}" + 
                               (f", {session_channel}" if session_channel else ""))
                    return
                    
            except (redis.RedisError, asyncio.TimeoutError) as e:
                logger.warning(f"Redis publish attempt {attempt + 1} failed: {e}")
                if attempt == self._retry_attempts - 1:
                    logger.error(f"Failed to publish event after {self._retry_attempts} attempts")
                    self._connection_available = False
                else:
                    await asyncio.sleep(0.1 * (attempt + 1))  # Exponential backoff
            except Exception as e:
                logger.error(f"Unexpected error publishing to Redis: {e}")
                break
    
    async def publish_messages_added(
        self, 
        session_id: str, 
        message_count: int,
        messages_data: List[str],
        metadata: Optional[AgentRunMetadata] = None
    ) -> None:
        """
        Publish messages added event to Redis.
        
        Publishes to both:
        - session.messages_added (global channel)
        - session:{session_id} (session-specific channel)
        """
        event = MessagesAddedEvent.create(session_id, message_count, messages_data, metadata)
        message = json.dumps(event.model_dump(), separators=(",", ":"))
        
        await self._publish_with_retry(
            channel="session.messages_added",
            message=message,
            session_channel=f"session:{session_id}"
        )
    
    async def publish_session_created(
        self, 
        session_id: str,
        metadata: Optional[AgentRunMetadata] = None
    ) -> None:
        """
        Publish session created event to Redis.
        
        Publishes to both:
        - session.created (global channel)
        - session:{session_id} (session-specific channel)
        """
        event = SessionCreatedEvent.create(session_id, metadata)
        message = json.dumps(event.model_dump(), separators=(",", ":"))
        
        await self._publish_with_retry(
            channel="session.created",
            message=message,
            session_channel=f"session:{session_id}"
        )
    
    async def publish_session_cleared(
        self, 
        session_id: str,
        metadata: Optional[AgentRunMetadata] = None
    ) -> None:
        """
        Publish session cleared event to Redis.
        
        Publishes to both:
        - session.cleared (global channel)
        - session:{session_id} (session-specific channel)
        """
        event = SessionClearedEvent.create(session_id, metadata)
        message = json.dumps(event.model_dump(), separators=(",", ":"))
        
        await self._publish_with_retry(
            channel="session.cleared",
            message=message,
            session_channel=f"session:{session_id}"
        )
    
    async def cleanup(self) -> None:
        """Clean up Redis connection."""
        if self._redis_client is not None:
            try:
                await self._redis_client.aclose()
                logger.debug("Redis connection closed")
            except Exception as e:
                logger.warning(f"Error closing Redis connection: {e}")
            finally:
                self._redis_client = None
                self._connection_available = True