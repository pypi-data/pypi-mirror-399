"""Markdown delimiter strategy."""

from typing import Any

from .base import BaseDelimiterStrategy


class MarkdownStrategy(BaseDelimiterStrategy):
    """
    Strategy that wraps context in markdown code blocks.

    Format: ```\\ncontext\\n```
    """

    def apply(
        self, context: str | list[str] | dict[str, Any] | None, section: str = "context"
    ) -> str | None:
        """
        Wrap context in markdown code blocks.

        Args:
            context: Context data
            section: Name of the section being delimited

        Returns:
            Context wrapped in markdown code blocks with section label
        """
        context_str = self.convert_to_string(context)
        if context_str is None:
            return None

        return f"```{section.lower()}\n{context_str}\n```"
