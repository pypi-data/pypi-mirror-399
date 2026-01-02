"""Inline adapter for providing prompt configuration directly."""

from typing import Any

from ..models import PromptConfig
from .base import BaseInputAdapter


class InlineAdapter(BaseInputAdapter):
    """
    Inline adapter for providing prompt configuration directly in code.

    This adapter allows you to define prompts programmatically without
    needing external files. You can provide either a simple template string
    or a full prompt configuration with validation schema and defense strategies.

    Features:
    - Define prompts directly in code
    - Support for simple string templates
    - Support for structured templates (system, task, output_format)
    - Optional validation schema
    - Optional defense strategies
    - Built-in caching (inherits from BaseInputAdapter)

    Examples:
        # Simple template
        adapter = InlineAdapter(
            name="greeting",
            version="1.0.0",
            template="Hello {{ name }}!"
        )

        # Structured template with validation
        adapter = InlineAdapter(
            name="code_review",
            version="2.0.0",
            description="AI-powered code review",
            template={
                "system": "You are an expert code reviewer.",
                "task": "Review this {{ language }} code: {{ code }}",
                "output_format": "Provide feedback in markdown format.",
                "use_sandwich_defense": True,
                "delimiting_strategy": "xml"
            },
            validation_schema=[
                {
                    "name": "language",
                    "type": "str",
                    "description": "Programming language",
                    "required": True
                },
                {
                    "name": "code",
                    "type": "str",
                    "description": "Code to review",
                    "required": True
                }
            ],
            defense_strategies=["perplexity_check", "classify_intent"]
        )
    """

    def __init__(
        self,
        name: str,
        version: str = "1.0.0",
        template: str | dict[str, Any] = "",
        description: str | None = None,
        validation_schema: list[dict[str, Any]] | None = None,
        defense_strategies: list[str] | None = None,
        cache_enabled: bool = False,  # Inline adapters typically don't need caching
    ) -> None:
        """
        Initialize the inline adapter with prompt configuration.

        Args:
            name: Prompt name/identifier
            version: Version string (semver format like "1.0.0")
            template: Template string or dict with system/task/output_format
            description: Optional description of the prompt
            validation_schema: Optional list of schema field definitions
            defense_strategies: Optional list of defense strategy names
            cache_enabled: Whether to enable caching (default False for inline)
        """
        super().__init__(cache_enabled=cache_enabled)

        self._name = name
        self._version = version
        self._template = template
        self._description = description
        self._validation_schema = validation_schema or []
        self._defense_strategies = defense_strategies or []

        # Pre-compile the configuration
        self._config = self._build_config()

    def _build_config(self) -> PromptConfig:
        """Build PromptConfig from constructor parameters."""
        config_dict: dict[str, Any] = {
            "name": self._name,
            "version": self._version,
            "template": self._template,
        }

        if self._description:
            config_dict["description"] = self._description

        if self._validation_schema:
            config_dict["validation_schema"] = self._validation_schema

        if self._defense_strategies:
            config_dict["defense_strategies"] = self._defense_strategies

        return self._compile_from_dict(config_dict)

    def load(self, identifier: str, version: str = "latest") -> PromptConfig:
        """
        Load the inline prompt configuration.

        The identifier and version parameters are ignored for inline adapters
        since there's only one configuration per adapter instance.

        Args:
            identifier: Ignored (always returns the configured prompt)
            version: Ignored (always returns the configured version)

        Returns:
            The pre-compiled PromptConfig instance

        Raises:
            StanzaNotFoundError: Never raised (inline always has one config)
        """
        # For inline adapter, we always return the same config
        return self._config

    @property
    def name(self) -> str:
        """Get the prompt name."""
        return self._name

    @property
    def version(self) -> str:
        """Get the prompt version."""
        return self._version
