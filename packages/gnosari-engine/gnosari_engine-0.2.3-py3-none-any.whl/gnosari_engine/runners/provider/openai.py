"""
OpenAI provider strategy implementation.
Clean implementation following SOLID principles and ProviderStrategy protocol.
"""

import asyncio
import logging
import os
from collections.abc import AsyncGenerator
from typing import List

from agents import AgentUpdatedStreamEvent
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from ...schemas.domain.execution import AgentRun
from ..interfaces import ExecutionResult, ExecutionStatus
from ..events import StreamEvent, EventFactory, EventType
from ...sessions.gnosari_session import GnosariSession
from ...tools.components import ToolManager
from .openai_agent_factory import OpenAIAgentFactory

logger = logging.getLogger(__name__)


class OpenAIProviderError(Exception):
    """OpenAI provider specific errors."""
    pass


class OpenAIProvider:
    """
    OpenAI provider strategy implementation.
    
    Follows SOLID Principles:
    - Single Responsibility: Handles only OpenAI execution logic
    - Open/Closed: Extensible for new OpenAI features, closed for modification
    - Liskov Substitution: Implements ProviderStrategy protocol correctly
    - Interface Segregation: Only implements required provider methods
    - Dependency Inversion: Can be injected into GnosariRunner
    """

    def __init__(self):
        self._api_key: str | None = None
        self._agent = None
        self._runner = None
        self._session_manager: GnosariSession | None = None
        self._tool_manager: ToolManager | None = None
        self._agent_factory: OpenAIAgentFactory | None = None
        self._is_initialized = False

    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return "openai"

    async def initialize(self, **config) -> None:
        """Initialize OpenAI provider with configuration."""
        logger.debug("Initializing OpenAI provider")
        
        if self._is_initialized:
            logger.debug("OpenAI provider already initialized")
            return

        # Get API key from config or environment
        self._api_key = (
            config.get("api_key") or 
            config.get("default_api_key") or 
            os.getenv("OPENAI_API_KEY")
        )

        if not self._api_key:
            logger.error("OpenAI API key not found in config or environment")
            raise OpenAIProviderError(
                "OpenAI API key is required. Set OPENAI_API_KEY environment variable "
                "or pass 'api_key' in configuration."
            )

        logger.debug(f"OpenAI API key found (length: {len(self._api_key) if self._api_key else 0})")

        try:
            # Import and create OpenAI agent
            from agents import Agent, Runner
            
            # Set the API key
            os.environ["OPENAI_API_KEY"] = self._api_key
            
            # Initialize tool manager for OpenAI provider
            self._tool_manager = ToolManager(provider_name=self.provider_name)
            await self._tool_manager.initialize(**config)
            
            # Initialize agent factory with MCP support
            self._agent_factory = OpenAIAgentFactory(self._tool_manager)
            
            logger.info("OpenAI provider initialized with agents SDK, tool manager, and agent factory")
            self._is_initialized = True
            logger.debug("OpenAI provider initialization completed successfully")
        except ImportError as e:
            logger.error(f"OpenAI agents package import failed: {e}")
            raise OpenAIProviderError(
                "OpenAI agents package not found. Install with: pip install agents"
            ) from e
        except Exception as e:
            logger.error(f"OpenAI provider initialization failed: {e}")
            raise OpenAIProviderError(f"Failed to initialize OpenAI provider: {e}") from e

    async def cleanup(self) -> None:
        """Cleanup OpenAI provider resources."""
        try:
            logger.debug("Cleaning up OpenAI provider")
            
            if self._session_manager is not None:
                await self._session_manager.cleanup()
                self._session_manager = None
            if self._tool_manager is not None:
                await self._tool_manager.cleanup()
                self._tool_manager = None
            if self._agent_factory is not None:
                self._agent_factory.clear_cache()
                self._agent_factory = None
            self._agent = None
            self._runner = None
            self._is_initialized = False
            
            logger.debug("OpenAI provider cleanup completed")
        except Exception as e:
            logger.error(f"Error during OpenAI provider cleanup: {e}")


    
    async def _create_session_for_agent(self, agent_run: AgentRun) -> GnosariSession:
        """Create session manager for agent execution."""
        logger.debug(f"Creating session for agent execution: agent_id={agent_run.agent.id}, team_id={agent_run.team.id}")
        
        # Strict validation - metadata should never be None due to default_factory
        if agent_run.metadata is None:
            raise OpenAIProviderError(
                f"AgentRun metadata is None for agent {agent_run.agent.id}. "
                f"This indicates a serious issue with AgentRun construction."
            )
        
        # Resolve session_id: use from agent_run.metadata if available, otherwise auto-generate
        session_id = agent_run.metadata.session_id
        
        if not session_id:
            session_id = f"{agent_run.agent.id}-{id(agent_run)}"
            logger.debug(f"Auto-generated session_id: {session_id}")
            # Store the generated session_id in metadata for consistency
            agent_run.metadata.session_id = session_id
        else:
            logger.debug(f"Using provided session_id: {session_id}")
        
        logger.debug(f"Using session_id: {session_id}")
        logger.debug(f"Session details: team_id={agent_run.team.id}, agent_id={agent_run.agent.id}")
        
        # Create session manager with resolved session_id - no SessionContext needed
        logger.debug(f"Creating GnosariSession with provider 'openai_database' for session {session_id}")
        session_manager = GnosariSession(
            session_id=session_id,
            provider_name="openai_database",
            agent_run=agent_run  # Pass AgentRun directly
        )
        
        logger.debug(f"Session manager created successfully for session {session_id}")
        return session_manager

    async def _create_agent_with_tools(self, agent_run: AgentRun):
        """Create OpenAI agent with configured tools, delegations, and handoffs."""
        if not self._agent_factory:
            raise OpenAIProviderError("Agent factory not initialized")

        # Create agent and get MCP configs for unified async context management
        # Pass agent_run to ensure tools get session_id and other metadata
        openai_agent, main_agent_mcp_configs = await self._agent_factory.create_agent_with_relations(
            agent_run.agent, agent_run.team, agent_run=agent_run
        )
        
        # Collect MCP configs from ALL agents (delegations + handoffs) for unified context
        all_mcp_configs = list(main_agent_mcp_configs)  # Start with main agent configs
        
        # Collect configs from delegation agents
        for delegation in agent_run.agent.delegations:
            target_agent = delegation.target_agent
            if not target_agent:
                target_agent = self._agent_factory._find_agent_in_team(delegation.target_agent_id, agent_run.team)
            if target_agent:
                delegation_mcp_configs = self._agent_factory._get_mcp_configs(target_agent, agent_run.team)
                all_mcp_configs.extend(delegation_mcp_configs)
                logger.debug(f"Added {len(delegation_mcp_configs)} MCP configs from delegation agent {target_agent.id}")
        
        # Collect configs from handoff agents
        for handoff in agent_run.agent.handoffs:
            target_agent = handoff.target_agent
            if not target_agent:
                target_agent = self._agent_factory._find_agent_in_team(handoff.target_agent_id, agent_run.team)
            if target_agent:
                handoff_mcp_configs = self._agent_factory._get_mcp_configs(target_agent, agent_run.team)
                all_mcp_configs.extend(handoff_mcp_configs)
                logger.debug(f"Added {len(handoff_mcp_configs)} MCP configs from handoff agent {target_agent.id}")
        
        logger.debug(f"Created agent with {len(all_mcp_configs)} total MCP configs for unified async context management")
        return openai_agent, all_mcp_configs


    async def run_agent(self, agent_run: AgentRun) -> ExecutionResult:
        """Execute agent synchronously with session persistence."""
        # Strict validation - fail fast if agent_run is invalid
        if agent_run is None:
            raise OpenAIProviderError("agent_run parameter cannot be None")
        if agent_run.agent is None:
            raise OpenAIProviderError("agent_run.agent cannot be None")
        if agent_run.team is None:
            raise OpenAIProviderError("agent_run.team cannot be None")
        if not agent_run.message:
            raise OpenAIProviderError("agent_run.message cannot be empty")
            
        logger.debug(f"Starting synchronous agent execution: agent_id={agent_run.agent.id}, message='{agent_run.message[:100]}...'")
        self._ensure_initialized()
        
        try:
            # Import OpenAI agents for execution
            from agents import Agent, Runner
            
            # Create session manager for this agent execution
            logger.debug(f"Creating session manager for agent {agent_run.agent.id}")
            session_manager = await self._create_session_for_agent(agent_run)
            
            try:
                # Get SessionABC implementation for OpenAI agent
                logger.debug(f"Getting session implementation for session {agent_run.metadata.session_id}")
                openai_session = await session_manager.get_session()
                logger.info(f"Retrieved session implementation of type {type(openai_session).__name__} for agent {agent_run.agent.id}")
                logger.debug(f"AgentRun context passed to OpenAI: team_id={agent_run.team.id}, agent_id={agent_run.agent.id}")
                
                # Create agent with tools, delegations, and handoffs
                logger.debug(f"Creating OpenAI Agent with relations: name={agent_run.agent.name}")
                agent, mcp_configs = await self._create_agent_with_tools(agent_run)
                
                # Use agent's actual message
                message = agent_run.message
                logger.debug(f"Executing agent with message: '{message[:100]}...' and session {agent_run.metadata.session_id}")

                # Create all MCP servers in unified async context
                if mcp_configs:
                    # Deduplicate MCP configs to avoid duplicate servers
                    unique_mcp_configs = self._deduplicate_mcp_configs(mcp_configs)
                    logger.debug(f"Creating {len(unique_mcp_configs)} unique MCP servers (from {len(mcp_configs)} total configs) in unified async context")
                    
                    # Create all MCP servers in this context using the factory
                    if not self._agent_factory or not self._agent_factory._mcp_factory:
                        raise OpenAIProviderError("MCP factory not available")
                    
                    mcp_servers = await self._agent_factory._mcp_factory.create_mcp_servers(unique_mcp_configs)
                    
                    # Use a SINGLE async context manager for all MCP servers
                    from contextlib import AsyncExitStack
                    async with AsyncExitStack() as stack:
                        # Enter all MCP servers in the same context stack
                        connected_servers = []
                        for server in mcp_servers:
                            connected_server = await stack.enter_async_context(server)
                            connected_servers.append(connected_server)
                        
                        # Assign MCP servers to each agent based on their configs
                        await self._assign_mcp_servers_to_agents(agent, agent_run, connected_servers, unique_mcp_configs)
                        
                        logger.debug(f"Successfully connected and assigned {len(connected_servers)} MCP servers in unified context")
                        
                        # Run agent with session passed to Runner.run
                        run_result = await Runner.run(
                            agent,
                            input=message,
                            session=openai_session,
                            context=agent_run
                        )
                        result = run_result.final_output if hasattr(run_result, 'final_output') else str(run_result)

                        # AsyncExitStack automatically handles cleanup of all contexts
                else:
                    # No MCP servers, run normally
                    run_result = await Runner.run(
                        agent,
                        input=message,
                        session=openai_session,
                        context=agent_run
                    )
                    result = run_result.final_output if hasattr(run_result, 'final_output') else str(run_result)
                
                logger.info(f"Agent execution completed successfully for session {agent_run.metadata.session_id}")
                logger.debug(f"Agent result length: {len(result)} characters")
                
                return ExecutionResult(
                    status=ExecutionStatus.COMPLETED,
                    output=result,
                    metadata={"provider": self.provider_name, "session_id": agent_run.metadata.session_id}
                )
            finally:
                # Clean up session manager
                logger.debug(f"Cleaning up session manager for session {agent_run.metadata.session_id}")
                await session_manager.cleanup()
                
        except Exception as e:
            import traceback
            error_details = {
                'error_message': str(e),
                'error_type': type(e).__name__,
                'traceback': traceback.format_exc(),
                'agent_id': agent_run.agent.id if (agent_run and hasattr(agent_run, 'agent') and agent_run.agent) else 'unknown',
                'file': __file__,
                'function': 'run_agent'
            }
            
            logger.error(
                f"Agent execution failed for agent {error_details['agent_id']}: {error_details['error_message']}\n"
                f"Error Type: {error_details['error_type']}\n"
                f"File: {error_details['file']}\n"
                f"Function: {error_details['function']}\n"
                f"Traceback:\n{error_details['traceback']}"
            )
            
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                error=str(e),
                metadata={
                    "provider": self.provider_name,
                    "error_type": error_details['error_type'],
                    "file": error_details['file'],
                    "function": error_details['function']
                }
            )

    async def run_agent_stream(self, agent_run: AgentRun) -> AsyncGenerator[StreamEvent, None]:
        """Execute agent with real OpenAI streaming and session persistence."""
        # Strict validation - fail fast if agent_run is invalid
        if agent_run is None:
            raise OpenAIProviderError("agent_run parameter cannot be None")
        if agent_run.agent is None:
            raise OpenAIProviderError("agent_run.agent cannot be None")
        if agent_run.team is None:
            raise OpenAIProviderError("agent_run.team cannot be None")
        if not agent_run.message:
            raise OpenAIProviderError("agent_run.message cannot be empty")
            
        logger.debug(f"Starting streaming agent execution: agent_id={agent_run.agent.id}, message='{agent_run.message[:100]}...'")
        self._ensure_initialized()

        # Create session manager for this agent execution
        logger.debug(f"Creating session manager for streaming agent {agent_run.agent.id}")
        session_manager = await self._create_session_for_agent(agent_run)

        try:
            yield EventFactory.create_agent_started(
                message=agent_run.message,
                session_id=agent_run.metadata.session_id,
                provider=self.provider_name,
                agent_id=agent_run.agent.id
            )

            # Get SessionABC implementation for OpenAI agent
            logger.debug(f"Getting session implementation for streaming session {agent_run.metadata.session_id}")
            openai_session = await session_manager.get_session()
            logger.info(f"Retrieved session implementation of type {type(openai_session).__name__} for streaming agent {agent_run.agent.id}")
            logger.debug(f"Streaming AgentRun context: team_id={agent_run.team.id}, agent_id={agent_run.agent.id}")
            
            # Import Runner here to avoid import issues during initialization
            from agents import Agent, Runner
            from openai.types.responses import ResponseTextDeltaEvent
            
            # Create agent with tools, delegations, and handoffs
            logger.debug(f"Creating OpenAI Agent with relations for streaming: name={agent_run.agent.name}")
            agent, mcp_configs = await self._create_agent_with_tools(agent_run)
            
            # Create all MCP servers in unified async context for streaming
            if mcp_configs:
                # Deduplicate MCP configs to avoid duplicate servers
                unique_mcp_configs = self._deduplicate_mcp_configs(mcp_configs)
                logger.debug(f"Creating {len(unique_mcp_configs)} unique MCP servers (from {len(mcp_configs)} total configs) in unified async context for streaming")
                
                # Create all MCP servers in this context using the factory
                if not self._agent_factory or not self._agent_factory._mcp_factory:
                    raise OpenAIProviderError("MCP factory not available")
                
                mcp_servers = await self._agent_factory._mcp_factory.create_mcp_servers(unique_mcp_configs)
                
                # Use a SINGLE async context manager for all MCP servers in streaming
                from contextlib import AsyncExitStack
                async with AsyncExitStack() as stack:
                    # Enter all MCP servers in the same context stack
                    connected_servers = []
                    for server in mcp_servers:
                        connected_server = await stack.enter_async_context(server)
                        connected_servers.append(connected_server)
                    
                    # Assign MCP servers to each agent based on their configs
                    await self._assign_mcp_servers_to_agents(agent, agent_run, connected_servers, unique_mcp_configs)
                    
                    logger.debug(f"Successfully connected and assigned {len(connected_servers)} MCP servers in unified context for streaming")
                    
                    # Run with streaming and session
                    logger.debug(f"Starting OpenAI streaming execution with session {agent_run.metadata.session_id}")
                    result = Runner.run_streamed(
                        agent, 
                        input=agent_run.message,
                        session=openai_session,
                        context=agent_run
                    )
                    
                    # Stream the events using proper OpenAI agents SDK event handling
                    logger.debug(f"Processing OpenAI stream events for session {agent_run.metadata.session_id}")
                    async for event in result.stream_events():
                        async for stream_event in self._handle_openai_event(event):
                            yield stream_event
                    
                    # AsyncExitStack automatically handles cleanup of all contexts
            else:
                # No MCP servers, run normally
                logger.debug(f"Starting OpenAI streaming execution with session {agent_run.metadata.session_id}")
                result = Runner.run_streamed(
                    agent, 
                    input=agent_run.message,
                    session=openai_session,
                    context=agent_run
                )
                
                # Stream the events using proper OpenAI agents SDK event handling
                logger.debug(f"Processing OpenAI stream events for session {agent_run.metadata.session_id}")
                async for event in result.stream_events():
                    async for stream_event in self._handle_openai_event(event):
                        yield stream_event

            logger.info(f"Streaming agent execution completed successfully for session {agent_run.metadata.session_id}")
            yield EventFactory.create_agent_completed(
                status="completed",
                session_id=agent_run.metadata.session_id,
                provider=self.provider_name,
                agent_id=agent_run.agent.id
            )

        except Exception as e:
            import traceback
            error_details = {
                'error_message': str(e),
                'error_type': type(e).__name__,
                'traceback': traceback.format_exc(),
                'agent_id': agent_run.agent.id if (agent_run and hasattr(agent_run, 'agent') and agent_run.agent) else 'unknown',
                'file': __file__,
                'function': 'run_agent_stream'
            }
            
            logger.error(
                f"Streaming agent execution failed for agent {error_details['agent_id']}: {error_details['error_message']}\n"
                f"Error Type: {error_details['error_type']}\n"
                f"File: {error_details['file']}\n"
                f"Function: {error_details['function']}\n"
                f"Traceback:\n{error_details['traceback']}"
            )
            
            yield EventFactory.create_agent_error(
                error=str(e),
                session_id=agent_run.metadata.session_id if agent_run and agent_run.metadata else None,
                provider=self.provider_name,
                agent_id=error_details['agent_id']
            )
        finally:
            # Clean up session manager
            if session_manager:
                logger.debug(f"Cleaning up streaming session manager for session {agent_run.metadata.session_id}")
                await session_manager.cleanup()

    async def _handle_openai_event(self, event) -> AsyncGenerator[StreamEvent, None]:
        """Handle OpenAI agents SDK events and convert to common StreamEvent format."""
        try:
            # Handle specific event types
            if event.type == "raw_response_event":
                async for stream_event in self._handle_raw_response_event(event):
                    yield stream_event
            
            # Handle agent updated events
            elif event.type == "agent_updated_stream_event":
                async for stream_event in self._handle_agent_updated_event(event):
                    yield stream_event
            
            # Handle run item events (tool calls, outputs, etc.)
            elif event.type == "run_item_stream_event":
                async for stream_event in self._handle_run_item_event(event):
                    yield stream_event
            
            # Handle message output events
            elif event.type == "message_output_event":
                async for stream_event in self._handle_message_output_event(event):
                    yield stream_event
            
            # Handle unknown events
            else:
                async for stream_event in self._handle_unknown_event(event):
                    yield stream_event
                    
        except Exception as e:
            logger.error(f"Error in _handle_openai_event: {e}, Event: {repr(event)}, Event type: {type(event)}")
            yield EventFactory.create_event_error(
                error=str(e),
                event_type=getattr(event, 'type', 'unknown'),
                provider=self.provider_name
            )

    async def _handle_raw_response_event(self, event) -> AsyncGenerator[StreamEvent, None]:
        """Handle raw response events with text delta data."""
        if hasattr(event, 'data') and event.data is not None:
            # Import ResponseTextDeltaEvent here to avoid import issues
            from openai.types.responses import ResponseTextDeltaEvent
            
            if isinstance(event.data, ResponseTextDeltaEvent):
                # Yield text delta events - this is the real streaming text!
                yield EventFactory.create_text_delta(
                    delta=event.data.delta,
                    provider=self.provider_name,
                    content_index=getattr(event.data, 'content_index', 0),
                    item_id=getattr(event.data, 'item_id', None),
                    original_event=event
                )

    async def _handle_agent_updated_event(self, event) -> AsyncGenerator[StreamEvent, None]:
        """Handle agent updated events."""
        if hasattr(event, 'new_agent') and event.new_agent:
            yield EventFactory.create_agent_updated(
                agent_name=event.new_agent.name,
                provider=self.provider_name
            )

    async def _handle_run_item_event(self, event) -> AsyncGenerator[StreamEvent, None]:
        """Handle run item events (tool calls, outputs, etc.)."""
        if hasattr(event, 'item') and event.item:
            if event.item.type == "tool_call_item":
                yield EventFactory.create_tool_call(
                    tool_name=getattr(event.item.raw_item, 'name', 'unknown_tool'),
                    call_id=getattr(event.item.raw_item, 'call_id', 'unknown'),
                    arguments=getattr(event.item, 'arguments', {}),
                    provider=self.provider_name,
                    original_event=event
                )
            elif event.item.type == "tool_call_output_item":
                yield EventFactory.create_tool_result(
                    content=getattr(event.item, 'output', ''),
                    call_id=event.item.raw_item['call_id'],
                    provider=self.provider_name,
                    original_event=event
                )
            elif event.item.type == "message_output_item":
                content = getattr(event.item, 'content', '')
                if content:
                    yield EventFactory.create_message_output(
                        content=content,
                        item_id=getattr(event.item, 'id', None),
                        provider=self.provider_name,
                        original_event=event
                    )

    async def _handle_message_output_event(self, event) -> AsyncGenerator[StreamEvent, None]:
        """Handle message output events."""
        try:
            # Try to extract text content
            from agents import ItemHelpers
            content = ItemHelpers.text_message_output(event.item)
        except Exception:
            # Fall back to string representation
            content = str(event.item)
        
        yield EventFactory.create_message_output(
            content=content,
            item_id=getattr(event.item, 'id', None),
            provider=self.provider_name,
            original_event=event
        )

    async def _handle_unknown_event(self, event) -> AsyncGenerator[StreamEvent, None]:
        """Handle unknown or unsupported event types."""
        # Check if event has data attribute
        if not hasattr(event, 'data') or event.data is None:
            yield EventFactory.create_debug_info(
                message="Event received but no data available",
                context={"event_type": event.type},
                provider=self.provider_name
            )
        else:
            yield EventFactory.create_unknown_event(
                event_type=event.type,
                raw_data=str(event.data),
                provider=self.provider_name
            )



    def _deduplicate_mcp_configs(self, mcp_configs: List) -> List:
        """Deduplicate MCP configurations to avoid duplicate server instances."""
        seen = set()
        unique_configs = []
        
        for config in mcp_configs:
            # Create a unique identifier for each MCP config
            # Use URL for HTTP servers, command for stdio servers
            if hasattr(config, 'url') and config.url:
                config_key = f"url:{config.url}"
            elif hasattr(config, 'command') and config.command:
                config_key = f"command:{' '.join(config.command) if isinstance(config.command, list) else config.command}"
            else:
                # Fallback to using the config's name or id
                config_key = f"name:{getattr(config, 'name', getattr(config, 'id', str(config)))}"
            
            if config_key not in seen:
                seen.add(config_key)
                unique_configs.append(config)
                logger.debug(f"Added unique MCP config: {config_key}")
            else:
                logger.debug(f"Skipped duplicate MCP config: {config_key}")
        
        return unique_configs

    async def _assign_mcp_servers_to_agents(self, main_agent, agent_run: AgentRun, connected_servers: List, unique_mcp_configs: List) -> None:
        """Assign appropriate MCP servers to each agent based on their configs."""
        # Create mapping from config to connected server
        config_to_server = {}
        for config, server in zip(unique_mcp_configs, connected_servers):
            config_key = self._get_config_key(config)
            config_to_server[config_key] = server
        
        # Assign servers to main agent
        main_agent_configs = self._agent_factory._get_mcp_configs(agent_run.agent, agent_run.team)
        main_agent_servers = []
        for config in main_agent_configs:
            config_key = self._get_config_key(config)
            if config_key in config_to_server:
                main_agent_servers.append(config_to_server[config_key])
        main_agent.mcp_servers = main_agent_servers
        logger.debug(f"Assigned {len(main_agent_servers)} MCP servers to main agent {agent_run.agent.id}")
        
        # Create a registry to track delegation agents that need MCP servers assigned
        delegation_agent_registry = {}
        
        # Assign servers to delegation agents by getting them from the factory cache
        for delegation in agent_run.agent.delegations:
            target_agent = delegation.target_agent
            if not target_agent:
                target_agent = self._agent_factory._find_agent_in_team(delegation.target_agent_id, agent_run.team)
            if target_agent:
                delegation_configs = self._agent_factory._get_mcp_configs(target_agent, agent_run.team)
                delegation_servers = []
                for config in delegation_configs:
                    config_key = self._get_config_key(config)
                    if config_key in config_to_server:
                        delegation_servers.append(config_to_server[config_key])
                
                # Get the delegation agent from factory cache
                cache_key = f"delegation_{target_agent.id}_{id(agent_run.team)}"
                if cache_key in self._agent_factory._agent_cache:
                    delegation_agent = self._agent_factory._agent_cache[cache_key]
                    delegation_agent.mcp_servers = delegation_servers
                    delegation_agent_registry[target_agent.id] = delegation_agent
                    logger.debug(f"Assigned {len(delegation_servers)} MCP servers to delegation agent {target_agent.id}")
                else:
                    logger.warning(f"Delegation agent {target_agent.id} not found in factory cache for MCP assignment")
        
        # Assign servers to handoff agents
        for handoff in agent_run.agent.handoffs:
            target_agent = handoff.target_agent
            if not target_agent:
                target_agent = self._agent_factory._find_agent_in_team(handoff.target_agent_id, agent_run.team)
            if target_agent:
                handoff_configs = self._agent_factory._get_mcp_configs(target_agent, agent_run.team)
                handoff_servers = []
                for config in handoff_configs:
                    config_key = self._get_config_key(config)
                    if config_key in config_to_server:
                        handoff_servers.append(config_to_server[config_key])
                
                # Find the handoff agent in main_agent.handoffs
                for handoff_agent in main_agent.handoffs:
                    if hasattr(handoff_agent, 'name') and handoff_agent.name == target_agent.name:
                        handoff_agent.mcp_servers = handoff_servers
                        logger.debug(f"Assigned {len(handoff_servers)} MCP servers to handoff agent {target_agent.id}")
                        break
    
    def _get_config_key(self, config) -> str:
        """Get unique key for MCP config matching deduplication logic."""
        if hasattr(config, 'url') and config.url:
            return f"url:{config.url}"
        elif hasattr(config, 'command') and config.command:
            return f"command:{' '.join(config.command) if isinstance(config.command, list) else config.command}"
        else:
            return f"name:{getattr(config, 'name', getattr(config, 'id', str(config)))}"
    
    def _ensure_initialized(self) -> None:
        """Ensure provider is initialized."""
        if not self._is_initialized:
            raise OpenAIProviderError("Provider not initialized. Call initialize() first.")


