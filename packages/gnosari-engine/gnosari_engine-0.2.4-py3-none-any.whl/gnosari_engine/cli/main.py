#!/usr/bin/env python3
"""
Gnosari Engine CLI - Enterprise-grade command line interface following SOLID principles
"""

import asyncio
from pathlib import Path
from typing import Optional

import click

from .services import (
    ConfigurationLoader,
    ExecutionService,
    DisplayService,
    SessionManager,
    DomainFactory
)
from .commands import RunCommand, StatusCommand, VersionCommand, KnowledgeSetupCommand, KnowledgeCommand, ViewCommand, LearnCommand, PushCommand, TaskRunCommand, StartCommand
from .logging_config import create_default_logging_configurator
from ..prompts.agent_prompt_builder import AgentPromptBuilder


class CLIApplication:
    """
    Main CLI Application following Dependency Inversion Principle
    All dependencies are injected, making it testable and extensible
    """
    
    def __init__(self):
        # Dependency injection following SOLID principles
        self._display_service = DisplayService()
        self._config_loader = ConfigurationLoader()  # With env substitution for run commands
        self._config_loader_no_subst = ConfigurationLoader(skip_env_substitution=True)  # Without substitution for push
        self._execution_service = ExecutionService()
        self._session_manager = SessionManager()
        self._domain_factory = DomainFactory()
        self._logging_configurator = create_default_logging_configurator()
        
        # Command objects with injected dependencies
        self._run_command = RunCommand(
            config_loader=self._config_loader,
            execution_service=self._execution_service,
            display_service=self._display_service,
            session_manager=self._session_manager,
            domain_factory=self._domain_factory,
            logging_configurator=self._logging_configurator
        )
        
        self._status_command = StatusCommand(
            display_service=self._display_service
        )
        
        self._version_command = VersionCommand(
            display_service=self._display_service
        )
        
        self._knowledge_setup_command = KnowledgeSetupCommand(
            display_service=self._display_service
        )
        
        self._knowledge_command = KnowledgeCommand(
            config_loader=self._config_loader,
            display_service=self._display_service,
            domain_factory=self._domain_factory,
            logging_configurator=self._logging_configurator
        )

        self._view_command = ViewCommand(
            config_loader=self._config_loader,
            display_service=self._display_service,
            domain_factory=self._domain_factory
        )
        
        # Learning command with required dependencies
        from ..learning import LearningService, TeacherAgentFactory
        
        # Note: SessionRepository will be created dynamically in the learn command
        # since it requires database connection details that are provided at runtime
        learning_service = LearningService()
        teacher_agent_factory = TeacherAgentFactory()
        
        self._learn_command = LearnCommand(
            config_loader=self._config_loader,
            display_service=self._display_service,
            session_manager=self._session_manager,
            domain_factory=self._domain_factory,
            logging_configurator=self._logging_configurator,
            learning_service=learning_service,
            teacher_agent_factory=teacher_agent_factory,
            session_repository=None  # Will be created dynamically
        )
        
        self._push_command = PushCommand(
            config_loader=self._config_loader_no_subst,  # Use loader without env substitution
            display_service=self._display_service,
            logging_configurator=self._logging_configurator
        )

        # Task run command with all required dependencies
        # Note: TaskRunCommand uses TaskExecutor service internally
        # instead of ExecutionService for better separation of concerns
        self._prompt_builder = AgentPromptBuilder()
        self._task_run_command = TaskRunCommand(
            config_loader=self._config_loader,
            display_service=self._display_service,
            session_manager=self._session_manager,
            domain_factory=self._domain_factory,
            logging_configurator=self._logging_configurator,
            prompt_builder=self._prompt_builder
        )

        # Start command for queue worker
        self._start_command = StartCommand(
            display_service=self._display_service
        )

    async def run_agent(
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
        """Execute run command through command object"""
        await self._run_command.execute(
            team_config=team_config,
            message=message,
            agent=agent,
            session_id=session_id,
            stream=stream,
            debug=debug,
            provider=provider,
            database_url=database_url,
            verbose=verbose,
            log_level=log_level,
            log_file=log_file,
            structured_logs=structured_logs,
            tool_streaming=tool_streaming,
            stream_merger=stream_merger
        )
    
    def show_status(self) -> None:
        """Execute status command through command object"""
        self._status_command.execute()
    
    def show_version(self) -> None:
        """Execute version command through command object"""
        self._version_command.execute()
    
    async def setup_knowledge(
        self,
        host: str = "localhost",
        port: int = 9200,
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_ssl: bool = False,
        verify_certs: bool = False,
        force: bool = False,
        no_sample_data: bool = False,
        no_hybrid: bool = False
    ) -> None:
        """Execute knowledge setup command through command object"""
        await self._knowledge_setup_command.execute(
            host=host,
            port=port,
            username=username,
            password=password,
            use_ssl=use_ssl,
            verify_certs=verify_certs,
            force=force,
            no_sample_data=no_sample_data,
            no_hybrid=no_hybrid
        )
    
    async def view_team_config(
        self,
        team_config: Path,
        format: str = "tree",
        show_raw: bool = False,
        verbose: bool = False
    ) -> None:
        """Execute view command through command object"""
        await self._view_command.execute(
            team_config=team_config,
            format=format,
            show_raw=show_raw,
            verbose=verbose
        )
    
    async def learn_agent(
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
        """Execute learn command through command object"""
        await self._learn_command.execute(
            team_config=team_config,
            agent_id=agent_id,
            session_id=session_id,
            provider=provider,
            database_url=database_url,
            debug=debug,
            verbose=verbose,
            log_level=log_level,
            log_file=log_file,
            structured_logs=structured_logs,
            max_sessions=max_sessions
        )
    
    async def load_knowledge(
        self,
        team_config: Path,
        agent_id: Optional[str] = None,
        provider: str = "opensearch",
        force_reload: bool = False,
        debug: bool = False,
        verbose: bool = False,
        log_level: Optional[str] = None,
        log_file: Optional[str] = None,
        structured_logs: bool = False
    ) -> None:
        """Execute knowledge load command through command object"""
        await self._knowledge_command.load(
            team_config=team_config,
            agent_id=agent_id,
            provider=provider,
            force_reload=force_reload,
            debug=debug,
            verbose=verbose,
            log_level=log_level,
            log_file=log_file,
            structured_logs=structured_logs
        )
    
    async def push_team(
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
        """Execute push command through command object"""
        await self._push_command.execute(
            team_config=team_config,
            api_url=api_url,
            api_key=api_key,
            debug=debug,
            verbose=verbose,
            log_level=log_level,
            log_file=log_file,
            structured_logs=structured_logs
        )

    async def run_task(
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
        """Execute task run command through command object"""
        await self._task_run_command.execute(
            team_config=team_config,
            task_id=task_id,
            session_id=session_id,
            stream=stream,
            debug=debug,
            provider=provider,
            database_url=database_url,
            verbose=verbose,
            log_level=log_level,
            log_file=log_file,
            structured_logs=structured_logs,
            tool_streaming=tool_streaming,
            stream_merger=stream_merger,
            async_mode=async_mode
        )

    async def start_worker(
        self,
        concurrency: int = 4,
        queue: str = "task_execution",
        log_level: str = "INFO"
    ) -> None:
        """Start queue worker through command object"""
        await self._start_command.execute(
            concurrency=concurrency,
            queue=queue,
            log_level=log_level
        )

    def show_header_only(self) -> None:
        """Show header when no command specified"""
        self._display_service.display_header()
        self._display_service.display_status(
            "Use 'gnosari --help' to see available commands", 
            "warning"
        )


# Global application instance (Singleton pattern for CLI)
app = CLIApplication()


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(version="1.0.0", prog_name="gnosari")
def cli(ctx):
    """
    Gnosari Engine - Enterprise-grade AI Agent Team Orchestration
    
    Run multi-agent teams with advanced orchestration capabilities.
    """
    if ctx.invoked_subcommand is None:
        app.show_header_only()


@cli.command()
@click.argument('team_config', type=click.Path(exists=True, path_type=Path))
@click.option('-m', '--message', 
              required=True,
              help='Message to send to the team or agent')
@click.option('-a', '--agent', 
              default=None,
              help='Specific agent ID to run (runs entire team if not specified)')
@click.option('-s', '--session-id',
              default=None,
              help='Session ID for conversation persistence')
@click.option('--stream/--no-stream',
              default=True,
              help='Enable/disable streaming output (default: enabled)')
@click.option('--debug/--no-debug',
              default=False,
              help='Enable/disable debug mode (default: disabled)')
@click.option('--provider',
              default='openai',
              type=click.Choice(['openai', 'claude', 'anthropic', 'deepseek', 'google']),
              help='LLM provider to use (default: openai)')
@click.option('--database-url',
              default=None,
              help='Database URL for session persistence')
@click.option('-v', '--verbose',
              is_flag=True,
              help='Enable verbose output')
@click.option('--log-level',
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], case_sensitive=False),
              help='Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
@click.option('--log-file',
              type=click.Path(),
              help='Path to log file for persistent logging')
@click.option('--structured-logs',
              is_flag=True,
              help='Enable structured JSON logging format')
@click.option('--tool-streaming/--no-tool-streaming',
              default=True,
              help='Enable/disable tool streaming (default: enabled)')
@click.option('--stream-merger',
              default='time_ordered',
              type=click.Choice(['basic', 'time_ordered', 'priority']),
              help='Stream merger type for tool events (default: time_ordered)')
def run(team_config: Path, 
        message: str, 
        agent: Optional[str], 
        session_id: Optional[str],
        stream: bool,
        debug: bool,
        provider: str,
        database_url: Optional[str],
        verbose: bool,
        log_level: Optional[str],
        log_file: Optional[str],
        structured_logs: bool,
        tool_streaming: bool,
        stream_merger: str):
    """
    Run a Gnosari team or individual agent
    
    Examples:
    
        Run entire team:
        $ gnosari run teams/my_team.yaml -m "Hello team!"
        
        Run specific agent:
        $ gnosari run teams/my_team.yaml -m "Hello agent!" -a ceo
        
        With session persistence:
        $ gnosari run teams/my_team.yaml -m "Continue our discussion" -s session-001
    """
    try:
        asyncio.run(app.run_agent(
            team_config=team_config,
            message=message,
            agent=agent,
            session_id=session_id,
            stream=stream,
            debug=debug,
            provider=provider,
            database_url=database_url,
            verbose=verbose,
            log_level=log_level,
            log_file=log_file,
            structured_logs=structured_logs,
            tool_streaming=tool_streaming,
            stream_merger=stream_merger
        ))
    except KeyboardInterrupt:
        click.echo("\n⚠ Execution interrupted by user", err=True)
        raise click.Abort()


@cli.command()
def status():
    """Check system status and configuration"""
    app.show_status()


@cli.command()
def version():
    """Display version information"""
    app.show_version()


@cli.command()
@click.argument('team_config', type=click.Path(exists=True, path_type=Path))
@click.option('--format', '-f',
              type=click.Choice(['tree', 'json', 'table', 'chart']),
              default='tree',
              help='Display format (tree, json, table, or chart)')
@click.option('--show-raw',
              is_flag=True,
              help='Show raw object representation in JSON format')
@click.option('-v', '--verbose',
              is_flag=True,
              help='Show detailed information including metadata and internal properties')
def view(team_config: Path, format: str, show_raw: bool, verbose: bool):
    """
    View comprehensive team configuration details
    
    This command loads and displays all team configuration details including:
    - Team metadata and properties
    - Agent configurations with tools and knowledge bases
    - Delegation/handoff relationships
    - Tools and their configurations
    - Knowledge base setups
    
    Examples:
    
        View team in tree format (default):
        $ gnosari view teams/my_team.yaml
        
        View as formatted JSON:
        $ gnosari view teams/my_team.yaml --format json
        
        View as tables:
        $ gnosari view teams/my_team.yaml --format table
        
        View as flow chart:
        $ gnosari view teams/my_team.yaml --format chart
        
        Show all details with verbose mode:
        $ gnosari view teams/my_team.yaml -v
        
        Show raw object representation:
        $ gnosari view teams/my_team.yaml --format json --show-raw
    """
    try:
        asyncio.run(app.view_team_config(
            team_config=team_config,
            format=format,
            show_raw=show_raw,
            verbose=verbose
        ))
    except KeyboardInterrupt:
        click.echo("\n⚠ View operation interrupted by user", err=True)
        raise click.Abort()


@cli.group()
def knowledge():
    """Knowledge base management commands"""
    pass


@knowledge.command()
@click.option('--host', default=None, help='OpenSearch host (defaults to OPENSEARCH_HOST env var or localhost)')
@click.option('--port', type=int, default=None, help='OpenSearch port (defaults to OPENSEARCH_PORT env var or 9200)')
@click.option('--username', help='OpenSearch username (defaults to OPENSEARCH_USERNAME env var)')
@click.option('--password', help='OpenSearch password (defaults to OPENSEARCH_PASSWORD env var)')
@click.option('--use-ssl', is_flag=True, default=None, help='Use SSL connection (defaults to OPENSEARCH_USE_SSL env var or false)')
@click.option('--verify-certs', is_flag=True, default=None, help='Verify SSL certificates (defaults to OPENSEARCH_VERIFY_CERTS env var or false)')
@click.option('--force', '-f', is_flag=True, help='Force recreate existing resources')
@click.option('--no-sample-data', is_flag=True, help='Skip sample data ingestion')
@click.option('--no-hybrid', is_flag=True, help='Disable hybrid search setup')
def setup(host: Optional[str], port: Optional[int], username: Optional[str], password: Optional[str],
          use_ssl: Optional[bool], verify_certs: Optional[bool], force: bool, no_sample_data: bool, no_hybrid: bool):
    """
    Set up OpenSearch for semantic search with OpenAI embeddings.
    
    This command creates a complete OpenSearch semantic search setup including:
    - OpenAI embedding model connector
    - Model group and deployment
    - Ingest pipeline for automatic text embedding
    - Search pipeline for hybrid search (optional)
    - Vector index optimized for semantic search
    - Sample data ingestion for testing
    
    Examples:
    
        Basic setup with defaults:
        $ gnosari knowledge setup
        
        Custom host and force recreation:
        $ gnosari knowledge setup --host my-opensearch.com --force
        
        Skip sample data and hybrid search:
        $ gnosari knowledge setup --no-sample-data --no-hybrid
        
        With authentication:
        $ gnosari knowledge setup --username admin --password secret --use-ssl
    """
    try:
        asyncio.run(app.setup_knowledge(
            host=host,
            port=port,
            username=username,
            password=password,
            use_ssl=use_ssl,
            verify_certs=verify_certs,
            force=force,
            no_sample_data=no_sample_data,
            no_hybrid=no_hybrid
        ))
    except KeyboardInterrupt:
        click.echo("\n⚠ Setup interrupted by user", err=True)
        raise click.Abort()


@knowledge.command()
@click.argument('team_config', type=click.Path(exists=True, path_type=Path))
@click.option('-a', '--agent', 
              default=None,
              help='Specific agent ID to load knowledge for (loads all agents if not specified)')
@click.option('--provider',
              default='opensearch',
              type=click.Choice(['opensearch']),
              help='Knowledge provider to use (currently only opensearch is supported)')
@click.option('--force-reload', '-f',
              is_flag=True,
              help='Force reload existing knowledge bases')
@click.option('--debug/--no-debug',
              default=False,
              help='Enable/disable debug mode (default: disabled)')
@click.option('-v', '--verbose',
              is_flag=True,
              help='Enable verbose output with progress updates')
@click.option('--log-level',
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], case_sensitive=False),
              help='Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
@click.option('--log-file',
              type=click.Path(),
              help='Path to log file for persistent logging')
@click.option('--structured-logs',
              is_flag=True,
              help='Enable structured JSON logging format')
def load(team_config: Path, 
         agent: Optional[str],
         provider: str,
         force_reload: bool,
         debug: bool,
         verbose: bool,
         log_level: Optional[str],
         log_file: Optional[str],
         structured_logs: bool):
    """
    Load knowledge sources from team configuration into knowledge bases.

    This command processes knowledge sources defined in team configurations
    and loads them into OpenSearch knowledge provider.

    Examples:

        Load all knowledge sources for all agents:
        $ gnosari knowledge load teams/my_team.yaml

        Load knowledge sources for specific agent:
        $ gnosari knowledge load teams/my_team.yaml -a ceo

        Force reload existing knowledge bases:
        $ gnosari knowledge load teams/my_team.yaml --force-reload

        Load with verbose output:
        $ gnosari knowledge load teams/my_team.yaml -v

        Load with debug logging to file:
        $ gnosari knowledge load teams/my_team.yaml --debug --log-file knowledge.log
    """
    try:
        asyncio.run(app.load_knowledge(
            team_config=team_config,
            agent_id=agent,
            provider=provider,
            force_reload=force_reload,
            debug=debug,
            verbose=verbose,
            log_level=log_level,
            log_file=log_file,
            structured_logs=structured_logs
        ))
    except KeyboardInterrupt:
        click.echo("\n⚠ Knowledge loading interrupted by user", err=True)
        raise click.Abort()

@cli.command()
@click.argument('team_config', type=click.Path(exists=True, path_type=Path))
@click.option('-a', '--agent', 'agent_id',
              required=True,
              help='Agent ID to generate learning for')
@click.option('-s', '--session-id',
              default=None,
              help='Session ID to analyze for learning (if not provided, analyzes all sessions)')
@click.option('--provider',
              default='openai',
              type=click.Choice(['openai', 'claude', 'anthropic', 'deepseek', 'google']),
              help='LLM provider to use (default: openai)')
@click.option('--database-url',
              default=None,
              help='Database URL for session persistence')
@click.option('--debug/--no-debug',
              default=False,
              help='Enable/disable debug mode (default: disabled)')
@click.option('-v', '--verbose',
              is_flag=True,
              help='Enable verbose output')
@click.option('--log-level',
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], case_sensitive=False),
              help='Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
@click.option('--log-file',
              type=click.Path(),
              help='Path to log file for persistent logging')
@click.option('--structured-logs',
              is_flag=True,
              help='Enable structured JSON logging format')
@click.option('--max-sessions',
              default=10,
              type=int,
              help='Maximum number of session messages to analyze (default: 10)')
def learn(team_config: Path,
          agent_id: str,
          session_id: Optional[str],
          provider: str,
          database_url: Optional[str],
          debug: bool,
          verbose: bool,
          log_level: Optional[str],
          log_file: Optional[str],
          structured_logs: bool,
          max_sessions: int):
    """
    Generate learning insights for an agent from session history
    
    This command analyzes previous session messages to help agents improve
    their performance through AI-generated learning content.
    
    Examples:
    
        Learn from a specific session:
        $ gnosari learn teams/my_team.yaml -a ceo -s session-001
        
        Learn from all sessions (when no session-id provided):
        $ gnosari learn teams/my_team.yaml -a ceo
        
        
        Analyze more messages with verbose output:
        $ gnosari learn teams/my_team.yaml -a ceo --max-sessions 20 -v
        
        Use different provider:
        $ gnosari learn teams/my_team.yaml -a ceo --provider anthropic
    """
    try:
        asyncio.run(app.learn_agent(
            team_config=team_config,
            agent_id=agent_id,
            session_id=session_id,
            provider=provider,
            database_url=database_url,
            debug=debug,
            verbose=verbose,
            log_level=log_level,
            log_file=log_file,
            structured_logs=structured_logs,
            max_sessions=max_sessions
        ))
    except KeyboardInterrupt:
        click.echo("\n⚠ Learning interrupted by user", err=True)
        raise click.Abort()


@cli.command()
@click.argument('team_config', type=click.Path(exists=True, path_type=Path))
@click.option('--api-url',
              default=None,
              help='Gnosari API URL (defaults to GNOSARI_API_URL environment variable)')
@click.option('--api-key',
              default=None,
              help='Gnosari API key (defaults to GNOSARI_API_KEY environment variable)')
@click.option('--debug/--no-debug',
              default=False,
              help='Enable/disable debug mode (default: disabled)')
@click.option('-v', '--verbose',
              is_flag=True,
              help='Enable verbose output')
@click.option('--log-level',
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], case_sensitive=False),
              help='Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
