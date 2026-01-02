"""PromptConfig model for YAML template configuration."""

from typing import Any

import yaml
from jinja2 import Environment, TemplateSyntaxError
from jinja2 import Template as Jinja2Template
from pydantic import BaseModel, Field, field_validator

from .schema import SchemaField
from .strategies import DefenseStrategy
from .template import TemplateStructure


class PromptConfig(BaseModel):
    """Configuration model for YAML template files."""

    # Prompt metadata
    name: str = Field(..., min_length=1, max_length=100, description="Prompt name")
    version: str = Field(
        ..., pattern=r"^\d+\.\d+\.\d+$", description="Semantic version (e.g., 1.0.0)"
    )
    description: str | None = Field(default=None, max_length=500, description="Prompt description")

    # Prompt Template components
    template: Jinja2Template | TemplateStructure = Field(
        ..., description="Compiled Jinja2 template or TemplateStructure object"
    )

    # Validation schema
    validation_schema: list[SchemaField] = Field(
        default_factory=list, description="Input validation schema for template variables"
    )

    # Safety parameters
    defense_strategies: list[str | DefenseStrategy] | None = Field(
        default_factory=list, description="List of defense strategies to apply"
    )

    @field_validator("version")
    @classmethod
    def validate_semver(cls, v: str) -> str:
        """Validate semantic versioning format."""
        parts = v.split(".")
        if len(parts) != 3:
            raise ValueError(f"Version must be in format X.Y.Z, got: {v}")

        for part in parts:
            if not part.isdigit():
                raise ValueError(f"Version parts must be numeric, got: {v}")

        return v

    @field_validator("defense_strategies", mode="before")
    @classmethod
    def validate_defense_strategies(cls, v: Any) -> list[DefenseStrategy]:
        """Convert string defense strategies to DefenseStrategy instances."""
        if v is None:
            return []

        if not isinstance(v, list):
            raise ValueError("defense_strategies must be a list")

        result = []
        for item in v:
            if isinstance(item, DefenseStrategy):
                result.append(item)
            elif isinstance(item, str):
                # Convert string to DefenseStrategy
                if item == "perplexity_check":
                    result.append(DefenseStrategy.PERPLEXITY_CHECK)
                elif item == "classify_intent":
                    result.append(DefenseStrategy.CLASSIFY_INTENT)
                elif item == "rewrite":
                    result.append(DefenseStrategy.REWRITE)
                else:
                    raise ValueError(f"Invalid defense strategy: {item}")
            else:
                raise ValueError(
                    f"Defense strategy must be string or DefenseStrategy, got {type(item)}"
                )

        return result

    @field_validator("template", mode="before")
    @classmethod
    def validate_and_compile_template(cls, v: Any, info) -> TemplateStructure | Jinja2Template:
        """Validate and compile template.

        Template can be a string or an object with system/task/output_format.
        """
        if isinstance(v, (Jinja2Template, TemplateStructure)):
            return v

        # Handle string format - compile to Jinja2Template
        if isinstance(v, str):
            try:
                env = Environment()
                return env.from_string(v)
            except TemplateSyntaxError as e:
                raise ValueError(f"Invalid Jinja2 template: {e}") from e

        # Handle object format - create TemplateStructure
        if isinstance(v, dict):
            # Validate required fields
            if "system" not in v:
                raise ValueError("Template object must contain 'system' field")
            if "task" not in v:
                raise ValueError("Template object must contain 'task' field")

            # Note: delimiting_strategy conversion happens in TemplateStructure
            # Create TemplateStructure instance (will validate and compile internally)
            return TemplateStructure(**v)

        raise ValueError(
            "Template must be a string, Jinja2Template, or object with system/task/output_format"
        )

    def render(self, **context: Any) -> str:
        """
        Render the template with the given context.

        Args:
            **context: Variables to render in the template

        Returns:
            Rendered template string
        """
        # Handle string/Jinja2Template format
        if isinstance(self.template, Jinja2Template):
            return self.template.render(**context)

        # Handle TemplateStructure format
        if isinstance(self.template, TemplateStructure):
            parts = []

            # Render system (required)
            parts.append(self.template.system.render(**context))

            # Render task (required)
            parts.append(self.template.task.render(**context))

            # Render output_format (optional)
            if self.template.output_format is not None:
                parts.append(self.template.output_format.render(**context))

            return "\n\n".join(parts)

        raise ValueError("Invalid template format")

    model_config = {"arbitrary_types_allowed": True}

    @classmethod
    def _validate_config(cls, data: dict) -> None:
        """Validate YAML data structure and content.

        Args:
            data: Parsed YAML data dictionary

        Raises:
            ValueError: If validation fails
        """
        # Validate required fields
        if "name" not in data:
            raise ValueError("Field 'name' is required")
        if not isinstance(data["name"], str) or not data["name"].strip():
            raise ValueError("Field 'name' must be a non-empty string")

        if "version" not in data:
            raise ValueError("Field 'version' is required")
        if not isinstance(data["version"], str):
            raise ValueError("Field 'version' must be a string")

        # Validate semver
        version = data["version"]
        parts = version.split(".")
        if len(parts) != 3:
            raise ValueError(f"Field 'version' must be in semver format X.Y.Z, got: {version}")
        for part in parts:
            if not part.isdigit():
                raise ValueError(f"Field 'version' parts must be numeric, got: {version}")

        # Validate optional string fields
        if (
            "description" in data
            and data["description"] is not None
            and not isinstance(data["description"], str)
        ):
            raise ValueError("Field 'description' must be a string")

        # Validate template (required) - can be string or object
        if "template" not in data:
            raise ValueError("Field 'template' is required")

        if isinstance(data["template"], str):
            if not data["template"].strip():
                raise ValueError("Field 'template' must be a non-empty string")
        elif isinstance(data["template"], dict):
            # Basic validation - detailed validation happens in TemplateStructure
            if "system" not in data["template"]:
                raise ValueError("Template object must contain 'system' field")
            if "task" not in data["template"]:
                raise ValueError("Template object must contain 'task' field")

            # Validate delimiting_strategy if provided
            if (
                "delimiting_strategy" in data["template"]
                and data["template"]["delimiting_strategy"] is not None
            ):
                strategy = data["template"]["delimiting_strategy"]
                if not isinstance(strategy, str):
                    raise ValueError("Template 'delimiting_strategy' must be a string")

                valid_strategies = {"none", "markdown", "xml", "marker", "angle_brackets"}
                if strategy.lower() not in valid_strategies:
                    raise ValueError(
                        f"Template 'delimiting_strategy' must be one of {valid_strategies}, "
                        f"got: {strategy}"
                    )
        else:
            raise ValueError("Field 'template' must be a string or object")

        # Template compilation and detailed validation happens in field_validator
        if "validation_schema" in data and data["validation_schema"] is not None:
            if not isinstance(data["validation_schema"], list):
                raise ValueError("Field 'validation_schema' must be a list")

            for idx, field in enumerate(data["validation_schema"]):
                if not isinstance(field, dict):
                    raise ValueError(f"Schema entry {idx} must be a dictionary")

                # Required fields in schema entry
                if "name" not in field:
                    raise ValueError(f"Schema entry {idx}: field 'name' is required")
                if not isinstance(field["name"], str) or not field["name"].strip():
                    raise ValueError(f"Schema entry {idx}: field 'name' must be a non-empty string")

                if "type" not in field:
                    raise ValueError(f"Schema entry {idx}: field 'type' is required")
                if not isinstance(field["type"], str):
                    raise ValueError(f"Schema entry {idx}: field 'type' must be a string")

                # Optional description
                if (
                    "description" in field
                    and field["description"] is not None
                    and not isinstance(field["description"], str)
                ):
                    raise ValueError(f"Schema entry {idx}: field 'description' must be a string")

                # Validate min_length and max_length
                if (
                    "min_length" in field
                    and field["min_length"] is not None
                    and (not isinstance(field["min_length"], int) or field["min_length"] < 0)
                ):
                    raise ValueError(
                        f"Schema entry {idx}: field 'min_length' must be a non-negative integer"
                    )

                if "max_length" in field and field["max_length"] is not None:
                    if not isinstance(field["max_length"], int) or field["max_length"] < 0:
                        raise ValueError(
                            f"Schema entry {idx}: field 'max_length' must be a non-negative integer"
                        )

                    # Validate max_length >= min_length
                    if (
                        "min_length" in field
                        and field["min_length"] is not None
                        and field["max_length"] < field["min_length"]
                    ):
                        raise ValueError(
                            f"Schema entry {idx}: 'max_length' must be >= 'min_length'"
                        )

        # Validate defense_strategies (optional)
        if "defense_strategies" in data and data["defense_strategies"] is not None:
            if not isinstance(data["defense_strategies"], list):
                raise ValueError("Field 'defense_strategies' must be a list")
            valid_defenses = {"perplexity_check", "classify_intent", "rewrite"}
            for idx, strategy in enumerate(data["defense_strategies"]):
                if not isinstance(strategy, str):
                    raise ValueError(f"Defense strategy {idx} must be a string")
                if strategy not in valid_defenses:
                    raise ValueError(
                        f"Defense strategy {idx} must be one of {valid_defenses}, got: {strategy}"
                    )

    @classmethod
    def load_yaml(cls, yaml_string: str) -> "PromptConfig":
        """Load prompt configuration from a YAML string.

        Args:
            yaml_string: YAML content as string

        Returns:
            PromptConfig instance

        Raises:
            ValueError: If YAML is invalid or validation fails
        """
        try:
            data = yaml.safe_load(yaml_string)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML: {e}") from e

        if not isinstance(data, dict):
            raise ValueError("YAML must contain a dictionary")

        # Validate YAML structure
        cls._validate_config(data)

        return cls(**data)
