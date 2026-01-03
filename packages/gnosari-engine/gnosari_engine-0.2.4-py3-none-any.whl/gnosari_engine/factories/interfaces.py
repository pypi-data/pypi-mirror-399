"""
Factory interfaces following extreme SOLID principles.
Each factory has a single responsibility with clear abstractions.
"""

from abc import ABC, abstractmethod

from ..config.configuration_service import ConfigurationService
from ..config.interfaces import IComponentResolver, IEnvironmentSubstitutor


class IConfigurationServiceFactory(ABC):
    """
    Interface for creating configuration services.
    Follows Single Responsibility Principle - only creates ConfigurationService instances.
    """

    @abstractmethod
    def create(
        self,
        resolution_strategy: str = "eager",
        env_substitutor: IEnvironmentSubstitutor | None = None,
    ) -> ConfigurationService:
        """
        Create optimized configuration service instance.

        Args:
            resolution_strategy: Component resolution strategy ("eager" or "lazy")
            env_substitutor: Optional custom environment substitutor

        Returns:
            Fully configured and optimized ConfigurationService instance

        Raises:
            ValueError: If invalid resolution strategy provided
        """
        pass

    @abstractmethod
    def create_with_custom_resolver(
        self,
        resolver: IComponentResolver,
        env_substitutor: IEnvironmentSubstitutor | None = None,
    ) -> ConfigurationService:
        """
        Create configuration service with custom resolver.

        Args:
            resolver: Custom component resolver implementation
            env_substitutor: Optional custom environment substitutor

        Returns:
            ConfigurationService with custom resolver
        """
        pass