@click.option('--log-file',
              type=click.Path(),
              help='Path to log file for persistent logging')
@click.option('--structured-logs',
              is_flag=True,
              help='Enable structured JSON logging format')
def push(team_config: Path,
         api_url: Optional[str],
         api_key: Optional[str],
         debug: bool,
         verbose: bool,
         log_level: Optional[str],
         log_file: Optional[str],
         structured_logs: bool):
    """
    Push team configuration to Gnosari API

    This command uploads a team configuration to the Gnosari API, creating or
    updating the team with all its agents, tools, knowledge sources, and traits.

    Examples:

        Push team with default API settings:
        $ gnosari push teams/my_team.yaml

        Push with custom API URL:
        $ gnosari push teams/my_team.yaml --api-url https://api.gnosari.com

        Push with verbose output:
        $ gnosari push teams/my_team.yaml -v

        Push with debug logging:
        $ gnosari push teams/my_team.yaml --debug --log-file push.log
    """
    try:
        asyncio.run(app.push_team(
            team_config=team_config,
            api_url=api_url,
            api_key=api_key,
            debug=debug,
            verbose=verbose,
            log_level=log_level,
            log_file=log_file,
            structured_logs=structured_logs
        ))
    except KeyboardInterrupt:
        click.echo("\n⚠ Push interrupted by user", err=True)
        raise click.Abort()


