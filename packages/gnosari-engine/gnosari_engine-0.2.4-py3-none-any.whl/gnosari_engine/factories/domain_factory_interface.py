"""
Domain object factory interface.
Separated to avoid circular imports following SOLID principles.
"""

from abc import ABC, abstractmethod

from ..schemas.domain import Agent, AgentRun, Team
from ..schemas.domain.execution import ExecutionContext, AgentRunMetadata


class IDomainObjectFactory(ABC):
    """
    Interface for creating domain execution objects.
    Follows Single Responsibility Principle - only creates domain execution contexts.
    """


    @abstractmethod
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
            agent: Agent domain object
            team: Team domain object for tools/knowledge context
            message: Execution message
            context: Optional execution context (creates default if None)
            metadata: Optional AgentRunMetadata with session information

        Returns:
            AgentRun object ready for execution with all session data
        """
        pass
