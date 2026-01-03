"""
Prompt builder interfaces following SOLID principles.
Defines contracts for prompt building services.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..schemas.domain.agent import Agent
    from ..schemas.domain.team import Team


class IPromptBuilder(ABC):
    """
    Interface for agent prompt building services.
    Follows Single Responsibility Principle - focused only on prompt building.
    """

    @abstractmethod
    def build_agent_prompt(self, agent: "Agent", team: "Team | None" = None) -> str:
        """
        Build enhanced agent prompt including traits, knowledge, and tools.

        Args:
            agent: Agent configuration with base instructions
            team: Optional team context providing available tools, knowledge, and traits

        Returns:
            Enhanced instructions string ready for LLM execution
        """
        pass