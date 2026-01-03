"""
OpenAI-specific knowledge query tool provider.

Integrates the provider-agnostic knowledge tool with OpenAI's agent framework.
"""

import json
import logging
from typing import Any

from agents import RunContextWrapper

from ...builtin.knowledge_query import KnowledgeQueryTool
from ....schemas.domain.tool import Tool
from ....schemas.session import SessionContext
from .base import OpenAIToolProvider

logger = logging.getLogger(__name__)


class KnowledgeQueryToolProvider(OpenAIToolProvider):
    """
    OpenAI-specific knowledge tool provider.
    
    Wraps the provider-agnostic KnowledgeQueryTool for OpenAI integration.
    Provides access to OpenAI-specific context including SessionContext.
    """

    def __init__(self, tool_config: Tool):
        # Create base tool
        base_tool = KnowledgeQueryTool(tool_config)
        super().__init__(base_tool)

    async def _execute_openai_tool(self, ctx: RunContextWrapper[Any], args: str) -> str:
        """
        OpenAI-specific knowledge query execution with RunContextWrapper.
        
        Args:
            ctx: OpenAI RunContextWrapper containing SessionContext
            args: JSON string with query parameters
            
        Returns:
            Knowledge query results formatted for OpenAI agent
        """
        logger.info(f"KnowledgeQueryToolProvider._execute_openai_tool called with args: {args}")
        logger.debug(f"Context type: {type(ctx)}, Context: {ctx}")
        logger.debug(f"Context.context type: {type(ctx.context) if hasattr(ctx, 'context') else 'No context attr'}")
        
        try:
            # Parse OpenAI arguments
            parsed_args = json.loads(args)
            logger.debug(f"Parsed args: {parsed_args}")

            session_context = ctx.context
            logger.debug(f"Session context: {session_context}")
            logger.debug(f"Session context type: {type(session_context)}")
            
            # Execute core knowledge logic with OpenAI context awareness
            result = await self._execute_with_context(
                session_context=session_context,
                **parsed_args
            )
            
            return str(result)
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing tool arguments: {e}")
            return f"Error parsing tool arguments: {e}"
        except Exception as e:
            logger.error(f"Error executing knowledge query: {e}", exc_info=True)
            return f"Error executing knowledge query: {e}"

    async def _execute_with_context(
        self, 
        session_context: SessionContext | None = None,
        **kwargs
    ) -> str:
        """
        Execute knowledge query with OpenAI context awareness.
        
        Args:
            session_context: OpenAI session context with team/agent info
            **kwargs: Query parameters (query, knowledge_name)
            
        Returns:
            Formatted knowledge query results
        """

        return await self.base_tool.execute_core_logic(session_context=session_context, **kwargs)

