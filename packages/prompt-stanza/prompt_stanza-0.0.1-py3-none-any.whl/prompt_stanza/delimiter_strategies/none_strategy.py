"""No delimiter strategy."""

from typing import Any

from .base import BaseDelimiterStrategy


class NoneStrategy(BaseDelimiterStrategy):
    """
    Strategy that applies no delimiters to context.

    Simply converts context to string format without any wrapping.
    """

    def apply(
        self, context: str | list[str] | dict[str, Any] | None, section: str = "context"
    ) -> str | None:
        """
        Apply no delimiters to context.

        Args:
            context: Context data
            section: Name of the section being delimited (ignored for none strategy)

        Returns:
            Context as string without delimiters
        """
        return self.convert_to_string(context)
