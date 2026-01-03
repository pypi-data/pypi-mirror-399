"""
Strategy Pattern implementation for different configuration loading approaches.
Supports both monolithic YAML files and modular directory structures.
"""

import logging
from pathlib import Path
from typing import Any

import yaml

from .interfaces import IConfigurationStrategy, IModularConfigurationLoader


class ConfigurationStrategyError(Exception):
    """Exception raised by configuration strategies."""

    pass


class MonolithicYamlStrategy(IConfigurationStrategy):
    """Strategy for single YAML file configurations."""

    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)

    def can_handle(self, path: Path) -> bool:
        """Check if this strategy can handle single YAML files."""
        return path.is_file() and path.suffix in [".yaml", ".yml"]

    def load(self, path: Path) -> dict[str, Any]:
        """Load configuration from single YAML file."""
        try:
            self._logger.debug(f"Loading monolithic YAML configuration: {path}")

            with open(path, encoding="utf-8") as f:
                config = yaml.safe_load(f)

            if config is None:
                raise ConfigurationStrategyError(f"Empty YAML file: {path}")

            self._logger.debug(f"Successfully loaded monolithic configuration: {path}")
            return config

        except yaml.YAMLError as e:
            raise ConfigurationStrategyError(
                f"YAML parsing error in {path}: {e}"
            ) from e
        except FileNotFoundError as e:
            raise ConfigurationStrategyError(
                f"Configuration file not found: {path}"
            ) from e
        except Exception as e:
            raise ConfigurationStrategyError(f"Failed to load {path}: {e}") from e


class ModularDirectoryStrategy(IConfigurationStrategy, IModularConfigurationLoader):
    """Strategy for modular directory configurations."""

    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)

    def can_handle(self, path: Path) -> bool:
        """Check if this strategy can handle modular directories."""
        return path.is_dir() and (path / "main.yaml").exists()

    def load(self, path: Path) -> dict[str, Any]:
        """Load configuration from modular directory structure."""
        try:
            self._logger.debug(f"Loading modular directory configuration: {path}")

            # Load main configuration
            main_config = self.load_main_config(path)

            # Load component directories
            agents = self.load_component_directory(path / "agents")
            tools = self.load_component_directory(path / "tools")
            knowledge = self.load_component_directory(path / "knowledge")
            traits = self.load_component_directory(path / "traits")

            # Merge everything into a single configuration
            merged_config = {
                **main_config,
                "agents": list(agents.values()),
                "tools": list(tools.values()),
                "knowledge": list(knowledge.values()),
                "traits": list(traits.values()),
            }

            self._logger.debug(f"Successfully loaded modular configuration: {path}")
            return merged_config

        except Exception as e:
            raise ConfigurationStrategyError(
                f"Failed to load modular configuration {path}: {e}"
            ) from e

    def load_main_config(self, path: Path) -> dict[str, Any]:
        """Load main configuration file (main.yaml)."""
        main_file = path / "main.yaml"
        if not main_file.exists():
            main_file = path / "main.yml"

        if not main_file.exists():
            raise ConfigurationStrategyError(
                f"No main.yaml or main.yml found in {path}"
            )

        try:
            with open(main_file, encoding="utf-8") as f:
                config = yaml.safe_load(f)

            return config or {}

        except yaml.YAMLError as e:
            raise ConfigurationStrategyError(
                f"YAML parsing error in {main_file}: {e}"
            ) from e
        except Exception as e:
            raise ConfigurationStrategyError(
                f"Failed to load main config {main_file}: {e}"
            ) from e

    def load_component_directory(self, path: Path) -> dict[str, dict[str, Any]]:
        """Load all component files from a directory."""
        components = {}

        if not path.exists() or not path.is_dir():
            self._logger.debug(f"Component directory does not exist: {path}")
            return components

        # Process both .yaml and .yml files
        for pattern in ["*.yaml", "*.yml"]:
            for file_path in path.glob(pattern):
                component_id = file_path.stem

                # Skip if we already loaded this component (prefer .yaml over .yml)
                if component_id in components:
                    continue

                component_config = self._load_component_file(file_path, component_id)
                if component_config is not None:
                    components[component_id] = component_config

        return components

    def _load_component_file(self, file_path: Path, component_id: str) -> dict[str, Any] | None:
        """Load and process a single component file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                component_config = yaml.safe_load(f)

            if component_config is None:
                self._logger.warning(f"Empty component file: {file_path}")
                return None

            # Ensure component has an ID
            if "id" not in component_config:
                component_config["id"] = component_id

            # Use file name as fallback for name
            if "name" not in component_config:
                component_config["name"] = (
                    component_id.replace("_", " ").replace("-", " ").title()
                )

            self._logger.debug(f"Loaded component: {component_id} from {file_path}")
            return component_config

        except yaml.YAMLError as e:
            self._logger.error(f"YAML parsing error in {file_path}: {e}")
            raise ConfigurationStrategyError(
                f"YAML parsing error in {file_path}: {e}"
            ) from e
        except Exception as e:
            self._logger.error(f"Failed to load component {file_path}: {e}")
            raise ConfigurationStrategyError(
                f"Failed to load component {file_path}: {e}"
            ) from e


class ConfigurationStrategyResolver:
    """Resolver for selecting appropriate configuration strategy."""

    def __init__(self) -> None:
        self._strategies = [
            ModularDirectoryStrategy(),  # Try modular first
            MonolithicYamlStrategy(),  # Fallback to monolithic
        ]
        self._logger = logging.getLogger(__name__)

    def resolve_strategy(self, path: Path) -> IConfigurationStrategy:
        """Find strategy that can handle the given path."""
        self._logger.debug(f"Resolving configuration strategy for: {path}")

        for strategy in self._strategies:
            if strategy.can_handle(path):
                strategy_name = strategy.__class__.__name__
                self._logger.debug(f"Selected strategy: {strategy_name} for {path}")
                return strategy

        raise ConfigurationStrategyError(f"No strategy can handle path: {path}")

    def add_strategy(
        self, strategy: IConfigurationStrategy, priority: int | None = None
    ) -> None:
        """Add a custom strategy to the resolver."""
        if priority is None:
            self._strategies.append(strategy)
        else:
            self._strategies.insert(priority, strategy)

    def list_strategies(self) -> list:
        """List all available strategies."""
        return [strategy.__class__.__name__ for strategy in self._strategies]
