"""
Base domain models and utilities.
Contains shared components used across all domain entities.
"""

from abc import ABC
from typing import Any

from pydantic import BaseModel, Field


def deep_merge(
    base_dict: dict[str, Any], update_dict: dict[str, Any]
) -> dict[str, Any]:
    """Deep merge two dictionaries."""
    result = base_dict.copy()
    for key, value in update_dict.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


class BaseComponent(BaseModel, ABC):
    """Base class for all configuration components."""

    id: str = Field(..., description="Component identifier")
    name: str | None = Field(None, description="Display name")
    description: str | None = Field(None, description="Component description")

    class Config:
        arbitrary_types_allowed = True
