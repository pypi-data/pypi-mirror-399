"""
Knowledge Loader Service - Clean library interface for loading knowledge bases
"""

import logging
import time
from pathlib import Path
from typing import Any, Callable, Optional, Protocol

from ...schemas.domain.knowledge import Knowledge
from ...schemas.domain.team import Team
from ..factories.knowledge_factory import KnowledgeProviderFactory
from ..interfaces import IKnowledgeProvider, IKnowledgeBase
from ..components import LoadingProgress, KnowledgeStatus
from ..streaming import (
    EventEmitter,
    KnowledgeEventCallback,
    KnowledgeEventType,
    KnowledgeBaseLoadStartEvent,
    KnowledgeBaseLoadCompleteEvent,
    KnowledgeBaseLoadErrorEvent,
    LoadingProgressEvent
)


class ProgressCallback(Protocol):
    """Protocol for progress callback functions."""
    
    def __call__(self, progress: LoadingProgress) -> None:
        """Called with progress updates during loading."""
        ...


class KnowledgeLoaderService:
    """
    Clean library interface for loading knowledge bases.
    
    This service provides a simple, reusable way to load knowledge sources
    that can be used both from CLI and as a library dependency.
    
    Example usage:
        ```python
        from gnosari_engine.knowledge.services import KnowledgeLoaderService
        
        # Basic usage
        loader = KnowledgeLoaderService()
        result = await loader.load_from_team_config(
            team_config_path="teams/my_team.yaml",
            agent_id="ceo"  # Optional - loads all agents if omitted
        )
        
        # With progress callback
        def on_progress(progress: LoadingProgress):
            print(f"Progress: {progress.progress_percentage:.1f}%")
        
        result = await loader.load_from_team_config(
            team_config_path="teams/my_team.yaml",
            progress_callback=on_progress,
            force_reload=True
        )
        ```
    """
    
    def __init__(
        self, 
        knowledge_factory: Optional[KnowledgeProviderFactory] = None,
        provider: str = "opensearch"
    ):
        """
        Initialize the knowledge loader service.
        
        Args:
            knowledge_factory: Optional factory for creating knowledge providers
            provider: Default provider to use (opensearch, embedchain, etc.)
        """
        self._knowledge_factory = knowledge_factory or KnowledgeProviderFactory()
        self._default_provider = provider
        self._logger = logging.getLogger(__name__)
    
    async def load_from_team_config(
        self,
        team_config_path: str | Path,
        agent_id: Optional[str] = None,
        provider: Optional[str] = None,
        force_reload: bool = False,
        event_callback: Optional[KnowledgeEventCallback] = None
    ) -> "KnowledgeLoadResult":
        """
        Load knowledge sources from a team configuration file.

        Args:
            team_config_path: Path to team configuration YAML file
            agent_id: Optional agent ID to load knowledge for (loads all if None)
            provider: Knowledge provider to use (defaults to configured provider)
            force_reload: Whether to force reload existing knowledge bases
            event_callback: Optional callback for strongly-typed event updates

        Returns:
            KnowledgeLoadResult with loading statistics and status

        Raises:
            FileNotFoundError: If team config file doesn't exist
            ValueError: If agent_id is specified but not found
            KnowledgeLoadError: If knowledge loading fails
        """
        team_config_path = Path(team_config_path)
        if not team_config_path.exists():
            raise FileNotFoundError(f"Team configuration not found: {team_config_path}")
        
        provider = provider or self._default_provider
        
        try:
            # Load team configuration
            from ...cli.services import ConfigurationLoader
            config_loader = ConfigurationLoader()
            team = config_loader.load_team_configuration(team_config_path)
            
            # Filter agents
            agents_to_process = self._filter_agents(team, agent_id)
            if not agents_to_process:
                if agent_id:
                    raise ValueError(f"Agent '{agent_id}' not found or has no knowledge sources")
                return KnowledgeLoadResult(
                    success=True,
                    total_agents=0,
                    total_knowledge_bases=0,
                    total_documents=0,
                    errors=[]
                )
            
            # Initialize provider
            knowledge_provider = await self._knowledge_factory.create_provider(provider)
            await knowledge_provider.initialize()
            
            # Load knowledge sources
            return await self._load_knowledge_sources(
                agents_to_process,
                knowledge_provider,
                force_reload,
                event_callback
            )
            
        except Exception as e:
            self._logger.error(f"Failed to load knowledge sources: {e}", exc_info=True)
            raise KnowledgeLoadError(f"Knowledge loading failed: {e}") from e
    
    async def load_from_knowledge_configs(
        self,
        knowledge_configs: list[Knowledge],
        provider: Optional[str] = None,
        force_reload: bool = False,
        event_callback: Optional[KnowledgeEventCallback] = None
    ) -> "KnowledgeLoadResult":
        """
        Load knowledge bases from a list of Knowledge configurations.

        Args:
            knowledge_configs: List of Knowledge domain objects
            provider: Knowledge provider to use
            force_reload: Whether to force reload existing knowledge bases
            event_callback: Optional callback for strongly-typed event updates

        Returns:
            KnowledgeLoadResult with loading statistics
        """
        provider = provider or self._default_provider

        try:
            # Initialize provider
            knowledge_provider = await self._knowledge_factory.create_provider(provider)
            await knowledge_provider.initialize()

            # Create event emitter
            event_emitter = EventEmitter(callback=event_callback)

            # Load each knowledge base
            total_documents = 0
            errors = []

            for i, knowledge_config in enumerate(knowledge_configs):
                # Emit loading progress event
                if event_emitter.has_callback:
                    progress_percent = (i / len(knowledge_configs)) * 100
                    event_emitter.emit(
                        KnowledgeEventType.LOADING_PROGRESS,
                        LoadingProgressEvent(
                            completed_sources=i,
                            total_sources=len(knowledge_configs),
                            documents_processed=total_documents,
                            current_source=knowledge_config.id,
                            progress_percent=progress_percent
                        )
                    )

                try:
                    doc_count = await self._load_single_knowledge_base(
                        knowledge_config,
                        knowledge_provider,
                        force_reload,
                        event_emitter
                    )
                    total_documents += doc_count
                except Exception as e:
                    error_msg = f"Failed to load knowledge base '{knowledge_config.id}': {e}"
                    errors.append(error_msg)
                    self._logger.error(error_msg)

            # Final progress update
            if event_emitter.has_callback:
                event_emitter.emit(
                    KnowledgeEventType.LOADING_PROGRESS,
                    LoadingProgressEvent(
                        completed_sources=len(knowledge_configs),
                        total_sources=len(knowledge_configs),
                        documents_processed=total_documents,
                        current_source="",
                        progress_percent=100.0
                    )
                )

            return KnowledgeLoadResult(
                success=len(errors) == 0,
                total_agents=1,  # Not applicable for direct config loading
                total_knowledge_bases=len(knowledge_configs),
                total_documents=total_documents,
                errors=errors
            )
            
        except Exception as e:
            self._logger.error(f"Failed to load knowledge configs: {e}", exc_info=True)
            raise KnowledgeLoadError(f"Knowledge loading failed: {e}") from e
    
    def _filter_agents(self, team: Team, agent_id: Optional[str]) -> list:
        """Filter agents based on agent_id and presence of knowledge sources."""
        if agent_id:
            target_agent = team.get_agent_by_id(agent_id)
            if not target_agent:
                return []
            
            if not hasattr(target_agent, 'knowledge') or not target_agent.knowledge:
                return []
            
            return [target_agent]
        else:
            return [
                agent for agent in team.agents 
                if hasattr(agent, 'knowledge') and agent.knowledge
            ]
    
    async def _load_knowledge_sources(
        self,
        agents: list,
        knowledge_provider: IKnowledgeProvider,
        force_reload: bool,
        event_callback: Optional[KnowledgeEventCallback]
    ) -> "KnowledgeLoadResult":
        """
        Load knowledge sources for all agents with deduplication.

        Collects all unique knowledge bases across all agents and loads each once,
        avoiding duplicate loading when multiple agents share the same knowledge base.
        """
        total_documents = 0
        errors = []

        # Create event emitter
        event_emitter = EventEmitter(callback=event_callback)

        # Deduplicate knowledge bases across all agents
        # Use dict to preserve order and store first occurrence
        unique_knowledge_bases: dict[str, Knowledge] = {}
        agents_per_kb: dict[str, list[str]] = {}  # Track which agents use each KB

        for agent in agents:
            for knowledge_config in agent.knowledge:
                kb_id = knowledge_config.id
                if kb_id not in unique_knowledge_bases:
                    unique_knowledge_bases[kb_id] = knowledge_config
                    agents_per_kb[kb_id] = []
                agents_per_kb[kb_id].append(agent.id)

        total_kb_count = len(unique_knowledge_bases)
        processed_kb_count = 0

        self._logger.info(
            f"Loading {total_kb_count} unique knowledge bases "
            f"(used by {len(agents)} agents, {sum(len(agent.knowledge) for agent in agents)} total references)"
        )

        # Load each unique knowledge base once
        for kb_id, knowledge_config in unique_knowledge_bases.items():
            # Emit loading progress event
            if event_emitter.has_callback:
                progress_percent = (processed_kb_count / total_kb_count) * 100
                agent_list = ", ".join(agents_per_kb[kb_id])
                event_emitter.emit(
                    KnowledgeEventType.LOADING_PROGRESS,
                    LoadingProgressEvent(
                        completed_sources=processed_kb_count,
                        total_sources=total_kb_count,
                        documents_processed=total_documents,
                        current_source=f"{kb_id} (used by: {agent_list})",
                        progress_percent=progress_percent
                    )
                )

            try:
                doc_count = await self._load_single_knowledge_base(
                    knowledge_config,
                    knowledge_provider,
                    force_reload,
                    event_emitter
                )
                total_documents += doc_count

                # Log which agents will use this knowledge base
                agent_names = ", ".join(agents_per_kb[kb_id])
                self._logger.info(
                    f"Knowledge base '{kb_id}' loaded with {doc_count} documents. "
                    f"Available to agents: {agent_names}"
                )

            except Exception as e:
                agent_list = ", ".join(agents_per_kb[kb_id])
                error_msg = f"Failed to load knowledge base '{kb_id}' (needed by agents: {agent_list}): {e}"
                errors.append(error_msg)
                self._logger.error(error_msg)

            processed_kb_count += 1

        # Final progress update
        if event_emitter.has_callback:
            event_emitter.emit(
                KnowledgeEventType.LOADING_PROGRESS,
                LoadingProgressEvent(
                    completed_sources=processed_kb_count,
                    total_sources=total_kb_count,
                    documents_processed=total_documents,
                    current_source="",
                    progress_percent=100.0
                )
            )

        return KnowledgeLoadResult(
            success=len(errors) == 0,
            total_agents=len(agents),
            total_knowledge_bases=total_kb_count,
            total_documents=total_documents,
            errors=errors
        )
    
    async def _load_single_knowledge_base(
        self,
        knowledge_config: Knowledge,
        knowledge_provider: IKnowledgeProvider,
        force_reload: bool,
        event_emitter: EventEmitter
    ) -> int:
        """Load a single knowledge base and return document count."""
        knowledge_id = knowledge_config.id
        start_time = time.time()

        try:
            # Emit knowledge base load start event
            if event_emitter.has_callback:
                event_emitter.emit(
                    KnowledgeEventType.KNOWLEDGE_BASE_LOAD_START,
                    KnowledgeBaseLoadStartEvent(
                        knowledge_base_id=knowledge_id,
                        knowledge_base_name=knowledge_config.name,
                        source_count=len(knowledge_config.data_sources)
                    )
                )

            # Get or create knowledge base
            knowledge_base = await knowledge_provider.get_knowledge_base(knowledge_id)
            if not knowledge_base:
                knowledge_base = await knowledge_provider.create_knowledge_base(knowledge_config)
                await knowledge_base.initialize()

            # Check if reload is needed
            if not force_reload:
                status = await knowledge_base.get_status()
                if status.document_count > 0:
                    self._logger.info(f"Knowledge base '{knowledge_id}' already loaded with {status.document_count} documents")

                    # Emit complete event
                    if event_emitter.has_callback:
                        duration = time.time() - start_time
                        event_emitter.emit(
                            KnowledgeEventType.KNOWLEDGE_BASE_LOAD_COMPLETE,
                            KnowledgeBaseLoadCompleteEvent(
                                knowledge_base_id=knowledge_id,
                                total_documents=0,
                                success=True,
                                duration_seconds=duration
                            )
                        )
                    return 0

            # Load data sources
            total_documents = 0
            for data_source in knowledge_config.data_sources:
                try:
                    doc_count = await knowledge_base.add_data_source(
                        data_source,
                        force_reload=force_reload,
                        event_emitter=event_emitter,  # Pass event emitter for progress tracking
                        metadata={
                            "knowledge_id": knowledge_config.id,
                            "knowledge_name": knowledge_config.name,
                            "source_type": knowledge_config.source_type
                        }
                    )
                    total_documents += doc_count
                    self._logger.info(f"Loaded {doc_count} documents from {data_source}")
                except Exception as e:
                    self._logger.error(f"Failed to load data source {data_source}: {e}")
                    raise

            # Emit knowledge base load complete event
            if event_emitter.has_callback:
                duration = time.time() - start_time
                event_emitter.emit(
                    KnowledgeEventType.KNOWLEDGE_BASE_LOAD_COMPLETE,
                    KnowledgeBaseLoadCompleteEvent(
                        knowledge_base_id=knowledge_id,
                        total_documents=total_documents,
                        success=True,
                        duration_seconds=duration
                    )
                )

            return total_documents

        except Exception as e:
            # Emit error event
            if event_emitter.has_callback:
                event_emitter.emit(
                    KnowledgeEventType.KNOWLEDGE_BASE_LOAD_ERROR,
                    KnowledgeBaseLoadErrorEvent(
                        knowledge_base_id=knowledge_id,
                        error_message=str(e),
                        error_type=type(e).__name__
                    )
                )
            raise


class KnowledgeLoadResult:
    """Result of knowledge loading operation."""
    
    def __init__(
        self,
        success: bool,
        total_agents: int,
        total_knowledge_bases: int,
        total_documents: int,
        errors: list[str]
    ):
        self.success = success
        self.total_agents = total_agents
        self.total_knowledge_bases = total_knowledge_bases
        self.total_documents = total_documents
        self.errors = errors
    
    @property
    def has_errors(self) -> bool:
        """Check if there were any errors during loading."""
        return len(self.errors) > 0
    
    def __str__(self) -> str:
        status = "Success" if self.success else "Partial failure"
        return (
            f"KnowledgeLoadResult({status}: "
            f"{self.total_documents} docs in {self.total_knowledge_bases} knowledge bases "
            f"for {self.total_agents} agents, {len(self.errors)} errors)"
        )


class KnowledgeLoadError(Exception):
    """Raised when knowledge loading fails."""
    pass


__all__ = [
    "KnowledgeLoaderService",
    "KnowledgeLoadResult", 
    "KnowledgeLoadError",
    "ProgressCallback",
]