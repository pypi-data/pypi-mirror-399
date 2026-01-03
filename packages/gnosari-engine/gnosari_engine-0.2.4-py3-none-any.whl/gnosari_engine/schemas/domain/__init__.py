"""
Domain models package.
Contains all domain entities following SOLID principles with clear separation of concerns.
"""

# Base components and utilities
# Agent domain models
from .agent import Agent, AgentDelegation, AgentHandoff, LearningObjective
from .base import BaseComponent, deep_merge

# Execution domain models
from .execution import AgentRun, ExecutionContext

# Knowledge domain models
from .knowledge import Knowledge

# Provider configuration models
from .provider import OpenAIAgentsConfig, ProviderConfiguration

# Team domain models
from .team import Team, TeamConfiguration

# Tool domain models
from .tool import Tool

# Trait domain models
from .trait import Trait

# Task domain models
from .task import Task, TaskRun, TaskExecutionContext, TaskRunMetadata

# Queue domain models
from .queue import (
    MessagePriority,
    MessageStatus,
    QueueMessage,
    TaskExecutionMessage,
    TaskExecutionResult,
)

__all__ = [
    "Agent",
    "AgentDelegation",
    "AgentHandoff",
    "AgentRun",
    "BaseComponent",
    "ExecutionContext",
    "Knowledge",
    "LearningObjective",
    "MessagePriority",
    "MessageStatus",
    "OpenAIAgentsConfig",
    "ProviderConfiguration",
    "QueueMessage",
    "Task",
    "TaskExecutionMessage",
    "TaskExecutionResult",
    "TaskRun",
    "TaskExecutionContext",
    "TaskRunMetadata",
    "Team",
    "TeamConfiguration",
    "Tool",
    "Trait",
    "deep_merge",
]
