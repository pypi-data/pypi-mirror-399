"""Main PromptStanza class for prompt composition."""

from typing import Any

from langchain_core.language_models import BaseChatModel

from ..builder.prompt_builder import PromptBuilder
from ..input_adapters.base import BaseInputAdapter
from ..output_adapters.base import BaseOutputAdapter
from ..output_adapters.string_output import StringOutputAdapter


class PromptStanza:
    """
    Main class for prompt composition.

    This class provides the compose() method to build prompts by:
    1. Loading template configuration from an input adapter
    2. Building the prompt using context, inputs, and builder
    3. Formatting the output using an output adapter
    """

    def __init__(
        self,
        input_adapter: BaseInputAdapter,
        llm: BaseChatModel,
        output_adapter: BaseOutputAdapter | None = None,
    ) -> None:
        """
        Initialize PromptStanza with an input adapter and optional output adapter.

        Args:
            input_adapter: An input adapter for loading templates
                          (LocalAdapter, InlineAdapter, etc.)
            llm: A chat model instance that will be used by the defensive strategies
            output_adapter: Optional output adapter for formatting the final prompt.
                          Defaults to StringOutputAdapter if not provided.
        """
        self.input_adapter = input_adapter
        self.llm = llm
        self.output_adapter = output_adapter or StringOutputAdapter()

    def compose(
        self,
        identifier: str,
        version: str = "latest",
        context: str | dict[str, Any] | None = None,
        inputs: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        """
        Compose a prompt from a template.

        Args:
            identifier: Template identifier (e.g., "code_review" or "engineering/code_review")
            version: Version string (semver like "1.0.0" or "latest")
            context: Additional context data (string or dict with retrieved docs, RAG data, etc.)
            inputs: Template input variables (validated against schema)
            **kwargs: Additional variables for template rendering

        Returns:
            Composed and formatted prompt (type depends on output adapter)

        Raises:
            ValidationError: If required inputs are missing or validation fails
            StanzaNotFoundError: If template cannot be found
            AdapterError: If template loading fails
        """
        # Load template configuration from adapter
        template_config = self.input_adapter.load(identifier, version)

        # Build prompt using builder with async support
        import asyncio

        # Check if we're already in an async context
        try:
            asyncio.get_running_loop()
            # We're in an async context, create a task
            # This requires the caller to use compose in an async context
            raise RuntimeError(
                "compose() called from async context. Use async compose() or run in sync context."
            )
        except RuntimeError as e:
            if "no running event loop" in str(e).lower():
                # We're in a sync context, create new event loop
                prompt = asyncio.run(
                    PromptBuilder.build(
                        config=template_config,
                        context=context,
                        inputs=inputs,
                        llm=self.llm,
                        **kwargs,
                    )
                )

                # Format using output adapter
                metadata = {
                    "name": template_config.name,
                    "version": template_config.version,
                    "identifier": identifier,
                }
                return self.output_adapter.format(prompt, metadata)
            else:
                # Re-raise if it's the "called from async context" error
                raise

    async def acompose(
        self,
        identifier: str,
        version: str = "latest",
        context: str | dict[str, Any] | None = None,
        inputs: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        """
        Async version of compose() for use in async contexts.

        Args:
            identifier: Template identifier (e.g., "code_review" or "engineering/code_review")
            version: Version string (semver like "1.0.0" or "latest")
            context: Additional context data (string or dict with retrieved docs, RAG data, etc.)
            inputs: Template input variables (validated against schema)
            **kwargs: Additional variables for template rendering

        Returns:
            Composed and formatted prompt (type depends on output adapter)

        Raises:
            ValidationError: If required inputs are missing or validation fails
            StanzaNotFoundError: If template cannot be found
            AdapterError: If template loading fails
        """
        # Load template configuration from adapter
        template_config = self.input_adapter.load(identifier, version)

        # Build prompt using builder
        prompt = await PromptBuilder.build(
            config=template_config,
            context=context,
            inputs=inputs,
            llm=self.llm,
            **kwargs,
        )

        # Format using output adapter
        metadata = {
            "name": template_config.name,
            "version": template_config.version,
            "identifier": identifier,
        }
        return self.output_adapter.format(prompt, metadata)
