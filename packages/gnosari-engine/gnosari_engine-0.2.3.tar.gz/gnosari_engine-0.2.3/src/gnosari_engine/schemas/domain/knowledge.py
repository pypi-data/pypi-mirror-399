"""
Knowledge domain models.
Contains knowledge base configuration and data source management.
"""

from typing import Any, Literal

from pydantic import Field, model_validator

from .base import BaseComponent, deep_merge


class Knowledge(BaseComponent):
    """Knowledge base configuration domain object (renamed from KnowledgeConfiguration)."""

    type: Literal[
        "website", "sitemap", "youtube", "pdf", "text", "csv", "json", "directory"
    ] = Field(..., description="Knowledge base type")
    data: list[str] = Field(..., description="Data sources (URLs, file paths, etc.)")

    # Primary configuration for OpenSearch
    config: dict[str, Any] = Field(
        default_factory=dict, description="Knowledge base configuration"
    )

    @property
    def provider(self) -> str:
        """Get the configured provider (currently only opensearch is supported)."""
        return self.config.get("provider", "opensearch")  # type: ignore[no-any-return]

    @property
    def opensearch_config(self) -> dict[str, Any] | None:
        """Get OpenSearch-specific configuration."""
        return self.config.get("opensearch")

    @property
    def loader_config(self) -> dict[str, Any]:
        """Get data loader configuration."""
        return self.config.get("loader_config", {})  # type: ignore[no-any-return]
    
    @property
    def source_type(self) -> str:
        """Get the source type (alias for type)."""
        return self.type
    
    @property
    def data_sources(self) -> list[str]:
        """Get data sources (alias for data)."""
        return self.data

    @model_validator(mode="after")
    def validate_knowledge_model(self) -> "Knowledge":
        """Validate knowledge configuration and set name if not provided."""
        # Set name from id if not provided
        if not self.name and self.id:
            self.name = self.id.replace("_", " ").replace("-", " ").title()

        # Validate data sources
        if not self.data:
            raise ValueError("Knowledge base must have at least one data source")

        # Type-specific validation
        if self.type in ["website", "sitemap"]:
            for source in self.data:
                if not source.startswith(("http://", "https://")):
                    raise ValueError(f"Website/sitemap sources must be URLs: {source}")
        elif self.type == "youtube":
            for source in self.data:
                if "youtube.com" not in source and "youtu.be" not in source:
                    raise ValueError(f"YouTube sources must be YouTube URLs: {source}")
        elif self.type in ["pdf", "text", "csv", "json"]:
            for source in self.data:
                if source.startswith(("http://", "https://")):
                    continue  # Allow URLs for remote files
                # For local files, we could validate existence, but skip for now

        return self

    def get_effective_config(self) -> dict[str, Any]:
        """Get effective configuration with defaults."""
        base_config = {
            "provider": "opensearch",
            "opensearch": {
                "host": "localhost",
                "port": "9200",
                "use_ssl": "false",
                "model_id": None,  # Must be provided by environment
                "pipeline_name": "openai_embedding_pipeline",
                "embedding_dimension": 1536,
                "username": None,  # Optional: provided by environment or config
                "password": None,  # Optional: provided by environment or config
            },
            "loader_config": {
                "timeout": 60,
                "user_agent": "Gnosari-Bot/1.0",
                "chunk_size": 6000,
                "chunk_overlap": 200,
            },
        }

        # Merge with custom config
        if self.config:
            return deep_merge(base_config, self.config)
        return base_config
    
    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "Knowledge":
        """Create Knowledge instance from configuration dictionary."""
        # Extract required fields
        knowledge_id = config.get("id") or config.get("name")
        if not knowledge_id:
            raise ValueError("Knowledge configuration must have 'id' or 'name' field")
        
        name = config.get("name", knowledge_id)
        source_type = config.get("type", "website")
        data_sources = config.get("data", [])
        
        # Extract nested config
        knowledge_config = config.get("config", {})
        
        return cls(
            id=knowledge_id,
            name=name,
            type=source_type,
            data=data_sources,
            config=knowledge_config
        )
