"""
Learn Command - Enables agent learning from session history
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
    DisplayServiceInterface,
    SessionManagerInterface,
    DomainFactoryInterface
)
from ..logging_config import LoggingConfigurator
from ...learning.learning_service import LearningService
from ...learning.teacher_agent_factory import TeacherAgentFactory
from ...sessions.repositories.session_repository import SessionRepository


class LearnCommand(BaseCommand):
    """
    Single Responsibility: Handle agent learning from session history
    Open/Closed: Easy to extend with new learning modes
    Dependency Inversion: Depends on abstractions, not concretions
    """
    
    def __init__(
        self,
        config_loader: ConfigurationLoaderInterface,
        display_service: DisplayServiceInterface,
        session_manager: SessionManagerInterface,
        domain_factory: DomainFactoryInterface,
        logging_configurator: LoggingConfigurator,
        learning_service: LearningService,
        teacher_agent_factory: TeacherAgentFactory,
        session_repository: Optional[SessionRepository]
    ):
        super().__init__(display_service)
        self._config_loader = config_loader
        self._session_manager = session_manager
        self._domain_factory = domain_factory
        self._logging_configurator = logging_configurator
        self._learning_service = learning_service
        self._teacher_agent_factory = teacher_agent_factory
        self._session_repository = session_repository
    
    async def execute(
        self,
        team_config: Path,
        agent_id: str,
        session_id: Optional[str] = None,
        provider: str = "openai",
        database_url: Optional[str] = None,
        debug: bool = False,
        verbose: bool = False,
        log_level: Optional[str] = None,
        log_file: Optional[str] = None,
        structured_logs: bool = False,
        max_sessions: int = 10
    ) -> None:
        """Execute the learn command with proper separation of concerns"""
        
        operation = "learn command execution"
        self._log_execution_start(operation)
        
        try:
            # Configure logging first
            self._configure_logging(
                log_level, debug, verbose, log_file, 
                structured_logs, session_id
            )
            
            self._display_service.display_header()
            self._display_service.display_status(f"🧠 Starting learning for agent: {agent_id}", "info")
            
            # Load and validate team configuration
            team = await self._load_team_configuration(team_config)
            
            # Find the target agent
            target_agent = team.get_agent_by_id(agent_id)
            if not target_agent:
                raise ValueError(f"Agent '{agent_id}' not found in team configuration")
            
            # Validate session exists if session_id is provided
            if session_id:
                await self._validate_session_exists(session_id, database_url)
            
            # Execute learning workflow
            await self._execute_learning_workflow(
                team, target_agent, session_id, provider, 
                database_url, max_sessions, verbose
            )
            
            self._display_service.display_status("Learning completed successfully", "success")
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
        session_id: str
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
    
    async def _validate_session_exists(self, session_id: str, database_url: Optional[str] = None) -> None:
        """Validate that the session exists in the database"""
        with self._display_service.show_loading("Validating session...") as status:
            try:
                session_repository = self._get_session_repository(database_url)
                exists = await session_repository.session_exists(session_id)
                if not exists:
                    raise ValueError(f"Session '{session_id}' not found in database")
                status.update("[bold green]✓ Session validated")
            except Exception as e:
                self._display_service.display_status(
                    f"Failed to validate session: {e}",
                    "error"
                )
                raise
    
    def _get_session_repository(self, database_url: Optional[str] = None) -> SessionRepository:
        """Get or create session repository dynamically"""
        if self._session_repository is not None:
            return self._session_repository
        
        # Create session repository with database connection
        # This mimics how it's done in the OpenAI database provider
        from sqlalchemy import MetaData, Table, Column, String, Integer, DateTime, Text, ForeignKey
        from sqlalchemy.sql import text as sql_text
        from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
        
        # Use priority order: parameter -> environment variable -> default
        database_url = (
            database_url or 
            os.getenv("GNOSARI_DATABASE_URL") or 
            "sqlite+aiosqlite:///sessions.db"
        )
        
        # Create database engine
        engine = create_async_engine(
            database_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        
        # Create session factory
        session_factory = async_sessionmaker(
            bind=engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False
        )
        
        # Create table metadata (matching the schema in the database provider)
        metadata = MetaData()
        
        sessions_table = Table(
            "sessions",
            metadata,
            Column("session_id", String, primary_key=True),
            Column("account_id", Integer, nullable=True),
            Column("team_id", Integer, nullable=True),
            Column("agent_id", Integer, nullable=True),
            Column("team_identifier", String, nullable=True),
            Column("agent_identifier", String, nullable=True),
            Column("created_at", DateTime, nullable=False, server_default=sql_text("CURRENT_TIMESTAMP")),
            Column("updated_at", DateTime, nullable=False, server_default=sql_text("CURRENT_TIMESTAMP"), onupdate=sql_text("CURRENT_TIMESTAMP")),
        )
        
        messages_table = Table(
            "session_messages",
            metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("session_id", String, ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False),
            Column("message_data", Text, nullable=False),
            Column("account_id", Integer, nullable=True),
            Column("created_at", DateTime, nullable=False, server_default=sql_text("CURRENT_TIMESTAMP")),
            Column("updated_at", DateTime, nullable=False, server_default=sql_text("CURRENT_TIMESTAMP"), onupdate=sql_text("CURRENT_TIMESTAMP"))
        )
        
        # Create and cache the repository
        self._session_repository = SessionRepository(
            session_factory,
            sessions_table,
            messages_table
        )
        
        return self._session_repository
    
    async def _execute_learning_workflow(
        self,
        team,
        target_agent,
        session_id: Optional[str],
        provider: str,
        database_url: Optional[str],
        max_sessions: int,
        verbose: bool
    ) -> None:
        """Execute the learning workflow"""
        
        # Display learning context
        self._display_learning_context(target_agent, session_id, max_sessions, team)
        
        # Retrieve session messages filtered by agent and team
        with self._display_service.show_loading("Retrieving session messages...") as status:
            session_repository = self._get_session_repository(database_url)
            session_messages = await session_repository.get_messages_by_agent_and_team(
                agent_identifier=target_agent.id,
                team_identifier=team.id,
                session_id=session_id,  # Will be None if not specified, which gets all sessions for this agent/team
                limit=max_sessions
            )
            
            if session_id:
                status.update(f"[bold green]✓ Retrieved {len(session_messages)} messages for agent '{target_agent.id}' in team '{team.id}' from session {session_id}")
            else:
                status.update(f"[bold green]✓ Retrieved {len(session_messages)} messages for agent '{target_agent.id}' in team '{team.id}' from all sessions")
        
        if not session_messages:
            if session_id:
                self._display_service.display_status(
                    f"No messages found for agent '{target_agent.id}' in team '{team.id}' in session '{session_id}'",
                    "warning"
                )
            else:
                self._display_service.display_status(
                    f"No messages found for agent '{target_agent.id}' in team '{team.id}' in any sessions",
                    "warning"
                )
            return
        
        # Generate learning content
        with self._display_service.show_loading("Updating memory...") as status:
            learning_content = await self._learning_service.generate_learning_content(
                target_agent=target_agent,
                session_messages=session_messages,
                provider=provider,
                database_url=database_url
            )
            status.update("[bold green]✓ Memory updated")

        # Apply learning to agent
        with self._display_service.show_loading("Applying memory update...") as status:
            updated_agent = await self._learning_service.apply_learning_to_agent(
                target_agent, learning_content
            )
            status.update("[bold green]✓ Learning applied to agent")

        # Display learning results
        self._display_learning_results(updated_agent, learning_content, verbose)
        
        # Display the final updated memory
        if updated_agent.memory and not updated_agent.memory.is_empty():
            self._display_service.display_status("🧠 Final Updated Memory:", "success")
            self._display_service.display_final_result(updated_agent.memory.content)
        else:
            self._display_service.display_status("No memory content available", "warning")
    
    def _display_learning_context(
        self,
        target_agent,
        session_id: Optional[str],
        max_sessions: int,
        team = None
    ) -> None:
        """Display learning context information"""
        self._display_service.display_status(
            f"Agent: {target_agent.name} ({target_agent.id})",
            "info"
        )
        if team:
            self._display_service.display_status(
                f"Team: {team.name} ({team.id})",
                "info"
            )
        if session_id:
            self._display_service.display_status(
                f"Session: {session_id}",
                "info"
            )
        else:
            self._display_service.display_status(
                "Session: All sessions",
                "info"
            )
        self._display_service.display_status(
            f"Max Messages: {max_sessions}",
            "info"
        )
        self._display_service.display_status(
            f"Learning Objectives: {len(target_agent.learning_objectives)}",
            "info"
        )
    
    def _display_learning_results(
        self,
        updated_agent,
        learning_content: str,
        verbose: bool
    ) -> None:
        """Display learning results"""
        self._display_service.display_status("🎓 Learning Results:", "success")
        
        # Display updated memory if it changed
        if not updated_agent.memory.is_empty():
            memory_summary = updated_agent.memory.get_summary(100)
            self._display_service.display_status(
                f"Updated Memory: {memory_summary}",
                "info"
            )
        
        # Display learning objectives progress
        if updated_agent.learning_objectives:
            self._display_service.display_status(
                f"Learning Objectives: {len(updated_agent.learning_objectives)} active",
                "info"
            )
        
        # Display learning content if verbose
        if verbose and learning_content:
            self._display_service.display_status("Generated Learning Content:", "info")
            # Truncate for display
            display_content = learning_content[:500] + "..." if len(learning_content) > 500 else learning_content
            self._display_service.display_status(display_content, "info")