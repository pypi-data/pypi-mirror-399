"""
Single Responsibility services for configuration loading and transformation.
Each service follows SRP by handling only one specific aspect of configuration processing.
"""

import logging
import os
from pathlib import Path
from typing import Any, Literal

import yaml

from ..schemas.domain import Agent, Knowledge, Team, TeamConfiguration, Tool, Trait
from .interfaces import (
    IComponentIndexer,
    IComponentResolver,
    IConfigurationParser,
    IConfigurationValidator,
    IDelegationResolver,
    IDomainObjectBuilder,
    IEnvironmentSubstitutor,
    IHandoffResolver,
)


# Custom exceptions for better error handling
class ConfigurationParsingError(Exception):
    """Exception raised during configuration parsing."""

    pass


class ConfigurationValidationError(Exception):
    """Exception raised during configuration validation."""

    def __init__(
        self,
        message: str,
        errors: list[str] | None = None,
        config_path: str | None = None,
    ):
        super().__init__(message)
        self.errors = errors or []
        self.config_path = config_path


class DomainObjectBuildError(Exception):
    """Exception raised during domain object building."""

    pass


class DelegationResolutionError(Exception):
    """Exception raised during delegation resolution."""

    def __init__(self, message: str, agent_id: str | None = None):
        super().__init__(message)
        self.agent_id = agent_id


class HandoffResolutionError(Exception):
    """Exception raised during handoff resolution."""

    def __init__(self, message: str, agent_id: str | None = None):
        super().__init__(message)
        self.agent_id = agent_id


class ConfigurationServiceError(Exception):
    """Exception raised by configuration service."""

    def __init__(self, message: str, config_path: str | None = None):
        """Initialize with message and optional config path."""
        super().__init__(message)
        self.config_path = config_path


class ConfigurationParser(IConfigurationParser):
    """Single responsibility: Parse YAML to dictionary."""

    def __init__(self, env_substitutor: IEnvironmentSubstitutor) -> None:
        self._env_substitutor = env_substitutor
        self._logger = logging.getLogger(__name__)

    def parse_yaml_to_dict(self, config_path: Path) -> dict[str, Any]:
        """Parse YAML file to dictionary with environment substitution."""
        try:
            self._logger.debug(f"Parsing YAML file: {config_path}")

            with open(config_path, encoding="utf-8") as f:
                raw_config = yaml.safe_load(f)

            if raw_config is None:
                raise ConfigurationParsingError(
                    f"Empty or invalid YAML file: {config_path}"
                )

            # Apply environment variable substitution
            substituted_config = self._env_substitutor.substitute(raw_config)

            self._logger.debug(f"Successfully parsed YAML file: {config_path}")
            return substituted_config

        except yaml.YAMLError as e:
            raise ConfigurationParsingError(
                f"YAML parsing error in {config_path}: {e}"
            ) from e
        except FileNotFoundError as e:
            raise ConfigurationParsingError(
                f"Configuration file not found: {config_path}"
            ) from e
        except Exception as e:
            raise ConfigurationParsingError(
                f"Failed to parse {config_path}: {e}"
            ) from e


