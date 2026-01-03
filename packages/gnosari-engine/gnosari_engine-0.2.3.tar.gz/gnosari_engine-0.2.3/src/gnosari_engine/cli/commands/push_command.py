"""
Push Command - Handles team configuration pushing to Gnosari API
"""

import os
import sys
from pathlib import Path
from typing import Optional, Any
import json
import aiohttp

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from .base_command import BaseCommand
from ..interfaces import (
    ConfigurationLoaderInterface,
    DisplayServiceInterface
)
from ..logging_config import LoggingConfigurator


class PushCommand(BaseCommand):
    """
    Single Responsibility: Handle the 'push' command execution
    Open/Closed: Easy to extend with new push modes or endpoints
    Dependency Inversion: Depends on abstractions, not concretions

    Note: Push command does NOT substitute environment variables to preserve
    ${VAR} syntax in the pushed configuration.
    """

    def __init__(
        self,
        config_loader: ConfigurationLoaderInterface,
        display_service: DisplayServiceInterface,
        logging_configurator: LoggingConfigurator
    ):
        super().__init__(display_service)
        self._config_loader = config_loader
        self._logging_configurator = logging_configurator
    
    async def execute(
        self,
        team_config: Path,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        debug: bool = False,
        verbose: bool = False,
        log_level: Optional[str] = None,
        log_file: Optional[str] = None,
        structured_logs: bool = False
    ) -> None:
        """Execute the push command with proper separation of concerns"""
        
        operation = "push command execution"
        self._log_execution_start(operation)
        
        try:
            # Configure logging first
            self._configure_logging(
                log_level, debug, verbose, log_file, 
                structured_logs
            )
            
            self._display_service.display_header()
            
            # Load and validate configuration
            team = await self._load_team_configuration(team_config)
            
            # Get API configuration
            effective_api_url, effective_api_key = self._get_api_configuration(
                api_url, api_key
            )
            
            # Convert team to API format
            team_config_data = self._convert_team_to_api_format(team)
            
            if verbose:
                import json
                try:
                    json.dumps(team_config_data)
                    self._display_service.display_status("✓ Team data successfully converted to JSON format", "success")
                except Exception as e:
                    self._display_service.display_status(f"JSON conversion test failed: {e}", "error")
                    # Let's inspect the problematic data
                    self._logger.debug(f"Team config data structure: {type(team_config_data)}")
                    raise
            
            # Push to API
            await self._push_team_to_api(
                team_config_data, effective_api_url, effective_api_key, verbose
            )
            
            self._display_service.display_status("Team pushed successfully", "success")
            self._log_execution_end(operation)
            
        except Exception as e:
            self._handle_error(e, operation)
            if verbose:
                import traceback
                self._display_service.display_status(traceback.format_exc(), "error")
            sys.exit(1)
    
    def _configure_logging(
        self, 
        log_level: Optional[str],
        debug: bool,
        verbose: bool,
        log_file: Optional[str],
        structured_logs: bool
    ) -> None:
        """Configure logging with provided parameters"""
        self._logging_configurator.configure_from_cli_args(
            log_level=log_level,
            debug=debug,
            verbose=verbose,
            log_file=log_file,
            structured_logs=structured_logs
        )
    
    async def _load_team_configuration(self, team_config: Path):
        """Load and validate team configuration"""
        with self._display_service.show_loading("Loading team configuration...") as status:
            try:
                team = self._config_loader.load_team_configuration(team_config)
                status.update("[bold green]✓ Team configuration loaded")
                return team
            except Exception as e:
                self._display_service.display_status(
                    f"Failed to load team configuration: {e}", 
                    "error"
                )
                raise
    
    def _get_api_configuration(
        self, 
        api_url: Optional[str], 
        api_key: Optional[str]
    ) -> tuple[str, str]:
        """Get effective API URL and key from parameters or environment"""
        effective_api_url = api_url or os.getenv("GNOSARI_API_URL")
        effective_api_key = api_key or os.getenv("GNOSARI_API_KEY")
        
        if not effective_api_url:
            raise ValueError("API URL is required. Set GNOSARI_API_URL environment variable or use --api-url parameter")
        
        if not effective_api_key:
            raise ValueError("API Key is required. Set GNOSARI_API_KEY environment variable or use --api-key parameter")
        
        return effective_api_url, effective_api_key
    
    def _convert_team_to_api_format(self, team) -> dict:
        """Convert team object to API format following the API schema"""
        
        # Base team configuration - all objects have proper attributes
        team_config = {
            "id": team.id,
            "name": team.name,
            "description": team.description,
            "version": team.version,
            "tags": team.tags,
            "config": self._convert_object_to_dict(team.config),
            "agents": [self._convert_agent_to_dict(agent) for agent in team.agents],
            "tools": [self._convert_tool_to_dict(tool) for tool in team.tools],
            "knowledge": [self._convert_knowledge_to_dict(knowledge) for knowledge in team.knowledge],
            "traits": [self._convert_trait_to_dict(trait) for trait in team.traits]
        }
        
        return team_config
    
    def _convert_object_to_dict(self, obj: Any) -> Any:
        """Convert any object to JSON-serializable format"""
        if obj is None:
            return None
        elif isinstance(obj, (str, int, float, bool)):
            return obj
        elif isinstance(obj, (list, tuple)):
            return [self._convert_object_to_dict(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: self._convert_object_to_dict(value) for key, value in obj.items()}
        elif hasattr(obj, 'model_dump'):
            # Pydantic model - get the dict representation
            return obj.model_dump()
        else:
            # Fallback to string representation for unknown types
            return str(obj)
    
    def _convert_agent_to_dict(self, agent) -> dict:
        """Convert agent object to API dict format"""
        return {
            "id": agent.id,
            "name": agent.name,
            "description": agent.description,
            "instructions": agent.instructions,
            "model": agent.model,
            "temperature": agent.temperature,
            "reasoning_effort": agent.reasoning_effort,
            "orchestrator": agent.is_orchestrator,
            "memory": agent.memory.content if agent.memory else "",
            "tools": [tool.id for tool in agent.tools],
            "knowledge": [knowledge.id for knowledge in agent.knowledge],
            "traits": [trait.id for trait in agent.traits],
            "delegation": [self._convert_delegation_to_dict(d) for d in agent.delegations],
            "learning_objectives": [self._convert_learning_objective_to_dict(lo) for lo in agent.learning_objectives],
            "listen": agent.listen
        }
    
    def _convert_delegation_to_dict(self, delegation) -> dict:
        """Convert delegation object to API dict format"""
        return {
            "agent": delegation.target_agent_id,
            "instructions": delegation.instructions
        }
    
    def _convert_learning_objective_to_dict(self, learning_objective) -> dict:
        """Convert learning objective object to API dict format"""
        obj_dict = learning_objective.model_dump()
        # Add required id field if missing
        if 'id' not in obj_dict:
            obj_dict['id'] = f"lo_{hash(learning_objective.objective) % 1000000}"
        return obj_dict
    
    def _convert_tool_to_dict(self, tool) -> dict:
        """Convert tool object to API dict format"""
        tool_config = {
            "id": tool.id,
            "name": tool.name,
            "description": tool.description,
            "module": tool.module,
            "class_name": tool.class_name,
            "url": tool.url,
            "command": tool.command,
            "connection_type": tool.connection_type,
            "args": self._convert_object_to_dict(tool.args),
            "headers": self._convert_object_to_dict(tool.headers),
            "timeout": tool.timeout
        }
        # Remove None values
        return {k: v for k, v in tool_config.items() if v is not None}
    
    def _convert_knowledge_to_dict(self, knowledge) -> dict:
        """Convert knowledge object to API dict format"""
        return {
            "id": knowledge.id,
            "name": knowledge.name,
            "description": knowledge.description,
            "type": knowledge.type,
            "data": knowledge.data,
            "config": self._convert_object_to_dict(knowledge.config)
        }
    
    def _convert_trait_to_dict(self, trait) -> dict:
        """Convert trait object to API dict format"""
        return {
            "id": trait.id,
            "name": trait.name,
            "description": trait.description,
            "instructions": trait.instructions,
            "weight": trait.weight,
            "category": trait.category,
            "tags": trait.tags
        }
    
    async def _push_team_to_api(
        self, 
        team_config: dict, 
        api_url: str, 
        api_key: str,
        verbose: bool
    ) -> None:
        """Push team configuration to the API"""
        
        push_url = f"{api_url.rstrip('/')}/api/v1/teams/push"
        
        headers = {
            'Content-Type': 'application/json',
            'X-AUTH-TOKEN': api_key
        }
        
        if verbose:
            self._display_service.display_status(f"Pushing to: {push_url}", "info")
            self._display_service.display_status(f"Team ID: {team_config.get('id')}", "info")

        # Debug: Log the request body
        self._logger.debug(f"Push URL: {push_url}")
        self._logger.debug(f"Request headers: {headers}")
        self._logger.debug(f"Request body: {json.dumps(team_config, indent=2)}")

        with self._display_service.show_loading("Pushing team to API...") as status:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        push_url,
                        headers=headers,
                        json=team_config,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        
                        # Debug: Log response status
                        self._logger.debug(f"Response status: {response.status}")

                        if response.status == 200:
                            result = await response.json()
                            self._logger.debug(f"Response body: {json.dumps(result, indent=2)}")
                            status.update("[bold green]✓ Team pushed successfully")

                            if verbose:
                                self._display_service.display_status(
                                    f"Team '{result.get('name', 'Unknown')}' pushed successfully",
                                    "success"
                                )

                        else:
                            error_text = await response.text()
                            self._logger.debug(f"Error response body: {error_text}")
                            try:
                                error_data = json.loads(error_text)
                                error_message = error_data.get('detail', error_text)
                            except json.JSONDecodeError:
                                error_message = error_text

                            raise Exception(f"API request failed with status {response.status}: {error_message}")
                            
            except aiohttp.ClientError as e:
                raise Exception(f"Network error: {e}")
            except Exception as e:
                self._display_service.display_status(f"Failed to push team: {e}", "error")
                raise