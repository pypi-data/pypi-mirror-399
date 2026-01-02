"""LangChain output adapter for LangChain PromptTemplate output."""

from typing import Any

from .base import BaseOutputAdapter


class LangChainOutputAdapter(BaseOutputAdapter):
    """
    Output adapter that returns a LangChain PromptTemplate.

    This adapter wraps the rendered prompt in a LangChain PromptTemplate
    object, which can be used directly in LangChain chains and workflows.

    Note: Requires langchain-core to be installed:
        pip install langchain-core
    """

    def __init__(self) -> None:
        """Initialize the LangChain output adapter."""
        try:
            # Import here to make langchain optional
            from langchain_core.prompts import (  # type: ignore  # noqa: F401
                PromptTemplate as LCPromptTemplate,
            )

            self._lc_prompt_template = LCPromptTemplate
        except ImportError as e:
            raise ImportError(
                "LangChain output adapter requires langchain-core. "
                "Install it with: pip install langchain-core"
            ) from e

    def format(
        self, prompt: str, metadata: dict[str, Any] | None = None
    ) -> Any:  # Returns LangChain PromptTemplate
        """
        Format the prompt as a LangChain PromptTemplate.

        Args:
            prompt: The rendered prompt string
            metadata: Optional metadata about the prompt

        Returns:
            LangChain PromptTemplate instance
        """
        # For LangChain, we typically want to preserve template variables
        # rather than rendering them. However, since we've already rendered
        # the prompt, we create a simple template from the rendered string.
        return self._lc_prompt_template.from_template(prompt)
