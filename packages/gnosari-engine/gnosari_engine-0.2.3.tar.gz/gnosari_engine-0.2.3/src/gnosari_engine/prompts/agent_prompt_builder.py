"""
Default agent prompt builder implementation.
Builds comprehensive agent prompts including traits, knowledge, and tools.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Any

if TYPE_CHECKING:
    from ..schemas.domain.agent import Agent
    from ..schemas.domain.team import Team

from .interfaces import IPromptBuilder


class AgentPromptBuilder(IPromptBuilder):
    """
    Default implementation of agent prompt building.
    Follows Single Responsibility Principle - only builds agent prompts.
    """

    def build_agent_prompt(self, agent: Agent, team: Team | None = None) -> str:
        """
        Build enhanced agent prompt including traits, knowledge, and tools.

        Args:
            agent: Agent configuration with base instructions
            team: Optional team context providing available tools, knowledge, and traits

        Returns:
            Enhanced instructions string ready for LLM execution
        """
        prompt_parts = []
        if agent.name:
            prompt_parts.append(f"You are {agent.name}. Your identifier is {agent.id}")

        # Only add team-based enhancements if team is provided
        if team is not None:
            prompt_parts.append(f"You work as part of the team {team.name}. \n")
            prompt_parts.append(f"The Team Identifier is `{team.id}`. \n")

        prompt_parts.append(agent.instructions)
        # Add traits section - agent has direct trait objects
        if agent.traits:
            prompt_parts.append("\n## Your Traits:")
            for trait in agent.traits:
                prompt_parts.append(f"- **{trait.name}**: {trait.description}")
                # Add trait instructions for behavior modification
                if trait.instructions:
                    prompt_parts.append(f"  Instructions: {trait.instructions}")

        # Add knowledge section - agent has direct knowledge objects
        if agent.knowledge:
            prompt_parts.append("\n## Available Knowledge Sources:")
            prompt_parts.append("Use the knowledge_query tool to search these knowledge bases:")
            for kb in agent.knowledge:
                prompt_parts.append(f"- **{kb.id}** ({kb.name}): {kb.description}")

            prompt_parts.append("\nTo query a knowledge base, use: knowledge_query(query='your search terms', knowledge_name='knowledge_base_id')")

        # Add tools section - agent has direct tool objects
        if agent.tools:
            prompt_parts.append("\n## Available Tools:")
            for tool in agent.tools:
                prompt_parts.append(f"- **{tool.name}**: {tool.description}")

        # Add handoffs section - agents you can transfer control to
        if agent.handoffs:
            prompt_parts.append("\n## Available Handoffs:")
            prompt_parts.append("You can transfer control to these agents:")
            for handoff in agent.handoffs:
                target_name = handoff.get_target_name()
                prompt_parts.append(f"- **{handoff.target_agent_id}** ({target_name})")
                if handoff.condition:
                    prompt_parts.append(f"  Condition: {handoff.condition}")
                if handoff.message:
                    prompt_parts.append(f"  Message: {handoff.message}")

        # Add delegations section - agents you can delegate tasks to
        if agent.delegations:
            prompt_parts.append("\n## Available Delegations:")
            prompt_parts.append("You can delegate tasks to these agents:")
            for delegation in agent.delegations:
                target_name = delegation.get_target_name()
                prompt_parts.append(f"- **{delegation.target_agent_id}** ({target_name}) - Mode: {delegation.mode}")
                if delegation.instructions:
                    prompt_parts.append(f"  Instructions: {delegation.instructions}")
                if delegation.timeout:
                    prompt_parts.append(f"  Timeout: {delegation.timeout}s")

        # Add memory section - only if memory content is not empty
        if agent.memory and not agent.memory.is_empty():
            prompt_parts.append("\n## Your Memory:")
            prompt_parts.append(agent.memory.content)

        return "\n".join(prompt_parts)

    def build_task_execution_prompt(self, agent: Agent, team: Team | None = None, task: Dict[str, Any] = None) -> str:
        """
        Build enhanced agent prompt for task execution.

        Includes the standard agent prompt plus task-specific context
        (title, description, input_message) to guide the agent's execution.

        Args:
            agent: Agent configuration with base instructions
            team: Optional team context providing available tools, knowledge, and traits
            task: Task data including title, description, and input_message

        Returns:
            Enhanced instructions string for task execution
        """
        # Build base agent prompt
        base_prompt = self.build_agent_prompt(agent, team)

        # Add task execution context if task is provided
        if task:
            task_parts = [base_prompt, "\n## Task to Execute:"]

            # Add task title
            if task.get('title'):
                task_parts.append(f"\n**Task Title:** {task['title']}")

            # Add task type and status
            if task.get('type'):
                task_parts.append(f"**Task Type:** {task['type']}")
            if task.get('status'):
                task_parts.append(f"**Current Status:** {task['status']}")

            # Add task description
            if task.get('description'):
                task_parts.append(f"\n**Task Description:**\n{task['description']}")

            # Add input message (original requirements)
            if task.get('input_message'):
                task_parts.append(f"\n**Original Requirements:**\n{task['input_message']}")

            # Add task tags if available
            if task.get('tags') and len(task['tags']) > 0:
                tags_str = ", ".join(task['tags'])
                task_parts.append(f"\n**Tags:** {tags_str}")

            # Add execution instructions
            task_parts.append("\n**Instructions:**")
            task_parts.append("Execute the task described above following the requirements and constraints specified.")
            task_parts.append("Provide a detailed response including your approach, actions taken, and results.")
            task_parts.append("If you need to use tools or delegate to other agents, do so as needed to complete the task successfully.")

            return "\n".join(task_parts)

        # If no task provided, return base prompt
        return base_prompt