class ConfigurationValidator(IConfigurationValidator):
    """Single responsibility: Validate configuration structure."""

    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)

    def validate_structure(self, config: dict[str, Any]) -> list[str]:
        """Validate configuration structure and return error list."""
        errors = []

        # Required field validation
        if not config.get("name"):
            errors.append("Team name is required")

        if not config.get("agents"):
            errors.append("Team must have at least one agent")

        # Agent validation
        agents = config.get("agents", [])
        if agents:
            self._validate_agents(agents, errors)

        # Component reference validation
        self._validate_component_references(config, errors)

        # Configuration structure validation
        self._validate_configuration_structure(config, errors)

        if errors:
            self._logger.warning(f"Configuration validation found {len(errors)} errors")
        else:
            self._logger.debug("Configuration validation passed")

        return errors

    def _validate_agents(self, agents: list[dict[str, Any]], errors: list[str]) -> None:
        """Validate agent configurations."""
        orchestrator_count = 0
        agent_names = []
        agent_ids = []

        for i, agent in enumerate(agents):
            # Required fields
            if not agent.get("name"):
                errors.append(f"Agent {i} is missing required field: name")
            else:
                agent_names.append(agent["name"])

            if not agent.get("instructions"):
                errors.append(f"Agent {i} is missing required field: instructions")

            # ID validation (use name if id not provided)
            agent_id = agent.get("id", agent.get("name", f"agent_{i}"))
            agent_ids.append(agent_id)

            # Orchestrator validation
            if agent.get("orchestrator", False):
                orchestrator_count += 1

        # Unique name validation
        if len(agent_names) != len(set(agent_names)):
            errors.append("Agent names must be unique within team")

        # Unique ID validation
        if len(agent_ids) != len(set(agent_ids)):
            errors.append("Agent IDs must be unique within team")

        # Orchestrator count validation
        if orchestrator_count != 1:
            errors.append(
                f"Team must have exactly one orchestrator, found {orchestrator_count}"
            )

    def _validate_component_references(
        self, config: dict[str, Any], errors: list[str]
    ) -> None:
        """Validate that component references are valid."""
        available_tools = {
            tool.get("id", tool.get("name", "")) for tool in config.get("tools", [])
        }
        available_knowledge = {
            kb.get("id", kb.get("name", "")) for kb in config.get("knowledge", [])
        }
        available_traits = {
            trait.get("id", trait.get("name", "")) for trait in config.get("traits", [])
        }

        for agent in config.get("agents", []):
            agent_name = agent.get("name", "unknown")

            # Validate tool references
            for tool_ref in agent.get("tools", []):
                if tool_ref not in available_tools:
                    errors.append(
                        f"Agent '{agent_name}' references unknown tool '{tool_ref}'"
                    )

            # Validate knowledge references
            for kb_ref in agent.get("knowledge", []):
                if kb_ref not in available_knowledge:
                    errors.append(
                        f"Agent '{agent_name}' references unknown knowledge base '{kb_ref}'"
                    )

            # Validate trait references
            for trait_ref in agent.get("traits", []):
                if isinstance(trait_ref, str) and trait_ref not in available_traits:
                    errors.append(
                        f"Agent '{agent_name}' references unknown trait '{trait_ref}'"
                    )

    def _validate_configuration_structure(
        self, config: dict[str, Any], errors: list[str]
    ) -> None:
        """Validate overall configuration structure."""
        # Validate that configuration is a dictionary
        if not isinstance(config, dict):
            errors.append("Configuration must be a dictionary")
            return

        # Validate component lists are actually lists
        for component_type in ["agents", "tools", "knowledge", "traits"]:
            if component_type in config and not isinstance(
                config[component_type], list
            ):
                errors.append(f"'{component_type}' must be a list")


