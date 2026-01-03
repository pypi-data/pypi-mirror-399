"""
Learning Service - Orchestrates the learning process for agents
"""

import json
import logging
from datetime import datetime
from typing import List, Optional

from .interfaces import LearningServiceInterface
from ..factories.domain_object_factory import DomainObjectFactory
from ..runners.streaming_enhanced_runner import StreamingEnhancedGnosariRunner
from ..schemas.domain.agent import Agent, Memory
from ..schemas.domain.execution import ExecutionContext


class LearningService(LearningServiceInterface):
    """
    Service for orchestrating agent learning from session analysis.
    
    Single Responsibility: Coordinate learning workflow and content generation
    Open/Closed: Easy to extend with new learning strategies
    Dependency Inversion: Uses interfaces and domain objects
    """

    def __init__(self, domain_factory: Optional[DomainObjectFactory] = None):
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._domain_factory = domain_factory or DomainObjectFactory()

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
        self._logger.info(f"Generating learning content for {target_agent.id}")

        try:
            # Create execution context for learning session
            execution_context = ExecutionContext(
                stream=False,  # We want a complete response, not streaming
                debug=False,
                tool_streaming=False
            )

            # Prepare analysis message
            analysis_message = self._build_analysis_message(target_agent, session_messages)

            # Create teacher agent first
            teacher_agent = self._create_teacher_agent(target_agent)

            # Create team with teacher agent included
            teacher_team = self._create_teacher_team_context(teacher_agent)

            # Create teacher run with proper agent and team
            teacher_run = self._domain_factory.create_agent_run(
                agent=teacher_agent,
                team=teacher_team,
                message=analysis_message,
                context=execution_context
            )

            # Execute teacher analysis
            runner = StreamingEnhancedGnosariRunner(
                provider_name=provider,
                enable_tool_streaming=False,
                stream_merger_type="time_ordered"
            )

            learning_content = ""
            async with runner:
                # Collect all events and handle them like the event display service
                async for event in runner.run_agent_stream(teacher_run):
                    self._logger.debug(f"Processing event: {event.event_type}")

                    # Handle TEXT_DELTA events for streaming content (like event_display.py)
                    if event.event_type == "text_delta":
                        content = self._extract_text_delta(event)
                        if content:
                            self._logger.debug(f"Text delta: {content[:50]}...")
                            learning_content += content

                    # Handle MESSAGE_OUTPUT events for complete messages
                    elif event.event_type == "message_output":
                        content = self._extract_message_content(event)
                        if content:
                            self._logger.debug(f"Message output: {content[:50]}...")
                            learning_content += content

                    # Handle RESPONSE_COMPLETE events
                    elif event.event_type == "response_complete":
                        self._logger.debug("Response complete event received")
                        # Continue to get any final content

                    # Handle AGENT_COMPLETED events
                    elif event.event_type == "agent_completed":
                        self._logger.debug("Agent completed event received")
                        break

                    # Handle AGENT_ERROR events
                    elif event.event_type == "agent_error":
                        error = self._extract_error_from_event(event)
                        raise RuntimeError(f"Teacher agent failed: {error}")

                    else:
                        # Log other event types for debugging
                        self._logger.debug(f"Unhandled event type: {event.event_type}")
                        # Skip agent_started and agent_updated events as they contain input message, not response
                        if event.event_type not in ["agent_started", "agent_updated"]:
                            # For unknown event types, try generic content extraction
                            content = self._extract_generic_content(event)
                            if content:
                                self._logger.debug(f"Found content in {event.event_type}: {content[:50]}...")
                                learning_content += content

            if not learning_content.strip():
                raise ValueError("Teacher agent did not generate any learning content")

            self._logger.info(f"Generated {len(learning_content)} characters of learning content")
            return learning_content.strip()

        except Exception as e:
            self._logger.error(f"Failed to generate learning content: {e}", exc_info=True)
            raise

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
        self._logger.info(f"Applying learning content to agent {target_agent.id}")

        try:
            # Create updated memory with learning insights
            updated_memory = self._update_agent_memory(target_agent, learning_content)

            # Create a copy of the agent with updated memory
            updated_agent = Agent(
                id=target_agent.id,
                name=target_agent.name,
                description=target_agent.description,
                instructions=target_agent.instructions,
                processed_instructions=target_agent.processed_instructions,
                model=target_agent.model,
                temperature=target_agent.temperature,
                reasoning_effort=target_agent.reasoning_effort,
                is_orchestrator=target_agent.is_orchestrator,
                role=target_agent.role,
                max_turns=target_agent.max_turns,
                debug=target_agent.debug,
                tools=target_agent.tools.copy(),
                knowledge=target_agent.knowledge.copy(),
                traits=target_agent.traits.copy(),
                handoffs=target_agent.handoffs.copy(),
                delegations=target_agent.delegations.copy(),
                learning_objectives=target_agent.learning_objectives.copy(),
                memory=updated_memory,
                listen=target_agent.listen.copy(),
                trigger=target_agent.trigger.copy()
            )

            self._logger.info(f"Successfully applied learning to agent {target_agent.id}")
            return updated_agent

        except Exception as e:
            self._logger.error(f"Failed to apply learning to agent: {e}", exc_info=True)
            raise

    def _build_analysis_message(self, target_agent: Agent, session_messages: List[str]) -> str:
        """Build the analysis message for the teacher agent"""

        # Parse and format session messages for analysis
        formatted_messages = self._format_session_messages(session_messages)
        # Include current agent memory
        current_memory = ""
        if target_agent.memory and not target_agent.memory.is_empty():
            current_memory = f"""
**Current Agent Memory:**
{target_agent.memory.content}
"""
        else:
            current_memory = "\n**Current Agent Memory:**\nNo existing memory content.\n"

        # Format learning objectives for display
        objectives_list = ""
        if target_agent.learning_objectives:
            objectives_list = "\n".join([
                f"- {obj.objective} (Priority: {obj.priority})"
                for obj in target_agent.learning_objectives
            ])
            objectives_list = f"\n**Learning Objectives:**\n{objectives_list}\n"

        message = f"""Agent: {target_agent.name}
{current_memory}{objectives_list}
**Session Messages:**
{formatted_messages}

Update memory with key learnings. Return only updated memory content."""

        return message

    def _format_session_messages(self, session_messages: List[str]) -> str:
        """Format session messages for analysis"""
        if not session_messages:
            return "No session messages available for analysis."

        formatted = []
        for i, message_data in enumerate(session_messages, 1):
            try:
                # Try to parse as JSON to extract structured data
                if message_data.startswith('{') or message_data.startswith('['):
                    parsed = json.loads(message_data)
                    # Extract relevant fields for analysis
                    if isinstance(parsed, dict):
                        content = parsed.get('content', str(parsed))
                        role = parsed.get('role', 'unknown')
                        formatted.append(f"Message {i} ({role}): {content}")
                    else:
                        formatted.append(f"Message {i}: {str(parsed)}")
                else:
                    # Plain text message
                    formatted.append(f"Message {i}: {message_data}")
            except json.JSONDecodeError:
                # Not JSON, treat as plain text
                formatted.append(f"Message {i}: {message_data}")

        return "\n\n".join(formatted)

    def _create_teacher_agent(self, target_agent: Agent) -> Agent:
        """Create teacher agent for learning analysis"""
        from .teacher_agent_factory import TeacherAgentFactory
        
        # Create minimal AgentRun for teacher agent factory
        from ..schemas.domain.execution import AgentRun, AgentRunMetadata, ExecutionContext
        
        agent_run_metadata = AgentRunMetadata(
            session_id=f"learning_{target_agent.id}",
            team_identifier="learning_team",
            agent_identifier=target_agent.id
        )
        
        # Create minimal team for AgentRun (will be replaced with proper team later)
        from ..schemas.domain.team import Team, TeamConfiguration
        minimal_team = Team(
            id="temp_team",
            name="Temporary Team",
            description="Temporary team for agent creation",
            version="1.0.0",
            config=TeamConfiguration(),
            agents=[target_agent],  # Satisfy validation temporarily
            tools=[],
            knowledge=[],
            traits=[]
        )
        
        temp_agent_run = AgentRun(
            agent=target_agent,
            team=minimal_team,
            message="Teacher agent creation",
            context=ExecutionContext(stream=False, debug=False),
            metadata=agent_run_metadata
        )
        
        teacher_factory = TeacherAgentFactory()
        return teacher_factory.create_teacher_agent(target_agent, temp_agent_run)

    def _create_teacher_team_context(self, teacher_agent: Agent):
        """Create a team context for the learning session with teacher agent"""
        from ..schemas.domain.team import Team, TeamConfiguration

        team_config = TeamConfiguration(
            max_turns=10,
            timeout=300,
            log_level="INFO",
            enable_memory=True,
            debug=False
        )

        # Create team with teacher agent included
        teacher_team = Team(
            id="learning_team",
            name="Learning Analysis Team", 
            description="Team for learning analysis with teacher agent",
            version="1.0.0",
            tags=["learning", "analysis"],
            config=team_config,
            agents=[teacher_agent],  # Include teacher agent
            tools=[],
            knowledge=[],
            traits=[]
        )

        return teacher_team

    def _update_agent_memory(self, target_agent: Agent, learning_content: str) -> Memory:
        """Update agent memory with learning insights"""
        current_time = datetime.now().isoformat()

        # Replace the entire memory content with the new content
        new_content = learning_content.strip()

        # Create updated metadata
        updated_metadata = {}
        if target_agent.memory:
            updated_metadata = target_agent.memory.metadata.copy()

        updated_metadata.update({
            "last_learning_session": current_time,
            "learning_sessions_count": updated_metadata.get("learning_sessions_count", 0) + 1,
            "content_length": len(new_content)
        })

        return Memory(
            content=new_content,
            metadata=updated_metadata,
            context_type="learning",
            importance=0.9,
            created_at=target_agent.memory.created_at if target_agent.memory else current_time,
            last_accessed=current_time
        )

    def _normalize_event_data(self, data) -> dict:
        """Normalize event data to a consistent dictionary format"""
        if hasattr(data, 'to_dict'):
            return data.to_dict()
        elif isinstance(data, dict):
            return data
        else:
            return {"value": str(data)}

    def _extract_text_delta(self, event) -> str:
        """Extract text delta content from streaming events"""
        try:
            data = self._normalize_event_data(event.data)
            delta = data.get("delta", data.get("value", ""))
            return delta if isinstance(delta, str) else ""
        except Exception as e:
            self._logger.warning(f"Failed to extract text delta: {e}")
            return ""

    def _extract_message_content(self, event) -> str:
        """Extract content from message output events"""
        try:
            data = self._normalize_event_data(event.data)
            content = data.get("content", data.get("message", data.get("text", "")))
            return content if isinstance(content, str) else ""
        except Exception as e:
            self._logger.warning(f"Failed to extract message content: {e}")
            return ""

    def _extract_generic_content(self, event) -> str:
        """Extract content from any event type as fallback"""
        try:
            data = self._normalize_event_data(event.data)

            # Try common content fields
            for field in ["content", "message", "text", "value", "delta"]:
                content = data.get(field, "")
                if content and isinstance(content, str) and len(content.strip()) > 0:
                    return content

            return ""
        except Exception as e:
            self._logger.warning(f"Failed to extract generic content: {e}")
            return ""

    def _extract_error_from_event(self, event) -> str:
        """Extract error information from an event object"""
        try:
            if hasattr(event, 'data'):
                event_data = event.data
                if hasattr(event_data, 'get'):
                    return event_data.get('error', 'Unknown error')
                elif hasattr(event_data, 'error'):
                    return getattr(event_data, 'error', 'Unknown error')
                else:
                    return str(event_data)
            return "Unknown error"
        except Exception as e:
            self._logger.warning(f"Failed to extract error from event: {e}")
            return "Unknown error"
