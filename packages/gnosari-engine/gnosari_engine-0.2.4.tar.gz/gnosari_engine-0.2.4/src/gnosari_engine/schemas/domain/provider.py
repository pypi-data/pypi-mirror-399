"""
Provider configuration domain models.
Contains OpenAI Agents SDK configuration following SOLID principles.
"""

from typing import Any

from pydantic import BaseModel, Field, field_validator

from .base import BaseComponent


class OpenAIAgentsConfig(BaseModel):
    """OpenAI Agents SDK configuration following Single Responsibility Principle."""

    provider_name: str = Field(
        "openai_agents", description="OpenAI Agents SDK provider identifier"
    )
    api_key: str | None = Field(None, description="OpenAI API key override")
    base_url: str | None = Field(None, description="Custom OpenAI API base URL")
    organization: str | None = Field(None, description="OpenAI organization ID")
    project: str | None = Field(None, description="OpenAI project ID")
    timeout: int | None = Field(None, ge=1, description="Request timeout in seconds")
    retry_attempts: int = Field(3, ge=1, le=10, description="Number of retry attempts")

    # Agents SDK specific configuration
    max_tokens: int | None = Field(None, ge=1, description="Maximum tokens per request")
    stream: bool = Field(True, description="Enable streaming responses")
    parallel_tool_calls: bool = Field(True, description="Enable parallel tool calls")
    enable_handoffs: bool = Field(True, description="Enable agent handoffs")
    max_handoffs: int = Field(
        10, ge=1, le=50, description="Maximum number of handoffs per conversation"
    )

    # Debug and monitoring
    enable_trace: bool = Field(False, description="Enable trace logging")
    trace_level: str = Field("INFO", description="Trace logging level")

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: str | None) -> str | None:
        """Validate base URL format."""
        if v and not v.startswith(("http://", "https://")):
            raise ValueError("Base URL must start with http:// or https://")
        return v

    @field_validator("provider_name")
    @classmethod
    def validate_provider_name(cls, v: str) -> str:
        """Validate provider name."""
        if v != "openai_agents":
            raise ValueError('Provider name must be "openai_agents"')
        return v


class ProviderConfiguration(BaseComponent):
    """
    OpenAI Agents SDK provider configuration domain object.
    Follows Single Responsibility Principle - focused on OpenAI Agents SDK only.
    """

    provider_type: str = Field(
        "openai_agents", description="Provider type (OpenAI Agents SDK)"
    )

    # OpenAI Agents SDK configuration
    openai_agents: OpenAIAgentsConfig = Field(
        default_factory=OpenAIAgentsConfig,  # type: ignore[arg-type]
        description="OpenAI Agents SDK configuration",
    )

    # Fallback configuration for custom settings
    custom_config: dict[str, Any] = Field(
        default_factory=dict, description="Custom configuration overrides"
    )

    def get_config(self) -> OpenAIAgentsConfig:
        """
        Get the OpenAI Agents configuration.
        Follows Single Responsibility Principle - only returns OpenAI config.
        """
        return self.openai_agents

    def update_config(self, **kwargs: Any) -> None:
        """
        Update OpenAI Agents configuration.
        Follows Open/Closed Principle - extensible through kwargs.
        """
        for key, value in kwargs.items():
            if hasattr(self.openai_agents, key):
                setattr(self.openai_agents, key, value)
            else:
                self.custom_config[key] = value

    def has_custom_config(self, key: str) -> bool:
        """Check if custom configuration exists for a key."""
        return key in self.custom_config

    def get_custom_config(self, key: str, default: Any = None) -> Any:
        """Get custom configuration value."""
        return self.custom_config.get(key, default)

    def is_streaming_enabled(self) -> bool:
        """Check if streaming is enabled."""
        return self.openai_agents.stream

    def is_handoffs_enabled(self) -> bool:
        """Check if agent handoffs are enabled."""
        return self.openai_agents.enable_handoffs

    def get_max_handoffs(self) -> int:
        """Get maximum number of handoffs allowed."""
        return self.openai_agents.max_handoffs