class DomainObjectBuilder(IDomainObjectBuilder):
    """Single responsibility: Build domain objects from validated configuration."""

    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)

    def _validate_connection_type(
        self, connection_type: str
    ) -> Literal["sse", "streamable_http", "stdio"]:
        """Validate and return a valid connection type."""
        valid_types: list[Literal["sse", "streamable_http", "stdio"]] = [
            "sse",
            "streamable_http",
            "stdio",
        ]
        if connection_type in valid_types:
            return connection_type  # type: ignore
        else:
            self._logger.warning(
                f"Invalid connection_type '{connection_type}', defaulting to 'sse'"
            )
            return "sse"

    def build_team(self, config: dict[str, Any]) -> Team:
        """Build Team domain object from configuration dictionary."""
        try:
            self._logger.debug("Building Team domain object")

            # Build components first
            tools = self.build_tools(config.get("tools", []))
            knowledge = self.build_knowledge(config.get("knowledge", []))
            traits = self.build_traits(config.get("traits", []))
            
            # Build agents with access to components for reference resolution
            agents = self.build_agents(
                config.get("agents", []), 
                tools=tools, 
                knowledge=knowledge, 
                traits=traits
            )
            
            return Team(
                id=config.get(
                    "id", config.get("name", "unknown").lower().replace(" ", "_")
                ),
                name=config.get("name", "Unknown Team"),
                description=config.get("description"),
                account_id=config.get("account_id"),
                config=TeamConfiguration(
                    max_turns=config.get("max_turns"),
                    timeout=config.get("timeout"),
                    log_level=config.get("log_level", "INFO"),
                    enable_memory=config.get("enable_memory", True),
                ),
                agents=agents,
                tools=tools,
                knowledge=knowledge,
                traits=traits,
                overrides=config.get("overrides", {}),
                components=config.get("components", {}),
            )
        except Exception as e:
            raise DomainObjectBuildError(f"Failed to build Team: {e}") from e

    def build_agents(
        self, 
        agents_data: list[dict[str, Any]], 
        tools: list[Tool], 
        knowledge: list[Knowledge], 
        traits: list[Trait]
    ) -> list[Agent]:
        """Build list of Agent objects with resolved component references."""
        agents = []
        
        # Create lookup dictionaries for efficient reference resolution
        tools_by_id = {tool.id: tool for tool in tools}
        knowledge_by_id = {kb.id: kb for kb in knowledge}
        traits_by_id = {trait.id: trait for trait in traits}
        
        for i, agent_data in enumerate(agents_data):
            try:
                # Resolve tool references
                agent_tools = []
                for tool_id in agent_data.get("tools", []):
                    if tool_id in tools_by_id:
                        agent_tools.append(tools_by_id[tool_id])
                    else:
                        self._logger.warning(f"Tool '{tool_id}' not found for agent {i}")
                
                # Resolve knowledge references
                agent_knowledge = []
                for kb_id in agent_data.get("knowledge", []):
                    if kb_id in knowledge_by_id:
                        agent_knowledge.append(knowledge_by_id[kb_id])
                    else:
                        self._logger.warning(f"Knowledge '{kb_id}' not found for agent {i}")
                
                # Resolve trait references
                agent_traits = []
                for trait_id in agent_data.get("traits", []):
                    if trait_id in traits_by_id:
                        agent_traits.append(traits_by_id[trait_id])
                    else:
                        self._logger.warning(f"Trait '{trait_id}' not found for agent {i}")
                
                # Get default model from env vars (OPENAI_MODEL or DEFAULT_LLM_MODEL)
                default_model = os.getenv("OPENAI_MODEL") or os.getenv("DEFAULT_LLM_MODEL") or "gpt-4o"

                agent = Agent(
                    id=agent_data.get("id", agent_data.get("name", f"agent_{i}")),
                    name=agent_data.get("name", f"Agent {i}"),
                    instructions=agent_data.get("instructions", ""),
                    model=agent_data.get("model", default_model),
                    temperature=agent_data.get("temperature", 0.7),
                    reasoning_effort=agent_data.get("reasoning_effort"),
                    is_orchestrator=agent_data.get("orchestrator", False),
                    tools=agent_tools,  # Now actual Tool objects
                    knowledge=agent_knowledge,  # Now actual Knowledge objects
                    traits=agent_traits,  # Now actual Trait objects
                    handoffs=self._build_handoffs(agent_data.get("handoffs", [])),
                    delegations=self._build_delegations(
                        agent_data.get("delegations", [])
                    ),
                    learning_objectives=self._build_learning_objectives(
                        agent_data.get("learning_objectives", [])
                    ),
                    memory=self._build_memory(agent_data.get("memory", {})),
                    listen=agent_data.get("listen", []),
                    trigger=agent_data.get("trigger", []),
                )
                agents.append(agent)
            except Exception as e:
                raise DomainObjectBuildError(f"Failed to build agent {i}: {e}") from e

        return agents

    def build_tools(self, tools_data: list[dict[str, Any]]) -> list[Tool]:
        """Build list of Tool objects."""
        tools = []
        for i, tool_data in enumerate(tools_data):
            try:
                tool = Tool(
                    id=tool_data.get("id", tool_data.get("name", f"tool_{i}")),
                    name=tool_data.get("name", f"Tool {i}"),
                    description=tool_data.get("description"),
                    module=tool_data.get("module"),
                    class_name=tool_data.get("class_name") or tool_data.get("class"),
                    url=tool_data.get("url"),
                    command=tool_data.get("command"),
                    connection_type=self._validate_connection_type(
                        tool_data.get("connection_type", "sse")
                    ),
                    args=tool_data.get("args", {}),
                    headers=tool_data.get("headers", {}),
                    timeout=tool_data.get("timeout", 30),
                    rate_limit=tool_data.get("rate_limit"),
                    enable_caching=tool_data.get("enable_caching", True),
                    cache_timeout=tool_data.get("cache_timeout", 3600),
                    retry_attempts=tool_data.get("retry_attempts", 3),
                    retry_delay=tool_data.get("retry_delay", 1.0),
                )
                tools.append(tool)
            except Exception as e:
                raise DomainObjectBuildError(f"Failed to build tool {i}: {e}") from e

        return tools

    def build_knowledge(self, knowledge_data: list[dict[str, Any]]) -> list[Knowledge]:
        """Build list of Knowledge objects."""
        knowledge_bases = []
        for i, kb_data in enumerate(knowledge_data):
            try:
                kb = Knowledge(
                    id=kb_data.get("id", kb_data.get("name", f"kb_{i}")),
                    name=kb_data.get("name", f"Knowledge Base {i}"),
                    description=kb_data.get("description"),
                    type=kb_data.get("type", "website"),
                    data=kb_data.get("data", []),
                    config=kb_data.get("config", {}),
                )
                knowledge_bases.append(kb)
            except Exception as e:
                raise DomainObjectBuildError(
                    f"Failed to build knowledge base {i}: {e}"
                ) from e

        return knowledge_bases

    def build_traits(self, traits_data: list[dict[str, Any]]) -> list[Trait]:
        """Build list of Trait objects."""
        traits = []
        for i, trait_data in enumerate(traits_data):
            try:
                trait = Trait(
                    id=trait_data.get("id", trait_data.get("name", f"trait_{i}")),
                    name=trait_data.get("name", f"Trait {i}"),
                    description=trait_data.get("description"),
                    instructions=trait_data.get("instructions", ""),
                    weight=trait_data.get("weight", 1.0),
                    category=trait_data.get("category"),
                    tags=trait_data.get("tags", []),
                )
                traits.append(trait)
            except Exception as e:
                raise DomainObjectBuildError(f"Failed to build trait {i}: {e}") from e

        return traits

    def _build_learning_entries(self, learning_data: list[dict[str, Any]]) -> list:
        """Build learning entries (simplified for now)."""
        return learning_data  # Will be enhanced later

    def _build_handoffs(self, handoffs_data: list[dict[str, Any]]) -> list:
        """Build handoff configurations with proper AgentHandoff objects."""
        from ..schemas.domain.agent import AgentHandoff
        
        handoffs = []
        for i, handoff_data in enumerate(handoffs_data):
            try:
                handoff = AgentHandoff(
                    target_agent_id=handoff_data.get("target_agent", f"unknown_{i}"),
                    condition=handoff_data.get("condition"),
                    message=handoff_data.get("message"),
                )
                handoffs.append(handoff)
            except Exception as e:
                raise DomainObjectBuildError(f"Failed to build handoff {i}: {e}") from e
        
        return handoffs

    def _build_delegations(self, delegations_data: list[dict[str, Any]]) -> list:
        """Build delegation configurations with proper AgentDelegation objects."""
        from ..schemas.domain.agent import AgentDelegation
        
        delegations = []
        for i, delegation_data in enumerate(delegations_data):
            try:
                delegation = AgentDelegation(
                    target_agent_id=delegation_data.get("target_agent", f"unknown_{i}"),
                    instructions=delegation_data.get("instructions"),
                    mode=delegation_data.get("mode", "sync"),
                    timeout=delegation_data.get("timeout"),
                    retry_attempts=delegation_data.get("retry_attempts", 1),
                )
                delegations.append(delegation)
            except Exception as e:
                raise DomainObjectBuildError(f"Failed to build delegation {i}: {e}") from e
        
        return delegations

    def _build_learning_objectives(self, objectives_data: list[dict[str, Any]]) -> list:
        """Build learning objectives from configuration data."""
        from ..schemas.domain.agent import LearningObjective
        
        objectives = []
        for i, obj_data in enumerate(objectives_data):
            try:
                objective = LearningObjective(
                    objective=obj_data.get("objective", f"Learning objective {i}"),
                    success_criteria=obj_data.get("success_criteria", ["Complete objective"]),
                    priority=obj_data.get("priority", "medium"),
                )
                objectives.append(objective)
            except Exception as e:
                raise DomainObjectBuildError(f"Failed to build learning objective {i}: {e}") from e
        
        return objectives

    def _build_memory(self, memory_data: dict[str, Any] | str) -> object:
        """Build memory object from configuration data."""
        from ..schemas.domain.agent import Memory
        
        # Handle both string and dict formats
        if isinstance(memory_data, str):
            # Simple string format - create basic memory
            return Memory(
                content=memory_data,
                context_type="conversation",
                importance=0.5
            )
        elif isinstance(memory_data, dict):
            # Dict format - full memory configuration
            return Memory(
                content=memory_data.get("content", ""),
                metadata=memory_data.get("metadata", {}),
                context_type=memory_data.get("context_type", "conversation"),
                importance=memory_data.get("importance", 0.5),
                created_at=memory_data.get("created_at"),
                last_accessed=memory_data.get("last_accessed"),
            )
        else:
            # Default empty memory
            return Memory()


