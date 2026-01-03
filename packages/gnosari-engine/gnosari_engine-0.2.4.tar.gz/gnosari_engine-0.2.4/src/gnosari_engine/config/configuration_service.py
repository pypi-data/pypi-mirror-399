"""
Main ConfigurationService orchestrating configuration loading with SOLID principles.
Coordinates all single-purpose services through dependency injection.
"""

import logging
from pathlib import Path
from typing import Any

from ..factories.domain_factory_interface import IDomainObjectFactory
from ..schemas.domain import AgentRun, Team
from .interfaces import (
    IComponentIndexer,
    IComponentResolver,
    IConfigurationParser,
    IConfigurationValidator,
    IDelegationResolver,
    IDomainObjectBuilder,
    IHandoffResolver,
)
from .services import (
    ConfigurationParsingError,
    ConfigurationServiceError,
    ConfigurationValidationError,
    DomainObjectBuildError,
)
from .strategies import ConfigurationStrategyResolver


class ConfigurationService:
    """
    Main service orchestrating configuration loading with SOLID principles.
    Follows Dependency Inversion Principle by depending on abstractions.
    """

    def __init__(
        self,
        parser: IConfigurationParser,
        validator: IConfigurationValidator,
        builder: IDomainObjectBuilder,
        resolver: IComponentResolver,
        indexer: IComponentIndexer,
        delegation_resolver: IDelegationResolver,
        handoff_resolver: IHandoffResolver,
        domain_factory: IDomainObjectFactory,
        strategy_resolver: ConfigurationStrategyResolver | None = None,
    ):
        """
        Initialize with dependency injection of all services.

        Args:
            parser: Service for parsing YAML configurations
            validator: Service for validating configuration structure
            builder: Service for building domain objects
            resolver: Service for resolving component references
            indexer: Service for adding performance indexes
            delegation_resolver: Service for resolving agent delegation references
            handoff_resolver: Service for resolving agent handoff references
            domain_factory: Factory for creating domain execution objects
            strategy_resolver: Optional strategy resolver (creates default if None)
        """
        self._parser = parser
        self._validator = validator
        self._builder = builder
        self._resolver = resolver
        self._indexer = indexer
        self._delegation_resolver = delegation_resolver
        self._handoff_resolver = handoff_resolver
        self._domain_factory = domain_factory
        self._strategy_resolver = strategy_resolver or ConfigurationStrategyResolver()
        self._logger = logging.getLogger(__name__)

    def load_team_configuration(self, config_path: str | Path) -> Team:
        """
        Load and transform team configuration using service pipeline.

        Args:
            config_path: Path to configuration file or directory

        Returns:
            Fully processed Team domain object

        Raises:
            ConfigurationServiceError: If any step in the pipeline fails
        """
        import time

        overall_start = time.time()
        config_path = Path(config_path)

        try:
            # Step 1: Determine strategy and load raw configuration
            self._logger.info(f"Loading configuration: {config_path}")
            strategy = self._strategy_resolver.resolve_strategy(config_path)
            raw_config = strategy.load(config_path)

            # Step 2: Parse configuration with environment substitution
            self._logger.info("Parsing configuration with environment substitution")
            if config_path.is_file():
                parsed_config = self._parser.parse_yaml_to_dict(config_path)
            else:
                # For directory configs, the strategy already handled parsing
                parsed_config = raw_config

            # Step 3: Validate structure
            self._logger.info("Validating configuration structure")
            validation_errors = self._validator.validate_structure(parsed_config)
            if validation_errors:
                raise ConfigurationValidationError(
                    f"Configuration validation failed: {', '.join(validation_errors)}",
                    errors=validation_errors,
                    config_path=str(config_path),
                )

            # Step 4: Build domain objects
            self._logger.info("Building domain objects")
            team = self._builder.build_team(parsed_config)

            # Step 5: Add performance indexes
            index_start = time.time()
            self._logger.info("Adding performance indexes")
            team = self._indexer.add_indexes_to_team(team)
            index_time = (time.time() - index_start) * 1000

            # Step 6: Resolve component references
            self._logger.info("Resolving component references")
            team = self._resolver.resolve_references(team)

            # Step 7: Resolve agent delegation references
            delegation_start = time.time()
            self._logger.info("Resolving agent delegation references")
            team = self._delegation_resolver.resolve_delegations(team)
            delegation_time = (time.time() - delegation_start) * 1000

            # Step 8: Resolve agent handoff references
            handoff_start = time.time()
            self._logger.info("Resolving agent handoff references")
            team = self._handoff_resolver.resolve_handoffs(team)
            handoff_time = (time.time() - handoff_start) * 1000

            overall_time = (time.time() - overall_start) * 1000
            self._logger.info(
                f"Successfully loaded team configuration: {team.name} (total: {overall_time:.2f}ms, indexing: {index_time:.2f}ms, delegations: {delegation_time:.2f}ms, handoffs: {handoff_time:.2f}ms)"
            )
            return team

        except (
            ConfigurationValidationError,
            ConfigurationParsingError,
            DomainObjectBuildError,
        ):
            # Re-raise known configuration errors
            raise

        except Exception as e:
            # Wrap unknown errors in ConfigurationServiceError
            self._logger.error(f"Unexpected error loading configuration: {e}")
            raise ConfigurationServiceError(
                f"Failed to load configuration from {config_path}: {e!s}",
                config_path=str(config_path)
            ) from e


    def validate_configuration_file(self, config_path: str | Path) -> dict:
        """
        Validate a configuration file without building domain objects.

        Args:
            config_path: Path to configuration file or directory

        Returns:
            Dictionary with validation results
        """
        config_path = Path(config_path)

        try:
            # Load and parse configuration
            strategy = self._strategy_resolver.resolve_strategy(config_path)
            raw_config = strategy.load(config_path)

            if config_path.is_file():
                parsed_config = self._parser.parse_yaml_to_dict(config_path)
            else:
                parsed_config = raw_config

            # Validate structure
            validation_errors = self._validator.validate_structure(parsed_config)

            return {
                "valid": len(validation_errors) == 0,
                "errors": validation_errors,
                "config_path": str(config_path),
                "strategy": strategy.__class__.__name__,
            }

        except Exception as e:
            return {
                "valid": False,
                "errors": [str(e)],
                "config_path": str(config_path),
                "strategy": None,
            }

    def get_available_strategies(self) -> list:
        """Get list of available configuration strategies."""
        return self._strategy_resolver.list_strategies()

    def add_custom_strategy(self, strategy: Any, priority: int | None = None) -> None:
        """Add a custom configuration strategy."""
        self._strategy_resolver.add_strategy(strategy, priority)
