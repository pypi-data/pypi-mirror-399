"""
Domain object factory implementation.
Follows Single Responsibility Principle - creates only domain execution contexts.
Provides simple, clean factory methods following SOLID principles.
"""

from ..schemas.domain import Agent, AgentRun, Team
from ..schemas.domain.execution import ExecutionContext, AgentRunMetadata
from .domain_factory_interface import IDomainObjectFactory


class DomainObjectFactory(IDomainObjectFactory):
    """
    Factory for creating domain execution objects.
    Simple, static methods that create execution contexts with minimal overhead.
    """


    def create_agent_run(
        self,
        agent: Agent,
        team: Team,
        message: str,
        context: ExecutionContext | None = None,
        metadata: AgentRunMetadata | None = None,
    ) -> AgentRun:
        """
        Create AgentRun execution context.

        Args:
            agent: Agent configuration
            team: Team configuration for tools/knowledge context
            message: Input message for the agent
            context: Optional execution context (creates default if None)
            metadata: Optional AgentRunMetadata with session information

        Returns:
            AgentRun object ready for execution with all session data
        """
        if context is None:
            context = ExecutionContext()
        if metadata is None:
            metadata = AgentRunMetadata()
        return AgentRun(agent=agent, team=team, message=message, context=context, metadata=metadata)
