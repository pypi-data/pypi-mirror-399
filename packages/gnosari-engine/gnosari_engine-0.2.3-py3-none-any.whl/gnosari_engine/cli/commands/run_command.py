"""
Run Command - Handles team and agent execution
"""

import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from .base_command import BaseCommand
from ..interfaces import (
    ConfigurationLoaderInterface,
    ExecutionServiceInterface,
    DisplayServiceInterface,
    SessionManagerInterface,
    DomainFactoryInterface
)
from ..logging_config import LoggingConfigurator


class RunCommand(BaseCommand):
    """
    Single Responsibility: Handle the 'run' command execution
    Open/Closed: Easy to extend with new execution modes
    Dependency Inversion: Depends on abstractions, not concretions
    """
    
    def __init__(
        self,
        config_loader: ConfigurationLoaderInterface,
        execution_service: ExecutionServiceInterface,
        display_service: DisplayServiceInterface,
        session_manager: SessionManagerInterface,
        domain_factory: DomainFactoryInterface,
        logging_configurator: LoggingConfigurator
    ):
        super().__init__(display_service)
        self._config_loader = config_loader
        self._execution_service = execution_service
        self._session_manager = session_manager
        self._domain_factory = domain_factory
        self._logging_configurator = logging_configurator
    
    async def execute(
        self,
        team_config: Path,
        message: str,
        agent: Optional[str] = None,
        session_id: Optional[str] = None,
        stream: bool = True,
        debug: bool = False,
        provider: str = "openai",
        database_url: Optional[str] = None,
        verbose: bool = False,
        log_level: Optional[str] = None,
        log_file: Optional[str] = None,
        structured_logs: bool = False,
        tool_streaming: bool = True,
        stream_merger: str = "time_ordered"
    ) -> None:
        """Execute the run command with proper separation of concerns"""
        
        operation = "run command execution"
        self._log_execution_start(operation)
        
        try:
            # Configure logging first
            self._configure_logging(
                log_level, debug, verbose, log_file, 
                structured_logs, session_id
            )
            
            self._display_service.display_header()
            
            # Load and validate configuration
            team = await self._load_team_configuration(team_config)
            
            # Setup session management
            effective_session_id = self._setup_session(
                session_id, team, agent, provider, verbose
            )
            
            # Execute agent only (team execution removed)
            if not agent:
                raise ValueError("Agent execution is required. Team execution has been removed.")
            
            await self._execute_agent(
                team, agent, message,
                provider, database_url, stream, debug, 
                tool_streaming, stream_merger
            )
            
            self._display_service.display_status("Execution completed successfully", "success")
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
        structured_logs: bool,
        session_id: Optional[str]
    ) -> None:
        """Configure logging with provided parameters"""
        self._logging_configurator.configure_from_cli_args(
            log_level=log_level,
            debug=debug,
            verbose=verbose,
            log_file=log_file,
            structured_logs=structured_logs,
            session_id=session_id
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
    
    def _setup_session(
        self,
        session_id: Optional[str],
        team,
        agent: Optional[str],
        provider: str,
        verbose: bool
    ) -> str:
        """Setup session management and context"""
        effective_session_id = session_id or self._session_manager.generate_session_id()
        
        # Add execution context to logging
        self._logging_configurator.add_execution_context(
            provider=provider,
            execution_mode="Agent Execution" if agent else "Team Execution",
            team_id=team.id,
            agent_id=agent
        )
        
        # Display execution details
        execution_mode = "Agent Execution" if agent else "Team Execution"
        self._display_service.display_execution_details(
            team, provider, execution_mode, effective_session_id
        )
        
        if verbose and session_id is None:
            self._display_service.display_status(
                f"Generated session ID: {effective_session_id}", 
                "info"
            )
        
        # Get account_id from environment variable
        account_id = os.getenv("GNOSARI_ACCOUNT_ID")
        if account_id:
            try:
                account_id = int(account_id)
            except ValueError:
                self._logger.warning(f"Invalid GNOSARI_ACCOUNT_ID format: {account_id}. Using None.")
                account_id = None
        
        # Store session metadata for later use in AgentRun.metadata
        self._session_id = effective_session_id
        self._account_id = account_id
        self._team_identifier = team.id
        self._agent_identifier = agent
        self._logger.debug(f"Session metadata prepared: session_id={effective_session_id}, account_id={account_id}")
        
        return effective_session_id
    
    
    async def _execute_agent(
        self,
        team,
        agent_id: str,
        message: str,
        provider: str,
        database_url: Optional[str],
        stream: bool,
        debug: bool,
        tool_streaming: bool,
        stream_merger: str
    ) -> None:
        """Execute a single agent"""
        self._logger.debug(f"Starting agent execution: {agent_id}")
        self._display_service.display_status(f"🎯 Running agent: {agent_id}", "info")
        
        # Create agent run
        agent_run = self._domain_factory.create_agent_run(
            team, agent_id, message, stream, debug, tool_streaming, stream_merger
        )
        
        # Set session metadata in AgentRun.metadata
        agent_run.metadata.session_id = self._session_id
        agent_run.metadata.account_id = self._account_id
        agent_run.metadata.team_identifier = self._team_identifier
        agent_run.metadata.agent_identifier = agent_id
        
        self._logger.debug(f"Agent run created for: {agent_id} with session_id: {self._session_id}")
        
        # Execute with appropriate mode
        if stream:
            await self._execute_agent_streaming(
                agent_run, provider, database_url, stream, debug
            )
        else:
            await self._execute_agent_batch(
                agent_run, provider, database_url, stream, debug
            )
        
        self._logger.debug(f"Agent execution completed: {agent_id}")
    
    async def _execute_agent_streaming(
        self,
        agent_run,
        provider: str,
        database_url: Optional[str],
        stream: bool,
        debug: bool
    ) -> None:
        """Execute agent in streaming mode"""
        self._logger.info("Executing agent in streaming mode")
        self._display_service.display_status("Streaming agent response...", "info")
        result = await self._execution_service.execute_agent(
            agent_run, provider, database_url, stream, debug
        )
        if result:
            self._display_service.display_final_result(result)
    
    async def _execute_agent_batch(
        self,
        agent_run,
        provider: str,
        database_url: Optional[str],
        stream: bool,
        debug: bool
    ) -> None:
        """Execute agent in batch mode"""
        self._logger.info("Executing agent in batch mode")
        with self._display_service.show_progress("Processing...") as progress:
            task = progress.add_task("Processing...", total=None)
            result = await self._execution_service.execute_agent(
                agent_run, provider, database_url, stream, debug
            )
            progress.update(task, completed=True)
        
        self._display_service.display_final_result(result)
    
    
    