class ComponentIndexer(IComponentIndexer):
    """Single responsibility: Create performance indexes for domain objects."""

    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)

    def add_indexes_to_team(self, team) -> "Team":
        """Add O(1) lookup indexes to team object."""
        import time

        try:
            start_time = time.time()
            self._logger.debug(f"Adding performance indexes to team: {team.name}")

            # Create indexes for fast component lookup using the correct field names
            team.agent_index = {agent.id: agent for agent in team.agents}
            team.agent_name_index = {
                agent.name: agent for agent in team.agents if agent.name
            }
            team.tool_index = {tool.id: tool for tool in team.tools}
            team.knowledge_index = {kb.id: kb for kb in team.knowledge}
            team.trait_index = {trait.id: trait for trait in team.traits}

            end_time = time.time()
            index_time_ms = (end_time - start_time) * 1000

            self._logger.debug(
                f"Performance indexes added to team: {team.name} in {index_time_ms:.2f}ms"
            )
            return team

        except Exception as e:
            self._logger.warning(f"Failed to add indexes to team: {e}")
            return team


class LazyComponentResolver(IComponentResolver):
    """Strategy: Resolve component references on-demand for memory efficiency."""

    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)

    def resolve_references(self, team: Team) -> Team:
        """Add lazy resolution methods to team."""
        try:
            self._logger.debug(
                f"Setting up lazy component resolution for team: {team.name}"
            )

            # For now, we'll implement basic reference validation
            # The actual lazy resolution would be implemented in the Team domain object
            # with method injection for on-demand resolution

            self._validate_references(team)

            return team

        except Exception as e:
            self._logger.warning(f"Failed to setup lazy resolution: {e}")
            return team

    def _validate_references(self, team: Team) -> None:
        """Validate that all references can be resolved."""
        tool_ids = {tool.id for tool in team.tools}
        knowledge_ids = {kb.id for kb in team.knowledge}
        trait_ids = {trait.id for trait in team.traits}

        for agent in team.agents:
            # Validate tool references
            for tool_ref in agent.tools:
                if tool_ref not in tool_ids:
                    self._logger.warning(
                        f"Agent '{agent.name}' references unknown tool '{tool_ref}'"
                    )

            # Validate knowledge references
            for kb_ref in agent.knowledge:
                if kb_ref not in knowledge_ids:
                    self._logger.warning(
                        f"Agent '{agent.name}' references unknown knowledge '{kb_ref}'"
                    )

            # Validate trait references
            for trait_ref in agent.traits:
                if trait_ref not in trait_ids:
                    self._logger.warning(
                        f"Agent '{agent.name}' references unknown trait '{trait_ref}'"
                    )


