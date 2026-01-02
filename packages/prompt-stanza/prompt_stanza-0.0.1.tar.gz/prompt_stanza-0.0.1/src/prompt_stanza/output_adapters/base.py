"""Base output adapter interface for prompt formatting."""

from abc import ABC, abstractmethod
from typing import Any


class BaseOutputAdapter(ABC):
    """
    Abstract base class for output adapters.

    Output adapters are responsible for formatting the final composed prompt
    into various formats (plain string, LangChain PromptTemplate, etc.).
    """

    @abstractmethod
    def format(self, prompt: str, metadata: dict[str, Any] | None = None) -> Any:
        """
        Format the composed prompt into the desired output format.

        Args:
            prompt: The rendered prompt string
            metadata: Optional metadata about the prompt (config, inputs, etc.)

        Returns:
            Formatted output (type depends on adapter implementation)
        """
        pass
