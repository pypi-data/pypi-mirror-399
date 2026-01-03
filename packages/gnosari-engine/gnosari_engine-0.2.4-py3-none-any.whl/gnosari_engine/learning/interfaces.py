"""
Learning Module Interfaces - Abstract contracts for learning components
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..schemas.domain.agent import Agent
from ..schemas.domain.execution import AgentRun


class TeacherAgentFactoryInterface(ABC):
    """Interface for creating teacher agents programmatically"""
    
    @abstractmethod
    def create_teacher_agent(
        self,
        target_agent: Agent,
        agent_run: AgentRun
    ) -> Agent:
        """
        Create a teacher agent specialized for teaching the target agent
        
        Args:
            target_agent: The agent that will receive learning
            agent_run: AgentRun context for metadata access
            
        Returns:
            Teacher agent configured for the learning task
        """
        pass


class LearningServiceInterface(ABC):
    """Interface for learning service operations"""
    
    @abstractmethod
    async def generate_learning_content(
        self,
        target_agent: Agent,
        session_messages: List[str],
        provider: str = "openai",
        database_url: Optional[str] = None
    ) -> str:
        """
        Generate learning content by analyzing session messages
        
        Args:
            target_agent: Agent that will receive the learning
            session_messages: Messages from the session to analyze
            provider: LLM provider to use
            database_url: Optional database URL for session persistence
            
        Returns:
            Generated learning content
        """
        pass
    
    @abstractmethod
    async def apply_learning_to_agent(
        self,
        target_agent: Agent,
        learning_content: str
    ) -> Agent:
        """
        Apply learning content to update an agent's memory and capabilities
        
        Args:
            target_agent: Agent to update
            learning_content: Learning insights to apply
            
        Returns:
            Updated agent with new learning applied
        """
        pass