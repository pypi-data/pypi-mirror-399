"""
Execution domain models.
Contains models for team and agent execution contexts.
"""

from typing import TYPE_CHECKING, Optional
from pydantic import BaseModel, Field, field_validator, model_validator

from .agent import Agent
from .knowledge import Knowledge
from .provider import ProviderConfiguration
from .team import Team
from .tool import Tool
from .trait import Trait

if TYPE_CHECKING:
    from ...tools.streaming.interfaces import IToolStreamContext


class ExecutionContext(BaseModel):
    """Base execution context with common configuration."""

    stream: bool = Field(False, description="Enable streaming mode")
    debug: bool = Field(False, description="Enable debug mode")
    tool_streaming: bool = Field(True, description="Enable tool streaming (requires stream=True)")
    tool_streaming_merger: str = Field("time_ordered", description="Stream merger type: basic, time_ordered, priority")
    provider_config: ProviderConfiguration | None = Field(
        None, description="Provider-specific configuration"
    )
    timeout_override: int | None = Field(
        None, ge=1, description="Override timeout in seconds"
    )

    def get_provider_config(self) -> ProviderConfiguration:
        """Get provider configuration, creating default if none exists."""
        if self.provider_config is None:
            self.provider_config = ProviderConfiguration(
                id="default_provider_config", name="Default Provider Configuration"
            )
        return self.provider_config

    def has_provider_config(self) -> bool:
        """Check if provider configuration is set."""
        return self.provider_config is not None




class AgentRunMetadata(BaseModel):
    """Metadata for agent execution tracking and multi-tenant scenarios."""

    account_id: Optional[int] = Field(
        default=1, description="Account identifier for multi-tenant scenarios"
    )

    # Integer IDs for database references (python-api style)
    team_id: Optional[int] = Field(
        default=None, description="Integer team ID (references teams table)"
    )

    agent_id: Optional[int] = Field(
        default=None, description="Integer agent ID (references agents table)"
    )

    # String identifiers from YAML configuration
    team_identifier: Optional[str] = Field(
        default=None, description="Team identifier from YAML root 'id' field"
    )

    agent_identifier: Optional[str] = Field(
        default=None, description="Agent identifier from YAML agents[].id field"
    )

    session_id: Optional[str] = Field(
        default=None, description="Session identifier for conversation tracking"
    )

    task_id: Optional[int] = Field(
        default=None, description="Task identifier for task execution tracking"
    )


class AgentRun(BaseModel):
    """Domain object for single agent execution."""

    agent: Agent = Field(..., description="Agent configuration")
    team: Team = Field(..., description="Team context for tools/knowledge access")
    message: str = Field(
        ..., min_length=1, description="Message to execute with the agent"
    )
    context: ExecutionContext = Field(
        default_factory=ExecutionContext, description="Execution context"
    )
    metadata: AgentRunMetadata = Field(
        default_factory=AgentRunMetadata, description="Execution metadata"
    )
    
    # Tool streaming context (set at runtime by runner)
    _tool_stream_context: "IToolStreamContext | None" = None

    @field_validator("message")
    @classmethod
    def validate_message(cls, v):
        """Validate message is not empty."""
        if not v or not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()

    def get_effective_max_turns(self) -> Optional[int]:
        """Get effective max turns from agent or team config."""
        return self.agent.max_turns or self.team.config.max_turns

    def get_effective_timeout(self) -> Optional[int]:
        """Get effective timeout."""
        return self.context.timeout_override or self.team.config.timeout

    def get_available_tools(self) -> list[Tool]:
        """Get tools available to this agent."""
        return self.agent.tools  # Agent now contains actual Tool objects

    def get_available_knowledge(self) -> list[Knowledge]:
        """Get knowledge bases available to this agent."""
        return self.agent.knowledge  # Agent now contains actual Knowledge objects

    def get_traits(self) -> list[Trait]:
        """Get trait objects for this agent."""
        return self.agent.traits  # Agent now contains actual Trait objects

    def get_mcp_servers(self) -> list[Tool]:
        """Get MCP server tools available to this agent."""
        return [tool for tool in self.agent.tools if tool.is_mcp_tool()]

    def get_builtin_tools(self) -> list[Tool]:
        """Get built-in tools available to this agent."""
        return [tool for tool in self.agent.tools if tool.is_builtin_tool()]

    def should_stream(self) -> bool:
        """Check if streaming is enabled."""
        return self.context.stream

    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled."""
        return self.context.debug or self.agent.debug or self.team.config.debug
    
    def set_tool_stream_context(self, context: "IToolStreamContext") -> None:
        """Set tool streaming context for this execution."""
        self._tool_stream_context = context
    
    def get_tool_stream_context(self) -> "IToolStreamContext | None":
        """Get tool streaming context if available."""
        return self._tool_stream_context
    
    def has_tool_streaming(self) -> bool:
        """Check if tool streaming is available."""
        return self._tool_stream_context is not None
    
    def should_use_tool_streaming(self) -> bool:
        """Check if tool streaming should be enabled based on context."""
        return (
            self.context.stream and 
            self.context.tool_streaming and 
            self._tool_stream_context is not None
        )

    @model_validator(mode="after")
    def process_agent_instructions(self) -> "AgentRun":
        """Process agent instructions with team context after initialization."""
        from ...prompts import AgentPromptBuilder
        
        # Auto-instantiate prompt builder and process instructions
        prompt_builder = AgentPromptBuilder()
        self.agent.processed_instructions = prompt_builder.build_agent_prompt(
            agent=self.agent, team=self.team
        )
        
        return self
