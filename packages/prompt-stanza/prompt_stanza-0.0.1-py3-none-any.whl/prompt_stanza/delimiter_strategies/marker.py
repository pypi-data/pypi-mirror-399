"""Marker delimiter strategy."""

from typing import Any

from .base import BaseDelimiterStrategy


class MarkerStrategy(BaseDelimiterStrategy):
    """
    Strategy that wraps context with BEGIN/END markers.

    Format: --- BEGIN CONTEXT ---\\ncontext\\n--- END CONTEXT ---
    """

    def apply(
        self, context: str | list[str] | dict[str, Any] | None, section: str = "context"
    ) -> str | None:
        """
        Wrap context with BEGIN/END markers.

        Args:
            context: Context data
            section: Name of the section being delimited (used in marker labels)

        Returns:
            Context wrapped with BEGIN/END markers
        """
        context_str = self.convert_to_string(context)
        if context_str is None:
            return None

        section_upper = section.upper()
        return f"--- BEGIN {section_upper} ---\n{context_str}\n--- END {section_upper} ---"
