"""Base class for delimiter strategies."""

from abc import ABC, abstractmethod
from typing import Any


class BaseDelimiterStrategy(ABC):
    """
    Abstract base class for delimiter strategies.

    Defines the interface for delimiter strategy implementations.
    """

    @staticmethod
    def convert_to_string(context: str | list[str] | dict[str, Any] | None) -> str | None:
        """
        Convert context to string representation.

        Args:
            context: Context data (string, list, or dict)

        Returns:
            String representation of context
        """
        if context is None:
            return None

        if isinstance(context, str):
            return context
        elif isinstance(context, list):
            return "\n".join(str(item) for item in context)
        elif isinstance(context, dict):
            return "\n".join(f"{k}: {v}" for k, v in context.items())
        else:
            return str(context)

    @abstractmethod
    def apply(
        self, context: str | list[str] | dict[str, Any] | None, section: str = "context"
    ) -> str | None:
        """
        Apply the delimiter strategy to context.

        Args:
            context: Context data to delimit
            section: Name of the section being delimited (system, task, context, output)

        Returns:
            Delimited context string or None
        """
        pass
