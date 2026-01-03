"""
Task Run Command - Handles task execution by ID

This command loads a task from the database, finds the assigned agent,
and executes the task with proper context and prompting.

Follows SOLID principles:
- Single Responsibility: Only handles task execution command orchestration
- Open/Closed: Easy to extend with new task execution modes
- Dependency Inversion: Depends on abstractions, not concretions

Architecture:
- Loads task from database via TaskRepository
- Creates domain objects via DomainFactory
- Delegates execution to TaskExecutor service
- TaskExecutor handles status management and result storage
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
from ...sessions.repositories.task_repository import TaskRepository
from ...prompts.agent_prompt_builder import AgentPromptBuilder
from ...services.task_executor import TaskExecutor
from ...queue.dispatcher import MessageDispatcher
from ...config.env_helpers import get_database_url

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


class TaskRunCommand(BaseCommand):
    """
    Single Responsibility: Handle the 'task run' command orchestration
    Open/Closed: Easy to extend with new execution modes
    Dependency Inversion: Depends on abstractions, not concretions

    This command is a thin orchestration layer that:
    1. Loads task from database
    2. Creates domain objects (Task, TaskRun)
    3. Delegates execution to TaskExecutor service
    """

    def __init__(
        self,
        config_loader: ConfigurationLoaderInterface,
        display_service: DisplayServiceInterface,
        session_manager: SessionManagerInterface,
        domain_factory: DomainFactoryInterface,
        logging_configurator: LoggingConfigurator,
        prompt_builder: AgentPromptBuilder,
        message_dispatcher: Optional[MessageDispatcher] = None
    ):
        super().__init__(display_service)
        self._config_loader = config_loader
        self._session_manager = session_manager
        self._domain_factory = domain_factory
        self._logging_configurator = logging_configurator
        self._prompt_builder = prompt_builder
        self._message_dispatcher = message_dispatcher or MessageDispatcher()
        self._task_repository = None
        self._task_executor = None

    async def execute(
        self,
        team_config: Path,
        task_id: int,
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
        stream_merger: str = "time_ordered",
        async_mode: bool = False
    ) -> None:
        """
        Execute the task run command.

        This is a thin orchestration layer that:
        1. Loads task from database
        2. Creates Task and TaskRun domain objects
        3. Delegates execution to TaskExecutor service

        TaskExecutor handles:
        - Status updates (pending → in_progress → completed/failed)
        - Agent execution
        - Result storage

        Args:
            team_config: Path to team configuration file
            task_id: ID of the task to execute
            session_id: Optional session ID
            stream: Enable streaming output
            debug: Enable debug mode
            provider: LLM provider to use
            database_url: Database connection URL
            verbose: Enable verbose output
            log_level: Logging level
            log_file: Log file path
            structured_logs: Enable structured logging
            tool_streaming: Enable tool streaming
            stream_merger: Stream merger strategy
            async_mode: Execute asynchronously via queue (default: False)
        """
        operation = "task run command execution"
        self._log_execution_start(operation)

        try:
            # Configure logging first
            self._configure_logging(
                log_level, debug, verbose, log_file,
                structured_logs, session_id
            )

            self._display_service.display_header()

            # Validate and get database URL
            database_url = self._get_database_url(database_url, verbose)

            # Get account_id from environment
            account_id = self._get_account_id()

            # Check if async mode - route to queue dispatcher
            if async_mode:
                await self._execute_async(
                    team_config=team_config,
                    task_id=task_id,
                    account_id=account_id,
                    provider=provider,
                    database_url=database_url,
                    session_id=session_id,
                    debug=debug,
                    tool_streaming=tool_streaming,
                    stream_merger=stream_merger,
                    verbose=verbose
                )
                return

            # Initialize task repository and executor
            await self._initialize_task_repository(database_url)
            self._task_executor = TaskExecutor(task_repository=self._task_repository)

            # Load task data from database
            task_data = await self._load_task_data(task_id, account_id, verbose)

            # Create Task domain object
            task = self._create_task_domain_object(task_data, verbose)

            # Load and validate team configuration
            team = await self._load_team_configuration(team_config)

            # Generate or use provided session ID
            effective_session_id = session_id or self._session_manager.generate_session_id()

            # Display execution details
            self._display_execution_details(team, task, provider, effective_session_id, verbose)

            # Create TaskRun domain object
            task_run = self._create_task_run(
                task, team, effective_session_id, account_id,
                stream, debug, tool_streaming, stream_merger, verbose
            )

            # Execute task via TaskExecutor service
            await self._execute_task(
                task_run, task_id, provider, database_url, stream, verbose
            )

            if verbose:
                self._display_service.display_status(
                    f"Task #{task_id} execution completed successfully", "success"
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

    def _get_account_id(self) -> int:
        """
        Get account_id from environment variable.

        Returns:
            Account ID

        Raises:
            ValueError: If account_id not set or invalid
        """
        account_id = os.getenv("GNOSARI_ACCOUNT_ID")
        if not account_id:
            raise ValueError(
                "GNOSARI_ACCOUNT_ID environment variable is required for task loading"
            )

        try:
            return int(account_id)
        except ValueError:
            raise ValueError(
                f"Invalid GNOSARI_ACCOUNT_ID format: {account_id}. Must be an integer."
            )

    def _get_database_url(self, database_url: Optional[str], verbose: bool) -> str:
        """
        Get database URL from parameter or environment variable.

        Args:
            database_url: Database URL from command line
            verbose: Enable verbose output

        Returns:
            Database URL string

        Raises:
            ValueError: If database URL is not provided
        """
        db_url = database_url or os.getenv("GNOSARI_DATABASE_URL")
        if not db_url:
            raise ValueError(
                "Database URL is required. Provide via --database-url or "
                "GNOSARI_DATABASE_URL environment variable."
            )

        if verbose:
            # Mask password in verbose output
            masked_url = db_url
            if "@" in masked_url and ":" in masked_url.split("@")[0]:
                parts = masked_url.split(":")
                if len(parts) >= 3:
                    masked_url = f"{parts[0]}:{parts[1]}:***@{':'.join(parts[3:])}"
            self._display_service.display_status(
                f"Using database: {masked_url}", "info"
            )

        return db_url

    async def _initialize_task_repository(self, database_url: str) -> None:
        """
        Initialize task repository with database connection.

        Args:
            database_url: Database connection URL
        """
        self._logger.debug("Initializing task repository")

        # Create async engine with connection pool
        engine = create_async_engine(
            database_url,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=3600,
            pool_pre_ping=True,
            echo=False
        )

        # Create session factory
        session_factory = async_sessionmaker(
            engine,
            expire_on_commit=False,
            autoflush=False
        )

        # Create repository
        self._task_repository = TaskRepository(session_factory)
        self._logger.debug("Task repository initialized successfully")

    async def _load_task_data(self, task_id: int, account_id: int, verbose: bool) -> dict:
        """
        Load task data from database by ID.

        Args:
            task_id: Task ID to load
            account_id: Account ID for multi-tenant isolation
            verbose: Enable verbose output

        Returns:
            Task data dictionary from database

        Raises:
            ValueError: If task not found
        """
        with self._display_service.show_loading(f"Loading task #{task_id}...") as status:
            # Load task from database
            task_data = await self._task_repository.get_task(task_id, account_id)

            if not task_data:
                raise ValueError(f"Task #{task_id} not found for account {account_id}")

            status.update(f"[bold green]✓ Task #{task_id} loaded: {task_data['title']}")

            if verbose:
                self._display_service.display_status(
                    f"Task: {task_data['title']} (Type: {task_data['type']}, "
                    f"Status: {task_data['status']})",
                    "info"
                )

            return task_data

    def _create_task_domain_object(self, task_data: dict, verbose: bool):
        """
        Create Task domain object from database data.

        Args:
            task_data: Task data dictionary from database
            verbose: Enable verbose output

        Returns:
            Task domain object
        """
        task = self._domain_factory.create_task_from_dict(task_data)

        if verbose:
            self._display_service.display_status(
                f"Created Task domain object: {task.title}", "info"
            )
            if task.assigned_agent_identifier:
                self._display_service.display_status(
                    f"Assigned to agent: {task.assigned_agent_identifier}", "info"
                )

        return task

    async def _load_team_configuration(self, team_config: Path):
        """
        Load and validate team configuration.

        Args:
            team_config: Path to team configuration file

        Returns:
            Loaded team object
        """
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

    def _display_execution_details(
        self,
        team,
        task,
        provider: str,
        session_id: str,
        verbose: bool
    ) -> None:
        """
        Display execution details.

        Args:
            team: Team object
            task: Task domain object
            provider: LLM provider
            session_id: Session ID
            verbose: Enable verbose output
        """
        # Add execution context to logging
        self._logging_configurator.add_execution_context(
            provider=provider,
            execution_mode="Task Execution",
            team_id=team.id,
            agent_id=task.assigned_agent_identifier
        )

        # Display execution details
        self._display_service.display_execution_details(
            team, provider, "Task Execution", session_id
        )

        if verbose:
            self._display_service.display_status(
                f"Session ID: {session_id}", "info"
            )
            self._display_service.display_status(
                f"Task: {task.title} (ID: {task.id})", "info"
            )

    def _create_task_run(
        self,
        task,
        team,
        session_id: str,
        account_id: int,
        stream: bool,
        debug: bool,
        tool_streaming: bool,
        stream_merger: str,
        verbose: bool
    ):
        """
        Create TaskRun domain object for execution.

        Args:
            task: Task domain object
            team: Team object
            session_id: Session ID
            account_id: Account ID
            stream: Enable streaming
            debug: Enable debug mode
            tool_streaming: Enable tool streaming
            stream_merger: Stream merger strategy
            verbose: Enable verbose output

        Returns:
            TaskRun domain object
        """
        if verbose:
            self._display_service.display_status(
                f"Creating TaskRun for task: {task.title}", "info"
            )

        # Create TaskRun using factory
        task_run = self._domain_factory.create_task_run(
            task=task,
            team=team,
            prompt_builder=self._prompt_builder,
            stream=stream,
            debug=debug,
            tool_streaming=tool_streaming,
            stream_merger=stream_merger,
            session_id=session_id,
            account_id=account_id
        )

        if verbose:
            self._display_service.display_status(
                f"TaskRun created for agent: {task_run.agent.name}", "info"
            )

        return task_run

    async def _execute_task(
        self,
        task_run,
        task_id: int,
        provider: str,
        database_url: Optional[str],
        stream: bool,
        verbose: bool
    ):
        """
        Execute task using TaskExecutor service.

        TaskExecutor handles:
        - Status updates (pending → in_progress → completed/failed)
        - Agent execution via runner
        - Result storage in database

        Args:
            task_run: TaskRun domain object
            task_id: Task ID for display
            provider: LLM provider
            database_url: Database URL
            stream: Enable streaming
            verbose: Enable verbose output
        """
        self._logger.debug(f"Starting task execution via TaskExecutor: task_id={task_id}")

        self._display_service.display_status(
            f"🎯 Executing task #{task_id}: {task_run.task.title}", "info"
        )
        self._display_service.display_status(
            f"📋 Agent: {task_run.agent.name} ({task_run.agent.id})", "info"
        )

        try:
            if stream:
                # Execute with streaming
                if verbose:
                    self._display_service.display_status(
                        "Streaming task execution...", "info"
                    )

                async for event in self._task_executor.execute_task_stream(
                    task_run=task_run,
                    provider=provider,
                    database_url=database_url
                ):
                    # Events are handled by the event display system
                    # in the ExecutionService layer
                    pass

                if verbose:
                    self._display_service.display_status(
                        f"Task #{task_id} streaming execution completed", "success"
                    )
            else:
                # Execute in batch mode
                if verbose:
                    self._display_service.display_status(
                        "Executing task in batch mode...", "info"
                    )

                with self._display_service.show_progress("Processing task...") as progress:
                    task = progress.add_task("Processing...", total=None)
                    result = await self._task_executor.execute_task(
                        task_run=task_run,
                        provider=provider,
                        database_url=database_url
                    )
                    progress.update(task, completed=True)

                if verbose:
                    self._display_service.display_status(
                        f"Task #{task_id} batch execution completed", "success"
                    )
                    if result.output:
                        self._display_service.display_final_result(str(result.output))

        except Exception as e:
            self._logger.error(f"Task execution failed: {e}")
            raise

    async def _execute_async(
        self,
        team_config: Path,
        task_id: int,
        account_id: int,
        provider: str,
        database_url: Optional[str],
        session_id: Optional[str],
        debug: bool,
        tool_streaming: bool,
        stream_merger: str,
        verbose: bool
    ) -> None:
        """
        Execute task asynchronously via queue.

        Args:
            team_config: Path to team YAML
            task_id: Task ID to execute
            account_id: Account ID
            provider: LLM provider
            database_url: Database URL
            session_id: Session ID
            debug: Debug mode
            tool_streaming: Tool streaming enabled
            stream_merger: Stream merger strategy
            verbose: Verbose output
        """
        self._display_service.display_status(
            f"🚀 Dispatching task #{task_id} to async queue", "info"
        )

        # Get database URL (use provided or from environment)
        db_url = database_url or get_database_url()

        # Dispatch to queue
        message_id = await self._message_dispatcher.dispatch_task_execution(
            task_id=task_id,
            account_id=account_id,
            team_config_path=str(team_config),
            provider=provider,
            session_id=session_id,
            database_url=db_url,
            debug=debug,
            tool_streaming=tool_streaming,
            stream_merger=stream_merger
        )

        if verbose:
            self._display_service.display_status(
                f"Message ID: {message_id}", "info"
            )

        self._display_service.display_status(
            f"✅ Task #{task_id} dispatched to queue (message: {message_id})",
            "success"
        )
        self._display_service.display_status(
            "📊 Task will be processed asynchronously by worker", "info"
        )
        self._display_service.display_status(
            "💡 Monitor progress: http://localhost:5555 (Flower UI)", "info"
        )