@cli.command()
@click.option('--concurrency', '-c',
              default=4,
              type=int,
              help='Number of concurrent worker processes (default: 4)')
@click.option('--queue', '-q',
              default='task_execution',
              help='Queue name to consume from (default: task_execution)')
@click.option('--log-level',
              default='INFO',
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR'], case_sensitive=False),
              help='Logging level (default: INFO)')
def start(concurrency: int, queue: str, log_level: str):
    """
    Start the queue worker/consumer process

    This command starts a Celery worker that processes asynchronous task execution
    messages from the queue. The worker will display received messages and their
    execution status in a user-friendly way.

    Examples:

        Start worker with default settings:
        $ gnosari start

        Start with custom concurrency:
        $ gnosari start --concurrency 8

        Start with debug logging:
        $ gnosari start --log-level DEBUG

        Start consuming from custom queue:
        $ gnosari start --queue priority_queue
    """
    try:
        asyncio.run(app.start_worker(
            concurrency=concurrency,
            queue=queue,
            log_level=log_level
        ))
    except KeyboardInterrupt:
        click.echo("\n🛑 Worker stopped by user", err=True)
        raise click.Abort()


@cli.group()
def task():
    """Task management commands"""
    pass


@task.command()
@click.argument('team_config', type=click.Path(exists=True, path_type=Path))
@click.option('--task-id', '-t',
              required=True,
              type=int,
              help='Task ID to execute')
