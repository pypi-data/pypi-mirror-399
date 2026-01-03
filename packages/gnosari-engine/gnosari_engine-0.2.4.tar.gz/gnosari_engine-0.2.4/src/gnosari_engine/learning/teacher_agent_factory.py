"""
Teacher Agent Factory - Creates specialized teacher agents for learning tasks
"""

import logging
from datetime import datetime
from typing import Dict, Any

from ..schemas.domain.agent import Agent, Memory
from ..schemas.domain.trait import Trait
from ..schemas.domain.execution import AgentRun
from .interfaces import TeacherAgentFactoryInterface


class TeacherAgentFactory(TeacherAgentFactoryInterface):
    """
    Factory for creating teacher agents programmatically.
    
    Single Responsibility: Create teacher agents specialized for learning tasks
    Open/Closed: Easy to extend with new teacher types
    Dependency Inversion: Uses domain objects, not implementation details
    """
    
    def __init__(self):
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def create_teacher_agent(
        self,
        target_agent: Agent,
        agent_run: AgentRun
    ) -> Agent:
        """
        Create a teacher agent specialized for updating the target agent's memory
        
        Args:
            target_agent: The agent that will receive learning
            agent_run: AgentRun context for metadata access
            
        Returns:
            Teacher agent configured for memory update
        """
        self._logger.debug(f"Creating memory updater agent for {target_agent.id}")
        
        # Create teacher-specific traits
        teacher_traits = self._create_teacher_traits(target_agent)
        
        # Create teacher memory with context about the target agent
        teacher_memory = self._create_teacher_memory(target_agent)
        
        # Validate AgentRun parameters
        if agent_run is None:
            raise ValueError("agent_run parameter cannot be None")
        if agent_run.metadata is None:
            raise ValueError("agent_run.metadata cannot be None")
        
        # Build teacher agent
        teacher_agent = Agent(
            id=f"memory_updater_{target_agent.id}",
            name=f"Memory Updater for {target_agent.name}",
            description=f"AI memory updater specialized in updating {target_agent.name}'s memory from session learnings. Do not remove or change memories text unless concepts need to be updated. In any case you should add memories if there is a strict need.",
            instructions=self._build_teacher_instructions(target_agent),
            model="gpt-4o",
            temperature=0.1,
            reasoning_effort="high",
            is_orchestrator=True,
            role="memory_updater",
            max_turns=5,
            debug=False,
            tools=[],  # Teacher doesn't need tools
            knowledge=[],  # Teacher uses its training
            traits=teacher_traits,
            handoffs=[],
            delegations=[],
            learning_objectives=[],
            memory=teacher_memory,
            listen=[],
            trigger=[]
        )
        
        self._logger.info(f"Created memory updater agent: {teacher_agent.id} for target: {target_agent.id}")
        return teacher_agent
    
    def _create_teacher_traits(self, target_agent: Agent) -> list[Trait]:
        """Create traits for memory update role"""
        return [
            Trait(
                id="memory_synthesis",
                name="Memory Synthesis",
                description="Concise synthesis of key learnings into memory",
                instructions="Extract and synthesize the most important learnings into concise, actionable memory content",
                weight=1.5,
                category="synthesis",
                tags=["synthesis", "memory", "concise"]
            )
        ]
    
    def _create_teacher_memory(self, target_agent: Agent) -> Memory:
        """Create memory context for the memory updater about the target agent"""
        memory_content = f"""Memory update context for agent: {target_agent.name} ({target_agent.id})

Agent Profile:
- Role: {target_agent.role or 'General Agent'}
- Learning Objectives: {len(target_agent.learning_objectives)} active objectives

Focus: Update agent memory with key learnings from session messages that align with learning objectives.
"""
        
        current_time = datetime.now().isoformat()
        
        return Memory(
            content=memory_content,
            metadata={
                "teaching_mode": "memory_update",
                "target_agent_id": target_agent.id,
                "target_agent_role": target_agent.role,
                "teacher_created_at": current_time
            },
            context_type="learning",
            importance=0.9,
            created_at=current_time,
            last_accessed=current_time
        )
    
    def _build_teacher_instructions(self, target_agent: Agent) -> str:
        """Build simple instructions for memory updater"""
        
        objectives_context = ""
        if target_agent.learning_objectives:
            objectives_list = "\n".join([
                f"- {obj.objective}"
                for obj in target_agent.learning_objectives
            ])
            objectives_context = f"""
Learning Objectives:
{objectives_list}
"""
        
        instructions = f"""You are a Memory Updater. Update the agent's memory based on session messages and learning objectives.

Agent: {target_agent.name}
{objectives_context}
Return ONLY the updated memory content. Be extremely concise. Use bullet points. Focus on key details that help reach learning objectives."""
        
        return instructions