"""
CLI Services - SOLID implementation of CLI business logic
"""

import logging
import uuid
from pathlib import Path
from typing import Optional, Any, Dict

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn

logger = logging.getLogger(__name__)

from .interfaces import (
    ConfigurationLoaderInterface,
    ExecutionServiceInterface,
    DisplayServiceInterface,
    SessionManagerInterface,
    DomainFactoryInterface
)
from .event_display import EventDisplayService
from ..factories import ConfigurationServiceFactory
from ..factories.domain_object_factory import DomainObjectFactory
from ..schemas.domain import Team, AgentRun, Task, TaskRun, TaskExecutionContext, TaskRunMetadata
from ..schemas.domain.execution import ExecutionContext
from ..runners.factory import create_enterprise_runner
from ..sessions.gnosari_session import GnosariSession


class ConfigurationLoader(ConfigurationLoaderInterface):
    """Handles team configuration loading with error handling"""

    def __init__(self, skip_env_substitution: bool = False):
        """
        Initialize configuration loader.

        Args:
            skip_env_substitution: If True, environment variables will NOT be substituted.
                                   Used for push command to preserve ${VAR} syntax.
        """
        config_factory = ConfigurationServiceFactory()

        if skip_env_substitution:
            from ..config.env_substitutor import NoOpEnvironmentSubstitutor
            self._config_service = config_factory.create(env_substitutor=NoOpEnvironmentSubstitutor())
        else:
            self._config_service = config_factory.create()

    def load_team_configuration(self, config_path: Path) -> Team:
        """Load team configuration from file"""
        return self._config_service.load_team_configuration(config_path)


class ExecutionService(ExecutionServiceInterface):
    """Handles execution orchestration for teams and agents"""

    def __init__(self):
        self._event_display = EventDisplayService()

    async def _ensure_session_exists_in_database(
        self,
        session_id: str,
        agent_run: AgentRun,
        database_url: Optional[str] = None
    ) -> None:
        """
        Ensure session exists in database before execution starts.

        Follows Single Responsibility: Session lifecycle management is part of
        execution orchestration.

        Creates the session record proactively so that:
        - Session exists even if execution fails before messages are generated
        - Complete audit trail is maintained
        - Fail-fast principle is applied

        Args:
            session_id: Unique session identifier
            agent_run: AgentRun with complete metadata
            database_url: Optional database URL

        Note:
            Errors are logged but don't fail execution - session will be created
            lazily if needed during message persistence.
        """
        try:
            import os
            from sqlalchemy import (
                MetaData, Table, Column, String, Integer, DateTime,
                Text, text as sql_text
            )
            from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
            from ..sessions.repositories.session_repository import SessionRepository

            # Get database URL from parameters, environment, or default
            db_url = (
                database_url or
                os.getenv("GNOSARI_DATABASE_URL") or
                "sqlite+aiosqlite:///sessions.db"
            )

            logger.debug(f"Pre-creating session {session_id} in database: {db_url}")

            # Create temporary engine for session creation
            engine = create_async_engine(
                db_url,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10
            )

            try:
                # Define database schema (matches existing structure)
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
                    Column("created_at", DateTime, nullable=False,
                           server_default=sql_text("CURRENT_TIMESTAMP")),
                    Column("updated_at", DateTime, nullable=False,
                           server_default=sql_text("CURRENT_TIMESTAMP")),
                )

                messages_table = Table(
                    "session_messages",
                    metadata,
                    Column("id", Integer, primary_key=True, autoincrement=True),
                    Column("session_id", String, nullable=False),
                    Column("message_data", Text, nullable=False),
                    Column("account_id", Integer, nullable=True),
                    Column("created_at", DateTime, nullable=False,
                           server_default=sql_text("CURRENT_TIMESTAMP")),
                    Column("updated_at", DateTime, nullable=False,
                           server_default=sql_text("CURRENT_TIMESTAMP")),
                    sqlite_autoincrement=True,
                )

                # Create tables if they don't exist
                async with engine.begin() as conn:
                    await conn.run_sync(metadata.create_all)

                logger.debug(f"Database tables ensured for session {session_id}")

                # Create session factory and repository
                session_factory = async_sessionmaker(
                    engine,
                    expire_on_commit=False,
                    autoflush=True,
                    autocommit=False
                )

                repository = SessionRepository(
                    session_factory,
                    sessions_table,
                    messages_table
                )

                # Ensure session exists with AgentRun context
                # This creates the session record with all metadata from agent_run
                await repository.ensure_session_exists(session_id, agent_run)

                logger.info(
                    f"Session {session_id} successfully pre-created in database "
                    f"before execution (account_id={agent_run.metadata.account_id}, "
                    f"team={agent_run.metadata.team_identifier}, "
                    f"agent={agent_run.metadata.agent_identifier})"
                )

            finally:
                # Clean up temporary engine
                await engine.dispose()
                logger.debug(f"Database engine disposed after session pre-creation")

        except Exception as e:
            # Log error but don't fail execution
            # Session will be created lazily during message persistence if needed
            logger.warning(
                f"Failed to pre-create session {session_id} in database: {e}. "
                f"Session will be created lazily if needed."
            )

    async def execute_agent(
        self,
        agent_run: AgentRun,
        provider: str,
        database_url: Optional[str] = None,
        stream: bool = True,
        debug: bool = False,
    ) -> str:
        """Execute a single agent with advanced event display"""
        # Use session_id from agent_run.metadata if available, otherwise generate one
        session_id = agent_run.metadata.session_id or f"agent-{agent_run.agent.id}-{uuid.uuid4().hex[:8]}"
        agent_run.metadata.session_id = session_id  # Ensure it's set

        session_manager = GnosariSession(
            session_id=session_id,
            provider_name=f"{provider}_database",
            agent_run=agent_run,  # Pass AgentRun directly
            database_url=database_url
        )

        # Pre-create session in database before execution starts
        # This ensures session exists even if execution fails before messages are generated
        await self._ensure_session_exists_in_database(
            session_id=session_id,
            agent_run=agent_run,
            database_url=database_url
        )

        runner = create_enterprise_runner(provider, agent_run.context)
        
        try:
            await runner.initialize()
            
            if stream:
                final_result = None
                agent_completed = False

                # Use live event display system
                with self._event_display.live_event_display(debug=debug):
                    async for event in runner.run_agent_stream(agent_run):
                        # Handle the event through the display service
                        self._event_display.handle_event(event, debug=debug)

                        # Check for completion events and capture result
                        if event.event_type == "agent_completed":
                            data = event.data
                            if hasattr(data, 'to_dict'):
                                data = data.to_dict()
                            final_result = data.get("output", "Agent execution completed")
                            agent_completed = True
                            # Continue processing remaining events instead of breaking
                        elif event.event_type == "agent_error":
                            data = event.data
                            if hasattr(data, 'to_dict'):
                                data = data.to_dict()
                            final_result = f"Agent error: {data.get('error', 'Unknown error')}"
                            agent_completed = True
                            # Continue processing remaining events instead of breaking

                # Display execution summary
                if not debug:
                    self._event_display.display_summary()

                return final_result or f"Agent {agent_run.agent.name} completed processing"
            else:
                return await runner.run_agent(agent_run)
                
        finally:
            await runner.cleanup()
            await session_manager.cleanup()