@click.option('-s', '--session-id',
              default=None,
              help='Session ID for conversation persistence')
@click.option('--stream/--no-stream',
              default=False,
              help='Enable/disable streaming output (default: disabled for tasks)')
@click.option('--debug/--no-debug',
              default=False,
              help='Enable/disable debug mode (default: disabled)')
@click.option('--provider',
              default='openai',
              type=click.Choice(['openai', 'claude', 'anthropic', 'deepseek', 'google']),
              help='LLM provider to use (default: openai)')
@click.option('--database-url',
              default=None,
              help='Database URL for task loading and session persistence')
@click.option('-v', '--verbose',
              is_flag=True,
              help='Enable verbose output')
@click.option('--log-level',
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], case_sensitive=False),
              help='Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
@click.option('--log-file',
              type=click.Path(),
              help='Path to log file for persistent logging')
@click.option('--structured-logs',
              is_flag=True,
              help='Enable structured JSON logging format')
@click.option('--tool-streaming/--no-tool-streaming',
              default=True,
              help='Enable/disable tool streaming (default: enabled)')
@click.option('--stream-merger',
              default='time_ordered',
              type=click.Choice(['basic', 'time_ordered', 'priority']),
              help='Stream merger type for tool events (default: time_ordered)')
@click.option('--async/--no-async', 'async_',
              default=False,
              help='Execute task asynchronously via queue (requires worker running)')
