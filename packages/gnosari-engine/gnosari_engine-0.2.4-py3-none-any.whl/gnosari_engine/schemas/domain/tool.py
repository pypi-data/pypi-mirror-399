"""
Tool domain models.
Contains tool configuration and validation logic.
"""

from typing import Any, Literal

from pydantic import Field, model_validator

from .base import BaseComponent


class Tool(BaseComponent):
    """Tool configuration domain object (renamed from ToolConfiguration)."""

    # Built-in tool fields
    module: str | None = Field(
        None, description="Python module path for built-in tools"
    )
    class_name: str | None = Field(None, description="Tool class name")

    # MCP tool fields
    url: str | None = Field(None, description="MCP server URL")
    command: str | None = Field(None, description="MCP server command")
    connection_type: Literal["sse", "streamable_http", "stdio"] | None = Field(
        "sse", description="MCP connection type"
    )
    headers: dict[str, str] = Field(
        default_factory=dict, description="HTTP headers for MCP"
    )
    timeout: int | None = Field(30, ge=1, description="Connection timeout in seconds")

    # Common configuration
    args: dict[str, Any] | list[str] = Field(
        default_factory=dict, description="Tool arguments"
    )

    # Advanced configuration
    rate_limit: int | None = Field(None, ge=1, description="Rate limit per minute")
    enable_caching: bool = Field(True, description="Enable response caching")
    cache_timeout: int = Field(3600, ge=1, description="Cache timeout in seconds")
    retry_attempts: int = Field(3, ge=0, le=10, description="Number of retry attempts")
    retry_delay: float = Field(
        1.0, ge=0.1, le=10.0, description="Retry delay in seconds"
    )

    @model_validator(mode="after")
    def validate_tool_model(self) -> "Tool":
        """Validate tool configuration and set name if not provided."""
        # Set name from id if not provided
        if not self.name and self.id:
            self.name = self.id.replace("_", " ").replace("-", " ").title()

        # Validate tool configuration
        has_builtin = self.module and self.class_name
        has_mcp = self.url or self.command

        if not (has_builtin or has_mcp):
            raise ValueError(
                "Tool must have either (module + class_name) OR (url OR command)"
            )

        return self

    def is_mcp_tool(self) -> bool:
        """Check if this is an MCP server tool."""
        return self.url is not None or self.command is not None

    def is_builtin_tool(self) -> bool:
        """Check if this is a built-in tool."""
        return self.module is not None and self.class_name is not None
