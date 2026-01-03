"""
Runner interfaces following SOLID principles.
Defines contracts for team and agent execution providers.
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from enum import Enum
from typing import Any, Protocol, runtime_checkable

from ..schemas.domain.execution import AgentRun
from .events import StreamEvent, EventFactory


class ExecutionStatus(Enum):
    """Execution status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExecutionResult:
    """Base execution result."""

    def __init__(
        self,
        status: ExecutionStatus,
        output: str | None = None,
        error: str | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        self.status = status
        self.output = output
        self.error = error
        self.metadata = metadata or {}


@runtime_checkable
class Runnable(Protocol):
    """Protocol for objects that can be executed."""

    async def run(self) -> ExecutionResult:
        """Execute the runnable object."""
        ...


@runtime_checkable
class StreamableRunnable(Protocol):
    """Protocol for objects that can be executed with streaming."""

    async def run_stream(self) -> AsyncGenerator[StreamEvent, None]:
        """Execute with streaming events."""
        ...


class BaseRunner(ABC):
    """
    Abstract base runner following Single Responsibility Principle.
    Each runner implementation handles one specific execution provider.
    """

    def __init__(self, provider_name: str):
        self._provider_name = provider_name
        self._is_initialized = False

    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return self._provider_name

    @property
    def is_initialized(self) -> bool:
        """Check if runner is initialized."""
        return self._is_initialized

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the runner (Open/Closed Principle - extensible)."""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup resources."""
        pass

    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()


class AgentRunner(BaseRunner):
    """
    Interface for agent execution providers.
    Follows Interface Segregation Principle - focused on agent execution only.
    """

    @abstractmethod
    async def run_agent(self, agent_run: AgentRun) -> ExecutionResult:
        """
        Execute a single agent.

        Args:
            agent_run: Agent execution configuration

        Returns:
            ExecutionResult with status and output
        """
        pass

    @abstractmethod
    async def run_agent_stream(
        self, agent_run: AgentRun
    ) -> AsyncGenerator[StreamEvent, None]:
        """
        Execute agent with streaming support.

        Args:
            agent_run: Agent execution configuration

        Yields:
            StreamEvent objects during execution
        """
        pass




class UnifiedRunner(AgentRunner):
    """
    Interface for providers that support agent execution.
    Follows Dependency Inversion Principle - depends on abstractions.
    """

    pass


@runtime_checkable
class RunnerProvider(Protocol):
    """
    Protocol for runner provider factories.
    Follows Dependency Inversion Principle.
    """

    def create_agent_runner(self, **kwargs) -> AgentRunner:
        """Create an agent runner instance."""
        ...


    def create_unified_runner(self, **kwargs) -> UnifiedRunner:
        """Create a unified runner instance."""
        ...




@runtime_checkable
class IAgentRunner(Protocol):
    """Protocol focused solely on agent operations - Interface Segregation Principle."""
    
    async def run_agent(self, agent_run: AgentRun) -> ExecutionResult:
        """Execute agent synchronously."""
        ...
    
    async def run_agent_stream(
        self, agent_run: AgentRun
    ) -> AsyncGenerator[StreamEvent, None]:
        """Execute agent with streaming."""
        ...


@runtime_checkable
class IProviderManager(Protocol):
    """Protocol for provider lifecycle management - Interface Segregation Principle."""
    
    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        ...
    
    @property
    def is_initialized(self) -> bool:
        """Check if provider is initialized."""
        ...
    
    async def initialize(self, **config) -> None:
        """Initialize the provider with configuration."""
        ...
    
    async def cleanup(self) -> None:
        """Cleanup provider resources."""
        ...
    
    async def switch_provider(self, provider_name: str, **provider_config) -> None:
        """Switch to a different provider."""
        ...


@runtime_checkable
class ProviderStrategy(IAgentRunner, IProviderManager, Protocol):
    """
    Complete provider strategy protocol combining all focused interfaces.
    Follows Strategy Pattern and Interface Segregation Principle.
    """
    pass


class RunnerRegistry:
    """
    Registry for runner providers following Open/Closed Principle.
    Open for extension (new providers), closed for modification.
    """

    def __init__(self):
        self._providers: dict[str, RunnerProvider] = {}

    def register_provider(self, name: str, provider: RunnerProvider) -> None:
        """Register a new runner provider."""
        self._providers[name] = provider

    def get_provider(self, name: str) -> RunnerProvider | None:
        """Get a registered provider by name."""
        return self._providers.get(name)

    def list_providers(self) -> list[str]:
        """List all registered provider names."""
        return list(self._providers.keys())