def run(team_config: Path,
        task_id: int,
        session_id: Optional[str],
        stream: bool,
        debug: bool,
        provider: str,
        database_url: Optional[str],
        verbose: bool,
        log_level: Optional[str],
        log_file: Optional[str],
        structured_logs: bool,
        tool_streaming: bool,
        stream_merger: str,
        async_: bool):
    """
    Execute a task by ID using the assigned agent

    This command loads a task from the database, finds the assigned agent
    in the team configuration, and executes the task with proper context.

    Examples:

        Execute task with ID 123:
        $ gnosari task run test_team_config.yaml --task-id 123

        Execute with custom database URL:
        $ gnosari task run test_team_config.yaml -t 123 --database-url postgresql://...

        Execute with session persistence:
        $ gnosari task run test_team_config.yaml -t 123 -s session-001

        Execute with verbose output:
        $ gnosari task run test_team_config.yaml -t 123 -v

        Execute with different provider:
        $ gnosari task run test_team_config.yaml -t 123 --provider anthropic
    """
    try:
        asyncio.run(app.run_task(
            team_config=team_config,
            task_id=task_id,
            session_id=session_id,
            stream=stream,
            debug=debug,
            provider=provider,
            database_url=database_url,
            verbose=verbose,
            log_level=log_level,
            log_file=log_file,
            structured_logs=structured_logs,
            tool_streaming=tool_streaming,
            stream_merger=stream_merger,
            async_mode=async_
        ))
    except KeyboardInterrupt:
        click.echo("\n⚠ Task execution interrupted by user", err=True)
        raise click.Abort()


def main():
    """
    Main entry point for the CLI
    
    This follows the Single Responsibility Principle:
    - Just delegates to Click's CLI handler
    - No business logic here
    """
    cli()


if __name__ == "__main__":
    main()