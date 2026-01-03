"""
Gnosari tasks management tool with streaming support.

Provides comprehensive task management capabilities including creation, updates,
dependency management, and hierarchical task organization through Gnosari API.
"""

import logging
import os
from typing import Any, Optional

import httpx

from ...schemas.domain.execution import AgentRun
from ...schemas.domain.tool import Tool
from ...tools.streaming.interfaces import IStreamableTool, IToolStreamContext
from ...tools.streaming.mixins import StreamableToolMixin, ProgressTracker
from .base import BaseProviderAgnosticTool

logger = logging.getLogger(__name__)


class GnosariTasksTool(StreamableToolMixin, BaseProviderAgnosticTool, IStreamableTool):
    """
    Gnosari tasks management tool with comprehensive streaming support.
    
    Enables creating, updating, and managing tasks in Gnosari platform through
    its REST API. Follows Open/Closed Principle: Extended with streaming without modification.
    """

    def __init__(self, tool_config: Tool, agent_run: AgentRun):
        logger.info(f"🚀 GNOSARI_TASKS_TOOL - Initializing with config: {tool_config.id}")
        print(f"🚀 GNOSARI_TASKS_TOOL - Initializing with config: {tool_config.id}")
        
        # Initialize BaseProviderAgnosticTool first
        BaseProviderAgnosticTool.__init__(self, tool_config)
        # Initialize streaming components
        StreamableToolMixin.__init__(self)
        self.agent_run = agent_run
        self._stream_context: IToolStreamContext | None = None
        
        # Get API configuration from tool args or environment
        self.api_key = self._get_config_value("api_key", "GNOSARI_API_KEY")
        self.api_url = self._get_config_value("api_url", "GNOSARI_API_URL", "https://api.gnosari.com")
        self.timeout = int(self._get_config_value("timeout", "GNOSARI_API_TIMEOUT", "30"))

        logger.info(f"🔧 GNOSARI_TASKS_TOOL - Config: api_url={self.api_url}, has_api_key={bool(self.api_key)}")
        print(f"🔧 GNOSARI_TASKS_TOOL - Config: api_url={self.api_url}, has_api_key={bool(self.api_key)}")
        
        if not self.api_key:
            error_msg = "Gnosari API key is required. Set it in tool args or GNOSARI_API_KEY environment variable"
            logger.error(f"❌ GNOSARI_TASKS_TOOL - {error_msg}")
            print(f"❌ GNOSARI_TASKS_TOOL - {error_msg}")
            raise ValueError(error_msg)
        
        logger.info(f"✅ GNOSARI_TASKS_TOOL - Successfully initialized")
        print(f"✅ GNOSARI_TASKS_TOOL - Successfully initialized")

    def _get_config_value(self, arg_key: str, env_key: str, default: str = None) -> str:
        """Get configuration value from tool args or environment with fallback."""
        # First try tool args
        if self.args and arg_key in self.args:
            return self.args[arg_key]
        
        # Then try environment
        env_value = os.getenv(env_key)
        if env_value:
            return env_value
            
        # Finally use default
        if default is not None:
            return default
            
        return None

    async def execute_core_logic(
        self,
        action: str,
        task_id: Optional[int] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        input_message: Optional[str] = None,
        task_type: str = "task",
        status: str = "pending",
        tags: Optional[list[str]] = None,
        assigned_team_identifier: Optional[str] = None,
        assigned_agent_identifier: Optional[str] = None,
        reporter_team_identifier: Optional[str] = None,
        reporter_agent_identifier: Optional[str] = None,
        parent_id: Optional[int] = None,
        dependency_ids: Optional[list[int]] = None,
        skip: int = 0,
        limit: int = 100,
        **kwargs
    ) -> str:
        """
        Execute Gnosari task management operations with streaming support.
        
        Args:
            action: Operation to perform (create, get, list, update, delete, add_dependency, remove_dependency)
            task_id: ID of task for get/update/delete operations
            title: Task title (required for create)
            description: Task description
            input_message: Input message or requirements
            task_type: Task type (bug, feature, task, improvement, research)
            status: Task status (pending, in_progress, review, completed, cancelled)
            tags: Tags for categorization
            assigned_team_identifier: Team identifier assignment (required for create)
            assigned_agent_identifier: Agent identifier assignment
            reporter_team_identifier: Reporter team identifier
            reporter_agent_identifier: Reporter agent identifier
            parent_id: Parent task ID for subtasks
            dependency_ids: List of dependency task IDs
            skip: Number of records to skip for list operations
            limit: Maximum records to return for list operations
            **kwargs: Additional parameters
            
        Returns:
            Formatted operation result or error message
        """
        logger.info(f"🎯 GNOSARI_TASKS_TOOL - Executing action: {action}")
        print(f"🎯 GNOSARI_TASKS_TOOL - Executing action: {action} with args: title={title}, task_id={task_id}")
        logger.info(f"Executing Gnosari tasks action: {action}")
        
        # Emit start event if streaming is available
        await self._emit_start({
            "action": action,
            "task_id": task_id,
            "operation": f"gnosari_task_{action}"
        })
        
        # Create progress tracker based on action complexity
        total_steps = self._get_action_steps(action)
        progress = ProgressTracker(self, total_steps=total_steps, operation_name=f"gnosari_task_{action}")
        
        try:
            # Step 1: Validate action and parameters
            await progress.step("validating_parameters", {"action": action, "task_id": task_id})
            self._validate_action_parameters(action, task_id, title, assigned_team_identifier)

            print(f"Gnosari task action: {action}. ApiKey: {self.api_key}. Api URL: {self.api_url}")
            # Step 2: Prepare HTTP client
            await progress.step("preparing_client", {"api_url": self.api_url})
            headers = {
                "X-AUTH-TOKEN": self.api_key,
                "Content-Type": "application/json"
            }
            
            # Step 3: Execute specific action
            await progress.step("executing_action", {"action": action})
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if action == "create":
                    result = await self._create_task(
                        client, headers, title, description, input_message,
                        task_type, status, tags, assigned_team_identifier, assigned_agent_identifier,
                        reporter_team_identifier, reporter_agent_identifier, parent_id, dependency_ids
                    )
                elif action == "get":
                    result = await self._get_task(client, headers, task_id)
                elif action == "list":
                    result = await self._list_tasks(
                        client, headers, skip, limit, status, assigned_team_identifier,
                        assigned_agent_identifier, parent_id, task_type
                    )
                elif action == "update":
                    result = await self._update_task(
                        client, headers, task_id, title, description, status,
                        assigned_agent_identifier, tags, dependency_ids
                    )
                elif action == "delete":
                    result = await self._delete_task(client, headers, task_id)
                elif action == "add_dependency":
                    dependency_id = kwargs.get("dependency_id")
                    if not dependency_id:
                        raise ValueError("dependency_id is required for add_dependency action")
                    result = await self._add_dependency(client, headers, task_id, dependency_id)
                elif action == "remove_dependency":
                    dependency_id = kwargs.get("dependency_id")
                    if not dependency_id:
                        raise ValueError("dependency_id is required for remove_dependency action")
                    result = await self._remove_dependency(client, headers, task_id, dependency_id)
                else:
                    raise ValueError(f"Unsupported action: {action}")
            
            # Step 4: Format and emit results
            await progress.step("formatting_results", {"action": action, "success": True})
            formatted_result = self._format_task_result(result, action)
            
            # Emit intermediate result
            await self._emit_result({
                "action": action,
                "task_id": task_id,
                "success": True,
                "result_type": type(result).__name__
            })
            
            # Complete progress tracking
            await progress.complete({
                "action": action,
                "task_id": task_id,
                "success": True,
                "result_size": len(formatted_result)
            })
            
            return formatted_result
            
        except Exception as e:
            error_details = f"Error executing task {action}: {str(e)}"
            
            # If it's an HTTP error, include response details
            if hasattr(e, 'response'):
                try:
                    status_code = e.response.status_code
                    response_text = e.response.text
                    response_headers = dict(e.response.headers) if hasattr(e.response, 'headers') else {}
                    
                    error_details = (
                        f"Error executing task {action}: HTTP {status_code}\n"
                        f"Response: {response_text}\n"
                        f"Headers: {response_headers}"
                    )
                    logger.error(f"API Error Details - Status: {status_code}, Response: {response_text}")
                    print(f"❌ API Error Details - Status: {status_code}, Response: {response_text}")
                except Exception:
                    # Fallback if we can't extract response details
                    pass
            
            logger.error(f"Error executing Gnosari task action {action}: {e}", exc_info=True)
            await self._emit_error(e)
            return error_details

    def _get_action_steps(self, action: str) -> int:
        """Get number of steps for progress tracking based on action complexity."""
        step_mapping = {
            "create": 4,
            "get": 4,
            "list": 4,
            "update": 4,
            "delete": 4,
            "add_dependency": 4,
            "remove_dependency": 4
        }
        return step_mapping.get(action, 4)

    def _validate_action_parameters(self, action: str, task_id: Optional[int], title: Optional[str], assigned_team_identifier: Optional[str]) -> None:
        """Validate required parameters for each action."""
        if action in ["get", "update", "delete", "add_dependency", "remove_dependency"] and not task_id:
            raise ValueError(f"task_id is required for {action} action")
        
        if action == "create":
            if not title:
                raise ValueError("title is required for create action")
            if not assigned_team_identifier:
                raise ValueError("assigned_team_identifier is required for create action")

    async def _create_task(
        self,
        client: httpx.AsyncClient,
        headers: dict,
        title: str,
        description: Optional[str],
        input_message: Optional[str],
        task_type: str,
        status: str,
        tags: Optional[list[str]],
        assigned_team_identifier: str,
        assigned_agent_identifier: Optional[str],
        reporter_team_identifier: Optional[str],
        reporter_agent_identifier: Optional[str],
        parent_id: Optional[int],
        dependency_ids: Optional[list[int]]
    ) -> dict:
        """Create a new task."""
        payload = {
            "title": title,
            "type": task_type,
            "status": status,
            "assigned_team_identifier": assigned_team_identifier
        }
        
        # Add optional fields
        if description:
            payload["description"] = description
        if input_message:
            payload["input_message"] = input_message
        if tags:
            payload["tags"] = tags
        if assigned_agent_identifier:
            payload["assigned_agent_identifier"] = assigned_agent_identifier
        if reporter_team_identifier:
            payload["reporter_team_identifier"] = reporter_team_identifier
        if reporter_agent_identifier:
            payload["reporter_agent_identifier"] = reporter_agent_identifier
        if parent_id:
            payload["parent_id"] = parent_id
        if dependency_ids:
            payload["dependency_ids"] = dependency_ids
        
        # Add reporter information from AgentRun if available (if not already set)
        if self.agent_run and self.agent_run.team and not reporter_team_identifier:
            team_identifier = getattr(self.agent_run.team, 'identifier', None)
            if team_identifier:
                payload["reporter_team_identifier"] = team_identifier
        
        if self.agent_run and not reporter_agent_identifier:
            agent_identifier = getattr(self.agent_run, 'agent_identifier', None)
            if agent_identifier:
                payload["reporter_agent_identifier"] = agent_identifier
        
        endpoint = f"{self.api_url}/api/v1/tasks"
        logger.debug(f"CREATE_TASK - Endpoint: {endpoint}")
        logger.debug(f"CREATE_TASK - Headers: {headers}")
        logger.debug(f"CREATE_TASK - Payload: {payload}")
        
        response = await client.post(
            endpoint,
            headers=headers,
            json=payload
        )
        
        logger.debug(f"CREATE_TASK - Response Status: {response.status_code}")
        logger.debug(f"CREATE_TASK - Response Headers: {dict(response.headers)}")
        
        response.raise_for_status()
        response_data = response.json()
        logger.debug(f"CREATE_TASK - Response Data: {response_data}")
        return response_data

    async def _get_task(self, client: httpx.AsyncClient, headers: dict, task_id: int) -> dict:
        """Get a specific task by ID."""
        endpoint = f"{self.api_url}/api/v1/tasks/{task_id}"
        logger.debug(f"GET_TASK - Endpoint: {endpoint}")
        logger.debug(f"GET_TASK - Headers: {headers}")
        
        response = await client.get(
            endpoint,
            headers=headers
        )
        
        logger.debug(f"GET_TASK - Response Status: {response.status_code}")
        logger.debug(f"GET_TASK - Response Headers: {dict(response.headers)}")
        
        response.raise_for_status()
        response_data = response.json()
        logger.debug(f"GET_TASK - Response Data: {response_data}")
        return response_data

    async def _list_tasks(
        self,
        client: httpx.AsyncClient,
        headers: dict,
        skip: int,
        limit: int,
        status: Optional[str],
        assigned_team_identifier: Optional[str],
        assigned_agent_identifier: Optional[str],
        parent_id: Optional[int],
        task_type: Optional[str]
    ) -> list[dict]:
        """List tasks with optional filtering."""
        params = {"skip": skip, "limit": limit}
        
        # Add filters
        if status:
            params["status"] = status
        if assigned_team_identifier:
            params["team_identifier"] = assigned_team_identifier
        if assigned_agent_identifier:
            params["agent_identifier"] = assigned_agent_identifier
        if parent_id:
            params["parent_id"] = parent_id
        if task_type:
            params["task_type"] = task_type
        
        endpoint = f"{self.api_url}/api/v1/tasks"
        logger.debug(f"LIST_TASKS - Endpoint: {endpoint}")
        logger.debug(f"LIST_TASKS - Headers: {headers}")
        logger.debug(f"LIST_TASKS - Params: {params}")
        
        response = await client.get(
            endpoint,
            headers=headers,
            params=params
        )
        
        logger.debug(f"LIST_TASKS - Response Status: {response.status_code}")
        logger.debug(f"LIST_TASKS - Response Headers: {dict(response.headers)}")
        
        response.raise_for_status()
        response_data = response.json()
        logger.debug(f"LIST_TASKS - Response Data: {response_data}")
        return response_data

    async def _update_task(
        self,
        client: httpx.AsyncClient,
        headers: dict,
        task_id: int,
        title: Optional[str],
        description: Optional[str],
        status: Optional[str],
        assigned_agent_identifier: Optional[str],
        tags: Optional[list[str]],
        dependency_ids: Optional[list[int]]
    ) -> dict:
        """Update an existing task."""
        payload = {}
        
        # Add fields to update
        if title:
            payload["title"] = title
        if description:
            payload["description"] = description
        if status:
            payload["status"] = status
        if assigned_agent_identifier is not None:  # Allow setting to None
            payload["assigned_agent_identifier"] = assigned_agent_identifier
        if tags:
            payload["tags"] = tags
        if dependency_ids:
            payload["dependency_ids"] = dependency_ids
        
        endpoint = f"{self.api_url}/api/v1/tasks/{task_id}"
        logger.debug(f"UPDATE_TASK - Endpoint: {endpoint}")
        logger.debug(f"UPDATE_TASK - Headers: {headers}")
        logger.debug(f"UPDATE_TASK - Payload: {payload}")
        
        response = await client.put(
            endpoint,
            headers=headers,
            json=payload
        )
        
        logger.debug(f"UPDATE_TASK - Response Status: {response.status_code}")
        logger.debug(f"UPDATE_TASK - Response Headers: {dict(response.headers)}")
        
        response.raise_for_status()
        response_data = response.json()
        logger.debug(f"UPDATE_TASK - Response Data: {response_data}")
        return response_data

    async def _delete_task(self, client: httpx.AsyncClient, headers: dict, task_id: int) -> dict:
        """Delete a task."""
        endpoint = f"{self.api_url}/api/v1/tasks/{task_id}"
        logger.debug(f"DELETE_TASK - Endpoint: {endpoint}")
        logger.debug(f"DELETE_TASK - Headers: {headers}")
        
        response = await client.delete(
            endpoint,
            headers=headers
        )
        
        logger.debug(f"DELETE_TASK - Response Status: {response.status_code}")
        logger.debug(f"DELETE_TASK - Response Headers: {dict(response.headers)}")
        
        response.raise_for_status()
        response_data = response.json()
        logger.debug(f"DELETE_TASK - Response Data: {response_data}")
        return response_data

    async def _add_dependency(self, client: httpx.AsyncClient, headers: dict, task_id: int, dependency_id: int) -> dict:
        """Add a dependency to a task."""
        endpoint = f"{self.api_url}/api/v1/tasks/{task_id}/dependencies/{dependency_id}"
        logger.debug(f"ADD_DEPENDENCY - Endpoint: {endpoint}")
        logger.debug(f"ADD_DEPENDENCY - Headers: {headers}")
        
        response = await client.post(
            endpoint,
            headers=headers
        )
        
        logger.debug(f"ADD_DEPENDENCY - Response Status: {response.status_code}")
        logger.debug(f"ADD_DEPENDENCY - Response Headers: {dict(response.headers)}")
        
        response.raise_for_status()
        response_data = response.json()
        logger.debug(f"ADD_DEPENDENCY - Response Data: {response_data}")
        return response_data

    async def _remove_dependency(self, client: httpx.AsyncClient, headers: dict, task_id: int, dependency_id: int) -> dict:
        """Remove a dependency from a task."""
        endpoint = f"{self.api_url}/api/v1/tasks/{task_id}/dependencies/{dependency_id}"
        logger.debug(f"REMOVE_DEPENDENCY - Endpoint: {endpoint}")
        logger.debug(f"REMOVE_DEPENDENCY - Headers: {headers}")
        
        response = await client.delete(
            endpoint,
            headers=headers
        )
        
        logger.debug(f"REMOVE_DEPENDENCY - Response Status: {response.status_code}")
        logger.debug(f"REMOVE_DEPENDENCY - Response Headers: {dict(response.headers)}")
        
        response.raise_for_status()
        response_data = response.json()
        logger.debug(f"REMOVE_DEPENDENCY - Response Data: {response_data}")
        return response_data

    def _format_task_result(self, result: Any, action: str) -> str:
        """Format task operation results for LLM consumption."""
        if action == "delete" or action in ["add_dependency", "remove_dependency"]:
            return f"Operation completed successfully: {result.get('message', 'Success')}"
        
        if action == "list":
            if not result:
                return "No tasks found matching the criteria."
            
            formatted_tasks = []
            for task in result:
                task_info = self._format_single_task(task)
                formatted_tasks.append(task_info)
            
            return f"Found {len(result)} tasks:\n\n" + "\n\n".join(formatted_tasks)
        
        # Single task (create, get, update)
        if isinstance(result, dict):
            return self._format_single_task(result)
        
        return str(result)

    def _format_single_task(self, task: dict) -> str:
        """Format a single task for display."""
        formatted = f"Task #{task.get('id')}: {task.get('title', 'Untitled')}\n"
        formatted += f"Status: {task.get('status', 'unknown')}\n"
        formatted += f"Type: {task.get('type', 'task')}\n"
        
        if task.get('description'):
            formatted += f"Description: {task['description']}\n"
        
        if task.get('tags'):
            formatted += f"Tags: {', '.join(task['tags'])}\n"
        
        # Team and agent assignments
        if task.get('assigned_team'):
            formatted += f"Assigned Team: {task['assigned_team'].get('name', 'Unknown')}\n"
        
        if task.get('assigned_agent'):
            formatted += f"Assigned Agent: {task['assigned_agent'].get('name', 'Unknown')}\n"
        
        # Parent and dependencies
        if task.get('parent'):
            formatted += f"Parent Task: #{task['parent']['id']} - {task['parent'].get('title', 'Untitled')}\n"
        
        if task.get('dependencies'):
            deps = [f"#{dep['id']} ({dep.get('status', 'unknown')})" for dep in task['dependencies']]
            formatted += f"Dependencies: {', '.join(deps)}\n"
        
        if task.get('subtasks'):
            formatted += f"Subtasks: {len(task['subtasks'])} subtask(s)\n"
        
        formatted += f"Created: {task.get('created_at', 'Unknown')}\n"
        formatted += f"Updated: {task.get('updated_at', 'Unknown')}"
        
        return formatted

    def get_input_schema(self) -> dict[str, Any]:
        """Get input schema for Gnosari tasks tool."""
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "Action to perform",
                    "enum": ["create", "get", "list", "update", "delete", "add_dependency", "remove_dependency"]
                },
                "task_id": {
                    "type": "integer",
                    "description": "Task ID (required for get, update, delete, dependency operations)"
                },
                "title": {
                    "type": "string",
                    "description": "Task title (required for create)"
                },
                "description": {
                    "type": "string",
                    "description": "Task description"
                },
                "input_message": {
                    "type": "string",
                    "description": "Input message or requirements"
                },
                "task_type": {
                    "type": "string",
                    "description": "Task type",
                    "enum": ["bug", "feature", "task", "improvement", "research"],
                    "default": "task"
                },
                "status": {
                    "type": "string",
                    "description": "Task status",
                    "enum": ["pending", "in_progress", "review", "completed", "cancelled"],
                    "default": "pending"
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Tags for categorization"
                },
                "assigned_team_identifier": {
                    "type": "string",
                    "description": "Team identifier assignment (required for create)"
                },
                "assigned_agent_identifier": {
                    "type": "string",
                    "description": "Agent identifier assignment"
                },
                "reporter_team_identifier": {
                    "type": "string",
                    "description": "Reporter team identifier"
                },
                "reporter_agent_identifier": {
                    "type": "string",
                    "description": "Reporter agent identifier"
                },
                "parent_id": {
                    "type": "integer",
                    "description": "Parent task ID for subtasks"
                },
                "dependency_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "List of dependency task IDs"
                },
                "dependency_id": {
                    "type": "integer",
                    "description": "Single dependency ID for add/remove dependency operations"
                },
                "skip": {
                    "type": "integer",
                    "description": "Number of records to skip for list operations",
                    "default": 0
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum records to return for list operations",
                    "default": 100
                }
            },
            "required": ["action"]
        }

    def get_output_schema(self) -> dict[str, Any]:
        """Get output schema for Gnosari tasks tool."""
        return {
            "type": "string",
            "description": "Formatted task operation result or error message"
        }
    
    # IStreamableTool interface methods
    def supports_streaming(self) -> bool:
        """Gnosari tasks tool supports streaming."""
        return True
    
    def set_stream_context(self, context: IToolStreamContext) -> None:
        """Set streaming context for this tool."""
        self._stream_context = context
        # Also set in the mixin
        super().set_stream_context(context)
    
    def _get_tool_name(self) -> str:
        """Get tool name for streaming events."""
        return self.name or "gnosari_tasks"