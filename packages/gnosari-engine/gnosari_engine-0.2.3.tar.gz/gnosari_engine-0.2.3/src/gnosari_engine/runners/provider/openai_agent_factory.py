"""
OpenAI Agent Factory for creating agents with delegations and handoffs.
Handles complex agent instantiation following SOLID principles.
"""

import logging
from typing import Dict, List, Optional

from agents import Agent

from ...schemas.domain.agent import Agent as GnosariAgent, AgentDelegation, AgentHandoff
from ...schemas.domain.team import Team
from ...tools.components import ToolManager
from .mcp_server_factory import MCPServerFactory, IMCPServerFactory

logger = logging.getLogger(__name__)


class OpenAIAgentFactoryError(Exception):
    """OpenAI agent factory specific errors."""
    pass


class OpenAIAgentFactory:
    """
    Factory for creating OpenAI agents with delegations and handoffs.
    
    Follows SOLID Principles:
    - Single Responsibility: Only responsible for agent creation logic
    - Open/Closed: Extensible for new agent creation patterns
    - Liskov Substitution: Can be used wherever agent creation is needed
    - Interface Segregation: Focused interface for agent creation
    - Dependency Inversion: Depends on abstractions (AgentRun, ToolManager)
    """

    def __init__(self, tool_manager: ToolManager, mcp_factory: IMCPServerFactory = None):
        """Initialize factory with tool manager and MCP factory dependencies."""
        self._tool_manager = tool_manager
        self._mcp_factory = mcp_factory or MCPServerFactory()
        self._agent_cache: Dict[str, Agent] = {}
        self._creation_stack: set[str] = set()  # Track agents being created to prevent infinite recursion

    async def create_agent_with_relations(self, agent: GnosariAgent, team: Team, collect_mcp_configs: bool = True, agent_run=None) -> tuple[Agent, list]:
        """
        Create OpenAI agent with delegations and handoffs configured.

        Args:
            agent: The Gnosari agent configuration
            team: The Gnosari team configuration
            collect_mcp_configs: Whether to collect MCP configs (only at root level)
            agent_run: Optional AgentRun with session metadata for tool initialization

        Returns:
            Tuple of (configured OpenAI Agent, list of MCP configurations for unified async context management)

        Raises:
            OpenAIAgentFactoryError: If agent creation fails
        """
        agent_id = agent.id
        
        # Check for infinite recursion
        if agent_id in self._creation_stack:
            logger.warning(f"Circular dependency detected for agent {agent_id}, skipping recursive creation")
            # Return a simple agent without delegations/handoffs to break the cycle
            return Agent(
                name=agent.name,
                instructions=agent.get_effective_instructions(),
                model=agent.model,  # Pass the configured model
                tools=await self._get_regular_tools(agent, team, agent_run=agent_run)
            ), []
        
        try:
            logger.debug(f"Creating agent {agent.name} with relations")
            
            # Add to creation stack
            self._creation_stack.add(agent_id)
            
            # Create delegation agents as tools (no MCP config collection from them)
            delegation_tools, _ = await self._create_delegation_tools(agent, team, collect_mcp_configs=False, agent_run=agent_run)


            # Get regular tools
            regular_tools = await self._get_regular_tools(agent, team, agent_run=agent_run)

            # Combine all tools
            all_tools = regular_tools + delegation_tools

            # Create handoff agents (no MCP config collection from them)
            handoff_agents, _ = await self._create_handoff_agents(agent, team, collect_mcp_configs=False, agent_run=agent_run)
            
            # Get MCP configurations ONLY for THIS agent (servers created later in unified context)
            agent_mcp_configs = self._get_mcp_configs(agent, team) if collect_mcp_configs else []
            
            # Create the agent without MCP servers (they'll be assigned later in unified async context)
            openai_agent = Agent(
                name=agent.name,
                instructions=agent.get_effective_instructions(),
                model=agent.model,  # Pass the configured model from Gnosari agent
                tools=all_tools,
                handoffs=handoff_agents,
            )
            
            logger.info(f"Created agent {agent.name} with {len(all_tools)} tools, {len(handoff_agents)} handoffs, and {len(agent_mcp_configs)} MCP configs")
            return openai_agent, agent_mcp_configs
            
        except Exception as e:
            logger.error(f"Failed to create agent {agent.name}: {e}")
            raise OpenAIAgentFactoryError(f"Agent creation failed: {e}") from e
        finally:
            # Remove from creation stack
            self._creation_stack.discard(agent_id)

    async def _create_delegation_tools(self, agent: GnosariAgent, team: Team, collect_mcp_configs: bool = True, agent_run=None) -> tuple[List, List]:
        """Create delegation agents as OpenAI tools using .as_tool() and collect their MCP configs."""
        delegation_tools = []
        all_mcp_configs = []

        for delegation in agent.delegations:
            try:
                delegation_agent, delegation_mcp_configs = await self._create_delegation_agent(delegation, team, collect_mcp_configs, agent_run=agent_run)
                
                # Convert delegation agent to tool using .as_tool()
                tool_name = self._generate_delegation_tool_name(delegation)
                tool_description = delegation.instructions
                
                delegation_tool = delegation_agent.as_tool(
                    tool_name=tool_name,
                    tool_description=tool_description
                )
                
                delegation_tools.append(delegation_tool)
                if collect_mcp_configs:
                    all_mcp_configs.extend(delegation_mcp_configs)
                logger.debug(f"Created delegation tool {tool_name} for agent {delegation.get_target_name()} with {len(delegation_mcp_configs) if collect_mcp_configs else 0} MCP configs")
                
            except Exception as e:
                logger.warning(f"Failed to create delegation tool for {delegation.get_target_name()}: {e}")
                
        return delegation_tools, all_mcp_configs

    async def _create_handoff_agents(self, agent: GnosariAgent, team: Team, collect_mcp_configs: bool = True, agent_run=None) -> tuple[List[Agent], List]:
        """Create handoff agents for OpenAI handoffs array and collect their MCP configs."""
        handoff_agents = []
        all_mcp_configs = []

        for handoff in agent.handoffs:
            try:
                handoff_agent, handoff_mcp_configs = await self._create_handoff_agent(handoff, team, collect_mcp_configs, agent_run=agent_run)
                handoff_agents.append(handoff_agent)
                if collect_mcp_configs:
                    all_mcp_configs.extend(handoff_mcp_configs)
                logger.debug(f"Created handoff agent {handoff.get_target_name()} with {len(handoff_mcp_configs) if collect_mcp_configs else 0} MCP configs")
                
            except Exception as e:
                logger.warning(f"Failed to create handoff agent for {handoff.get_target_name()}: {e}")
                
        return handoff_agents, all_mcp_configs

    async def _get_regular_tools(self, agent: GnosariAgent, team: Team, agent_run=None) -> List:
        """Get regular (non-delegation, non-MCP) tools for the agent."""
        tools = agent.tools  # Direct access to tools property
        openai_tools = []

        if tools and self._tool_manager:
            # Use the provided agent_run if available, otherwise create a temporary one
            # The provided agent_run should have session_id and other metadata populated
            if agent_run is None:
                from ...schemas.domain.execution import AgentRun
                agent_run = AgentRun(agent=agent, team=team, message="Dummy Message")
                logger.debug(f"Created temporary AgentRun for tool initialization (no session metadata)")
            else:
                logger.debug(f"Using provided AgentRun with session_id: {agent_run.metadata.session_id if agent_run.metadata else 'None'}")

            for tool in tools:
                # Skip MCP tools as they're handled separately
                if tool.is_mcp_tool():
                    continue

                try:
                    tool_implementation = await self._tool_manager.get_tool_implementation(tool, agent_run=agent_run)
                    openai_tools.append(tool_implementation)
                    logger.debug(f"Added regular tool {tool.id} to agent {agent.name}")
                except Exception as e:
                    logger.warning(f"Failed to load tool {tool.id} for agent {agent.name}: {e}")

        return openai_tools

    def _get_mcp_configs(self, agent: GnosariAgent, team: Team) -> List:
        """Get MCP tool configurations for the agent."""
        mcp_tools = [tool for tool in agent.tools if tool.is_mcp_tool()]
        
        if not mcp_tools:
            logger.debug(f"No MCP tools found for agent {agent.name}")
            return []
        
        logger.debug(f"Found {len(mcp_tools)} MCP tool configs for agent {agent.name}")
        return mcp_tools

    async def _create_delegation_agent(self, delegation: AgentDelegation, team: Team, collect_mcp_configs: bool = True, agent_run=None) -> tuple[Agent, List]:
        """Create a delegation agent from delegation configuration with full recursive creation."""
        # Use resolved target_agent if available, otherwise fall back to lookup
        target_agent = delegation.target_agent
        if not target_agent:
            logger.debug(f"Delegation target_agent is None, looking up by target_agent_id: {delegation.target_agent_id}")
            target_agent = self._find_agent_in_team(delegation.target_agent_id, team)
            if not target_agent:
                logger.error(f"Agent lookup failed for target_agent_id: {delegation.target_agent_id}")
                logger.debug(f"Available agents in team: {[agent.id for agent in team.agents]}")
                raise OpenAIAgentFactoryError(f"Delegation target agent not found: {delegation.target_agent_id}")

        logger.debug(f"Creating delegation agent for target: {target_agent.id}")
        return await self._create_target_agent(
            target_agent=target_agent,
            team=team,
            cache_prefix="delegation",
            relation_type="delegation",
            target_name=delegation.get_target_name(),
            collect_mcp_configs=collect_mcp_configs,
            agent_run=agent_run
        )

    async def _create_handoff_agent(self, handoff: AgentHandoff, team: Team, collect_mcp_configs: bool = True, agent_run=None) -> tuple[Agent, List]:
        """Create a handoff agent from handoff configuration with full recursive creation."""
        # Use resolved target_agent if available, otherwise fall back to lookup
        target_agent = handoff.target_agent
        if not target_agent:
            target_agent = self._find_agent_in_team(handoff.target_agent_id, team)
            if not target_agent:
                raise OpenAIAgentFactoryError(f"Handoff target agent not found: {handoff.target_agent_id}")

        return await self._create_target_agent(
            target_agent=target_agent,
            team=team,
            cache_prefix="handoff",
            relation_type="handoff",
            target_name=handoff.get_target_name(),
            collect_mcp_configs=collect_mcp_configs,
            agent_run=agent_run
        )

    async def _create_target_agent(
        self,
        target_agent: GnosariAgent,
        team: Team,
        cache_prefix: str,
        relation_type: str,
        target_name: str,
        collect_mcp_configs: bool = True,
        agent_run=None
    ) -> tuple[Agent, List]:
        """Common method to create target agents for delegations and handoffs with full recursive creation."""
        if target_agent is None:
            raise OpenAIAgentFactoryError(f"Target agent is None for {relation_type} relation")

        cache_key = f"{cache_prefix}_{target_agent.id}_{id(team)}"

        if cache_key in self._agent_cache:
            logger.debug(f"Using cached {relation_type} agent for {target_name}")
            # For cached agents, we only get MCP configs if we're collecting them
            target_mcp_configs = self._get_mcp_configs(target_agent, team) if collect_mcp_configs else []
            return self._agent_cache[cache_key], target_mcp_configs

        # Check if we're in the middle of creating this agent (true circular dependency)
        if target_agent.id in self._creation_stack:
            logger.debug(f"Agent {target_name} is already being created, using cached simple agent to prevent infinite recursion")
            # Create a simple agent without delegations/handoffs to break the recursion
            simple_agent = Agent(
                name=target_agent.name,
                instructions=target_agent.get_effective_instructions(),
                model=target_agent.model,  # Pass the configured model
                tools=await self._get_regular_tools(target_agent, team, agent_run=agent_run)
            )
            # Cache the simple agent to avoid recreating it
            self._agent_cache[cache_key] = simple_agent
            logger.debug(f"Created and cached simple {relation_type} agent {target_name} (recursion prevention)")

            # Only collect MCP configs if we're at the collection level
            target_mcp_configs = self._get_mcp_configs(target_agent, team) if collect_mcp_configs else []
            return simple_agent, target_mcp_configs

        # Use the full factory method to create agent with all its relations
        # Each agent gets its own MCP servers, so always collect_mcp_configs=True for the agent itself
        # Pass agent_run through to ensure ALL tools in the execution share the same session_id
        openai_agent, target_mcp_configs = await self.create_agent_with_relations(target_agent, team, collect_mcp_configs=True, agent_run=agent_run)

        # Cache the agent (we don't cache MCP configs as they're collected fresh each time)
        self._agent_cache[cache_key] = openai_agent
        logger.debug(f"Created and cached {relation_type} agent {target_name}")

        return openai_agent, target_mcp_configs

    def _find_agent_in_team(self, agent_id: str, team: Team) -> Optional[GnosariAgent]:
        """Find agent configuration in team by ID."""
        for agent_config in team.agents:
            if agent_config.id == agent_id:
                return agent_config
        return None

    def _generate_delegation_tool_name(self, delegation: AgentDelegation) -> str:
        """Generate a tool name for delegation."""
        # Use target agent name or ID, sanitized for tool naming
        if delegation.target_agent:
            base_name = delegation.target_agent.id
        else:
            base_name = delegation.target_agent_id
        return f"delegate_to_{base_name}"

    def _generate_delegation_tool_description(self, delegation: AgentDelegation) -> str:
        """Generate a tool description for delegation."""
        target_name = delegation.get_target_name()
        
        if delegation.instructions:
            return f"Delegate task to {target_name}: {delegation.instructions}"
        else:
            return f"Delegate task to {target_name} agent"

    def clear_cache(self) -> None:
        """Clear the agent cache and creation stack."""
        self._agent_cache.clear()
        self._creation_stack.clear()
        logger.debug("Cleared agent factory cache and creation stack")