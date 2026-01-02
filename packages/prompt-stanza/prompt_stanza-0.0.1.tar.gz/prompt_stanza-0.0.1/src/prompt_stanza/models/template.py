"""Template structure for prompt configuration."""

from typing import Any

from jinja2 import Environment, TemplateSyntaxError
from jinja2 import Template as Jinja2Template
from pydantic import BaseModel, Field, field_serializer, field_validator

from .strategies import DelimitingStrategy


class TemplateStructure(BaseModel):
    """Structure for template object format."""

    system: Jinja2Template = Field(..., description="Compiled system/persona template")
    task: Jinja2Template = Field(..., description="Compiled task template")
    output_format: Jinja2Template | None = Field(
        default=None, description="Compiled output format template"
    )
    use_sandwich_defense: bool = Field(
        default=False, description="Whether to apply sandwich defense"
    )
    delimiting_strategy: str = Field(
        default="none",
        description="Delimiting strategy for this template",
    )

    @field_validator("delimiting_strategy", mode="before")
    @classmethod
    def validate_delimiting_strategy(cls, v: Any) -> str:
        """Validate delimiting strategy value."""
        # Accept DelimitingStrategy constants or strings
        if hasattr(DelimitingStrategy, v.upper() if isinstance(v, str) else ""):
            return v.lower()

        valid_strategies = ["none", "markdown", "xml", "marker", "angle_brackets"]
        v_str = str(v).lower()

        if v_str not in valid_strategies:
            raise ValueError(
                f"Invalid delimiting strategy: '{v}'. Must be one of: {', '.join(valid_strategies)}"
            )

        return v_str

    @field_validator("system", "task", "output_format", mode="before")
    @classmethod
    def compile_template(cls, v: Any, info) -> Jinja2Template | None:
        """Compile template strings to Jinja2Template."""
        if v is None:
            return None

        if isinstance(v, Jinja2Template):
            return v

        if isinstance(v, str):
            try:
                env = Environment()
                return env.from_string(v)
            except TemplateSyntaxError as e:
                raise ValueError(f"Invalid Jinja2 template in '{info.field_name}': {e}") from e

        raise ValueError(f"Template '{info.field_name}' must be a string or Jinja2Template")

    @field_serializer("system", "task", "output_format")
    def serialize_template(self, value: Jinja2Template | None, _info) -> str | None:
        """Serialize Jinja2Template to string."""
        if value is None:
            return None
        # Return the template source
        return value.source if hasattr(value, "source") else str(value)

    model_config = {"arbitrary_types_allowed": True}
