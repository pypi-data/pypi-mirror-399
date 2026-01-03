"""
Configuration service factory implementation.
Follows Single Responsibility Principle - creates only ConfigurationService instances.
Optimized by default with intelligent dependency injection.
"""

import logging

from ..config.configuration_service import ConfigurationService
from ..config.env_substitutor import EnvironmentVariableSubstitutor
from ..config.interfaces import IComponentResolver, IEnvironmentSubstitutor
from ..config.services import (
    ComponentIndexer,
    ConfigurationParser,
    ConfigurationValidator,
    DelegationResolver,
    DomainObjectBuilder,
    EagerComponentResolver,
    HandoffResolver,
    LazyComponentResolver,
)
from ..config.strategies import ConfigurationStrategyResolver
from .domain_object_factory import DomainObjectFactory
from .interfaces import IConfigurationServiceFactory


class ConfigurationServiceFactory(IConfigurationServiceFactory):
    """
    Factory for creating optimized configuration services.
    Follows Dependency Injection pattern with intelligent defaults.
    """

    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)

    def create(
        self,
        resolution_strategy: str = "eager",
        env_substitutor: IEnvironmentSubstitutor | None = None,
    ) -> ConfigurationService:
        """
        Create optimized configuration service instance.
        Uses eager resolution and performance optimizations by default.
        """
        self._logger.debug(
            f"Creating ConfigurationService with strategy: {resolution_strategy}"
        )

        if env_substitutor is None:
            env_substitutor = EnvironmentVariableSubstitutor()

        parser = ConfigurationParser(env_substitutor)
        validator = ConfigurationValidator()
        builder = DomainObjectBuilder()
        indexer = ComponentIndexer()
        delegation_resolver = DelegationResolver()
        handoff_resolver = HandoffResolver()
        domain_factory = DomainObjectFactory()
        strategy_resolver = ConfigurationStrategyResolver()

        resolver = self._create_resolver(resolution_strategy)

        self._logger.debug(
            f"Created ConfigurationService with {resolution_strategy} resolution"
        )

        return ConfigurationService(
            parser=parser,
            validator=validator,
            builder=builder,
            resolver=resolver,
            indexer=indexer,
            delegation_resolver=delegation_resolver,
            handoff_resolver=handoff_resolver,
            domain_factory=domain_factory,
            strategy_resolver=strategy_resolver,
        )

    def create_with_custom_resolver(
        self,
        resolver: IComponentResolver,
        env_substitutor: IEnvironmentSubstitutor | None = None,
    ) -> ConfigurationService:
        """
        Create configuration service with custom resolver.
        Maintains optimization while allowing custom resolution strategies.
        """
        if env_substitutor is None:
            env_substitutor = EnvironmentVariableSubstitutor()

        parser = ConfigurationParser(env_substitutor)
        validator = ConfigurationValidator()
        builder = DomainObjectBuilder()
        indexer = ComponentIndexer()
        delegation_resolver = DelegationResolver()
        handoff_resolver = HandoffResolver()
        domain_factory = DomainObjectFactory()
        strategy_resolver = ConfigurationStrategyResolver()

        return ConfigurationService(
            parser=parser,
            validator=validator,
            builder=builder,
            resolver=resolver,
            indexer=indexer,
            delegation_resolver=delegation_resolver,
            handoff_resolver=handoff_resolver,
            domain_factory=domain_factory,
            strategy_resolver=strategy_resolver,
        )

    def _create_resolver(self, resolution_strategy: str) -> IComponentResolver:
        """
        Create appropriate resolver based on strategy.
        Encapsulates resolver creation logic following Single Responsibility.
        """
        if resolution_strategy == "lazy":
            return LazyComponentResolver()
        elif resolution_strategy == "eager":
            return EagerComponentResolver()
        else:
            raise ValueError(f"Unknown resolution strategy: {resolution_strategy}")