class EagerComponentResolver(IComponentResolver):
    """Strategy: Resolve all component references upfront for performance."""

    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)

    def resolve_references(self, team: Team) -> Team:
        """Pre-resolve all component references."""
        try:
            self._logger.debug(
                f"Eagerly resolving component references for team: {team.name}"
            )

            # TODO: Implement component reference resolution
            # This would resolve tool/knowledge/trait references within agents
            # Following SRP, this logic should be delegated to appropriate resolver services
            # Create lookup dictionaries
            # tool_map = {tool.id: tool for tool in team.tools}
            # knowledge_map = {kb.id: kb for kb in team.knowledge}
            # trait_map = {trait.id: trait for trait in team.traits}

            # Resolve references for each agent
            # for agent in team.agents:
            # This would be implemented in the actual Agent domain object
            # agent._resolved_tools = [tool_map.get(tool_ref) for tool_ref in agent.tools]
            # agent._resolved_knowledge = [knowledge_map.get(kb_ref) for kb_ref in agent.knowledge]
            # agent._resolved_traits = [trait_map.get(trait_ref) for trait_ref in agent.traits]
            # pass

            return team

        except Exception as e:
            self._logger.warning(f"Failed to eagerly resolve references: {e}")
            return team


class DelegationResolver(IDelegationResolver):
    """Single responsibility: Resolve agent delegation references to actual Agent objects."""

    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)

    def resolve_delegations(self, team: Team) -> Team:
        """
        Resolve agent delegation references to actual Agent objects.
        
        This service follows the Single Responsibility Principle by focusing
        solely on delegation reference resolution.
        """
        try:
            self._logger.debug(f"Resolving delegations for team: {team.name}")
            
            # Create agent lookup for efficient resolution
            agent_lookup = {agent.id: agent for agent in team.agents}
            agent_name_lookup = {agent.name: agent for agent in team.agents if agent.name}
            
            resolved_agents = []
            
            for agent in team.agents:
                resolved_delegations = []
                
                for delegation in agent.delegations:
                    try:
                        resolved_delegation = self._resolve_single_delegation(
                            delegation, agent_lookup, agent_name_lookup, agent.id
                        )
                        resolved_delegations.append(resolved_delegation)
                    except DelegationResolutionError as e:
                        self._logger.warning(
                            f"Failed to resolve delegation for agent '{agent.id}': {e}"
                        )
                        # Keep unresolved delegation for debugging
                        resolved_delegations.append(delegation)
                
                # Create new agent with resolved delegations
                resolved_agent = agent.model_copy(update={"delegations": resolved_delegations})
                resolved_agents.append(resolved_agent)
            
            # Return team with resolved delegations
            resolved_team = team.model_copy(update={"agents": resolved_agents})
            
            # CRITICAL: Rebuild indexes to point to the new agents
            # The model_copy copies the old indexes which still point to the original agents
            resolved_team.agent_index = {agent.id: agent for agent in resolved_team.agents}
            resolved_team.agent_name_index = {
                agent.name: agent for agent in resolved_team.agents if agent.name
            }
            
            self._logger.debug(f"Successfully resolved delegations for team: {team.name}")
            return resolved_team
            
        except Exception as e:
            self._logger.error(f"Failed to resolve delegations for team '{team.name}': {e}")
            # Return original team on error to avoid breaking the build process
            return team

    def _resolve_single_delegation(
        self, 
        delegation: "AgentDelegation", 
        agent_lookup: dict[str, Agent], 
        agent_name_lookup: dict[str, Agent],
        source_agent_id: str
    ) -> "AgentDelegation":
        """Resolve a single delegation reference to an Agent object."""
        from ..schemas.domain.agent import AgentDelegation
        
        target_agent_id = delegation.target_agent_id
        target_agent = None
        
        # Try to resolve by ID first
        if target_agent_id in agent_lookup:
            target_agent = agent_lookup[target_agent_id]
        # Fallback to name lookup
        elif target_agent_id in agent_name_lookup:
            target_agent = agent_name_lookup[target_agent_id]
        
        if target_agent is None:
            raise DelegationResolutionError(
                f"Target agent '{target_agent_id}' not found in team", 
                source_agent_id
            )
        
        # Prevent self-delegation
        if target_agent.id == source_agent_id:
            raise DelegationResolutionError(
                f"Agent '{source_agent_id}' cannot delegate to itself", 
                source_agent_id
            )
        
        # Create resolved delegation
        return AgentDelegation(
            target_agent_id=delegation.target_agent_id,
            target_agent=target_agent,  # Now resolved to actual Agent object
            instructions=delegation.instructions,
            mode=delegation.mode,
            timeout=delegation.timeout,
            retry_attempts=delegation.retry_attempts,
        )


