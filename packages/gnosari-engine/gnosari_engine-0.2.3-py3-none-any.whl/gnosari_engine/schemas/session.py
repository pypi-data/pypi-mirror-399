"""Session context schema for tools and runners."""

from typing import Any

from pydantic import Field

from .base import BaseIOSchema


class SessionContext(BaseIOSchema):
    """Session execution context for tools and runners - replaces TeamContext."""

    account_id: int | None = Field(
        default=None, description="Account identifier for multi-tenant scenarios"
    )

    # Integer IDs for database references (python-api style)
    team_id: int | None = Field(
        default=None, description="Integer team ID (references teams table)"
    )

    agent_id: int | None = Field(
        default=None, description="Integer agent ID (references agents table)"
    )

    # String identifiers from YAML configuration
    team_identifier: str | None = Field(
        default=None, description="Team identifier from YAML root 'id' field"
    )

    agent_identifier: str | None = Field(
        default=None, description="Agent identifier from YAML agents[].id field"
    )

    session_id: str | None = Field(
        default=None, description="Session identifier for conversation tracking"
    )

    # Original YAML configuration for OpenAI Agents SDK compatibility
    original_config: dict[str, Any] | None = Field(
        default_factory=dict, description="Original team configuration from YAML"
    )

    # For OpenAI Agents SDK compatibility - returns self as dict
    @property
    def session_context(self) -> dict[str, Any]:
        """Get session context as dict for OpenAI Agents SDK compatibility."""
        return self.model_dump(exclude_none=True)

    # Extensibility for future context fields
    metadata: dict[str, Any] | None = Field(
        default_factory=dict, description="Additional context metadata"
    )


__all__ = ["SessionContext"]
