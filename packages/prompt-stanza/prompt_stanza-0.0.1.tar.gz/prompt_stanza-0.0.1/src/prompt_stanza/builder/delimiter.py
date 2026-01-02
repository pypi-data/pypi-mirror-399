"""Delimiter handler for applying formatting strategies."""

from typing import Any

from ..delimiter_strategies import (
    AngleBracketsStrategy,
    MarkdownStrategy,
    MarkerStrategy,
    NoneStrategy,
    XmlStrategy,
)
from ..models import DelimitingStrategy


class DelimiterHandler:
    """
    Handler for applying delimiting strategies to context data.

    Delegates to strategy classes:
    - NONE: NoneStrategy
    - MARKDOWN: MarkdownStrategy
    - XML: XmlStrategy
    - MARKER: MarkerStrategy
    - ANGLE_BRACKETS: AngleBracketsStrategy
    """

    @staticmethod
    def apply_strategy(
        strategy: DelimitingStrategy,
        context: str | list[str] | dict[str, Any] | None,
        section: str = "context",
    ) -> str | None:
        """
        Apply delimiting strategy to context.

        Args:
            strategy: Delimiting strategy to use
            context: Context data to delimit
            section: Name of the section being delimited (system, task, context, output)

        Returns:
            Delimited context string or None
        """
        if context is None:
            return None

        # Select and instantiate appropriate strategy
        if strategy == DelimitingStrategy.NONE:
            strategy_instance = NoneStrategy()
        elif strategy == DelimitingStrategy.MARKDOWN:
            strategy_instance = MarkdownStrategy()
        elif strategy == DelimitingStrategy.XML:
            strategy_instance = XmlStrategy()
        elif strategy == DelimitingStrategy.MARKER:
            strategy_instance = MarkerStrategy()
        elif strategy == DelimitingStrategy.ANGLE_BRACKETS:
            strategy_instance = AngleBracketsStrategy()
        else:
            # Default to no delimiter
            strategy_instance = NoneStrategy()

        return strategy_instance.apply(context, section)
