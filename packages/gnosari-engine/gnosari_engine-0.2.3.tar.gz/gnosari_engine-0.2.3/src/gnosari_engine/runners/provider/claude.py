"""
Claude provider strategy implementation.
Clean implementation following SOLID principles and ProviderStrategy protocol.
"""

import asyncio
import logging
import os
from collections.abc import AsyncGenerator
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from ...schemas.domain.execution import AgentRun
from ..interfaces import ExecutionResult, ExecutionStatus
from ..events import StreamEvent, EventFactory, EventType
from ...sessions.gnosari_session import GnosariSession
from ...tools.components import ToolManager
from .claude_agent_factory import ClaudeAgentFactory

logger = logging.getLogger(__name__)


class ClaudeProviderError(Exception):
    """Claude provider specific errors."""
    pass


class ClaudeProvider:
    """
    Claude provider strategy implementation.
    
    Follows SOLID Principles:
    - Single Responsibility: Handles only Claude execution logic
    - Open/Closed: Extensible for new Claude features, closed for modification
    - Liskov Substitution: Implements ProviderStrategy protocol correctly
    - Interface Segregation: Only implements required provider methods
    - Dependency Inversion: Can be injected into GnosariRunner
    """

    def __init__(self):
        self._api_key: str | None = None
        self._client = None
        self._session_manager: GnosariSession | None = None
        self._tool_manager: ToolManager | None = None
        self._agent_factory: ClaudeAgentFactory | None = None
        self._is_initialized = False

    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return "claude"

    async def initialize(self, **config) -> None:
        """Initialize Claude provider with configuration."""
        logger.debug("Initializing Claude provider")
        
        if self._is_initialized:
            logger.debug("Claude provider already initialized")
            return

        # Get API key from config or environment
        self._api_key = (
            config.get("api_key") or
            config.get("default_api_key") or
            os.getenv("ANTHROPIC_API_KEY") or
            os.getenv("CLAUDE_CODE_OAUTH_TOKEN")
        )

        if not self._api_key:
            logger.error("Claude API key not found in config or environment")
            raise ClaudeProviderError(
                "Claude API key is required. Set ANTHROPIC_API_KEY or CLAUDE_CODE_OAUTH_TOKEN "
                "environment variable or pass 'api_key' in configuration."
            )

        logger.debug(f"Claude API key found (length: {len(self._api_key) if self._api_key else 0})")

        try:
            # Import Claude SDK
            from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
            
            # Set the API key
            os.environ["ANTHROPIC_API_KEY"] = self._api_key
            
            # Initialize tool manager for Claude provider
            self._tool_manager = ToolManager(provider_name=self.provider_name)
            await self._tool_manager.initialize(**config)
            
            # Initialize agent factory with MCP support
            self._agent_factory = ClaudeAgentFactory(self._tool_manager)
            
            logger.info("Claude provider initialized with Claude SDK, tool manager, and agent factory")
            self._is_initialized = True
            logger.debug("Claude provider initialization completed successfully")
        except ImportError as e:
            logger.error(f"Claude SDK package import failed: {e}")
            raise ClaudeProviderError(
                "Claude SDK package not found. Install with: pip install claude-agent-sdk"
            ) from e
        except Exception as e:
            logger.error(f"Claude provider initialization failed: {e}")
            raise ClaudeProviderError(f"Failed to initialize Claude provider: {e}") from e

    async def cleanup(self) -> None:
        """Cleanup Claude provider resources."""
        try:
            logger.debug("Cleaning up Claude provider")
            
            if self._session_manager is not None:
                await self._session_manager.cleanup()
                self._session_manager = None
            if self._tool_manager is not None:
                await self._tool_manager.cleanup()
                self._tool_manager = None
            if self._agent_factory is not None:
                self._agent_factory.clear_cache()
                self._agent_factory = None
            self._client = None
            self._is_initialized = False
            
            logger.debug("Claude provider cleanup completed")
        except Exception as e:
            logger.error(f"Error during Claude provider cleanup: {e}")

    async def _create_session_for_agent(self, agent_run: AgentRun) -> GnosariSession:
        """Create session manager for agent execution."""
        logger.debug(f"Creating session for agent execution: agent_id={agent_run.agent.id}, team_id={agent_run.team.id}")
        
        # Strict validation - metadata should never be None due to default_factory
        if agent_run.metadata is None:
            raise ClaudeProviderError(
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
        logger.debug(f"Creating GnosariSession with provider 'claude_database' for session {session_id}")
        session_manager = GnosariSession(
            session_id=session_id,
            provider_name="claude_database",
            agent_run=agent_run  # Pass AgentRun directly
        )
        
        logger.debug(f"Session manager created successfully for session {session_id}")
        return session_manager

    async def _create_basic_claude_options(self, agent_run: AgentRun):
        """Create basic Claude options for agent execution."""
        try:
            from claude_agent_sdk import ClaudeAgentOptions
        except ImportError as e:
            raise ClaudeProviderError("Claude SDK not available") from e
        
        logger.debug(f"Creating basic Claude options for agent: {agent_run.agent.name}")
        
        # Build system prompt for the agent
        system_prompt = self._build_system_prompt(agent_run.agent, agent_run.team)
        
        # Create basic Claude options
        claude_options = ClaudeAgentOptions(
            system_prompt=system_prompt,
            max_turns=agent_run.agent.max_turns if hasattr(agent_run.agent, 'max_turns') and agent_run.agent.max_turns else 20,
            permission_mode="bypassPermissions"  # Default to accepting edits for agent execution
        )
        
        logger.debug(f"Created basic Claude options for agent {agent_run.agent.id}")
        return claude_options

    def _build_system_prompt(self, agent, team) -> str:
        """Build system prompt for the agent."""
        prompt_parts = []
        
        # Add agent instructions
        if agent.instructions:
            prompt_parts.append(agent.instructions)
        
        # Add team context if needed
        if team.description:
            prompt_parts.append(f"\nTeam Context: {team.description}")
        
        # Add role-specific instructions
        if hasattr(agent, 'orchestrator') and agent.orchestrator:
            prompt_parts.append("\nYou are the orchestrator of this team. Coordinate with other agents as needed.")
        else:
            prompt_parts.append("\nYou are a specialized team member. Focus on your expertise area.")
        
        return "\n".join(prompt_parts)

    async def _create_claude_client_with_tools(self, agent_run: AgentRun):
        """Create Claude client with configured tools, delegations, and handoffs."""
        if not self._agent_factory:
            raise ClaudeProviderError("Agent factory not initialized")
            
        # Create Claude options and get MCP configs for unified async context management
        claude_options, main_agent_mcp_configs = await self._agent_factory.create_claude_options_with_relations(
            agent_run.agent, agent_run.team
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
        
        logger.debug(f"Created Claude options with {len(all_mcp_configs)} total MCP configs for unified async context management")
        return claude_options, all_mcp_configs

    async def run_agent(self, agent_run: AgentRun) -> ExecutionResult:
        """Execute agent synchronously with session persistence."""
        # Strict validation - fail fast if agent_run is invalid
        if agent_run is None:
            raise ClaudeProviderError("agent_run parameter cannot be None")
        if agent_run.agent is None:
            raise ClaudeProviderError("agent_run.agent cannot be None")
        if agent_run.team is None:
            raise ClaudeProviderError("agent_run.team cannot be None")
        if not agent_run.message:
            raise ClaudeProviderError("agent_run.message cannot be empty")
            
        logger.debug(f"Starting synchronous agent execution: agent_id={agent_run.agent.id}, message='{agent_run.message[:100]}...'")
        self._ensure_initialized()
        
        try:
            # Import Claude SDK for execution
            from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock, ResultMessage
            
            # Use agent's actual message
            message = agent_run.message
            logger.debug(f"Executing agent with message: '{message[:100]}...' and session {agent_run.metadata.session_id}")

            # Create basic Claude options without unsupported parameters
            claude_options = ClaudeAgentOptions(
                system_prompt=self._build_system_prompt(agent_run.agent, agent_run.team),
                max_turns=agent_run.agent.max_turns if hasattr(agent_run.agent, 'max_turns') and agent_run.agent.max_turns else 20
            )

            # Execute with ClaudeSDKClient
            client = ClaudeSDKClient(options=claude_options)
            result_parts = []
            
            async with client:
                await client.query(message)
                
                # Collect all response content
                async for response_message in client.receive_response():
                    if isinstance(response_message, AssistantMessage):
                        for block in response_message.content:
                            if isinstance(block, TextBlock):
                                result_parts.append(block.text)
                    elif isinstance(response_message, ResultMessage):
                        # Final result message
                        if response_message.result:
                            result_parts.append(response_message.result)
            
            result = "\n".join(result_parts)
            
            logger.info(f"Agent execution completed successfully for session {agent_run.metadata.session_id}")
            logger.debug(f"Agent result length: {len(result)} characters")
            
            return ExecutionResult(
                status=ExecutionStatus.COMPLETED,
                output=result,
                metadata={"provider": self.provider_name, "session_id": agent_run.metadata.session_id}
            )
                
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
        """Execute agent with real Claude streaming and session persistence."""
        # Strict validation - fail fast if agent_run is invalid
        if agent_run is None:
            raise ClaudeProviderError("agent_run parameter cannot be None")
        if agent_run.agent is None:
            raise ClaudeProviderError("agent_run.agent cannot be None")
        if agent_run.team is None:
            raise ClaudeProviderError("agent_run.team cannot be None")
        if not agent_run.message:
            raise ClaudeProviderError("agent_run.message cannot be empty")
            
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

            # Import Claude SDK here to avoid import issues during initialization
            from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock, ToolUseBlock, ToolResultBlock, ResultMessage
            
            # Create basic Claude options for streaming
            logger.debug(f"Creating Claude client for streaming: name={agent_run.agent.name}")
            claude_options = ClaudeAgentOptions(
                system_prompt=self._build_system_prompt(agent_run.agent, agent_run.team),
                permission_mode='bypassPermissions',
                max_turns=agent_run.agent.max_turns if hasattr(agent_run.agent, 'max_turns') and agent_run.agent.max_turns else 20
            )
            
            # Create Claude SDK client
            client = ClaudeSDKClient(options=claude_options)
            
            # Run with streaming
            logger.debug(f"Starting Claude streaming execution with session {agent_run.metadata.session_id}")
            
            async with client:
                await client.query(agent_run.message)
                
                # Stream the events using Claude SDK message handling
                logger.debug(f"Processing Claude stream events for session {agent_run.metadata.session_id}")
                async for message in client.receive_messages():
                    async for stream_event in self._handle_claude_message(message):
                        yield stream_event

                    # Check if we've received the final result
                    if isinstance(message, ResultMessage):
                        break

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

    async def _handle_claude_message(self, message) -> AsyncGenerator[StreamEvent, None]:
        """Handle Claude SDK messages and convert to common StreamEvent format."""
        try:
            # Import Claude SDK message types
            from claude_agent_sdk import AssistantMessage, UserMessage, SystemMessage, ResultMessage

            # Route to specific handler based on message type
            if isinstance(message, AssistantMessage):
                async for stream_event in self._handle_assistant_message(message):
                    yield stream_event

            elif isinstance(message, UserMessage):
                async for stream_event in self._handle_user_message(message):
                    yield stream_event

            elif isinstance(message, SystemMessage):
                async for stream_event in self._handle_system_message(message):
                    yield stream_event

            elif isinstance(message, ResultMessage):
                async for stream_event in self._handle_result_message(message):
                    yield stream_event

            # Handle unknown message types
            else:
                async for stream_event in self._handle_unknown_message(message):
                    yield stream_event

        except Exception as e:
            logger.error(f"Error in _handle_claude_message: {e}, Message: {repr(message)}, Message type: {type(message)}")
            yield EventFactory.create_event_error(
                error=str(e),
                event_type=type(message).__name__,
                provider=self.provider_name
            )

    async def _handle_assistant_message(self, message) -> AsyncGenerator[StreamEvent, None]:
        """Handle Claude AssistantMessage with content blocks."""
        try:
            from claude_agent_sdk import TextBlock, ThinkingBlock, ToolUseBlock

            for block in message.content:
                if isinstance(block, TextBlock):
                    # Yield text content as message output
                    yield EventFactory.create_message_output(
                        content=block.text,
                        provider=self.provider_name
                    )
                elif isinstance(block, ThinkingBlock):
                    # Yield thinking content as debug info
                    thinking_text = block.thinking if hasattr(block, 'thinking') else str(block)
                    yield EventFactory.create_debug_info(
                        message=f"Thinking: {thinking_text[:100]}...",
                        context={"thinking_signature": getattr(block, 'signature', None)},
                        provider=self.provider_name
                    )
                elif isinstance(block, ToolUseBlock):
                    # Yield tool call event
                    yield EventFactory.create_tool_call(
                        tool_name=block.name,
                        call_id=block.id,
                        arguments=block.input,
                        provider=self.provider_name
                    )
        except Exception as e:
            logger.error(f"Error handling AssistantMessage: {e}")
            yield EventFactory.create_event_error(
                error=str(e),
                event_type="AssistantMessage",
                provider=self.provider_name
            )

    async def _handle_user_message(self, message) -> AsyncGenerator[StreamEvent, None]:
        """Handle Claude UserMessage (typically contains tool results)."""
        try:
            from claude_agent_sdk import ToolResultBlock

            for block in message.content:
                if isinstance(block, ToolResultBlock):
                    # Yield tool result event
                    content = str(block.content) if block.content else ""
                    # Check if this is an error result
                    is_error = getattr(block, 'is_error', False)

                    if is_error:
                        # Yield as tool error
                        yield EventFactory.create_event_error(
                            error=content,
                            event_type="ToolResult",
                            provider=self.provider_name
                        )
                    else:
                        # Yield as normal tool result
                        yield EventFactory.create_tool_result(
                            content=content,
                            call_id=block.tool_use_id,
                            provider=self.provider_name
                        )
        except Exception as e:
            logger.error(f"Error handling UserMessage: {e}")
            yield EventFactory.create_event_error(
                error=str(e),
                event_type="UserMessage",
                provider=self.provider_name
            )

    async def _handle_system_message(self, message) -> AsyncGenerator[StreamEvent, None]:
        """Handle Claude SystemMessage."""
        try:
            subtype = getattr(message, 'subtype', 'unknown')
            data = getattr(message, 'data', {})

            yield EventFactory.create_debug_info(
                message=f"System: {subtype}",
                context=data if isinstance(data, dict) else {"data": str(data)},
                provider=self.provider_name
            )
        except Exception as e:
            logger.error(f"Error handling SystemMessage: {e}")
            yield EventFactory.create_event_error(
                error=str(e),
                event_type="SystemMessage",
                provider=self.provider_name
            )

    async def _handle_result_message(self, message) -> AsyncGenerator[StreamEvent, None]:
        """Handle Claude ResultMessage (final execution result)."""
        try:
            yield EventFactory.create_debug_info(
                message=f"Execution completed in {message.duration_ms}ms",
                context={
                    "duration_ms": message.duration_ms,
                    "duration_api_ms": message.duration_api_ms,
                    "num_turns": message.num_turns,
                    "session_id": message.session_id,
                    "total_cost_usd": message.total_cost_usd,
                    "usage": message.usage if hasattr(message, 'usage') else {}
                },
                provider=self.provider_name
            )
        except Exception as e:
            logger.error(f"Error handling ResultMessage: {e}")
            yield EventFactory.create_event_error(
                error=str(e),
                event_type="ResultMessage",
                provider=self.provider_name
            )

    async def _handle_unknown_message(self, message) -> AsyncGenerator[StreamEvent, None]:
        """Handle unknown or unsupported message types."""
        yield EventFactory.create_unknown_event(
            event_type=type(message).__name__,
            raw_data=str(message),
            provider=self.provider_name
        )
    
    def _ensure_initialized(self) -> None:
        """Ensure provider is initialized."""
        if not self._is_initialized:
            raise ClaudeProviderError("Provider not initialized. Call initialize() first.")