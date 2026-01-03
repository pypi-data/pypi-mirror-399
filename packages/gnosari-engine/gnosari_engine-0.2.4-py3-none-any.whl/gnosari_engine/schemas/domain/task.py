"""
Task domain models.
Contains task-related domain objects for task execution.
"""

from __future__ import annotations

from typing import Any, Literal, Optional
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from .base import BaseComponent


class Task(BaseComponent):
    """
    Task domain object representing a unit of work to be executed.

    This is the domain representation of a database task, enriched with
    business logic and validation rules.
    """

    # Core task information
    title: str = Field(..., min_length=1, description="Task title")
    description: Optional[str] = Field(None, description="Detailed task description")
    input_message: Optional[str] = Field(
        None, description="Original input/requirements for the task"
    )

    # Task classification
    type: Literal["bug", "feature", "task", "improvement", "research"] = Field(
        "task", description="Task type classification"
    )
    status: Literal["pending", "in_progress", "review", "completed", "failed", "cancelled"] = Field(
        "pending", description="Current task status"
    )
    tags: list[str] = Field(default_factory=list, description="Task tags for categorization")

    # Assignment information
    assigned_team_id: Optional[int] = Field(None, description="Database ID of assigned team")
    assigned_agent_id: Optional[int] = Field(None, description="Database ID of assigned agent")
    assigned_team_identifier: str = Field(..., description="Team identifier from YAML")
    assigned_agent_identifier: Optional[str] = Field(
        None, description="Agent identifier from YAML"
    )

    # Reporter information (who created the task)
    reporter_team_id: Optional[int] = Field(None, description="Database ID of reporter team")
    reporter_agent_id: Optional[int] = Field(None, description="Database ID of reporter agent")
    reporter_team_identifier: Optional[str] = Field(None, description="Reporter team identifier")
    reporter_agent_identifier: Optional[str] = Field(None, description="Reporter agent identifier")

    # Hierarchy and relationships
    parent_id: Optional[int] = Field(None, description="Parent task ID for subtasks")
    subtasks: list[Task] = Field(default_factory=list, description="Child tasks")

    # Execution tracking
    result: Optional[str] = Field(None, description="Execution result or error message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation tracking")
    account_id: int = Field(..., description="Account ID for multi-tenant isolation")

    # Timestamps
    created_at: Optional[datetime] = Field(None, description="Task creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate task title is not empty."""
        if not v or not v.strip():
            raise ValueError("Task title cannot be empty")
        return v.strip()

    @field_validator("assigned_team_identifier")
    @classmethod
    def validate_assigned_team_identifier(cls, v: str) -> str:
        """Validate assigned team identifier."""
        if not v or not v.strip():
            raise ValueError("Assigned team identifier cannot be empty")
        return v.strip()

    def is_pending(self) -> bool:
        """Check if task is pending."""
        return self.status == "pending"

    def is_in_progress(self) -> bool:
        """Check if task is in progress."""
        return self.status == "in_progress"

    def is_completed(self) -> bool:
        """Check if task is completed."""
        return self.status == "completed"

    def is_failed(self) -> bool:
        """Check if task is failed."""
        return self.status == "failed"

    def has_subtasks(self) -> bool:
        """Check if task has subtasks."""
        return len(self.subtasks) > 0

    def get_full_description(self) -> str:
        """
        Get full task description including input message.

        Returns:
            Combined description and input message
        """
        parts = []

        if self.description:
            parts.append(self.description)

        if self.input_message:
            parts.append(f"\nOriginal Requirements:\n{self.input_message}")

        return "\n".join(parts) if parts else ""

    def to_dict(self) -> dict[str, Any]:
        """
        Convert task to dictionary representation.

        Returns:
            Dictionary with task data
        """
        return {
            "id": self.id,
            "name": self.name,
            "title": self.title,
            "description": self.description,
            "input_message": self.input_message,
            "type": self.type,
            "status": self.status,
            "tags": self.tags,
            "assigned_team_id": self.assigned_team_id,
            "assigned_agent_id": self.assigned_agent_id,
            "assigned_team_identifier": self.assigned_team_identifier,
            "assigned_agent_identifier": self.assigned_agent_identifier,
            "reporter_team_id": self.reporter_team_id,
            "reporter_agent_id": self.reporter_agent_id,
            "reporter_team_identifier": self.reporter_team_identifier,
            "reporter_agent_identifier": self.reporter_agent_identifier,
            "parent_id": self.parent_id,
            "result": self.result,
            "session_id": self.session_id,
            "account_id": self.account_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "subtasks_count": len(self.subtasks)
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Task:
        """
        Create Task domain object from dictionary (e.g., from database).

        Args:
            data: Dictionary with task data

        Returns:
            Task domain object
        """
        # Extract subtasks if present
        subtasks_data = data.pop("subtasks", [])

        # Convert id to string if it's an integer (from database)
        if isinstance(data.get("id"), int):
            data["id"] = str(data["id"])

        # Parse datetime strings if present
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if isinstance(data.get("updated_at"), str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])

        # Create task
        task = cls(**data)

        # Add subtasks recursively
        if subtasks_data:
            task.subtasks = [cls.from_dict(st) for st in subtasks_data]

        return task


class TaskExecutionContext(BaseModel):
    """
    Task execution context configuration.

    Similar to ExecutionContext but specific to task execution.
    """

    stream: bool = Field(True, description="Enable streaming mode")
    debug: bool = Field(False, description="Enable debug mode")
    tool_streaming: bool = Field(True, description="Enable tool streaming")
    tool_streaming_merger: str = Field("time_ordered", description="Stream merger type")
    timeout_override: Optional[int] = Field(None, ge=1, description="Override timeout in seconds")

    # Task-specific options
    update_status: bool = Field(True, description="Automatically update task status")
    store_result: bool = Field(True, description="Automatically store execution result")
    fail_on_error: bool = Field(True, description="Fail task on execution error")


class TaskRunMetadata(BaseModel):
    """
    Metadata for task execution tracking.

    Extends AgentRunMetadata concept for task-specific tracking.
    """

    # Task identification
    task_id: int = Field(..., description="Task database ID")
    task_identifier: Optional[str] = Field(None, description="Task identifier (if applicable)")

    # Multi-tenancy
    account_id: int = Field(..., description="Account ID for multi-tenant isolation")

    # Team and agent information
    team_id: Optional[int] = Field(None, description="Team database ID")
    agent_id: Optional[int] = Field(None, description="Agent database ID")
    team_identifier: Optional[str] = Field(None, description="Team identifier from YAML")
    agent_identifier: Optional[str] = Field(None, description="Agent identifier from YAML")

    # Session tracking
    session_id: Optional[str] = Field(None, description="Session ID for conversation tracking")

    # Execution tracking
    execution_start: Optional[datetime] = Field(None, description="Execution start time")
    execution_end: Optional[datetime] = Field(None, description="Execution end time")

    def get_execution_duration(self) -> Optional[float]:
        """
        Get execution duration in seconds.

        Returns:
            Duration in seconds or None if not completed
        """
        if self.execution_start and self.execution_end:
            return (self.execution_end - self.execution_start).total_seconds()
        return None


class TaskRun(BaseModel):
    """
    Domain object for task execution.

    Similar to AgentRun, this encapsulates everything needed to execute a task.
    This is the main object passed to execution services.
    """

    task: Task = Field(..., description="Task domain object to execute")
    agent: Any = Field(..., description="Agent object that will execute the task")  # Avoid circular import
    team: Any = Field(..., description="Team context for execution")  # Avoid circular import
    message: str = Field(..., description="Execution message built from task context")
    context: TaskExecutionContext = Field(
        default_factory=TaskExecutionContext,
        description="Task execution context configuration"
    )
    metadata: TaskRunMetadata = Field(..., description="Task execution metadata")

    # Agent run reference (created during execution)
    agent_run: Optional[Any] = Field(None, description="Underlying AgentRun object")

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate message is not empty."""
        if not v or not v.strip():
            raise ValueError("Execution message cannot be empty")
        return v.strip()

    def to_agent_run(self):
        """
        Convert TaskRun to AgentRun for execution.

        This is used internally by the executor to leverage existing
        agent execution infrastructure.

        Returns:
            AgentRun object
        """
        # Import here to avoid circular dependency
        from .execution import AgentRun, ExecutionContext, AgentRunMetadata

        # Create execution context
        execution_context = ExecutionContext(
            stream=self.context.stream,
            debug=self.context.debug,
            tool_streaming=self.context.tool_streaming,
            tool_streaming_merger=self.context.tool_streaming_merger,
            timeout_override=self.context.timeout_override
        )

        # Create agent run metadata
        agent_metadata = AgentRunMetadata(
            account_id=self.metadata.account_id,
            team_id=self.metadata.team_id,
            agent_id=self.metadata.agent_id,
            team_identifier=self.metadata.team_identifier,
            agent_identifier=self.metadata.agent_identifier,
            session_id=self.metadata.session_id,
            task_id=self.metadata.task_id
        )

        # Create and return AgentRun
        return AgentRun(
            agent=self.agent,
            team=self.team,
            message=self.message,
            context=execution_context,
            metadata=agent_metadata
        )


__all__ = [
    "Task",
    "TaskExecutionContext",
    "TaskRunMetadata",
    "TaskRun"
]
