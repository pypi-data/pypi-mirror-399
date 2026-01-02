"""Defense handler for applying security strategies."""

import asyncio
from typing import Any

from langchain_core.language_models import BaseChatModel

from ..defense_strategies import ClassifyIntentStrategy, PerplexityCheckStrategy, RewriteStrategy
from ..models import DefenseStrategy


class DefenseHandler:
    """
    Handler for applying defense strategies to protect against prompt injection.

    Delegates to strategy classes:
    - PERPLEXITY_CHECK: PerplexityCheckStrategy
    - CLASSIFY_INTENT: ClassifyIntentStrategy
    - REWRITE: RewriteStrategy
    """

    @staticmethod
    async def apply_strategies(
        strategies: list[DefenseStrategy],
        inputs: dict[str, Any],
        context: str | list[str] | dict[str, Any] | None = None,
        llm: BaseChatModel | None = None,
    ) -> tuple[dict[str, Any], str | list[str] | dict[str, Any] | None]:
        """
        Apply defense strategies to inputs and context.

        Args:
            strategies: List of defense strategies to apply
            inputs: Input values (dictionary)
            context: Context data (string, list of strings, or dict)
            llm: Language model for LLM-based strategies

        Returns:
            Tuple of (processed inputs, processed context)

        Raises:
            SecurityError: If jailbreak attempt is detected
            ValueError: If LLM is required but not provided
        """
        # Check if LLM is needed
        llm_strategies = {
            DefenseStrategy.PERPLEXITY_CHECK,
            DefenseStrategy.CLASSIFY_INTENT,
            DefenseStrategy.REWRITE,
        }
        needs_llm = any(s in llm_strategies for s in strategies)

        if needs_llm and llm is None:
            raise ValueError(
                "LLM is required for PERPLEXITY_CHECK, CLASSIFY_INTENT and REWRITE strategies"
            )

        processed_inputs = inputs.copy()
        processed_context = context

        # Create strategy instances and execute in parallel
        tasks = []
        strategy_instances = []

        for strategy in strategies:
            if strategy == DefenseStrategy.PERPLEXITY_CHECK:
                strategy_instance = PerplexityCheckStrategy()
                tasks.append(strategy_instance.apply(processed_inputs, processed_context, llm))
                strategy_instances.append(strategy_instance)
            elif strategy == DefenseStrategy.CLASSIFY_INTENT:
                strategy_instance = ClassifyIntentStrategy()
                tasks.append(strategy_instance.apply(processed_inputs, processed_context, llm))
                strategy_instances.append(strategy_instance)
            elif strategy == DefenseStrategy.REWRITE:
                strategy_instance = RewriteStrategy()
                tasks.append(strategy_instance.apply(processed_inputs, processed_context, llm))
                strategy_instances.append(strategy_instance)

        # Execute all strategies in parallel
        if tasks:
            results = await asyncio.gather(*tasks)

            # Process results - apply changes from strategies
            for strategy, result in zip(strategies, results, strict=False):
                if strategy == DefenseStrategy.REWRITE:
                    processed_inputs, processed_context = result
                # PERPLEXITY_CHECK and CLASSIFY_INTENT return unchanged data (or raise errors)

        return processed_inputs, processed_context
