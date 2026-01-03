"""
Enhanced Gnosari Runner with tool streaming support.

Extends the base GnosariRunner to add enterprise-grade tool streaming
capabilities following SOLID principles.
"""

import asyncio
import logging
from collections.abc import AsyncGenerator

from ..schemas.domain.execution import AgentRun
from ..tools.streaming.interfaces import IStreamableTool, IToolStreamContext
from .gnosari_runner import GnosariRunner
from .interfaces import ExecutionResult, StreamEvent

logger = logging.getLogger(__name__)


class StreamingEnhancedGnosariRunner(GnosariRunner):
    """
    Enhanced Gnosari Runner with tool streaming support.
    
    Follows Open/Closed Principle: Extends GnosariRunner without modifying it.
    Follows Single Responsibility Principle: Adds only streaming capabilities.
    """
    
    def __init__(
        self,
        provider_name: str | None = None,
        provider=None,
        provider_factory=None,
        enable_tool_streaming: bool = True,
        **provider_config
    ):
        super().__init__(provider_name, provider, provider_factory, **provider_config)

        self._enable_tool_streaming = enable_tool_streaming

        logger.debug(f"StreamingEnhancedGnosariRunner initialized with tool streaming: {enable_tool_streaming}")
    
    async def initialize(self) -> None:
        """Initialize the runner."""
        await super().initialize()

    async def cleanup(self) -> None:
        """Cleanup runner resources."""
        await super().cleanup()
    
    async def run_agent(self, agent_run: AgentRun) -> ExecutionResult:
        """Execute agent synchronously (no streaming)."""
        await self._ensure_initialized()

        return await super().run_agent(agent_run)
    
    async def run_agent_stream(
        self, agent_run: AgentRun
    ) -> AsyncGenerator[StreamEvent, None]:
        """Execute agent with enhanced tool streaming - ULTRA SIMPLE VERSION."""
        await self._ensure_initialized()

        if not self._enable_tool_streaming:
            # Fall back to standard streaming if tool streaming is disabled
            async for event in super().run_agent_stream(agent_run):
                yield event
            return

        try:
            # ULTRA-CLEAN: Create simple sync context with callback for real-time streaming
            from ..tools.streaming.sync_context import SyncToolStreamContext
            import asyncio

            # Queue to collect events from callback
            event_queue = asyncio.Queue()

            # Callback to immediately add events to queue
            def event_callback(event):
                try:
                    event_queue.put_nowait(event)
                except Exception as e:
                    logger.error(f"Error adding event to queue: {e}")

            sync_context = SyncToolStreamContext(event_callback=event_callback)

            # Register context in global registry by session ID
            session_id = agent_run.metadata.session_id if agent_run.metadata else None
            if session_id:
                from ..tools.streaming.registry import StreamContextRegistry
                StreamContextRegistry.register(session_id, sync_context)
                logger.info(f"Registered sync stream context for session: {session_id}")

            # Initialize knowledge bases if any are defined in the team
            if agent_run.team.knowledge:
                await self._initialize_knowledge_bases(agent_run.team.knowledge)

            # REAL-TIME STREAMING: Merge agent and tool events with background polling
            agent_stream = self._get_agent_stream(agent_run)
            agent_completed = False
            agent_task = None

            try:
                # Create async iterator for agent events
                agent_iter = agent_stream.__aiter__()

                # Poll for events (agent or tool) with timeout
                while not agent_completed:
                    # Try to get next agent event (non-blocking with timeout)
                    if agent_task is None:
                        agent_task = asyncio.create_task(agent_iter.__anext__())

                    # Wait for either an agent event or timeout
                    done, pending = await asyncio.wait(
                        [agent_task],
                        timeout=0.05  # Check every 50ms for tool events
                    )

                    # Yield any tool events that arrived
                    while not event_queue.empty():
                        try:
                            tool_event = event_queue.get_nowait()
                            stream_event = tool_event.to_stream_event()
                            if self._context_enricher:
                                yield self._context_enricher.enrich_event(stream_event)
                            else:
                                yield stream_event
                        except asyncio.QueueEmpty:
                            break

                    # If agent event arrived, yield it
                    if agent_task in done:
                        try:
                            agent_event = agent_task.result()
                            agent_task = None  # Reset for next iteration

                            if self._context_enricher:
                                yield self._context_enricher.enrich_event(agent_event)
                            else:
                                yield agent_event

                            # Check for completion
                            if agent_event.event_type in ("agent_completed", "agent_error"):
                                agent_completed = True
                                break
                        except StopAsyncIteration:
                            agent_completed = True
                            break

                # After agent completes, drain remaining tool events
                while not event_queue.empty():
                    try:
                        tool_event = event_queue.get_nowait()
                        stream_event = tool_event.to_stream_event()
                        if self._context_enricher:
                            yield self._context_enricher.enrich_event(stream_event)
                        else:
                            yield stream_event
                    except asyncio.QueueEmpty:
                        break

            finally:
                # Cancel any pending agent task
                if agent_task and not agent_task.done():
                    agent_task.cancel()
                    try:
                        await agent_task
                    except (asyncio.CancelledError, StopAsyncIteration):
                        pass

        except Exception as e:
            import traceback
            logger.error(f"Error in enhanced streaming: {e}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            # Emit error event
            if self._context_enricher:
                yield self._context_enricher.create_error_event(e)
            else:
                yield StreamEvent("execution_error", {"error": str(e), "error_type": type(e).__name__})
        finally:
            # ULTRA-CLEAN: Unregister context from global registry
            session_id = agent_run.metadata.session_id if agent_run.metadata else None
            if session_id:
                from ..tools.streaming.registry import StreamContextRegistry
                StreamContextRegistry.unregister(session_id)
                logger.info(f"Unregistered stream context for session: {session_id}")
    
    async def _get_agent_stream(self, agent_run: AgentRun) -> AsyncGenerator[StreamEvent, None]:
        """Get the base agent stream."""
        try:
            # Call the parent's stream method directly
            stream = self._initializer.provider.run_agent_stream(agent_run)
            async for event in stream:
                yield event
        except Exception as e:
            logger.error(f"Error in agent stream: {e}")
            yield StreamEvent("agent_error", {"error": str(e)})
    
    
    async def switch_provider(self, provider_name: str, **provider_config) -> None:
        """Switch provider."""
        await super().switch_provider(provider_name, **provider_config)
    
    def enable_tool_streaming(self) -> None:
        """Enable tool streaming at runtime."""
        self._enable_tool_streaming = True
        logger.info("Tool streaming enabled")
    
    def disable_tool_streaming(self) -> None:
        """Disable tool streaming at runtime."""
        self._enable_tool_streaming = False
        logger.info("Tool streaming disabled")
    
    def is_tool_streaming_enabled(self) -> bool:
        """Check if tool streaming is enabled."""
        return self._enable_tool_streaming
    
    def get_streaming_stats(self) -> dict[str, any]:
        """Get streaming statistics for monitoring."""
        return {
            "tool_streaming_enabled": self._enable_tool_streaming,
            "provider_name": self.provider_name,
            "is_initialized": self.is_initialized
        }