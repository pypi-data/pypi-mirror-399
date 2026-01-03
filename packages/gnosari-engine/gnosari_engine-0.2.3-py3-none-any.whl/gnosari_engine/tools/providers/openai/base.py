"""
Base OpenAI tool provider implementation.

Provides common functionality for OpenAI agent integration following
the Single Responsibility Principle.
"""

import json
from typing import Any

from agents import RunContextWrapper

from ...builtin.base import BaseProviderAgnosticTool
from ...interfaces import IToolProvider
from ....schemas.domain.tool import Tool


class OpenAIToolProvider(IToolProvider):
    """
    OpenAI-specific tool provider base class.
    
    Follows Single Responsibility Principle by focusing only on OpenAI integration.
    Delegates core logic to provider-agnostic tool implementation.
    """

    def __init__(self, base_tool: BaseProviderAgnosticTool, agent_run=None, **config):
        self.base_tool = base_tool
        self.agent_run = agent_run  # Store AgentRun context for tool execution
        self._openai_tool = None
        self._is_initialized = False

    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "openai"

    @property
    def tool_name(self) -> str:
        """Get tool name from base tool."""
        return self.base_tool.name

    @property
    def is_initialized(self) -> bool:
        """Check if tool is initialized."""
        return self._is_initialized

    async def initialize(self, **config) -> None:
        """Initialize OpenAI-specific tool implementation."""
        try:
            from agents import FunctionTool
            
            # Initialize base tool first
            await self.base_tool.initialize(**config)
            
            # Create OpenAI FunctionTool
            self._openai_tool = FunctionTool(
                name=self.base_tool.name,
                description=self.base_tool.description or f"Execute {self.base_tool.name}",
                params_json_schema=self.base_tool.get_input_schema(),
                on_invoke_tool=self._execute_openai_tool
            )
            self._is_initialized = True
            
        except ImportError as e:
            raise RuntimeError(f"OpenAI agents SDK not available: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize OpenAI tool {self.base_tool.name}: {e}")

    async def cleanup(self) -> None:
        """Cleanup tool resources."""
        if self.base_tool:
            await self.base_tool.cleanup()
        self._openai_tool = None
        self._is_initialized = False

    def get_tool_implementation(self) -> Any:
        """Return OpenAI FunctionTool instance."""
        if not self._is_initialized:
            raise RuntimeError(f"Tool {self.base_tool.name} not initialized")
        return self._openai_tool

    async def _execute_openai_tool(self, ctx: RunContextWrapper[Any], args: str) -> str:
        """
        Execute tool within OpenAI context.
        
        Args:
            ctx: OpenAI RunContextWrapper containing SessionContext
            args: JSON string containing tool arguments
            
        Returns:
            String result for OpenAI agent
        """
        try:
            # Parse OpenAI arguments
            parsed_args = json.loads(args)

            session_context = ctx.context
            
            # Execute core logic through base tool with session context
            result = await self.base_tool.execute_core_logic(agent_run=session_context, **parsed_args)
            
            # Convert result to string for OpenAI
            return str(result)
            
        except json.JSONDecodeError as e:
            return f"Error parsing tool arguments: {e}"
        except Exception as e:
            return f"Error executing tool {self.base_tool.name}: {e}"