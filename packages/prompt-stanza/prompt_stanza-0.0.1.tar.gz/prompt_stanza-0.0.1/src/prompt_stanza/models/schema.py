"""Schema field model for input validation."""

from typing import Any

from pydantic import BaseModel, Field, field_validator


class SchemaField(BaseModel):
    """Schema definition for a template input field."""

    name: str = Field(..., min_length=1, description="Field name")
    type: str = Field(..., description="Field type (str, int, float, bool, list, dict)")
    required: bool = Field(default=True, description="Whether field is required")
    default: Any | None = Field(default=None, description="Default value if not required")
    description: str | None = Field(default=None, description="Field description")
    min_length: int | None = Field(default=None, ge=0, description="Minimum length constraint")
    max_length: int | None = Field(default=None, ge=0, description="Maximum length constraint")
    max_tokens: int | None = Field(
        default=None, ge=0, description="Maximum token count (using tiktoken)"
    )
    block_phrases: list[str] | None = Field(
        default=None,
        description="List of phrases to block (e.g., 'ignore previous', 'system prompt')",
    )

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate that type is one of the supported types."""
        allowed_types = {"str", "int", "float", "bool", "list", "dict"}
        if v not in allowed_types:
            raise ValueError(f"Type must be one of {allowed_types}, got: {v}")
        return v

    @field_validator("max_length")
    @classmethod
    def validate_max_length(cls, v: int | None, info) -> int | None:
        """Validate that max_length is greater than min_length if both are set."""
        if (
            v is not None
            and info.data.get("min_length") is not None
            and v < info.data["min_length"]
        ):
            raise ValueError("max_length must be greater than or equal to min_length")
        return v
