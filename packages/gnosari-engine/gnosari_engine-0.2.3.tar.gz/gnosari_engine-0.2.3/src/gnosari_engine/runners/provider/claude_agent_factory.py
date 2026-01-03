"""
Claude agent factory implementation.
Creates Claude SDK clients with tools, delegations, and handoffs.
"""

import logging
import os
from typing import List, Dict, Any, Optional, Tuple

from ...schemas.domain import Agent, Team, Tool as DomainTool
from ...tools.components import ToolManager
from .mcp_server_factory import MCPServerFactory

logger = logging.getLogger(__name__)


class ClaudeAgentFactoryError(Exception):
    """Claude agent factory specific errors."""
    pass


class ClaudeAgentFactory:
    """
    Factory for creating Claude SDK clients with tools, delegations, and handoffs.
    
    Follows Single Responsibility Principle: Only responsible for creating
    Claude SDK configurations and managing agent relationships.
    """

    def __init__(self, tool_manager: ToolManager):
        self._tool_manager = tool_manager
        self._mcp_factory = MCPServerFactory() if MCPServerFactory else None
        self._agent_cache: Dict[str, Any] = {}
        
    def clear_cache(self) -> None:
        """Clear the agent cache."""
        self._agent_cache.clear()

    async def create_claude_options_with_relations(self, agent: Agent, team: Team) -> Tuple[Any, List]:
        """
        Create Claude SDK options with configured tools, delegations, and handoffs.
        
        Args:
            agent: The primary agent to create options for
            team: The team context containing other agents
            
        Returns:
            Tuple of (ClaudeAgentOptions, mcp_configs)
        """
        try:
            from claude_agent_sdk import ClaudeAgentOptions
        except ImportError as e:
            raise ClaudeAgentFactoryError("Claude SDK not available") from e
        
        logger.debug(f"Creating Claude options for agent: {agent.name}")
        
        # Get MCP configs for the main agent
        main_agent_mcp_configs = self._get_mcp_configs(agent, team)
        
        # Build allowed tools list
        allowed_tools = []
        
        # Add agent's tools
        if agent.tools:
            for tool_id in agent.tools:
                tool = self._find_tool_in_team(tool_id, team)
                if tool:
                    tool_name = self._get_tool_name(tool)
                    allowed_tools.append(tool_name)
                    logger.debug(f"Added tool '{tool_name}' for agent {agent.id}")
        
        # Add MCP tools
        for config in main_agent_mcp_configs:
            if hasattr(config, 'name'):
                # Add all tools from this MCP server (pattern: mcp__server__tool)
                allowed_tools.append(f"mcp__{config.name}__*")
                logger.debug(f"Added MCP server tools pattern: mcp__{config.name}__*")
        
        # Build MCP servers configuration
        mcp_servers = {}
        for config in main_agent_mcp_configs:
            if hasattr(config, 'name'):
                mcp_servers[config.name] = config
        
        # Create system prompt for the agent
        system_prompt = self._build_system_prompt(agent, team)
        
        # Create Claude options
        claude_options = ClaudeAgentOptions(
            system_prompt=system_prompt,
            allowed_tools=allowed_tools,
            mcp_servers=mcp_servers,
            model=agent.model if hasattr(agent, 'model') and agent.model else None,
            max_turns=agent.max_turns if hasattr(agent, 'max_turns') and agent.max_turns else None,
            permission_mode="acceptEdits",  # Default to accepting edits for agent execution
            setting_sources=["project"]  # Load project settings for CLAUDE.md
        )
        
        logger.debug(f"Created Claude options with {len(allowed_tools)} tools and {len(mcp_servers)} MCP servers")
        return claude_options, main_agent_mcp_configs

    def _build_system_prompt(self, agent: Agent, team: Team) -> str:
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
        
        # Add delegation instructions if agent has delegations
        if hasattr(agent, 'delegations') and agent.delegations:
            delegation_info = []
            for delegation in agent.delegations:
                target_agent = delegation.target_agent
                if not target_agent:
                    target_agent = self._find_agent_in_team(delegation.target_agent_id, team)
                if target_agent:
                    delegation_info.append(f"- {target_agent.name}: {delegation.instructions}")
            
            if delegation_info:
                prompt_parts.append(f"\nDelegation Options:\n" + "\n".join(delegation_info))
        
        return "\n".join(prompt_parts)

    def _get_mcp_configs(self, agent: Agent, team: Team) -> List:
        """Get MCP configurations for an agent."""
        mcp_configs = []
        
        if not agent.tools:
            return mcp_configs
        
        for tool_id in agent.tools:
            tool = self._find_tool_in_team(tool_id, team)
            if tool and self._is_mcp_tool(tool):
                try:
                    mcp_config = self._create_mcp_config_from_tool(tool)
                    if mcp_config:
                        mcp_configs.append(mcp_config)
                        logger.debug(f"Created MCP config for tool {tool.id}")
                except Exception as e:
                    logger.warning(f"Failed to create MCP config for tool {tool.id}: {e}")
        
        return mcp_configs

    def _is_mcp_tool(self, tool: DomainTool) -> bool:
        """Check if a tool is an MCP tool."""
        return hasattr(tool, 'url') and tool.url is not None

    def _create_mcp_config_from_tool(self, tool: DomainTool) -> Optional[Dict[str, Any]]:
        """Create MCP configuration from a domain tool."""
        if not self._is_mcp_tool(tool):
            return None
        
        # Create MCP config based on tool properties
        config = {
            'name': tool.id,
            'type': getattr(tool, 'connection_type', 'http').lower()
        }
        
        if hasattr(tool, 'url') and tool.url:
            config['url'] = tool.url
        
        if hasattr(tool, 'headers') and tool.headers:
            config['headers'] = tool.headers
        
        if hasattr(tool, 'command') and tool.command:
            config['command'] = tool.command
            if hasattr(tool, 'args') and tool.args:
                config['args'] = tool.args
        
        return config

    def _get_tool_name(self, tool: DomainTool) -> str:
        """Get the tool name for Claude SDK."""
        if self._is_mcp_tool(tool):
            # MCP tools use pattern: mcp__server__tool
            return f"mcp__{tool.id}__*"
        else:
            # Built-in tools use their class name or module name
            if hasattr(tool, 'class_name') and tool.class_name:
                return tool.class_name
            elif hasattr(tool, 'name') and tool.name:
                return tool.name
            else:
                return tool.id

    def _find_tool_in_team(self, tool_id: str, team: Team) -> Optional[DomainTool]:
        """Find a tool by ID in the team configuration."""
        if not team.tools:
            return None
        
        for tool in team.tools:
            if tool.id == tool_id:
                return tool
        
        return None

    def _find_agent_in_team(self, agent_id: str, team: Team) -> Optional[Agent]:
        """Find an agent by ID in the team configuration."""
        if not team.agents:
            return None
        
        for agent in team.agents:
            if agent.id == agent_id:
                return agent
        
        return None