class DisplayService(DisplayServiceInterface):
    """Handles all display and formatting concerns"""
    
    def __init__(self):
        self.console = Console()
    
    def display_header(self) -> None:
        return
        """Display the CLI header with ASCII art"""
        header = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║     ██████╗ ███╗   ██╗ ██████╗ ███████╗ █████╗ ██████╗ ██╗   ║
    ║    ██╔════╝ ████╗  ██║██╔═══██╗██╔════╝██╔══██╗██╔══██╗██║   ║
    ║    ██║  ███╗██╔██╗ ██║██║   ██║███████╗███████║██████╔╝██║   ║
    ║    ██║   ██║██║╚██╗██║██║   ██║╚════██║██╔══██║██╔══██╗██║   ║
    ║    ╚██████╔╝██║ ╚████║╚██████╔╝███████║██║  ██║██║  ██║██║   ║
    ║     ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝   ║
    ║                                                              ║
    ║                 🚀 AI Agent Team Orchestration               ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
        """
        
        text = Text(header, style="bold cyan")
        self.console.print(text, justify="center")
    
    def display_execution_details(
        self, 
        team: Team, 
        provider: str, 
        execution_mode: str,
        session_id: Optional[str] = None
    ) -> None:
        """Display execution details panel"""
        details = (
            f"[bold cyan]Team:[/bold cyan] {team.name}\n"
            f"[bold cyan]Agents:[/bold cyan] {len(team.agents)}\n"
            f"[bold cyan]Provider:[/bold cyan] {provider}\n"
            f"[bold cyan]Mode:[/bold cyan] {execution_mode}"
        )
        
        if session_id:
            details += f"\n[bold cyan]Session:[/bold cyan] {session_id}"
        
        self.console.print(Panel.fit(
            details,
            title="🎯 Execution Details",
            border_style="cyan"
        ))
    
    def display_status(self, message: str, status_type: str = "info") -> None:
        """Display status messages"""
        color_map = {
            "info": "blue",
            "success": "green",
            "warning": "yellow",
            "error": "red"
        }
        color = color_map.get(status_type, "blue")
        self.console.print(f"[{color}]{message}[/{color}]")
    
    def display_streaming_output(self, content: str) -> None:
        """Display streaming content"""
        self.console.print(content, end="")
    
    def display_final_result(self, result: str) -> None:
        """Display final execution result"""
        self.console.print(f"\n[bold green]Final Result:[/bold green] {result}")
    
    def show_loading(self, message: str):
        """Create a loading context manager"""
        return self.console.status(f"[bold blue]{message}[/bold blue]", spinner="dots")
    
    def show_progress(self, description: str):
        """Create a progress context manager"""
        return Progress(
            SpinnerColumn(),
            TextColumn(f"[progress.description]{description}"),
            console=self.console
        )


class SessionManager(SessionManagerInterface):
    """Handles session management concerns"""
    
    def generate_session_id(self) -> str:
        """Generate a new session ID"""
        return f"session-{uuid.uuid4().hex[:8]}"
    


class DomainFactory(DomainFactoryInterface):
    """Handles domain object creation"""
    
    def __init__(self):
        self._domain_factory = DomainObjectFactory()
    
    
    def create_agent_run(
        self,
        team: Team,
        agent_id: str,
        message: str,
        stream: bool = True,
        debug: bool = False,
        tool_streaming: bool = True,
        stream_merger: str = "time_ordered"
    ) -> AgentRun:
        """Create agent execution context"""
        agent = team.get_agent_by_id(agent_id) or team.get_agent_by_name(agent_id)
        if not agent:
            raise ValueError(f"Agent '{agent_id}' not found in team configuration")

        execution_context = ExecutionContext(
            stream=stream,
            debug=debug,
            tool_streaming=tool_streaming,
            tool_streaming_merger=stream_merger
        )
        return self._domain_factory.create_agent_run(agent, team, message, execution_context)

    def create_task_from_dict(self, task_data: Dict[str, Any]) -> Task:
        """
        Create Task domain object from dictionary (e.g., from database).

        Args:
            task_data: Dictionary with task data from database

        Returns:
            Task domain object
        """
        return Task.from_dict(task_data)

    def create_task_run(
        self,
        task: Task,
        team: Team,
        prompt_builder: Any,
        stream: bool = True,
        debug: bool = False,
        tool_streaming: bool = True,
        stream_merger: str = "time_ordered",
        session_id: Optional[str] = None,
        account_id: Optional[int] = None
    ) -> TaskRun:
        """
        Create TaskRun execution context.

        Args:
            task: Task domain object
            team: Team configuration
            prompt_builder: Prompt builder for task-specific prompts
            stream: Enable streaming mode
            debug: Enable debug mode
            tool_streaming: Enable tool streaming
            stream_merger: Stream merger type
            session_id: Optional session ID
            account_id: Optional account ID

        Returns:
            TaskRun domain object ready for execution

        Raises:
            ValueError: If assigned agent not found in team
        """
        # Find agent in team by identifier
        agent = team.get_agent_by_id(task.assigned_agent_identifier)
        if not agent:
            agent = team.get_agent_by_name(task.assigned_agent_identifier)

        if not agent:
            available_agents = [a.id for a in team.agents]
            raise ValueError(
                f"Agent '{task.assigned_agent_identifier}' not found in team. "
                f"Available agents: {', '.join(available_agents)}"
            )

        # Build task-specific prompt
        task_prompt = prompt_builder.build_task_execution_prompt(
            agent, team, task.to_dict()
        )

        # Use task.input_message as the execution message if available
        # otherwise use title
        message = task.input_message or f"Execute task: {task.title}"

        # Create execution context
        context = TaskExecutionContext(
            stream=stream,
            debug=debug,
            tool_streaming=tool_streaming,
            tool_streaming_merger=stream_merger
        )

        # Create metadata
        from datetime import datetime
        metadata = TaskRunMetadata(
            task_id=int(task.id) if task.id else 0,
            task_identifier=task.name,
            account_id=account_id or task.account_id,
            team_id=task.assigned_team_id,
            agent_id=task.assigned_agent_id,
            team_identifier=task.assigned_team_identifier,
            agent_identifier=task.assigned_agent_identifier,
            session_id=session_id or task.session_id,
            execution_start=datetime.utcnow()
        )

        # Store original instructions and override temporarily
        original_instructions = agent.instructions
        agent.instructions = task_prompt

        # Create TaskRun
        task_run = TaskRun(
            task=task,
            agent=agent,
            team=team,
            message=message,
            context=context,
            metadata=metadata
        )

        # Restore original instructions
        agent.instructions = original_instructions

        return task_run