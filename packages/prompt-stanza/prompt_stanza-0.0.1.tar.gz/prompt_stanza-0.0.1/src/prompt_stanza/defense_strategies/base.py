"""Base class for defense strategies."""

import json
from abc import ABC, abstractmethod
from typing import Any

from langchain_core.language_models import BaseChatModel


class BaseDefenseStrategy(ABC):
    """
    Abstract base class for defense strategies.

    Provides common serialization/deserialization methods and defines
    the interface for defense strategy implementations.
    """

    @staticmethod
    def serialize_data(data: Any) -> str:
        """
        Serialize data to a string format for LLM analysis.

        Args:
            data: Data to serialize (can be string, list, dict, etc.)

        Returns:
            String representation of data
        """
        if isinstance(data, str):
            return data
        elif isinstance(data, list):
            return "\n".join(str(item) for item in data)
        elif isinstance(data, dict):
            return json.dumps(data, indent=2)
        else:
            return str(data)

    @staticmethod
    def deserialize_to_original_format(serialized: str, original: Any) -> Any:
        """
        Deserialize string back to original data format.

        Args:
            serialized: Serialized string data
            original: Original data to match format

        Returns:
            Data in original format
        """
        if isinstance(original, str):
            return serialized
        elif isinstance(original, list):
            # Split by newlines to restore list format
            return [line.strip() for line in serialized.split("\n") if line.strip()]
        elif isinstance(original, dict):
            try:
                return json.loads(serialized)
            except json.JSONDecodeError:
                # If JSON parsing fails, return as string
                return serialized
        else:
            return serialized

    @abstractmethod
    async def apply(
        self,
        inputs: dict[str, Any],
        context: str | list[str] | dict[str, Any] | None,
        llm: BaseChatModel | None = None,
    ) -> tuple[dict[str, Any], str | list[str] | dict[str, Any] | None]:
        """
        Apply the defense strategy to inputs and context.

        Args:
            inputs: Input dictionary to process
            context: Context data to process
            llm: Language model for LLM-based strategies

        Returns:
            Tuple of (processed inputs, processed context)

        Raises:
            SecurityError: If threat is detected (for classification strategies)
        """
        pass
