"""
Generic Gnosari Runner implementation.
Autodiscovers and delegates to provider strategies following SOLID principles.
"""

import logging
from collections.abc import AsyncGenerator

from ..schemas.domain.execution import AgentRun
from .interfaces import ExecutionResult, StreamEvent, IAgentRunner, IProviderManager, ProviderStrategy
from ..knowledge.factories.knowledge_factory import KnowledgeProviderFactory
from .factories.interfaces import IProviderFactory
from .runner_components import (
    RunnerConfiguration, 
    RunnerInitializer, 
    ProviderContextEnricher,
    RunnerConfigurationError
)
from ..tools.streaming.interfaces import IStreamableTool, IToolStreamContext
from ..tools.factories.tool_factory import AutoDiscoveryToolFactory

logger = logging.getLogger(__name__)


class GnosariRunnerError(Exception):
    """Gnosari runner specific errors."""
    pass

class GnosariRunner(IAgentRunner, IProviderManager):
    """
    Generic Gnosari Runner with provider autodiscovery.
    
    Follows SOLID Principles:
    - Single Responsibility: Orchestrates execution using specialized components
    - Open/Closed: Open for new providers via autodiscovery, closed for modification
    - Liskov Substitution: All providers implement ProviderStrategy protocol
    - Interface Segregation: Implements focused interfaces for different concerns
    - Dependency Inversion: Depends on abstractions and uses dependency injection
    
    Usage:
        # Simple usage - autodiscover provider
        runner = GnosariRunner("openai", api_key="sk-...")
        
        # Advanced usage - custom provider instance
        custom_provider = MyCustomProvider()
        runner = GnosariRunner(provider=custom_provider)
    """

    def __init__(
        self,
        provider_name: str | None = None,
        provider: ProviderStrategy | None = None,
        provider_factory: IProviderFactory | None = None,
        **provider_config
    ):
        try:
            # Create configuration object (Single Responsibility)
            config = RunnerConfiguration(
                provider_name=provider_name,
                provider=provider,
                provider_factory=provider_factory,
                **provider_config
            )

            # Inject specialized components (Dependency Injection)
            self._initializer = RunnerInitializer(config)
            self._context_enricher: ProviderContextEnricher | None = None
            self._knowledge_factory = KnowledgeProviderFactory()
            self._tool_factory = AutoDiscoveryToolFactory()

        except RunnerConfigurationError as e:
            raise GnosariRunnerError(str(e)) from e

    @property
    def provider_name(self) -> str:
        """Get the current provider name."""
        return self._initializer.provider_name

    @property
    def is_initialized(self) -> bool:
        """Check if runner is initialized."""
        return self._initializer.is_initialized

    async def initialize(self) -> None:
        """Initialize the runner and its provider."""
        await self._initializer.initialize()

        # Initialize context enricher once we have the provider name
        if self._context_enricher is None:
            self._context_enricher = ProviderContextEnricher(self.provider_name)

    async def cleanup(self) -> None:
        """Cleanup runner resources."""
        await self._initializer.cleanup()
        self._context_enricher = None

    async def run_agent(self, agent_run: AgentRun) -> ExecutionResult:
        """Execute agent synchronously."""
        await self._ensure_initialized()

        try:
            # Initialize knowledge bases if any are defined in the team
            if agent_run.team.knowledge:
                await self._initialize_knowledge_bases(agent_run.team.knowledge)

            return await self._initializer.provider.run_agent(agent_run)
        except Exception as e:
            raise GnosariRunnerError(f"Agent execution failed: {e}") from e

    async def run_agent_stream(
        self, agent_run: AgentRun
    ) -> AsyncGenerator[StreamEvent, None]:
        """Execute agent with streaming."""
        await self._ensure_initialized()

        try:
            # Initialize knowledge bases if any are defined in the team
            if agent_run.team.knowledge:
                await self._initialize_knowledge_bases(agent_run.team.knowledge)

            # Standard streaming
            async for event in self._run_standard_streaming(agent_run):
                yield event

        except Exception as e:
            # Use context enricher for consistent error event creation
            if self._context_enricher:
                yield self._context_enricher.create_error_event(e)
            else:
                yield StreamEvent("execution_error", {"error": str(e)})

    async def switch_provider(self, provider_name: str, **provider_config) -> None:
        """Switch to a different provider at runtime."""
        await self.cleanup()
        
        # Create new configuration and initializer
        try:
            config = RunnerConfiguration(
                provider_name=provider_name,
                provider=None,
                provider_factory=None,  # Will use default
                **provider_config
            )
            self._initializer = RunnerInitializer(config)
            
        except RunnerConfigurationError as e:
            raise GnosariRunnerError(f"Failed to switch provider: {e}") from e
        
        await self.initialize()

    async def _ensure_initialized(self) -> None:
        """Ensure the runner is initialized."""
        if not self.is_initialized:
            await self.initialize()

    async def _initialize_knowledge_bases(self, knowledge_bases: list) -> None:
        """Initialize knowledge bases with OpenSearch provider and load data sources."""
        logger.info(f"Starting knowledge base initialization for {len(knowledge_bases)} knowledge bases")
        
        try:
            # Import Knowledge model for conversion
            from ..schemas.domain.knowledge import Knowledge
            
            logger.debug("Creating OpenSearch provider...")
            # Create OpenSearch provider 
            provider = await self._knowledge_factory.create_provider(
                provider_type="opensearch"
            )
            
            logger.debug("Initializing OpenSearch provider...")
            # Initialize provider with configuration
            await provider.initialize()
            logger.info("OpenSearch provider initialized successfully")
            
            # Process each knowledge base configuration
            initialized_count = 0
            total_documents = 0
            
            for i, kb_config in enumerate(knowledge_bases):
                try:
                    logger.debug(f"Processing knowledge base {i+1}/{len(knowledge_bases)}: {type(kb_config)} - {kb_config}")
                    
                    # Check if already a Knowledge object or needs conversion
                    if isinstance(kb_config, Knowledge):
                        knowledge = kb_config
                        logger.debug(f"Knowledge base already parsed: {knowledge.id}")
                    else:
                        # Convert config dict to Knowledge domain object
                        knowledge = Knowledge.from_config(kb_config)
                        logger.debug(f"Converted config dict to Knowledge object: {knowledge.id}")
                    
                    logger.info(f"Initializing knowledge base: {knowledge.id} ({knowledge.name})")
                    
                    # Create knowledge base instance
                    logger.debug(f"Creating knowledge base instance for {knowledge.id}")
                    kb = await provider.create_knowledge_base(knowledge)
                    logger.debug(f"Initializing knowledge base instance for {knowledge.id}")
                    await kb.initialize()
                    logger.info(f"Knowledge base {knowledge.id} initialized successfully")
                    
                    # Check if data needs to be loaded
                    force_reload = getattr(kb_config, 'force_reload', False) if isinstance(kb_config, Knowledge) else kb_config.get("force_reload", False)
                    logger.debug(f"Found {len(knowledge.data_sources)} data sources for {knowledge.id}, force_reload: {force_reload}")
                    
                    # Check if index already has data (unless force reload)
                    if not force_reload:
                        try:
                            status = await kb.get_status()
                            if status.document_count > 0:
                                logger.info(f"Index gnosari_{knowledge.id} already contains {status.document_count} documents, skipping data loading")
                                total_documents += status.document_count
                                continue
                            else:
                                logger.info(f"Index gnosari_{knowledge.id} exists but is empty, loading data sources")
                        except Exception as status_error:
                            logger.debug(f"Could not get index status, proceeding with data loading: {status_error}")
                    
                    # Load data sources if index is empty or force reload is requested
                    for j, data_source in enumerate(knowledge.data_sources):
                        logger.info(f"Loading data source {j+1}/{len(knowledge.data_sources)}: {data_source}")
                        try:
                            indexed_count = await kb.add_data_source(
                                data_source,
                                force_reload=force_reload,
                                metadata={
                                    "knowledge_id": knowledge.id,
                                    "knowledge_name": knowledge.name,
                                    "source_type": knowledge.source_type
                                }
                            )
                            total_documents += indexed_count
                            logger.info(f"Successfully loaded {indexed_count} documents from {data_source}")
                        except Exception as ds_error:
                            logger.error(f"Failed to load data source {data_source}: {ds_error}", exc_info=True)
                            # Continue with other data sources
                            continue
                    
                    initialized_count += 1
                    logger.info(f"Knowledge base {knowledge.id} fully initialized")
                    
                except Exception as kb_error:
                    kb_id = getattr(kb_config, 'id', 'unknown') if isinstance(kb_config, Knowledge) else kb_config.get('id', 'unknown')
                    logger.error(f"Failed to initialize knowledge base {kb_id}: {kb_error}", exc_info=True)
                    # Continue with other knowledge bases
                    continue
            
            logger.info(f"Knowledge base initialization complete: {initialized_count}/{len(knowledge_bases)} successful with {total_documents} total documents")
            
        except Exception as e:
            logger.error(f"Critical failure in knowledge base initialization: {e}", exc_info=True)
            # Continue execution even if knowledge initialization fails
    
    async def _run_standard_streaming(self, agent_run: AgentRun) -> AsyncGenerator[StreamEvent, None]:
        """Execute agent with standard streaming."""
        async for event in self._get_agent_stream(agent_run):
            # Enrich events if context enricher is available
            if self._context_enricher:
                enriched_event = self._context_enricher.enrich_event(event)
                yield enriched_event
            else:
                yield event

            # Break on completion events to ensure stream ends
            if event.event_type in ("agent_completed", "agent_error", "execution_completed"):
                logger.debug(f"Agent execution finished with event: {event.event_type}")
                break

    async def _get_agent_stream(self, agent_run: AgentRun) -> AsyncGenerator[StreamEvent, None]:
        """Get the base agent stream."""
        try:
            # Call the provider's stream method directly
            stream = self._initializer.provider.run_agent_stream(agent_run)
            async for event in stream:
                yield event
        except Exception as e:
            logger.error(f"Error in agent stream: {e}")
            yield StreamEvent("agent_error", {"error": str(e)})

    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()


