"""
Trait domain models.
Contains trait configuration and behavior customization.
"""

from pydantic import Field, field_validator, model_validator

from .base import BaseComponent

# Weight threshold constants following SOLID principles
WEIGHT_SUBTLE_THRESHOLD = 0.5
WEIGHT_MODERATE_THRESHOLD = 0.9
WEIGHT_NORMAL = 1.0
WEIGHT_STRONG_THRESHOLD = 1.5


class Trait(BaseComponent):
    """Trait configuration domain object (renamed from TraitConfiguration)."""

    instructions: str = Field(
        ..., min_length=1, max_length=1000, description="Trait behavior instructions"
    )
    weight: float = Field(1.0, ge=0.0, le=2.0, description="Trait influence weight")
    category: str | None = Field(
        None, description="Trait category (personality, communication, workflow)"
    )
    tags: list[str] = Field(
        default_factory=list, description="Trait tags for organization"
    )

    @field_validator("instructions")
    @classmethod
    def validate_safe_instructions(cls, v: str) -> str:
        """Ensure trait instructions are safe and appropriate."""
        dangerous_patterns = [
            "ignore previous instructions",
            "system prompt",
            "act as if",
            "pretend you are",
            "forget everything",
            "disregard",
            "override",
        ]

        v_lower = v.lower()
        for pattern in dangerous_patterns:
            if pattern in v_lower:
                raise ValueError(
                    f"Trait instructions contain potentially unsafe content: {pattern}"
                )

        return v.strip()

    @model_validator(mode="after")
    def validate_trait_model(self) -> "Trait":
        """Set name from id if not provided."""
        if not self.name and self.id:
            self.name = self.id.replace("_", " ").replace("-", " ").title()
        return self

    def get_weight_description(self) -> str:
        """Get human-readable weight description."""
        if self.weight <= WEIGHT_SUBTLE_THRESHOLD:
            return "Subtle influence"
        elif self.weight <= WEIGHT_MODERATE_THRESHOLD:
            return "Moderate influence"
        elif self.weight == WEIGHT_NORMAL:
            return "Normal influence"
        elif self.weight <= WEIGHT_STRONG_THRESHOLD:
            return "Strong influence"
        else:
            return "Dominant influence"
