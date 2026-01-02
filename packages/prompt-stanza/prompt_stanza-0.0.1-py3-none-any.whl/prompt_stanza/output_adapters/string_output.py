"""String output adapter for plain text prompt output."""

from typing import Any

from .base import BaseOutputAdapter


class StringOutputAdapter(BaseOutputAdapter):
    """
    Output adapter that returns the prompt as a plain string.

    This is the default output format and simply returns the rendered
    prompt without any additional formatting or wrapping.
    """

    def format(self, prompt: str, metadata: dict[str, Any] | None = None) -> str:
        """
        Return the prompt as-is.

        Args:
            prompt: The rendered prompt string
            metadata: Optional metadata (unused for string output)

        Returns:
            The prompt string unchanged
        """
        return prompt
