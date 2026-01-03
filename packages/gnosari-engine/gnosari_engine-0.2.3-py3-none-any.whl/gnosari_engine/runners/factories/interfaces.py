"""
Runner factory interfaces following extreme SOLID principles.
Clean abstractions for provider and stream processing factories.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..interfaces import ProviderStrategy

class IProviderFactory(ABC):
    """
    Interface for creating provider strategy instances.
    Follows Single Responsibility Principle - only creates ProviderStrategy instances.
    Follows Open/Closed Principle - extensible for new providers without modification.
    """

    @abstractmethod
    def create_provider(self, provider_name: str) -> "ProviderStrategy":
        """
        Create provider strategy instance by name.

        Args:
            provider_name: Name of the provider to create

        Returns:
            ProviderStrategy instance ready for use

        Raises:
            ValueError: If provider_name is unknown or invalid
        """
        pass

    @abstractmethod
    def register_provider(self, name: str, provider_class: type["ProviderStrategy"]) -> None:
        """
        Register a new provider class.

        Args:
            name: Provider name identifier
            provider_class: Provider class that implements ProviderStrategy

        Raises:
            ValueError: If name already registered or provider_class invalid
        """
        pass

    @abstractmethod
    def get_available_providers(self) -> list[str]:
        """
        Get list of all registered provider names.

        Returns:
            List of available provider names
        """
        pass


class IStreamResultProcessor(ABC):
    """
    Interface for processing streaming execution results.
    Follows Single Responsibility Principle - only processes stream results.
    Follows Interface Segregation Principle - focused interface for result processing.
    """

    @abstractmethod
    async def collect_team_result(self, stream) -> str:
        """
        Collect and aggregate team execution results from stream.

        Args:
            stream: AsyncGenerator of StreamEvent objects

        Returns:
            Aggregated result string from team execution
        """
        pass

    @abstractmethod
    async def collect_agent_result(self, stream) -> str:
        """
        Collect and aggregate agent execution results from stream.

        Args:
            stream: AsyncGenerator of StreamEvent objects

        Returns:
            Aggregated result string from agent execution
        """
        pass