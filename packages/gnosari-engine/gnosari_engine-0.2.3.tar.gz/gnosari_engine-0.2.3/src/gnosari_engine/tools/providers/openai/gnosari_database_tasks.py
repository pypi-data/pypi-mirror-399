"""
OpenAI-specific Gnosari database tasks tool provider.

Integrates the provider-agnostic Gnosari database tasks tool with OpenAI's agent framework,
providing seamless task management capabilities within OpenAI agent workflows.
"""

import json
import logging
from typing import Any, Optional

from agents import RunContextWrapper

from ...builtin.gnosari_database_tasks import GnosariDatabaseTasksTool
from ....schemas import AgentRun
from ....schemas.domain.tool import Tool
from ....schemas.session import SessionContext
from .base import OpenAIToolProvider

logger = logging.getLogger(__name__)


class GnosariDatabaseTasksToolProvider(OpenAIToolProvider):
    """
    OpenAI-specific Gnosari database tasks tool provider.

    Wraps the provider-agnostic GnosariDatabaseTasksTool for OpenAI integration.
    Provides access to OpenAI-specific context including SessionContext
    and agent execution information for task management operations.

    Follows Single Responsibility Principle: Only handles OpenAI integration.
    Delegates all task logic to the core GnosariDatabaseTasksTool implementation.
    """

    def __init__(self, tool_config: Tool, agent_run=None):
        """
        Initialize OpenAI Gnosari database tasks tool provider.

        Args:
            tool_config: Tool configuration from team YAML
            agent_run: Optional AgentRun context for task operations
        """
        logger.info(f"🚀 GNOSARI_DATABASE_TASKS_PROVIDER - Initializing OpenAI provider for: {tool_config.id}")
        print(f"🚀 GNOSARI_DATABASE_TASKS_PROVIDER - Initializing OpenAI provider for: {tool_config.id}")

        # Create base tool with AgentRun context
        base_tool = GnosariDatabaseTasksTool(tool_config, agent_run)
        super().__init__(base_tool, agent_run)

        logger.info(f"✅ GNOSARI_DATABASE_TASKS_PROVIDER - Successfully initialized")
        print(f"✅ GNOSARI_DATABASE_TASKS_PROVIDER - Successfully initialized")

    async def _execute_openai_tool(self, ctx: RunContextWrapper[Any], args: str) -> str:
        """
        OpenAI-specific Gnosari database tasks execution with RunContextWrapper.

        Args:
            ctx: OpenAI RunContextWrapper containing SessionContext
            args: JSON string with task operation parameters

        Returns:
            Task operation results formatted for OpenAI agent consumption
        """
        logger.info(f"🎯 GNOSARI_DATABASE_TASKS_PROVIDER - _execute_openai_tool called with args: {args}")
        print(f"🎯 GNOSARI_DATABASE_TASKS_PROVIDER - _execute_openai_tool called with args: {args}")
        logger.info(f"GnosariDatabaseTasksToolProvider._execute_openai_tool called with args: {args}")
        logger.debug(f"Context type: {type(ctx)}, Context: {ctx}")
        logger.debug(f"Context.context type: {type(ctx.context) if hasattr(ctx, 'context') else 'No context attr'}")

        try:
            # Parse OpenAI arguments
            parsed_args = json.loads(args)
            logger.debug(f"Parsed args: {parsed_args}")

            session_context = ctx.context
            logger.debug(f"Session context: {session_context}")
            logger.debug(f"Session context type: {type(session_context)}")

            # Execute core task management logic with OpenAI context awareness
            result = await self._execute_with_context(
                session_context=session_context,
                **parsed_args
            )

            return str(result)

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing tool arguments: {e}")
            return f"Error parsing tool arguments: {e}"
        except Exception as e:
            logger.error(f"Error executing Gnosari database tasks operation: {e}", exc_info=True)
            return f"Error executing Gnosari database tasks operation: {e}"

    async def _execute_with_context(
        self,
        session_context: Optional[AgentRun] = None,
        **kwargs
    ) -> str:
        """
        Execute Gnosari database task operation with OpenAI context awareness.

        Args:
            session_context: OpenAI session context with team/agent info
            **kwargs: Task operation parameters (action, task_id, title, etc.)

        Returns:
            Formatted task operation results
        """

        logger.debug(f"Executing Gnosari database task operation with context: {session_context}")
        logger.debug(f"Operation parameters: {kwargs}")

        # Extract agent run information from the tool for context
        if self.agent_run:
            logger.debug(f"Using AgentRun context: team={getattr(self.agent_run.team, 'id', None) if self.agent_run.team else None}")

        # Enrich operation parameters with context if available
        if session_context and hasattr(session_context, 'team_context'):
            # Add team context information if available
            if not kwargs.get('assigned_team_identifier') and hasattr(session_context.team_context, 'team_identifier'):
                kwargs['assigned_team_identifier'] = session_context.team_context.team_identifier

        # Execute the core task management logic
        return await self.base_tool.execute_core_logic(**kwargs)

    def get_enhanced_input_schema(self) -> dict[str, Any]:
        """
        Get enhanced input schema with OpenAI-specific context information.

        Returns:
            Enhanced JSON schema with additional context fields
        """
        base_schema = self.base_tool.get_input_schema()

        # Add OpenAI-specific enhancements to the schema
        base_schema["description"] = (
            "Comprehensive Gnosari database task management operations with direct database access. "
            "Supports creating, updating, listing, and managing task dependencies. "
            "Supports task tree creation with parent and subtasks in a single operation. "
            "Automatically integrates with current team and agent context."
        )

        # Add examples for common operations
        base_schema["examples"] = [
            {
                "action": "create",
                "title": "Implement user authentication",
                "description": "Add OAuth2 authentication to the platform",
                "type": "feature",
                "tags": ["authentication", "security"],
                "assigned_team_identifier": "backend_team"
            },
            {
                "action": "create",
                "title": "Refactor API layer",
                "description": "Improve API structure and error handling",
                "type": "improvement",
                "assigned_team_identifier": "backend_team",
                "subtasks": [
                    {
                        "title": "Refactor authentication endpoints",
                        "type": "task",
                        "assigned_team_identifier": "backend_team"
                    },
                    {
                        "title": "Improve error responses",
                        "type": "task",
                        "assigned_team_identifier": "backend_team"
                    }
                ]
            },
            {
                "action": "list",
                "status": "pending",
                "limit": 20
            },
            {
                "action": "update",
                "task_id": 123,
                "status": "in_progress",
                "assigned_agent_identifier": "code_reviewer"
            }
        ]

        return base_schema

    async def initialize(self, **config) -> None:
        """
        Initialize OpenAI-specific tool with enhanced configuration.

        Args:
            **config: Additional configuration parameters
        """
        logger.info(f"Initializing GnosariDatabaseTasksToolProvider with config: {config}")

        # Initialize the base tool first
        await super().initialize(**config)

        # Log successful initialization with context information
        if self.agent_run and self.agent_run.team:
            logger.info(f"GnosariDatabaseTasksToolProvider initialized for team: {self.agent_run.team.id}")
        else:
            logger.info("GnosariDatabaseTasksToolProvider initialized without specific team context")

    def get_tool_description(self) -> str:
        """
        Get enhanced tool description for OpenAI agent integration.

        Returns:
            Comprehensive tool description for OpenAI agents
        """
        return (
            "Gnosari Database Tasks Management Tool - Comprehensive task management capabilities "
            "with direct database access. Supports task creation (individual and tree structures), "
            "updates, status tracking, dependency management, and hierarchical task organization. "
            "Integrates with your current team and agent context for seamless workflow management. "
            "Ideal for creating complex task hierarchies with parent and subtasks in a single operation."
        )