class HandoffResolver(IHandoffResolver):
    """Single responsibility: Resolve agent handoff references to actual Agent objects."""

    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)

    def resolve_handoffs(self, team: Team) -> Team:
        """
        Resolve agent handoff references to actual Agent objects.
        
        This service follows the Single Responsibility Principle by focusing
        solely on handoff reference resolution.
        """
        try:
            self._logger.debug(f"Resolving handoffs for team: {team.name}")
            
            # Create agent lookup for efficient resolution
            agent_lookup = {agent.id: agent for agent in team.agents}
            agent_name_lookup = {agent.name: agent for agent in team.agents if agent.name}
            
            resolved_agents = []
            
            for agent in team.agents:
                resolved_handoffs = []
                
                for handoff in agent.handoffs:
                    try:
                        resolved_handoff = self._resolve_single_handoff(
                            handoff, agent_lookup, agent_name_lookup, agent.id
                        )
                        resolved_handoffs.append(resolved_handoff)
                    except HandoffResolutionError as e:
                        self._logger.warning(
                            f"Failed to resolve handoff for agent '{agent.id}': {e}"
                        )
                        # Keep unresolved handoff for debugging
                        resolved_handoffs.append(handoff)
                
                # Create new agent with resolved handoffs
                resolved_agent = agent.model_copy(update={"handoffs": resolved_handoffs})
                resolved_agents.append(resolved_agent)
            
            # Return team with resolved handoffs
            resolved_team = team.model_copy(update={"agents": resolved_agents})
            
            # CRITICAL: Rebuild indexes to point to the new agents
            # The model_copy copies the old indexes which still point to the original agents
            resolved_team.agent_index = {agent.id: agent for agent in resolved_team.agents}
            resolved_team.agent_name_index = {
                agent.name: agent for agent in resolved_team.agents if agent.name
            }
            
            self._logger.debug(f"Successfully resolved handoffs for team: {team.name}")
            return resolved_team
            
        except Exception as e:
            self._logger.error(f"Failed to resolve handoffs for team '{team.name}': {e}")
            # Return original team on error to avoid breaking the build process
            return team

    def _resolve_single_handoff(
        self, 
        handoff: "AgentHandoff", 
        agent_lookup: dict[str, Agent], 
        agent_name_lookup: dict[str, Agent],
        source_agent_id: str
    ) -> "AgentHandoff":
        """Resolve a single handoff reference to an Agent object."""
        from ..schemas.domain.agent import AgentHandoff
        
        target_agent_id = handoff.target_agent_id
        target_agent = None
        
        # Try to resolve by ID first
        if target_agent_id in agent_lookup:
            target_agent = agent_lookup[target_agent_id]
        # Fallback to name lookup
        elif target_agent_id in agent_name_lookup:
            target_agent = agent_name_lookup[target_agent_id]
        
        if target_agent is None:
            raise HandoffResolutionError(
                f"Target agent '{target_agent_id}' not found in team", 
                source_agent_id
            )
        
        # Prevent self-handoff
        if target_agent.id == source_agent_id:
            raise HandoffResolutionError(
                f"Agent '{source_agent_id}' cannot handoff to itself", 
                source_agent_id
            )
        
        # Create resolved handoff
        return AgentHandoff(
            target_agent_id=handoff.target_agent_id,
            target_agent=target_agent,  # Now resolved to actual Agent object
            condition=handoff.condition,
            message=handoff.message,
        )
