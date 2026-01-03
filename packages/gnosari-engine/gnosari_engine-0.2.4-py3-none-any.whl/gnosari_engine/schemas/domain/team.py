"""
Team domain models.
Contains team configuration and component orchestration.
"""

from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from ..session import SessionContext
from .agent import Agent
from .base import BaseComponent
from .knowledge import Knowledge
from .tool import Tool
from .trait import Trait


class TeamConfiguration(BaseModel):
    """Team-level configuration for Team object."""

    max_turns: int | None = Field(None, ge=1, description="Maximum conversation turns")
    timeout: int | None = Field(
        None, ge=1, description="Team execution timeout in seconds"
    )
    log_level: str = Field("INFO", description="Logging level")
    enable_memory: bool = Field(True, description="Enable team memory/learning")
    debug: bool = Field(False, description="Enable debug mode")

    class Config:
        arbitrary_types_allowed = True


class Team(BaseComponent):
    """Complete team configuration domain object with performance optimizations (renamed from TeamConfiguration)."""

    version: str = Field("1.0.0", description="Configuration version")
    tags: list[str] = Field(default_factory=list, description="Team tags")
    account_id: int | None = Field(None, description="Account ID for cloud integration")

    # Team-level configuration
    config: TeamConfiguration = Field(
        default_factory=TeamConfiguration,  # type: ignore[arg-type]
        description="Team-level configuration",
    )

    # Session Context (moved from TeamRun)
    session_context: SessionContext | None = Field(
        None, description="Session context for persistence"
    )

    # Core components (configuration data)
    agents: list[Agent] = Field(..., description="Team agents")
    tools: list[Tool] = Field(default_factory=list, description="Available tools")
    knowledge: list[Knowledge] = Field(
        default_factory=list, description="Available knowledge bases"
    )
    traits: list[Trait] = Field(default_factory=list, description="Available traits")

    # Hierarchical overrides
    overrides: dict[str, dict[str, dict[str, Any]]] = Field(
        default_factory=dict, description="Component overrides"
    )

    # Component filtering
    components: dict[str, dict[str, list[str]]] = Field(
        default_factory=dict, description="Component inclusion/exclusion"
    )

    # Performance indexes (added by ComponentIndexer service)
    agent_index: dict[str, Agent] = Field(default_factory=dict, exclude=True)
    agent_name_index: dict[str, Agent] = Field(default_factory=dict, exclude=True)
    tool_index: dict[str, Tool] = Field(default_factory=dict, exclude=True)
    knowledge_index: dict[str, Knowledge] = Field(default_factory=dict, exclude=True)
    trait_index: dict[str, Trait] = Field(default_factory=dict, exclude=True)

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Validate team ID."""
        if not v or not isinstance(v, str) or not v.strip():
            raise ValueError("Team ID is required and must be a non-empty string")
        return v.strip()

    @field_validator("agents")
    @classmethod
    def validate_agents(cls, v: list[Agent]) -> list[Agent]:
        """Validate agent configuration."""
        if not v:
            raise ValueError("Team must have at least one agent")

        # Check for exactly one orchestrator
        orchestrators = [agent for agent in v if agent.is_orchestrator]
        if len(orchestrators) != 1:
            raise ValueError("Team must have exactly one orchestrator agent")

        # Check for unique agent names and IDs
        names = [agent.name for agent in v if agent.name]
        ids = [agent.id for agent in v]

        if len(set(names)) != len(names):
            raise ValueError("Agent names must be unique within team")

        if len(set(ids)) != len(ids):
            raise ValueError("Agent IDs must be unique within team")

        return v

    @field_validator("tools")
    @classmethod
    def validate_tools_uniqueness(cls, v: list[Tool]) -> list[Tool]:
        """Validate tool ID uniqueness."""
        if not v:
            return v

        ids = [item.id for item in v]
        if len(set(ids)) != len(ids):
            raise ValueError("Tool IDs must be unique within team")

        return v

    @field_validator("knowledge")
    @classmethod
    def validate_knowledge_uniqueness(cls, v: list[Knowledge]) -> list[Knowledge]:
        """Validate knowledge ID uniqueness."""
        if not v:
            return v

        ids = [item.id for item in v]
        if len(set(ids)) != len(ids):
            raise ValueError("Knowledge IDs must be unique within team")

        return v

    @field_validator("traits")
    @classmethod
    def validate_traits_uniqueness(cls, v: list[Trait]) -> list[Trait]:
        """Validate trait ID uniqueness."""
        if not v:
            return v

        ids = [item.id for item in v]
        if len(set(ids)) != len(ids):
            raise ValueError("Trait IDs must be unique within team")

        return v

    @model_validator(mode="after")
    def validate_team_model(self) -> "Team":
        """Set name from id if not provided."""
        if not self.name and self.id:
            self.name = self.id.replace("_", " ").replace("-", " ").title()
        return self

    @model_validator(mode="after")
    def ensure_agent_tools_in_team(self) -> "Team":
        """Automatically add all agent tools to team tools if not already present."""
        # Get all unique tool IDs that are already in the team
        existing_tool_ids = {tool.id for tool in self.tools}
        
        # Collect all unique tools from all agents
        agent_tools_to_add = []
        for agent in self.agents:
            for tool in agent.tools:
                if tool.id not in existing_tool_ids:
                    # Check if we haven't already collected this tool
                    if not any(t.id == tool.id for t in agent_tools_to_add):
                        agent_tools_to_add.append(tool)
                        existing_tool_ids.add(tool.id)
        
        # Add all collected agent tools to the team
        self.tools.extend(agent_tools_to_add)
        
        return self

    def get_orchestrator(self) -> Agent:
        """Get the orchestrator agent."""
        # Use index if available, fallback to linear search
        if self.agent_index:
            for agent in self.agent_index.values():
                if agent.is_orchestrator:
                    return agent
        else:
            for agent in self.agents:
                if agent.is_orchestrator:
                    return agent
        raise ValueError("No orchestrator agent found")

    def get_worker_agents(self) -> list[Agent]:
        """Get all worker (non-orchestrator) agents."""
        # Use index if available
        if self.agent_index:
            return [
                agent
                for agent in self.agent_index.values()
                if not agent.is_orchestrator
            ]
        else:
            return [agent for agent in self.agents if not agent.is_orchestrator]

    def get_agent_by_name(self, name: str) -> Agent | None:
        """Get agent by name - O(1) with index, O(n) without."""
        if self.agent_name_index:
            return self.agent_name_index.get(name)
        else:
            # Fallback to linear search
            for agent in self.agents:
                if agent.name == name:
                    return agent
            return None

    def get_agent_by_id(self, agent_id: str) -> Agent | None:
        """Get agent by ID - O(1) with index, O(n) without."""
        if self.agent_index:
            return self.agent_index.get(agent_id)
        else:
            # Fallback to linear search
            for agent in self.agents:
                if agent.id == agent_id:
                    return agent
            return None

    def get_tool_by_id(self, tool_id: str) -> Tool | None:
        """Get tool by ID - O(1) with index, O(n) without."""
        if self.tool_index:
            return self.tool_index.get(tool_id)
        else:
            # Fallback to linear search
            for tool in self.tools:
                if tool.id == tool_id:
                    return tool
            return None

    def get_knowledge_by_id(self, knowledge_id: str) -> Knowledge | None:
        """Get knowledge base by ID - O(1) with index, O(n) without."""
        if self.knowledge_index:
            return self.knowledge_index.get(knowledge_id)
        else:
            # Fallback to linear search
            for kb in self.knowledge:
                if kb.id == knowledge_id:
                    return kb
            return None

    def get_trait_by_id(self, trait_id: str) -> Trait | None:
        """Get trait by ID - O(1) with index, O(n) without."""
        if self.trait_index:
            return self.trait_index.get(trait_id)
        else:
            # Fallback to linear search
            for trait in self.traits:
                if trait.id == trait_id:
                    return trait
            return None
