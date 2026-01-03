"""
Queue message domain objects.

This module contains all domain models for the async task queue system.
Follows SOLID principles with immutable, well-validated domain objects.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class MessagePriority(str, Enum):
    """Message priority levels for queue processing."""

    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class MessageStatus(str, Enum):
    """Message processing status tracking."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class QueueMessage(BaseModel):
    """
    Base class for all queue messages.

    Follows Single Responsibility Principle - only represents message data.
    Open/Closed Principle - extensible via inheritance.
    Liskov Substitution Principle - all subclasses maintain message contract.
    """

    message_id: str = Field(..., description="Unique message identifier")
    message_type: str = Field(..., description="Message type identifier")
    priority: MessagePriority = Field(
        default=MessagePriority.NORMAL, description="Message priority level"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Message creation timestamp"
    )
    retry_count: int = Field(default=0, ge=0, description="Number of retry attempts")
    max_retries: int = Field(default=3, ge=0, description="Maximum retry attempts")

    # Execution tracking
    started_at: Optional[datetime] = Field(
        default=None, description="Processing start timestamp"
    )
    completed_at: Optional[datetime] = Field(
        default=None, description="Processing completion timestamp"
    )

    class Config:
        """Pydantic configuration."""

        frozen = False  # Allow updates during processing
        use_enum_values = True

    @field_validator("message_type")
    @classmethod
    def validate_message_type(cls, v: str) -> str:
        """Validate message type is not empty."""
        if not v or not v.strip():
            raise ValueError("Message type cannot be empty")
        return v.strip()

    def mark_started(self) -> None:
        """Mark message as started processing."""
        self.started_at = datetime.utcnow()

    def mark_completed(self) -> None:
        """Mark message as completed processing."""
        self.completed_at = datetime.utcnow()

    def increment_retry(self) -> None:
        """Increment retry count."""
        self.retry_count += 1

    def can_retry(self) -> bool:
        """
        Check if message can be retried.

        Returns:
            True if retry count is below maximum
        """
        return self.retry_count < self.max_retries

    def get_processing_duration(self) -> Optional[float]:
        """
        Get processing duration in seconds.

        Returns:
            Duration in seconds if both timestamps exist, None otherwise
        """
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class TaskExecutionMessage(QueueMessage):
    """
    Message for asynchronous task execution.

    Contains all information needed to execute a task asynchronously.
    Follows Interface Segregation Principle - contains only task execution data.
    """

    message_type: Literal["task_execution"] = "task_execution"

    # Task identification
    task_id: int = Field(..., gt=0, description="Task database ID")
    account_id: int = Field(..., gt=0, description="Account ID for multi-tenancy")

    # Team and agent configuration
    team_config_path: str = Field(..., description="Path to team YAML configuration")
    assigned_agent_identifier: Optional[str] = Field(
        default=None, description="Agent identifier from YAML configuration"
    )

    # Execution configuration
    provider: str = Field(default="openai", description="LLM provider to use")
    session_id: Optional[str] = Field(
        default=None, description="Session ID for tracking"
    )
    database_url: Optional[str] = Field(
        default=None, description="Database connection URL"
    )

    # Execution options
    stream: bool = Field(
        default=False, description="Enable streaming (not used in async mode)"
    )
    debug: bool = Field(default=False, description="Enable debug mode")
    tool_streaming: bool = Field(default=True, description="Enable tool streaming")
    stream_merger: str = Field(
        default="time_ordered", description="Stream merger strategy"
    )

    @field_validator("team_config_path")
    @classmethod
    def validate_team_config_path(cls, v: str) -> str:
        """Validate team config path is not empty."""
        if not v or not v.strip():
            raise ValueError("Team config path cannot be empty")
        return v.strip()

    def to_execution_params(self) -> dict[str, Any]:
        """
        Convert message to execution parameters.

        Returns:
            Dictionary of parameters for TaskExecutor
        """
        return {
            "task_id": self.task_id,
            "account_id": self.account_id,
            "team_config_path": self.team_config_path,
            "provider": self.provider,
            "session_id": self.session_id,
            "database_url": self.database_url,
            "debug": self.debug,
            "tool_streaming": self.tool_streaming,
            "stream_merger": self.stream_merger,
        }


class TaskExecutionResult(BaseModel):
    """
    Result of task execution via queue.

    Immutable result object following Single Responsibility Principle.
    """

    message_id: str = Field(..., description="Original message ID")
    task_id: int = Field(..., description="Task database ID")
    status: MessageStatus = Field(..., description="Execution status")
    output: Optional[str] = Field(default=None, description="Execution output")
    error: Optional[str] = Field(
        default=None, description="Error message if failed"
    )
    duration_seconds: Optional[float] = Field(
        default=None, description="Execution duration in seconds"
    )
    retry_count: int = Field(default=0, description="Number of retries performed")

    class Config:
        """Pydantic configuration."""

        use_enum_values = True
        frozen = True  # Results are immutable
