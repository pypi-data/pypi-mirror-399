"""
Agent domain models.
Contains all agent-related configuration and behavior models.
"""

from __future__ import annotations

import os
from typing import Any, Literal

from .trait import Trait
from .knowledge import Knowledge
from .tool import Tool

from pydantic import BaseModel, Field, field_validator, model_validator

from .base import BaseComponent


def _get_default_model() -> str:
    """Get default model from environment variables or fallback to gpt-4o."""
    return os.getenv("OPENAI_MODEL") or os.getenv("DEFAULT_LLM_MODEL") or "gpt-4o"



class AgentHandoff(BaseModel):
    """Agent handoff configuration with resolved agent reference."""

    # For configuration loading (string reference)
    target_agent_id: str = Field(..., description="Target agent ID for handoff")
    
    # For runtime (resolved Agent object)
    target_agent: Agent | None = Field(None, description="Resolved target agent object")
    
    condition: str | None = Field(None, description="Condition for automatic handoff")
    message: str | None = Field(None, description="Message to include in handoff")

    @field_validator("target_agent_id")
    @classmethod
    def validate_target_agent_id(cls, v: str) -> str:
        """Validate target agent ID."""
        if not v or not isinstance(v, str) or not v.strip():
            raise ValueError("Target agent ID must be a non-empty string")
        return v.strip()

    def is_resolved(self) -> bool:
        """Check if the handoff has been resolved to an actual Agent object."""
        return self.target_agent is not None

    def get_target_name(self) -> str:
        """Get the target agent name, preferring resolved agent over ID."""
        if self.target_agent:
            return self.target_agent.name or self.target_agent.id
        return self.target_agent_id


class AgentDelegation(BaseModel):
    """Agent delegation configuration with resolved agent reference."""

    # For configuration loading (string reference)
    target_agent_id: str = Field(..., description="Target agent ID for delegation")
    
    # For runtime (resolved Agent object)
    target_agent: Agent | None = Field(None, description="Resolved target agent object")
    
    instructions: str | None = Field(None, description="Specific instructions for this delegation")
    mode: Literal["sync", "async"] = Field("sync", description="Delegation mode")
    timeout: int | None = Field(None, ge=1, description="Delegation timeout in seconds")
    retry_attempts: int = Field(1, ge=1, le=5, description="Number of retry attempts")

    @field_validator("target_agent_id")
    @classmethod
    def validate_target_agent_id(cls, v: str) -> str:
        """Validate target agent ID."""
        if not v or not isinstance(v, str) or not v.strip():
            raise ValueError("Target agent ID must be a non-empty string")
        return v.strip()

    def is_resolved(self) -> bool:
        """Check if the delegation has been resolved to an actual Agent object."""
        return self.target_agent is not None

    def get_target_name(self) -> str:
        """Get the target agent name, preferring resolved agent over ID."""
        if self.target_agent:
            return self.target_agent.name or self.target_agent.id
        return self.target_agent_id


class Memory(BaseModel):
    """Agent memory structure for scalable memory management."""
    
    content: str = Field("", description="Main memory content from previous interactions")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Memory metadata (timestamps, importance, etc.)"
    )
    context_type: Literal["conversation", "task", "learning", "system"] = Field(
        "conversation", description="Type of memory context"
    )
    importance: float = Field(0.5, ge=0.0, le=1.0, description="Memory importance score")
    created_at: str | None = Field(None, description="Memory creation timestamp")
    last_accessed: str | None = Field(None, description="Last access timestamp")
    
    def is_empty(self) -> bool:
        """Check if memory is empty."""
        return not self.content.strip()
    
    def get_summary(self, max_length: int = 100) -> str:
        """Get a summary of the memory content."""
        if len(self.content) <= max_length:
            return self.content
        return self.content[:max_length].rsplit(' ', 1)[0] + "..."


