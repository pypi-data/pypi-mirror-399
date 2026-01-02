"""Perplexity check defense strategy to detect gibberish inputs."""

from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from .base import BaseDefenseStrategy


class PerplexityCheckStrategy(BaseDefenseStrategy):
    """
    Defense strategy that checks if input is gibberish using perplexity analysis.

    Uses an LLM to analyze whether the input appears to be nonsensical or
    gibberish text. If the perplexity score indicates gibberish, raises an error.
    """

    def __init__(self, threshold: float = 0.7):
        """
        Initialize the perplexity check strategy.

        Args:
            threshold: Confidence threshold for gibberish detection (0.0-1.0).
                      Higher values are more strict. Default is 0.7.
        """
        self.threshold = threshold

    async def apply(
        self,
        inputs: dict[str, Any],
        context: str | list[str] | dict[str, Any] | None,
        llm: BaseChatModel | None = None,
    ) -> tuple[dict[str, Any], str | list[str] | dict[str, Any] | None]:
        """
        Check inputs and context for gibberish content.

        Args:
            inputs: Input dictionary to check
            context: Context data to check
            llm: Language model for perplexity analysis

        Returns:
            Original inputs and context if check passes

        Raises:
            ValueError: If gibberish is detected above threshold
            RuntimeError: If LLM is not provided
        """
        if llm is None:
            raise RuntimeError("PerplexityCheckStrategy requires an LLM to be provided")

        # Serialize data for analysis
        serialized_inputs = self.serialize_data(inputs)
        serialized_context = self.serialize_data(context) if context else ""

        # Combine for analysis
        combined_text = f"Inputs:\n{serialized_inputs}"
        if serialized_context:
            combined_text += f"\n\nContext:\n{serialized_context}"

        # Create prompt for gibberish detection
        system_prompt = (
            "You are a text quality analyzer. Analyze the provided text and determine if it "
            "appears to be gibberish or nonsensical.\n\n"
            "Gibberish indicators:\n"
            "- Random character sequences with no meaningful words\n"
            "- Excessive special characters or symbols\n"
            "- Repeated patterns that don't form coherent language\n"
            "- Mixed language fragments that make no sense\n"
            "- Keyboard mashing or random typing\n\n"
            "Respond with ONLY a JSON object in this format:\n"
            "{\n"
            '  \\"is_gibberish\\": true/false,\n'
            '  \\"confidence\\": 0.0-1.0,\n'
            '  \\"reason\\": \\"brief explanation\\"\n'
            "}"
        )

        human_prompt = f"""Analyze this text for gibberish:

{combined_text}

Is this gibberish?"""

        # Query LLM for analysis
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt),
        ]

        response = await llm.ainvoke(messages)
        response_text = response.content.strip()

        # Parse response
        try:
            import json

            # Extract JSON from response (handle markdown code blocks)
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            result = json.loads(response_text)

            is_gibberish = result.get("is_gibberish", False)
            confidence = result.get("confidence", 0.0)
            reason = result.get("reason", "Unknown")

            # Check if gibberish detected above threshold
            if is_gibberish and confidence >= self.threshold:
                raise ValueError(f"Gibberish detected (confidence: {confidence:.2f}): {reason}")

        except json.JSONDecodeError:
            # If we can't parse response, assume not gibberish to avoid false positives
            pass

        except ValueError:
            # Re-raise gibberish detection errors
            raise

        # Return original inputs and context if check passes
        return inputs, context
