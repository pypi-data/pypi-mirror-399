"""Angle brackets delimiter strategy."""

from typing import Any

from .base import BaseDelimiterStrategy


class AngleBracketsStrategy(BaseDelimiterStrategy):
    """
    Strategy that wraps context with angle bracket delimiters.

    Format: <<<\\ncontext\\n>>>
    """

    def apply(
        self, context: str | list[str] | dict[str, Any] | None, section: str = "context"
    ) -> str | None:
        """
        Wrap context with angle bracket delimiters.

        Args:
            context: Context data
            section: Name of the section being delimited

        Returns:
            Context wrapped with angle brackets and section label
        """
        context_str = self.convert_to_string(context)
        if context_str is None:
            return None

        return f"<<<{section.upper()}\n{context_str}\n{section.upper()}>>>"
