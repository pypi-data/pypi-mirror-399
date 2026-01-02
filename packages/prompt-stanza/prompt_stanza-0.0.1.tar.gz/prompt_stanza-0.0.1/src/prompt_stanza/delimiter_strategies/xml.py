"""XML delimiter strategy."""

from typing import Any

from .base import BaseDelimiterStrategy


class XmlStrategy(BaseDelimiterStrategy):
    """
    Strategy that wraps context in XML tags.

    Format: <context>\\ncontext\\n</context>
    """

    def apply(
        self, context: str | list[str] | dict[str, Any] | None, section: str = "context"
    ) -> str | None:
        """
        Wrap context in XML tags.

        Args:
            context: Context data
            section: Name of the section being delimited (used as XML tag name)

        Returns:
            Context wrapped in XML tags
        """
        context_str = self.convert_to_string(context)
        if context_str is None:
            return None

        return f"<{section}>\n{context_str}\n</{section}>"
