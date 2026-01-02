"""
Prompt Stanza - A PromptOps library for modular prompt composition.

Philosophy: "Prompts as Code" - Prompts are modular, versioned functions
with strict typing and unit tests, rather than hardcoded strings.
"""

from .ab_testing import ABTestConfig, ABTestSelector, MultiVariantSelector, VariantConfig
from .core import PromptStanza
from .defense_strategies import (
    BaseDefenseStrategy,
    ClassifyIntentStrategy,
    PerplexityCheckStrategy,
    RewriteStrategy,
)
from .delimiter_strategies import (
    AngleBracketsStrategy,
    BaseDelimiterStrategy,
    MarkdownStrategy,
    MarkerStrategy,
    NoneStrategy,
    XmlStrategy,
)
from .exceptions import (
    AdapterError,
    PromptStanzaError,
    SecurityError,
    StanzaNotFoundError,
    ValidationError,
)
from .input_adapters import (
    BaseInputAdapter,
    DynamoDBAdapter,
    InlineAdapter,
    LocalFileAdapter,
    MongoDBAdapter,
    S3FileAdapter,
    SQLAdapter,
)
from .models import DefenseStrategy, DelimitingStrategy, PromptConfig, SchemaField
from .output_adapters import BaseOutputAdapter, LangChainOutputAdapter, StringOutputAdapter

__version__ = "0.1.0"

__all__ = [
    # Core classes
    "PromptStanza",
    # Models
    "PromptConfig",
    "SchemaField",
    "DelimitingStrategy",
    "DefenseStrategy",
    # Defense Strategies
    "BaseDefenseStrategy",
    "ClassifyIntentStrategy",
    "PerplexityCheckStrategy",
    "RewriteStrategy",
    # Delimiter Strategies
    "BaseDelimiterStrategy",
    "NoneStrategy",
    "MarkdownStrategy",
    "XmlStrategy",
    "MarkerStrategy",
    "AngleBracketsStrategy",
    # Input Adapters
    "BaseInputAdapter",
    "DynamoDBAdapter",
    "InlineAdapter",
    "LocalFileAdapter",
    "MongoDBAdapter",
    "S3FileAdapter",
    "SQLAdapter",
    # Output Adapters
    "BaseOutputAdapter",
    "LangChainOutputAdapter",
    "StringOutputAdapter",
    # A/B Testing
    "ABTestConfig",
    "ABTestSelector",
    "MultiVariantSelector",
    "VariantConfig",
    # Exceptions
    "PromptStanzaError",
    "ValidationError",
    "StanzaNotFoundError",
    "AdapterError",
    "SecurityError",
]