class LearningObjective(BaseModel):
    """Agent learning objective."""

    objective: str = Field(
        ..., min_length=1, description="Learning objective description"
    )
    success_criteria: list[str] = Field(
        default_factory=list, description="Success criteria for this objective"
    )
    priority: Literal["low", "medium", "high", "critical"] = Field(
        "medium", description="Objective priority"
    )

    @field_validator("success_criteria")
    @classmethod
    def validate_success_criteria(cls, v: list[str]) -> list[str]:
        """Validate success criteria."""
        if not v:
            raise ValueError("At least one success criterion is required")
        return v


class Agent(BaseComponent):
    """Agent configuration domain object (renamed from AgentConfiguration)."""

    instructions: str = Field(
        ..., min_length=10, description="Agent base instructions/prompt"
    )
    processed_instructions: str | None = Field(
        None, description="Enhanced instructions processed with traits, knowledge, and tools"
    )
    model: str = Field(default_factory=_get_default_model, description="LLM model to use")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Model temperature")
    reasoning_effort: Literal["low", "medium", "high"] | None = Field(
        "medium", description="Reasoning effort level"
    )

    # Agent roles and capabilities
    is_orchestrator: bool = Field(
        False, description="Whether this agent is the orchestrator"
    )
    role: str | None = Field(None, description="Agent role (specialist, manager, etc.)")
    max_turns: int | None = Field(None, ge=1, description="Maximum conversation turns")
    debug: bool = Field(False, description="Enable debug mode")

    # Component objects (actual objects, not IDs)
    tools: list[Tool] = Field(
        default_factory=list,
        description="Tool objects assigned to this agent",
    )
    knowledge: list[Knowledge] = Field(
        default_factory=list,
        description="Knowledge base objects assigned to this agent",
    )
    traits: list[Trait] = Field(
        default_factory=list,
        description="Trait objects assigned to this agent",
    )

    # Delegation and handoffs
    handoffs: list[AgentHandoff] = Field(
        default_factory=list, description="Agent handoff configurations"
    )
    delegations: list[AgentDelegation] = Field(
        default_factory=list, description="Agent delegation configurations"
    )

    # Learning system
    learning_objectives: list[LearningObjective] = Field(
        default_factory=list, description="Learning objectives"
    )
    memory: Memory = Field(
        default_factory=Memory, description="Agent memory from previous interactions"
    )

    # Event system
    listen: list[str | dict[str, Any]] = Field(
        default_factory=list, description="Event listeners"
    )
    trigger: list[dict[str, Any]] = Field(
        default_factory=list, description="Event triggers"
    )


    @field_validator("traits")
    @classmethod
    def validate_traits(cls, v: list[Trait]) -> list[Trait]:
        """Validate trait objects."""
        # Check for unique trait IDs
        trait_ids = [trait.id for trait in v]
        if len(trait_ids) != len(set(trait_ids)):
            raise ValueError("Trait IDs must be unique within an agent")

        return v

    @model_validator(mode="after")
    def validate_agent_model(self) -> "Agent":
        """Set name from id if not provided."""
        if not self.name and self.id:
            self.name = self.id.replace("_", " ").replace("-", " ").title()
        return self

    @model_validator(mode="after")
    def ensure_knowledge_query_tool(self) -> "Agent":
        """Automatically inject knowledge_query tool if agent has knowledge bases."""
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Check if agent has knowledge bases but no knowledge_query tool
        if (self.knowledge and 
            not any(tool.id == "knowledge_query" for tool in self.tools)):
            
            # Create knowledge_query tool with standard configuration
            knowledge_query_tool = Tool(
                id="knowledge_query",
                name="Knowledge Query Tool", 
                description="Enhanced knowledge querying with semantic search",
                module="gnosari_engine.tools.builtin.knowledge_query",
                class_name="KnowledgeQueryTool"
            )
            
            # Add to agent's tools
            self.tools.append(knowledge_query_tool)
            
            logger.debug(f"Auto-injected knowledge_query tool for agent {self.id}")
        
        return self

    def get_effective_instructions(self) -> str:
        """
        Get the effective instructions to use for execution.
        
        Returns:
            Processed instructions if available, otherwise raw instructions
        """
        return self.processed_instructions or self.instructions
