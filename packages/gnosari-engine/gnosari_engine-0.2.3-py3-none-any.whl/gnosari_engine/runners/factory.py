"""
Enterprise runner factory for creating configured runners with SOLID principles.

Provides factory methods for creating runners with appropriate capabilities
based on configuration requirements.
"""

import logging
from typing import Any, Union, TYPE_CHECKING

from ..schemas.domain.execution import ExecutionContext
from .gnosari_runner import GnosariRunner
from .interfaces import IAgentRunner, IProviderManager
from .streaming_enhanced_runner import StreamingEnhancedGnosariRunner

if TYPE_CHECKING:
    # For type checking, define a combined interface
    class EnterpriseRunner(IAgentRunner, IProviderManager):
        pass
else:
    # At runtime, use Union for compatibility
    EnterpriseRunner = Union[IAgentRunner, IProviderManager]

logger = logging.getLogger(__name__)


class RunnerFactory:
    """
    Factory for creating appropriate runner instances.
    
    Follows Factory Pattern and Open/Closed Principle:
    - Open for extension (new runner types)
    - Closed for modification (existing logic unchanged)
    """
    
    @staticmethod
    def create_runner(
        provider_name: str | None = None,
        provider=None,
        provider_factory=None,
        execution_context: ExecutionContext | None = None,
        **provider_config
    ) -> EnterpriseRunner:
        """
        Create appropriate runner based on configuration.
        
        Args:
            provider_name: Name of the provider to use
            provider: Direct provider instance
            provider_factory: Provider factory instance
            execution_context: Execution context with streaming configuration
            **provider_config: Additional provider configuration
            
        Returns:
            Configured runner instance
        """
        # Determine if tool streaming should be enabled
        enable_tool_streaming = RunnerFactory._should_enable_tool_streaming(execution_context)
        
        if enable_tool_streaming:
            # Create enhanced runner with tool streaming
            merger_type = execution_context.tool_streaming_merger if execution_context else "time_ordered"
            
            logger.info(f"Creating StreamingEnhancedGnosariRunner with merger: {merger_type}")
            return StreamingEnhancedGnosariRunner(
                provider_name=provider_name,
                provider=provider,
                provider_factory=provider_factory,
                enable_tool_streaming=True,
                stream_merger_type=merger_type,
                **provider_config
            )
        else:
            # Create standard runner
            logger.info("Creating standard GnosariRunner")
            return GnosariRunner(
                provider_name=provider_name,
                provider=provider,
                provider_factory=provider_factory,
                **provider_config
            )
    
    @staticmethod
    def create_streaming_runner(
        provider_name: str | None = None,
        provider=None,
        provider_factory=None,
        tool_streaming: bool = True,
        merger_type: str = "time_ordered",
        **provider_config
    ) -> StreamingEnhancedGnosariRunner:
        """
        Create enhanced runner with explicit streaming configuration.
        
        Args:
            provider_name: Name of the provider to use
            provider: Direct provider instance
            provider_factory: Provider factory instance
            tool_streaming: Enable tool streaming
            merger_type: Stream merger type (basic, time_ordered, priority)
            **provider_config: Additional provider configuration
            
        Returns:
            StreamingEnhancedGnosariRunner instance
        """
        logger.info(f"Creating explicit StreamingEnhancedGnosariRunner with tool_streaming={tool_streaming}")
        return StreamingEnhancedGnosariRunner(
            provider_name=provider_name,
            provider=provider,
            provider_factory=provider_factory,
            enable_tool_streaming=tool_streaming,
            stream_merger_type=merger_type,
            **provider_config
        )
    
    @staticmethod
    def create_basic_runner(
        provider_name: str | None = None,
        provider=None,
        provider_factory=None,
        **provider_config
    ) -> GnosariRunner:
        """
        Create basic runner without tool streaming.
        
        Args:
            provider_name: Name of the provider to use
            provider: Direct provider instance
            provider_factory: Provider factory instance
            **provider_config: Additional provider configuration
            
        Returns:
            GnosariRunner instance
        """
        logger.info("Creating basic GnosariRunner without tool streaming")
        return GnosariRunner(
            provider_name=provider_name,
            provider=provider,
            provider_factory=provider_factory,
            **provider_config
        )
    
    @staticmethod
    def _should_enable_tool_streaming(execution_context: ExecutionContext | None) -> bool:
        """
        Determine if tool streaming should be enabled.
        
        Args:
            execution_context: Execution context with configuration
            
        Returns:
            True if tool streaming should be enabled
        """
        if not execution_context:
            # Default configuration: enable tool streaming for streaming contexts
            return False
        
        # Tool streaming requires regular streaming to be enabled
        if not execution_context.stream:
            return False
        
        # Check explicit tool streaming configuration
        return execution_context.tool_streaming
    
    @staticmethod
    def get_available_merger_types() -> list[str]:
        """Get list of available stream merger types."""
        return ["basic", "time_ordered", "priority"]
    
    @staticmethod
    def validate_merger_type(merger_type: str) -> bool:
        """Validate stream merger type."""
        return merger_type in RunnerFactory.get_available_merger_types()


