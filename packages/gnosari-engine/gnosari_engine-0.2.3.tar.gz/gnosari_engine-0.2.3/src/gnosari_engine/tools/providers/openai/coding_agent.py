"""
OpenAI-specific coding agent tool provider.

Integrates the provider-agnostic coding agent tool with OpenAI's agent framework.
"""

import json
import logging
from typing import Any

from agents import RunContextWrapper

from ...builtin.coding_agent import CodingAgentTool
from ....schemas.domain.tool import Tool
from ....schemas.session import SessionContext
from .base import OpenAIToolProvider

logger = logging.getLogger(__name__)


class CodingAgentToolProvider(OpenAIToolProvider):
    """
    OpenAI-specific coding agent tool provider.
    
    Wraps the provider-agnostic CodingAgentTool for OpenAI integration.
    Provides access to OpenAI-specific context including SessionContext.
    """

    def __init__(self, tool_config: Tool, agent_run=None):
        # Create base tool with agent_run context
        base_tool = CodingAgentTool(tool_config, agent_run)
        super().__init__(base_tool, agent_run)

    async def _execute_openai_tool(self, ctx: RunContextWrapper[Any], args: str) -> str:
        """
        OpenAI-specific coding agent execution with RunContextWrapper.
        
        Args:
            ctx: OpenAI RunContextWrapper containing SessionContext
            args: JSON string with coding agent parameters
            
        Returns:
            Coding agent results formatted for OpenAI agent
        """
        logger.info(f"CodingAgentToolProvider._execute_openai_tool called with args: {args}")
        logger.debug(f"Context type: {type(ctx)}, Context: {ctx}")
        logger.debug(f"Context.context type: {type(ctx.context) if hasattr(ctx, 'context') else 'No context attr'}")
        
        try:
            # Parse OpenAI arguments
            parsed_args = json.loads(args)
            logger.info(f"🔧 [DEBUG] OpenAI CodingAgent execution:")
            logger.info(f"  - raw args: {args}")
            logger.info(f"  - parsed_args: {parsed_args}")

            session_context = ctx.context
            logger.info(f"  - session_context: {session_context}")
            logger.info(f"  - session_context type: {type(session_context)}")
            
            # Execute core coding agent logic with OpenAI context awareness
            logger.info(f"🎯 [DEBUG] Calling _execute_with_context with kwargs: {parsed_args}")
            result = await self._execute_with_context(
                session_context=session_context,
                **parsed_args
            )
            
            return str(result)
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing tool arguments: {e}")
            return f"Error parsing tool arguments: {e}"
        except Exception as e:
            logger.error(f"Error executing coding agent: {e}", exc_info=True)
            return f"Error executing coding agent: {e}"

    async def _execute_with_context(
        self, 
        session_context: SessionContext | None = None,
        **kwargs
    ) -> str:
        """
        Execute coding agent with OpenAI context awareness.
        
        Args:
            session_context: OpenAI session context with team/agent info
            **kwargs: Coding agent parameters (message, working_directory)
            
        Returns:
            Formatted coding agent results
        """
        logger.info(f"🔍 [DEBUG] _execute_with_context called:")
        logger.info(f"  - session_context: {session_context}")
        logger.info(f"  - kwargs: {kwargs}")
        
        # Extract working directory from session context if not provided
        if "working_directory" not in kwargs and session_context:
            # Try to get working directory from session context or team configuration
            # This allows teams to configure default working directories
            team = getattr(session_context, 'team', None) if session_context else None
            logger.info(f"  - team from session_context: {team}")
            if team and hasattr(team, 'config'):
                team_config = getattr(team, 'config', {})
                logger.info(f"  - team_config: {team_config}")
                if isinstance(team_config, dict):
                    working_dir = team_config.get("working_directory")
                    logger.info(f"  - working_directory from team_config: {working_dir}")
                    kwargs.setdefault("working_directory", working_dir)
        
        logger.info(f"🎯 [DEBUG] Final kwargs before calling base_tool.execute_core_logic: {kwargs}")
        return await self.base_tool.execute_core_logic(**kwargs)