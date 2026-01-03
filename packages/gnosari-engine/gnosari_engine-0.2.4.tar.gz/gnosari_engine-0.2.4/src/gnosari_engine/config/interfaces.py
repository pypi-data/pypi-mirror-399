"""
SOLID service interfaces for configuration loading and transformation.
Follows Dependency Inversion Principle with clear abstractions.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from ..schemas.domain import Agent, Knowledge, Team, Tool, Trait


class IConfigurationLoader(ABC):
    """Interface for loading raw configuration data."""

    @abstractmethod
    def load_config(self, path: str | Path) -> dict[str, Any]:
        """
        Load raw configuration from file or directory.

        Args:
            path: Path to configuration file or directory

        Returns:
            Raw configuration dictionary

        Raises:
            ConfigurationLoadingError: If loading fails
        """
        pass


class IEnvironmentSubstitutor(ABC):
    """Interface for environment variable substitution."""

    @abstractmethod
    def substitute(self, config: dict[str, Any]) -> dict[str, Any]:
        """
        Substitute environment variables in configuration.

        Args:
            config: Configuration dictionary with possible ${ENV_VAR} placeholders

        Returns:
            Configuration with environment variables substituted

        Raises:
            EnvironmentSubstitutionError: If substitution fails
        """
        pass


class IConfigurationParser(ABC):
    """Interface for parsing configuration structures."""

    @abstractmethod
    def parse_yaml_to_dict(self, config_path: Path) -> dict[str, Any]:
        """
        Parse YAML file to dictionary with environment substitution.

        Args:
            config_path: Path to YAML configuration file

        Returns:
            Parsed configuration dictionary

        Raises:
            ConfigurationParsingError: If parsing fails
        """
        pass


class IConfigurationValidator(ABC):
    """Interface for validating configuration data."""

    @abstractmethod
    def validate_structure(self, config: dict[str, Any]) -> list[str]:
        """
        Validate configuration structure and return error list.

        Args:
            config: Configuration dictionary to validate

        Returns:
            List of validation errors (empty if valid)
        """
        pass


class IDomainObjectBuilder(ABC):
    """Interface for building domain objects from configuration."""

    @abstractmethod
    def build_team(self, config: dict[str, Any]) -> Team:
        """
        Build Team domain object from configuration dictionary.

        Args:
            config: Validated configuration dictionary

        Returns:
            Team domain object

        Raises:
            DomainObjectBuildError: If building fails
        """
        pass

    @abstractmethod
    def build_agents(
        self, 
        agents_data: list[dict[str, Any]], 
        tools: list[Tool], 
        knowledge: list[Knowledge], 
        traits: list[Trait]
    ) -> list[Agent]:
        """
        Build list of Agent objects with resolved component references.

        Args:
            agents_data: List of agent configuration dictionaries
            tools: Available Tool objects for reference resolution
            knowledge: Available Knowledge objects for reference resolution
            traits: Available Trait objects for reference resolution

        Returns:
            List of Agent objects with resolved component references
        """
        pass

    @abstractmethod
    def build_tools(self, tools_data: list[dict[str, Any]]) -> list[Tool]:
        """
        Build list of Tool objects.

        Args:
            tools_data: List of tool configuration dictionaries

        Returns:
            List of Tool objects
        """
        pass

    @abstractmethod
    def build_knowledge(self, knowledge_data: list[dict[str, Any]]) -> list[Knowledge]:
        """
        Build list of Knowledge objects.

        Args:
            knowledge_data: List of knowledge configuration dictionaries

        Returns:
            List of Knowledge objects
        """
        pass

    @abstractmethod
    def build_traits(self, traits_data: list[dict[str, Any]]) -> list[Trait]:
        """
        Build list of Trait objects.

        Args:
            traits_data: List of trait configuration dictionaries

        Returns:
            List of Trait objects
        """
        pass


class IComponentResolver(ABC):
    """Interface for resolving component references."""

    @abstractmethod
    def resolve_references(self, team: Team) -> Team:
        """
        Resolve component references within team configuration.

        Args:
            team: Team configuration with unresolved references

        Returns:
            Team configuration with resolved references
        """
        pass


class IComponentIndexer(ABC):
    """Interface for creating performance indexes."""

    @abstractmethod
    def add_indexes_to_team(self, team: Team) -> Team:
        """
        Add O(1) lookup indexes to team object for performance.

        Args:
            team: Team configuration without indexes

        Returns:
            Team configuration with performance indexes
        """
        pass


class IDelegationResolver(ABC):
    """Interface for resolving agent delegation references."""

    @abstractmethod
    def resolve_delegations(self, team: Team) -> Team:
        """
        Resolve agent delegation references to actual Agent objects.

        Args:
            team: Team with unresolved delegation references

        Returns:
            Team with resolved delegation references

        Raises:
            DelegationResolutionError: If delegation resolution fails
        """
        pass


class IHandoffResolver(ABC):
    """Interface for resolving agent handoff references."""

    @abstractmethod
    def resolve_handoffs(self, team: Team) -> Team:
        """
        Resolve agent handoff references to actual Agent objects.

        Args:
            team: Team with unresolved handoff references

        Returns:
            Team with resolved handoff references

        Raises:
            HandoffResolutionError: If handoff resolution fails
        """
        pass


class IConfigurationStrategy(ABC):
    """Strategy interface for different configuration formats."""

    @abstractmethod
    def can_handle(self, path: Path) -> bool:
        """
        Check if this strategy can handle the given path.

        Args:
            path: Path to configuration file or directory

        Returns:
            True if strategy can handle this path
        """
        pass

    @abstractmethod
    def load(self, path: Path) -> dict[str, Any]:
        """
        Load configuration using this strategy.

        Args:
            path: Path to configuration file or directory

        Returns:
            Raw configuration dictionary

        Raises:
            ConfigurationStrategyError: If loading fails
        """
        pass


class IModularConfigurationLoader(ABC):
    """Interface for loading modular configuration structures."""

    @abstractmethod
    def load_component_directory(self, path: Path) -> dict[str, dict[str, Any]]:
        """
        Load all component files from a directory.

        Args:
            path: Path to component directory (agents/, tools/, etc.)

        Returns:
            Dictionary mapping component IDs to configuration data
        """
        pass

    @abstractmethod
    def load_main_config(self, path: Path) -> dict[str, Any]:
        """
        Load main configuration file (main.yaml).

        Args:
            path: Path to configuration root directory

        Returns:
            Main configuration dictionary
        """
        pass