class EnterpriseRunnerBuilder:
    """
    Builder pattern for creating complex runner configurations.
    
    Follows Builder Pattern for complex configuration scenarios.
    """
    
    def __init__(self):
        self._provider_name: str | None = None
        self._provider: Any = None
        self._provider_factory: Any = None
        self._enable_tool_streaming: bool = True
        self._merger_type: str = "time_ordered"
        self._provider_config: dict[str, Any] = {}
        self._execution_context: ExecutionContext | None = None
    
    def with_provider(self, provider_name: str) -> "EnterpriseRunnerBuilder":
        """Set provider name."""
        self._provider_name = provider_name
        return self
    
    def with_provider_instance(self, provider: Any) -> "EnterpriseRunnerBuilder":
        """Set provider instance directly."""
        self._provider = provider
        return self
    
    def with_provider_factory(self, factory: Any) -> "EnterpriseRunnerBuilder":
        """Set provider factory."""
        self._provider_factory = factory
        return self
    
    def with_tool_streaming(self, enabled: bool = True) -> "EnterpriseRunnerBuilder":
        """Enable/disable tool streaming."""
        self._enable_tool_streaming = enabled
        return self
    
    def with_merger_type(self, merger_type: str) -> "EnterpriseRunnerBuilder":
        """Set stream merger type."""
        if not RunnerFactory.validate_merger_type(merger_type):
            raise ValueError(f"Invalid merger type: {merger_type}")
        self._merger_type = merger_type
        return self
    
    def with_execution_context(self, context: ExecutionContext) -> "EnterpriseRunnerBuilder":
        """Set execution context."""
        self._execution_context = context
        return self
    
    def with_provider_config(self, **config) -> "EnterpriseRunnerBuilder":
        """Set provider configuration."""
        self._provider_config.update(config)
        return self
    
    def build(self) -> EnterpriseRunner:
        """Build the configured runner."""
        if self._execution_context:
            # Use factory with execution context
            return RunnerFactory.create_runner(
                provider_name=self._provider_name,
                provider=self._provider,
                provider_factory=self._provider_factory,
                execution_context=self._execution_context,
                **self._provider_config
            )
        elif self._enable_tool_streaming:
            # Create streaming runner explicitly
            return RunnerFactory.create_streaming_runner(
                provider_name=self._provider_name,
                provider=self._provider,
                provider_factory=self._provider_factory,
                tool_streaming=self._enable_tool_streaming,
                merger_type=self._merger_type,
                **self._provider_config
            )
        else:
            # Create basic runner
            return RunnerFactory.create_basic_runner(
                provider_name=self._provider_name,
                provider=self._provider,
                provider_factory=self._provider_factory,
                **self._provider_config
            )


# Convenience factory functions
def create_enterprise_runner(
    provider_name: str,
    execution_context: ExecutionContext | None = None,
    **provider_config
) -> EnterpriseRunner:
    """
    Convenience function to create enterprise-grade runner.
    
    Args:
        provider_name: Provider to use
        execution_context: Execution configuration
        **provider_config: Provider-specific configuration
        
    Returns:
        Configured runner with appropriate capabilities
    """
    return RunnerFactory.create_runner(
        provider_name=provider_name,
        execution_context=execution_context,
        **provider_config
    )


def create_streaming_runner(
    provider_name: str,
    tool_streaming: bool = True,
    merger_type: str = "time_ordered",
    **provider_config
) -> StreamingEnhancedGnosariRunner:
    """
    Convenience function to create streaming runner.
    
    Args:
        provider_name: Provider to use
        tool_streaming: Enable tool streaming
        merger_type: Stream merger type
        **provider_config: Provider-specific configuration
        
    Returns:
        StreamingEnhancedGnosariRunner instance
    """
    return RunnerFactory.create_streaming_runner(
        provider_name=provider_name,
        tool_streaming=tool_streaming,
        merger_type=merger_type,
        **provider_config
    )